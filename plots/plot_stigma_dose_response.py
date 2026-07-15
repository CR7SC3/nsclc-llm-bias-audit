"""Fig 7 twin — stigma dose-response as small multiples (one panel per model).

Companion to the CI-bearing Fig 7 bar chart: shows the stigmatizing-language rate
as a CURVE across an ordinal socioeconomic-disadvantage ladder, so the paper's
headline word -- "monotonically" -- becomes visually and inferentially testable
per model. Each panel highlights one model (colour + 95% Wilson CI ribbon) over
ghost lines of the other five for context. Race-only is drawn OFF the ladder as a
non-SES reference (it carries no socioeconomic disadvantage), making "race is not
on the dose axis" explicit.

The x-axis is an ORDINAL rank (spacing arbitrary, per reviewer note); the
monotone-trend claim is backed by a per-model Cochran-Armitage trend test on the
SES ladder (the correct trend test for a binary outcome across ordered groups),
annotated in each panel.

Reads results/analysis/panel_stigma_rates.csv (k, n, rate, Wilson CI per model x
stratum -- same numbers as Fig 7).
Output -> figures/manuscript/Fig7b_stigma_dose_response.png
Run:  python3 plots/plot_stigma_dose_response.py
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm

from plots.plot_publishable_nsclc import MODELS, MC, ML

OUT = Path("figures/manuscript"); OUT.mkdir(parents=True, exist_ok=True)
CSV = "results/analysis/panel_stigma_rates.csv"

# ordinal SES-disadvantage ladder (spacing arbitrary — treated as ranks 0..4)
LADDER = ["control", "uninsured", "underinsured", "low_income", "unhoused"]
LADDER_NICE = ["white-male\ncontrol", "uninsured", "underinsured", "low\nincome", "unhoused"]
RACE = "race_only"          # off-ladder non-SES reference


def cochran_armitage(ks, ns, ts):
    """Two-sided Cochran-Armitage trend z and p from per-group successes k_i,
    totals n_i, and ordinal scores t_i."""
    ks, ns, ts = map(np.asarray, (ks, ns, ts))
    N = ns.sum(); p = ks.sum() / N
    num = np.sum(ts * (ks - p * ns))
    var = p * (1 - p) * (np.sum(ns * ts ** 2) - np.sum(ns * ts) ** 2 / N)
    if var <= 0:
        return 0.0, 1.0
    z = num / np.sqrt(var)
    return z, 2 * (1 - norm.cdf(abs(z)))


def main():
    df = pd.read_csv(CSV)
    xs = np.arange(len(LADDER))          # 0..4

    # precompute each model's ladder curve (for ghost lines)
    curves = {}
    for m in MODELS:
        sub = df[df.model == m].set_index("stratum")
        curves[m] = np.array([sub.loc[s, "rate"] * 100 for s in LADDER])

    fig, axes = plt.subplots(2, 3, figsize=(13.5, 7.4), sharex=True, sharey=True)
    for ax, m in zip(axes.flat, MODELS):
        sub = df[df.model == m].set_index("stratum")
        rate = np.array([sub.loc[s, "rate"] * 100 for s in LADDER])
        lo = np.array([sub.loc[s, "ci_low"] * 100 for s in LADDER])
        hi = np.array([sub.loc[s, "ci_high"] * 100 for s in LADDER])

        # ghost lines: the other five models
        for m2 in MODELS:
            if m2 != m:
                ax.plot(xs, curves[m2], color="0.8", lw=1.0, zorder=1)
        # highlighted model + Wilson CI ribbon
        ax.fill_between(xs, lo, hi, color=MC[m], alpha=0.22, zorder=2)
        ax.plot(xs, rate, color=MC[m], lw=2.2, marker="o", ms=5,
                markeredgecolor="k", markeredgewidth=0.5, zorder=3)

        # race-only off-ladder reference (plotted left of the ladder at x=-1)
        r_rate = sub.loc[RACE, "rate"] * 100
        r_lo = sub.loc[RACE, "ci_low"] * 100
        r_hi = sub.loc[RACE, "ci_high"] * 100
        ax.errorbar(-1, r_rate, yerr=[[r_rate - r_lo], [r_hi - r_rate]], fmt="D",
                    ms=6, color="0.35", ecolor="0.35", capsize=3, zorder=3)
        ax.axvline(-0.5, color="0.6", ls=":", lw=1.0, zorder=1)

        # Cochran-Armitage trend test on the SES ladder
        z, p = cochran_armitage([sub.loc[s, "k"] for s in LADDER],
                                [sub.loc[s, "n"] for s in LADDER], xs)
        ptxt = "p<0.001" if p < 1e-3 else f"p={p:.3f}"
        ax.set_title(ML[m], color=MC[m], fontweight="bold", fontsize=11)
        ax.text(0.03, 0.95, f"trend z={z:.1f}, {ptxt}", transform=ax.transAxes,
                va="top", ha="left", fontsize=8.5, color="0.25")

    for ax in axes.flat:
        ax.set_xticks([-1] + list(xs))
        ax.set_xticklabels(["race-\nonly"] + LADDER_NICE, fontsize=8)
        ax.set_ylim(0, 100)
        ax.grid(axis="y", alpha=0.25)
    for ax in axes[:, 0]:
        ax.set_ylabel("Stigmatizing-language rate (%)")
    for ax in axes[1, :]:
        ax.set_xlabel("Socioeconomic disadvantage (ordinal rank; spacing arbitrary)", fontsize=8.5)

    fig.suptitle("Stigmatizing language rises with socioeconomic disadvantage in five of six models "
                 "(GPT-4o-mini near-null);\nrace-only (grey diamond) stays at the control floor "
                 "(95% Wilson CI; Cochran-Armitage trend test)",
                 fontsize=12, fontweight="bold", y=1.01)
    fig.tight_layout()
    fig.savefig(OUT / "Fig7b_stigma_dose_response.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("wrote", OUT / "Fig7b_stigma_dose_response.png")


if __name__ == "__main__":
    main()
