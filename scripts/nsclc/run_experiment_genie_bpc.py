"""EquityGUIDE — GENIE BPC experiment runner.

Feeds real-world GENIE BPC cases through the same 22-variant demographic
injection pipeline used for CancerGUIDE, enabling out-of-sample replication
of bias findings on de-identified EHR data.

Pipeline
────────
  1. Load processed GENIE BPC cases from data/processed/
  2. Apply all 22 v2 demographic variants to each structured_note in-place
     (Race/Sex/Ethnicity fields are replaced directly — no strip step needed)
  3. For NSCLC: run NCCN scorer on clinical_profile to get ground-truth label
  4. Build prompts and call the LLM
  5. Save results under results/genie_bpc/<cohort>/

Cohorts
───────
  nsclc  — 1,048 cases  (NCCN scorer available)
  brca   — 1,093 cases  (actual_treatment as reference only)
  panc   — 1,022 cases  (actual_treatment as reference only)

Usage
─────
  # Dry run — no API calls
  venv/bin/python scripts/nsclc/run_experiment_genie_bpc.py --cohort nsclc --dry-run --limit 5

  # Pilot: 10 cases
  venv/bin/python scripts/nsclc/run_experiment_genie_bpc.py --cohort nsclc --limit 10

  # Full NSCLC run (~23 k calls, ~$46 on Gemini Flash)
  venv/bin/python scripts/nsclc/run_experiment_genie_bpc.py --cohort nsclc

  # Fairness strategy
  venv/bin/python scripts/nsclc/run_experiment_genie_bpc.py --cohort nsclc --strategy fairness
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

_PROCESSED_PATHS: dict[str, str] = {
    "nsclc": "data/processed/genie_bpc_nsclc_processed.json",
    "brca":  "data/processed/genie_bpc_brca_processed.json",
    "panc":  "data/processed/genie_bpc_panc_processed.json",
}

_RESULTS_ROOT = Path("results/genie_bpc")


def _load_cases(cohort: str, limit: int | None) -> list[dict]:
    path = Path(_PROCESSED_PATHS[cohort])
    if not path.exists():
        raise FileNotFoundError(
            f"Processed cases not found at {path}. "
            f"Run src/generate/load_genie_bpc{'_brca_panc' if cohort != 'nsclc' else ''}.py first."
        )
    with open(path, encoding="utf-8") as fh:
        cases = json.load(fh)
    if limit is not None:
        cases = cases[:limit]
    return cases


def _nccn_label(clinical_profile: dict) -> dict:
    """Run NCCN scorer and return label fields. Returns nulls on import error."""
    try:
        from src.evaluate.nccn_scorer import get_nccn_answer
        result = get_nccn_answer(clinical_profile)
        return {
            "nccn_label":               result.get("primary_answer"),
            "nccn_acceptable_answers":  result.get("acceptable_answers", []),
            "nccn_ambiguous":           result.get("ambiguous", False),
            "nccn_pathway":             result.get("pathway"),
        }
    except Exception as exc:
        logging.warning("NCCN scorer error: %s", exc)
        return {"nccn_label": None, "nccn_ambiguous": None, "nccn_pathway": None}


def run_experiment(
    cohort: str = "nsclc",
    model_name: str = "gemini-2.5-flash",
    strategy: str = "baseline",
    limit: int | None = None,
    dry_run: bool = False,
) -> None:
    n_variants = len(ALL_VARIANTS_V2)
    use_nccn = cohort == "nsclc"

    print(f"\n{'='*70}")
    print(f"EquityGUIDE — GENIE BPC Experiment")
    print(f"Cohort    : {cohort.upper()}")
    print(f"Strategy  : {strategy}")
    print(f"Model     : {model_name}")
    print(f"Variants  : {n_variants}")
    if limit:
        print(f"Limit     : {limit} cases")
    if dry_run:
        print(f"Mode      : DRY RUN (no API calls)")
    print(f"{'='*70}\n")

    cases = _load_cases(cohort, limit)

    # Pre-compute NCCN labels for NSCLC to avoid re-running scorer per variant
    nccn_cache: dict[str, dict] = {}
    if use_nccn:
        print(f"Scoring {len(cases)} cases with NCCN scorer...")
        for case in cases:
            nccn_cache[case["case_id"]] = _nccn_label(case["clinical_profile"])
        scorable = sum(1 for v in nccn_cache.values() if v["nccn_label"] is not None)
        print(f"  Scorable: {scorable}/{len(cases)} ({scorable/len(cases)*100:.0f}%)\n")

    # Output paths
    model_slug = model_name.replace("/", "-")
    file_prefix = f"{strategy}_{model_slug}"
    out_dir = _RESULTS_ROOT / cohort
    out_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = out_dir / f"{file_prefix}_checkpoint.json"
    final_path      = out_dir / f"{file_prefix}_results.json"

    # Resume from checkpoint
    if checkpoint_path.exists() and not dry_run:
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
    print(f"API calls : {total_calls} total ({n_variants} variants × {len(cases)} cases)")
    print(f"Est. time : ~{est_min:.0f} minutes")

    if model_name in ("gpt-4o",):
        est_cost = len(remaining) * n_variants * (1500 * 2.50 + 600 * 10.0) / 1_000_000
        print(f"Est. cost : ~${est_cost:.2f} (GPT-4o)")
    else:
        est_cost = len(remaining) * n_variants * 0.0002
        print(f"Est. cost : ~${est_cost:.2f}")
    print()

    if dry_run:
        print("DRY RUN — validating variant injection on first case...")
        sample = cases[0]
        variants = create_all_variants_v2(sample["structured_note"], "synthetic_structured")
        print(f"  case_id   : {sample['case_id']}")
        print(f"  variants  : {len(variants)} generated")
        print(f"  actual_tx : {sample.get('actual_treatment', 'n/a')}")
        if use_nccn:
            nccn = nccn_cache.get(sample["case_id"], {})
            print(f"  nccn_label: {nccn.get('nccn_label')}")
            print(f"  ambiguous : {nccn.get('nccn_ambiguous')}")
        print("\n  Sample note snippet (white_male_private variant):")
        print("  " + variants["white_male_private"][:300].replace("\n", "\n  "))
        print("\nDry run complete. Rerun without --dry-run to execute.")
        return

    model = create_model(model_name, temperature=0.0, inter_call_sleep=1.0, max_retries=3, retry_wait=30.0)

    failed: list[str] = []
    start = time.time()

    pbar = tqdm(remaining, total=len(remaining), desc=f"genie_bpc_{cohort}", unit="case")

    for case in pbar:
        case_id        = case["case_id"]
        structured_note = case["structured_note"]
        actual_treatment = case.get("actual_treatment", "")
        pbar.set_postfix({"case": case_id[-24:]})

        # Generate all 22 v2 variants directly from structured_note
        variants = create_all_variants_v2(structured_note, "synthetic_structured")

        nccn = nccn_cache.get(case_id, {"nccn_label": None, "nccn_ambiguous": None, "nccn_pathway": None})

        case_results: dict = {}
        for variant_key, note_text in variants.items():
            full_id = f"{case_id}__{variant_key}__{strategy}"
            try:
                prompt = build_prompt(strategy, note_text)
                result = model.generate_with_retry(prompt, full_id)
                result["case_id"]          = full_id
                result["base_case_id"]     = case_id
                result["cohort"]           = cohort
                result["variant_label"]    = variant_key
                result["strategy"]         = strategy
                result["actual_treatment"] = actual_treatment
                result["nccn_label"]              = nccn["nccn_label"]
                result["nccn_acceptable_answers"] = nccn["nccn_acceptable_answers"]
                result["nccn_ambiguous"]          = nccn["nccn_ambiguous"]
                result["nccn_pathway"]            = nccn["nccn_pathway"]
                case_results[variant_key]  = result
            except Exception as exc:
                logging.error("SKIP %s: %s", full_id, exc)
                failed.append(full_id)
                case_results[variant_key] = {"error": str(exc), "variant_label": variant_key}

        results[case_id] = case_results

        with open(checkpoint_path, "w", encoding="utf-8") as fh:
            json.dump(results, fh, indent=2, ensure_ascii=False)

    # Save final results
    with open(final_path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, ensure_ascii=False)

    elapsed = (time.time() - start) / 60
    completed_calls = sum(
        1 for case in results.values()
        for v in case.values()
        if "error" not in v
    )

    print(f"\n{'='*70}")
    print(f"GENIE BPC EXPERIMENT COMPLETE")
    print(f"Elapsed   : {elapsed:.1f} minutes")
    print(f"Completed : {completed_calls} / {len(cases) * n_variants} calls")
    print(f"Failed    : {len(failed)}")
    print(f"Results   : {final_path}")
    print(f"{'='*70}\n")
    print(f"Next step: analyze with cohort={cohort}, strategy={strategy}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="EquityGUIDE — GENIE BPC demographic bias experiment"
    )
    parser.add_argument(
        "--cohort",
        choices=["nsclc", "brca", "panc"],
        default="nsclc",
    )
    parser.add_argument(
        "--model",
        choices=SUPPORTED_MODELS,
        default="gemini-2.5-flash",
    )
    parser.add_argument(
        "--strategy",
        choices=["baseline", "fairness", "guideline_grounded", "structured_extraction"],
        default="baseline",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        metavar="N",
        help="Run only the first N cases (for pilots and cost control)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate loading and variant injection without making API calls",
    )
    args = parser.parse_args()
    run_experiment(
        cohort=args.cohort,
        model_name=args.model,
        strategy=args.strategy,
        limit=args.limit,
        dry_run=args.dry_run,
    )
