"""Statistical tests for EquityGUIDE flip-rate and concordance analyses.

Tests
-----
flip_stats(k, n)
    Wilson 95% CI for a single flip rate.

chi_square_flip_homogeneity(per_variant, variants, reference_variant)
    Chi-square test of homogeneity across minority-variant flip rates.
    H0: all demographic variants have the same underlying flip probability.

concordance_fisher(conc_ref, total_ref, conc_min, total_min)
    Fisher's exact test comparing a minority variant's concordance rate
    to the reference variant's concordance rate.
    H0: concordance rates are equal.  H1 (one-tailed): minority < reference.

All p-values are reported without multiple-comparison correction; callers
should apply Bonferroni or BH correction when printing tables.
"""

from __future__ import annotations

import numpy as np
from scipy import stats as sp_stats


# ---------------------------------------------------------------------------
# Wilson confidence interval
# ---------------------------------------------------------------------------

def wilson_ci(k: int, n: int, confidence: float = 0.95) -> tuple[float, float]:
    """Wilson score confidence interval for proportion k/n."""
    if n == 0:
        return (0.0, 0.0)
    from scipy.stats import norm
    z = norm.ppf((1 + confidence) / 2)
    p_hat = k / n
    denom = 1 + z**2 / n
    centre = (p_hat + z**2 / (2 * n)) / denom
    margin = z * np.sqrt(p_hat * (1 - p_hat) / n + z**2 / (4 * n**2)) / denom
    return (max(0.0, centre - margin), min(1.0, centre + margin))


# ---------------------------------------------------------------------------
# Flip-rate statistics
# ---------------------------------------------------------------------------

def flip_stats(flips: int, total: int, confidence: float = 0.95) -> dict:
    """Rate and Wilson CI for a single variant's flip count.

    Returns
    -------
    dict with keys: rate, ci_low, ci_high
    """
    rate = flips / total if total > 0 else 0.0
    ci_low, ci_high = wilson_ci(flips, total, confidence)
    return {"rate": rate, "ci_low": ci_low, "ci_high": ci_high}


def chi_square_flip_homogeneity(
    per_variant: dict,
    variants: list[str],
    reference_variant: str,
) -> dict:
    """Chi-square test of homogeneity across minority-variant flip rates.

    Builds a 2 × k contingency table (flip / no-flip) × minority variants.
    H0: all minority variants have the same underlying flip probability.

    Returns
    -------
    dict with keys: chi2, p_value, dof
    """
    minority = [v for v in variants if v != reference_variant]
    table = np.array([
        [per_variant[v]["flips"], per_variant[v]["total"] - per_variant[v]["flips"]]
        for v in minority
    ]).T  # shape: 2 × k

    chi2, p_value, dof, _ = sp_stats.chi2_contingency(table)
    return {"chi2": chi2, "p_value": p_value, "dof": dof}


# ---------------------------------------------------------------------------
# Concordance statistics
# ---------------------------------------------------------------------------

def concordance_fisher(
    conc_ref: int,
    total_ref: int,
    conc_min: int,
    total_min: int,
) -> dict:
    """Fisher's exact test: is minority concordance rate < reference rate?

    2 × 2 table:
                    concordant   non-concordant
        reference       a              b
        minority        c              d

    H1 (one-tailed less): minority concordance rate < reference rate.
    Also returns the two-tailed p-value and odds ratio.

    Returns
    -------
    dict with keys: odds_ratio, p_value_two, p_value_less, table
    """
    b = total_ref - conc_ref
    d = total_min - conc_min
    table = [[conc_ref, b], [conc_min, d]]

    odds_ratio_two, p_two = sp_stats.fisher_exact(table, alternative="two-sided")
    _, p_less = sp_stats.fisher_exact(table, alternative="less")

    return {
        "odds_ratio": odds_ratio_two,
        "p_value_two": p_two,
        "p_value_less": p_less,
        "table": table,
    }


# ---------------------------------------------------------------------------
# Concordance homogeneity across all groups
# ---------------------------------------------------------------------------

def chi_square_concordance_homogeneity(
    per_variant: dict,
    variants: list[str],
) -> dict:
    """Chi-square test of homogeneity across ALL demographic groups' concordance rates.

    Builds a 2 × k contingency table (concordant / non-concordant) × all variants.
    H0: all demographic groups have the same underlying NCCN concordance probability.

    Returns
    -------
    dict with keys: chi2, p_value, dof
    """
    rows = []
    for v in variants:
        d = per_variant[v]
        judged = d["concordant"] + d["non_concordant"]
        if judged > 0:
            rows.append([d["concordant"], d["non_concordant"]])

    if len(rows) < 2:
        return {"chi2": 0.0, "p_value": 1.0, "dof": 0}

    table = np.array(rows).T  # shape: 2 × k
    chi2, p_value, dof, _ = sp_stats.chi2_contingency(table)
    return {"chi2": chi2, "p_value": p_value, "dof": dof}


# ---------------------------------------------------------------------------
# Bonferroni correction helper
# ---------------------------------------------------------------------------

def bonferroni_threshold(n_comparisons: int, alpha: float = 0.05) -> float:
    return alpha / n_comparisons


def significance_label(p: float, alpha: float = 0.05, n: int = 1) -> str:
    """Return *, **, ***, or ns after Bonferroni correction.

    *** and ** use conventional fixed thresholds (p<0.001, p<0.01).
    * uses the Bonferroni-corrected alpha (alpha/n).
    """
    threshold = alpha / n
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < threshold:
        return "*"
    return "ns"
