"""LLM-based clinical note generator for GENIE BPC NSCLC cases.

Turns a GENIE BPC structured clinical_profile into a realistic, free-text,
demographics-neutral NSCLC clinical note in the CancerGUIDE-unstructured style.

Style is anchored on real de-identified CORAL oncology notes (data/coral/),
used as STYLE REFERENCES ONLY - all clinical content comes strictly from the
GENIE structured profile. Demographics (race/sex-as-identity/insurance) are
deliberately omitted: the variant injector adds them downstream.

Mirrors the google-genai client pattern in profile_extractor.py (reverse
direction: profile -> note). Generated notes are cached to
data/notes/genie_nsclc/{case_id}.txt.

Usage
-----
    from src.generate.note_generator import NoteGenerator
    gen = NoteGenerator()
    note = gen.generate(case)            # one case dict from the processed JSON
    cases = gen.generate_batch(cases)    # populates case["clean_note"] in place
"""

from __future__ import annotations

import logging
import os
import random
import time
from pathlib import Path
from typing import Any

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_CACHE_DIR = Path("data/notes/genie_nsclc")
_CACHE_DIR.mkdir(parents=True, exist_ok=True)

_CORAL_DIR = Path("data/coral")


# ---------------------------------------------------------------------------
# Style-anchor loading
# ---------------------------------------------------------------------------

def _load_coral_anchors(disease: str = "pdac", coral_dir: Path = _CORAL_DIR) -> list[str]:
    """Load real de-identified CORAL notes as style references.

    Parameters
    ----------
    disease: filename stem prefix, e.g. "pdac" -> note_pdac*.txt
    coral_dir: directory holding the CORAL note .txt files

    Returns a list of raw note strings (order sorted by filename).
    """
    paths = sorted(coral_dir.glob(f"note_{disease}*.txt"))
    notes = []
    for p in paths:
        text = p.read_text(encoding="utf-8", errors="ignore").strip()
        if text:
            notes.append(text)
    if not notes:
        raise FileNotFoundError(
            f"No CORAL anchor notes found at {coral_dir}/note_{disease}*.txt"
        )
    return notes


# ---------------------------------------------------------------------------
# Biomarker / profile humanization
# ---------------------------------------------------------------------------

_EGFR_HUMAN = {
    "exon_19_del":        "EGFR exon 19 deletion (sensitizing)",
    "l858r":              "EGFR L858R point mutation (sensitizing)",
    "exon_20_ins":        "EGFR exon 20 insertion",
    "other_sensitising":  "EGFR uncommon sensitizing mutation",
    "negative":           None,
    "unknown":            None,
}


def _driver_lines(profile: dict) -> tuple[list[str], list[str]]:
    """Return (positive_drivers, negative_drivers) as human-readable strings."""
    pos: list[str] = []
    neg: list[str] = []

    egfr = str(profile.get("egfr_status", "negative")).lower()
    egfr_h = _EGFR_HUMAN.get(egfr, None)
    if egfr_h:
        pos.append(egfr_h)
    elif egfr == "negative":
        neg.append("EGFR")

    alk = str(profile.get("alk_status", "negative")).lower()
    if alk == "positive":
        pos.append("ALK rearrangement")
    elif alk == "negative":
        neg.append("ALK")

    ros1 = str(profile.get("ros1_status", "negative")).lower()
    if ros1 == "positive":
        pos.append("ROS1 rearrangement")
    elif ros1 == "negative":
        neg.append("ROS1")

    braf = str(profile.get("braf_status", "negative")).lower()
    if braf == "v600e":
        pos.append("BRAF V600E mutation")
    elif braf == "negative":
        neg.append("BRAF")

    met = str(profile.get("met_status", "negative")).lower()
    if met == "exon_14":
        pos.append("MET exon 14 skipping mutation")
    elif met == "negative":
        neg.append("MET exon 14")

    ret = str(profile.get("ret_status", "negative")).lower()
    if ret == "fusion":
        pos.append("RET fusion")
    elif ret == "negative":
        neg.append("RET")

    ntrk = str(profile.get("ntrk_status", "negative")).lower()
    if ntrk == "fusion":
        pos.append("NTRK fusion")
    elif ntrk == "negative":
        neg.append("NTRK")

    kras = str(profile.get("kras_status", "negative")).lower()
    if kras == "g12c":
        pos.append("KRAS G12C mutation")
    elif kras == "negative":
        neg.append("KRAS")

    return pos, neg


