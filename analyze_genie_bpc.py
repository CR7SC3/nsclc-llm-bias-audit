"""EquityGUIDE — GENIE BPC results analysis.

Loads experiment results, parses LLM responses, scores guideline adherence
(0-3 ordinal) and 11 soft bias dimensions, then produces an Omar et al.
(Nature Medicine 2025)-equivalent statistical summary.

Primary outputs
───────────────
  adherence_by_variant.csv      mean ± SD, MWU vs reference, effect size
  soft_bias_by_variant.csv      % per dim per variant, OR vs reference, Fisher p
  soft_bias_asymmetry.csv       within-case paired asymmetry (McNemar)
  flip_rates.csv                flip rate per variant, Wilson CIs
  concordance_rates.csv         NCCN concordance rate per variant (NSCLC only)
  case_detail.csv               flat per-(case, variant) record for downstream R/Python

Statistical framework
─────────────────────
  Adherence     : Mann-Whitney U (non-parametric, ordinal 0-3), rank-biserial r
  Soft bias     : Fisher's exact OR with Cornfield 95% CI + McNemar within-case
  Concordance   : Fisher's exact one-tailed (minority < reference)
  Correction    : Bonferroni per family (21 variants for adherence;
                  11 × 21 = 231 for soft bias)

Usage
─────
    python analyze_genie_bpc.py --cohort nsclc --model gemini-2.5-flash
    python analyze_genie_bpc.py --cohort nsclc --model gemini-2.5-flash --save
    python analyze_genie_bpc.py --cohort nsclc --model gemini-2.5-flash --save --quiet
"""

from __future__ import annotations

import argparse
import json
import sys
from math import exp, log, sqrt
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import fisher_exact, mannwhitneyu, chi2_contingency

sys.path.insert(0, str(Path(__file__).parent))

from src.analyze.response_parser import ResponseParser
from src.analyze.adherence_scorer import compute_adherence_score, nccn_to_category
from src.analyze.soft_bias import DIMENSIONS, DIMS, detect_all, bias_signal
from src.analyze.stats import wilson_ci, bonferroni_threshold, significance_label
from src.generate.variant_injector_v2 import ALL_VARIANTS_V2, REFERENCE_VARIANT_V2

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REFERENCE = REFERENCE_VARIANT_V2  # "white_male_private"

TIERS: dict[str, list[str]] = {
    "A — race × insurance": [
        "white_male_private",
        "black_female_medicaid", "latina_female_uninsured",
        "black_female_private", "white_female_medicaid",
    ],
    "B — insurance only": [
        "uninsured_only", "medicaid_only", "medicare_only",
        "medicare_advantage_only", "underinsured_only",
    ],
    "C — race only": [
        "black_race_only", "hispanic_race_only", "asian_race_only",
        "native_american_race_only", "middle_eastern_race_only", "multiracial_race_only",
    ],
    "D — geography": ["rural_patient", "small_community_hospital"],
    "E — age": ["elderly_patient_75"],
    "F — immigration / language": ["immigrant_patient", "limited_english_patient"],
    "G — SES only": ["unhoused_patient", "low_income_patient", "high_income_patient"],
    "H — race × SES": ["black_unhoused", "low_income_black"],
    "I — gender / identity": ["non_binary_patient", "transgender_woman", "gay_male_patient"],
}

# Variants compared against reference (excludes reference itself and control)
COMPARE_VARIANTS: list[str] = [
    v for tier in TIERS.values() for v in tier
]

SOFT_BIAS_KEYS: list[str] = [d.key for d in DIMENSIONS]

RESULTS_ROOT = Path("results/genie_bpc")
ANALYSIS_DIR = Path("results/analysis")

_parser = ResponseParser()


# ---------------------------------------------------------------------------
# Tier lookup
# ---------------------------------------------------------------------------

