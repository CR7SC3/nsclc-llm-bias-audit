"""Framing volcano — every model×variant framing contrast on one plane.

Single-outcome volcano (framing Cohen's d only — NOT co-plotted with concordance,
which would be an incommensurable axis): x = added soft-framing intensity (Cohen's
d vs no-demographics), y = -log10(q), for all 6 models x 29 demographic variants.
Points are coloured by variant CLASS (not model). The socioeconomic-disadvantage
contrasts march out to the upper right (large, significant); race-only and
control/privileged contrasts cluster at the null origin. That is the paper's
dissociation — "framing bias is socioeconomic, not racial" — in one panel.

q-values are the per-model BH-FDR values already in each *_soft_intensity.csv
(i.e. FDR corrected WITHIN each model, not pooled across models).

Proposed placement: main-text replacement for the Fig 5 forest (it shows the same
SES-vs-race effect-size story across all contrasts at once). Named *_ALT so it does
not overwrite Fig 5 until that swap is decided.

Output -> figures/manuscript/FigS08_framing_volcano.png
Run:  python3 plots/plot_framing_volcano.py
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

from plots.plot_publishable_nsclc import MODELS, ML, SUF, BASE

OUT = Path("figures/manuscript"); OUT.mkdir(parents=True, exist_ok=True)

# variant -> class. Colour + marker encode class (redundant for colourblind safety).
RACE = {"black_race_only", "hispanic_race_only", "asian_race_only",
        "native_american_race_only", "middle_eastern_race_only", "multiracial_race_only"}
SES = {"uninsured_only", "underinsured_only", "low_income_patient", "unhoused_patient",
       "medicaid_only", "black_female_medicaid", "white_female_medicaid",
       "latina_female_uninsured", "low_income_black", "black_unhoused"}
CONTROL = {"white_male_private", "high_income_patient"}


def vclass(v):
    if v in SES:
        return "ses"
    if v in RACE:
        return "race"
    if v in CONTROL:
        return "control"
    return "other"


CLASS_STYLE = {
    "ses":     ("#C1272D", "o", "Socioeconomic disadvantage"),
    "race":    ("#6A51A3", "^", "Race / ethnicity only"),
    "control": ("#666666", "s", "Control / privileged"),
    "other":   ("#9FB0C0", "x", "Other identity / context"),
}
# SES points worth labelling (the drivers) if they clear this |d|
LABEL_IF_D = 1.0
NICE = {"unhoused_patient": "unhoused", "low_income_patient": "low income",
        "underinsured_only": "underinsured", "uninsured_only": "uninsured",
        "black_unhoused": "Black+unhoused", "low_income_black": "low-income Black",
        "latina_female_uninsured": "Latina uninsured", "medicaid_only": "medicaid",
        "black_female_medicaid": "Black medicaid", "white_female_medicaid": "white medicaid"}


def read_model(suffix):
    p = Path(f"{BASE}{suffix}_soft_intensity.csv")
    rows = []
    if not p.exists():
        return rows
    with open(p, newline="") as fh:
        for r in csv.DictReader(fh):
            v = r["variant"]
            if v == "no_demographics":
                continue
            try:
                d = float(r["cohens_d"]); q = float(r["q_value_bh"])
            except (ValueError, TypeError):
                continue
            rows.append((v, d, q))
    return rows


def draw(ax, pts, sig_y, yceil):
    """Render the volcano into ax (no title — banner belongs in the caption).
    Points at/above the clip ceiling (q < 1e-6) are spread with vertical jitter in a
    band above a break line, so their density and x-distribution stay visible instead
    of collapsing into one uninformative horizontal smear."""
    rng = np.random.default_rng(17)
    band_lo, band_hi = yceil + 0.15, yceil + 1.5
    ax.axhline(sig_y, color="0.5", ls="--", lw=1.0, zorder=1)
    ax.axhline(yceil, color="0.6", ls="-", lw=1.0, zorder=1)   # break line
    ax.axvline(0, color="0.5", ls="-", lw=0.8, zorder=1)

    for c in ("other", "control", "race", "ses"):      # draw SES last (on top)
        if not pts[c]:
            continue
        xs, ys = zip(*pts[c])
        ys = np.array(ys, float)
        clipped = ys >= yceil
        yplot = ys.copy()
        yplot[clipped] = rng.uniform(band_lo, band_hi, size=int(clipped.sum()))
        colour, marker, _ = CLASS_STYLE[c]
        big = c in ("ses", "race")
        kw = dict(s=40 if big else 30, marker=marker, color=colour,
                  alpha=0.75 if big else 0.55, zorder=3)
        if marker != "x":
            kw.update(edgecolor="white", linewidth=0.4)
        else:
            kw.update(linewidths=1.6)
        ax.scatter(np.array(xs), yplot, **kw)

    ax.set_ylim(-0.3, band_hi + 0.4)
    ax.text(0.995, sig_y, " q=0.05", va="bottom", ha="right", fontsize=8, color="0.4",
            transform=ax.get_yaxis_transform())
    ax.text(0.995, band_hi, "q < 1e-6 (jittered for density;\nheight above break not meaningful)",
            va="top", ha="right", fontsize=7.5, color="0.5",
            transform=ax.get_yaxis_transform(),
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85))
    ax.set_xlabel("Added soft-framing intensity (Cohen's $d$)", fontsize=10)
    ax.set_ylabel("$-\\log_{10}$ q  (BH-FDR)", fontsize=10)
    ax.grid(True, ls=":", alpha=0.4, zorder=0)
    handles = [mlines.Line2D([], [], marker=CLASS_STYLE[c][1], linestyle="none",
                             color=CLASS_STYLE[c][0], markersize=7,
                             markeredgecolor="white" if CLASS_STYLE[c][1] != "x" else CLASS_STYLE[c][0],
                             label=CLASS_STYLE[c][2]) for c in ("ses", "race", "control", "other")]
    ax.legend(handles=handles, loc="center right", fontsize=8.5, framealpha=0.95)


def main():
    yceil = 6.0                       # clip -log10 q here; SES q's underflow to ~0
    sig_y = -np.log10(0.05)

    # collect per class for clean legend + overplot density
    pts = {c: [] for c in CLASS_STYLE}
    for m in MODELS:
        for v, d, q in read_model(SUF[m]):
            y = -np.log10(max(q, 1e-300))     # raw; draw() jitters the >=ceil band
            pts[vclass(v)].append((d, y))

    # standalone (banner title kept) -> figures/manuscript/
    fig, ax = plt.subplots(figsize=(9.2, 6.4))
    draw(ax, pts, sig_y, yceil)
    ax.set_title("Framing bias is socioeconomic, not racial: every model×variant contrast\n"
                 "(6 models × 29 variants); SES contrasts (red) fan right at high significance, "
                 "race-only and\ncontrols cluster at the null origin",
                 fontsize=11.5, fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUT / "FigS08_framing_volcano.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # titleless panel for the combined figure — WIDE/SHORT aspect (~2.46:1) so it fills
    # the full-width top row of Figure 3 at the same height as the B|C bottom row, with
    # no marker distortion (combine_figures.py stamps the letter; banner -> caption).
    PANELS = Path("figures/manuscript_combined/panels"); PANELS.mkdir(parents=True, exist_ok=True)
    figp, axp = plt.subplots(figsize=(12.4, 5.05))
    draw(axp, pts, sig_y, yceil)
    figp.tight_layout()
    figp.savefig(PANELS / "p_volcano.png", dpi=200, bbox_inches="tight")
    plt.close(figp)
    print("wrote", OUT / "FigS08_framing_volcano.png", "and", PANELS / "p_volcano.png")


if __name__ == "__main__":
    main()
