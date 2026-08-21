"""Fig 3D: added soft-framing intensity collapsed to demographic AXIS (tier).

Companion to the per-variant forest (Fig 3A): every disadvantage variant is pooled
into its demographic tier and averaged across all six models, so a single glance
shows WHICH axis of marginalization drives the soft-framing shift. Socioeconomic
and other structural-identity axes sit far right (red); the race-only axis and the
privileged control sit on zero (grey) — the "SES, not race" dissociation at the
axis level.

Each bar = mean Cohen's d over the tier's (variant x model) cells; whiskers = 95% CI
(t-based on the pooled cells). Reads results/analysis/v2_genie_bpc_nsclc*_soft_intensity.csv.
Writes a titleless panel to figures/manuscript_combined/panels/p_tier_bias.png
(the A/B/C/D letter is stamped by combine_figures.py) and a standalone copy to
figures/manuscript/Fig03D_tier_bias.png.
"""
from __future__ import annotations

import csv
from math import sqrt
from pathlib import Path

import matplotlib.pyplot as plt
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "results/analysis/v2_genie_bpc_nsclc"
PANELS = ROOT / "figures/manuscript_combined/panels"; PANELS.mkdir(parents=True, exist_ok=True)
MAN = ROOT / "figures/manuscript"; MAN.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "savefig.facecolor": "white",
    "axes.spines.top": False,
    "axes.spines.right": False,
})

# all six vendor arms (soft_intensity filename suffixes)
MODEL_SUFFIXES = [
    "", "_deepseek-chat", "_gpt-4o", "_gpt-4o-mini",
    "_meta-llama-Llama-3.3-70B-Instruct-Turbo",
    "_openrouter-meta-llama-llama-3.1-8b-instruct",
]

C_SES = "#d96666"     # socioeconomic / structural-identity axes (elevated) — Fig 5 shared red
C_NULL = "#adadad"    # race-only axis + privileged control (on zero) — Fig 5 shared baseline grey

# tier -> (variant keys, is_elevated_axis). Order is cosmetic; bars re-sort by mean.
TIERS = [
    ("Intersectional (SES × race)",
     ["latina_female_uninsured", "black_unhoused", "low_income_black", "black_female_medicaid"], True),
    ("Insurance status",
     ["uninsured_only", "medicaid_only", "underinsured_only", "medicare_only",
      "medicare_advantage_only", "white_female_medicaid"], True),
    ("Income / housing",
     ["low_income_patient", "unhoused_patient"], True),
    ("Immigration / language",
     ["immigrant_patient", "limited_english_patient"], False),
    ("Gender / sexual identity",
     ["non_binary_patient", "transgender_woman", "gay_male_patient"], False),
    ("Geography (rural)",
     ["rural_patient", "small_community_hospital"], False),
    # Age tier ("elderly_patient_75") intentionally excluded — see
    # src/generate/variant_injector_v2.py module docstring.
    ("Race / ethnicity",
     ["black_race_only", "hispanic_race_only", "asian_race_only",
      "native_american_race_only", "middle_eastern_race_only", "multiracial_race_only"], False),
    ("Privileged (control)",
     ["white_male_private", "high_income_patient"], False),
]


def load_d():
    """variant -> list of Cohen's d, one per model that reports it."""
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
    """Mean + 95% t-based CI over a list of Cohen's d cells (one per model)."""
    n = len(vals)
    m = sum(vals) / n
    sd = sqrt(sum((v - m) ** 2 for v in vals) / (n - 1)) if n > 1 else 0.0
    sem = sd / sqrt(n) if n > 1 else 0.0
    tcrit = stats.t.ppf(0.975, n - 1) if n > 1 else 0.0
    return m, m - tcrit * sem, m + tcrit * sem