def _tier(variant: str) -> str:
    for t, variants in TIERS.items():
        if variant in variants:
            return t
    if variant == REFERENCE:
        return "reference"
    return "control"


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _load_results(cohort: str, model_slug: str, strategy: str) -> dict:
    prefix = f"{strategy}_{model_slug}"
    for suffix in ("_results.json", "_checkpoint.json"):
        p = RESULTS_ROOT / cohort / f"{prefix}{suffix}"
        if p.exists():
            print(f"Loading: {p}  ({p.stat().st_size // 1024} KB)")
            with open(p, encoding="utf-8") as fh:
                return json.load(fh)
    raise FileNotFoundError(
        f"No results found at {RESULTS_ROOT}/{cohort}/{prefix}_*.json\n"
        f"Run: python run_experiment_genie_bpc.py --cohort {cohort} --model {model_slug}"
    )


# ---------------------------------------------------------------------------
# OR computation (Cornfield 95% CI)
# ---------------------------------------------------------------------------

def _compute_or(pos_var: int, n_var: int,
                pos_ref: int, n_ref: int) -> tuple[float, float, float, float]:
    """OR with 95% Cornfield CI and Fisher's exact p (two-sided).

    Returns (or, ci_lo, ci_hi, p). Adds 0.5 correction to zero cells.
    """
    neg_var = n_var - pos_var
    neg_ref = n_ref - pos_ref
    a, b = float(pos_var), float(neg_var)
    c, d = float(pos_ref), float(neg_ref)
    # Haldane-Anscombe correction
    if a == 0 or b == 0 or c == 0 or d == 0:
        a += 0.5; b += 0.5; c += 0.5; d += 0.5
    or_ = (a * d) / (b * c)
    log_se = sqrt(1/a + 1/b + 1/c + 1/d)
    ci_lo = exp(log(or_) - 1.96 * log_se)
    ci_hi = exp(log(or_) + 1.96 * log_se)
    table = [[int(pos_var), int(n_var - pos_var)],
             [int(pos_ref), int(n_ref - pos_ref)]]
    _, p = fisher_exact(table, alternative="two-sided")
    return or_, ci_lo, ci_hi, p


# ---------------------------------------------------------------------------
# Build flat case-detail DataFrame
# ---------------------------------------------------------------------------

def _build_case_detail(results: dict) -> pd.DataFrame:
    """Parse every result record and return a flat DataFrame.

    Columns
    ───────
    case_id, variant_label, tier,
    parsed_category, adherence_score,
    concordant_primary (score==3), concordant_any (score>=2),
    flip (vs reference), nccn_label, nccn_ambiguous, actual_treatment,
    sb_<dim_key> × 11
    """
    rows = []
    for case_id, variants in results.items():
        ref_result = variants.get(REFERENCE, {})
        ref_text   = ref_result.get("response_text", "") if "error" not in ref_result else ""
        ref_parsed = _parser.parse(ref_text).category if ref_text else "unknown"

        for variant_label, result in variants.items():
            if "error" in result:
                continue
            response_text = result.get("response_text", "")
            if not response_text:
                continue

            parsed  = _parser.parse(response_text)
            nccn_lbl   = result.get("nccn_label")
            nccn_acc   = result.get("nccn_acceptable_answers") or []
            nccn_ambig = result.get("nccn_ambiguous")

            adh_score = compute_adherence_score(
                parsed.category, nccn_lbl, nccn_acc
            )

            sb_flags = detect_all(response_text)

            row = {
                "case_id":            case_id,
                "variant_label":      variant_label,
                "tier":               _tier(variant_label),
                "parsed_category":    parsed.category,
                "adherence_score":    adh_score,
                "concordant_primary": int(adh_score == 3) if adh_score is not None else None,
                "concordant_any":     int(adh_score >= 2) if adh_score is not None else None,
                "flip":               int(parsed.category != ref_parsed
                                          and parsed.category not in ("unknown", "error")
                                          and ref_parsed not in ("unknown", "error"))
                                      if variant_label != REFERENCE else 0,
                "nccn_label":         nccn_lbl,
                "nccn_ambiguous":     nccn_ambig,
                "actual_treatment":   result.get("actual_treatment"),
                **{f"sb_{k}": int(v) for k, v in sb_flags.items()},
            }
            rows.append(row)

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Adherence summary
# ---------------------------------------------------------------------------

