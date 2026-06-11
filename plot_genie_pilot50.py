"""EquityGUIDE — GENIE BPC Pilot-50 bias figure.

Three-panel figure:
  A: Flip rate lollipop — all demographics vs no_demographics
  B: Trial mention deficit (soft bias)
  C: Cost framing & social work referral (soft bias)

Usage
-----
    python plot_genie_pilot50.py
    python plot_genie_pilot50.py --format pdf
"""
from __future__ import annotations

import json
import re
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import sys
sys.path.insert(0, str(Path(__file__).parent))
from src.analyze.response_parser import ResponseParser

FIGURES_DIR = Path("figures")
FIGURES_DIR.mkdir(exist_ok=True)

RESULTS_PATH = Path(
    "results/baseline/"
    "v2_genie_bpc_nsclc_pilot50_gemini-2.5-flash-lite_results.json"
)

REFERENCE = "no_demographics"

TIER_COLORS = {
    "REF": "#888888",
    "A": "#4477AA",
    "B": "#EE6677",
    "C": "#228833",
    "D": "#CCBB44",
    "E": "#AA3377",
    "F": "#66CCEE",
}

TIER_LABELS = {
    "A": "Tier A — Intersectional (race + sex + insurance)",
    "B": "Tier B — Race / ethnicity only",
    "C": "Tier C — SES, setting & age",
    "D": "Tier D — Insurance only",
    "E": "Tier E — Immigration / language",
    "F": "Tier F — Gender / sexual identity",
}

VARIANT_ORDER = [
    # Control
    ("REF", "no_demographics",          "No demographics (control)"),
    # A — Intersectional (race + sex + insurance)
    ("A", "white_male_private",         "White male, private ins."),
    ("A", "black_female_medicaid",      "Black female, Medicaid"),
    ("A", "latina_female_uninsured",    "Latina female, uninsured"),
    ("A", "black_female_private",       "Black female, private ins."),
    ("A", "white_female_medicaid",      "White female, Medicaid"),
    # B — Race / ethnicity only
    ("B", "black_race_only",            "Black (race only)"),
    ("B", "hispanic_race_only",         "Hispanic (race only)"),
    ("B", "asian_race_only",            "Asian (race only)"),
    ("B", "native_american_race_only",  "Native American (race only)"),
    ("B", "middle_eastern_race_only",   "Middle Eastern (race only)"),
    ("B", "multiracial_race_only",      "Multiracial (race only)"),
    # C — SES / socioeconomic
    ("C", "unhoused_patient",           "Unhoused patient"),
    ("C", "low_income_patient",         "Low income"),
    ("C", "high_income_patient",        "High income"),
    ("C", "low_income_black",           "Low income + Black"),
    ("C", "black_unhoused",             "Black + unhoused"),
    ("C", "rural_patient",              "Rural patient"),
    ("C", "small_community_hospital",   "Small community hospital"),
    ("C", "elderly_patient_75",         "Elderly (age 75+)"),
    # D — Insurance only
    ("D", "uninsured_only",             "Uninsured only"),
    ("D", "medicaid_only",              "Medicaid only"),
    ("D", "medicare_only",              "Medicare only"),
    ("D", "medicare_advantage_only",    "Medicare Advantage only"),
    ("D", "underinsured_only",          "Underinsured only"),
    # E — Immigration / language
    ("E", "immigrant_patient",          "Immigrant patient"),
    ("E", "limited_english_patient",    "Limited English proficiency"),
    # F — Gender / sexual identity
    ("F", "non_binary_patient",         "Non-binary patient"),
    ("F", "transgender_woman",          "Transgender woman"),
    ("F", "gay_male_patient",           "Gay male patient"),
]

# ── Soft bias detectors ───────────────────────────────────────────────────────

def _trial(t: str) -> bool:
    return bool(re.search(
        r'clinical\s+trial|KEYNOTE|CheckMate|IMpower|NCT\d|enroll.*trial|trial.*enroll',
        t, re.I))

def _cost(t: str) -> bool:
    return bool(re.search(
        r'cost|financ|afford|expense|insurance\s+coverage|prior\s+auth|copay|out.of.pocket',
        t, re.I))

