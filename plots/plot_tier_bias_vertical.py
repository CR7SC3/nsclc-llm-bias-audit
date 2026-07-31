"""Poster-only vertical-bar version of Fig 3D (bias by demographic axis).

Same data/aggregation as plot_tier_bias.py, but transposed to VERTICAL bars so it
tiles as a landscape panel in the 2-column poster grid. Axis labels stay upright
(angled), the "SES not race" dissociation reads left-to-right (most-biased axis on
the left, race/control at zero on the right), and the marginal-race-at-fixed-SES
inset is kept. Writes poster_figures/_raw_bias_by_axis_vertical.png only; does NOT
touch the manuscript panel.
"""
from __future__ import annotations

import csv
from math import sqrt
from pathlib import Path

import matplotlib.pyplot as plt
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "results/analysis/v2_genie_bpc_nsclc"
OUT = ROOT / "poster_figures"; OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "savefig.facecolor": "white",
    "axes.spines.top": False,
    "axes.spines.right": False,
})

MODEL_SUFFIXES = [
    "", "_deepseek-chat", "_gpt-4o", "_gpt-4o-mini",
    "_meta-llama-Llama-3.3-70B-Instruct-Turbo",
    "_openrouter-meta-llama-llama-3.1-8b-instruct",
]

C_SES = "#d96666"
C_NULL = "#adadad"

TIERS = [
    ("Intersectional\n(SES × race)",
     ["latina_female_uninsured", "black_unhoused", "low_income_black", "black_female_medicaid"], True),
    ("Insurance\nstatus",
     ["uninsured_only", "medicaid_only", "underinsured_only", "medicare_only",
      "medicare_advantage_only", "white_female_medicaid"], True),
    ("Income /\nhousing",
     ["low_income_patient", "unhoused_patient"], True),
    ("Immigration /\nlanguage",
     ["immigrant_patient", "limited_english_patient"], False),
    ("Gender /\nsexual identity",
     ["non_binary_patient", "transgender_woman", "gay_male_patient"], False),
    ("Geography\n(rural)",
     ["rural_patient", "small_community_hospital"], False),
    ("Age\n(elderly 75)",
     ["elderly_patient_75"], False),
    ("Race /\nethnicity",
     ["black_race_only", "hispanic_race_only", "asian_race_only",
      "native_american_race_only", "middle_eastern_race_only", "multiracial_race_only"], False),
    ("Privileged\n(control)",
     ["white_male_private", "high_income_patient"], False),
]


def load_d():
    d = {}
    for suf in MODEL_SUFFIXES:
        p = Path(f"{BASE}{suf}_soft_intensity.csv")
        if not p.exists():
            continue
        for r in csv.DictReader(open(p, newline="")):
            try:
                val = float(r["cohens_d"])
            except (ValueError, KeyError):
                continue
            d.setdefault(r["variant"], []).append(val)
    return d


def mean_ci(vals):
    n = len(vals)
    m = sum(vals) / n
    sd = sqrt(sum((v - m) ** 2 for v in vals) / (n - 1)) if n > 1 else 0.0
    sem = sd / sqrt(n) if n > 1 else 0.0
    tcrit = stats.t.ppf(0.975, n - 1) if n > 1 else 0.0
    return m, m - tcrit * sem, m + tcrit * sem