def _adherence_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Per-variant adherence statistics vs reference."""
    # Only use scored cases
    scored = df[df["adherence_score"].notna()].copy()
    if scored.empty:
        return pd.DataFrame()

    ref_scores = scored[scored["variant_label"] == REFERENCE]["adherence_score"].values
    if len(ref_scores) == 0:
        return pd.DataFrame()

    n_comparisons = len(COMPARE_VARIANTS)
    bonf_alpha    = bonferroni_threshold(n_comparisons)

    rows = []
    for variant in [REFERENCE] + COMPARE_VARIANTS:
        vs = scored[scored["variant_label"] == variant]["adherence_score"].values
        if len(vs) == 0:
            continue
        mean_v = vs.mean()
        sd_v   = vs.std(ddof=1)
        median_v = np.median(vs)

        if variant == REFERENCE:
            rows.append({
                "variant": variant, "tier": "reference",
                "n": len(vs), "mean": mean_v, "sd": sd_v, "median": median_v,
                "delta_mean": 0.0, "mwu_stat": None, "mwu_p": None,
                "effect_r": 0.0, "bonf_p": None, "sig": "ref",
            })
            continue

        stat, p = mannwhitneyu(ref_scores, vs, alternative="two-sided")
        n1, n2  = len(ref_scores), len(vs)
        r       = 1 - 2 * stat / (n1 * n2)   # rank-biserial correlation
        bonf_p  = min(p * n_comparisons, 1.0)
        sig     = significance_label(p, alpha=bonf_alpha, n=1)

        rows.append({
            "variant":    variant,
            "tier":       _tier(variant),
            "n":          len(vs),
            "mean":       round(mean_v, 3),
            "sd":         round(sd_v, 3),
            "median":     round(median_v, 3),
            "delta_mean": round(mean_v - ref_scores.mean(), 3),
            "mwu_stat":   round(stat, 1),
            "mwu_p":      round(p, 5),
            "effect_r":   round(r, 3),
            "bonf_p":     round(bonf_p, 5),
            "sig":        sig,
        })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Concordance summary
# ---------------------------------------------------------------------------

def _concordance_summary(df: pd.DataFrame, strict: bool = False) -> pd.DataFrame:
    """Per-variant NCCN concordance rate (primary or any-acceptable)."""
    col = "concordant_primary" if strict else "concordant_any"
    scored = df[df[col].notna()].copy()
    if scored.empty:
        return pd.DataFrame()

    ref_df   = scored[scored["variant_label"] == REFERENCE]
    ref_conc = int(ref_df[col].sum())
    ref_n    = len(ref_df)
    if ref_n == 0:
        return pd.DataFrame()

    n_comparisons = len(COMPARE_VARIANTS)
    bonf_alpha    = bonferroni_threshold(n_comparisons)
    rows = []

    for variant in [REFERENCE] + COMPARE_VARIANTS:
        vdf   = scored[scored["variant_label"] == variant]
        n     = len(vdf)
        conc  = int(vdf[col].sum())
        if n == 0:
            continue
        rate  = conc / n
        ci_lo, ci_hi = wilson_ci(conc, n)

        if variant == REFERENCE:
            rows.append({
                "variant": variant, "tier": "reference",
                "n": n, "concordant": conc, "rate": round(rate, 3),
                "ci_lo": round(ci_lo, 3), "ci_hi": round(ci_hi, 3),
                "fisher_p": None, "bonf_p": None, "sig": "ref",
            })
            continue

        from scipy.stats import fisher_exact as fe
        table = [[conc, n - conc], [ref_conc, ref_n - ref_conc]]
        _, p_less = fe(table, alternative="less")
        bonf_p = min(p_less * n_comparisons, 1.0)
        sig    = significance_label(p_less, alpha=bonf_alpha, n=1)

        rows.append({
            "variant":  variant,
            "tier":     _tier(variant),
            "n":        n,
            "concordant": conc,
            "rate":     round(rate, 3),
            "ci_lo":    round(ci_lo, 3),
            "ci_hi":    round(ci_hi, 3),
            "fisher_p": round(p_less, 5),
            "bonf_p":   round(bonf_p, 5),
            "sig":      sig,
        })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Flip rate summary
# ---------------------------------------------------------------------------

def _flip_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    n_comparisons = len(COMPARE_VARIANTS)
    bonf_alpha    = bonferroni_threshold(n_comparisons)

    # Ref flip rate = 0 by definition
    ref_df = df[df["variant_label"] == REFERENCE]
    rows.append({
        "variant": REFERENCE, "tier": "reference",
        "n": len(ref_df), "flips": 0, "rate": 0.0,
        "ci_lo": 0.0, "ci_hi": 0.0, "chi2_p": None, "sig": "ref",
    })

    for variant in COMPARE_VARIANTS:
        vdf   = df[df["variant_label"] == variant]
        n     = len(vdf)
        flips = int(vdf["flip"].sum()) if "flip" in vdf.columns else 0
        if n == 0:
            continue
        rate = flips / n
        ci_lo, ci_hi = wilson_ci(flips, n)
        # Chi-square vs reference (0 flips) — use binomial test vs 0
        from scipy.stats import binomtest
        p = binomtest(flips, n, p=0.0001, alternative="greater").pvalue
        bonf_p = min(p * n_comparisons, 1.0)
        sig    = significance_label(p, alpha=bonf_alpha, n=1)

        rows.append({
            "variant": variant, "tier": _tier(variant),
            "n": n, "flips": flips, "rate": round(rate, 3),
            "ci_lo": round(ci_lo, 3), "ci_hi": round(ci_hi, 3),
            "chi2_p": round(p, 5), "bonf_p": round(bonf_p, 5), "sig": sig,
        })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Soft bias summary — marginal rates + OR
# ---------------------------------------------------------------------------

def _soft_bias_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Per-(variant, dimension): marginal rate, OR vs reference, Fisher p."""
    ref_df = df[df["variant_label"] == REFERENCE]
    ref_n  = len(ref_df)

    n_comparisons = len(COMPARE_VARIANTS) * len(SOFT_BIAS_KEYS)
    bonf_alpha    = bonferroni_threshold(n_comparisons)

    rows = []
    for dim in SOFT_BIAS_KEYS:
        col = f"sb_{dim}"
        if col not in df.columns:
            continue
        ref_pos = int(ref_df[col].sum())

        for variant in [REFERENCE] + COMPARE_VARIANTS:
            vdf   = df[df["variant_label"] == variant]
            n     = len(vdf)
            pos   = int(vdf[col].sum())
            if n == 0:
                continue
            rate = pos / n
            ci_lo, ci_hi = wilson_ci(pos, n)

            if variant == REFERENCE:
                rows.append({
                    "variant": variant, "tier": "reference", "dimension": dim,
                    "n": n, "positive": pos, "rate": round(rate, 4),
                    "ci_lo": round(ci_lo, 4), "ci_hi": round(ci_hi, 4),
                    "OR": 1.0, "or_ci_lo": None, "or_ci_hi": None,
                    "fisher_p": None, "bonf_p": None, "sig": "ref",
                    "direction": DIMS[dim].bias_direction,
                })
                continue

            or_, or_lo, or_hi, p = _compute_or(pos, n, ref_pos, ref_n)
            bonf_p = min(p * n_comparisons, 1.0)
            sig    = significance_label(p, alpha=bonf_alpha, n=1)

            rows.append({
                "variant":   variant,
                "tier":      _tier(variant),
                "dimension": dim,
                "n":         n,
                "positive":  pos,
                "rate":      round(rate, 4),
                "ci_lo":     round(ci_lo, 4),
                "ci_hi":     round(ci_hi, 4),
                "OR":        round(or_, 3),
                "or_ci_lo":  round(or_lo, 3),
                "or_ci_hi":  round(or_hi, 3),
                "fisher_p":  round(p, 5),
                "bonf_p":    round(bonf_p, 5),
                "sig":       sig,
                "direction": DIMS[dim].bias_direction,
            })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Soft bias asymmetry — within-case paired comparison
