"""EquityGUIDE — Post-experiment analysis script.

Parses all LLM responses from the experiment checkpoint/results file,
computes flip rates by demographic group, and prints a summary report.

Usage
-----
    # After experiment finishes (reads final results file):
    python analyze_results.py --subset synthetic_structured

    # Mid-run (reads checkpoint):
    python analyze_results.py --subset synthetic_structured --checkpoint

    # Save CSV tables to results/analysis/:
    python analyze_results.py --subset synthetic_structured --save
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.analyze.response_parser import ResponseParser
from src.analyze.stats import (
    flip_stats,
    chi_square_flip_homogeneity,
    significance_label,
)
from src.evaluate.concordance_checker import (
    ConcordanceChecker,
    compute_concordance_rates,
    print_concordance_report,
    save_concordance_csv,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VARIANTS = [
    "white_male_private",
    "black_male_medicaid",
    "black_female_medicaid",
    "latina_female_uninsured",
    "asian_female_medicare",
    "no_demographics",
]

REFERENCE_VARIANT = "white_male_private"

_RESULTS_DIR = Path("results")
_ANALYSIS_DIR = _RESULTS_DIR / "analysis"


# ---------------------------------------------------------------------------
# Core analysis
# ---------------------------------------------------------------------------

def load_checkpoint(subset: str, use_checkpoint: bool, model: str = "gemini-2.5-flash") -> dict:
    strategy_dir = _RESULTS_DIR / "baseline"
    # Gemini keeps legacy filename; all other models include a slug
    prefix = subset if model == "gemini-2.5-flash" else f"{subset}_{model.replace('/', '-')}"
    if use_checkpoint:
        path = strategy_dir / f"{prefix}_checkpoint.json"
    else:
        path = strategy_dir / f"{prefix}_results.json"

    if not path.exists():
        fallback = strategy_dir / f"{prefix}_checkpoint.json"
        if fallback.exists():
            print(f"[warn] Final results not found — using checkpoint: {fallback}")
            path = fallback
        else:
            raise FileNotFoundError(f"No results found at {path} or {fallback}")

    print(f"Loading: {path}  ({path.stat().st_size // 1024} KB)")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def compute_flip_rates(parsed: dict) -> dict:
    """Aggregate flip counts and rates per demographic variant.

    Returns
    -------
    dict with keys:
        per_variant  — {variant: {flips, total, rate}}
        per_case     — {case_id: {reference_category, flips: {variant: bool}}}
        flip_matrix  — {from_category: {to_category: count}}
        cases_with_any_flip — int
        total_cases  — int
    """
    per_variant: dict[str, dict] = {
        v: {"flips": 0, "total": 0, "flip_cases": []}
        for v in VARIANTS
        if v != REFERENCE_VARIANT
    }

    flip_matrix: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    cases_with_flip = 0

    for case_id, case_data in parsed.items():
        ref_cat = case_data["reference_category"]
        case_has_flip = False

        for variant, did_flip in case_data["flips"].items():
            if variant not in per_variant:
                continue
            per_variant[variant]["total"] += 1
            if did_flip:
                per_variant[variant]["flips"] += 1
                per_variant[variant]["flip_cases"].append(case_id)
                to_cat = case_data["variants"][variant].category
                flip_matrix[ref_cat][to_cat] += 1
                case_has_flip = True

        if case_has_flip:
            cases_with_flip += 1

    for v in per_variant:
        n = per_variant[v]["total"]
        per_variant[v]["rate"] = per_variant[v]["flips"] / n if n > 0 else 0.0

    return {
        "per_variant": per_variant,
        "per_case": parsed,
        "flip_matrix": {k: dict(v) for k, v in flip_matrix.items()},
        "cases_with_any_flip": cases_with_flip,
        "total_cases": len(parsed),
    }


def print_report(rates: dict, subset: str) -> None:
    total = rates["total_cases"]
    flip_cases = rates["cases_with_any_flip"]
    pv = rates["per_variant"]
    n_minority = sum(1 for v in VARIANTS if v != REFERENCE_VARIANT)

    print(f"\n{'='*75}")
    print(f"EquityGUIDE — Flip Rate Analysis")
    print(f"Subset  : {subset}")
    print(f"Cases   : {total}")
    print(f"{'='*75}")

    # --- Chi-square homogeneity test across all minority variants ---
    hom = chi_square_flip_homogeneity(pv, VARIANTS, REFERENCE_VARIANT)
    sig = significance_label(hom["p_value"])
    print(f"\nHomogeneity test (H0: all variants have equal flip rate)")
    print(f"  χ²({hom['dof']}) = {hom['chi2']:.3f},  p = {hom['p_value']:.4f}  {sig}")

    # --- Per-variant flip rates with Wilson CI ---
    print(f"\nFlip rate vs reference ({REFERENCE_VARIANT})")
    print(f"{'Demographic variant':<30} {'Flips':>6} {'Cases':>6} {'Rate':>8}  {'95% CI':<18}  {'Sig':>4}")
    print("-" * 75)
    for variant in VARIANTS:
        if variant == REFERENCE_VARIANT:
            continue
        d = pv[variant]
        fs = flip_stats(d["flips"], d["total"])
        # Individual significance after Bonferroni correction for n_minority comparisons
        # Use one-sample exact binomial vs p=0 approximated by Wilson CI not including 0
        sig_v = "*" if fs["ci_low"] > 0 else "ns"
        ci_str = f"[{fs['ci_low']:.1%}, {fs['ci_high']:.1%}]"
        print(f"{variant:<30} {d['flips']:>6} {d['total']:>6} {d['rate']:>7.1%}  {ci_str:<18}  {sig_v:>4}")

    # --- Cases with at least one flip ---
    print(f"\nCases with ≥1 flip : {flip_cases} / {total}  ({flip_cases/total:.1%})")

    # --- Category transition matrix ---
    matrix = rates["flip_matrix"]
    if matrix:
        print(f"\nFlip transition matrix  (reference -> flipped-to category)")
        header_label = "From / To"
        print(f"{header_label:<28}", end="")
        all_to_cats = sorted({cat for row in matrix.values() for cat in row})
        for cat in all_to_cats:
            print(f"  {cat[:14]:<14}", end="")
        print()
        print("-" * (28 + 16 * len(all_to_cats)))
        for from_cat in sorted(matrix.keys()):
            print(f"{from_cat:<28}", end="")
            for to_cat in all_to_cats:
                n = matrix[from_cat].get(to_cat, 0)
                print(f"  {n:<14}", end="")
            print()

    # --- Per-case detail ---
    print(f"\nPer-case flip detail")
    print(f"{'Case':<25} {'Ref category':<25} {'Flipped variants'}")
    print("-" * 80)
    for case_id, case_data in sorted(rates["per_case"].items()):
        flipped = [v for v, f in case_data["flips"].items() if f]
        ref = case_data["reference_category"]
        if flipped:
            flip_str = ", ".join(
                f"{v}→{case_data['variants'][v].category}" for v in flipped
            )
            print(f"{case_id:<25} {ref:<25} {flip_str}")
        else:
            print(f"{case_id:<25} {ref:<25} (no flip)")

    print(f"\n{'='*65}\n")


def save_csv(rates: dict, subset: str) -> None:
    _ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

    # Flip rate summary
    rows = []
    for variant in VARIANTS:
        if variant == REFERENCE_VARIANT:
            continue
        d = rates["per_variant"][variant]
        rows.append(f"{variant},{d['flips']},{d['total']},{d['rate']:.4f}")

    model_slug = rates.get("model", "gemini-2.5-flash").replace("/", "-")
    prefix = subset if model_slug == "gemini-2.5-flash" else f"{subset}_{model_slug}"
    summary_path = _ANALYSIS_DIR / f"{prefix}_flip_rates.csv"
    with open(summary_path, "w", encoding="utf-8") as fh:
        fh.write("variant,flips,total,flip_rate\n")
        fh.write("\n".join(rows) + "\n")
    print(f"Saved: {summary_path}")

    # Per-case detail
    detail_rows = []
    for case_id, case_data in sorted(rates["per_case"].items()):
        ref = case_data["reference_category"]
        for variant in VARIANTS:
            if variant == REFERENCE_VARIANT:
                continue
            pv = case_data["variants"].get(variant)
            cat = pv.category if pv else "error"
            did_flip = case_data["flips"].get(variant, False)
            detail_rows.append(f"{case_id},{ref},{variant},{cat},{int(did_flip)}")

    detail_path = _ANALYSIS_DIR / f"{prefix}_case_detail.csv"
    with open(detail_path, "w", encoding="utf-8") as fh:
        fh.write("case_id,reference_category,variant,variant_category,flip\n")
        fh.write("\n".join(detail_rows) + "\n")
    print(f"Saved: {detail_path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze EquityGUIDE experiment results.")
    parser.add_argument(
        "--subset",
        choices=["synthetic_structured", "synthetic_unstructured", "both"],
        default="synthetic_structured",
    )
    parser.add_argument(
        "--checkpoint",
        action="store_true",
        help="Read checkpoint file instead of final results file.",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save CSV tables to results/analysis/.",
    )
    parser.add_argument(
        "--concordance",
        action="store_true",
        help="Run NCCN concordance analysis after flip analysis.",
    )
    parser.add_argument(
        "--no-extract",
        action="store_true",
        help="Skip ProfileExtractor API calls; only use cached profiles for concordance.",
    )
    parser.add_argument(
        "--model",
        default="gemini-2.5-flash",
        help="Model whose results to analyse (default: gemini-2.5-flash).",
    )
    args = parser.parse_args()

    response_parser = ResponseParser()

    subsets = (
        ["synthetic_structured", "synthetic_unstructured"]
        if args.subset == "both"
        else [args.subset]
    )

    for subset in subsets:
        checkpoint = load_checkpoint(subset, args.checkpoint, model=args.model)
        parsed = response_parser.parse_checkpoint(checkpoint)
        rates = compute_flip_rates(parsed)
        rates["model"] = args.model
        print_report(rates, subset)
        if args.save:
            save_csv(rates, subset)

        if args.concordance:
            print("Running NCCN concordance check...")
            checker = ConcordanceChecker(
                extract_missing=not args.no_extract,
            )
            concordance_results = checker.check_batch(parsed, subset=subset)
            conc_rates = compute_concordance_rates(concordance_results)
            print_concordance_report(conc_rates, subset)
            if args.save:
                save_concordance_csv(conc_rates, concordance_results, subset, model=args.model)


if __name__ == "__main__":
    main()
