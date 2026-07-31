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


def benjamini_hochberg(pvalues: dict) -> dict:
    """Benjamini-Hochberg FDR-adjusted q-values for a family of tests.

    Parameters
    ----------
    pvalues:
        {key: p_value_or_None}. None entries (untestable comparisons) are
        excluded from the family size m and returned as None.

    Returns
    -------
    dict
        {key: q_value_or_None}, q monotonic and capped at 1.0. The family size
        m is the number of non-None p-values.
    """
    valid = [(k, p) for k, p in pvalues.items() if p is not None]
    m = len(valid)
    out = {k: None for k in pvalues}
    if m == 0:
        return out
    # Ascending by p; q_i = p_i * m / rank, then enforce monotonic non-decreasing
    valid.sort(key=lambda kv: kv[1])
    prev = 1.0
    for i in range(m - 1, -1, -1):       # largest rank → smallest
        k, p = valid[i]
        q = min(prev, p * m / (i + 1))
        out[k] = q
        prev = q
    return out


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


# ---------------------------------------------------------------------------
# Paired continuous-score statistics (1–10 equity scores vs reference)
# ---------------------------------------------------------------------------

def paired_scores(
    ref_scores: dict,
    variant_scores: dict,
) -> tuple[list[float], list[float]]:
    """Align two {case_id: score} maps, keeping only cases scored in BOTH.

    None scores are dropped. Returns (ref_list, variant_list) of equal length,
    paired by case_id, suitable for paired tests against the reference variant.
    """
    ref_aligned: list[float] = []
    var_aligned: list[float] = []
    for case_id, r in ref_scores.items():
        v = variant_scores.get(case_id)
        if r is None or v is None:
            continue
        ref_aligned.append(float(r))
        var_aligned.append(float(v))
    return ref_aligned, var_aligned


def cohens_d_paired(ref: list[float], variant: list[float]) -> float:
    """Paired Cohen's d = mean(variant − ref) / sd(variant − ref)."""
    diffs = np.asarray(variant, dtype=float) - np.asarray(ref, dtype=float)
    if len(diffs) < 2:
        return 0.0
    sd = diffs.std(ddof=1)
    if sd == 0:
        return 0.0
    return float(diffs.mean() / sd)


def paired_delta(
    ref_scores: dict,
    variant_scores: dict,
    test: str = "wilcoxon",
    confidence: float = 0.95,
) -> dict:
    """Compare a variant's continuous scores to the reference, paired by case.

    Parameters
    ----------
    ref_scores, variant_scores:
        {case_id: score_or_None} maps for the reference and the variant.
    test:
        "wilcoxon" (signed-rank, robust at small n; default) or "t" (paired t).

    Returns
    -------
    dict with keys:
        n          paired, non-None case count
        mean       variant mean score
        ref_mean   reference mean score (over the paired cases)
        delta      mean(variant − ref) — negative = variant scored lower
        cohens_d   paired effect size
        ci_low     CI on the mean delta (t-based)
        ci_high
        p_value    two-sided p (None if test undefined, e.g. all diffs zero)
    """
    ref, var = paired_scores(ref_scores, variant_scores)
    n = len(ref)
    if n == 0:
        return {"n": 0, "mean": None, "ref_mean": None, "delta": None,
                "cohens_d": None, "ci_low": None, "ci_high": None, "p_value": None}

    ref_arr = np.asarray(ref, dtype=float)
    var_arr = np.asarray(var, dtype=float)
    diffs = var_arr - ref_arr
    delta = float(diffs.mean())

    # t-based CI on the mean difference
    if n >= 2 and diffs.std(ddof=1) > 0:
        se = diffs.std(ddof=1) / np.sqrt(n)
        t_crit = sp_stats.t.ppf((1 + confidence) / 2, df=n - 1)
        ci_low, ci_high = delta - t_crit * se, delta + t_crit * se
    else:
        ci_low = ci_high = delta

    # Significance test on the paired differences
    p_value: float | None
    if np.allclose(diffs, 0.0):
        p_value = None
    elif test == "t":
        p_value = float(sp_stats.ttest_rel(var_arr, ref_arr).pvalue)
    else:  # wilcoxon signed-rank
        try:
            p_value = float(sp_stats.wilcoxon(var_arr, ref_arr).pvalue)
        except ValueError:
            p_value = None

    return {
        "n":        n,
        "mean":     float(var_arr.mean()),
        "ref_mean": float(ref_arr.mean()),
        "delta":    delta,
        "cohens_d": cohens_d_paired(ref, var),
        "ci_low":   float(ci_low),
        "ci_high":  float(ci_high),
        "p_value":  p_value,
    }
