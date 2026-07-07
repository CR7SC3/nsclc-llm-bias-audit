"""Resilient chunked GPT-4o batch driver (respects OpenAI tier-1 enqueued-token cap).

OpenAI tier-1 caps enqueued batch tokens at 1,350,000. One ~6k-request batch
reserves ~17M (input + max_tokens), so we submit in ~14-case chunks (420 reqs ~
1.2M tokens) sequentially: submit -> poll -> collect -> checkpoint -> next chunk.
Transient APIConnectionErrors are retried with backoff (the failure that killed
the bash loop). Writes to the same checkpoint analyze_results_v2 / finalize_panel
read. Resumes from checkpoint, so safe to re-run.

Usage
-----
    python scripts/nsclc/run_gpt4o_chunked.py --target 196 --chunk 14
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from dotenv import load_dotenv
load_dotenv()

import run_experiment_v2_batch as R

MODEL = "gpt-4o"
STRAT = "baseline"


class FundingExhausted(RuntimeError):
    """Raised when OpenAI reports insufficient_quota / billing_hard_limit."""


def _is_funding_error(e) -> bool:
    code = getattr(e, "code", "") or ""
    msg = str(e).lower()
    return ("insufficient_quota" in str(code).lower()
            or "insufficient_quota" in msg
            or "billing" in msg and "limit" in msg)


def _retry(fn, *a, tries=5, base=8, **k):
    import openai
    for i in range(tries):
        try:
            return fn(*a, **k)
        except (openai.APIConnectionError, openai.InternalServerError, openai.RateLimitError) as e:
            if _is_funding_error(e):
                raise FundingExhausted(str(e))
            wait = base * (2 ** i)
            print(f"  transient {type(e).__name__}; retry {i+1}/{tries} in {wait}s")
            time.sleep(wait)
    raise RuntimeError("retries exhausted")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subset", default="genie_bpc_nsclc_n300")
    ap.add_argument("--target", type=int, default=196)
    ap.add_argument("--chunk", type=int, default=14)
    args = ap.parse_args()

    SUBSET = args.subset
    CK = Path(f"results/baseline/v2_{SUBSET}_gpt-4o_checkpoint.json")
    RESULTS = Path(f"results/baseline/v2_{SUBSET}_gpt-4o_results.json")

    while True:
        (cases, nccn_index, label_index, results, remaining,
         tasks, id_map, tag) = R._build_tasks(SUBSET, STRAT, CK, max_cases=args.chunk)
        done = len(results)
        if done >= args.target or not tasks:
            print(f"Done: {done} cases complete (target {args.target}).")
            break
        print(f"[{done}/{args.target}] submitting chunk of {len(remaining)} cases ({len(tasks)} reqs)...")
        try:
            bid = _retry(R._openai_submit, tasks, MODEL, Path("results/baseline"))
            print(f"  batch {bid}; polling...")
            _retry(R._openai_poll, bid)
            parsed = _retry(R._openai_collect, bid)
        except FundingExhausted as e:
            R._atomic_dump(results, CK)
            R._atomic_dump(results, RESULTS)
            print(f"FUNDING EXHAUSTED at {len(results)} cases: {e}")
            return
        results, written = R._assemble(results, parsed, id_map, MODEL, tag,
                                       nccn_index, label_index, cases)
        R._atomic_dump(results, CK)
        print(f"  collected {len(parsed)} resps -> +{written} cases (total {len(results)})")

    R._atomic_dump(results, RESULTS)
    print("GPT-4o chunked run complete.")


if __name__ == "__main__":
    main()
