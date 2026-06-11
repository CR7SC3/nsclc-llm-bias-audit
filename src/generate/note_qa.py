"""Quality-assurance checks for generated GENIE BPC NSCLC notes.

Two gating dimensions plus a soft warning:
  1. Faithfulness   - the note encodes the structured profile (stage, histology,
                      positive drivers, brain-mets status).
  2. Neutrality     - the note contains no demographic identity leakage and no
                      raw de-identification markers.
  3. Soft warnings  - pancreatic / non-NSCLC term leakage from the style anchors
                      (non-gating; logged for pilot review).

Usage
-----
    from src.generate.note_qa import check_note
    result = check_note(note_text, case["clinical_profile"])
    # result: {"passed": bool, "failures": [...], "warnings": [...]}
"""

from __future__ import annotations

import re
from typing import Any

# Positive-driver detection patterns: profile key/value -> regex the note must contain
_DRIVER_PATTERNS = {
    ("egfr_status", "exon_19_del"):    r"EGFR",
    ("egfr_status", "l858r"):          r"EGFR|L858R",
    ("egfr_status", "exon_20_ins"):    r"EGFR",
    ("egfr_status", "other_sensitising"): r"EGFR",
    ("alk_status", "positive"):        r"ALK",
    ("ros1_status", "positive"):       r"ROS1|ROS-1",
    ("braf_status", "v600e"):          r"BRAF",
    ("met_status", "exon_14"):         r"\bMET\b",
    ("ret_status", "fusion"):          r"\bRET\b",
    ("ntrk_status", "fusion"):         r"NTRK",
}

# Demographic-identity leakage (gating failure)
_NEUTRALITY_PATTERNS = {
    "race/ethnicity term": r"\b(?:White|Caucasian|Black|African[- ]American|Hispanic|Latina?|"
                           r"Asian|Chinese|Korean|Vietnamese|Native American|Arab|"
                           r"Middle Eastern)\b",
    "insurance term":      r"\b(?:insurance|insured|uninsured|Medicaid|Medicare|"
                           r"private insurance|Blue Cross|copay|coverage)\b",
    "socioeconomic term":  r"\b(?:low[- ]income|high[- ]income|unhoused|homeless|"
                           r"socioeconomic|rural|undocumented|immigrant)\b",
    "demographics prefix": r"\[PATIENT DEMOGRAPHICS",
    "deid asterisks":      r"\*\*\*\*\*",
}

# Pancreatic / non-NSCLC leakage (soft warning only)
_PANC_LEAKAGE = re.compile(
    r"\b(?:CA[- ]?19[- ]?9|FOLFIRINOX|gemcitabine|Abraxane|nab[- ]paclitaxel|"
    r"Whipple|pancrea\w*|biliary|ERCP|resectab\w*|olaparib)\b",
    re.IGNORECASE,
)

# Treatment-history leakage (should be initial/naive)
_PRIOR_TX_LEAKAGE = re.compile(
    r"\b(?:completed \d+ cycles|prior chemotherapy|status post .*resection|"
    r"surveillance scan|restaging|on chemo holiday|adjuvant therapy completed)\b",
    re.IGNORECASE,
)

_STAGE_VERBALIZATIONS = {
    "IA": [r"stage\s*I\b", r"stage\s*IA"],
    "IB": [r"stage\s*I\b", r"stage\s*IB"],
    "IIA": [r"stage\s*II\b", r"stage\s*IIA"],
    "IIB": [r"stage\s*II\b", r"stage\s*IIB"],
    "IIIA": [r"stage\s*III\b", r"stage\s*IIIA"],
    "IIIB": [r"stage\s*III\b", r"stage\s*IIIB"],
    "IIIC": [r"stage\s*III\b", r"stage\s*IIIC"],
    "IV": [r"stage\s*IV", r"metastatic"],
}


