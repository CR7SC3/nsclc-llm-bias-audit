"""EquityGUIDE — single-model GENIE BPC Pilot-50 concordance figure.

Two-panel figure for one model across the full 30-variant set:
  A: NCCN concordance by demographic variant (lollipop, Wilson 95% CI),
     with CancerGUIDE GPT-4o (80%) and Gemini V1 synthetic (63%) reference lines.
  B: Concordance by tier vs the no-demographics reference.

Reuses the scorer helpers in plot_genie_concordance.py so scoring stays identical.
Variant order/tiers mirror src/generate/variant_injector_v2.py (the corrected set).

Usage
-----
    venv/bin/python plot_genie_concordance_single.py \
        --results results/baseline/v2_genie_bpc_nsclc_pilot50_deepseek-chat_results.json \
        --model-label "deepseek-chat (temp 0)" --tag _deepseek_temp0
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import plot_genie_concordance as P  # concordance_by_variant, wilson, TIER_COLORS

FIGURES_DIR = Path("figures")
FIGURES_DIR.mkdir(exist_ok=True)

CASES_PATH = Path("data/processed/genie_bpc_nsclc_pilot50_with_notes.json")
REFERENCE = "no_demographics"
BENCHMARK_GPT4O = 0.80   # CancerGUIDE GPT-4o concordance
BASELINE_GEMINI = 0.63   # EquityGUIDE V1 Gemini synthetic structured

# Full 30-variant order, mirroring VARIANT_GROUPS_V2 / corrected analyze TIERS.
VARIANT_ORDER = [
    ("REF", "no_demographics",          "No demographics (control)"),
    ("A", "white_male_private",         "White male, private ins."),
    ("A", "black_female_medicaid",      "Black female, Medicaid"),
    ("A", "latina_female_uninsured",    "Latina female, uninsured"),
    ("A", "black_female_private",       "Black female, private ins."),
    ("A", "white_female_medicaid",      "White female, Medicaid"),
    ("B", "uninsured_only",             "Uninsured only"),
    ("B", "medicaid_only",              "Medicaid only"),
    ("B", "medicare_only",              "Medicare only"),
    ("B", "medicare_advantage_only",    "Medicare Advantage only"),
    ("B", "underinsured_only",          "Underinsured only"),
    ("C", "black_race_only",            "Black (race only)"),
    ("C", "hispanic_race_only",         "Hispanic (race only)"),
    ("C", "asian_race_only",            "Asian (race only)"),
    ("C", "native_american_race_only",  "Native American (race only)"),
    ("C", "middle_eastern_race_only",   "Middle Eastern (race only)"),
    ("C", "multiracial_race_only",      "Multiracial (race only)"),
    ("D", "rural_patient",              "Rural patient"),
    ("D", "small_community_hospital",   "Small community hospital"),
    ("E", "elderly_patient_75",         "Elderly (age 75+)"),
    ("F", "immigrant_patient",          "Immigrant patient"),
    ("F", "limited_english_patient",    "Limited English proficiency"),
    ("G", "unhoused_patient",           "Unhoused patient"),
    ("G", "low_income_patient",         "Low income"),
    ("G", "high_income_patient",        "High income"),
    ("H", "black_unhoused",             "Black + unhoused"),
    ("H", "low_income_black",           "Low income + Black"),
    ("I", "non_binary_patient",         "Non-binary patient"),
    ("I", "transgender_woman",          "Transgender woman"),
    ("I", "gay_male_patient",           "Gay male patient"),
]

TIER_COLORS = {
    "REF": "#888888", "A": "#4477AA", "B": "#CCBB44", "C": "#EE6677",
    "D": "#AA3377", "E": "#BBBBBB", "F": "#66CCEE", "G": "#228833",
    "H": "#117755", "I": "#EE9944",
}

TIER_LABELS = {
    "A": "A — Race × insurance",
    "B": "B — Insurance only",
    "C": "C — Race only",
    "D": "D — Geography",
    "E": "E — Age",
    "F": "F — Immigration / language",
    "G": "G — SES only",
    "H": "H — Race × SES",
    "I": "I — Gender / identity",
}

TIERS = {t: [v for tt, v, _ in VARIANT_ORDER if tt == t]
         for t in ["A", "B", "C", "D", "E", "F", "G", "H", "I"]}


def make_figure(results: dict, case_map: dict, model_label: str,
                tag: str, fmt: str = "png") -> None:
    conc = P.concordance_by_variant(results, case_map)

    fig, (axA, axB) = plt.subplots(
        1, 2, figsize=(16, 11), gridspec_kw={"width_ratios": [2.3, 1]})
    fig.subplots_adjust(wspace=0.34)

    # ── Panel A: concordance by variant ──────────────────────────────────────
    rows = []
    for tier, variant, label in VARIANT_ORDER:
        s = conc.get(variant, {"correct": 0, "total": 0})
        rate = s["correct"] / s["total"] if s["total"] else 0
        lo, hi = P.wilson(rate, s["total"])
        rows.append((tier, label, rate, lo, hi, s["total"], s["correct"]))

    ref_rate = rows[0][2]
    y = np.arange(len(rows))[::-1]
    for yi, (tier, label, rate, lo, hi, tot, cor) in zip(y, rows):
        color = TIER_COLORS[tier]
        axA.plot([lo, hi], [yi, yi], color=color, lw=2, alpha=0.5, zorder=1)
        axA.scatter([rate], [yi], color=color, s=90, zorder=2,
                    edgecolor="white", linewidth=0.8)
        axA.text(hi + 0.012, yi, f"{rate:.0%} ({cor}/{tot})", va="center",
                 fontsize=8, color="#222")

    axA.axvline(ref_rate, color="#888", ls="-", lw=1.0, alpha=0.7, zorder=0)
    axA.axvline(BENCHMARK_GPT4O, color="#333", ls="--", lw=1.3, zorder=0)
    axA.text(BENCHMARK_GPT4O, len(rows) - 0.3, " CancerGUIDE\n GPT-4o (80%)",
             fontsize=8, color="#333", va="top")
    axA.axvline(BASELINE_GEMINI, color="#cc5500", ls=":", lw=1.3, zorder=0)
    axA.text(BASELINE_GEMINI, len(rows) - 0.3, " Gemini V1\n synthetic (63%)",
             fontsize=8, color="#cc5500", va="top", ha="right")

    axA.set_yticks(y)
    axA.set_yticklabels([r[1] for r in rows], fontsize=8.5)
    axA.set_xlim(0.4, 1.02)
    axA.set_xlabel("NCCN guideline concordance rate", fontsize=10)
    axA.set_title(f"A · NCCN concordance by demographic variant\n"
                  f"{model_label} · GENIE BPC pilot-50 · 95% Wilson CI",
                  fontsize=11, loc="left")
    axA.grid(axis="x", alpha=0.25)
    for spine in ("top", "right"):
        axA.spines[spine].set_visible(False)

    # tier separators
    tiers_seq = [r[0] for r in rows]
    for i in range(1, len(rows)):
        if tiers_seq[i] != tiers_seq[i - 1]:
            axA.axhline(y[i] + 0.5, color="#dddddd", lw=0.8, zorder=0)

    # ── Panel B: concordance by tier ─────────────────────────────────────────
    def rate(variants):
        t = sum(conc.get(v, {}).get("total", 0) for v in variants)
        c = sum(conc.get(v, {}).get("correct", 0) for v in variants)
        return (c / t if t else 0), t

    overall_t = sum(s["total"] for s in conc.values())
    overall_c = sum(s["correct"] for s in conc.values())
    groups = ["Overall", "Reference"] + [TIER_LABELS[k] for k in TIERS]
    vals, colors = [], []
    ovr = overall_c / overall_t if overall_t else 0
    vals.append(ovr); colors.append("#444444")
    rr, _ = rate([REFERENCE]); vals.append(rr); colors.append(TIER_COLORS["REF"])
    for k in TIERS:
        v, _ = rate(TIERS[k]); vals.append(v); colors.append(TIER_COLORS[k])

    yb = np.arange(len(groups))[::-1]
    axB.barh(yb, vals, height=0.62, color=colors, alpha=0.9)
    for yi, v in zip(yb, vals):
        axB.text(v + 0.01, yi, f"{v:.0%}", va="center", fontsize=8.5)

    axB.axvline(ovr, color="#444", ls="-", lw=1.0, alpha=0.6, zorder=0)
    axB.axvline(BENCHMARK_GPT4O, color="#333", ls="--", lw=1.1, zorder=0)
    axB.set_yticks(yb)
    axB.set_yticklabels(groups, fontsize=9)
    axB.set_xlim(0, 1.05)
    axB.set_xlabel("NCCN concordance rate", fontsize=10)
    axB.set_title("B · Concordance by tier", fontsize=11, loc="left")
    axB.grid(axis="x", alpha=0.25)
    for spine in ("top", "right"):
        axB.spines[spine].set_visible(False)

    fig.suptitle(f"EquityGUIDE · GENIE BPC NSCLC pilot-50 · NCCN concordance · {model_label}",
                 fontsize=13, y=0.95)

    out = FIGURES_DIR / f"fig_genie_pilot50_concordance{tag}.{fmt}"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {out}")
    print(f"  Overall concordance: {ovr:.1%}  ({overall_c}/{overall_t})")
    print(f"  Reference:           {rr:.1%}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True, help="Path to v2 results/checkpoint JSON")
    ap.add_argument("--model-label", default="model", help="Model name shown in titles")
    ap.add_argument("--tag", default="", help="Suffix for output filename")
    ap.add_argument("--format", choices=["png", "pdf"], default="png")
    args = ap.parse_args()

    cases = json.loads(CASES_PATH.read_text())
    case_map = {c["case_id"]: c for c in cases}
    results = json.loads(Path(args.results).read_text())
    make_figure(results, case_map, args.model_label, args.tag, fmt=args.format)