# ---------------------------------------------------------------------------

def _soft_bias_asymmetry(df: pd.DataFrame) -> pd.DataFrame:
    """Within-case paired asymmetry for each (variant, dimension).

    For each case where both reference and variant responses exist:
      var_only = variant has dim, ref does NOT  (minority-disadvantaging for minority_higher)
      ref_only = ref has dim, variant does NOT  (white-advantaging)
      both     = both have dim
      neither  = neither has dim

    McNemar OR = var_only / ref_only  (how much more likely is variant to have this
                                       vs reference, given discordant pairs)
    """
    ref_df = df[df["variant_label"] == REFERENCE].set_index("case_id")

    n_comparisons = len(COMPARE_VARIANTS) * len(SOFT_BIAS_KEYS)
    bonf_alpha    = bonferroni_threshold(n_comparisons)

    rows = []
    for variant in COMPARE_VARIANTS:
        vdf = df[df["variant_label"] == variant].set_index("case_id")
        # Only matched case_ids
        common = ref_df.index.intersection(vdf.index)
        if len(common) == 0:
            continue

        for dim in SOFT_BIAS_KEYS:
            col = f"sb_{dim}"
            if col not in ref_df.columns:
                continue

            r_flags = ref_df.loc[common, col].values.astype(int)
            v_flags = vdf.loc[common, col].values.astype(int)

            var_only = int(((v_flags == 1) & (r_flags == 0)).sum())
            ref_only = int(((r_flags == 1) & (v_flags == 0)).sum())
            both     = int(((r_flags == 1) & (v_flags == 1)).sum())
            neither  = int(((r_flags == 0) & (v_flags == 0)).sum())
            total    = len(common)

            # McNemar test on discordant pairs
            from scipy.stats import binomtest
            discordant = var_only + ref_only
            if discordant > 0:
                p_mcnemar = binomtest(var_only, discordant, p=0.5,
                                     alternative="two-sided").pvalue
            else:
                p_mcnemar = 1.0

            # McNemar OR = var_only / ref_only (add 0.5 if zero)
            a = var_only + 0.5 if var_only == 0 else var_only
            b = ref_only + 0.5 if ref_only == 0 else ref_only
            mc_or = a / b

            bonf_p = min(p_mcnemar * n_comparisons, 1.0)
            sig    = significance_label(p_mcnemar, alpha=bonf_alpha, n=1)
            d      = DIMS[dim]

            rows.append({
                "variant":        variant,
                "tier":           _tier(variant),
                "dimension":      dim,
                "dim_direction":  d.bias_direction,
                "n_pairs":        total,
                "var_only":       var_only,   # variant has it, ref doesn't
                "ref_only":       ref_only,   # ref has it, variant doesn't
                "both":           both,
                "neither":        neither,
                "pct_var_only":   round(var_only / total * 100, 2),
                "pct_ref_only":   round(ref_only / total * 100, 2),
                "mc_or":          round(mc_or, 3),
                "mcnemar_p":      round(p_mcnemar, 5),
                "bonf_p":         round(bonf_p, 5),
                "sig":            sig,
                "bias_signal":    (var_only > ref_only if d.bias_direction == "minority_higher"
                                   else ref_only > var_only),
            })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Console report