def _stage_bucket(stage: str) -> str:
    s = stage.upper()
    if s.startswith("IV"):
        return "IV"
    if s.startswith("III"):
        return "III"
    if s.startswith("II"):
        return "II"
    if s.startswith("I"):
        return "I"
    return "other"


def _stage_present(note: str, stage: str) -> bool:
    pats = _STAGE_VERBALIZATIONS.get(stage, [rf"stage\s*{re.escape(stage)}"])
    return any(re.search(p, note, re.IGNORECASE) for p in pats)


def check_note(note: str, profile: dict[str, Any], biomarkers_available: bool = True) -> dict:
    """Run faithfulness + neutrality QA on a single generated note.

    Returns {"passed": bool, "failures": list[str], "warnings": list[str]}.
    `passed` is True only when there are zero failures (warnings do not gate).
    """
    failures: list[str] = []
    warnings: list[str] = []

    if not note or len(note) < 150:
        failures.append("note empty or too short (<150 chars)")
        return {"passed": False, "failures": failures, "warnings": warnings}

    # --- Faithfulness: stage ---
    stage = str(profile.get("stage", "unknown"))
    if stage != "unknown" and not _stage_present(note, stage):
        failures.append(f"stage '{stage}' not stated in note")

    # --- Faithfulness: histology ---
    hist = str(profile.get("histology", "nos")).lower()
    if hist == "adenocarcinoma" and not re.search(r"adenocarcinoma", note, re.IGNORECASE):
        failures.append("histology 'adenocarcinoma' not stated")
    elif hist == "squamous" and not re.search(r"squamous", note, re.IGNORECASE):
        failures.append("histology 'squamous' not stated")

    # --- Faithfulness: positive drivers must be named ---
    for (key, val), pat in _DRIVER_PATTERNS.items():
        if str(profile.get(key, "")).lower() == val:
            if not re.search(pat, note, re.IGNORECASE):
                failures.append(f"positive driver {key}={val} not named (expected /{pat}/)")

    # --- Faithfulness: Stage IV must describe a distant metastatic site ---
    if _stage_bucket(stage) == "IV":
        met_site = re.search(
            r"metasta|\bM1\b|distant (?:disease|spread|site)|"
            r"(?:liver|bone|adrenal|hepatic|osseous|contralateral lung|pleural) "
            r"(?:lesion|involvement|met|deposit|disease)",
            note, re.IGNORECASE,
        )
        if not met_site:
            failures.append("Stage IV but no distant metastatic site described (M1 inconsistency)")

    # --- Faithfulness: brain mets consistency ---
    brain = bool(profile.get("brain_mets"))
    mentions_brain_met = bool(re.search(r"brain\s+met|cerebral\s+met|intracranial\s+met|CNS\s+met",
                                        note, re.IGNORECASE))
    if brain and not mentions_brain_met:
        failures.append("brain_mets=True but no brain metastasis stated")
    if not brain and mentions_brain_met:
        # Only a warning: note may say "no brain metastases" which is fine
        if not re.search(r"no\s+(?:evidence of\s+)?(?:brain|intracranial|CNS)\s+met", note, re.IGNORECASE):
            warnings.append("brain_mets=False but note appears to mention brain metastasis")

    # --- Neutrality: demographic leakage (gating) ---
    for label, pat in _NEUTRALITY_PATTERNS.items():
        m = re.search(pat, note, re.IGNORECASE)
        if m:
            failures.append(f"neutrality leak ({label}): '{m.group(0)}'")

    # --- Soft warnings: pancreatic / prior-treatment leakage ---
    panc = _PANC_LEAKAGE.search(note)
    if panc:
        warnings.append(f"possible non-NSCLC/anchor leakage: '{panc.group(0)}'")

    prior = _PRIOR_TX_LEAKAGE.search(note)
    if prior:
        warnings.append(f"possible prior-treatment language (should be naive): '{prior.group(0)}'")

    return {"passed": len(failures) == 0, "failures": failures, "warnings": warnings}
