"""EquityGUIDE — Anthropic Message Batches runner (50% cost) for Sonnet 5.

Why a separate runner
---------------------
``run_experiment_v2.py`` fires one real-time request per call through a
ThreadPoolExecutor. That is right for OpenRouter/Together/Groq, but for an
Anthropic model the Message Batches API processes the same requests
asynchronously at **50% of standard token price** — ideal for our 31,440
independent, latency-insensitive calls. This script builds the identical
prompts/variants, submits them as one (or more) batches, polls to completion,
and writes results into the **same checkpoint schema and path** as the v2
runner, so ``analyze_results_v2.py`` consumes them unchanged.

Params parity
-------------
The per-request params are byte-identical to what ``AnthropicModel`` sends for
Sonnet 5 (``model`` + ``max_tokens`` + ``messages``; temperature omitted, since
Sonnet 5 rejects sampling params and runs under adaptive thinking). We do NOT
add ``thinking``/``output_config`` here — keeping the arm comparable to the rest
of the cohort and avoiding surprise thinking-token cost. If the first batch's
output tokens come back high, add ``output_config={"effort": "low"}`` centrally.

Cost safety
-----------
The default invocation is a **dry run**: it builds every request, prints the
count and a cost estimate, and exits WITHOUT touching the API. Actual
submission requires ``--submit``. ``--limit-cases N`` bounds spend to the first
N cases of the cohort (pilot). Results write to the standard cohort checkpoint,
so a later full run resumes and skips the pilot cases already done
("top up and continue").

Usage
-----
    # Dry run — build + cost estimate, no API call (default, safe)
    python scripts/nsclc/run_experiment_batch.py --subset genie_bpc_nsclc \
        --model claude-sonnet-5 --limit-cases 30

    # Actually submit + poll + collect (spends credit)
    python scripts/nsclc/run_experiment_batch.py --subset genie_bpc_nsclc \
        --model claude-sonnet-5 --limit-cases 30 --submit

    # Collect an already-submitted batch (resume after interruption)
    python scripts/nsclc/run_experiment_batch.py --subset genie_bpc_nsclc \
        --model claude-sonnet-5 --collect
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from dotenv import load_dotenv

from src.generate.variant_injector_v2 import create_all_variants_v2, ALL_VARIANTS_V2
from src.generate.nccn_labels import load_nccn_index, nccn_fields
from prompts.evaluation.prompt_templates import build_prompt

# Reuse the v2 runner's checkpoint helpers and processed-case loader verbatim,
# so the output format and file naming stay in lockstep with the real-time arm.
from scripts.nsclc.run_experiment_v2 import (
    _atomic_dump,
    _acquire_lock,
    _load_processed,
    _RESULTS_DIR,
)

load_dotenv()

# Anthropic batch custom_id cap is 64 chars; our natural rep_ids
# (case + variant + strategy) exceed that, so we key requests by a short index
# and keep the full mapping in a sidecar manifest.
_CUSTOM_ID_FMT = "r{:06d}"

# Token averages measured from the completed llama-3.1-8B cohort (30,330
# successful calls): 741 input / 560 output per call. Used only for the dry-run
# cost estimate; real usage is read back from the batch results.
_AVG_IN, _AVG_OUT = 741, 560
# Sonnet 5 list price ($/token). Batch applies 50%.
_PRICE_IN, _PRICE_OUT = 2.0 / 1e6, 10.0 / 1e6


def _paths(subset: str, model_name: str, strategy: str):
    strategy_tag = "baseline_v2" if strategy == "baseline" else strategy
    prefix_suffix = "" if strategy == "baseline" else f"_{strategy}"
    model_slug = model_name.replace("/", "-")
    file_prefix = f"v2_{subset}_{model_slug}{prefix_suffix}"
    d = _RESULTS_DIR / "baseline"
    d.mkdir(parents=True, exist_ok=True)
    return (
        strategy_tag,
        d / f"{file_prefix}_checkpoint.json",
        d / f"{file_prefix}_batch_manifest.json",
        d / f"{file_prefix}_results.json",
    )


def _build_requests(subset, model_name, strategy, strategy_tag, n_samples,
                    max_tokens, limit_cases, completed):
    """Build (anthropic_requests, mapping) for every not-yet-done call.

    mapping: custom_id -> {case_id, variant_key, rep_id}
    Skips cases already complete in the checkpoint (resume/top-up).
    """
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request

    cases = _load_processed(subset)
    if limit_cases:
        cases = cases[:limit_cases]

    requests, mapping = [], {}
    idx = 0
    for case in cases:
        case_id = case["case_id"]
        if case_id in completed:
            continue
        base_note = case["clean_note"]
        variants = create_all_variants_v2(base_note, subset)
        for variant_key, note_text in variants.items():
            full_id = f"{case_id}__{variant_key}__{strategy_tag}"
            prompt = build_prompt(strategy, note_text)
            for rep in range(n_samples):
                rep_id = full_id if n_samples == 1 else f"{full_id}__rep{rep}"
                cid = _CUSTOM_ID_FMT.format(idx)
                idx += 1
                # Params parity with AnthropicModel for a no-temperature model:
                # model + max_tokens + messages only.
                params = MessageCreateParamsNonStreaming(
                    model=model_name,
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}],
                )
                requests.append(Request(custom_id=cid, params=params))
                mapping[cid] = {
                    "case_id": case_id,
                    "variant_key": variant_key,
                    "rep_id": rep_id,
                }
    return cases, requests, mapping


def _load_checkpoint(checkpoint_path):
    if not checkpoint_path.exists():
        return {}, set()
    import json
    with open(checkpoint_path, encoding="utf-8") as fh:
        results = json.load(fh)
    completed = {
        cid for cid, cres in results.items()
        if cres and not any("error" in v for v in cres.values())
    }
    # Drop partial cases so they are cleanly rebuilt.
    results = {cid: results[cid] for cid in completed}
    return results, completed


def _assemble_and_write(client, batch_id, mapping, cases, subset, model_name,
                        strategy_tag, n_samples, checkpoint_path, results_path,
                        label_index, nccn_index):
    """Retrieve batch results, fold them into the v2 checkpoint schema, write."""
    import json

    # Collect per (case_id, variant_key) -> sample dict
    samples = {}   # (case_id, variant_key) -> list[sample]
    n_ok = n_err = 0
    for res in client.messages.batches.results(batch_id):
        meta = mapping.get(res.custom_id)
        if meta is None:
            continue
        case_id, variant_key = meta["case_id"], meta["variant_key"]
        key = (case_id, variant_key)
        samples.setdefault(key, [])
        if res.result.type == "succeeded":
            msg = res.result.message
            text = next((b.text for b in msg.content if b.type == "text"), "")
            u = msg.usage
            samples[key].append({
                "response_text": text,
                "prompt_tokens": u.input_tokens if u else None,
                "completion_tokens": u.output_tokens if u else None,
                "total_tokens": (u.input_tokens + u.output_tokens) if u else None,
                "timestamp": datetime.utcnow().isoformat(),
            })
            n_ok += 1
        else:
            n_err += 1  # errored / expired / canceled -> leave variant to fail below

    # Load existing checkpoint (has prior completed cases) and merge.
    results, _ = _load_checkpoint(checkpoint_path)

    # Which cases did this batch touch?
    touched = {m["case_id"] for m in mapping.values()}
    for case in cases:
        case_id = case["case_id"]
        if case_id not in touched:
            continue
        variants = create_all_variants_v2(case["clean_note"], subset)
        case_results = {}
        for variant_key in variants:
            svs = samples.get((case_id, variant_key), [])
            if not svs:
                case_results[variant_key] = {"error": "all samples failed"}
                continue
            first = svs[0]
            case_results[variant_key] = {
                "case_id": f"{case_id}__{variant_key}__{strategy_tag}",
                "model": model_name,
                "variant_label": variant_key,
                "strategy": strategy_tag,
                "base_case_id": case_id,
                "ground_truth_label": label_index.get(case_id, ""),
                **nccn_fields(nccn_index, case_id),
                "n_samples": len(svs),
                "response_text": first["response_text"],
                "prompt_tokens": first["prompt_tokens"],
                "completion_tokens": first["completion_tokens"],
                "total_tokens": first["total_tokens"],
                "timestamp": first["timestamp"],
                "samples": svs,
            }
        results[case_id] = case_results

    _atomic_dump(results, checkpoint_path)
    _atomic_dump(results, results_path)
    return n_ok, n_err


def main():
    p = argparse.ArgumentParser(description="EquityGUIDE Anthropic Batch runner (50% cost)")
    p.add_argument("--subset", default="genie_bpc_nsclc")
    p.add_argument("--model", default="claude-sonnet-5")
    p.add_argument("--strategy", default="baseline")
    p.add_argument("--n-samples", type=int, default=1)
    p.add_argument("--max-tokens", type=int, default=2048,
                   help="matches the real-time arm's cap for comparability")
    p.add_argument("--limit-cases", type=int, default=None,
                   help="only the first N cases of the cohort (pilot / budget cap)")
    p.add_argument("--submit", action="store_true",
                   help="actually create the batch (default is a dry run)")
    p.add_argument("--collect", action="store_true",
                   help="retrieve+write an already-submitted batch from the manifest")
    p.add_argument("--poll-seconds", type=int, default=30)
    args = p.parse_args()

    import json
    import anthropic

    strategy_tag, checkpoint_path, manifest_path, results_path = _paths(
        args.subset, args.model, args.strategy
    )

    cases_all = _load_processed(args.subset)
    label_index = {c["case_id"]: c.get("label", "") for c in cases_all}
    nccn_index = load_nccn_index()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY not set in .env")
    client = anthropic.Anthropic(api_key=api_key)

    # ---- COLLECT mode: resume an already-submitted batch --------------------
    if args.collect:
        if not manifest_path.exists():
            raise SystemExit(f"No manifest at {manifest_path}; nothing to collect.")
        manifest = json.loads(manifest_path.read_text())
        batch_id = manifest["batch_id"]
        mapping = manifest["mapping"]
        limit_cases = manifest.get("limit_cases")
        cases = cases_all[:limit_cases] if limit_cases else cases_all
        b = client.messages.batches.retrieve(batch_id)
        print(f"Batch {batch_id}: status={b.processing_status}")
        if b.processing_status != "ended":
            print("Not finished yet. Re-run --collect later.")
            return
        n_ok, n_err = _assemble_and_write(
            client, batch_id, mapping, cases, args.subset, args.model,
            manifest["strategy_tag"], args.n_samples, checkpoint_path,
            results_path, label_index, nccn_index,
        )
        print(f"Collected: {n_ok} succeeded, {n_err} errored. -> {checkpoint_path}")
        return

    # ---- BUILD (dry run and submit share this) ------------------------------
    _, completed = _load_checkpoint(checkpoint_path)
    cases, requests, mapping = _build_requests(
        args.subset, args.model, args.strategy, strategy_tag, args.n_samples,
        args.max_tokens, args.limit_cases, completed,
    )
    n = len(requests)
    est_full = n * (_AVG_IN * _PRICE_IN + _AVG_OUT * _PRICE_OUT)
    est_batch = est_full * 0.5

    print(f"\n{'='*70}")
    print(f"EquityGUIDE — Anthropic BATCH build")
    print(f"Subset      : {args.subset}   Model: {args.model}")
    print(f"Strategy    : {strategy_tag}   n_samples: {args.n_samples}")
    print(f"Cases       : {len(cases)}"
          + (f" (limited to first {args.limit_cases})" if args.limit_cases else "")
          + f"   already-complete skipped: {len(completed)}")
    print(f"Requests    : {n}  ({len(ALL_VARIANTS_V2)} variants/case)")
    print(f"Est. cost   : ~${est_batch:.2f} batch  (~${est_full:.2f} real-time)")
    print(f"              [est. from 741 in / 560 out avg; real usage read back]")
    print(f"Checkpoint  : {checkpoint_path}")
    print(f"{'='*70}\n")

    if n == 0:
        print("Nothing to submit — all requested cases already complete.")
        return

    if not args.submit:
        print("DRY RUN (default). Nothing submitted. Re-run with --submit to spend credit.")
        return

    # ---- SUBMIT -------------------------------------------------------------
    _acquire_lock(checkpoint_path)
    print(f"Submitting {n} requests as one batch ...")
    batch = client.messages.batches.create(requests=requests)
    manifest = {
        "batch_id": batch.id,
        "created_at": datetime.utcnow().isoformat(),
        "subset": args.subset,
        "model": args.model,
        "strategy_tag": strategy_tag,
        "n_samples": args.n_samples,
        "limit_cases": args.limit_cases,
        "mapping": mapping,
    }
    _atomic_dump(manifest, manifest_path)
    print(f"Batch id    : {batch.id}   (manifest -> {manifest_path})")

    # Poll to completion (batches usually finish < 1h, max 24h).
    while True:
        b = client.messages.batches.retrieve(batch.id)
        rc = b.request_counts
        print(f"  status={b.processing_status}  "
              f"proc={rc.processing} ok={rc.succeeded} err={rc.errored}")
        if b.processing_status == "ended":
            break
        time.sleep(args.poll_seconds)

    n_ok, n_err = _assemble_and_write(
        client, batch.id, mapping, cases, args.subset, args.model,
        strategy_tag, args.n_samples, checkpoint_path, results_path,
        label_index, nccn_index,
    )
    print(f"\nDONE: {n_ok} succeeded, {n_err} errored. -> {checkpoint_path}")
    print(f"Next: python scripts/nsclc/analyze_results_v2.py "
          f"--subset {args.subset} --model {args.model} --concordance --save")


if __name__ == "__main__":
    main()
