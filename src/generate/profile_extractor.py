"""LLM-based clinical profile extractor for CancerGUIDE notes.

Reads a free-text NSCLC clinical note and extracts the structured
clinical profile dict required by nccn_scorer.get_nccn_answer().

Results are cached to data/profiles/ so each case is only extracted once.

Usage
-----
    from src.generate.profile_extractor import ProfileExtractor

    extractor = ProfileExtractor()
    profile = extractor.extract("case_001", note_text)
    nccn_result = get_nccn_answer(profile)
"""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_CACHE_DIR = Path("data/profiles")
_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Allowed values for validation
# ---------------------------------------------------------------------------

_ALLOWED: dict[str, set] = {
    "stage":              {"IA", "IB", "IIA", "IIB", "IIIA", "IIIB", "IIIC", "IV",
                           "IVA", "IVB", "IVC",  # substage variants — normalised below
                           "unknown"},
    "histology":          {"adenocarcinoma", "squamous", "nos", "unknown"},
    "egfr_status":        {"exon_19_del", "L858R", "exon_20_ins", "uncommon", "negative", "unknown"},
    "alk_status":         {"positive", "negative", "unknown"},
    "ros1_status":        {"positive", "negative", "unknown"},
    "braf_status":        {"V600E", "negative", "unknown"},
    "met_status":         {"exon_14", "negative", "unknown"},
    "ret_status":         {"fusion", "negative", "unknown"},
    "ntrk_status":        {"fusion", "negative", "unknown"},
    "pdl1_tps_category":  {"high", "intermediate", "low", "unknown"},
    "treatment_phase":    {"initial", "post_resection"},
    "resectability":      {"resectable", "unresectable", "marginally_resectable", "unknown"},
    "resection_status":   {"R0", "R1", "R2", "unknown"},
    "t_category":         {"T1a", "T1b", "T1c", "T2a", "T2b", "T3", "T4",
                           "T1", "T2",  # plain variants without a/b suffix
                           "unknown"},
}

_EXTRACTION_PROMPT = """\
You are a clinical NLP assistant. Extract structured fields from the NSCLC clinical note below.
Return ONLY a valid JSON object — no explanation, no markdown fencing.

Extract these fields exactly:

{{
  "stage":             one of ["IA","IB","IIA","IIB","IIIA","IIIB","IIIC","IV","unknown"],
  "histology":         one of ["adenocarcinoma","squamous","nos","unknown"],
  "egfr_status":       one of ["exon_19_del","L858R","exon_20_ins","uncommon","negative","unknown"],
  "alk_status":        one of ["positive","negative","unknown"],
  "ros1_status":       one of ["positive","negative","unknown"],
  "braf_status":       one of ["V600E","negative","unknown"],
  "met_status":        one of ["exon_14","negative","unknown"],
  "ret_status":        one of ["fusion","negative","unknown"],
  "ntrk_status":       one of ["fusion","negative","unknown"],
  "pdl1_tps_category": one of ["high","intermediate","low","unknown"],
                       (high = TPS ≥50%, intermediate = 1–49%, low = <1%, unknown = not tested/reported),
  "ecog_ps":           integer 0–4 (use 1 if not stated),
  "prior_therapy":     one of ["naive","treated"],
                       (naive = treatment-naive at this encounter; treated = received prior systemic therapy),
  "brain_mets":        true or false,
  "treatment_phase":   one of ["initial","post_resection"],
                       (post_resection = note describes a patient who has ALREADY undergone surgical resection
                        and is deciding on adjuvant therapy; look for "R0/R1/R2 resection", "post-surgical",
                        "following resection", "adjuvant"; otherwise use "initial"),
  "medically_inoperable": true or false,
                       (true if note states patient cannot tolerate surgery due to pulmonary function,
                        cardiac risk, or explicitly declines surgery),
  "resectability":     one of ["resectable","unresectable","marginally_resectable","unknown"],
                       (for Stage I/II default to "resectable" unless note states otherwise;
                        for Stage III use the note's explicit statement or "unknown"),
  "resection_status":  one of ["R0","R1","R2","unknown"],
                       (only relevant for post_resection phase; "unknown" if initial),
  "t_category":        one of ["T1a","T1b","T1c","T2a","T2b","T3","T4","unknown"]
                       (extract from TNM staging or tumour size: ≤1cm=T1a, >1–2cm=T1b, >2–3cm=T1c,
                        >3–4cm=T2a, >4–5cm=T2b, >5–7cm=T3, >7cm or invasion=T4)
}}

Rules:
- If a field is not mentioned or cannot be determined, use "unknown" (or false for booleans, 1 for ecog_ps).
- If molecular testing was not performed (no results available), set all biomarker fields to "unknown".
- If the note says a biomarker is NEGATIVE, use "negative", not "unknown".
- Do NOT infer or guess values; use "unknown" when uncertain.

CLINICAL NOTE:
{note}
"""


