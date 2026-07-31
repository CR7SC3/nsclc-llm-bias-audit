"""Escalation-ladder panel: bias magnitude across the THREE output layers, on one
shared horizontal effect-size axis, in escalation order top -> bottom:

  1. Guideline decision (NCCN concordance)   -- INVARIANT layer
  2. Care intensity (trial / de-escalation)  -- INTERMEDIATE layer
  3. Language framing (stigma composite)     -- TOP/largest layer

This turns the paper's spine metaphor ("the softer the output, the more bias
leaks in") into a plotted result: the three markers step near-zero -> small ->
large as the output gets softer/more discretionary.

AXIS / ENCODING NOTE (read before changing numbers):
The three layers are measured on genuinely different natural scales:
  - Layer 1 (decision) is a %-concordance delta (pre-registered binary NCCN
    label, dem vs. no_demographics), tiny by construction (<=1.1 pp per model,
    per plots/plot_publishable_nsclc.py fig2_concordance()).
  - Layer 2 (care intensity) is a POOLED DIRECTIONAL PROPORTION (fraction of
    dem-vs-ref decisions that moved in the harm direction), from
    plots/plot_fig3_care_intensity.py / results/analysis/advanced_care_per_model.csv.
  - Layer 3 (framing) is a Cohen's d on a continuous soft-framing-intensity
    score, from results/analysis/v2_genie_bpc_nsclc*_soft_intensity.csv
    (same source as plots/plot_tier_bias.py).
We refuse to force these onto one metric by fiat. Instead we put ALL THREE on
a single Cohen's-d-STYLE arcsine effect-size axis:
  - Layers 1 and 2 are naturally proportions (dem-vs-ref rate; harm-direction
    rate vs. the 50/50 null), so both are converted via COHEN'S H
    (h = 2*arcsin(sqrt(p1)) - 2*arcsin(sqrt(p2))), which lives on the same
    "small effect ~0.2, medium ~0.5, large ~0.8" scale as Cohen's d and IS the
    standard effect size for two-proportion comparisons.
  - Layer 3 is already a Cohen's d on a continuous score; d and h are on
    comparable (not identical) footing -- both are "SD-scaled mean effect
    size" quantities. We plot them on the same axis with an explicit dual
    label ("d / h") and flag layer 2 as an APPROXIMATE mapping in the caption
    and in-panel annotation. No p-value or CI is stretched across scales.
This is the more honest of the two options offered in the brief (transparent
Cohen's-h mapping vs. an invented "relative bias magnitude" index); a made-up
normalized index would hide exactly the scale mismatch the council is
checking for.

Layer 1 (decision, Cohen's h, dem vs. no_demographics, mean over 6 models):
  ref/dem concordance pairs from plots/plot_publishable_nsclc.py fig2_concordance()
  (pre-registered binary NCCN concordance rates per model). mean h = -0.002,
  95% CI [-0.024, +0.021], n=6 models -- sits inside the TOST equivalence
  margin d/h = +/-0.10 used for the decision-layer equivalence claim.

Layer 2 (care intensity, Cohen's h vs. 0.50 null, pooled over both metrics):
  results/analysis/advanced_care_per_model.csv, read via the same hfrac()
  logic as plots/plot_fig3_care_intensity.py.
  Advanced-treatment (clinical-trial mention): 66/84 harmward (p=0.786) -> h=+0.608
  De-escalation (palliative/BSC framing):       64/84 harmward (p=0.762) -> h=+0.551
  mean h = +0.580 (one-sided binomial p<0.001 pooled, per plot_fig3_care_intensity.py)

Layer 3 (framing, Cohen's d, income/housing tier, pooled over 6 models):
  results/analysis/v2_genie_bpc_nsclc*_soft_intensity.csv, "low_income_patient"
  + "unhoused_patient" variants (same cells as plots/plot_tier_bias.py
  "Income / housing" tier). mean d = +0.765, 95% CI [+0.466, +1.064], n=12 cells.

Writes a titleless panel to figures/manuscript_combined/panels/p_ladder.png
(the A/B/C letter is stamped by combine_figures.py) and a standalone copy to
figures/manuscript/Fig_ladder.png.
"""
from __future__ import annotations

import csv
from math import asin, sqrt
from pathlib import Path

import matplotlib.pyplot as plt
from scipy import stats
from scipy.stats import binomtest
from statsmodels.stats.proportion import proportion_confint

