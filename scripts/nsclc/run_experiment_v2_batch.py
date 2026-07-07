"""EquityGUIDE v2 — Batch API runner (Anthropic + OpenAI) for 50% cost.

Why this exists
---------------
The synchronous runner (run_experiment_v2.py) makes one HTTP call per
case x variant. For the credited GPT-4o and Claude arms, the Batch APIs cut
token cost ~50% (Anthropic Message Batches, OpenAI Batch). This runner builds
the *same* prompts, variants, and NCCN labels, submits them as one batch,
polls, then writes results into the *same* checkpoint file the sync runner uses
— so analyze_results_v2.py and every downstream step are unchanged.

Providers
---------
- Anthropic (`claude-*`): client.messages.batches  (no beta header).
- OpenAI (`gpt-*`):        client.batches + Files API, /v1/chat/completions.

Both run temperature=0, max_tokens=2048, single user message — byte-identical to
the sync wrappers (anthropic_model.py / openai_model.py).

Usage
-----
    # submit + poll to completion + write checkpoint (one shot)
    python scripts/nsclc/run_experiment_v2_batch.py --subset genie_bpc_nsclc --model claude-sonnet-4-6

    # submit only (returns immediately with a batch id), collect later:
    python scripts/nsclc/run_experiment_v2_batch.py --subset genie_bpc_nsclc --model gpt-4o --submit-only
    python scripts/nsclc/run_experiment_v2_batch.py --subset genie_bpc_nsclc --model gpt-4o --collect

State (batch id + custom_id->(case,variant) map) is saved next to the checkpoint
so --collect can resume in a later process. Resuming skips cases already complete
in the checkpoint, exactly like the sync runner.
"""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from dotenv import load_dotenv
load_dotenv()  # pick up ANTHROPIC_API_KEY / OPENAI_API_KEY from .env, like the wrappers

from run_experiment_v2 import _PROCESSED_PATHS, _load_processed, _atomic_dump, _RESULTS_DIR
from src.generate.nccn_labels import load_nccn_index, nccn_fields
from src.generate.variant_injector_v2 import create_all_variants_v2, VARIANT_GROUPS_V2
from prompts.evaluation.prompt_templates import build_prompt

MAX_TOKENS = 2048
TEMPERATURE = 0.0


# ---------------------------------------------------------------------------
# Shared task construction — identical prompts to the sync runner
# ---------------------------------------------------------------------------

def _build_tasks(subset: str, strategy: str, checkpoint_path: Path, max_cases: int = 0):
    """Return (cases, results, tasks, id_map). `tasks` is a list of
    (short_id, prompt). `id_map` maps short_id -> (case_id, variant_key).

    max_cases > 0 limits this submission to the first N not-yet-complete cases
    (cheapest-affordable chunk). The checkpoint makes the next run continue with
    the following chunk — so you can fund the arm incrementally."""
    cases = _load_processed(subset)
    nccn_index = load_nccn_index()
    label_index = {c["case_id"]: c.get("label", "") for c in cases}

    results = {}
    completed = set()
    if checkpoint_path.exists():
        results = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        completed = {
            cid for cid, cres in results.items()
            if cres and not any("error" in v for v in cres.values())
        }
        results = {cid: results[cid] for cid in completed}
    remaining = [c for c in cases if c["case_id"] not in completed]
    if max_cases and max_cases > 0:
        remaining = remaining[:max_cases]

    strategy_tag = f"{strategy}_v2"
    tasks = []
    id_map = {}
    n = 0
    for case in remaining:
        variants = create_all_variants_v2(case["clean_note"], subset)
        for variant_key, note_text in variants.items():
            short = f"t{n:06d}"
            n += 1
            id_map[short] = (case["case_id"], variant_key)
            tasks.append((short, build_prompt(strategy, note_text)))
    return cases, nccn_index, label_index, results, remaining, tasks, id_map, strategy_tag


