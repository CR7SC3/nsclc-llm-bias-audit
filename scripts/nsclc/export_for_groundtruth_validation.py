"""Export GENIE BPC NSCLC cases for oncologist validation of the GROUND-TRUTH labels.

This validates the *treatment recommendation label* (clinical_ground_truth), not the
realism of the note. The oncologist reads each note and judges whether the proposed
guideline-concordant treatment is correct.

Input : data/processed/genie_nsclc_notes_groundtruth.csv
Output (results/annotation/):
  groundtruth_validation_export_YYYYMMDD.csv  — sent to oncologist (note + proposed label + blank rating cols)
  groundtruth_validation_review_YYYYMMDD.md   — human-readable, one case per section

Notes
-----
* `actual_treatment` is intentionally EXCLUDED. The GENIE BPC cohort predates the
  2025 NCCN standard the ground truth is built against, so the historically-given
  treatment would mislead the reviewer rather than help.
* Sampling is proportional to clinical_ground_truth category frequency, with a floor
  of `--floor` cases per category so the validated accuracy reflects the real dataset
  composition while still covering every regimen. Seed=42 for reproducibility.

Usage
-----
    venv/bin/python scripts/nsclc/export_for_groundtruth_validation.py
    venv/bin/python scripts/nsclc/export_for_groundtruth_validation.py --n 50 --floor 2
"""

from __future__ import annotations

import argparse
import csv
import random
from collections import defaultdict
from datetime import date
from pathlib import Path

# ── Paths / config ───────────────────────────────────────────────────────────

_SRC_CSV = Path("data/processed/genie_nsclc_notes_groundtruth.csv")
_OUT_DIR = Path("results/annotation")
_TODAY   = date.today().strftime("%Y%m%d")
SEED     = 42

# Columns the oncologist fills in. Allowed values documented in the review .md.
_RATING_COLS = [
    "label_agreement",      # Agree | Acceptable-not-preferred | Disagree
    "preferred_treatment",  # free text — only if Disagree
    "note_sufficiency",     # Yes | Partial | No  (enough info to recommend?)
    "confidence",           # 1=Low | 2=Medium | 3=High
    "case_complexity",      # Easy | Moderate | Complex
    "reviewer_comments",    # free text
]

# Columns the oncologist SEES (note context + proposed label). No actual_treatment.
_CONTEXT_COLS = [
    "stage",
    "histology",
    "clinical_ground_truth",
    "nccn_acceptable_answers",
    "note_text",
]


# ── Sampling ─────────────────────────────────────────────────────────────────

def stratified_sample(rows: list[dict], n_target: int, floor: int,
                      rng: random.Random) -> list[dict]:
    """Allocate `n_target` cases across treatment categories proportional to their
    frequency, with a minimum of `floor` per category so every regimen is covered.
    This keeps the validated accuracy representative of the overall dataset."""

    by_cat: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_cat[r["clinical_ground_truth"].strip()].append(r)

    total = sum(len(v) for v in by_cat.values())

    # Floor first (capped at what each category actually has).
    alloc: dict[str, int] = {c: min(floor, len(v)) for c, v in by_cat.items()}

    # Distribute the remaining budget proportionally, one seat at a time, to the
    # category with the largest under-allocation relative to its proportional share.
    while sum(alloc.values()) < n_target:
        if all(alloc[c] >= len(by_cat[c]) for c in by_cat):
            break  # exhausted every pool
        target_share = {c: n_target * len(v) / total for c, v in by_cat.items()}
        cat = max(
            (c for c in by_cat if alloc[c] < len(by_cat[c])),
            key=lambda c: target_share[c] - alloc[c],
        )
        alloc[cat] += 1

    sample: list[dict] = []
    for cat, pool in by_cat.items():
        picks = sorted(pool, key=lambda r: r["case_id"])
        rng.shuffle(picks)
        sample.extend(picks[: alloc[cat]])

    rng.shuffle(sample)
    return sample


