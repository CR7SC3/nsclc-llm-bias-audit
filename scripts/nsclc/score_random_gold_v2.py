"""Two-rater RANDOM gold-set adjudication for Paper 1 (NSCLC).

Companion to `scripts/nsclc/build_random_gold_v2.py`. Back-ports the BRCA/PANC
two-rater scoring (`scripts/brca_panc/score_gold_v2.py`) to NSCLC's random,
unenriched validation sample, so the original single-rater limitation flagged in
`adjudication/VALIDATION_SUMMARY.md` can finally be reported with an inter-rater
kappa.

Reports, in order:
  1. Rater 1 vs Rater 2  — inter-rater reliability (the headline number).
  2. Rater-consensus vs JUDGE       — validates the Sonnet judge.
  3. Rater-consensus vs CLASSIFIER  — validates the regex composite.

Consensus rule (explicit, matching the BRCA/PANC scorer): on the binary
STIGMA-vs-not collapse, consensus = the shared label for items where
rater1 == rater2. Items where the raters disagree have no consensus label and
are excluded from the consensus comparisons, but the disagreement RATE is
reported explicitly — it is part of the reliability picture, not noise to hide.

Unlike the targeted set's `score_gold.py`, there is no "contested-case" cut here:
this sample is a uniform random draw, so the classifier base rate it yields is a
prevalence estimate, and the interesting question is reliability, not which side
wins on enriched edge cases.

Usage
-----
    python scripts/nsclc/score_random_gold_v2.py
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

OUT = Path("adjudication")
KAPPA_TARGET = 0.60  # same substantial-agreement bar used for BRCA/PANC


def _bin(lab: str) -> int:
    return 1 if "STIGMA" in (lab or "").strip().upper() else 0


def _kappa(a, b):
    n = len(a)
    if not n:
        return float("nan")
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return (po - pe) / (1 - pe) if pe != 1 else 1.0


_LABEL_COL = {
    "random":  "your_label (STIGMA/APPROPRIATE/NEUTRAL)",
    "flagged": "your_label (APPROPRIATE/STIGMA)",
}


def _read_gold(path: Path, label_col: str) -> dict:
    gold = {}
    if not path.exists():
        return gold
    with open(path) as fh:
        for row in csv.DictReader(fh):
            lab = (row.get(label_col) or "").strip()
            if lab:
                gold[row["id"]] = lab
    return gold


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold-tag", default="random", choices=["random", "flagged"],
                    help="'random' = full uniform sample (STIGMA/APPROPRIATE/NEUTRAL); "
                         "'flagged' = classifier-flagged-only APPROPRIATE-vs-STIGMA set. "
                         "Selects the gold_{tag}_rater{1,2}.csv sheets and, unless "
                         "overridden, the matching {tag}_judge_items.jsonl / "
                         "{tag}_judge_labels.json.")
    ap.add_argument("--items", default=None,
                    help="override the blinded-items file (default: {gold-tag}_judge_items.jsonl)")
    ap.add_argument("--labels", default=None,
                    help="override the Sonnet judge-labels file "
                         "(default: {gold-tag}_judge_labels.json); optional.")
    args = ap.parse_args()

    tag = args.gold_tag
    items_path = OUT / (args.items or f"{tag}_judge_items.jsonl")
    labels_path = OUT / (args.labels or f"{tag}_judge_labels.json")
    r1_path = OUT / f"gold_{tag}_rater1.csv"
    r2_path = OUT / f"gold_{tag}_rater2.csv"

    if not items_path.exists():
        print(f"no {items_path} — run build_random_gold_v2.py first.")
        return

    items = {json.loads(l)["id"]: json.loads(l)
             for l in items_path.read_text().splitlines() if l.strip()}
    judge = json.loads(labels_path.read_text()) if labels_path.exists() else {}
    label_col = _LABEL_COL[tag]
    r1 = _read_gold(r1_path, label_col)
    r2 = _read_gold(r2_path, label_col)

    if not r1 or not r2:
        missing = [p.name for p, g in ((r1_path, r1), (r2_path, r2)) if not g]
        print(f"Rater labels not yet complete: {', '.join(missing)} unfilled/missing.")
        print(f"  (rater1 labeled: {len(r1)}, rater2 labeled: {len(r2)}) "
              f"— cannot compute inter-rater kappa until both raters finish.")
        return

    # ── Rater-vs-rater reliability (headline) ───────────────────────────────
    common = sorted(set(r1) & set(r2))
    if not common:
        print("No overlapping items between rater1 and rater2 — cannot score.")
        return
    a = [_bin(r1[i]) for i in common]
    b = [_bin(r2[i]) for i in common]
    agree_rr = sum(x == y for x, y in zip(a, b)) / len(common)
    kappa_rr = _kappa(a, b)
    print(f"=== Rater 1 vs Rater 2 (n={len(common)}) ===")
    print(f"  agreement: {100*agree_rr:.1f}%   Cohen's kappa: {kappa_rr:.3f}   "
          f"(target >= {KAPPA_TARGET:.2f})")
    print("  -> MEETS substantial-agreement bar." if kappa_rr >= KAPPA_TARGET
          else "  -> BELOW substantial-agreement bar; interpret validated rates "
               "with caution (more rater training / rubric clarification / third "
               "adjudicator). FLAG for study-team decision — not resolved here.")

    # ── Consensus ───────────────────────────────────────────────────────────
    agree_ids = [i for i in common if _bin(r1[i]) == _bin(r2[i])]
    disagree_rate = 1 - len(agree_ids) / len(common)
    consensus = {i: _bin(r1[i]) for i in agree_ids}
    print(f"\n  Consensus available for {len(agree_ids)}/{len(common)} items "
          f"({100*disagree_rate:.1f}% rater disagreement, excluded below).")
    prev = sum(consensus.values()) / len(consensus) if consensus else float("nan")
    print(f"  Consensus STIGMA prevalence: {100*prev:.1f}% "
          f"({sum(consensus.values())}/{len(consensus)}) "
          f"— human-validated estimate on the random sample.")

    # ── Consensus vs judge ──────────────────────────────────────────────────
    if judge:
        cj = [i for i in consensus if i in judge]
        if cj:
            cg = [consensus[i] for i in cj]
            jg = [_bin(judge[i]) for i in cj]
            print(f"\n=== Rater-consensus vs JUDGE (n={len(cj)}) ===")
            print(f"  agreement: {100*sum(x==y for x,y in zip(cg,jg))/len(cj):.1f}%   "
                  f"Cohen's kappa: {_kappa(cg, jg):.3f}")
        else:
            print("\n  (no overlap between consensus items and judge labels)")
    else:
        print(f"\n  no {labels_path.name} — run "
              f"`run_judge.py --items {args.items}` for judge-vs-consensus.")

    # ── Consensus vs classifier ─────────────────────────────────────────────
    cc = [i for i in consensus if i in items]
    if cc:
        cg = [consensus[i] for i in cc]
        rg = [1 if items[i]["_classifier_stigma"] else 0 for i in cc]
        print(f"\n=== Rater-consensus vs CLASSIFIER (n={len(cc)}) ===")
        print(f"  agreement: {100*sum(x==y for x,y in zip(cg,rg))/len(cc):.1f}%   "
              f"Cohen's kappa: {_kappa(cg, rg):.3f}")


if __name__ == "__main__":
    main()