# ---------------------------------------------------------------------------

def _print_adherence_report(adh: pd.DataFrame, cohort: str) -> None:
    if adh.empty:
        print("\n  [No adherence data — cohort may lack NCCN scorer coverage]\n")
        return

    ref_row = adh[adh["variant"] == REFERENCE]
    ref_mean = ref_row["mean"].values[0] if not ref_row.empty else None

    print(f"\n{'─'*72}")
    print(f"GUIDELINE ADHERENCE SCORE  (0=discordant → 3=concordant primary)")
    if ref_mean is not None:
        print(f"Reference ({REFERENCE}):  mean = {ref_mean:.3f} ± "
              f"{ref_row['sd'].values[0]:.3f}  "
              f"(n={int(ref_row['n'].values[0])})")
    print(f"{'─'*72}")
    print(f"  {'Variant':<35} {'n':>5} {'mean':>6} {'Δmean':>7} "
          f"{'r':>6} {'p':>8} {'bonf_p':>8} {'sig':>4}")
    print(f"  {'─'*35} {'─'*5} {'─'*6} {'─'*7} {'─'*6} {'─'*8} {'─'*8} {'─'*4}")

    current_tier = None
    for _, row in adh.iterrows():
        if row["variant"] == REFERENCE:
            continue
        tier = row["tier"]
        if tier != current_tier:
            print(f"\n  {tier}")
            current_tier = tier
        sig = row["sig"] if row["sig"] != "ns" else ""
        p   = f"{row['mwu_p']:.4f}" if row["mwu_p"] is not None else "  —  "
        bp  = f"{row['bonf_p']:.4f}" if row["bonf_p"] is not None else "  —  "
        print(f"  {row['variant']:<35} {row['n']:>5} {row['mean']:>6.3f} "
              f"{row['delta_mean']:>+7.3f} {row['effect_r']:>6.3f} "
              f"{p:>8} {bp:>8} {sig:>4}")
    print()


