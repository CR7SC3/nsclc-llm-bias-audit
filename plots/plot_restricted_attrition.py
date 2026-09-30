"""Methods schematic: per-model attrition of the no_demographics control cohort
when restricted to the guideline-concordant subset used for the HARD-endpoint
(downgrade) bias-gap analysis.

Context
-------
The bias-gap (relative) analysis for the hard/downgrade endpoint is only
well-defined among control cases where the model's own no_demographics
recommendation was already NCCN-guideline-concordant (otherwise "downgrade"
vs. what baseline is undefined). Control here means the no_demographics
reference arm — NOT white_male_private, which is a privileged variant, never
the project's reference (see no_demographics_reference convention). This
restriction differs by model, so a single pooled Venn diagram would hide how
much power differs across vendors. Instead this is a per-model stacked-bar
attrition panel: each bar is the full 1,048-case control cohort, split into
the guideline-concordant subset carried forward into the hard-endpoint
bias-gap vs. the excluded non-concordant remainder. The soft (stigma-framing)
endpoint is unaffected and uses the full 1,048-case sample regardless.

Reads results/analysis/v2_genie_bpc_nsclc_restricted_venn_counts.csv
Writes figures/manuscript/FigS12_restricted_control_attrition.{png,pdf}

Run:  ./venv/bin/python plots/plot_restricted_attrition.py
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.legend_handler import HandlerTuple
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "results/analysis/v2_genie_bpc_nsclc_restricted_venn_counts.csv"
OUT = ROOT / "figures/manuscript"
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 12,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "axes.labelcolor": "#222222",
    "xtick.color": "#222222",
    "ytick.color": "#222222",
    "axes.spines.top": False,
    "axes.spines.right": False,
})

NICE = {
    "gemini-2.5-flash": "Gemini-2.5-flash",
    "deepseek-chat": "DeepSeek-chat",
    "llama-3.3-70b": "Llama-3.3-70B",
    "llama-3.1-8b": "Llama-3.1-8B",
    "gpt-4o": "GPT-4o",
    "gpt-4o-mini": "GPT-4o-mini",
}
# Canonical model order used throughout the paper's per-model figures.
ORDER = ["gemini-2.5-flash", "deepseek-chat", "llama-3.3-70b",
         "llama-3.1-8b", "gpt-4o", "gpt-4o-mini"]

# House model colors (fixed across all Paper 1 figures) for the retained
# segment; otherwise styled to match eFigure 4 (plot_pmc_provenance.py): grey
# excluded fill, thin black outlines, regular-weight labels, no grid.
MC = {
    "gemini-2.5-flash": "#4C72B0", "deepseek-chat": "#C44E52",
    "llama-3.3-70b": "#55A868", "llama-3.1-8b": "#937860",
    "gpt-4o": "#8172B3", "gpt-4o-mini": "#CCB974",
}
C_EXCLUDED = "#adadad"
EDGE = dict(edgecolor="k", linewidth=0.5)


def load():
    rows = {}
    with open(SRC, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            rows[r["model"]] = {
                "n_scoreable": int(r["n_scoreable"]),
                "n_ctrl_concordant": int(r["n_ctrl_concordant"]),
            }
    return rows


def text_color(hex_color):
    """Black on light fills, white on dark ones (relative luminance)."""
    r, g, b = (int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return "k" if 0.2126 * r + 0.7152 * g + 0.0722 * b > 0.65 else "white"


def main():
    data = load()
    models = [m for m in ORDER if m in data]

    n = len(models)
    y = list(range(n))[::-1]  # first model at top
    height = 0.62

    fig, ax = plt.subplots(figsize=(8.0, 4.6))

    for yi, m in zip(y, models):
        total = data[m]["n_scoreable"]
        sel = data[m]["n_ctrl_concordant"]
        exc = total - sel
        pct = 100.0 * sel / total

        ax.barh(yi, sel, height=height, color=MC[m], **EDGE, zorder=3)
        ax.barh(yi, exc, height=height, left=sel, color=C_EXCLUDED, **EDGE, zorder=3)

        ax.text(sel / 2, yi, f"{sel:,} ({pct:.0f}%)", ha="center", va="center",
                fontsize=11, color=text_color(MC[m]), zorder=4)

    ax.set_yticks(y)
    ax.set_yticklabels([NICE[m] for m in models], fontsize=11.5)
    ax.set_xlim(0, 1100); ax.tick_params(axis="x", labelsize=11)
    ax.set_xlabel("No-demographics reference responses (n = 1,048)", fontsize=12)
    ax.set_ylim(-0.7, n - 0.3)
    ax.tick_params(axis="y", length=0)

    # retained entry shows all 6 model colors side by side
    retained = tuple(Patch(facecolor=MC[m], **EDGE) for m in models)
    excluded = Patch(facecolor=C_EXCLUDED, **EDGE)
    fig.legend([retained, excluded],
               ["Guideline-concordant reference (retained)", "Not concordant (excluded)"],
               handler_map={tuple: HandlerTuple(ndivide=None, pad=0)},
               loc="lower center", fontsize=11, frameon=False, ncol=2,
               bbox_to_anchor=(0.55, -0.02), handlelength=4)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    fig.subplots_adjust(top=0.97, bottom=0.22, left=0.19, right=0.97)

    png = OUT / "FigS12_restricted_control_attrition.png"
    pdf = OUT / "FigS12_restricted_control_attrition.pdf"
    fig.savefig(png, dpi=200, bbox_inches="tight")
    fig.savefig(pdf, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {png}")
    print(f"Saved: {pdf}")


if __name__ == "__main__":
    main()
