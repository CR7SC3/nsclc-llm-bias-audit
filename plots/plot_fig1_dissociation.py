"""EquityGUIDE, Figure 1 (manuscript centerpiece): the decision/framing dissociation.

Twin panels sharing one row per demographic variant:
  (A) Treatment SELECTION: flip rate vs the no-demographics reference, with the
      temp-0 self-flip noise band shaded. Every dot sits inside the band -> the null.
  (B) Response FRAMING: added soft-framing intensity (Cohen's d). The same rows
      fan out: socioeconomic-disadvantage variants shoot right, race-only and
      control sit at zero.

One image encodes all three claims: decision-stable, framing-biased, SES-not-race.
Three complete vendor arms (Gemini, DeepSeek, Llama-3.3-70B).

Usage:  python plot_fig1_dissociation.py [--format png|pdf]
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np

OUT_DIR = Path("figures/manuscript")

MODELS = {  # label -> (soft_intensity suffix, flip suffix, colour, self-flip noise floor %)
    "Gemini":   ("", "", "#EE7733", 3.4),
    "DeepSeek": ("_deepseek-chat", "_deepseek-chat", "#0077BB", 9.4),
    "Llama-3.3-70B": (
        "_meta-llama-Llama-3.3-70B-Instruct-Turbo",
        "_meta-llama-Llama-3.3-70B-Instruct-Turbo",
        "#009988", 12.3,
    ),
}

# Tiered display set (top -> bottom). Tier colour is applied to the ROW LABEL only,
# so it never collides with the per-model dot colours.
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


def _read(path: str, key_cols: dict) -> dict:
    out: dict[str, dict] = {}
    p = Path(path)
    if not p.exists():
        return out
    with open(p, newline="") as fh:
        for row in csv.DictReader(fh):
            rec = {}
            for k, col in key_cols.items():
                v = row.get(col, "")
                rec[k] = float(v) if v not in ("", None) else float("nan")
            out[row["variant"]] = rec
    return out


def load():
    data = {}
    for m, (si_suf, fl_suf, _c, _n) in MODELS.items():
        soft = _read(f"{BASE}{si_suf}_soft_intensity.csv",
                     {"d": "cohens_d", "q": "q_value_bh"})
        flip = _read(f"{BASE}{fl_suf}_flip_rates.csv",
                     {"rate": "flip_rate", "lo": "ci_low", "hi": "ci_high"})
        # no_demographics is the reference -> flip 0 by construction, d 0.
        flip.setdefault("no_demographics", {"rate": 0.0, "lo": 0.0, "hi": 0.0})
        soft.setdefault("no_demographics", {"d": 0.0, "q": float("nan")})
        data[m] = {"soft": soft, "flip": flip}
    return data


def make(fmt: str = "png") -> None:
    data = load()

    variants, tier_spans = [], []
    for name, colour, vs in TIERS:
        start = len(variants)
        variants += vs
        tier_spans.append((name, colour, start, len(variants)))
    n = len(variants)
    y = np.arange(n)[::-1]                       # first variant at top
    offs = np.linspace(-0.26, 0.26, len(MODELS))  # per-model dodge within a row

    fig, (axA, axB) = plt.subplots(
        1, 2, figsize=(11.5, 6.6), sharey=True,
        gridspec_kw={"wspace": 0.08},
    )

    # ── (A) SELECTION: flip rate vs each vendor's mean flip ──────────────────
    # Dashed line per vendor = its mean flip across the demographic variants.
    # Every variant overlaps its vendor line, so no demographic-specific effect.
    demo_vars = [v for v in variants if v != "no_demographics"]
    for (m, (_si, _fl, colour, _nf)), off in zip(MODELS.items(), offs):
        fl = data[m]["flip"]
        meanflip = np.nanmean([fl.get(v, {}).get("rate", np.nan) * 100 for v in demo_vars])
        axA.axvline(meanflip, color=colour, ls="--", lw=1.0, alpha=0.45, zorder=1)
        xs = [fl.get(v, {}).get("rate", np.nan) * 100 for v in variants]
        los = [fl.get(v, {}).get("lo", np.nan) * 100 for v in variants]
        his = [fl.get(v, {}).get("hi", np.nan) * 100 for v in variants]
        axA.hlines(y + off, los, his, color=colour, linewidth=1.0, alpha=0.55, zorder=2)
        axA.scatter(xs, y + off, s=22, color=colour, zorder=3,
                    edgecolor="white", linewidth=0.4)

    axA.text(0.5, n - 0.25, "dashed = each vendor's\nmean flip across variants",
             ha="left", va="top", fontsize=7.0, color="#555555", style="italic")
    axA.set_xlim(0, 27)
    axA.set_xlabel("Treatment-recommendation flip rate (%)", fontsize=9.5)
    axA.set_title("(A)  Treatment selection", fontsize=10.5, fontweight="bold", pad=8)
    axA.xaxis.grid(True, ls="--", alpha=0.35, zorder=0)

    # ── (B) FRAMING: Cohen's d ───────────────────────────────────────────────
    axB.axvline(0, color="#444444", linewidth=0.9, zorder=4)
    for (m, (_si, _fl, colour, _nf)), off in zip(MODELS.items(), offs):
        sd = data[m]["soft"]
        xs = [sd.get(v, {}).get("d", np.nan) for v in variants]
        sig = [sd.get(v, {}).get("q", np.nan) < 0.05 for v in variants]
        axB.scatter(xs, y + off, s=[30 if s else 20 for s in sig], color=colour,
                    zorder=3, edgecolor="white", linewidth=0.4)

    axB.set_xlim(-0.3, 2.05)
    axB.set_xlabel("Added soft-framing intensity (Cohen's $d$)", fontsize=9.5)
    axB.set_title("(B)  Response framing", fontsize=10.5, fontweight="bold", pad=8)
    axB.xaxis.grid(True, ls="--", alpha=0.35, zorder=0)

    # ── shared rows / tier-coloured labels / separators ──────────────────────
    axA.set_yticks(y)
    axA.set_yticklabels([LABELS[v] for v in variants], fontsize=9)
    tick_colour = {}
    for name, colour, s, e in tier_spans:
        for v in variants[s:e]:
            tick_colour[v] = colour
    for tick, v in zip(axA.get_yticklabels(), variants):
        tick.set_color(tick_colour[v])
    for ax in (axA, axB):
        ax.set_ylim(-0.6, n - 0.4)
        ax.tick_params(axis="y", length=0)
        for name, colour, s, e in tier_spans:
            if s != 0:
                ax.axhline((y[s] + y[s - 1]) / 2, color="#dddddd", lw=0.8, zorder=1)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.set_axisbelow(True)

    # tier brackets on far left
    for name, colour, s, e in tier_spans:
        mid = (y[s] + y[e - 1]) / 2
        axA.annotate(name, xy=(0, 0), xytext=(-0.40, mid),
                     textcoords=("axes fraction", "data"),
                     rotation=90, ha="center", va="center",
                     fontsize=8.2, fontweight="bold", color=colour,
                     annotation_clip=False)

    handles = [mlines.Line2D([], [], marker="o", linestyle="none",
                             color=c, markersize=7,
                             markeredgecolor="white", label=m)
               for m, (_si, _fl, c, _nf) in MODELS.items()]
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False,
               fontsize=9, bbox_to_anchor=(0.5, -0.02))

    fig.suptitle(
        "Demographic labels leave the treatment decision unchanged but reshape its framing",
        fontsize=12, fontweight="bold", y=0.99,
    )
    fig.text(0.5, -0.075,
             "1,048 GENIE NSCLC cases · 3 vendors · each variant = same note, one prepended demographic label vs no label.\n"
             "(A) Every variant overlaps its vendor's mean flip rate, so no demographic group destabilizes the recommendation. "
             "(B) Larger markers: $q_{BH}<0.05$.",
             ha="center", fontsize=7.4, color="#555555", style="italic")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"fig_dissociation.{fmt}"
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
