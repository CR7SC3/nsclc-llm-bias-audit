"""EquityGUIDE — Real-note (PubMed/PMC) replication figure.

Single-panel grouped horizontal bars: added soft-framing intensity (Cohen's d
vs the no-demographics reference) per demographic variant, for the two vendors
run on the 40 real open-access PMC NSCLC case-report notes. Variants are grouped
into tiers (socioeconomic disadvantage / race-only / control) to show that the
framing bias tracks SES, not race, and that it survives on real human-written
prose — rebutting the synthetic-note artifact objection.

Usage
-----
    python plot_pmc_realnote.py
    python plot_pmc_realnote.py --format pdf
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ─── Config ──────────────────────────────────────────────────────────────────

FIGURES_DIR = Path("figures")

CSV_PATHS = {
    "DeepSeek": Path("results/analysis/v2_pmc_nsclc_deepseek-chat_soft_intensity.csv"),
    "Gemini":   Path("results/analysis/v2_pmc_nsclc_soft_intensity.csv"),
}

MODEL_COLORS = {
    "DeepSeek": "#0077BB",   # Paul Tol blue
    "Gemini":   "#EE7733",   # Paul Tol orange (house Gemini colour)
}

# Tiered variant set — the story-carrying contrast, top (disadvantaged) to
# bottom (control). Ordered within tier by descending pooled effect.
TIERS = [
    ("Socioeconomic\ndisadvantage", [
        "underinsured_only",
        "uninsured_only",
        "latina_female_uninsured",
        "low_income_patient",
        "black_unhoused",
        "unhoused_patient",
    ]),
    ("Race only", [
        "black_race_only",
        "hispanic_race_only",
        "asian_race_only",
    ]),
    ("Control", [
        "no_demographics",
    ]),
]

VARIANT_LABELS = {
    "underinsured_only":       "Underinsured",
    "uninsured_only":          "Uninsured",
    "latina_female_uninsured": "Latina female, uninsured",
    "low_income_patient":      "Low income",
    "black_unhoused":          "Black + unhoused",
    "unhoused_patient":        "Unhoused",
    "black_race_only":         "Black",
    "hispanic_race_only":      "Hispanic",
    "asian_race_only":         "Asian",
    "no_demographics":         "No demographics",
}

SIG_Q = 0.05


def load_intensity(path: Path) -> dict[str, dict]:
    """Return {variant: {d, q}} from a soft_intensity CSV."""
    out: dict[str, dict] = {}
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            try:
                d = float(row["cohens_d"])
            except (ValueError, KeyError):
                continue
            q = row.get("q_value_bh", "")
            out[row["variant"]] = {
                "d": d,
                "q": float(q) if q not in ("", None) else float("nan"),
            }
    return out


def make_figure(fmt: str = "png") -> None:
    data = {m: load_intensity(p) for m, p in CSV_PATHS.items()}
    models = list(CSV_PATHS.keys())

    # Flat ordered list of variants + tier boundary bookkeeping (top-to-bottom).
    variants: list[str] = []
    tier_spans: list[tuple[str, int, int]] = []
    for tier_name, vs in TIERS:
        start = len(variants)
        variants.extend(vs)
        tier_spans.append((tier_name, start, len(variants)))

    n = len(variants)
    # y positions: row 0 at TOP -> invert so first variant sits highest.
    y = np.arange(n)[::-1]
    height = 0.38
    offs = {models[0]: +height / 2, models[1]: -height / 2}

    fig, ax = plt.subplots(figsize=(8.2, 6.4))

    for m in models:
        ds = [data[m].get(v, {}).get("d", 0.0) for v in variants]
        qs = [data[m].get(v, {}).get("q", float("nan")) for v in variants]
        bars = ax.barh(
            y + offs[m], ds, height,
            color=MODEL_COLORS[m], alpha=0.9,
            edgecolor="white", linewidth=0.6, zorder=3, label=m,
        )
        for bar, d, q in zip(bars, ds, qs):
            sig = (q < SIG_Q)
            txt = f"{d:+.2f}" + ("*" if sig else "")
            ax.text(
                bar.get_width() + (0.03 if d >= 0 else -0.03),
                bar.get_y() + bar.get_height() / 2,
                txt, ha="left" if d >= 0 else "right", va="center",
                fontsize=7.5, color="#333333",
                fontweight="bold" if sig else "normal",
            )

    # Zero reference
    ax.axvline(0, color="#444444", linewidth=0.9, zorder=4)

    # Y ticks / labels
    ax.set_yticks(y)
    ax.set_yticklabels([VARIANT_LABELS[v] for v in variants], fontsize=9)

    # Tier separators + left-margin tier brackets
    for tier_name, start, end in tier_spans:
        if start != 0:  # separator line above each tier after the first
            sep = (y[start] + y[start - 1]) / 2
            ax.axhline(sep, color="#d0d0d0", linewidth=0.8, zorder=1)
        mid = (y[start] + y[end - 1]) / 2
        ax.annotate(
            tier_name, xy=(0, 0), xytext=(-0.62, mid),
            textcoords=("axes fraction", "data"),
            fontsize=8.5, fontweight="bold", color="#555555",
            ha="left", va="center", annotation_clip=False,
        )

    xmax = max(
        data[m].get(v, {}).get("d", 0.0)
        for m in models for v in variants
    )
    ax.set_xlim(-0.35, xmax * 1.18 + 0.15)
    ax.set_xlabel(
        "Added soft-framing intensity  (Cohen's $d$ vs no-demographics reference)",
        fontsize=9.5,
    )
    ax.set_title(
        "Socioeconomic — not racial — framing bias replicates on real notes\n"
        "40 open-access PubMed NSCLC case reports · DeepSeek + Gemini",
        fontsize=11, fontweight="bold", pad=10,
    )
    ax.xaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)

    handles = [mpatches.Patch(color=MODEL_COLORS[m], label=m, alpha=0.9) for m in models]
    ax.legend(
        handles=handles, loc="lower right", fontsize=9, frameon=False,
        title="* $q_{BH}<0.05$", title_fontsize=8,
    )

    fig.text(
        0.5, -0.02,
        "Each variant: same real note, one prepended demographic label vs no label. "
        "Soft framing = added cost / financial-barrier / social-work / adherence language.\n"
        "Effect sizes attenuate vs synthetic notes (information-density effect) but the "
        "SES-vs-race dissociation and control ≈ 0 hold across both vendors.",
        ha="center", fontsize=7.5, color="#555555", style="italic",
    )

    FIGURES_DIR.mkdir(exist_ok=True)
    out = FIGURES_DIR / f"fig_pmc_realnote.{fmt}"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {out}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", choices=["png", "pdf", "svg"], default="png")
    args = parser.parse_args()

    plt.rcParams.update({
        "font.family":       "sans-serif",
        "font.sans-serif":   ["Helvetica", "Arial", "DejaVu Sans"],
        "figure.facecolor":  "white",
        "axes.facecolor":    "white",
        "savefig.facecolor": "white",
        "axes.labelcolor":   "#222222",
        "xtick.color":       "#222222",
        "ytick.color":       "#222222",
    })
    make_figure(fmt=args.format)


if __name__ == "__main__":
    main()
