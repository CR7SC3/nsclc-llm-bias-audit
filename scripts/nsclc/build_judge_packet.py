"""Option-A stigma-classifier validation — build the blinded judge packet.

Purpose
-------
The strongest claim (stigmatizing language elevated for the most disadvantaged)
rests on a regex classifier (`src/analyze/soft_bias.py`). To validate it without
recruiting human raters, we have a held-out LLM judge (Claude Sonnet 4.6) label a
blinded, stratified sample of real model responses, then compare its labels to the
classifier's. A small human gold set (you, ~40 items) anchors the judge.

This script builds the packet from EXISTING results (no new audit spend):
  adjudication/judge_items.jsonl   — blinded items: id, response_text, and the
                                     classifier's verdict (hidden from the judge)
  adjudication/gold_template.csv    — 40 items for you to label by hand (blinded)

The judge never sees the variant or the classifier verdict — only the text.

Usage
-----
    python scripts/nsclc/build_judge_packet.py --per-group 30 --gold 40
"""
from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.analyze.soft_bias import detect_all

OUT = Path("adjudication")
OUT.mkdir(exist_ok=True)

SOURCES = {
    "gemini":   "results/baseline/v2_genie_bpc_nsclc_checkpoint.json",
    "deepseek": "results/baseline/v2_genie_bpc_nsclc_deepseek-chat_checkpoint.json",
}

# Stratify across the variants that matter for the stigma claim: the elevated
# groups, plus clean controls that should read ~neutral.
GROUPS = {
    "disadvantaged": ["unhoused_patient", "black_unhoused", "low_income_patient"],
    "race_only":     ["black_race_only", "hispanic_race_only", "asian_race_only"],
    "control":       ["white_male_private", "no_demographics"],
}

# The defensible "stigmatizing" composite — the classifier verdict we validate.
# Restricted to the two dims that cleanly discriminate disadvantaged from controls
# (adherence-doubt + hallucinated SDOH: ~0% in race-only & white-male controls).
# treatment_hedging/watchful_waiting were dropped — hedging fires ~70% on ALL strata
# (ordinary clinical caution, not bias), so it doesn't belong in an absolute composite.
STIGMA_DIMS = ("adherence_compliance", "sdoh_generation")


def _classifier_stigma(text: str) -> dict:
    dims = detect_all(text)
    fired = [k for k in STIGMA_DIMS if dims.get(k)]
    return {"stigma": bool(fired), "fired_dims": fired}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-group", type=int, default=30,
                    help="items sampled per (source x group-stratum)")
    ap.add_argument("--gold", type=int, default=40, help="size of the human gold set")
    ap.add_argument("--seed", type=int, default=17)
    args = ap.parse_args()
    rng = random.Random(args.seed)

    data = {name: json.loads(Path(p).read_text()) for name, p in SOURCES.items()
            if Path(p).exists()}

    items = []
    for source, ck in data.items():
        for stratum, variants in GROUPS.items():
            pool = []
            for case_id, cres in ck.items():
                for vk in variants:
                    rec = cres.get(vk)
                    if isinstance(rec, dict) and rec.get("response_text"):
                        pool.append((case_id, vk, rec["response_text"]))
            rng.shuffle(pool)
            for case_id, vk, text in pool[:args.per_group]:
                cl = _classifier_stigma(text)
                items.append({
                    "case_id": case_id,
                    # hidden metadata (NOT shown to judge): for later analysis only
                    "_source": source, "_variant": vk, "_stratum": stratum,
                    "_classifier_stigma": cl["stigma"], "_classifier_dims": cl["fired_dims"],
                    "response_text": text,
                })

    rng.shuffle(items)  # blind ordering — strata interleaved
    for i, it in enumerate(items):
        it["id"] = f"j{i:04d}"

    items_path = OUT / "judge_items.jsonl"
    with open(items_path, "w", encoding="utf-8") as fh:
        for it in items:
            fh.write(json.dumps(it) + "\n")

    # Human gold set: a blinded subset, classifier verdict withheld, for you to label.
    gold = items[:args.gold]
    gold_path = OUT / "gold_template.csv"
    with open(gold_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "your_label (STIGMA/APPROPRIATE/NEUTRAL)", "response_text"])
        for it in gold:
            w.writerow([it["id"], "", it["response_text"].replace("\n", " ")])

    n_stigma = sum(it["_classifier_stigma"] for it in items)
    print(f"Wrote {len(items)} blinded items -> {items_path}")
    print(f"  classifier flagged stigma in {n_stigma}/{len(items)} "
          f"({100*n_stigma/len(items):.0f}%)")
    by = {}
    for it in items:
        by.setdefault(it["_stratum"], [0, 0])
        by[it["_stratum"]][0] += 1
        by[it["_stratum"]][1] += it["_classifier_stigma"]
    for s, (n, k) in by.items():
        print(f"  {s:14s} n={n:3d}  classifier-stigma={k:3d} ({100*k/n:.0f}%)")
    print(f"Wrote {len(gold)}-item gold sheet -> {gold_path}")
    print("\nNext: label the gold sheet (STIGMA/APPROPRIATE/NEUTRAL), then run:")
    print("  python scripts/nsclc/run_judge.py        # Sonnet judges all items, computes agreement + kappa")


if __name__ == "__main__":
    main()
