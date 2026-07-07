"""Test-retest noise floor: re-run the SAME no_demographics input K times at
temp 0 and measure how often the parsed recommendation changes with NO input
change. This is the missing measurement the review panel demanded — it tells us
how much of the ~13-18% demographic 'flip rate' is intrinsic model
non-determinism vs. real demographic sensitivity.

Usage:  ./venv/bin/python scripts/nsclc/test_retest.py --model deepseek-chat --n 250 --k 3
"""
from __future__ import annotations

import argparse
import json
import random
from concurrent.futures import ThreadPoolExecutor
from itertools import combinations
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.models.factory import create_model
from src.generate.variant_injector_v2 import create_all_variants_v2
from prompts.evaluation.prompt_templates import build_prompt
from src.analyze.response_parser import ResponseParser

REF = "no_demographics"
SUBSET = "genie_bpc_nsclc"
CASES_PATH = "data/processed/genie_bpc_nsclc_with_notes.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--n", type=int, default=250, help="cases to sample")
    ap.add_argument("--k", type=int, default=3, help="repeats per case")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    cases = json.loads(Path(CASES_PATH).read_text())
    cases = cases if isinstance(cases, list) else list(cases.values())
    random.seed(args.seed)
    sample = random.sample(cases, min(args.n, len(cases)))

    model = create_model(args.model, temperature=0)
    parser = ResponseParser()

    # Build the no_demographics prompt for each sampled case
    prompts = {}
    for c in sample:
        cid = c["case_id"]
        note = create_all_variants_v2(c["clean_note"], SUBSET)[REF]
        prompts[cid] = build_prompt("baseline", note)

    # K independent calls per case, parallel
    tasks = [(cid, rep) for cid in prompts for rep in range(args.k)]

    def call(t):
        cid, rep = t
        try:
            r = model.generate_with_retry(prompts[cid], f"{cid}__retest_rep{rep}")
            cat = parser.parse(r.get("response_text", "")).category
            return cid, cat
        except Exception as e:
            return cid, f"ERROR:{e}"[:40]

    results: dict[str, list[str]] = {cid: [] for cid in prompts}
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        for cid, cat in ex.map(call, tasks):
            results[cid].append(cat)

    # Metrics
    usable = {cid: cats for cid, cats in results.items()
              if len(cats) == args.k and all(not c.startswith("ERROR") and c != "unknown" for c in cats)}
    n_usable = len(usable)
    consistent = sum(1 for cats in usable.values() if len(set(cats)) == 1)
    # pairwise self-flip rate (directly comparable to the demographic flip rate)
    pair_total = pair_diff = 0
    for cats in usable.values():
        for a, b in combinations(cats, 2):
            pair_total += 1
            if a != b:
                pair_diff += 1
    self_flip = pair_diff / pair_total if pair_total else 0.0

    print("=" * 70)
    print(f"TEST-RETEST NOISE FLOOR — {args.model}  (k={args.k}, sampled {len(sample)} cases)")
    print("=" * 70)
    print(f"usable cases (k clean, non-unknown parses): {n_usable}")
    print(f"fully self-consistent (all {args.k} agree):  {consistent}/{n_usable} "
          f"({100*consistent/n_usable:.1f}%)" if n_usable else "n/a")
    print(f"SELF-FLIP RATE (pairwise disagreement):     {100*self_flip:.1f}%  "
          f"({pair_diff}/{pair_total} pairs)")
    print()
    print(f"  -> Demographic flip rate for this model is ~13-19%. If self-flip is")
    print(f"     ~0%, that whole range is real demographic effect. If self-flip is")
    print(f"     close to 13-19%, much of it is intrinsic non-determinism.")
    # save raw
    out = Path(f"results/baseline/retest_{args.model.replace('/','-')}.json")
    out.write_text(json.dumps(results, indent=2))
    print(f"\nsaved: {out}")


if __name__ == "__main__":
    main()
