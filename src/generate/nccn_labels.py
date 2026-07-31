"""Load validated NCCN ground-truth labels for GENIE BPC NSCLC cases.

The labels live in data/processed/genie_nsclc_notes_groundtruth.csv with columns
`case_id`, `clinical_ground_truth` (primary answer) and `nccn_acceptable_answers`
(a ';'-separated list). This module exposes a single loader so both the experiment
runner and the backfill utility attach labels identically.

Result records consume two fields, matching compute_adherence_score's signature:
  nccn_label              : str   — primary NCCN answer
  nccn_acceptable_answers : list  — acceptable answers (primary included)

Usage
-----
    from src.generate.nccn_labels import load_nccn_index
    idx = load_nccn_index()                 # {case_id: {"label": str, "acceptable": [str, ...]}}
    rec.update(nccn_fields(idx, case_id))   # safe even when case_id is missing
"""

from __future__ import annotations

import csv
from pathlib import Path

_DEFAULT_PATH = Path("data/processed/genie_nsclc_notes_groundtruth.csv")


def _split_acceptable(primary: str, raw: str) -> list[str]:
    """Parse the ';'-separated acceptable list, ensuring the primary is included."""
    items = [a.strip() for a in (raw or "").split(";") if a.strip()]
    primary = (primary or "").strip()
    if primary and primary not in items:
        items.insert(0, primary)
    return items


def load_nccn_index(path: Path | str = _DEFAULT_PATH) -> dict[str, dict]:
    """Return {case_id: {"label": primary, "acceptable": [answers]}}.

    Returns an empty dict if the file is absent so callers degrade gracefully
    (labels simply stay unattached and adherence reports as un-scoreable).
    """
    p = Path(path)
    if not p.exists():
        return {}
    idx: dict[str, dict] = {}
    with open(p, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            cid = r.get("case_id", "").strip()
            if not cid:
                continue
            primary = (r.get("clinical_ground_truth") or "").strip()
            idx[cid] = {
                "label":      primary,
                "acceptable": _split_acceptable(primary, r.get("nccn_acceptable_answers", "")),
            }
    return idx


def nccn_fields(idx: dict[str, dict], case_id: str) -> dict:
    """Return the result-record fields for a case_id (empty-safe)."""
    entry = idx.get(case_id)
    if not entry:
        return {"nccn_label": None, "nccn_acceptable_answers": None}
    return {
        "nccn_label":              entry["label"] or None,
        "nccn_acceptable_answers": entry["acceptable"] or None,
    }
