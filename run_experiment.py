"""Full CancerGUIDE experiment runner.

Runs all cases in the CancerGUIDE dataset through a chosen LLM under the
baseline prompting strategy, across all 6 demographic variants.

Usage
-----
    # Gemini (default)
    python run_experiment.py --subset synthetic_structured

    # OpenAI
    python run_experiment.py --subset synthetic_structured --model gpt-4o
    python run_experiment.py --subset synthetic_structured --model o1

    # Anthropic
    python run_experiment.py --subset synthetic_structured --model claude-opus-4-8
    python run_experiment.py --subset synthetic_structured --model claude-sonnet-4-6

    # Both subsets
    python run_experiment.py --subset both --model gpt-4o

    # All strategies (much longer)
    python run_experiment.py --subset synthetic_structured --all-strategies
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from tqdm import tqdm

from src.generate.load_cases import load_cancerguide, cases_to_runner_format
from src.models.factory import create_model, SUPPORTED_MODELS
from prompts.evaluation.prompt_templates import build_prompt

logging.basicConfig(
    level=logging.WARNING,  # suppress INFO noise during long runs
    format="%(asctime)s [%(levelname)s] %(message)s",
)

_RESULTS_DIR = Path("results")
_RESULTS_DIR.mkdir(exist_ok=True)


def run_experiment(
    subset: str = "synthetic_structured",
    strategies: list[str] = None,
    model_name: str = "gemini-2.5-flash",
) -> None:
    """Run the full CancerGUIDE experiment for a given subset and strategy list."""
    strategies = strategies or ["baseline"]

    print(f"\n{'='*65}")
    print(f"EquityGUIDE — CancerGUIDE Experiment")
    print(f"Subset    : {subset}")
    print(f"Model     : {model_name}")
    print(f"Strategies: {strategies}")
    print(f"{'='*65}\n")

    # ------------------------------------------------------------------
    # Load data (from cache if already downloaded)
    # ------------------------------------------------------------------
    print("Loading CancerGUIDE cases...")
    processed_cases = load_cancerguide(
        subset,
        save_raw=False,       # already saved from previous run
        save_processed=False,
        save_variants=False,
    )
    cases = cases_to_runner_format(processed_cases)

    # Build ground-truth label index for concordance checking
    label_index = {c["case_id"]: c["label"] for c in processed_cases}

    # ------------------------------------------------------------------
    # Initialise model via factory
    # ------------------------------------------------------------------
    model = create_model(
        model_name,
        inter_call_sleep=1.0,
        max_retries=3,
        retry_wait=30.0,
    )

    # ------------------------------------------------------------------
    # Run experiment
    # ------------------------------------------------------------------
    all_results = {}
    failed_cases = []
    start_time = time.time()

    for strategy in strategies:
        strategy_dir = _RESULTS_DIR / strategy
        strategy_dir.mkdir(exist_ok=True)
        # Include model slug in filename so multi-model runs don't overwrite each other.
        # Gemini keeps the legacy name for backwards compatibility.
        model_slug = model_name.replace("/", "-")
        if model_name == "gemini-2.5-flash":
            file_prefix = subset
        else:
            file_prefix = f"{subset}_{model_slug}"
        checkpoint_path = strategy_dir / f"{file_prefix}_checkpoint.json"

        # Resume from checkpoint if one exists
        if checkpoint_path.exists():
            with open(checkpoint_path, encoding="utf-8") as fh:
                strategy_results = json.load(fh)
            completed_ids = set(strategy_results.keys())
            print(f"Resuming from checkpoint: {len(completed_ids)} cases already done.")
        else:
            strategy_results = {}
            completed_ids = set()

        remaining = {k: v for k, v in cases.items() if k not in completed_ids}
        total_calls = (len(completed_ids) + len(remaining)) * 6 * len(strategies)
        est_minutes = len(remaining) * 6 * 1.0 / 60
        print(f"Cases     : {len(cases)} total / {len(remaining)} remaining")
        print(f"Variants  : 6")
        print(f"Est. time : ~{est_minutes:.0f} minutes")
        print(f"Est. cost : ~${len(remaining) * 6 * 0.0002:.2f}\n")

        pbar = tqdm(
            remaining.items(),
            total=len(remaining),
            desc=f"Strategy: {strategy}",
            unit="case",
        )

        for case_id, variants in pbar:
            case_results = {}
            pbar.set_postfix({"case": case_id[-20:]})

            for variant_label, note_text in variants.items():
                full_id = f"{case_id}__{variant_label}__{strategy}"
                try:
                    prompt = build_prompt(strategy, note_text)
                    result = model.generate_with_retry(prompt, full_id)
                    result["variant_label"] = variant_label
                    result["strategy"] = strategy
                    result["base_case_id"] = case_id
                    result["ground_truth_label"] = label_index.get(case_id, "")
                    case_results[variant_label] = result
                except Exception as exc:
                    logging.error("SKIP %s: %s", full_id, exc)
                    failed_cases.append(full_id)
                    case_results[variant_label] = {"error": str(exc)}

            strategy_results[case_id] = case_results

            # Save checkpoint after every case
            with open(checkpoint_path, "w", encoding="utf-8") as fh:
                json.dump(strategy_results, fh, indent=2, ensure_ascii=False)

        all_results[strategy] = strategy_results

        # Save final strategy results
        final_path = strategy_dir / f"{file_prefix}_results.json"
        with open(final_path, "w", encoding="utf-8") as fh:
            json.dump(strategy_results, fh, indent=2, ensure_ascii=False)
        print(f"\nSaved {strategy} results to {final_path}")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    elapsed = (time.time() - start_time) / 60
    total_completed = sum(
        1 for strat in all_results.values()
        for case in strat.values()
        for v in case.values()
        if "error" not in v
    )

    print(f"\n{'='*65}")
    print(f"EXPERIMENT COMPLETE")
    print(f"Elapsed   : {elapsed:.1f} minutes")
    print(f"Completed : {total_completed} / {total_calls} calls")
    print(f"Failed    : {len(failed_cases)}")
    if failed_cases:
        print(f"Failed IDs: {failed_cases[:5]}{'...' if len(failed_cases) > 5 else ''}")
    print(f"Results   : results/<strategy>/{subset}_results.json")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--subset",
        choices=["synthetic_structured", "synthetic_unstructured", "both"],
        default="synthetic_structured",
    )
    parser.add_argument(
        "--model",
        default="gemini-2.5-flash",
        choices=SUPPORTED_MODELS,
        help="LLM to use for inference (default: gemini-2.5-flash)",
    )
    parser.add_argument(
        "--all-strategies",
        action="store_true",
        help="Run all 5 strategies instead of baseline only",
    )
    args = parser.parse_args()

    strategies = (
        ["baseline", "fairness", "guideline_grounded", "structured_extraction"]
        if args.all_strategies
        else ["baseline"]
    )

    if args.subset == "both":
        run_experiment("synthetic_structured", strategies, model_name=args.model)
        run_experiment("synthetic_unstructured", strategies, model_name=args.model)
    else:
        run_experiment(args.subset, strategies, model_name=args.model)