def main():
    dvals = load_d()
    rows = []
    for label, variants, elevated in TIERS:
        cells = [v for vk in variants for v in dvals.get(vk, [])]
        if not cells:
            continue
        n = len(cells)
        mean = sum(cells) / n
        sd = sqrt(sum((c - mean) ** 2 for c in cells) / (n - 1)) if n > 1 else 0.0
        sem = sd / sqrt(n) if n > 1 else 0.0
        tcrit = stats.t.ppf(0.975, n - 1) if n > 1 else 0.0
        rows.append((label, mean, mean - tcrit * sem, mean + tcrit * sem, elevated, n))

    rows.sort(key=lambda r: -r[1])                     # descending -> largest bar on the LEFT
    labels = [r[0] for r in rows]
    means = [r[1] for r in rows]
    lo = [r[1] - r[2] for r in rows]
    hi = [r[3] - r[1] for r in rows]
    colours = [C_SES if r[4] else C_NULL for r in rows]
    xs = range(len(rows))

    fig, ax = plt.subplots(figsize=(8.4, 5.4))
    ax.axhline(0, color="#333", lw=0.8, zorder=1)
    ax.bar(list(xs), means, color=colours, width=0.68, zorder=2,
           edgecolor="k", linewidth=0.5,
           error_kw=dict(ecolor="#444", elinewidth=1.1, capsize=3),
           yerr=[lo, hi])
    for x, r in zip(xs, rows):
        ns = r[2] < 0 < r[3]
        txt = f"{r[1]:+.2f}" + ("\n(ns)" if ns else "")
        ax.text(x, r[3] + 0.03, txt, va="bottom", ha="center",
                fontsize=8.0, color="#777" if ns else "#333")

    ax.set_xticks(list(xs))
    ax.set_xticklabels(labels, fontsize=10.5, rotation=0)
    for lbl, r in zip(ax.get_xticklabels(), rows):
        if not r[4]:
            lbl.set_color("#777")
    ax.set_ylim(-0.12, 1.35)
    ax.set_xlim(-0.7, len(rows) - 0.3)
    ax.set_ylabel("Added soft-framing intensity (Cohen's $d$)", fontsize=9)
    ax.set_title("Bias by demographic axis", fontsize=12, fontweight="bold",
                 loc="left", pad=8)
    ax.tick_params(length=0)

    # marginal race contrast at fixed SES -- enlarged inset floats top-right
    bu = dvals.get("black_unhoused", [])
    up = dvals.get("unhoused_patient", [])
    if bu and up and len(bu) == len(up):
        m_bu, lo_bu, hi_bu = mean_ci(bu)
        m_up, lo_up, hi_up = mean_ci(up)
        diffs = [b - u for b, u in zip(bu, up)]
        m_diff, lo_diff, hi_diff = mean_ci(diffs)
        t_stat, p_val = stats.ttest_rel(bu, up)   # paired: adding race at fixed SES
        ns = p_val >= 0.05

        inset = ax.inset_axes([0.55, 0.47, 0.42, 0.47])
        ix = [0, 1]
        inset.bar(ix, [m_up, m_bu], width=0.58,
                  color=[C_SES, C_SES], edgecolor="k", linewidth=0.6,
                  yerr=[[m_up - lo_up, m_bu - lo_bu], [hi_up - m_up, hi_bu - m_bu]],
                  error_kw=dict(ecolor="#444", elinewidth=1.1, capsize=3.5), zorder=2)
        inset.set_xticks(ix)
        inset.set_xticklabels(["unhoused", "Black +\nunhoused"], fontsize=8.5)
        inset.set_ylabel("Cohen's $d$", fontsize=8.5, labelpad=2)
        inset.tick_params(axis="y", labelsize=8.0, length=0)
        inset.tick_params(axis="x", length=0)
        for spine in ("top", "right"):
            inset.spines[spine].set_visible(False)

        # significance bracket between the two bars, carrying the paired statistic
        ytop = max(hi_up, hi_bu)
        y_br = ytop + 0.11
        inset.plot([0, 0, 1, 1], [ytop + 0.03, y_br, y_br, ytop + 0.03],
                   color="#444", lw=1.0, zorder=3)
        p_txt = "p < 0.001" if p_val < 0.001 else f"p = {p_val:.2f}"
        stat_txt = fr"$\Delta d$ = {m_diff:+.2f},  {p_txt}" + ("  (ns)" if ns else "")
        inset.text(0.5, y_br + 0.02, stat_txt,
                   ha="center", va="bottom", fontsize=8.0, color="#333")
        inset.set_ylim(0, y_br + 0.30)
        inset.set_xlim(-0.65, 1.65)
        inset.set_title("Adding race at fixed SES", fontsize=9.0,
                        loc="center", pad=6, color="#333", fontweight="bold")
        inset.set_facecolor("white")
        inset.patch.set_alpha(0.92)

    fig.tight_layout()
    p_out = OUT / "_raw_bias_by_axis_vertical.png"
    fig.savefig(p_out, dpi=220, bbox_inches="tight")
    print(f"wrote {p_out}")
    for r in rows:
        print(f"  {r[0][:20]:20s} d={r[1]:+.3f}  [{r[2]:+.3f}, {r[3]:+.3f}]  n={r[5]}")


if __name__ == "__main__":
    main()