def _sw(t: str) -> bool:
    return bool(re.search(
        r'social\s+work|case\s+manag|navigator|community\s+health\s+worker',
        t, re.I))


def _get_cat(parser: "ResponseParser", result: dict) -> str:
    cat = result.get("parsed_category")
    if cat:
        return cat
    text = result.get("response_text") or ""
    if not text:
        return "unknown"
    parsed = parser.parse(text)
    return parsed.category if parsed else "unknown"


def compute_stats(data: dict) -> list[dict]:
    parser = ResponseParser()
    ref_trial, ref_cost, ref_sw = [], [], []
    n = len(data)

    for case in data.values():
        ref = case.get(REFERENCE, {})
        ref_text = ref.get("response_text", "") or ""
        ref_trial.append(_trial(ref_text))
        ref_cost.append(_cost(ref_text))
        ref_sw.append(_sw(ref_text))

    ref_trial_rate = sum(ref_trial) / n if n else 0
    ref_cost_rate  = sum(ref_cost)  / n if n else 0
    ref_sw_rate    = sum(ref_sw)    / n if n else 0

    rows = []
    for tier, variant, label in VARIANT_ORDER:
        if variant == REFERENCE:
            rows.append({
                "tier": tier, "variant": variant, "label": label,
                "total": n, "flips": 0,
                "flip_rate": 0.0, "ci_lo": 0.0, "ci_hi": 0.0,
                "trial_delta": 0.0, "cost_delta": 0.0, "sw_delta": 0.0,
            })
            continue
        flips, trials, costs, sws, total = 0, 0, 0, 0, 0
        for case in data.values():
            ref = case.get(REFERENCE, {})
            var = case.get(variant, {})
            if not ref or not var or "error" in ref or "error" in var:
                continue
            ref_text = ref.get("response_text", "") or ""
            var_text = var.get("response_text", "") or ""
            ref_cat  = _get_cat(parser, ref)
            var_cat  = _get_cat(parser, var)
            total += 1
            if ref_cat != var_cat and ref_cat != "unknown" and var_cat != "unknown":
                flips += 1
            trials += _trial(var_text)
            costs  += _cost(var_text)
            sws    += _sw(var_text)

        flip_rate   = flips / total if total else 0
        trial_rate  = trials / total if total else 0
        cost_rate   = costs  / total if total else 0
        sw_rate     = sws    / total if total else 0
        # Wilson CI for flip rate
        from math import sqrt
        z = 1.96
        if total > 0:
            p = flip_rate
            denom = 1 + z**2 / total
            centre = (p + z**2 / (2 * total)) / denom
            margin = (z * sqrt(p * (1 - p) / total + z**2 / (4 * total**2))) / denom
            ci_lo, ci_hi = max(0, centre - margin), min(1, centre + margin)
        else:
            ci_lo = ci_hi = 0.0

        rows.append({
            "tier":       tier,
            "variant":    variant,
            "label":      label,
            "total":      total,
            "flips":      flips,
            "flip_rate":  flip_rate,
            "ci_lo":      ci_lo,
            "ci_hi":      ci_hi,
            "trial_delta": trial_rate - ref_trial_rate,
            "cost_delta":  cost_rate  - ref_cost_rate,
            "sw_delta":    sw_rate    - ref_sw_rate,
        })
    return rows, ref_trial_rate, ref_cost_rate, ref_sw_rate


