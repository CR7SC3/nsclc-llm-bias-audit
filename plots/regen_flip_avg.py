#!/usr/bin/env python3
"""DRAFT panel B for the reworked Figure 2: treatment-recommendation flip rate
is stable across demographics, AVERAGED across the 6 LLMs (one clean series
instead of six overlapping ones).

Message: every demographic label perturbs the recommendation ~16% (the test-retest
/ label-salience floor), and that floor is identical for advantaged and
disadvantaged labels -- no demographic group destabilizes the decision.
Includes the privileged "White male, private" as a grey reference anchor.

Non-destructive: writes panels/p_flip_avg.png. Run from repo root.
"""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from plot_publishable_nsclc import MODELS, SUF, BASE, _read

T = 2.571  # t(0.975, df=5) for 95% CI across 6 models

# (display label, variant key, colour)
SES = "#C1272D"; RACE = "#6A51A3"; REF = "#666666"
ROWS = [
    ("Underinsured", "underinsured_only", SES),
    ("Uninsured", "uninsured_only", SES),
    ("Latina female, uninsured", "latina_female_uninsured", SES),
    ("Low income", "low_income_patient", SES),
    ("Black + unhoused", "black_unhoused", SES),
    ("Unhoused", "unhoused_patient", SES),
    ("Black", "black_race_only", RACE),
    ("Hispanic", "hispanic_race_only", RACE),
    ("Asian", "asian_race_only", RACE),
    ("White male, private", "white_male_private", REF),
]
TIER_SPANS = [("Socioeconomic\ndisadvantage", SES, 0, 6),
              ("Race only", RACE, 6, 9),
              ("Privileged", REF, 9, 10)]
PANELS = Path("figures/manuscript_combined/panels")
OUT_PANEL = PANELS / "p_flip_avg.png"


def main():
    flips = {m: _read(f"{BASE}{SUF[m]}_flip_rates.csv", {"r": "flip_rate"}) for m in MODELS}
    means, cis = [], []
    for _, key, _c in ROWS:
        vals = np.array([flips[m].get(key, {}).get("r", np.nan) for m in MODELS], float) * 100
        vals = vals[~np.isnan(vals)]
        means.append(vals.mean())
        cis.append(T * vals.std(ddof=1) / np.sqrt(len(vals)))
    means, cis = np.array(means), np.array(cis)
    demo_mean = means[:9].mean()          # grand mean of the 9 demographic variants

    n = len(ROWS); y = np.arange(n)[::-1]
    fig, ax = plt.subplots(figsize=(6.9, 5.0))
    ax.axvline(demo_mean, color="#888888", ls="--", lw=1.0, zorder=1,
               label=f"mean {demo_mean:.0f}%")
    for i, (lab, key, colour) in enumerate(ROWS):
        ax.errorbar(means[i], y[i], xerr=cis[i], fmt="o", ms=7, color=colour,
                    ecolor=colour, elinewidth=1.4, capsize=3,
                    markeredgecolor="white", markeredgewidth=0.6, zorder=3)
    ax.set_xlim(0, 27)
    ax.set_ylim(-0.6, n - 0.4)
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in ROWS], fontsize=9)
    for tick, (_, _, colour) in zip(ax.get_yticklabels(), ROWS):
        tick.set_color(colour)
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel("Treatment-recommendation flip rate (%) vs no-demographics reference",
                  fontsize=9.0)
    ax.set_title("Flip rate uniform across demographics",
                 fontsize=10.0, fontweight="bold", pad=8)
    ax.xaxis.grid(True, ls="--", alpha=0.35, zorder=0)
    ax.set_axisbelow(True)
    for name, colour, s, e in TIER_SPANS:
        if s != 0:
            ax.axhline((y[s] + y[s - 1]) / 2, color="#dddddd", lw=0.8, zorder=1)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.legend(loc="lower right", frameon=False, fontsize=8.5)

    PANELS.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PANEL, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    from PIL import Image
    w, h = Image.open(OUT_PANEL).size
    print(f"wrote {OUT_PANEL}  {w}x{h}  aspect={w/h:.3f}")
    print("demographic means (%):", ", ".join(f"{m:.1f}" for m in means))


if __name__ == "__main__":
    main()