def _print_soft_bias_report(asym: pd.DataFrame) -> None:
    if asym.empty:
        print("\n  [No soft bias data]\n")
        return

    print(f"\n{'─'*72}")
    print(f"SOFT BIAS — within-case asymmetry vs {REFERENCE}")
    print(f"  +McNemar: % cases where minority has language / reference does NOT")
    print(f"{'─'*72}")

    for dim in SOFT_BIAS_KEYS:
        dim_df = asym[asym["dimension"] == dim]
        if dim_df.empty:
            continue
        d = DIMS[dim]
        sig_count = (dim_df["bonf_p"] < 0.05).sum()
        bias_count = dim_df["bias_signal"].sum()
        print(f"\n  {dim}  [{d.bias_direction}]  "
              f"({sig_count}/{len(dim_df)} variants p<0.05, "
              f"{bias_count}/{len(dim_df)} in expected direction)")
        print(f"    {'Variant':<35} {'var%':>5} {'ref%':>5} {'McOR':>6} "
              f"{'p':>8} {'sig':>4}")

        for _, row in dim_df.sort_values("pct_var_only", ascending=False).head(10).iterrows():
            sig = row["sig"] if row["sig"] != "ns" else ""
            print(f"    {row['variant']:<35} {row['pct_var_only']:>5.1f} "
                  f"{row['pct_ref_only']:>5.1f} {row['mc_or']:>6.2f} "
                  f"{row['mcnemar_p']:>8.4f} {sig:>4}")
    print()


def _print_flip_report(flip: pd.DataFrame) -> None:
    if flip.empty:
        return
    print(f"\n{'─'*72}")
    print(f"FLIP RATE  (vs {REFERENCE})")
    print(f"{'─'*72}")
    print(f"  {'Variant':<35} {'n':>5} {'flips':>6} {'rate':>6}  95% CI         {'sig':>4}")
    current_tier = None
    for _, row in flip.iterrows():
        if row["variant"] == REFERENCE:
            continue
        tier = row["tier"]
        if tier != current_tier:
            print(f"\n  {tier}")
            current_tier = tier
        sig = row["sig"] if row["sig"] != "ns" else ""
        ci  = f"[{row['ci_lo']:.2f}–{row['ci_hi']:.2f}]"
        print(f"  {row['variant']:<35} {row['n']:>5} {row['flips']:>6} "
              f"{row['rate']:>6.3f}  {ci:<16} {sig:>4}")
    print()


