#!/usr/bin/env python3
"""Full 28-variant version of Figure 2B (regen_flip_avg.py), for presentation use.
(Filename/output path still say "full29" from before the age variant, Tier E
"elderly_patient_75", was removed from analysis — see
src/generate/variant_injector_v2.py module docstring.)

Same data source and CI method as the main-text 10-row panel; just every variant
instead of the curated subset. Non-destructive: writes panels/p_flip_avg_full29.png.
Run from repo root.
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from plot_publishable_nsclc import MODELS, SUF, BASE, _read

T = 2.571  # t(0.975, df=5) for 95% CI across 6 models

SES = "#C1272D"       # socioeconomic disadvantage (incl. SES-side intersectional)
RACE = "#6A51A3"       # race/ethnicity only
OTHER = "#1B7837"      # geography, age, immigration/language, gender/identity
REF = "#666666"        # privileged / control comparators

# (display label, variant key, colour, category)
ROWS = [
    ("Underinsured", "underinsured_only", SES, "Socioeconomic"),
    ("Uninsured", "uninsured_only", SES, "Socioeconomic"),
    ("Low income", "low_income_patient", SES, "Socioeconomic"),
    ("Unhoused", "unhoused_patient", SES, "Socioeconomic"),
    ("High income", "high_income_patient", REF, "Socioeconomic (control)"),
    ("Medicaid", "medicaid_only", SES, "Insurance"),
    ("Medicare Advantage", "medicare_advantage_only", SES, "Insurance"),
    ("Medicare", "medicare_only", SES, "Insurance"),
    ("Black + unhoused", "black_unhoused", SES, "Race x socioeconomic"),
    ("Low income, Black", "low_income_black", SES, "Race x socioeconomic"),
    ("Black, Medicaid", "black_female_medicaid", SES, "Race x insurance"),
    ("Latina, uninsured", "latina_female_uninsured", SES, "Race x insurance"),
    ("Black, private (priv.)", "black_female_private", REF, "Race x insurance (control)"),
    ("White, Medicaid", "white_female_medicaid", REF, "Race x insurance (control)"),
    ("White male, private (privileged)", "white_male_private", REF, "Race x insurance (privileged)"),
    ("Black", "black_race_only", RACE, "Race/ethnicity"),
    ("Hispanic", "hispanic_race_only", RACE, "Race/ethnicity"),
    ("Asian", "asian_race_only", RACE, "Race/ethnicity"),
    ("Native American", "native_american_race_only", RACE, "Race/ethnicity"),
    ("Middle Eastern", "middle_eastern_race_only", RACE, "Race/ethnicity"),
    ("Multiracial", "multiracial_race_only", RACE, "Race/ethnicity"),
    ("Rural", "rural_patient", OTHER, "Geography"),
    ("Small community hospital", "small_community_hospital", OTHER, "Geography"),
    # Age row ("elderly_patient_75") intentionally excluded — see
    # src/generate/variant_injector_v2.py module docstring.
    ("Immigrant", "immigrant_patient", OTHER, "Immigration/language"),
    ("Limited English", "limited_english_patient", OTHER, "Immigration/language"),
    ("Gay male", "gay_male_patient", OTHER, "Gender/identity"),
    ("Non-binary", "non_binary_patient", OTHER, "Gender/identity"),
    ("Transgender woman", "transgender_woman", OTHER, "Gender/identity"),
]
PANELS = Path("figures/manuscript_combined/panels")
OUT_PANEL = PANELS / "p_flip_avg_full29.png"


def main():
    flips = {m: _read(f"{BASE}{SUF[m]}_flip_rates.csv", {"r": "flip_rate"}) for m in MODELS}
    means, cis = [], []
    for _, key, _c, _cat in ROWS:
        vals = np.array([flips[m].get(key, {}).get("r", np.nan) for m in MODELS], float) * 100
        vals = vals[~np.isnan(vals)]
        means.append(vals.mean())
        cis.append(T * vals.std(ddof=1) / np.sqrt(len(vals)))
    means, cis = np.array(means), np.array(cis)
    grand_mean = means.mean()

    n = len(ROWS); y = np.arange(n)[::-1]
    fig, ax = plt.subplots(figsize=(7.5, 10.5))
    ax.axvline(grand_mean, color="#888888", ls="--", lw=1.0, zorder=1,
               label=f"mean {grand_mean:.0f}%")
    for i, (lab, key, colour, cat) in enumerate(ROWS):
        ax.errorbar(means[i], y[i], xerr=cis[i], fmt="o", ms=6, color=colour,
                    ecolor=colour, elinewidth=1.2, capsize=2.5,
                    markeredgecolor="white", markeredgewidth=0.5, zorder=3)
    ax.set_xlim(0, 27)
    ax.set_ylim(-0.6, n - 0.4)
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in ROWS], fontsize=8)
    for tick, (_, _, colour, _cat) in zip(ax.get_yticklabels(), ROWS):
        tick.set_color(colour)
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel("Treatment-recommendation flip rate (%) vs no-demographics reference",
                  fontsize=9.0)
    ax.set_title("Flip rate uniform across all 28 demographic variants",
                 fontsize=11.0, fontweight="bold", pad=10)
    ax.xaxis.grid(True, ls="--", alpha=0.35, zorder=0)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)

    from matplotlib.lines import Line2D
    legend_handles = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=SES, markersize=7, label="Socioeconomic disadvantage"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=RACE, markersize=7, label="Race/ethnicity only"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=OTHER, markersize=7, label="Geography / language / gender"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=REF, markersize=7, label="Privileged / control comparator"),
        Line2D([0], [0], color="#888888", ls="--", lw=1.0, label=f"mean {grand_mean:.0f}%"),
    ]
    ax.legend(handles=legend_handles, loc="upper center", bbox_to_anchor=(0.5, -0.045),
              ncol=2, frameon=False, fontsize=7.5, handletextpad=0.5, columnspacing=1.2)

    PANELS.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PANEL, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    from PIL import Image
    w, h = Image.open(OUT_PANEL).size
    print(f"wrote {OUT_PANEL}  {w}x{h}  aspect={w/h:.3f}")
    print(f"grand mean: {grand_mean:.1f}%  (range {means.min():.1f}-{means.max():.1f}%)")


if __name__ == "__main__":
    main()
