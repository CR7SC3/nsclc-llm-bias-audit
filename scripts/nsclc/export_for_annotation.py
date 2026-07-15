"""Export LLM responses for oncologist annotation — Cohen's kappa validation.

Produces two files:
  annotation_export_YYYYMMDD.csv   — sent to oncologist (no ground truth)
  annotation_answerkey_YYYYMMDD.csv — internal key (ground truth + scorer label)

Sampling: stratified random (seed=42)
  50 concordant + 25 non-concordant = 75 cases
  Source: v1 Gemini structured checkpoint, white_male_private variant

Usage
-----
    python scripts/nsclc/export_for_annotation.py
"""

from __future__ import annotations

import csv
import json
import random
from datetime import date
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────

_CHECKPOINT   = Path("results/baseline/synthetic_structured_results.json")
_PROCESSED    = Path("data/processed/cancerguide_synthetic_structured_processed.json")
_CONCORDANCE  = Path("results/analysis/synthetic_structured_concordance_detail.csv")
_OUT_DIR      = Path("results/annotation")
_TODAY        = date.today().strftime("%Y%m%d")

# ── Config ─────────────────────────────────────────────────────────────────

VARIANT       = "white_male_private"
N_CONCORDANT  = 50
N_NON_CONC    = 25
SEED          = 42

# ── Load data ──────────────────────────────────────────────────────────────

def load_concordance_index() -> dict[str, dict]:
    """Return {case_id: {scorer_concordant, nccn_category}} for white_male_private."""
    index = {}
    with open(_CONCORDANCE, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row["variant"] != VARIANT:
                continue
            conc = row["concordant"]
            if conc == "":
                continue  # skip not-scoreable
            index[row["case_id"]] = {
                "scorer_concordant": int(conc),
                "nccn_category":     row["nccn_category"],
                "ground_truth_label": "",  # filled below from checkpoint
            }
    return index


def main() -> None:
    _OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load all three sources
    checkpoint = json.loads(_CHECKPOINT.read_text(encoding="utf-8"))
    processed  = json.loads(_PROCESSED.read_text(encoding="utf-8"))
    conc_index = load_concordance_index()

    # Build clean-note lookup
    clean_notes = {c["case_id"]: c["clean_note"] for c in processed}

    # Attach ground truth from checkpoint
    for case_id, variants in checkpoint.items():
        if VARIANT in variants and case_id in conc_index:
            conc_index[case_id]["ground_truth_label"] = variants[VARIANT].get("ground_truth_label", "")

    # Stratified sampling
    concordant     = [cid for cid, d in conc_index.items() if d["scorer_concordant"] == 1]
    non_concordant = [cid for cid, d in conc_index.items() if d["scorer_concordant"] == 0]

    rng = random.Random(SEED)
    sampled_conc    = rng.sample(sorted(concordant),     min(N_CONCORDANT, len(concordant)))
    sampled_non     = rng.sample(sorted(non_concordant), min(N_NON_CONC,   len(non_concordant)))
    sampled         = sampled_conc + sampled_non
    rng.shuffle(sampled)  # mix concordant/non-concordant so order doesn't cue the annotator

    print(f"Sampled {len(sampled_conc)} concordant + {len(sampled_non)} non-concordant = {len(sampled)} cases")

    # ── Write annotation export (no ground truth) ──────────────────────────

    export_path = _OUT_DIR / f"annotation_export_{_TODAY}.csv"
    with open(export_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "row_id",
            "clinical_note",
            "llm_response",
            "nccn_concordant",   # blank — annotator fills Y / N / Uncertain
            "confidence",        # blank — annotator fills High / Medium / Low
            "notes",             # blank — free text
        ])
        for row_id, case_id in enumerate(sampled, start=1):
            clean_note   = clean_notes.get(case_id, "")
            llm_response = checkpoint[case_id][VARIANT].get("response_text", "")
            writer.writerow([row_id, clean_note, llm_response, "", "", ""])

    print(f"Annotation export : {export_path}  ({len(sampled)} rows)")

    # ── Write answer key (internal) ────────────────────────────────────────

    key_path = _OUT_DIR / f"annotation_answerkey_{_TODAY}.csv"
    with open(key_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "row_id",
            "case_id",
            "ground_truth_label",
            "nccn_category",
            "scorer_concordant",   # 1 = concordant, 0 = non-concordant
        ])
        for row_id, case_id in enumerate(sampled, start=1):
            d = conc_index[case_id]
            writer.writerow([
                row_id,
                case_id,
                d["ground_truth_label"],
                d["nccn_category"],
                d["scorer_concordant"],
            ])

    print(f"Answer key        : {key_path}  ({len(sampled)} rows)")
    print()
    print("Next step: send annotation_export CSV to oncologist.")
    print(f"After annotations return, run:")
    print(f"  python {_OUT_DIR}/compute_kappa.py --annotation {export_path}")


if __name__ == "__main__":
    main()