class ProfileExtractor:
    """Extract structured NCCN clinical profiles from free-text clinical notes."""

    def __init__(
        self,
        model_name: str = "gemini-2.5-flash",
        inter_call_sleep: float = 1.0,
        max_retries: int = 3,
        retry_wait: float = 15.0,
    ) -> None:
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        if not project:
            raise EnvironmentError("GOOGLE_CLOUD_PROJECT not set in .env")

        self._client = genai.Client(vertexai=True, project=project, location=location)
        self._model = model_name
        self._gen_config = types.GenerateContentConfig(
            temperature=0,
            response_mime_type="application/json",
        )
        self.inter_call_sleep = inter_call_sleep
        self.max_retries = max_retries
        self.retry_wait = retry_wait

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract(self, case_id: str, clinical_note: str, force: bool = False) -> dict[str, Any]:
        """Extract structured profile for one case.

        Parameters
        ----------
        case_id:      Unique identifier used for caching.
        clinical_note: De-identified (demographics-stripped) clinical note text.
        force:        If True, re-extract even if a cached result exists.

        Returns
        -------
        dict matching the nccn_scorer.get_nccn_answer() profile schema.
        """
        if not force:
            cached = self._load_cache(case_id)
            if cached is not None:
                return cached

        prompt = _EXTRACTION_PROMPT.format(note=clinical_note)
        raw_json = self._call_with_retry(prompt, case_id)
        profile = self._parse_and_validate(raw_json, case_id)
        profile["cancer_type"] = "nsclc"
        self._save_cache(case_id, profile)
        time.sleep(self.inter_call_sleep)
        return profile

    def extract_batch(
        self,
        cases: list[dict],
        note_field: str = "clean_note",
        force: bool = False,
        progress: bool = True,
    ) -> dict[str, dict[str, Any]]:
        """Extract profiles for a list of case dicts.

        Parameters
        ----------
        cases:      List of dicts, each with at least ``case_id`` and ``note_field``.
        note_field: Key in each case dict containing the clinical note text.
        force:      Re-extract even if cached.
        progress:   Print progress counter.

        Returns
        -------
        dict: {case_id: profile_dict}
        """
        results: dict[str, dict] = {}
        total = len(cases)

        for i, case in enumerate(cases, 1):
            case_id = case["case_id"]
            note = case.get(note_field, case.get("raw_note", ""))

            if progress:
                print(f"\r  Extracting profiles: {i}/{total}", end="", flush=True)

            try:
                results[case_id] = self.extract(case_id, note, force=force)
            except Exception as exc:
                logger.error("Failed to extract profile for %s: %s", case_id, exc)
                results[case_id] = self._fallback_profile(case_id)

        if progress:
            print()
        return results

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

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

    def _parse_and_validate(self, raw_json: str, case_id: str) -> dict[str, Any]:
        """Parse JSON response and validate/normalise field values."""
        try:
            profile = json.loads(raw_json)
        except json.JSONDecodeError as exc:
            logger.error("JSON parse error for %s: %s\nRaw: %s", case_id, exc, raw_json[:200])
            return self._fallback_profile(case_id)

        validated: dict[str, Any] = {}

        # String fields validated against allowed sets
        for field, allowed in _ALLOWED.items():
            val = str(profile.get(field, "unknown")).strip()
            # Normalise Stage IV substages to "IV" (scorer only uses major stage)
            if field == "stage" and val in ("IVA", "IVB", "IVC"):
                val = "IV"
            if val not in allowed:
                logger.warning(
                    "%s: field '%s' has unexpected value '%s', defaulting to 'unknown'",
                    case_id, field, val,
                )
                val = "unknown"
            validated[field] = val

        # Integer: ecog_ps
        try:
            ecog = int(profile.get("ecog_ps", 1))
            validated["ecog_ps"] = max(0, min(4, ecog))
        except (ValueError, TypeError):
            validated["ecog_ps"] = 1

        # Booleans
        for bool_field in ("brain_mets", "medically_inoperable"):
            raw_val = profile.get(bool_field, False)
            if isinstance(raw_val, str):
                validated[bool_field] = raw_val.lower() in ("true", "yes", "1")
            else:
                validated[bool_field] = bool(raw_val)

        # prior_therapy
        prior = str(profile.get("prior_therapy", "naive")).lower()
        validated["prior_therapy"] = "treated" if "treated" in prior else "naive"

        return validated

    def _fallback_profile(self, case_id: str) -> dict[str, Any]:
        """Return an all-unknown profile when extraction fails."""
        return {
            "cancer_type": "nsclc",
            "stage": "unknown",
            "histology": "unknown",
            "egfr_status": "unknown",
            "alk_status": "unknown",
            "ros1_status": "unknown",
            "braf_status": "unknown",
            "met_status": "unknown",
            "ret_status": "unknown",
            "ntrk_status": "unknown",
            "pdl1_tps_category": "unknown",
            "ecog_ps": 1,
            "prior_therapy": "naive",
            "brain_mets": False,
            "treatment_phase": "initial",
            "medically_inoperable": False,
            "resectability": "unknown",
            "resection_status": "unknown",
            "t_category": "unknown",
            "_extraction_failed": True,
            "_case_id": case_id,
        }

    def _cache_path(self, case_id: str) -> Path:
        return _CACHE_DIR / f"{case_id}_profile.json"

    def _load_cache(self, case_id: str) -> dict[str, Any] | None:
        path = self._cache_path(case_id)
        if path.exists():
            with open(path, encoding="utf-8") as fh:
                return json.load(fh)
        return None

    def _save_cache(self, case_id: str, profile: dict[str, Any]) -> None:
        path = self._cache_path(case_id)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(profile, fh, indent=2, ensure_ascii=False)
