"""EquityGUIDE v3 — Intervention study figure.

Two-panel publication figure:
  Panel A: Financial framing rate by strategy × variant
  Panel B: NCCN concordance rate by strategy × variant

Usage
-----
    python plot_v3_intervention.py
    python plot_v3_intervention.py --format pdf
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ── Config ────────────────────────────────────────────────────────────────────

FIGURES_DIR = Path("figures")
FIGURES_DIR.mkdir(exist_ok=True)

CSV_PATH = Path("results/analysis/v3_strategy_comparison_synthetic_unstructured.csv")

STRATEGY_ORDER = ["baseline_v2", "fairness", "structured_extraction", "guideline_grounded"]
STRATEGY_LABELS = {
    "baseline_v2":           "Baseline\n(v2)",
    "fairness":              "Fairness\ndirective",
    "structured_extraction": "Structured\nextraction",
    "guideline_grounded":    "Guideline-\ngrounded",
}
STRATEGY_COLORS = {
    "baseline_v2":           "#666666",
    "fairness":              "#009E73",   # green — eliminates bias, no cost
    "structured_extraction": "#56B4E9",   # blue — eliminates bias, concordance cost
    "guideline_grounded":    "#D55E00",   # red-orange — amplifies bias
}

VARIANT_ORDER = [
    "white_male_private",
    "latina_female_uninsured",
    "uninsured_only",
    "low_income_patient",
    "white_male_uninsured",
]
VARIANT_LABELS = {
    "white_male_private":      "White male\nprivate ins.\n[reference]",
    "latina_female_uninsured": "Latina female\nuninsured",
    "uninsured_only":          "Uninsured\nonly",
    "low_income_patient":      "Low income\nonly",
    "white_male_uninsured":    "White male\nuninsured",
}


def load_data() -> dict[str, dict[str, dict]]:
    """Return {strategy: {variant: {cost_rate, sw_rate, concordance_rate, n}}}."""
    data: dict[str, dict] = {}
    with open(CSV_PATH, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            s = row["strategy"]
            v = row["variant"]
            data.setdefault(s, {})[v] = {
                "cost_rate":        float(row["cost_rate"]),
                "sw_rate":          float(row["sw_rate"]),
                "concordance_rate": float(row["concordance_rate"]),
                "n":                int(row["n"]),
            }
    return data


def make_figure(data: dict, fmt: str = "png") -> None:
    n_variants  = len(VARIANT_ORDER)
    n_strategies = len(STRATEGY_ORDER)
    x = np.arange(n_variants)
    width = 0.22
    offsets = np.linspace(-(n_strategies - 1) / 2, (n_strategies - 1) / 2, n_strategies) * width

    fig, (ax_cost, ax_conc) = plt.subplots(
        1, 2, figsize=(13, 5.5), sharey=False
    )
    fig.subplots_adjust(wspace=0.35)

    # ── Panel A: Financial framing rate ──────────────────────────────────────
    for i, strategy in enumerate(STRATEGY_ORDER):
        vals = [
            data.get(strategy, {}).get(v, {}).get("cost_rate", 0)
            for v in VARIANT_ORDER
        ]
        bars = ax_cost.bar(
            x + offsets[i], vals, width,
            label=STRATEGY_LABELS[strategy],
            color=STRATEGY_COLORS[strategy],
            alpha=0.88,
            edgecolor="white", linewidth=0.5,
            zorder=3,
        )
        # Annotate bars
        for bar, val in zip(bars, vals):
            if val > 2:
                ax_cost.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 1.5,
                    f"{val:.0f}%",
                    ha="center", va="bottom",
                    fontsize=7.5, color="#333333", fontweight="bold",
                )

    ax_cost.set_xticks(x)
    ax_cost.set_xticklabels([VARIANT_LABELS[v] for v in VARIANT_ORDER], fontsize=8.5)
    ax_cost.set_ylabel("Financial framing rate (%)", fontsize=10)
    ax_cost.set_ylim(0, 115)
    ax_cost.set_title(
        "(A)  Financial barrier framing by prompt strategy\n"
        "Fairness directive eliminates bias; guideline-grounded amplifies it",
        fontsize=10, fontweight="bold", pad=10,
    )
    ax_cost.axhline(0, color="black", linewidth=0.5)
    ax_cost.yaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
    ax_cost.set_axisbelow(True)
    ax_cost.spines[["top", "right"]].set_visible(False)

    # ── Panel B: NCCN Concordance ─────────────────────────────────────────────
    for i, strategy in enumerate(STRATEGY_ORDER):
        vals = [
            data.get(strategy, {}).get(v, {}).get("concordance_rate", 0)
            for v in VARIANT_ORDER
        ]
        bars = ax_conc.bar(
            x + offsets[i], vals, width,
            label=STRATEGY_LABELS[strategy],
            color=STRATEGY_COLORS[strategy],
            alpha=0.88,
            edgecolor="white", linewidth=0.5,
            zorder=3,
        )
        for bar, val in zip(bars, vals):
            ax_conc.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.8,
                f"{val:.0f}%",
                ha="center", va="bottom",
                fontsize=7, color="#333333",
            )

    ax_conc.set_xticks(x)
    ax_conc.set_xticklabels([VARIANT_LABELS[v] for v in VARIANT_ORDER], fontsize=8.5)
    ax_conc.set_ylabel("NCCN concordance rate (%)", fontsize=10)
    ax_conc.set_ylim(0, 100)
    ax_conc.set_title(
        "(B)  NCCN guideline concordance by prompt strategy\n"
        "Fairness directive maintains concordance — no clinical accuracy tradeoff",
        fontsize=10, fontweight="bold", pad=10,
    )
    ax_conc.axhline(0, color="black", linewidth=0.5)
    ax_conc.yaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
    ax_conc.set_axisbelow(True)
    ax_conc.spines[["top", "right"]].set_visible(False)

    # ── Shared legend ─────────────────────────────────────────────────────────
    handles = [
        mpatches.Patch(color=STRATEGY_COLORS[s], label=STRATEGY_LABELS[s].replace("\n", " "), alpha=0.88)
        for s in STRATEGY_ORDER
    ]
    fig.legend(
        handles=handles,
        loc="lower center",
        ncol=3,
        fontsize=9.5,
        frameon=False,
        bbox_to_anchor=(0.5, -0.05),
    )

    # ── Caption ───────────────────────────────────────────────────────────────
    fig.text(
        0.5, -0.10,
        "Gemini 2.5 Flash · synthetic unstructured NSCLC notes · n=151 cases (fairness), n=80 cases (guideline-grounded, partial), n=119 cases (baseline)\n"
        "Financial framing: % of cases where LLM adds unsolicited cost/financial barrier language absent from the clinical note.",
        ha="center", fontsize=7.5, color="#555555", style="italic",
    )

    out_path = FIGURES_DIR / f"fig_v3_intervention.{fmt}"
    fig.savefig(out_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", choices=["png", "pdf"], default="png")
    args = parser.parse_args()

    data = load_data()
    make_figure(data, fmt=args.format)
