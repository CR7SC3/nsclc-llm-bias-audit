"""Adjudicate regex-vs-judge using the human gold labels.

Once you fill in adjudication/gold_targeted.csv (STIGMA/APPROPRIATE/NEUTRAL),
this reports who the human sides with on the contested cases:

  - human vs judge agreement (+ kappa)   -> validates the judge
  - human vs regex agreement (+ kappa)    -> validates the classifier
  - on the 17 disagreement cases: human sided with JUDGE vs REGEX

This is the number that settles whether the regex over-counts (report
judge-adjudicated rates) or the judge is too lenient.

Usage
-----
    python scripts/nsclc/score_gold.py                       # uses gold_targeted.csv
    python scripts/nsclc/score_gold.py --gold gold_template.csv
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

OUT = Path("adjudication")


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", default="gold_targeted.csv")
    args = ap.parse_args()

    items = {json.loads(l)["id"]: json.loads(l) for l in (OUT / "judge_items.jsonl").read_text().splitlines() if l.strip()}
    judge = json.loads((OUT / "judge_labels.json").read_text())

    gold = {}
    with open(OUT / args.gold) as fh:
        for row in csv.DictReader(fh):
            lab = (row.get("your_label (STIGMA/APPROPRIATE/NEUTRAL)") or "").strip()
            if lab:
                gold[row["id"]] = lab
    if not gold:
        print(f"No labels filled in {args.gold} yet — add STIGMA/APPROPRIATE/NEUTRAL and rerun.")
        return

    common = [i for i in gold if i in judge]
    h = [_bin(gold[i]) for i in common]
    j = [_bin(judge[i]) for i in common]
    r = [1 if items[i]["_classifier_stigma"] else 0 for i in common]

    print(f"Gold labels: {len(gold)} | scored: {len(common)}\n")
    print(f"Human vs JUDGE:  {100*sum(x==y for x,y in zip(h,j))/len(h):.0f}%  kappa={_kappa(h,j):.3f}")
    print(f"Human vs REGEX:  {100*sum(x==y for x,y in zip(h,r))/len(h):.0f}%  kappa={_kappa(h,r):.3f}")

    # the decisive cut: contested cases where regex=STIGMA, judge!=STIGMA
    contested = [i for i in common if items[i]["_classifier_stigma"] and judge[i] != "STIGMA"]
    if contested:
        sided_judge = sum(_bin(gold[i]) == 0 for i in contested)   # human says NOT stigma -> judge right
        sided_regex = len(contested) - sided_judge                  # human says stigma -> regex right
        print(f"\n=== Contested cases (regex=STIGMA, judge=APPROPRIATE), n={len(contested)} ===")
        print(f"  human sided with JUDGE (not stigma): {sided_judge}/{len(contested)}")
        print(f"  human sided with REGEX (stigma):     {sided_regex}/{len(contested)}")
        if sided_judge > sided_regex:
            print("  -> JUDGE is more accurate: regex over-counts. Report judge-adjudicated rates.")
        elif sided_regex > sided_judge:
            print("  -> REGEX is more accurate: judge too lenient. Report regex rates (revisit composite).")
        else:
            print("  -> split: report both, discuss as a measurement-uncertainty band.")


if __name__ == "__main__":
    main()
