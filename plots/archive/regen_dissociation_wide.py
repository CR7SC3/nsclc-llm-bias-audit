#!/usr/bin/env python3
"""DRAFT: regenerate the dissociation panel at the heatmap's wide aspect (~3.18:1)
so it fills a full-width band the same box as Figure 2's tier-shift heatmap,
without distorting the scatter. Non-destructive: writes a NEW draft panel
(p_dissociation_wide.png); the canonical panels/p_dissociation.png is untouched.

Reuses the exact data + plotting logic from plot_publishable_nsclc.fig4_dissociation,
with two changes: (1) figsize widened to match the heatmap aspect, (2) the internal
"(A)/(B)" sub-titles dropped to plain "Treatment selection"/"Response framing" so
they don't collide with the composite panel letter "C".
Run from repo root:  python plots/regen_dissociation_wide.py
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

from plot_publishable_nsclc import MODELS, MC, ML, LABELS, TIERS, SUF, BASE, _read

# heatmap aspect target (p_flip_heatmap.png is 3269x1027 -> 3.183)
FIG_W, FIG_H = 24.6, 6.8      # tuned so tight-bbox aspect ~= 3.18
PANELS = Path("figures/manuscript_combined/panels")
OUT_PANEL = PANELS / "p_dissociation_wide.png"


def main():
    variants, tier_spans = [], []
    for name, colour, vs in TIERS:
        s = len(variants); variants += vs; tier_spans.append((name, colour, s, len(variants)))
    n = len(variants); y = np.arange(n)[::-1]
    offs = np.linspace(-0.30, 0.30, len(MODELS))

    data = {}
    for m in MODELS:
        soft = _read(f"{BASE}{SUF[m]}_soft_intensity.csv", {"d": "cohens_d", "q": "q_value_bh"})
        flip = _read(f"{BASE}{SUF[m]}_flip_rates.csv", {"rate": "flip_rate", "lo": "ci_low", "hi": "ci_high"})
        flip.setdefault("no_demographics", {"rate": 0.0, "lo": 0.0, "hi": 0.0})
        soft.setdefault("no_demographics", {"d": 0.0, "q": float("nan")})
        data[m] = {"soft": soft, "flip": flip}

    fig, (axA, axB) = plt.subplots(1, 2, figsize=(FIG_W, FIG_H), sharey=True,
                                    gridspec_kw={"wspace": 0.06})
    demo_vars = [v for v in variants if v != "no_demographics"]
    for m, off in zip(MODELS, offs):
        colour = MC[m]; fl = data[m]["flip"]
        meanflip = np.nanmean([fl.get(v, {}).get("rate", np.nan) * 100 for v in demo_vars])
        axA.axvline(meanflip, color=colour, ls="--", lw=0.9, alpha=0.4, zorder=1)
        xs = [fl.get(v, {}).get("rate", np.nan) * 100 for v in variants]
        los = [fl.get(v, {}).get("lo", np.nan) * 100 for v in variants]
        his = [fl.get(v, {}).get("hi", np.nan) * 100 for v in variants]
        axA.hlines(y + off, los, his, color=colour, linewidth=0.9, alpha=0.55, zorder=2)
        axA.scatter(xs, y + off, s=18, color=colour, zorder=3, edgecolor="white", linewidth=0.3)
    axA.set_xlim(0, 27)
    axA.set_xlabel("Treatment-recommendation flip rate (%)", fontsize=9.5)
    axA.set_title("Treatment selection", fontsize=10.5, fontweight="bold", pad=8)
    axA.xaxis.grid(True, ls="--", alpha=0.35, zorder=0)

    axB.axvline(0, color="#444444", linewidth=0.9, zorder=4)
    for m, off in zip(MODELS, offs):
        colour = MC[m]; sd = data[m]["soft"]
        xs = [sd.get(v, {}).get("d", np.nan) for v in variants]
        sig = [sd.get(v, {}).get("q", np.nan) < 0.05 for v in variants]
        axB.scatter(xs, y + off, s=[26 if s else 16 for s in sig], color=colour,
                    zorder=3, edgecolor="white", linewidth=0.3)
    axB.set_xlim(-0.3, 2.05)
    axB.set_xlabel("Added soft-framing intensity (Cohen's $d$)", fontsize=9.5)
    axB.set_title("Response framing", fontsize=10.5, fontweight="bold", pad=8)
    axB.xaxis.grid(True, ls="--", alpha=0.35, zorder=0)

    axA.set_yticks(y); axA.set_yticklabels([LABELS[v] for v in variants], fontsize=9)
    tick_colour = {v: colour for name, colour, s, e in tier_spans for v in variants[s:e]}
    for tick, v in zip(axA.get_yticklabels(), variants):
        tick.set_color(tick_colour[v])
    for ax in (axA, axB):
        ax.set_ylim(-0.6, n - 0.4); ax.tick_params(axis="y", length=0)
        for name, colour, s, e in tier_spans:
            if s != 0:
                ax.axhline((y[s] + y[s - 1]) / 2, color="#dddddd", lw=0.8, zorder=1)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.set_axisbelow(True)
    for name, colour, s, e in tier_spans:
        mid = (y[s] + y[e - 1]) / 2
        axA.annotate(name, xy=(0, 0), xytext=(-0.16, mid), textcoords=("axes fraction", "data"),
                     rotation=90, ha="center", va="center", fontsize=8.0, fontweight="bold",
                     color=colour, annotation_clip=False)

    handles = [mlines.Line2D([], [], marker="o", linestyle="none", color=MC[m],
                             markersize=6.5, markeredgecolor="white", label=ML[m]) for m in MODELS]
    fig.legend(handles=handles, loc="lower center", ncol=6, frameon=False, fontsize=8.2,
               bbox_to_anchor=(0.5, -0.02))

    PANELS.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PANEL, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    from PIL import Image
    w, h = Image.open(OUT_PANEL).size
    print(f"wrote {OUT_PANEL}  {w}x{h}  aspect={w/h:.3f}  (heatmap target 3.183)")


if __name__ == "__main__":
    main()
