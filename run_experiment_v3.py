"""EquityGUIDE v3 — Intervention study: prompt strategy vs. SES-triggered bias.

Tests whether prompt design can eliminate the financial framing and social-work
referral bias identified in v2 (SES/insurance labels in unstructured notes).

Runs 5 high-signal variants × a single user-specified strategy on the
unstructured subset (where bias concentrates). Compare outputs to the v2
baseline to measure bias reduction and concordance trade-off.

High-signal variants (from v2 partial results at n=70):
  white_male_private       2% cost, 1% SW  ← reference
  latina_female_uninsured 64% cost, 53% SW ← primary finding
  uninsured_only          44% cost, 36% SW
  low_income_patient      60% cost, 37% SW
  white_male_uninsured    51% cost, 33% SW ← confirms SES > race

Strategies
──────────
  fairness              Explicit demographic-neutrality directive
  guideline_grounded    Walks NCCN pathway step-by-step
  structured_extraction Two-step demographic blinding (extract → recommend)
  self_consistency      Identical prompt to baseline (run once; ×5 is future work)

Usage
-----
    python run_experiment_v3.py --strategy fairness
    python run_experiment_v3.py --strategy guideline_grounded
    python run_experiment_v3.py --strategy structured_extraction
    python run_experiment_v3.py --strategy structured_extraction --model gpt-4o
    python run_experiment_v3.py --strategy fairness --dry-run
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

from src.models.factory import create_model, SUPPORTED_MODELS
from src.generate.variant_injector_v2 import create_all_variants_v2
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
}

V3_STRATEGIES = ["fairness", "guideline_grounded", "structured_extraction", "self_consistency"]

# 5 variants selected for maximum bias signal from v2 partial results (n=70 unstructured)
V3_INTERVENTION_VARIANTS = [
    "white_male_private",       # reference: 2% cost, 1% SW
    "latina_female_uninsured",  # 64% cost, 53% SW — primary finding
    "uninsured_only",           # 44% cost, 36% SW
    "low_income_patient",       # 60% cost, 37% SW
    "white_male_uninsured",     # 51% cost, 33% SW — SES > race confirmation
]


def _load_processed(subset: str) -> list[dict]:
    path = Path(_PROCESSED_PATHS[subset])
    if not path.exists():
        raise FileNotFoundError(
            f"Processed cases not found at {path}. "
            "Run `python -m src.generate.load_cases` first."
        )
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def run_experiment_v3(
    strategy: str,
    subset: str = "synthetic_unstructured",
    model_name: str = "gemini-2.5-flash",
    dry_run: bool = False,
) -> None:
    n_variants = len(V3_INTERVENTION_VARIANTS)

    print(f"\n{'='*70}")
    print(f"EquityGUIDE v3 — Intervention Study")
    print(f"Strategy  : {strategy}")
    print(f"Subset    : {subset}")
    print(f"Model     : {model_name}")
    print(f"Variants  : {n_variants} (high-signal SES/insurance set)")
    if dry_run:
        print(f"DRY RUN   : no API calls will be made")
    print(f"{'='*70}\n")

    cases = _load_processed(subset)
    label_index = {c["case_id"]: c.get("label", "") for c in cases}

    model_slug = model_name.replace("/", "-")
    strategy_slug = strategy.replace("_", "-")
    if model_name == "gemini-2.5-flash":
        file_prefix = f"v3_{subset}_{strategy_slug}"
    else:
        file_prefix = f"v3_{subset}_{strategy_slug}_{model_slug}"

    out_dir = _RESULTS_DIR / "baseline"
    out_dir.mkdir(exist_ok=True)
    checkpoint_path = out_dir / f"{file_prefix}_checkpoint.json"

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

    # Cost estimates based on observed v2 token averages for unstructured notes
    # (avg 1738 input + 1313 output tokens per call)
    if model_name == "gpt-4o":
        est_cost = len(remaining) * n_variants * (1738 * 2.50 + 1313 * 10.0) / 1_000_000
        print(f"Est. cost : ~${est_cost:.2f} (GPT-4o)")
        print(f"WARNING   : GPT-4o costs ~${est_cost:.0f} per strategy run.")
    elif model_name == "gemini-2.5-flash":
        est_cost = len(remaining) * n_variants * 0.0002
        print(f"Est. cost : ~${est_cost:.2f} (Gemini)")
    else:
        est_cost = len(remaining) * n_variants * 0.0002
        print(f"Est. cost : ~${est_cost:.2f} (estimated)")
    print()

    if dry_run:
        print("Dry-run complete. Variant filtering and checkpoint path look correct.")
        print(f"Checkpoint would be written to: {checkpoint_path}")
        print(f"Variants: {V3_INTERVENTION_VARIANTS}")
        # Verify variant filtering against a real case
        sample_case = cases[0]
        all_v = create_all_variants_v2(sample_case["clean_note"], subset)
        filtered = {k: v for k, v in all_v.items() if k in V3_INTERVENTION_VARIANTS}
        print(f"Sample case variants available: {list(filtered.keys())}")
        missing = [v for v in V3_INTERVENTION_VARIANTS if v not in filtered]
        if missing:
            print(f"WARNING: missing variants: {missing}")
        return

    model = create_model(model_name, inter_call_sleep=1.0, max_retries=3, retry_wait=30.0)

    failed = []
    start = time.time()

    pbar = tqdm(remaining, total=len(remaining), desc=f"v3/{strategy}", unit="case")

    for case in pbar:
        case_id = case["case_id"]
        base_note = case["clean_note"]
        pbar.set_postfix({"case": case_id[-20:]})

        all_variants = create_all_variants_v2(base_note, subset)
        variants = {k: v for k, v in all_variants.items() if k in V3_INTERVENTION_VARIANTS}

        case_results: dict = {}
        for variant_key, note_text in variants.items():
            full_id = f"{case_id}__{variant_key}__{strategy}_v3"
            try:
                prompt = build_prompt(strategy, note_text)
                result = model.generate_with_retry(prompt, full_id)
                result["variant_label"] = variant_key
                result["strategy"] = strategy
                result["experiment"] = "v3_intervention"
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

    final_path = out_dir / f"{file_prefix}_results.json"
    with open(final_path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, ensure_ascii=False)

    elapsed = (time.time() - start) / 60
    completed_calls = sum(
        1 for case in results.values()
        for v in case.values()
        if "error" not in v
    )

    print(f"\n{'='*70}")
    print(f"EXPERIMENT v3 COMPLETE — strategy: {strategy}")
    print(f"Elapsed   : {elapsed:.1f} minutes")
    print(f"Completed : {completed_calls} / {len(cases) * n_variants} calls")
    print(f"Failed    : {len(failed)}")
    print(f"Checkpoint: {checkpoint_path}")
    print(f"Results   : {final_path}")
    print(f"{'='*70}\n")
    print(f"Next step: python analyze_v3.py")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="EquityGUIDE v3 — intervention study (prompt strategy vs. SES bias)"
    )
    parser.add_argument(
        "--strategy",
        choices=V3_STRATEGIES,
        required=True,
        help="Prompt strategy to test against the v2 baseline.",
    )
    parser.add_argument(
        "--subset",
        choices=["synthetic_structured", "synthetic_unstructured"],
        default="synthetic_unstructured",
        help="Note format subset (default: unstructured, where bias concentrates).",
    )
    parser.add_argument(
        "--model",
        choices=SUPPORTED_MODELS,
        default="gemini-2.5-flash",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate config and variant filtering without making API calls.",
    )
    args = parser.parse_args()
    run_experiment_v3(
        strategy=args.strategy,
        subset=args.subset,
        model_name=args.model,
        dry_run=args.dry_run,
    )