def _assemble(results, parsed, id_map, model_name, strategy_tag, nccn_index, label_index, cases):
    """Fold parsed {short_id: {response_text, prompt_tokens,...}} into the
    checkpoint schema, grouped by case. Only cases with ALL 30 variants present
    are written (partial cases stay out so --collect/ retry is clean)."""
    by_case = {}
    for short, (case_id, variant_key) in id_map.items():
        by_case.setdefault(case_id, {})[variant_key] = parsed.get(short)

    n_variants = len(VARIANT_GROUPS_V2)
    written = 0
    for case_id, variants in by_case.items():
        if any(variants.get(v) is None for v in VARIANT_GROUPS_V2):
            continue  # incomplete — leave for a retry batch
        case_results = {}
        for variant_key in VARIANT_GROUPS_V2:
            p = variants[variant_key]
            ts = datetime.now(timezone.utc).isoformat()
            sample = {
                "response_text": p["response_text"],
                "prompt_tokens": p.get("prompt_tokens"),
                "completion_tokens": p.get("completion_tokens"),
                "total_tokens": p.get("total_tokens"),
                "timestamp": ts,
            }
            case_results[variant_key] = {
                "case_id": f"{case_id}__{variant_key}__{strategy_tag}",
                "model": model_name,
                "variant_label": variant_key,
                "strategy": strategy_tag,
                "base_case_id": case_id,
                "ground_truth_label": label_index.get(case_id, ""),
                **nccn_fields(nccn_index, case_id),
                "n_samples": 1,
                **sample,
                "samples": [sample],
            }
        results[case_id] = case_results
        written += 1
    return results, written


# ---------------------------------------------------------------------------
# Anthropic Message Batches
# ---------------------------------------------------------------------------

def _anthropic_submit(tasks, model_name):
    import anthropic
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request
    client = anthropic.Anthropic()
    requests = [
        Request(
            custom_id=short,
            params=MessageCreateParamsNonStreaming(
                model=model_name,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                messages=[{"role": "user", "content": prompt}],
            ),
        )
        for short, prompt in tasks
    ]
    batch = client.messages.batches.create(requests=requests)
    return batch.id


def _anthropic_poll(batch_id):
    import anthropic
    client = anthropic.Anthropic()
    while True:
        b = client.messages.batches.retrieve(batch_id)
        if b.processing_status == "ended":
            return
        c = b.request_counts
        print(f"  status={b.processing_status} done={c.succeeded} err={c.errored} proc={c.processing}")
        time.sleep(60)


def _anthropic_collect(batch_id):
    import anthropic
    client = anthropic.Anthropic()
    parsed = {}
    for r in client.messages.batches.results(batch_id):
        if r.result.type != "succeeded":
            continue
        msg = r.result.message
        text = next((b.text for b in msg.content if b.type == "text"), "")
        u = msg.usage
        parsed[r.custom_id] = {
            "response_text": text,
            "prompt_tokens": u.input_tokens,
            "completion_tokens": u.output_tokens,
            "total_tokens": u.input_tokens + u.output_tokens,
        }
    return parsed


# ---------------------------------------------------------------------------
# OpenAI Batch
# ---------------------------------------------------------------------------

def _openai_submit(tasks, model_name, state_dir):
    from openai import OpenAI
    client = OpenAI()
    jsonl = state_dir / "openai_input.jsonl"
    with open(jsonl, "w", encoding="utf-8") as fh:
        for short, prompt in tasks:
            fh.write(json.dumps({
                "custom_id": short,
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": model_name,
                    "max_tokens": MAX_TOKENS,
                    "temperature": TEMPERATURE,
                    "messages": [{"role": "user", "content": prompt}],
                },
            }) + "\n")
    up = client.files.create(file=open(jsonl, "rb"), purpose="batch")
    batch = client.batches.create(
        input_file_id=up.id, endpoint="/v1/chat/completions", completion_window="24h"
    )
    return batch.id


def _openai_poll(batch_id):
    from openai import OpenAI
    client = OpenAI()
    while True:
        b = client.batches.retrieve(batch_id)
        if b.status in ("completed", "failed", "expired", "cancelled"):
            if b.status != "completed":
                raise RuntimeError(f"OpenAI batch {batch_id} ended: {b.status}")
            return
        print(f"  status={b.status} counts={b.request_counts}")
        time.sleep(60)