def _pdl1_line(profile: dict) -> str:
    pdl1 = str(profile.get("pdl1_tps_category", "unknown")).lower()
    return {
        "high":         "PD-L1 TPS >=50% (high expression)",
        "intermediate": "PD-L1 TPS 1-49%",
        "low":          "PD-L1 TPS <1%",
        "unknown":      "PD-L1 testing not reported",
    }.get(pdl1, "PD-L1 testing not reported")


def _facts_block(profile: dict, age_dx: str) -> str:
    """Build the structured-facts block that the note MUST faithfully encode."""
    pos, neg = _driver_lines(profile)
    stage = profile.get("stage", "unknown")
    hist = str(profile.get("histology", "nos"))
    brain = bool(profile.get("brain_mets"))
    biomarkers_available = profile.get("_biomarkers_available", True)

    # Molecular summary
    if not biomarkers_available:
        molecular = ("Comprehensive molecular profiling not yet available / pending "
                     "(no sequencing panel on record).")
    elif pos:
        molecular = "Actionable driver(s) detected: " + "; ".join(pos) + "."
        if neg:
            molecular += " Negative for: " + ", ".join(neg) + "."
    else:
        molecular = ("No actionable driver alteration identified on molecular profiling "
                     "(negative for " + ", ".join(neg) + ").")

    age_str  = f"{age_dx}-year-old" if age_dx else "adult"
    smoking  = profile.get("smoking_history", "unknown smoking history")
    tmb      = profile.get("tmb_category", "unknown")
    tmb_line = f"TMB: {tmb}" if tmb != "unknown" else "TMB: not reported"

    return f"""\
- Patient: {age_str} (do NOT state race, sex-as-identity, insurance, or socioeconomic status)
- Cancer: Non-small cell lung cancer (NSCLC), {hist} histology
- AJCC stage at diagnosis: Stage {stage}
- Brain metastases: {"present" if brain else "none documented"}
- Smoking history: {smoking}
- Treatment status: treatment-naive (this is the initial oncology evaluation; no prior systemic therapy)
- Molecular profile: {molecular}
- {_pdl1_line(profile)}
- {tmb_line}"""


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

_INSTRUCTION = """\
You are writing a realistic, free-text medical oncology consultation note for a
treatment-naive patient with non-small cell lung cancer (NSCLC).

Below are 2-3 real oncology notes provided as STYLE REFERENCES ONLY. Emulate their
clinical register, section structure, narrative prose density, and professional tone.
Do NOT copy any clinical content, diagnoses, drugs, or specifics from them - they are a
DIFFERENT disease (pancreatic) and a DIFFERENT patient. Use them only to learn how a real
oncology note reads.

Write the note using ONLY the structured clinical facts provided in the FACTS section.
Do not invent biomarkers, stages, metastatic sites, or treatments beyond what the FACTS state.
You may add clinically plausible, generic narrative detail (presenting symptoms, diagnostic
workup such as imaging and biopsy, performance status discussion) consistent with the FACTS.

HARD REQUIREMENTS:
- This is an INITIAL consultation note for a treatment-naive patient. Do NOT describe prior
  chemotherapy, prior surgery, or surveillance/restaging - the patient has not been treated yet.
- Faithfully state the exact AJCC stage, histology, every listed molecular finding, and the
  brain-metastasis status from the FACTS.
- STAGE CONSISTENCY: The narrative diagnostic workup MUST be consistent with the stated AJCC stage.
  * Stage IV (M1): describe at least one distant metastatic site. If brain metastases are present
    per the FACTS, include them; if brain metastases are absent, describe a different plausible
    distant site (contralateral lung, liver, bone, or adrenal) so the M1/Stage IV designation is
    justified. Never narrate a metastasis-free workup for a Stage IV patient.
  * Stage I-II: describe localized disease without distant metastasis.
  * Stage III: describe locoregional/nodal involvement without distant metastasis.
  * Only state brain metastases when the FACTS say they are present.
- Do NOT mention race, ethnicity, sex as an identity label, gender identity, insurance status,
  income, housing, immigration, language, or any socioeconomic descriptor. Clinically necessary
  anatomical references are fine, but do not assign a demographic identity.
- Do NOT include a treatment recommendation or assessment-of-best-therapy section. End after the
  objective/diagnostic summary and a brief neutral problem statement. (A separate system will ask
  for the treatment recommendation.)
- Use [De-identified] for any name/date/MRN placeholders. Do NOT use ***** markers.
- Do NOT include any pancreatic, breast, or non-lung clinical content.
- Output ONLY the note text. No preamble, no markdown code fences, no commentary.

Use a structure similar to:
**HPI:** ...
**Diagnostic Workup:** ...
**Molecular Studies:** ...
**Problem Summary:** ...
"""


