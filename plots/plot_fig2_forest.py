"""EquityGUIDE, Figure 2 (manuscript): three-vendor SES-vs-race effect-size forest.

Horizontal forest / caterpillar plot of added soft-framing intensity (Cohen's d
with 95% CI), one row per demographic variant, three markers per row for the three
complete vendor arms (Gemini, DeepSeek, Llama-3.3-70B). Variants grouped into
socioeconomic-disadvantage / race-only / control tiers. The race-only CIs straddle
zero on every vendor; the SES CIs sit far right on every vendor, the dissociation
is adjudicated by the uncertainty intervals, not asserted.

Usage:  python plot_fig2_forest.py [--format png|pdf]
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np

OUT_DIR = Path("figures/manuscript")

MODELS = {  # label -> (soft_intensity suffix, colour)
    "Gemini":   ("", "#EE7733"),
    "DeepSeek": ("_deepseek-chat", "#0077BB"),
    "Llama-3.3-70B": ("_meta-llama-Llama-3.3-70B-Instruct-Turbo", "#009988"),
}

TIERS = [
    ("Socioeconomic disadvantage", "#C1272D", [
        "underinsured_only", "uninsured_only", "latina_female_uninsured",
        "low_income_patient", "black_unhoused", "unhoused_patient",
    ]),
    ("Race only", "#6A51A3", [
        "black_race_only", "hispanic_race_only", "asian_race_only",
    ]),
    ("Control", "#666666", [
        "no_demographics",
    ]),
]

LABELS = {
    "underinsured_only": "Underinsured", "uninsured_only": "Uninsured",
    "latina_female_uninsured": "Latina female, uninsured", "low_income_patient": "Low income",
    "black_unhoused": "Black + unhoused", "unhoused_patient": "Unhoused",
    "black_race_only": "Black", "hispanic_race_only": "Hispanic", "asian_race_only": "Asian",
    "white_male_private": "White male, private ins.", "no_demographics": "No demographics",
}
BASE = "results/analysis/v2_genie_bpc_nsclc"


def _read(suffix: str) -> dict:
    out: dict[str, dict] = {}
    p = Path(f"{BASE}{suffix}_soft_intensity.csv")
    if not p.exists():
        return out
    with open(p, newline="") as fh:
        for row in csv.DictReader(fh):
            def f(c):
                v = row.get(c, "")
                return float(v) if v not in ("", None) else float("nan")
            d, delta = f("cohens_d"), f("delta")
            lo_raw, hi_raw = f("ci_low"), f("ci_high")
            # CSV CIs bound the raw mean difference (delta); rescale onto the
            # Cohen's d axis (same SD) so the interval is centred on d.
            scale = (d / delta) if delta not in (0.0, float("nan")) else 0.0
            out[row["variant"]] = {"d": d, "lo": lo_raw * scale,
                                   "hi": hi_raw * scale, "q": f("q_value_bh")}
    out.setdefault("no_demographics", {"d": 0.0, "lo": 0.0, "hi": 0.0, "q": float("nan")})
    return out


def make(fmt: str = "png") -> None:
    data = {m: _read(suf) for m, (suf, _c) in MODELS.items()}

    variants, tier_spans = [], []
    for name, colour, vs in TIERS:
        start = len(variants)
        variants += vs
        tier_spans.append((name, colour, start, len(variants)))
    n = len(variants)
    y = np.arange(n)[::-1]
    offs = np.linspace(-0.24, 0.24, len(MODELS))

    fig, ax = plt.subplots(figsize=(8.6, 6.6))
    ax.axvline(0, color="#444444", linewidth=0.9, zorder=4)

    for (m, (_suf, colour)), off in zip(MODELS.items(), offs):
        sd = data[m]
        ds = [sd.get(v, {}).get("d", np.nan) for v in variants]
        los = [sd.get(v, {}).get("lo", np.nan) for v in variants]
        his = [sd.get(v, {}).get("hi", np.nan) for v in variants]
        ax.hlines(y + off, los, his, color=colour, linewidth=1.3, alpha=0.85, zorder=2)
        ax.scatter(ds, y + off, s=26, color=colour, zorder=3,
                   edgecolor="white", linewidth=0.5)

    ax.set_yticks(y)
    ax.set_yticklabels([LABELS[v] for v in variants], fontsize=9)
    tick_colour = {v: colour for name, colour, s, e in tier_spans for v in variants[s:e]}
    for tick, v in zip(ax.get_yticklabels(), variants):
        tick.set_color(tick_colour[v])

    for name, colour, s, e in tier_spans:
        if s != 0:
            ax.axhline((y[s] + y[s - 1]) / 2, color="#dddddd", lw=0.8, zorder=1)
        mid = (y[s] + y[e - 1]) / 2
        ax.annotate(name, xy=(0, 0), xytext=(-0.46, mid),
                    textcoords=("axes fraction", "data"),
                    rotation=90, ha="center", va="center",
                    fontsize=8.2, fontweight="bold", color=colour,
                    annotation_clip=False)

    ax.set_ylim(-0.6, n - 0.4)
    ax.set_xlim(-0.55, 2.05)
    ax.set_xlabel("Added soft-framing intensity  (Cohen's $d$ vs no-demographics, 95% CI)",
                  fontsize=9.5)
    ax.set_title(
        "Framing bias is socioeconomic, not racial, and generalizes across three vendors\n"
        "1,048 GENIE NSCLC cases · effect size with 95% CI per vendor",
        fontsize=11, fontweight="bold", pad=10,
    )
    ax.xaxis.grid(True, ls="--", alpha=0.4, zorder=0)
    ax.tick_params(axis="y", length=0)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.set_axisbelow(True)

    handles = [mlines.Line2D([], [], marker="o", linestyle="-",
                             color=c, markersize=7, markeredgecolor="white", label=m)
               for m, (_suf, c) in MODELS.items()]
    ax.legend(handles=handles, loc="lower right", frameon=False, fontsize=9)

    fig.text(0.5, -0.02,
             "Soft framing = added cost / financial-barrier / social-work / adherence language. "
             "Race-only CIs straddle 0 on all vendors; SES CIs sit far right on all vendors.",
             ha="center", fontsize=7.4, color="#555555", style="italic")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"fig_forest_ses_vs_race.{fmt}"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {out}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--format", choices=["png", "pdf", "svg"], default="png")
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
        "figure.facecolor": "white", "axes.facecolor": "white",
        "savefig.facecolor": "white",
    })
    make(ap.parse_args().format)


if __name__ == "__main__":
    main()
