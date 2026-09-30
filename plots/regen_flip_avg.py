#!/usr/bin/env python3
"""Figure 1B: treatment-recommendation flip rate vs the no-demographics reference,
averaged across the 6 LLMs, summarized by label category (9 rows covering all 28
labels).

Each row shows the category mean (large marker) with a 95% CI across the 6 models:
the category mean is taken within each model first, then the t-interval (df = 5)
is computed over the 6 model-level values. Small open circles just below each row
are the individual labels in that category (each averaged across models). The dashed
line is the mean of all 28 labels.

Category names follow Figure 3 (plot_fig3_care_intensity.py); the comparator split
(matched counterexamples vs privileged comparators) follows Figure 1C.

Writes panels/p_flip_avg.png. Run from repo root.
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from plot_publishable_nsclc import MODELS, SUF, BASE, _read

T = 2.571  # t(0.975, df=5) for 95% CI across 6 models

SES = "#C1272D"; RACE = "#6A51A3"; OTHER = "#1B7837"; REF = "#666666"
# (display name, variant keys, colour)
GROUPS = [
    ("Income / housing", ["unhoused_patient", "low_income_patient"], SES),
    ("Insurance", ["medicaid_only", "underinsured_only", "uninsured_only",
                   "medicare_only", "medicare_advantage_only"], SES),
    ("Race + disadvantage", ["black_unhoused", "low_income_black",
                             "black_female_medicaid", "latina_female_uninsured"], SES),
    ("Race / ethnicity only", ["black_race_only", "hispanic_race_only", "asian_race_only",
                               "native_american_race_only", "middle_eastern_race_only",
                               "multiracial_race_only"], RACE),
    ("Geography", ["small_community_hospital", "rural_patient"], OTHER),
    ("Immigration / language", ["immigrant_patient", "limited_english_patient"], OTHER),
    ("Gender / sexual identity", ["transgender_woman", "gay_male_patient",
                                  "non_binary_patient"], OTHER),
    ("Matched counterexamples", ["black_female_private", "white_female_medicaid"], REF),
    ("Privileged comparators", ["white_male_private", "high_income_patient"], REF),
]
PANELS = Path("figures/manuscript_combined/panels")
OUT_PANEL = PANELS / "p_flip_avg.png"


def main():
    flips = {m: _read(f"{BASE}{SUF[m]}_flip_rates.csv", {"r": "flip_rate"}) for m in MODELS}
    keys = [k for _, ks, _ in GROUPS for k in ks]
    assert len(keys) == 28 and len(set(keys)) == 28, "expected all 28 labels exactly once"
    assert "elderly_patient_75" not in keys

    # rate[model][key] in percent
    rate = {m: {k: flips[m][k]["r"] * 100 for k in keys} for m in MODELS}
    label_mean = {k: np.mean([rate[m][k] for m in MODELS]) for k in keys}
    grand = np.mean(list(label_mean.values()))

    means, cis = [], []
    for _, ks, _ in GROUPS:
        per_model = np.array([np.mean([rate[m][k] for k in ks]) for m in MODELS])
        means.append(per_model.mean())
        cis.append(T * per_model.std(ddof=1) / np.sqrt(len(per_model)))

    n = len(GROUPS); y = np.arange(n)[::-1]
    fig, ax = plt.subplots(figsize=(6.9, 5.0))
    ax.axvline(grand, color="#888888", ls="--", lw=1.0, zorder=1,
               label=f"Mean of all 28 labels, {grand:.1f}%")
    for i, (name, ks, colour) in enumerate(GROUPS):
        ax.scatter([label_mean[k] for k in ks], [y[i] - 0.22] * len(ks), s=18,
                   facecolors="none", edgecolors=colour, linewidths=0.9, alpha=0.8, zorder=2)
        ax.errorbar(means[i], y[i], xerr=cis[i], fmt="o", ms=8.5, color=colour,
                    ecolor=colour, elinewidth=1.4, capsize=3,
                    markeredgecolor="white", markeredgewidth=0.6, zorder=3)
    ax.set_xlim(0, 27)
    ax.set_ylim(-0.6, n - 0.4)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{name} ({len(ks)})" for name, ks, _ in GROUPS], fontsize=11.5)
    for tick, (_, _, colour) in zip(ax.get_yticklabels(), GROUPS):
        tick.set_color(colour)
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel("Treatment-recommendation flip rate (%) vs reference", fontsize=11.5)
    ax.tick_params(axis="x", labelsize=11)
    ax.xaxis.grid(True, ls="--", alpha=0.35, zorder=0)
    ax.set_axisbelow(True)
    for s in (3, 4, 7):   # separators: SES | race only | other | comparators
        ax.axhline((y[s] + y[s - 1]) / 2, color="#dddddd", lw=0.8, zorder=1)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.legend(loc="upper left", frameon=False, fontsize=10.5)

    PANELS.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PANEL, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    from PIL import Image
    w, h = Image.open(OUT_PANEL).size
    print(f"wrote {OUT_PANEL}  {w}x{h}  aspect={w/h:.3f}")
    print(f"grand mean of 28 labels: {grand:.2f}%")
    for (name, ks, _), m_, c in zip(GROUPS, means, cis):
        lm = [label_mean[k] for k in ks]
        print(f"  {name:26s} n={len(ks)}  {m_:5.1f} ± {c:4.1f}   labels {min(lm):.1f}-{max(lm):.1f}")


if __name__ == "__main__":
    main()