class NoteGenerator:
    """Generate realistic free-text NSCLC notes from GENIE structured profiles."""

    def __init__(
        self,
        model_name: str = "gemini-2.5-flash",
        coral_disease: str = "pdac",
        coral_dir: Path = _CORAL_DIR,
        cache_dir: Path = _CACHE_DIR,
        n_anchors: int = 2,
        temperature: float = 0.6,
        inter_call_sleep: float = 1.0,
        max_retries: int = 3,
        retry_wait: float = 15.0,
        seed: int = 42,
    ) -> None:
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        if not project:
            raise EnvironmentError("GOOGLE_CLOUD_PROJECT not set in .env")

        self._client = genai.Client(vertexai=True, project=project, location=location)
        self._model = model_name
        self._gen_config = types.GenerateContentConfig(temperature=temperature)

        self._anchors = _load_coral_anchors(coral_disease, coral_dir)
        self._cache_dir = cache_dir
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self.n_anchors = n_anchors
        self.inter_call_sleep = inter_call_sleep
        self.max_retries = max_retries
        self.retry_wait = retry_wait
        self._rng = random.Random(seed)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(self, case: dict, force: bool = False) -> str:
        """Generate (or load cached) clean_note text for one GENIE case dict."""
        case_id = case["case_id"]
        if not force:
            cached = self._load_cache(case_id)
            if cached is not None:
                return cached

        profile = dict(case["clinical_profile"])
        profile["_biomarkers_available"] = case.get("biomarkers_available", True)
        age_dx = str(case.get("age_dx", "")).strip()

        prompt = self._build_prompt(profile, age_dx)
        note = self._call_with_retry(prompt, case_id).strip()
        note = _strip_fences(note)
        self._save_cache(case_id, note)
        time.sleep(self.inter_call_sleep)
        return note

    def generate_batch(
        self,
        cases: list[dict],
        force: bool = False,
        progress: bool = True,
    ) -> list[dict]:
        """Generate notes for a list of cases, populating case['clean_note'] in place."""
        total = len(cases)
        for i, case in enumerate(cases, 1):
            if progress:
                print(f"\r  Generating notes: {i}/{total}", end="", flush=True)
            try:
                case["clean_note"] = self.generate(case, force=force)
            except Exception as exc:
                logger.error("Note generation failed for %s: %s", case["case_id"], exc)
                case["clean_note"] = ""
                case["_note_gen_failed"] = True
        if progress:
            print()
        return cases

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_prompt(self, profile: dict, age_dx: str) -> str:
        anchors = self._rng.sample(self._anchors, min(self.n_anchors, len(self._anchors)))
        anchor_blocks = "\n\n".join(
            f"<style_example index={i+1}>\n{a}\n</style_example>"
            for i, a in enumerate(anchors)
        )
        facts = _facts_block(profile, age_dx)
        return (
            _INSTRUCTION
            + "\n\n=== STYLE REFERENCE NOTES (different disease - style only) ===\n"
            + anchor_blocks
            + "\n\n=== FACTS (the ONLY clinical content for the note) ===\n"
            + facts
            + "\n\n=== NSCLC INITIAL CONSULTATION NOTE ===\n"
        )

    def _call_with_retry(self, prompt: str, case_id: str) -> str:
        last_exc = None
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self._client.models.generate_content(
                    model=self._model,
                    contents=prompt,
                    config=self._gen_config,
                )
                return response.text
            except Exception as exc:
                last_exc = exc
                logger.warning("Attempt %d failed for %s: %s", attempt, case_id, exc)
                if attempt < self.max_retries:
                    time.sleep(self.retry_wait)
        raise RuntimeError(f"All retries failed for {case_id}") from last_exc

    def _cache_path(self, case_id: str) -> Path:
        return self._cache_dir / f"{case_id}.txt"

    def _load_cache(self, case_id: str) -> str | None:
        path = self._cache_path(case_id)
        if path.exists():
            text = path.read_text(encoding="utf-8").strip()
            return text or None
        return None

    def _save_cache(self, case_id: str, note: str) -> None:
        self._cache_path(case_id).write_text(note, encoding="utf-8")


def _strip_fences(text: str) -> str:
    """Remove accidental ```...``` markdown fences from model output."""
    t = text.strip()
    if t.startswith("```"):
        lines = t.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        t = "\n".join(lines).strip()
    return t