ROOT = Path(__file__).resolve().parent.parent
PANELS = ROOT / "figures/manuscript_combined/panels"; PANELS.mkdir(parents=True, exist_ok=True)
MAN = ROOT / "figures/manuscript"; MAN.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "savefig.facecolor": "white",
    "axes.spines.top": False,
    "axes.spines.right": False,
})

C_NULL = "#adadad"   # Fig 5 shared baseline grey -- invariant decision layer
C_MID = "#e0968f"    # escalation ramp midpoint -- care-intensity (intermediate) layer
C_SES = "#d96666"    # Fig 5 shared SES red -- framing layer (largest effect)

EQUIV_MARGIN = 0.10  # TOST equivalence margin (d/h = +/- 0.10) for the decision layer


def cohens_h(p1: float, p2: float) -> float:
    return 2 * asin(sqrt(p1)) - 2 * asin(sqrt(p2))


def layer1_decision():
    """Cohen's h per model (dem vs. no_demographics, pre-registered binary NCCN
    concordance), mean + t-based 95% CI over 6 models. Source rates copied
    verbatim from plots/plot_publishable_nsclc.py fig2_concordance()."""
    ref = {"gemini-2.5-flash": 81.7, "deepseek-chat": 90.7, "llama-3.3-70B": 75.9,
           "llama-3.1-8B": 49.5, "gpt-4o": 89.7, "gpt-4o-mini": 55.6}
    dem = {"gemini-2.5-flash": 82.8, "deepseek-chat": 90.6, "llama-3.3-70B": 75.5,
           "llama-3.1-8B": 49.0, "gpt-4o": 88.7, "gpt-4o-mini": 56.4}
    hs = [cohens_h(dem[m] / 100, ref[m] / 100) for m in ref]
    n = len(hs)
    mean = sum(hs) / n
    sd = sqrt(sum((x - mean) ** 2 for x in hs) / (n - 1))
    sem = sd / sqrt(n)
    tcrit = stats.t.ppf(0.975, n - 1)
    return mean, mean - tcrit * sem, mean + tcrit * sem, n


def layer2_care_intensity():
    """Pooled directional-harm proportion (2 metrics x 6 models = 84 cells each),
    from results/analysis/advanced_care_per_model.csv, converted to Cohen's h
    vs. the 0.50 no-bias null. Mirrors hfrac() in plots/plot_fig3_care_intensity.py."""
    src = ROOT / "results/analysis/advanced_care_per_model.csv"
    d = {}
    for r in csv.DictReader(open(src)):
        d.setdefault(r["variant"], {})[r["model"]] = (float(r["ct_net"]), float(r["pall_net"]))
    marginal = ["unhoused_patient", "low_income_patient", "medicaid_only", "underinsured_only",
                "uninsured_only", "medicare_only", "medicare_advantage_only",
                "small_community_hospital", "rural_patient", "immigrant_patient",
                "limited_english_patient", "transgender_woman", "gay_male_patient",
                "non_binary_patient"]
    models = sorted({m for v in d.values() for m in v})

    def hfrac(idx, harm_neg):
        cells = [d[v][m][idx] for v in marginal for m in models if m in d.get(v, {})]
        k = sum(1 for x in cells if (x < 0 if harm_neg else x > 0))
        n = len(cells)
        p = binomtest(k, n, 0.5, alternative="greater").pvalue
        return k, n, p

    k_ct, n_ct, p_ct = hfrac(0, True)     # advanced treatment / clinical-trial mention
    k_pall, n_pall, p_pall = hfrac(1, False)  # de-escalation / palliative-BSC

    h_ct = cohens_h(k_ct / n_ct, 0.5)
    h_pall = cohens_h(k_pall / n_pall, 0.5)
    lo_ct, hi_ct = proportion_confint(k_ct, n_ct, method="wilson")
    lo_pall, hi_pall = proportion_confint(k_pall, n_pall, method="wilson")
    h_lo = (cohens_h(lo_ct, 0.5) + cohens_h(lo_pall, 0.5)) / 2
    h_hi = (cohens_h(hi_ct, 0.5) + cohens_h(hi_pall, 0.5)) / 2
    mean_h = (h_ct + h_pall) / 2
    detail = {
        "advanced_treatment": (k_ct, n_ct, p_ct, h_ct),
        "de_escalation": (k_pall, n_pall, p_pall, h_pall),
    }
    return mean_h, h_lo, h_hi, detail


