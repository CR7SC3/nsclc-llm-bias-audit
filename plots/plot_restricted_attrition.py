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

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "results/analysis/v2_genie_bpc_nsclc_restricted_venn_counts.csv"
OUT = ROOT / "figures/manuscript"
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "axes.labelcolor": "#222222",
    "xtick.color": "#222222",
    "ytick.color": "#222222",
    "axes.spines.top": False,
    "axes.spines.right": False,
})

# House model color mapping (fixed across all Paper 1 figures) — reused here
# for the "selected/concordant" segment so each bar keeps its model identity.
NICE = {
    "gemini-2.5-flash": "Gemini-2.5-flash",
    "deepseek-chat": "DeepSeek-chat",
    "llama-3.3-70b": "Llama-3.3-70B",
    "llama-3.1-8b": "Llama-3.1-8B",
    "gpt-4o": "GPT-4o",
    "gpt-4o-mini": "GPT-4o-mini",
}
MC = {
    "gemini-2.5-flash": "#4C72B0", "deepseek-chat": "#C44E52",
    "llama-3.3-70b": "#55A868", "llama-3.1-8b": "#937860",
    "gpt-4o": "#8172B3", "gpt-4o-mini": "#CCB974",
}
# Canonical model order used throughout the paper's per-model figures.
ORDER = ["gemini-2.5-flash", "deepseek-chat", "llama-3.3-70b",
         "llama-3.1-8b", "gpt-4o", "gpt-4o-mini"]

C_EXCLUDED = "#B7C0C4"  # muted neutral grey (matches the house "excluded/neutral" grey)


def load():
    rows = {}
    with open(SRC, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            rows[r["model"]] = {
                "n_scoreable": int(r["n_scoreable"]),
                "n_ctrl_concordant": int(r["n_ctrl_concordant"]),
            }
    return rows


def main():
    data = load()
    models = [m for m in ORDER if m in data]

    n = len(models)
    y = list(range(n))[::-1]  # first model at top
    height = 0.62

    fig, ax = plt.subplots(figsize=(8.8, 6.0))

    for yi, m in zip(y, models):
        total = data[m]["n_scoreable"]
        sel = data[m]["n_ctrl_concordant"]
        exc = total - sel
        pct = 100.0 * sel / total

        # selected/concordant segment (model color)
        ax.barh(yi, sel, height=height, color=MC[m], edgecolor="white",
                linewidth=0.6, zorder=3, label="Concordant with guidelines "
                "(selected for hard-endpoint bias-gap)" if yi == y[0] else None)
        # excluded/non-concordant segment (muted grey, hatched)
        ax.barh(yi, exc, height=height, left=sel, color=C_EXCLUDED,
                edgecolor="white", linewidth=0.6, hatch="//", zorder=3,
                label="Not concordant (excluded)" if yi == y[0] else None)

        ax.text(sel / 2, yi, f"{sel:,} ({pct:.0f}%)", ha="center", va="center",
                fontsize=8.6, color="white", fontweight="bold", zorder=4)
        ax.text(total + 14, yi, f"n={total:,} total", ha="left", va="center",
                fontsize=7.6, color="#666666", zorder=4)

    ax.set_yticks(y)
    ax.set_yticklabels([NICE[m] for m in models], fontsize=9.5)
    ax.set_xlim(0, 1048 * 1.20)
    ax.set_xlabel("no_demographics control cases (n = 1,048 scoreable)", fontsize=9.5)
    ax.set_ylim(-0.7, n - 0.3)
    ax.xaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0)

    fig.suptitle(
        "Control-cohort restriction for the hard-endpoint bias-gap analysis",
        fontsize=12.5, fontweight="bold", x=0.5, y=0.985,
    )
    fig.text(
        0.5, 0.90,
        "Control = no_demographics reference (not white_male_private). Cases are restricted to those where\n"
        "the model's own no_demographics recommendation is already NCCN-guideline-concordant, before computing\n"
        "the HARD (downgrade) bias-gap; retention varies by model. The SOFT (stigma-framing) endpoint is\n"
        "unaffected and uses the full n=1,048 sample.",
        ha="center", va="top", fontsize=8.2, color="#555555",
    )

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", fontsize=8.4, frameon=False,
               ncol=1, bbox_to_anchor=(0.5, 0.005))

    fig.subplots_adjust(top=0.76, bottom=0.20, left=0.16, right=0.95)

    png = OUT / "FigS12_restricted_control_attrition.png"
    pdf = OUT / "FigS12_restricted_control_attrition.pdf"
    fig.savefig(png, dpi=200, bbox_inches="tight")
    fig.savefig(pdf, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {png}")
    print(f"Saved: {pdf}")


if __name__ == "__main__":
    main()
