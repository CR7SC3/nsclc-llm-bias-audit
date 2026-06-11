"""EquityGUIDE v2 Structured — flat bias figure.

Two-panel publication figure:
  Panel A: Concordance rate lollipop — all 22 variants, colored by tier
  Panel B: Soft bias rates (cost, SW) — near-zero across all tiers

Usage
-----
    python plot_v2_structured.py
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

FIGURES_DIR = Path("figures")
FIGURES_DIR.mkdir(exist_ok=True)
CSV_PATH = Path("results/analysis/v2_synthetic_structured_bias_summary.csv")

TIER_COLORS = {
    "A": "#4477AA",   # blue  — intersectional (v1 replication)
    "B": "#EE6677",   # red   — race only
    "C": "#228833",   # green — SES only
    "D": "#CCBB44",   # yellow— insurance only
    "E": "#AA3377",   # purple— isolation
    "F": "#66CCEE",   # cyan  — gender/identity
}

TIER_LABELS = {
    "A": "Tier A — Intersectional (race + sex + insurance)",
    "B": "Tier B — Race only",
    "C": "Tier C — SES only",
    "D": "Tier D — Insurance only",
    "E": "Tier E — Isolation variants",
    "F": "Tier F — Gender / sexual identity",
}

VARIANT_DISPLAY = {
    "white_male_private":      "White male, private ins.",
    "black_male_medicaid":     "Black male, Medicaid",
    "black_female_medicaid":   "Black female, Medicaid",
    "latina_female_uninsured": "Latina female, uninsured",
    "asian_female_medicare":   "Asian female, Medicare",
    "no_demographics":         "No demographics (control)",
    "black_race_only":         "Black (race only)",
    "hispanic_race_only":      "Hispanic (race only)",
    "asian_race_only":         "Asian (race only)",
    "native_american_race_only": "Native American (race only)",
    "arab_race_only":          "Arab (race only)",
    "unhoused_patient":        "Unhoused patient",
    "high_income_patient":     "High income",
    "low_income_patient":      "Low income",
    "uninsured_only":          "Uninsured only",
    "medicaid_only":           "Medicaid only",
    "white_female_medicaid":   "White female, Medicaid",
    "black_female_private":    "Black female, private ins.",
    "white_male_uninsured":    "White male, uninsured",
    "non_binary_patient":      "Non-binary patient",
    "transgender_woman":       "Transgender woman",
    "gay_male_patient":        "Gay male patient",
}


def load() -> list[dict]:
    rows = []
    with open(CSV_PATH, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            rows.append({
                "tier":        r["tier"],
                "variant":     r["variant"],
                "concordance": float(r["concordance_rate"]),
                "cost":        float(r["cost_rate"]),
                "sw":          float(r["sw_rate"]),
                "label":       VARIANT_DISPLAY.get(r["variant"], r["variant"]),
            })
    return rows


def make_figure(rows: list[dict], fmt: str = "png") -> None:
    fig, (ax_conc, ax_soft) = plt.subplots(
        1, 2, figsize=(14, 7.5),
        gridspec_kw={"width_ratios": [2.2, 1]},
    )
    fig.subplots_adjust(wspace=0.05)

    y = np.arange(len(rows))
    ref_conc = next(r["concordance"] for r in rows if r["variant"] == "white_male_private")

    # ── Panel A: Concordance lollipop ─────────────────────────────────────────
    ax_conc.axvline(ref_conc, color="#999999", linewidth=1.2, linestyle="--", zorder=1,
                    label=f"Reference (white male, private) = {ref_conc:.1f}%")

    # shaded ±3pp band around reference
    ax_conc.axvspan(ref_conc - 3, ref_conc + 3, alpha=0.07, color="#999999", zorder=0)

    for i, row in enumerate(rows):
        color = TIER_COLORS[row["tier"]]
        # stem
        ax_conc.hlines(i, ref_conc, row["concordance"], color=color, linewidth=1.5, alpha=0.6, zorder=2)
        # dot
        ax_conc.scatter(row["concordance"], i, color=color, s=60, zorder=3,
                        edgecolors="white", linewidths=0.5)
        # value label
        offset = 0.25 if row["concordance"] >= ref_conc else -0.25
        ha = "left" if row["concordance"] >= ref_conc else "right"
        ax_conc.text(row["concordance"] + offset, i, f"{row['concordance']:.1f}%",
                     va="center", ha=ha, fontsize=7.5, color="#333333")

    ax_conc.set_yticks(y)
    ax_conc.set_yticklabels([r["label"] for r in rows], fontsize=8.5)
    ax_conc.set_xlim(85, 102)
    ax_conc.set_xlabel("NCCN guideline concordance rate (%)", fontsize=10)
    ax_conc.set_title(
        "(A)  Concordance across all 22 demographic variants — structured notes\n"
        "Max spread: 2.4 pp  |  No variant deviates from reference",
        fontsize=10, fontweight="bold", pad=10,
    )
    ax_conc.spines[["top", "right"]].set_visible(False)
    ax_conc.xaxis.grid(True, linestyle="--", alpha=0.35, zorder=0)
    ax_conc.set_axisbelow(True)
    ax_conc.invert_yaxis()

    # Tier separators and labels on left margin
    tier_changes = [0] + [i for i in range(1, len(rows)) if rows[i]["tier"] != rows[i-1]["tier"]] + [len(rows)]
    for start, end in zip(tier_changes[:-1], tier_changes[1:]):
        mid = (start + end - 1) / 2
        tier = rows[start]["tier"]
        ax_conc.text(85.3, mid, f"Tier {tier}", va="center", fontsize=7.5,
                     color=TIER_COLORS[tier], fontweight="bold", alpha=0.85)
        if start > 0:
            ax_conc.axhline(start - 0.5, color="#dddddd", linewidth=0.8, zorder=0)

    # ── Panel B: Soft bias (cost + SW) ───────────────────────────────────────
    bar_h = 0.35
    for i, row in enumerate(rows):
        color = TIER_COLORS[row["tier"]]
        ax_soft.barh(i + bar_h/2, row["cost"], bar_h, color=color, alpha=0.75,
                     label="Cost" if i == 0 else "", zorder=3)
        ax_soft.barh(i - bar_h/2, row["sw"],   bar_h, color=color, alpha=0.40,
                     label="Social work" if i == 0 else "", zorder=3, hatch="///")
        if row["cost"] > 0.5:
            ax_soft.text(row["cost"] + 0.1, i + bar_h/2, f"{row['cost']:.1f}%",
                         va="center", fontsize=6.5, color="#333333")
        if row["sw"] > 0.5:
            ax_soft.text(row["sw"] + 0.1, i - bar_h/2, f"{row['sw']:.1f}%",
                         va="center", fontsize=6.5, color="#333333")

    ax_soft.set_xlim(0, 12)
    ax_soft.set_xlabel("Rate (%)", fontsize=10)
    ax_soft.set_title(
        "(B)  Soft bias measures\n(cost framing, social work referral)",
        fontsize=10, fontweight="bold", pad=10,
    )
    ax_soft.set_yticks(y)
    ax_soft.set_yticklabels([], fontsize=0)
    ax_soft.spines[["top", "right"]].set_visible(False)
    ax_soft.xaxis.grid(True, linestyle="--", alpha=0.35, zorder=0)
    ax_soft.set_axisbelow(True)
    ax_soft.invert_yaxis()

    for start, _ in zip(tier_changes[:-1], tier_changes[1:]):
        if start > 0:
            ax_soft.axhline(start - 0.5, color="#dddddd", linewidth=0.8, zorder=0)

    # Soft bias legend
    solid = mpatches.Patch(color="#666666", alpha=0.75, label="Cost / financial framing")
    hatch = mpatches.Patch(color="#666666", alpha=0.40, hatch="///", label="Social work referral")
    ax_soft.legend(handles=[solid, hatch], fontsize=8, loc="lower right",
                   frameon=False, bbox_to_anchor=(1.0, 0.0))

    # ── Tier legend ───────────────────────────────────────────────────────────
    handles = [mpatches.Patch(color=TIER_COLORS[t], label=TIER_LABELS[t]) for t in "ABCDEF"]
    fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=8.5,
               frameon=False, bbox_to_anchor=(0.5, -0.04))

    out = FIGURES_DIR / f"fig_v2_structured_flat.{fmt}"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {out}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", choices=["png", "pdf"], default="png")
    args = parser.parse_args()
    make_figure(load(), fmt=args.format)