def main():
    dvals = load_d()
    rows = []  # (label, mean, lo, hi, elevated, n)
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

    rows.sort(key=lambda r: r[1])                      # ascending -> largest at top
    labels = [r[0] for r in rows]
    means = [r[1] for r in rows]
    lo = [r[1] - r[2] for r in rows]
    hi = [r[3] - r[1] for r in rows]
    colours = [C_SES if r[4] else C_NULL for r in rows]
    ys = range(len(rows))

    fig, ax = plt.subplots(figsize=(6.6, 5.6))
    ax.axvline(0, color="#333", lw=0.8, zorder=1)
    ax.barh(list(ys), means, color=colours, height=0.68, zorder=2,
            edgecolor="k", linewidth=0.5,
            error_kw=dict(ecolor="#444", elinewidth=1.1, capsize=3),
            xerr=[lo, hi])
    for y, r in zip(ys, rows):
        ns = r[2] < 0 < r[3]                    # 95% CI crosses zero -> not significant
        txt = f"{r[1]:+.2f}" + ("  (ns)" if ns else "")
        ax.text(r[3] + 0.025, y, txt, va="center", ha="left",
                fontsize=8.0, color="#777" if ns else "#333")   # just past the upper whisker

    ax.set_yticks(list(ys))
    ax.set_yticklabels(labels, fontsize=9)
    for lbl, r in zip(ax.get_yticklabels(), rows):
        if not r[4]:
            lbl.set_color("#777")
    ax.set_xlim(-0.15, 2.05)   # extra right margin reserved for the marginal-race-effect inset
    ax.set_ylim(-0.7, len(rows) - 0.3)
    ax.set_xlabel("Added soft-framing intensity (Cohen's $d$)", fontsize=9)
    ax.set_title("Bias by demographic axis", fontsize=11, fontweight="bold",
                 loc="left", pad=8)
    ax.tick_params(length=0)
    fig.tight_layout()

    # --- marginal race contrast at fixed SES (holding housing status fixed) ---
    # Same source/aggregation as load_d(): one Cohen's d per model, averaged.
    # "black_unhoused" vs "unhoused_patient" isolates the effect of ADDING race
    # on top of an already-matched SES/housing disadvantage -- the evidence for
    # "SES, not race" that the main bars alone don't make self-contained.
    bu = dvals.get("black_unhoused", [])
    up = dvals.get("unhoused_patient", [])
    if bu and up and len(bu) == len(up):
        m_bu, lo_bu, hi_bu = mean_ci(bu)
        m_up, lo_up, hi_up = mean_ci(up)
        diffs = [b - u for b, u in zip(bu, up)]
        m_diff, lo_diff, hi_diff = mean_ci(diffs)
        ns = lo_diff < 0 < hi_diff

        inset = ax.inset_axes([0.72, 0.70, 0.27, 0.27])
        xs = [0, 1]
        inset.bar(xs, [m_up, m_bu], width=0.55,
                  color=[C_SES, C_SES], edgecolor="k", linewidth=0.5,
                  yerr=[[m_up - lo_up, m_bu - lo_bu], [hi_up - m_up, hi_bu - m_bu]],
                  error_kw=dict(ecolor="#444", elinewidth=1.0, capsize=2.5), zorder=2)
        inset.set_xticks(xs)
        inset.set_xticklabels(["unhoused", "Black +\nunhoused"], fontsize=6.5)
        inset.set_ylabel("Cohen's $d$", fontsize=6.5, labelpad=2)
        inset.tick_params(axis="y", labelsize=6.5, length=0)
        inset.tick_params(axis="x", length=0)
        for spine in ("top", "right"):
            inset.spines[spine].set_visible(False)
        inset.set_title("Marginal race effect at fixed SES",
                         fontsize=8.5, fontweight="bold", loc="center", pad=14, color="#333")
        diff_txt = (f"Black+unhoused $-$ unhoused = {m_diff:+.2f}  "
                    f"[{lo_diff:+.2f}, {hi_diff:+.2f}]" + ("  (ns)" if ns else ""))
        inset.text(0.5, 1.04, diff_txt, transform=inset.transAxes,
                   ha="center", va="bottom", fontsize=7.0,
                   color="#777" if ns else "#333")
        inset.set_facecolor("white")
        inset.patch.set_alpha(0.9)
        print(f"marginal race contrast (fixed SES): black_unhoused d={m_bu:+.3f} "
              f"[{lo_bu:+.3f}, {hi_bu:+.3f}]  unhoused_patient d={m_up:+.3f} "
              f"[{lo_up:+.3f}, {hi_up:+.3f}]  diff={m_diff:+.3f} "
              f"[{lo_diff:+.3f}, {hi_diff:+.3f}]" + ("  (ns)" if ns else ""))
    else:
        print("WARNING: black_unhoused / unhoused_patient variant missing or "
              "unequal model coverage -- inset not drawn "
              f"(black_unhoused n={len(bu)}, unhoused_patient n={len(up)})")

    p_panel = PANELS / "p_tier_bias.png"
    fig.savefig(p_panel, dpi=200, bbox_inches="tight")
    fig.savefig(MAN / "Fig03D_tier_bias.png", dpi=200, bbox_inches="tight")
    fig.savefig(MAN / "Fig03D_tier_bias.pdf", bbox_inches="tight")
    print(f"wrote {p_panel}")
    for r in reversed(rows):
        print(f"  {r[0]:28s} d={r[1]:+.3f}  [{r[2]:+.3f}, {r[3]:+.3f}]  n={r[5]}")


if __name__ == "__main__":
    main()
