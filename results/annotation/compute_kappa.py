"""Compute Cohen's kappa between NCCN scorer and oncologist annotations.

Usage
-----
    # After oncologist fills in the annotation export CSV:
    python results/annotation/compute_kappa.py \\
        --annotation results/annotation/annotation_export_20260605.csv

    # With multiple annotators (pass each filled CSV):
    python results/annotation/compute_kappa.py \\
        --annotation annotator1.csv annotator2.csv annotator3.csv
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np


def _load_annotation(path: Path) -> dict[int, str]:
    """Return {row_id: oncologist_label} where label is Y/N/Uncertain."""
    out = {}
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            label = row.get("nccn_concordant", "").strip()
            if label:
                out[int(row["row_id"])] = label.upper()
    return out


def _load_answerkey(annotation_path: Path) -> dict[int, int]:
    """Find the matching answer key and return {row_id: scorer_concordant}."""
    # Infer answer key path from annotation path
    stem = annotation_path.stem.replace("annotation_export", "annotation_answerkey")
    key_path = annotation_path.parent / f"{stem}.csv"
    if not key_path.exists():
        raise FileNotFoundError(f"Answer key not found: {key_path}")
    out = {}
    with open(key_path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            out[int(row["row_id"])] = int(row["scorer_concordant"])
    return out


def _to_binary(label: str) -> int | None:
    """Map oncologist label to binary. Uncertain → None (excluded from kappa)."""
    if label in ("Y", "YES"):
        return 1
    if label in ("N", "NO"):
        return 0
    return None  # Uncertain


def cohen_kappa(y1: list[int], y2: list[int]) -> float:
    """Cohen's kappa for two binary label lists."""
    n = len(y1)
    if n == 0:
        return 0.0
    po = sum(a == b for a, b in zip(y1, y2)) / n
    p1 = (sum(y1) / n) * (sum(y2) / n)
    p0 = ((n - sum(y1)) / n) * ((n - sum(y2)) / n)
    pe = p1 + p0
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def bootstrap_kappa_ci(
    y1: list[int], y2: list[int], n_boot: int = 2000, seed: int = 42
) -> tuple[float, float]:
    """95% CI for kappa via bootstrap."""
    rng = np.random.default_rng(seed)
    arr1, arr2 = np.array(y1), np.array(y2)
    kappas = []
    for _ in range(n_boot):
        idx = rng.integers(0, len(arr1), len(arr1))
        kappas.append(cohen_kappa(arr1[idx].tolist(), arr2[idx].tolist()))
    kappas_sorted = sorted(kappas)
    lo = kappas_sorted[int(0.025 * n_boot)]
    hi = kappas_sorted[int(0.975 * n_boot)]
    return lo, hi


def run(annotation_paths: list[Path]) -> None:
    first_path = annotation_paths[0]
    key = _load_answerkey(first_path)

    print(f"\n{'='*60}")
    print("EquityGUIDE — Oncologist Annotation Kappa Report")
    print(f"{'='*60}")

    annotator_labels: list[dict[int, int]] = []

    for path in annotation_paths:
        raw = _load_annotation(path)
        binary = {rid: _to_binary(lbl) for rid, lbl in raw.items()}
        # Rows where oncologist gave Y or N (exclude Uncertain)
        judged = {rid: v for rid, v in binary.items() if v is not None}
        annotator_labels.append(judged)

        # Compute kappa vs scorer
        shared = sorted(set(judged) & set(key))
        scorer_vals = [key[r] for r in shared]
        onc_vals    = [judged[r] for r in shared]
        kappa = cohen_kappa(scorer_vals, onc_vals)
        ci_lo, ci_hi = bootstrap_kappa_ci(scorer_vals, onc_vals)
        uncertain = sum(1 for lbl in raw.values() if _to_binary(lbl) is None)
        agreement = sum(s == o for s, o in zip(scorer_vals, onc_vals)) / len(shared) if shared else 0

        print(f"\nAnnotator: {path.name}")
        print(f"  Judged cases     : {len(shared)} / {len(raw)} (excluded {uncertain} Uncertain)")
        print(f"  Raw agreement    : {agreement:.1%}")
        print(f"  Cohen's kappa    : {kappa:.3f}  95% CI [{ci_lo:.3f}, {ci_hi:.3f}]")
        if kappa >= 0.80:
            print(f"  Verdict          : PASS (≥0.80 — substantial/almost perfect agreement)")
        elif kappa >= 0.60:
            print(f"  Verdict          : MARGINAL (0.60–0.79 — moderate agreement, review edge cases)")
        else:
            print(f"  Verdict          : FAIL (<0.60 — scorer needs recalibration)")

        # Breakdown by category
        cats: dict[str, list] = {}
        with open(first_path.parent / first_path.name.replace("export", "answerkey"), newline="") as fh:
            for row in csv.DictReader(fh):
                rid = int(row["row_id"])
                if rid in shared:
                    cat = row["nccn_category"]
                    cats.setdefault(cat, []).append((key[rid], judged[rid]))

        print(f"\n  Agreement by treatment category:")
        for cat, pairs in sorted(cats.items()):
            agree = sum(s == o for s, o in pairs) / len(pairs)
            print(f"    {cat:<30} {agree:.0%}  (n={len(pairs)})")

    # Inter-annotator kappa (if multiple annotators)
    if len(annotator_labels) > 1:
        print(f"\n  Inter-annotator kappa (pairwise):")
        for i in range(len(annotator_labels)):
            for j in range(i + 1, len(annotator_labels)):
                shared = sorted(set(annotator_labels[i]) & set(annotator_labels[j]))
                v1 = [annotator_labels[i][r] for r in shared]
                v2 = [annotator_labels[j][r] for r in shared]
                k = cohen_kappa(v1, v2)
                print(f"    Annotator {i+1} vs {j+1}: κ={k:.3f}  (n={len(shared)})")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--annotation", nargs="+", required=True, help="Filled annotation CSV(s)")
    args = parser.parse_args()
    run([Path(p) for p in args.annotation])
