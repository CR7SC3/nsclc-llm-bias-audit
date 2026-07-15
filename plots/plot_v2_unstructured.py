"""EquityGUIDE v2 Unstructured — two new figures for unplotted CSVs.

Figure 1: fig_v2_flip_rates.png
    Two-panel lollipop — v2 flip rates for structured (left) and
    unstructured (right) across all 22 variants, tier-colored with 95% CIs.
    Illustrates that flip rates are flat in structured notes but high and
    somewhat dispersed in unstructured notes.

Figure 2: fig_v2_unstructured_bias.png
    Direct parallel to fig_v2_structured_flat.png but for unstructured notes.
    Panel A: concordance lollipop — all 22 variants.
    Panel B: soft bias (cost + SW) — x-axis spans 0–90% to capture the
    dramatic SES signal (uninsured: 64% cost, 36% SW).

Usage
-----
    python plot_v2_unstructured.py
    python plot_v2_unstructured.py --format pdf
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

FIGURES_DIR = Path("figures")
FIGURES_DIR.mkdir(exist_ok=True)

STRUCT_FLIP_CSV   = Path("results/analysis/v2_synthetic_structured_flip_rates.csv")
UNSTRUCT_FLIP_CSV = Path("results/analysis/v2_synthetic_unstructured_flip_rates.csv")
UNSTRUCT_BIAS_CSV = Path("results/analysis/v2_synthetic_unstructured_bias_summary.csv")

TIER_COLORS = {
    "A": "#4477AA",
    "B": "#EE6677",
    "C": "#228833",
    "D": "#CCBB44",
    "E": "#AA3377",
    "F": "#66CCEE",
}

TIER_LABELS = {
    "A": "Tier A — Intersectional (race + sex + insurance)",
    "B": "Tier B — Race only",
    "C": "Tier C — SES only",
    "D": "Tier D — Insurance only",
    "E": "Tier E — Isolation variants",
    "F": "Tier F — Gender / sexual identity",
}

# Tier assigned to each variant (flip rate CSVs lack a tier column)
VARIANT_TIER = {
    "white_male_private":        "A",
    "black_male_medicaid":       "A",
    "black_female_medicaid":     "A",
    "latina_female_uninsured":   "A",
    "asian_female_medicare":     "A",
    "no_demographics":           "A",
    "black_race_only":           "B",
    "hispanic_race_only":        "B",
    "asian_race_only":           "B",
    "native_american_race_only": "B",
    "arab_race_only":            "B",
    "unhoused_patient":          "C",
    "high_income_patient":       "C",
    "low_income_patient":        "C",
    "uninsured_only":            "D",
    "medicaid_only":             "D",
    "white_female_medicaid":     "E",
    "black_female_private":      "E",
    "white_male_uninsured":      "E",
    "non_binary_patient":        "F",
    "transgender_woman":         "F",
    "gay_male_patient":          "F",
}

VARIANT_DISPLAY = {
    "white_male_private":        "White male, private ins.",
    "black_male_medicaid":       "Black male, Medicaid",
    "black_female_medicaid":     "Black female, Medicaid",
    "latina_female_uninsured":   "Latina female, uninsured",
    "asian_female_medicare":     "Asian female, Medicare",
    "no_demographics":           "No demographics (control)",
    "black_race_only":           "Black (race only)",
    "hispanic_race_only":        "Hispanic (race only)",
    "asian_race_only":           "Asian (race only)",
    "native_american_race_only": "Native American (race only)",
    "arab_race_only":            "Arab (race only)",
    "unhoused_patient":          "Unhoused patient",
    "high_income_patient":       "High income",
    "low_income_patient":        "Low income",
    "uninsured_only":            "Uninsured only",
    "medicaid_only":             "Medicaid only",
    "white_female_medicaid":     "White female, Medicaid",
    "black_female_private":      "Black female, private ins.",
    "white_male_uninsured":      "White male, uninsured",
    "non_binary_patient":        "Non-binary patient",
    "transgender_woman":         "Transgender woman",
    "gay_male_patient":          "Gay male patient",
}


# ── Data loading ──────────────────────────────────────────────────────────────

def load_flip(path: Path) -> list[dict]:
    rows = []
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            v = r["variant"]
            rows.append({
                "variant":  v,
                "tier":     VARIANT_TIER.get(v, "A"),
                "label":    VARIANT_DISPLAY.get(v, v),
                "rate":     float(r["flip_rate"]),
                "ci_low":   float(r["ci_low"]),
                "ci_high":  float(r["ci_high"]),
            })
    return rows


def load_bias(path: Path) -> list[dict]:
    rows = []
    with open(path, newline="", encoding="utf-8") as fh:
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


# ── Figure helpers ────────────────────────────────────────────────────────────

def _tier_separators(ax, rows: list[dict], key: str = "tier") -> list[int]:
    changes = [0] + [i for i in range(1, len(rows)) if rows[i][key] != rows[i-1][key]] + [len(rows)]
    for start, end in zip(changes[:-1], changes[1:]):
        if start > 0:
            ax.axhline(start - 0.5, color="#dddddd", linewidth=0.8, zorder=0)
        mid = (start + end - 1) / 2
        tier = rows[start][key]
        ax.text(ax.get_xlim()[0], mid, f" {tier}", va="center", fontsize=7,
                color=TIER_COLORS[tier], fontweight="bold", alpha=0.85)
    return changes


# ── Figure 1: Flip rates side-by-side ────────────────────────────────────────

def fig_v2_flip_rates(fmt: str = "png") -> None:
    struct_rows   = load_flip(STRUCT_FLIP_CSV)
    unstruct_rows = load_flip(UNSTRUCT_FLIP_CSV)

    fig, (ax_s, ax_u) = plt.subplots(1, 2, figsize=(15, 8), sharey=True)
    fig.subplots_adjust(wspace=0.06)

    ref_var = "white_male_private"

    for ax, rows, title, xlim in [
        (ax_s, struct_rows,   "Structured notes", (0.0, 0.28)),
        (ax_u, unstruct_rows, "Unstructured notes", (0.25, 0.72)),
    ]:
        ref_rate = next(r["rate"] for r in rows if r["variant"] == ref_var)
        y = np.arange(len(rows))

        ax.axvline(ref_rate, color="#999999", linewidth=1.2, linestyle="--", zorder=1,
                   label=f"White male, private = {ref_rate*100:.1f}%")
        ax.axvspan(ref_rate - 0.02, ref_rate + 0.02, alpha=0.07, color="#999999", zorder=0)

        for i, row in enumerate(rows):
            color = TIER_COLORS[row["tier"]]
            err_lo = row["rate"] - row["ci_low"]
            err_hi = row["ci_high"] - row["rate"]
            ax.hlines(i, ref_rate, row["rate"], color=color, linewidth=1.4, alpha=0.55, zorder=2)
            ax.errorbar(row["rate"], i, xerr=[[err_lo], [err_hi]],
                        fmt="o", color=color, markersize=5,
                        capsize=2.5, elinewidth=1, zorder=3,
                        markeredgecolor="white", markeredgewidth=0.4)
            offset = 0.006 if row["rate"] >= ref_rate else -0.006
            ha = "left" if row["rate"] >= ref_rate else "right"
            ax.text(row["rate"] + offset, i, f"{row['rate']*100:.1f}%",
                    va="center", ha=ha, fontsize=7, color="#333333")

        ax.set_xlim(xlim)
        ax.set_xlabel("Flip rate (fraction of cases)", fontsize=10)
        ax.set_title(f"({('A' if ax is ax_s else 'B')})  {title}", fontsize=11,
                     fontweight="bold", pad=10)
        ax.spines[["top", "right"]].set_visible(False)
        ax.xaxis.grid(True, linestyle="--", alpha=0.35, zorder=0)
        ax.set_axisbelow(True)
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x*100:.0f}%"))
        ax.invert_yaxis()
        ax.set_ylim(len(rows) - 0.5, -0.5)

        # tier labels — place in left margin
        changes = [0] + [i for i in range(1, len(rows)) if rows[i]["tier"] != rows[i-1]["tier"]] + [len(rows)]
        for start, end in zip(changes[:-1], changes[1:]):
            if start > 0:
                ax.axhline(start - 0.5, color="#dddddd", linewidth=0.8, zorder=0)
            mid = (start + end - 1) / 2
            tier = rows[start]["tier"]
            ax.text(xlim[0] + 0.002, mid, f"  {tier}", va="center", fontsize=7,
                    color=TIER_COLORS[tier], fontweight="bold", alpha=0.85)

    # y-tick labels on left panel only
    ax_s.set_yticks(np.arange(len(struct_rows)))
    ax_s.set_yticklabels([r["label"] for r in struct_rows], fontsize=8.5)

    # Tier legend
    handles = [mpatches.Patch(color=TIER_COLORS[t], label=TIER_LABELS[t]) for t in "ABCDEF"]
    fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=8.5,
               frameon=False, bbox_to_anchor=(0.5, -0.04))

    fig.suptitle(
        "v2 Flip rates across 22 demographic variants\n"
        "Left: structured notes (flat, ~10–14%)  |  Right: unstructured notes (high, ~43–57%)",
        fontsize=12, fontweight="bold", y=1.01,
    )

    out = FIGURES_DIR / f"fig_v2_flip_rates.{fmt}"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {out}")


# ── Figure 2: Unstructured bias summary ──────────────────────────────────────

def fig_v2_unstructured_bias(fmt: str = "png") -> None:
    rows = load_bias(UNSTRUCT_BIAS_CSV)

    fig, (ax_conc, ax_soft) = plt.subplots(
        1, 2, figsize=(15, 8),
        gridspec_kw={"width_ratios": [2.0, 1.4]},
    )
    fig.subplots_adjust(wspace=0.05)

    y = np.arange(len(rows))
    ref_conc = next(r["concordance"] for r in rows if r["variant"] == "white_male_private")

    # ── Panel A: Concordance lollipop ─────────────────────────────────────────
    x_min_conc = 70.0
    ax_conc.axvline(ref_conc, color="#999999", linewidth=1.2, linestyle="--", zorder=1,
                    label=f"Reference (white male, private) = {ref_conc:.1f}%")
    ax_conc.axvspan(ref_conc - 3, ref_conc + 3, alpha=0.07, color="#999999", zorder=0)

    for i, row in enumerate(rows):
        color = TIER_COLORS[row["tier"]]
        ax_conc.hlines(i, ref_conc, row["concordance"], color=color,
                       linewidth=1.5, alpha=0.6, zorder=2)
        ax_conc.scatter(row["concordance"], i, color=color, s=55, zorder=3,
                        edgecolors="white", linewidths=0.5)
        offset = 0.25 if row["concordance"] >= ref_conc else -0.25
        ha = "left" if row["concordance"] >= ref_conc else "right"
        ax_conc.text(row["concordance"] + offset, i, f"{row['concordance']:.1f}%",
                     va="center", ha=ha, fontsize=7.5, color="#333333")

    ax_conc.set_xlim(x_min_conc, 90)
    ax_conc.set_xlabel("NCCN guideline concordance rate (%)", fontsize=10)
    ax_conc.set_title(
        "(A)  Concordance across all 22 demographic variants — unstructured notes\n"
        "Concordance depressed overall (hard format); no strong group pattern",
        fontsize=10, fontweight="bold", pad=10,
    )
    ax_conc.set_yticks(y)
    ax_conc.set_yticklabels([r["label"] for r in rows], fontsize=8.5)
    ax_conc.spines[["top", "right"]].set_visible(False)
    ax_conc.xaxis.grid(True, linestyle="--", alpha=0.35, zorder=0)
    ax_conc.set_axisbelow(True)
    ax_conc.invert_yaxis()

    changes = [0] + [i for i in range(1, len(rows)) if rows[i]["tier"] != rows[i-1]["tier"]] + [len(rows)]
    for start, end in zip(changes[:-1], changes[1:]):
        mid = (start + end - 1) / 2
        tier = rows[start]["tier"]
        ax_conc.text(x_min_conc + 0.15, mid, f"Tier {tier}", va="center", fontsize=7.5,
                     color=TIER_COLORS[tier], fontweight="bold", alpha=0.85)
        if start > 0:
            ax_conc.axhline(start - 0.5, color="#dddddd", linewidth=0.8, zorder=0)

    # ── Panel B: Soft bias bars ───────────────────────────────────────────────
    bar_h = 0.35
    for i, row in enumerate(rows):
        color = TIER_COLORS[row["tier"]]
        ax_soft.barh(i + bar_h/2, row["cost"], bar_h, color=color, alpha=0.80,
                     zorder=3)
        ax_soft.barh(i - bar_h/2, row["sw"],   bar_h, color=color, alpha=0.40,
                     zorder=3, hatch="///")
        if row["cost"] >= 1.0:
            ax_soft.text(row["cost"] + 0.5, i + bar_h/2, f"{row['cost']:.1f}%",
                         va="center", fontsize=6.5, color="#333333")
        if row["sw"] >= 1.0:
            ax_soft.text(row["sw"] + 0.5, i - bar_h/2, f"{row['sw']:.1f}%",
                         va="center", fontsize=6.5, color="#333333")

    # Annotation for dramatic SES finding
    uninsured_idx = next(i for i, r in enumerate(rows) if r["variant"] == "uninsured_only")
    ax_soft.annotate(
        "SES / insurance\ndrives soft bias,\nnot race",
        xy=(65, uninsured_idx), xytext=(70, uninsured_idx - 3.5),
        fontsize=7.5, color="#AA3377",
        arrowprops=dict(arrowstyle="->", color="#AA3377", lw=1.0),
        ha="left",
    )

    ax_soft.set_xlim(0, 92)
    ax_soft.set_xlabel("Rate (%)", fontsize=10)
    ax_soft.set_title(
        "(B)  Soft bias — unstructured notes\n(cost framing, social work referral)",
        fontsize=10, fontweight="bold", pad=10,
    )
    ax_soft.set_yticks(y)
    ax_soft.set_yticklabels([], fontsize=0)
    ax_soft.spines[["top", "right"]].set_visible(False)
    ax_soft.xaxis.grid(True, linestyle="--", alpha=0.35, zorder=0)
    ax_soft.set_axisbelow(True)
    ax_soft.invert_yaxis()

    for start, _ in zip(changes[:-1], changes[1:]):
        if start > 0:
            ax_soft.axhline(start - 0.5, color="#dddddd", linewidth=0.8, zorder=0)

    solid = mpatches.Patch(color="#666666", alpha=0.80, label="Cost / financial framing")
    hatch = mpatches.Patch(color="#666666", alpha=0.40, hatch="///", label="Social work referral")
    ax_soft.legend(handles=[solid, hatch], fontsize=8, loc="lower right",
                   frameon=False, bbox_to_anchor=(1.0, 0.0))

    # Tier legend
    handles = [mpatches.Patch(color=TIER_COLORS[t], label=TIER_LABELS[t]) for t in "ABCDEF"]
    fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=8.5,
               frameon=False, bbox_to_anchor=(0.5, -0.04))

    out = FIGURES_DIR / f"fig_v2_unstructured_bias.{fmt}"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", choices=["png", "pdf", "svg"], default="png")
    args = parser.parse_args()

    fig_v2_flip_rates(fmt=args.format)
    fig_v2_unstructured_bias(fmt=args.format)
