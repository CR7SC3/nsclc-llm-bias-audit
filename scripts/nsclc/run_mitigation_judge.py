#!/usr/bin/env python3
"""Blinded LLM-judge (Sonnet-4.6) over the mitigation-ladder responses — the PRIMARY
stigma estimator for analyze_mitigation_nsclc.py.

The regex stigma composite is near-tautological for the stigma_targeted arm (it forbids the
very tokens the regex counts), so the reworked mitigation analysis treats the blinded judge as
primary and regex as corroborating. This script judges every arm x case x {SES variants +
reference} response with the SAME rubric used for the Paper-1 gold-set validation
(scripts/nsclc/run_judge.py — STIGMA / APPROPRIATE / NEUTRAL, temperature 0), blinded to arm and
demographic label, and writes the nested label map the analysis loads:

    results/annotation/mitigation_judge_{model}_{subset}.json
        {arm: {case_id: {variant: "STIGMA"|"APPROPRIATE"|"NEUTRAL"}}}

Judged units = (baseline + 4 mitigation arms) x common cases x (7 SES variants + no_demographics).
For the DeepSeek 151 salvage that is ~5 x 151 x 8 = ~6,040 items. Uses the Anthropic Batch API
(50% cheaper) by default; --sync for a small synchronous run; --limit N to smoke-test N items.

Usage
-----
    python scripts/nsclc/run_mitigation_judge.py --model deepseek-chat --subset genie_bpc_nsclc_n300 --limit 8 --sync
    python scripts/nsclc/run_mitigation_judge.py --model deepseek-chat --subset genie_bpc_nsclc_n300
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
load_dotenv()

from scripts.nsclc.run_judge import _prompt, _parse, MODEL  # noqa: E402  (reuse the exact rubric)
from scripts.nsclc.analyze_mitigation_nsclc import (  # noqa: E402
    load_arms, common_cases, SES_VARIANTS, REFERENCE, ARMS,
)

JUDGE_VARIANTS = SES_VARIANTS + [REFERENCE]
SEP = "||"  # item-id separator: arm||case_id||variant


def build_items(arms: dict[str, dict], cases: list[str]) -> list[dict]:
    """One judge item per (arm, case, JUDGE_VARIANT) with a usable response_text.

    The Batch API custom_id must match ^[A-Za-z0-9_-]{1,64}$, and arm||cid||variant is both
    too long and uses illegal '|' chars, so each item gets a short surrogate id ('m<index>')
    and carries arm/cid/variant fields for reconstruction in nest()."""
    items = []
    idx = 0
    for arm in [a for a in ARMS if a in arms]:
        cp = arms[arm]
        for cid in cases:
            vmap = cp.get(cid, {})
            for variant in JUDGE_VARIANTS:
                res = vmap.get(variant, {})
                text = res.get("response_text") if isinstance(res, dict) else None
                if not text or "error" in (res or {}):
                    continue
                items.append({"id": f"m{idx}", "arm": arm, "cid": cid,
                              "variant": variant, "response_text": text})
                idx += 1
    return items


def judge_sync(items, limit=None):
    import anthropic
    client = anthropic.Anthropic()
    todo = items[:limit] if limit else items
    labels = {}
    for i, it in enumerate(todo):
        r = client.messages.create(
            model=MODEL, max_tokens=10, temperature=0,
            messages=[{"role": "user", "content": _prompt(it["response_text"])}],
        )
        labels[it["id"]] = _parse(r.content[0].text if r.content else "")
        if (i + 1) % 25 == 0:
            print(f"  judged {i+1}/{len(todo)}")
    return labels


def judge_batch(items):
    import time
    import anthropic
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request
    client = anthropic.Anthropic()
    # Anthropic batches cap at 100k requests; ~6k here fits in one batch.
    reqs = [Request(custom_id=it["id"], params=MessageCreateParamsNonStreaming(
        model=MODEL, max_tokens=10, temperature=0,
        messages=[{"role": "user", "content": _prompt(it["response_text"])}],
    )) for it in items]
    batch = client.messages.batches.create(requests=reqs)
    print(f"Submitted judge batch {batch.id} ({len(reqs)} items); polling every 30s...")
    while True:
        b = client.messages.batches.retrieve(batch.id)
        if b.processing_status == "ended":
            break
        print(f"  {b.processing_status}  succeeded={b.request_counts.succeeded} "
              f"errored={b.request_counts.errored}")
        time.sleep(30)
    labels = {}
    for r in client.messages.batches.results(batch.id):
        if r.result.type == "succeeded":
            msg = r.result.message
            labels[r.custom_id] = _parse(next((b.text for b in msg.content if b.type == "text"), ""))
    return labels


def nest(labels: dict, items: list[dict]) -> dict:
    """{item_id: LABEL} + items -> {arm: {cid: {variant: LABEL}}} via each item's fields."""
    by_id = {it["id"]: it for it in items}
    out: dict = {}
    for k, lab in labels.items():
        it = by_id.get(k)
        if not it:
            continue
        out.setdefault(it["arm"], {}).setdefault(it["cid"], {})[it["variant"]] = lab
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Blinded Sonnet judge over mitigation-ladder responses")
    ap.add_argument("--model", default="deepseek-chat")
    ap.add_argument("--subset", default="genie_bpc_nsclc_n300")
    ap.add_argument("--baseline-subset", default="genie_bpc_nsclc")
    ap.add_argument("--sync", action="store_true", help="synchronous (no Batch API)")
    ap.add_argument("--limit", type=int, default=None, help="judge only the first N items (smoke test)")
    args = ap.parse_args()

    print(f"Loading arms: model={args.model} subset={args.subset}")
    arms = load_arms(args.model, args.subset, args.baseline_subset)
    if "baseline" not in arms:
        sys.exit("ERROR: baseline arm required.")
    cases = common_cases(arms)
    items = build_items(arms, cases)
    print(f"Paired on {len(cases)} common cases; {len(items)} judge items "
          f"({len([a for a in ARMS if a in arms])} arms x cases x {len(JUDGE_VARIANTS)} variants).")

    if args.sync or args.limit:
        labels = judge_sync(items, limit=args.limit)
    else:
        labels = judge_batch(items)
    print(f"Got {len(labels)} labels.")

    out = REPO_ROOT / "results" / "annotation" / \
        f"mitigation_judge_{args.model.replace('/', '-')}_{args.subset}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    if args.limit:
        # smoke test: don't clobber a full run; write a _smoke sidecar and print a sample
        smoke = out.with_name(out.stem + "_smoke.json")
        smoke.write_text(json.dumps(nest(labels, items), indent=2))
        from collections import Counter
        print("SMOKE label distribution:", dict(Counter(labels.values())))
        print(f"Wrote smoke labels -> {smoke}")
        return
    out.write_text(json.dumps(nest(labels, items), indent=2))
    from collections import Counter
    print("Label distribution:", dict(Counter(labels.values())))
    print(f"Wrote judge labels -> {out}")
    print("Re-run analyze_mitigation_nsclc.py to pick up the PRIMARY judge estimator.")


if __name__ == "__main__":
    main()