def layer3_framing():
    """Cohen's d, income/housing tier (low_income_patient + unhoused_patient),
    pooled over 6 vendor arms -- same cells as the "Income / housing" tier in
    plots/plot_tier_bias.py."""
    base = ROOT / "results/analysis/v2_genie_bpc_nsclc"
    suffixes = ["", "_deepseek-chat", "_gpt-4o", "_gpt-4o-mini",
                "_meta-llama-Llama-3.3-70B-Instruct-Turbo",
                "_openrouter-meta-llama-llama-3.1-8b-instruct"]
    variants = ["low_income_patient", "unhoused_patient"]
    cells = []
    for suf in suffixes:
        p = Path(f"{base}{suf}_soft_intensity.csv")
        if not p.exists():
            continue
        for r in csv.DictReader(open(p, newline="")):
            if r["variant"] not in variants:
                continue
            try:
                cells.append(float(r["cohens_d"]))
            except (ValueError, KeyError):
                continue
    n = len(cells)
    mean = sum(cells) / n
    sd = sqrt(sum((c - mean) ** 2 for c in cells) / (n - 1))
    sem = sd / sqrt(n)
    tcrit = stats.t.ppf(0.975, n - 1)
    return mean, mean - tcrit * sem, mean + tcrit * sem, n


def main():
    m1, lo1, hi1, n1 = layer1_decision()
    m2, lo2, hi2, detail2 = layer2_care_intensity()
    m3, lo3, hi3, n3 = layer3_framing()

    rows = [
        ("Guideline decision\n(NCCN concordance)", m1, lo1, hi1, C_NULL,
         f"h={m1:+.3f}  [{lo1:+.3f}, {hi1:+.3f}]  n={n1} models"),
        ("Care intensity\n(trial / de-escalation framing)", m2, lo2, hi2, C_MID,
         f"h={m2:+.3f}  [{lo2:+.3f}, {hi2:+.3f}]  (approx. mapping, see note)"),
        ("Language framing\n(stigma composite, SES)", m3, lo3, hi3, C_SES,
         f"d={m3:+.3f}  [{lo3:+.3f}, {hi3:+.3f}]  n={n3} cells"),
    ]
    ys = [2, 1, 0]  # top -> bottom = escalation order

    fig, ax = plt.subplots(figsize=(7.4, 3.6))

    # TOST equivalence band, drawn only around the decision-layer row
    band_y = ys[0]
    ax.axvspan(-EQUIV_MARGIN, EQUIV_MARGIN, ymin=(band_y - 0.42 + 0.5) / 3,
               ymax=(band_y + 0.42 + 0.5) / 3, color="#2c7a4b", alpha=0.12, zorder=0)

    ax.axvline(0, color="#333", lw=0.8, zorder=1)

    for (label, mean, lo, hi, color, note), y in zip(rows, ys):
        ax.plot([lo, hi], [y, y], color=color, lw=2.2, zorder=2, solid_capstyle="round")
        ax.plot(mean, y, "o", ms=11, color=color, mec="k", mew=0.6, zorder=3)
        ax.text(max(hi, mean) + 0.05, y + 0.16, note, va="bottom", ha="left",
                fontsize=7.6, color="#555")

    ax.set_yticks(ys)
    ax.set_yticklabels([r[0] for r in rows], fontsize=9.5)
    ax.set_ylim(-0.7, 2.7)
    ax.set_xlim(-0.25, 1.25)
    ax.set_xlabel("Bias magnitude (Cohen's $d$ / Cohen's $h$ effect-size axis)", fontsize=9)
    ax.text(0.0, 1.04, "Escalation ladder: bias grows with output softness",
            transform=ax.transAxes, fontsize=10.5, fontweight="bold", ha="left", va="bottom")
    ax.text(-EQUIV_MARGIN, 2.55, f"equivalence band $\\pm${EQUIV_MARGIN:.2f}",
            fontsize=6.8, color="#2c7a4b", ha="left", va="bottom", style="italic")
    ax.tick_params(length=0)
    fig.tight_layout()

    p_panel = PANELS / "p_ladder.png"
    fig.savefig(p_panel, dpi=200, bbox_inches="tight")
    fig.savefig(MAN / "Fig_ladder.png", dpi=200, bbox_inches="tight")
    print(f"wrote {p_panel}")
    print(f"wrote {MAN / 'Fig_ladder.png'}")
    for label, mean, lo, hi, color, note in rows:
        print(f"  {label.splitlines()[0]:40s} mean={mean:+.4f}  CI=[{lo:+.4f}, {hi:+.4f}]  {note}")
    print("  Layer 2 detail:", detail2)


if __name__ == "__main__":
    main()