# ---------------------------------------------------------------------------
# Save outputs
# ---------------------------------------------------------------------------

def _save_outputs(
    cohort: str, model_slug: str, strategy: str,
    case_detail: pd.DataFrame,
    adh: pd.DataFrame,
    conc: pd.DataFrame,
    soft_bias: pd.DataFrame,
    asym: pd.DataFrame,
    flip: pd.DataFrame,
) -> None:
    out_dir = ANALYSIS_DIR
    out_dir.mkdir(exist_ok=True)
    prefix = f"genie_{cohort}_{strategy}_{model_slug}"

    files = {
        "case_detail":           case_detail,
        "adherence_by_variant":  adh,
        "concordance_rates":     conc,
        "soft_bias_by_variant":  soft_bias,
        "soft_bias_asymmetry":   asym,
        "flip_rates":            flip,
    }
    for name, df in files.items():
        if df is not None and not df.empty:
            path = out_dir / f"{prefix}_{name}.csv"
            df.to_csv(path, index=False)
            print(f"  Saved: {path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_analysis(
    cohort: str = "nsclc",
    model_slug: str = "gemini-2.5-flash",
    strategy: str = "baseline",
    save: bool = False,
    quiet: bool = False,
) -> dict[str, pd.DataFrame]:
    print(f"\n{'='*72}")
    print(f"EquityGUIDE — GENIE BPC Analysis")
    print(f"Cohort   : {cohort.upper()}")
    print(f"Model    : {model_slug}")
    print(f"Strategy : {strategy}")
    print(f"Reference: {REFERENCE}")
    print(f"{'='*72}\n")

    results = _load_results(cohort, model_slug, strategy)

    n_cases    = len(results)
    n_variants = max((len(v) for v in results.values()), default=0)
    print(f"Cases loaded : {n_cases}")
    print(f"Variants/case: {n_variants}")
    print(f"\nParsing responses and scoring...")

    df = _build_case_detail(results)
    n_scored = df["adherence_score"].notna().sum()
    print(f"  Total records: {len(df)}")
    print(f"  Adherence-scored: {n_scored} ({n_scored/len(df)*100:.0f}%)")

    adh   = _adherence_summary(df)
    conc  = _concordance_summary(df, strict=False)
    soft  = _soft_bias_summary(df)
    asym  = _soft_bias_asymmetry(df)
    flip  = _flip_summary(df)

    if not quiet:
        _print_adherence_report(adh, cohort)
        _print_flip_report(flip)
        _print_soft_bias_report(asym)

    if save:
        print("Saving CSVs...")
        _save_outputs(cohort, model_slug, strategy,
                      df, adh, conc, soft, asym, flip)

    return {
        "case_detail": df,
        "adherence":   adh,
        "concordance": conc,
        "soft_bias":   soft,
        "asymmetry":   asym,
        "flip":        flip,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="EquityGUIDE GENIE BPC results analysis"
    )
    parser.add_argument("--cohort",   default="nsclc",
                        choices=["nsclc", "brca", "panc"])
    parser.add_argument("--model",    default="gemini-2.5-flash")
    parser.add_argument("--strategy", default="baseline",
                        choices=["baseline", "fairness",
                                 "guideline_grounded", "structured_extraction"])
    parser.add_argument("--save",  action="store_true",
                        help="Write CSV outputs to results/analysis/")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress console report (useful when piping)")
    args = parser.parse_args()
    run_analysis(
        cohort=args.cohort,
        model_slug=args.model,
        strategy=args.strategy,
        save=args.save,
        quiet=args.quiet,
    )
