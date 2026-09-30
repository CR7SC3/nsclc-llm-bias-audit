"""Framing volcano — every model×variant framing contrast on one plane.

Single-outcome volcano (framing Cohen's d only — NOT co-plotted with concordance,
which would be an incommensurable axis): x = added soft-framing intensity (Cohen's
d vs no-demographics), y = -log10(q), for all 6 models x 28 demographic variants.
Points are coloured by variant CLASS (not model). The socioeconomic-disadvantage
contrasts march out to the upper right (large, significant); race-only and
control/privileged contrasts cluster at the null origin. That is the paper's
dissociation — "framing bias is socioeconomic, not racial" — in one panel.

q-values are Benjamini-Hochberg FDR corrected ONCE across all 168 model x variant
cells (the family defined in the eMethods multiplicity summary), recomputed here from
the raw p-values in each *_soft_intensity.csv. The CSVs' own q_value_bh column is
per-model and was computed with the since-removed elderly_patient_75 label, so it is
not used. elderly_patient_75 is excluded from the plot.

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
    "control": ("#666666", "s", "Privileged comparators"),
    "other":   ("#9FB0C0", "x", "Other labels"),
}
# SES points worth labelling (the drivers) if they clear this |d|
LABEL_IF_D = 1.0
NICE = {"unhoused_patient": "unhoused", "low_income_patient": "low income",
        "underinsured_only": "underinsured", "uninsured_only": "uninsured",
        "black_unhoused": "Black+unhoused", "low_income_black": "low-income Black",
        "latina_female_uninsured": "Latina uninsured", "medicaid_only": "medicaid",
        "black_female_medicaid": "Black medicaid", "white_female_medicaid": "white medicaid"}


DROPPED = {"no_demographics", "elderly_patient_75"}


def read_model(suffix):
    """[(variant, cohens_d, raw p)] for one model, reference and dropped label excluded."""
    p = Path(f"{BASE}{suffix}_soft_intensity.csv")
    rows = []
    if not p.exists():
        return rows
    with open(p, newline="") as fh:
        for r in csv.DictReader(fh):
            v = r["variant"]
            if v in DROPPED:
                continue
            try:
                d = float(r["cohens_d"]); pv = float(r["p_value"])
            except (ValueError, TypeError):
                continue
            rows.append((v, d, pv))
    return rows


def bh(pvals):
    """Benjamini-Hochberg q-values for a list of p-values (one family)."""
    n = len(pvals)
    order = sorted(range(n), key=lambda i: pvals[i])
    q = [0.0] * n
    prev = 1.0
    for rank in range(n, 0, -1):
        i = order[rank - 1]
        prev = min(prev, pvals[i] * n / rank)
        q[i] = prev
    return q


def draw(ax, pts, sig_y, yceil):
    """Render the volcano into ax (no title — banner belongs in the caption).
    Points at/above the clip ceiling (q < 1e-6) are drawn in one shaded strip
    labelled ">=6" with vertical jitter only, so their density and x-distribution
    stay visible; height inside the strip carries no information."""
    rng = np.random.default_rng(17)
    # every cell with q below the ceiling is drawn in one strip; vertical position
    # inside the strip is jitter only (stated in the caption), not a q value
    strip_y = yceil + 0.7
    band_lo, band_hi = strip_y - 0.25, strip_y + 0.25
    ax.axhline(sig_y, color="0.5", ls="--", lw=1.0, zorder=1)
    ax.axhspan(band_lo - 0.12, band_hi + 0.12, color="0.94", zorder=0)
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

    ax.set_ylim(-0.3, band_hi + 0.3)
    ax.set_yticks([0, 1, 2, 3, 4, 5, strip_y])
    ax.set_yticklabels(["0", "1", "2", "3", "4", "5", f"$\\geq${yceil:.0f}"])
    ax.tick_params(labelsize=12)
    ax.text(0.995, sig_y, "$q$ = .05", va="bottom", ha="right", fontsize=11, color="0.4",
            transform=ax.get_yaxis_transform())
    ax.set_xlabel("Flagged-language effect (Cohen $d$)", fontsize=13)
    ax.set_ylabel("$-\\log_{10}\\,q$ (Benjamini-Hochberg)", fontsize=13)
    ax.grid(True, ls=":", alpha=0.4, zorder=0)
    handles = [mlines.Line2D([], [], marker=CLASS_STYLE[c][1], linestyle="none",
                             color=CLASS_STYLE[c][0], markersize=7,
                             markeredgecolor="white" if CLASS_STYLE[c][1] != "x" else CLASS_STYLE[c][0],
                             label=CLASS_STYLE[c][2]) for c in ("ses", "race", "control", "other")]
    ax.legend(handles=handles, loc="center right", fontsize=12, framealpha=0.95)


def main():
    yceil = 6.0                       # clip -log10 q here; SES q's underflow to ~0
    sig_y = -np.log10(0.05)

    # collect per class for clean legend + overplot density
    pts = {c: [] for c in CLASS_STYLE}
    cells = [(v, d, pv) for m in MODELS for v, d, pv in read_model(SUF[m])]
    assert len(cells) == 168, len(cells)
    qs = bh([pv for _, _, pv in cells])        # one BH family across the whole grid
    for (v, d, _), q in zip(cells, qs):
        y = -np.log10(max(q, 1e-300))         # raw; draw() jitters the >=ceil band
        pts[vclass(v)].append((d, y))
    print(f"{sum(q < 0.05 for q in qs)} of {len(qs)} cells q < .05 (BH across the grid)")
    print(f"{sum(q < 10 ** -yceil for q in qs)} cells with q < 1e-{yceil:.0f} drawn in the top strip")

    # standalone (banner title kept) -> figures/manuscript/
    fig, ax = plt.subplots(figsize=(9.2, 6.4))
    draw(ax, pts, sig_y, yceil)
    ax.set_title("Framing bias is socioeconomic, not racial: every model×variant contrast\n"
                 "(6 models × 28 variants); SES contrasts (red) fan right at high significance, "
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