# ── Writers ──────────────────────────────────────────────────────────────────

def write_export_csv(rows: list[dict], path: Path) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["row_id", "case_id"] + _CONTEXT_COLS + _RATING_COLS)
        for i, r in enumerate(rows, start=1):
            w.writerow(
                [i, r["case_id"]]
                + [r["stage"], r["histology"], r["clinical_ground_truth"],
                   r["nccn_acceptable_answers"], r["query"]]
                + [""] * len(_RATING_COLS)
            )


def write_review_md(rows: list[dict], path: Path) -> None:
    lines = [
        "# GENIE BPC NSCLC — Oncologist Ground-Truth Validation",
        "",
        f"**Date:** {_TODAY}  |  **N:** {len(rows)} cases  |  **Seed:** {SEED}",
        "",
        "## Task",
        "",
        "For each case, read the clinical note and judge whether the **proposed treatment**",
        "(the guideline-concordant ground-truth label) is correct for this patient. The",
        "historically-administered treatment is deliberately omitted — these cases predate",
        "the 2025 standard, so it would mislead rather than help.",
        "",
        "## Fields to complete",
        "",
        "| Field | Allowed values |",
        "|---|---|",
        "| `label_agreement` | **Agree** / **Acceptable-not-preferred** / **Disagree** |",
        "| `preferred_treatment` | free text — fill only if Disagree |",
        "| `note_sufficiency` | **Yes** / **Partial** / **No** (enough info to recommend?) |",
        "| `confidence` | **1** Low / **2** Medium / **3** High |",
        "| `case_complexity` | **Easy** / **Moderate** / **Complex** |",
        "| `reviewer_comments` | free text |",
        "",
        "---",
        "",
    ]
    for i, r in enumerate(rows, start=1):
        lines += [
            f"## Case {i}",
            "",
            f"**Stage:** {r['stage']}  |  **Histology:** {r['histology']}",
            "",
            "### Clinical Note",
            "",
            r["query"].strip(),
            "",
            "### Proposed Ground Truth",
            "",
            f"**Recommended treatment:** {r['clinical_ground_truth']}",
            "",
            f"**Also NCCN-acceptable:** {r['nccn_acceptable_answers']}",
            "",
            "### Your Assessment",
            "",
            "| Field | Your answer |",
            "|---|---|",
            "| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |",
            "| Preferred treatment (if disagree) |  |",
            "| Note sufficiency (Yes / Partial / No) |  |",
            "| Confidence (1–3) |  |",
            "| Case complexity (Easy / Moderate / Complex) |  |",
            "| Comments |  |",
            "",
            "---",
            "",
        ]
    path.write_text("\n".join(lines), encoding="utf-8")


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, default=50,
                    help="Total cases to sample. Default 50.")
    ap.add_argument("--floor", type=int, default=2,
                    help="Minimum cases per treatment category. Default 2.")
    args = ap.parse_args()

    _OUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(_SRC_CSV, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    print(f"Loaded {len(rows)} cases from {_SRC_CSV}")

    rng = random.Random(SEED)
    sample = stratified_sample(rows, args.n, args.floor, rng)

    # Strata summary
    from collections import Counter
    cats = Counter(r["clinical_ground_truth"].strip() for r in sample)
    print(f"\nSampled {len(sample)} cases across {len(cats)} treatment categories:")
    for cat, n in cats.most_common():
        print(f"  {n:>3}  {cat}")

    export_path = _OUT_DIR / f"groundtruth_validation_export_{_TODAY}.csv"
    review_path = _OUT_DIR / f"groundtruth_validation_review_{_TODAY}.md"
    write_export_csv(sample, export_path)
    write_review_md(sample, review_path)

    print(f"\nExport CSV : {export_path}  ({len(sample)} rows)")
    print(f"Review doc : {review_path}")
    print("\nNext: send either file to the oncologist; CSV is spreadsheet-friendly,")
    print("the .md is easier to read case-by-case.")


if __name__ == "__main__":
    main()
