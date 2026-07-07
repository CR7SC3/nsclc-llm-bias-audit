"""EquityGUIDE v2 experiment runner — clean label demographic injection.

Identical pipeline to run_experiment.py except:
  - Uses variant_injector_v2 (22 Omar-aligned label-only groups)
  - Saves checkpoints under results/baseline/ with 'v2_' prefix
  - Applies variants at runtime from processed notes (no reprocessing needed)

Variant tiers
─────────────
  A  Replicate v1 (cross-experiment comparison)      6 groups
  B  Race only — Omar et al. style                   5 groups
  C  SES only — housing / income                     3 groups
  D  Insurance only — EquityGUIDE contribution       2 groups
  E  Isolation — race vs insurance disentanglement   3 groups
  F  Gender / identity — LGBTQIA+                    3 groups
  ─────────────────────────────────────────────────────────────
  Total                                             22 groups

Usage
-----
    # Structured notes (default model = Gemini)
    python scripts/nsclc/run_experiment_v2.py --subset synthetic_structured

    # GPT-4o on unstructured
    python scripts/nsclc/run_experiment_v2.py --subset synthetic_unstructured --model gpt-4o

    # Resume an interrupted run
    python scripts/nsclc/run_experiment_v2.py --subset synthetic_structured --model gpt-4o
    # (automatically resumes from checkpoint)
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tqdm import tqdm

from src.models.factory import create_model, SUPPORTED_MODELS
from src.generate.variant_injector_v2 import create_all_variants_v2, ALL_VARIANTS_V2
from prompts.evaluation.prompt_templates import build_prompt

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

_RESULTS_DIR = Path("results")
_RESULTS_DIR.mkdir(exist_ok=True)

_PROCESSED_PATHS = {
    "synthetic_structured":   "data/processed/cancerguide_synthetic_structured_processed.json",
    "synthetic_unstructured": "data/processed/cancerguide_synthetic_unstructured_processed.json",
    # GENIE BPC NSCLC: real-derived structured profiles -> LLM-generated free-text notes.
    # Routes to unstructured injection (subset != "synthetic_structured").
    "genie_bpc_nsclc":        "data/processed/genie_bpc_nsclc_with_notes.json",
    "genie_bpc_nsclc_pilot50": "data/processed/genie_bpc_nsclc_pilot50_with_notes.json",
}


def _load_processed(subset: str) -> list[dict]:
    path = Path(_PROCESSED_PATHS[subset])
    if not path.exists():
        raise FileNotFoundError(
            f"Processed cases not found at {path}. "
            "Run `python -m src.generate.load_cases` first."
        )
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def run_experiment_v2(
    subset: str = "synthetic_structured",
    model_name: str = "gemini-2.5-flash",
) -> None:
    n_variants = len(ALL_VARIANTS_V2)

    print(f"\n{'='*70}")
    print(f"EquityGUIDE v2 — Clean Label Experiment")
    print(f"Subset    : {subset}")
    print(f"Model     : {model_name}")
    print(f"Variants  : {n_variants} (Omar-aligned label-only groups)")
    print(f"{'='*70}\n")

    # Load processed (demographics-stripped) notes
    cases = _load_processed(subset)
    label_index = {c["case_id"]: c.get("label", "") for c in cases}

    # Checkpoint path
    model_slug = model_name.replace("/", "-")
    if model_name == "gemini-2.5-flash":
        file_prefix = f"v2_{subset}"
    else:
        file_prefix = f"v2_{subset}_{model_slug}"

    strategy_dir = _RESULTS_DIR / "baseline"
    strategy_dir.mkdir(exist_ok=True)
    checkpoint_path = strategy_dir / f"{file_prefix}_checkpoint.json"

    if checkpoint_path.exists():
        with open(checkpoint_path, encoding="utf-8") as fh:
            results = json.load(fh)
        completed = set(results.keys())
        print(f"Resuming from checkpoint: {len(completed)} cases already done.")
    else:
        results = {}
        completed = set()

    remaining = [c for c in cases if c["case_id"] not in completed]
    total_calls = len(cases) * n_variants
    est_min = len(remaining) * n_variants * 1.0 / 60

    print(f"Cases     : {len(cases)} total / {len(remaining)} remaining")
    print(f"Variants  : {n_variants} per case = {total_calls} total calls")
    print(f"Est. time : ~{est_min:.0f} minutes")

    from src.models.factory import _GROQ_MODELS
    is_groq = model_name in _GROQ_MODELS

    if model_name == "gpt-4o":
        est_cost = len(remaining) * n_variants * (1500 * 2.50 + 600 * 10.0) / 1_000_000
        print(f"Est. cost : ~${est_cost:.2f} (GPT-4o @ avg 1500 input + 600 output tokens)")
    elif model_name in ("gpt-4o-mini", "gemini-2.5-flash"):
        est_cost = len(remaining) * n_variants * 0.0002
        print(f"Est. cost : ~${est_cost:.2f}")
    elif is_groq:
        print("Est. cost : free (Groq free tier)")
    print()

    # Groq free tier enforces tokens-per-minute limits; pace calls to stay under.
    # Other providers tolerate near-zero spacing.
    sleep = 6.0 if is_groq else 1.0
    model = create_model(model_name, inter_call_sleep=sleep, max_retries=5, retry_wait=30.0)

    failed = []
    start = time.time()

    pbar = tqdm(remaining, total=len(remaining), desc="v2 experiment", unit="case")

    for case in pbar:
        case_id = case["case_id"]
        base_note = case["clean_note"]
        pbar.set_postfix({"case": case_id[-20:]})

        # Generate all v2 variants for this note
        variants = create_all_variants_v2(base_note, subset)

        case_results: dict = {}
        for variant_key, note_text in variants.items():
            full_id = f"{case_id}__{variant_key}__baseline_v2"
            try:
                prompt = build_prompt("baseline", note_text)
                result = model.generate_with_retry(prompt, full_id)
                result["variant_label"] = variant_key
                result["strategy"] = "baseline_v2"
                result["base_case_id"] = case_id
                result["ground_truth_label"] = label_index.get(case_id, "")
                case_results[variant_key] = result
            except Exception as exc:
                logging.error("SKIP %s: %s", full_id, exc)
                failed.append(full_id)
                case_results[variant_key] = {"error": str(exc)}

        results[case_id] = case_results

        with open(checkpoint_path, "w", encoding="utf-8") as fh:
            json.dump(results, fh, indent=2, ensure_ascii=False)

    # Save final results
    final_path = strategy_dir / f"{file_prefix}_results.json"
    with open(final_path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, ensure_ascii=False)

    elapsed = (time.time() - start) / 60
    completed_calls = sum(
        1 for case in results.values()
        for v in case.values()
        if "error" not in v
    )

    print(f"\n{'='*70}")
    print(f"EXPERIMENT v2 COMPLETE")
    print(f"Elapsed   : {elapsed:.1f} minutes")
    print(f"Completed : {completed_calls} / {len(cases) * n_variants} calls")
    print(f"Failed    : {len(failed)}")
    print(f"Checkpoint: {checkpoint_path}")
    print(f"Results   : {final_path}")
    print(f"{'='*70}\n")
    print(f"Next step: python scripts/nsclc/analyze_results_v2.py --subset {subset} --model {model_name} --concordance --save")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="EquityGUIDE v2 — clean label demographic experiment"
    )
    parser.add_argument(
        "--subset",
        choices=["synthetic_structured", "synthetic_unstructured", "genie_bpc_nsclc", "genie_bpc_nsclc_pilot50"],
        default="synthetic_structured",
    )
    parser.add_argument(
        "--model",
        choices=SUPPORTED_MODELS,
        default="gemini-2.5-flash",
    )
    args = parser.parse_args()
    run_experiment_v2(subset=args.subset, model_name=args.model)