def _openai_collect(batch_id):
    from openai import OpenAI
    client = OpenAI()
    b = client.batches.retrieve(batch_id)
    content = client.files.content(b.output_file_id).text
    parsed = {}
    for line in content.splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        resp = rec.get("response") or {}
        if resp.get("status_code") != 200:
            continue
        body = resp["body"]
        text = body["choices"][0]["message"]["content"] or ""
        u = body.get("usage", {})
        parsed[rec["custom_id"]] = {
            "response_text": text,
            "prompt_tokens": u.get("prompt_tokens"),
            "completion_tokens": u.get("completion_tokens"),
            "total_tokens": u.get("total_tokens"),
        }
    return parsed


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subset", choices=list(_PROCESSED_PATHS), required=True)
    ap.add_argument("--model", required=True, help="claude-* or gpt-* model id")
    ap.add_argument("--strategy", default="baseline")
    ap.add_argument("--submit-only", action="store_true",
                    help="submit the batch and exit (collect later with --collect)")
    ap.add_argument("--collect", action="store_true",
                    help="skip submit; poll the saved batch id and write the checkpoint")
    ap.add_argument("--max-cases", type=int, default=0,
                    help="submit only the first N not-yet-complete cases this run "
                         "(affordable chunk); re-run later to continue the next chunk")
    args = ap.parse_args()

    is_anthropic = args.model.startswith("claude")
    provider = "anthropic" if is_anthropic else "openai"

    model_slug = args.model.replace("/", "-")
    suffix = "" if args.strategy == "baseline" else f"_{args.strategy}"
    file_prefix = f"v2_{args.subset}_{model_slug}{suffix}"
    strategy_dir = _RESULTS_DIR / "baseline"
    strategy_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = strategy_dir / f"{file_prefix}_checkpoint.json"
    state_path = strategy_dir / f"{file_prefix}_batch_state.json"
    state_dir = strategy_dir

    (cases, nccn_index, label_index, results, remaining,
     tasks, id_map, strategy_tag) = _build_tasks(args.subset, args.strategy, checkpoint_path,
                                                 max_cases=args.max_cases)

    if args.collect:
        if not state_path.exists():
            raise SystemExit(f"No batch state at {state_path}; submit first.")
        state = json.loads(state_path.read_text())
        batch_id, id_map = state["batch_id"], {k: tuple(v) for k, v in state["id_map"].items()}
    else:
        print(f"Provider  : {provider}\nModel     : {args.model}\nSubset    : {args.subset}")
        print(f"Remaining : {len(remaining)} cases x {len(VARIANT_GROUPS_V2)} = {len(tasks)} requests")
        if not tasks:
            print("Nothing to do — checkpoint already complete.")
            return
        submit = _anthropic_submit if is_anthropic else (lambda t, m: _openai_submit(t, m, state_dir))
        batch_id = submit(tasks, args.model)
        state_path.write_text(json.dumps({"batch_id": batch_id, "id_map": id_map}))
        print(f"Submitted batch {batch_id}\nState saved: {state_path}")
        if args.submit_only:
            print("Exiting (--submit-only). Re-run with --collect when the batch ends.")
            return

    poll = _anthropic_poll if is_anthropic else _openai_poll
    collect = _anthropic_collect if is_anthropic else _openai_collect
    print(f"Polling batch {batch_id} ...")
    poll(batch_id)
    parsed = collect(batch_id)
    print(f"Collected {len(parsed)} successful responses.")

    results, written = _assemble(results, parsed, id_map, args.model, strategy_tag,
                                 nccn_index, label_index, cases)
    _atomic_dump(results, checkpoint_path)
    final = strategy_dir / f"{file_prefix}_results.json"
    _atomic_dump(results, final)
    print(f"Wrote {written} complete cases -> {checkpoint_path}")
    print(f"Next: python scripts/nsclc/analyze_results_v2.py --subset {args.subset} --model {args.model} --concordance --save")


if __name__ == "__main__":
    main()
