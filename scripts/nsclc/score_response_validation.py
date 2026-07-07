"""Score the filled response-validation sheet against the hidden answer key.

Computes:
  Parser   — accuracy, Cohen's κ, and a confusion matrix (human × parser) to expose
             systematic misparses.
  Soft-bias — per-dimension precision / recall / F1 and Cohen's κ (regex vs human),
             treating the human label as ground truth.

Optionally, pass a second filled sheet (--filled2) to also report inter-annotator
agreement (κ) — this establishes the human ceiling and, for soft bias, whether each
construct is even reliably human-labelable.

Usage
-----
    venv/bin/python scripts/nsclc/score_response_validation.py \
        --filled results/annotation/response_validation_export_YYYYMMDD.csv \
        --key    results/annotation/response_validation_answerkey_YYYYMMDD.csv
    # add --filled2 <second annotator csv> for inter-annotator κ
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.analyze.soft_bias import DIMENSIONS

SB_KEYS = [d.key for d in DIMENSIONS]


# ── helpers ──────────────────────────────────────────────────────────────────

def _read(path: Path) -> dict[str, dict]:
    with open(path, encoding="utf-8") as fh:
        return {r["row_id"]: r for r in csv.DictReader(fh)}


def _norm(s: str) -> str:
    return (s or "").strip().lower().replace(" ", "_")


def _yn(s: str) -> int | None:
    v = (s or "").strip().lower()
    if v in ("y", "yes", "1", "true", "t"):
        return 1
    if v in ("n", "no", "0", "false", "f"):
        return 0
    return None  # blank / unrecognised → excluded


def cohens_kappa(pairs: list[tuple]) -> float:
    """Cohen's κ for a list of (rater_a, rater_b) categorical labels."""
    n = len(pairs)
    if n == 0:
        return float("nan")
    labels = sorted({x for p in pairs for x in p})
    po = sum(1 for a, b in pairs if a == b) / n
    a_cnt = Counter(a for a, _ in pairs)
    b_cnt = Counter(b for _, b in pairs)
    pe = sum((a_cnt[l] / n) * (b_cnt[l] / n) for l in labels)
    return 1.0 if pe == 1.0 else (po - pe) / (1 - pe)


# ── parser scoring ───────────────────────────────────────────────────────────

def score_parser(filled: dict, key: dict) -> None:
    pairs = []          # (human, parser)
    for rid, row in filled.items():
        human = _norm(row.get("human_category"))
        if not human or rid not in key:
            continue
        parser = _norm(key[rid]["parser_category"])
        pairs.append((human, parser))

    print("\n" + "=" * 60)
    print(f"PARSER VALIDATION   (n scored = {len(pairs)})")
    print("=" * 60)
    if not pairs:
        print("  No human_category labels filled in.")
        return

    acc = sum(1 for h, p in pairs if h == p) / len(pairs)
    print(f"  Accuracy (human == parser): {acc:.1%}")
    print(f"  Cohen's κ                 : {cohens_kappa(pairs):.3f}")

    # Confusion: only show disagreements (the actionable part — systematic misparses)
    disagree = Counter((h, p) for h, p in pairs if h != p)
    if disagree:
        print("\n  Disagreements (human → parser, count):")
        for (h, p), n in sorted(disagree.items(), key=lambda kv: -kv[1]):
            print(f"    {n:>3}  {h}  →  {p}")
    else:
        print("  No disagreements.")


# ── soft-bias scoring ────────────────────────────────────────────────────────

def score_soft_bias(filled: dict, key: dict) -> None:
    print("\n" + "=" * 78)
    print("SOFT-BIAS DETECTOR VALIDATION   (human label = ground truth; regex = predictor)")
    print("=" * 78)
    print(f"  {'dimension':<24} {'n':>4} {'TP':>3} {'FP':>3} {'FN':>3} "
          f"{'prec':>6} {'recall':>7} {'F1':>6} {'κ':>6}")
    print(f"  {'-'*24} {'-'*4} {'-'*3} {'-'*3} {'-'*3} {'-'*6} {'-'*7} {'-'*6} {'-'*6}")

    for dim in SB_KEYS:
        pairs = []  # (human, regex)
        for rid, row in filled.items():
            if rid not in key:
                continue
            h = _yn(row.get(f"sb_{dim}"))
            if h is None:
                continue
            g = int(key[rid][f"regex_{dim}"])
            pairs.append((h, g))
        n = len(pairs)
        if n == 0:
            print(f"  {dim:<24} {'—':>4}")
            continue
        tp = sum(1 for h, g in pairs if h == 1 and g == 1)
        fp = sum(1 for h, g in pairs if h == 0 and g == 1)
        fn = sum(1 for h, g in pairs if h == 1 and g == 0)
        prec = tp / (tp + fp) if (tp + fp) else float("nan")
        rec  = tp / (tp + fn) if (tp + fn) else float("nan")
        f1   = (2 * prec * rec / (prec + rec)
                if prec == prec and rec == rec and (prec + rec) else float("nan"))
        kap  = cohens_kappa([(h, g) for h, g in pairs])
        def f(x): return f"{x:.2f}" if x == x else "  — "
        print(f"  {dim:<24} {n:>4} {tp:>3} {fp:>3} {fn:>3} "
              f"{f(prec):>6} {f(rec):>7} {f(f1):>6} {kap:>6.2f}")


# ── inter-annotator ──────────────────────────────────────────────────────────

def inter_annotator(f1: dict, f2: dict) -> None:
    print("\n" + "=" * 60)
    print("INTER-ANNOTATOR AGREEMENT (rater 1 vs rater 2)")
    print("=" * 60)
    common = [rid for rid in f1 if rid in f2]
    cat_pairs = [(_norm(f1[r].get("human_category")), _norm(f2[r].get("human_category")))
                 for r in common
                 if _norm(f1[r].get("human_category")) and _norm(f2[r].get("human_category"))]
    if cat_pairs:
        print(f"  Treatment category κ: {cohens_kappa(cat_pairs):.3f}  (n={len(cat_pairs)})")
    print("  Soft-bias κ per dimension:")
    for dim in SB_KEYS:
        pairs = []
        for r in common:
            a, b = _yn(f1[r].get(f"sb_{dim}")), _yn(f2[r].get(f"sb_{dim}"))
            if a is not None and b is not None:
                pairs.append((a, b))
        if pairs:
            print(f"    {dim:<24} κ={cohens_kappa(pairs):>6.2f}  (n={len(pairs)})")


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--filled", required=True, help="Filled annotator sheet CSV")
    ap.add_argument("--key", required=True, help="Hidden answer key CSV")
    ap.add_argument("--filled2", help="Optional second annotator sheet for inter-annotator κ")
    args = ap.parse_args()

    filled = _read(Path(args.filled))
    key    = _read(Path(args.key))

    score_parser(filled, key)
    score_soft_bias(filled, key)
    if args.filled2:
        inter_annotator(filled, _read(Path(args.filled2)))


if __name__ == "__main__":
    main()