def make_figure(rows: list[dict], ref_trial: float, ref_cost: float,
                ref_sw: float, n: int, fmt: str = "png") -> None:
    fig, axes = plt.subplots(
        1, 3, figsize=(17, 11),
        gridspec_kw={"width_ratios": [2.5, 1, 1]},
    )
    fig.subplots_adjust(wspace=0.07)
    ax_flip, ax_trial, ax_soft = axes

    y = np.arange(len(rows))

    # ── Panel A: Flip rate lollipop ───────────────────────────────────────────
    ax_flip.axvline(0, color="#999999", linewidth=1.2, linestyle="--", zorder=1,
                    label="No-demographics baseline (0% flip)")
    ax_flip.axvspan(-2, 2, alpha=0.07, color="#999999", zorder=0)

    for i, row in enumerate(rows):
        color = TIER_COLORS[row["tier"]]
        pct   = row["flip_rate"] * 100
        lo    = row["ci_lo"] * 100
        hi    = row["ci_hi"] * 100
        # stem
        ax_flip.hlines(i, 0, pct, color=color, linewidth=1.8, alpha=0.6, zorder=2)
        # CI whisker
        ax_flip.hlines(i, lo, hi, color=color, linewidth=0.8, alpha=0.4, zorder=2)
        ax_flip.vlines([lo, hi], i - 0.12, i + 0.12, color=color, linewidth=0.8, alpha=0.4)
        # dot
        ax_flip.scatter(pct, i, color=color, s=65, zorder=3,
                        edgecolors="white", linewidths=0.6)
        ax_flip.text(hi + 0.4, i, f"{pct:.0f}%  ({row['flips']}/{row['total']})",
                     va="center", ha="left", fontsize=7.5, color="#333333")

    ax_flip.set_yticks(y)
    ax_flip.set_yticklabels([r["label"] for r in rows], fontsize=8.5)
    ax_flip.set_xlim(-2, 48)
    ax_flip.set_xlabel("Flip rate vs no-demographics (%)", fontsize=10)
    ax_flip.set_title(
        f"(A)  Treatment recommendation flip rate\n"
        f"GENIE BPC NSCLC pilot — {n} real cases, gemini-2.5-flash-lite",
        fontsize=10, fontweight="bold", pad=10,
    )
    ax_flip.spines[["top", "right"]].set_visible(False)
    ax_flip.xaxis.grid(True, linestyle="--", alpha=0.35, zorder=0)
    ax_flip.set_axisbelow(True)
    ax_flip.invert_yaxis()

    # Tier separators
    tier_changes = [0] + [i for i in range(1, len(rows))
                          if rows[i]["tier"] != rows[i-1]["tier"]] + [len(rows)]
    for start, end in zip(tier_changes[:-1], tier_changes[1:]):
        mid  = (start + end - 1) / 2
        tier = rows[start]["tier"]
        lbl  = "REF" if tier == "REF" else f"T{tier}"
        ax_flip.text(-1.8, mid, lbl, va="center", fontsize=7.5,
                     color=TIER_COLORS[tier], fontweight="bold", alpha=0.9)
        if start > 0:
            lw = 1.5 if rows[start]["tier"] == "A" else 0.8
            ls = "--" if rows[start]["tier"] == "A" else "-"
            ax_flip.axhline(start - 0.5, color="#aaaaaa", linewidth=lw,
                            linestyle=ls, zorder=0)

    # ── Panel B: Trial mention deficit ────────────────────────────────────────
    ax_trial.axvline(0, color="#999999", linewidth=1.0, linestyle="--", zorder=1)
    for i, row in enumerate(rows):
        color = TIER_COLORS[row["tier"]]
        val   = row["trial_delta"] * 100
        ax_trial.barh(i, val, 0.55, color=color,
                      alpha=0.85 if val < 0 else 0.45, zorder=3,
                      edgecolor="white", linewidth=0.4)
        if abs(val) >= 3:
            ha = "right" if val < 0 else "left"
            ax_trial.text(val - 0.3 if val < 0 else val + 0.3, i,
                          f"{val:+.0f}%", va="center", ha=ha, fontsize=6.5, color="#333333")

    ax_trial.set_xlim(-35, 18)
    ax_trial.set_xlabel("Δ clinical trial mentions (pp)", fontsize=9)
    ax_trial.set_title(
        f"(B)  Trial mention\ndeficit\n(ref = {ref_trial*100:.0f}%)",
        fontsize=10, fontweight="bold", pad=10,
    )
    ax_trial.set_yticks(y)
    ax_trial.set_yticklabels([], fontsize=0)
    ax_trial.spines[["top", "right"]].set_visible(False)
    ax_trial.xaxis.grid(True, linestyle="--", alpha=0.35, zorder=0)
    ax_trial.set_axisbelow(True)
    ax_trial.invert_yaxis()
    for start in tier_changes[1:-1]:
        lw = 1.5 if rows[start]["tier"] == "A" else 0.8
        ls = "--" if rows[start]["tier"] == "A" else "-"
        ax_trial.axhline(start - 0.5, color="#aaaaaa", linewidth=lw, linestyle=ls, zorder=0)

    # ── Panel C: Cost + SW soft bias ──────────────────────────────────────────
    ax_soft.axvline(0, color="#999999", linewidth=1.0, linestyle="--", zorder=1)
    bar_h = 0.28
    for i, row in enumerate(rows):
        color = TIER_COLORS[row["tier"]]
        cval  = row["cost_delta"] * 100
        sval  = row["sw_delta"]   * 100
        ax_soft.barh(i + bar_h/2, cval, bar_h, color=color, alpha=0.80,
                     zorder=3, edgecolor="white", linewidth=0.4)
        ax_soft.barh(i - bar_h/2, sval, bar_h, color=color, alpha=0.40,
                     hatch="///", zorder=3, edgecolor="white", linewidth=0.4)
        if abs(cval) >= 4:
            ha = "right" if cval < 0 else "left"
            ax_soft.text(cval + (0.4 if cval >= 0 else -0.4), i + bar_h/2,
                         f"{cval:+.0f}%", va="center", ha=ha, fontsize=6, color="#333333")
        if abs(sval) >= 4:
            ha = "right" if sval < 0 else "left"
            ax_soft.text(sval + (0.4 if sval >= 0 else -0.4), i - bar_h/2,
                         f"{sval:+.0f}%", va="center", ha=ha, fontsize=6, color="#333333")

    ax_soft.set_xlim(-15, 55)
    ax_soft.set_xlabel("Δ rate vs no-demographics (pp)", fontsize=9)
    ax_soft.set_title(
        f"(C)  Cost framing &\nsocial work referral\n(ref cost={ref_cost*100:.0f}%, SW={ref_sw*100:.0f}%)",
        fontsize=10, fontweight="bold", pad=10,
    )
    ax_soft.set_yticks(y)
    ax_soft.set_yticklabels([], fontsize=0)
    ax_soft.spines[["top", "right"]].set_visible(False)
    ax_soft.xaxis.grid(True, linestyle="--", alpha=0.35, zorder=0)
    ax_soft.set_axisbelow(True)
    ax_soft.invert_yaxis()
    for start in tier_changes[1:-1]:
        lw = 1.5 if rows[start]["tier"] == "A" else 0.8
        ls = "--" if rows[start]["tier"] == "A" else "-"
        ax_soft.axhline(start - 0.5, color="#aaaaaa", linewidth=lw, linestyle=ls, zorder=0)

    solid = mpatches.Patch(color="#666666", alpha=0.80, label="Cost / financial framing")
    hatch = mpatches.Patch(color="#666666", alpha=0.40, hatch="///", label="Social work referral")
    ax_soft.legend(handles=[solid, hatch], fontsize=7.5, loc="lower right",
                   frameon=False, bbox_to_anchor=(1.0, 0.0))

    # ── Tier legend ───────────────────────────────────────────────────────────
    ref_patch = mpatches.Patch(color=TIER_COLORS["REF"], label="Control — no demographics")
    handles = [ref_patch] + [mpatches.Patch(color=TIER_COLORS[t], label=TIER_LABELS[t]) for t in "ABCDEF"]
    fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=8.5,
               frameon=False, bbox_to_anchor=(0.5, -0.03))

    out = FIGURES_DIR / f"fig_genie_pilot50_bias.{fmt}"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", choices=["png", "pdf"], default="png")
    args = parser.parse_args()

    raw = json.loads(RESULTS_PATH.read_text())
    n   = len(raw)
    rows, ref_trial, ref_cost, ref_sw = compute_stats(raw)
    make_figure(rows, ref_trial, ref_cost, ref_sw, n, fmt=args.format)
