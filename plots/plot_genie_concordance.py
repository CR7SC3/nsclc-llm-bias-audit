"""EquityGUIDE — GENIE BPC Pilot-50 concordance figure.

Two-panel figure:
  A: NCCN concordance by demographic variant (Flash), with Wilson 95% CI,
     CancerGUIDE GPT-4o benchmark (80%) and Gemini synthetic baseline (63%) lines.
  B: Flash vs Flash-Lite overall + per-tier concordance comparison.

Usage
-----
    venv/bin/python plot_genie_concordance.py
    venv/bin/python plot_genie_concordance.py --format pdf
"""
from __future__ import annotations

import argparse
import json
from math import sqrt
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.analyze.response_parser import ResponseParser
from src.evaluate.nccn_scorer import get_nccn_answer
from src.evaluate.concordance_checker import _NCCN_TO_CATEGORY

FIGURES_DIR = Path("figures")
FIGURES_DIR.mkdir(exist_ok=True)

CASES_PATH = Path("data/processed/genie_bpc_nsclc_pilot50_with_notes.json")
FLASH_PATH = Path("results/baseline/v2_genie_bpc_nsclc_pilot50_results.json")
LITE_PATH  = Path("results/baseline/v2_genie_bpc_nsclc_pilot50_gemini-2.5-flash-lite_results.json")
GPT4O_PATH = Path("results/baseline/v2_genie_bpc_nsclc_pilot50_gpt-4o_results.json")

REFERENCE = "no_demographics"
BENCHMARK_GPT4O = 0.80   # CancerGUIDE GPT-4o concordance
BASELINE_GEMINI = 0.63   # EquityGUIDE V1 Gemini synthetic structured

TIER_COLORS = {
    "REF": "#888888", "A": "#4477AA", "B": "#EE6677",
    "C": "#228833", "D": "#CCBB44", "E": "#AA3377", "F": "#66CCEE",
}

VARIANT_ORDER = [
    ("REF", "no_demographics",          "No demographics (control)"),
    ("A", "white_male_private",         "White male, private ins."),
    ("A", "black_female_medicaid",      "Black female, Medicaid"),
    ("A", "latina_female_uninsured",    "Latina female, uninsured"),
    ("A", "black_female_private",       "Black female, private ins."),
    ("A", "white_female_medicaid",      "White female, Medicaid"),
    ("B", "black_race_only",            "Black (race only)"),
    ("B", "hispanic_race_only",         "Hispanic (race only)"),
    ("B", "asian_race_only",            "Asian (race only)"),
    ("B", "native_american_race_only",  "Native American (race only)"),
    ("C", "unhoused_patient",           "Unhoused patient"),
    ("C", "low_income_patient",         "Low income"),
    ("C", "high_income_patient",        "High income"),
    ("D", "uninsured_only",             "Uninsured only"),
    ("D", "medicaid_only",              "Medicaid only"),
    ("E", "white_female_medicaid",      "White female, Medicaid (iso)"),
    ("E", "black_female_private",       "Black female, private (iso)"),
    ("F", "non_binary_patient",         "Non-binary patient"),
    ("F", "transgender_woman",          "Transgender woman"),
    ("F", "gay_male_patient",           "Gay male patient"),
]
# E tier duplicates A labels — dedupe for panel A display
PANEL_A_ORDER = [
    ("REF", "no_demographics",          "No demographics (control)"),
    ("A", "white_male_private",         "White male, private ins."),
    ("A", "black_female_medicaid",      "Black female, Medicaid"),
    ("A", "latina_female_uninsured",    "Latina female, uninsured"),
    ("A", "black_female_private",       "Black female, private ins."),
    ("A", "white_female_medicaid",      "White female, Medicaid"),
    ("B", "black_race_only",            "Black (race only)"),
    ("B", "hispanic_race_only",         "Hispanic (race only)"),
    ("B", "asian_race_only",            "Asian (race only)"),
    ("B", "native_american_race_only",  "Native American (race only)"),
    ("C", "unhoused_patient",           "Unhoused patient"),
    ("C", "low_income_patient",         "Low income"),
    ("C", "high_income_patient",        "High income"),
    ("D", "uninsured_only",             "Uninsured only"),
    ("D", "medicaid_only",              "Medicaid only"),
    ("F", "non_binary_patient",         "Non-binary patient"),
    ("F", "transgender_woman",          "Transgender woman"),
    ("F", "gay_male_patient",           "Gay male patient"),
]

TIERS = {
    "A": ["white_male_private", "black_female_medicaid", "latina_female_uninsured",
          "black_female_private", "white_female_medicaid"],
    "B": ["black_race_only", "hispanic_race_only", "asian_race_only",
          "native_american_race_only"],
    "C": ["unhoused_patient", "low_income_patient", "high_income_patient"],
    "D": ["uninsured_only", "medicaid_only"],
    "F": ["non_binary_patient", "transgender_woman", "gay_male_patient"],
}


def _acceptable_cats(nccn: dict) -> set[str]:
    primary = _NCCN_TO_CATEGORY.get(nccn["primary_answer"])
    cats = {primary} if primary else set()
    for ans in nccn.get("acceptable_answers", []):
        c = _NCCN_TO_CATEGORY.get(ans)
        if c:
            cats.add(c)
    return cats


def concordance_by_variant(results: dict, case_map: dict) -> dict:
    parser = ResponseParser()
    vstats: dict[str, dict] = {}
    for case_id, variants in results.items():
        cp = case_map.get(case_id, {}).get("clinical_profile", {})
        nccn = get_nccn_answer(cp)
        if not nccn:
            continue
        cats = _acceptable_cats(nccn)
        if not cats:
            continue
        for v, result in variants.items():
            vstats.setdefault(v, {"correct": 0, "total": 0})
            if "error" in result:
                continue
            cat = result.get("parsed_category") or parser.parse(
                result.get("response_text", "")).category
            if cat and cat != "unknown":
                vstats[v]["total"] += 1
                if cat in cats:
                    vstats[v]["correct"] += 1
    return vstats


def wilson(p: float, n: int) -> tuple[float, float]:
    if n == 0:
        return 0.0, 0.0
    z = 1.96
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    margin = (z * sqrt(p * (1 - p) / n + z**2 / (4 * n**2))) / denom
    return max(0, centre - margin), min(1, centre + margin)


def make_figure(flash: dict, lite: dict, case_map: dict, fmt: str = "png", gpt4o: dict | None = None) -> None:
    flash_conc = concordance_by_variant(flash, case_map)
    lite_conc  = concordance_by_variant(lite, case_map)
    gpt_conc   = concordance_by_variant(gpt4o, case_map) if gpt4o else flash_conc

    fig, (axA, axB) = plt.subplots(
        1, 2, figsize=(16, 9), gridspec_kw={"width_ratios": [2.2, 1]})
    fig.subplots_adjust(wspace=0.32)

    # ── Panel A: concordance by variant (Flash) ──────────────────────────────
    rows = []
    for tier, variant, label in PANEL_A_ORDER:
        s = flash_conc.get(variant, {"correct": 0, "total": 0})
        rate = s["correct"] / s["total"] if s["total"] else 0
        lo, hi = wilson(rate, s["total"])
        rows.append((tier, label, rate, lo, hi, s["total"]))

    y = np.arange(len(rows))[::-1]
    for yi, (tier, label, rate, lo, hi, tot) in zip(y, rows):
        color = TIER_COLORS[tier]
        axA.plot([lo, hi], [yi, yi], color=color, lw=2, alpha=0.5, zorder=1)
        axA.scatter([rate], [yi], color=color, s=90, zorder=2,
                    edgecolor="white", linewidth=0.8)
        axA.text(rate + 0.012, yi, f"{rate:.0%}", va="center", fontsize=8.5,
                 color="#222")

    axA.axvline(BENCHMARK_GPT4O, color="#333", ls="--", lw=1.3, zorder=0)
    axA.text(BENCHMARK_GPT4O, len(rows) - 0.3, " CancerGUIDE\n GPT-4o (80%)",
             fontsize=8, color="#333", va="top")
    axA.axvline(BASELINE_GEMINI, color="#cc5500", ls=":", lw=1.3, zorder=0)
    axA.text(BASELINE_GEMINI, len(rows) - 0.3, " Gemini V1\n synthetic (63%)",
             fontsize=8, color="#cc5500", va="top", ha="right")

    axA.set_yticks(y)
    axA.set_yticklabels([r[1] for r in rows], fontsize=9)
    axA.set_xlim(0.5, 1.0)
    axA.set_xlabel("NCCN guideline concordance rate", fontsize=10)
    axA.set_title("A · NCCN concordance by demographic variant\n"
                  "Gemini 2.5 Flash · GENIE BPC pilot-50 · 95% Wilson CI",
                  fontsize=11, loc="left")
    axA.grid(axis="x", alpha=0.25)
    for spine in ("top", "right"):
        axA.spines[spine].set_visible(False)

    # ── Panel B: Flash vs Flash-Lite (overall + per-tier) ────────────────────
    def overall(conc):
        t = sum(s["total"] for s in conc.values())
        c = sum(s["correct"] for s in conc.values())
        return c / t if t else 0

    def tier_rate(conc, variants):
        t = sum(conc.get(v, {}).get("total", 0) for v in variants)
        c = sum(conc.get(v, {}).get("correct", 0) for v in variants)
        return c / t if t else 0

    groups = ["Overall", "Reference"] + [f"Tier {k}" for k in TIERS]
    flash_vals = [overall(flash_conc),
                  flash_conc[REFERENCE]["correct"] / flash_conc[REFERENCE]["total"]]
    lite_vals  = [overall(lite_conc),
                  lite_conc[REFERENCE]["correct"] / lite_conc[REFERENCE]["total"]]
    gpt_vals   = [overall(gpt_conc),
                  gpt_conc[REFERENCE]["correct"] / gpt_conc[REFERENCE]["total"]]
    for k, variants in TIERS.items():
        flash_vals.append(tier_rate(flash_conc, variants))
        lite_vals.append(tier_rate(lite_conc, variants))
        gpt_vals.append(tier_rate(gpt_conc, variants))

    yb = np.arange(len(groups))[::-1]
    h = 0.26
    axB.barh(yb + h,       flash_vals, height=h, color="#4477AA", label="Flash")
    axB.barh(yb,           gpt_vals,   height=h, color="#228833", label="GPT-4o")
    axB.barh(yb - h,       lite_vals,  height=h, color="#EE9944", label="Flash-Lite")
    for yi, fv, gv, lv in zip(yb, flash_vals, gpt_vals, lite_vals):
        axB.text(fv + 0.01, yi + h,  f"{fv:.0%}", va="center", fontsize=7)
        axB.text(gv + 0.01, yi,      f"{gv:.0%}", va="center", fontsize=7)
        axB.text(lv + 0.01, yi - h,  f"{lv:.0%}", va="center", fontsize=7)

    axB.axvline(BENCHMARK_GPT4O, color="#333", ls="--", lw=1.1, zorder=0)
    axB.set_yticks(yb)
    axB.set_yticklabels(groups, fontsize=9)
    axB.set_xlim(0, 1.0)
    axB.set_xlabel("NCCN concordance rate", fontsize=10)
    axB.set_title("B · 3-model concordance comparison",
                  fontsize=11, loc="left")
    axB.legend(fontsize=9, loc="lower right")
    axB.grid(axis="x", alpha=0.25)
    for spine in ("top", "right"):
        axB.spines[spine].set_visible(False)

    fig.suptitle("EquityGUIDE · GENIE BPC NSCLC pilot-50 · NCCN guideline concordance",
                 fontsize=13, y=0.97)

    out = FIGURES_DIR / f"fig_genie_pilot50_concordance.{fmt}"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {out}")
    print(f"  Flash overall:    {overall(flash_conc):.1%}")
    print(f"  GPT-4o overall:   {overall(gpt_conc):.1%}")
    print(f"  Lite overall:     {overall(lite_conc):.1%}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--format", choices=["png", "pdf"], default="png")
    args = ap.parse_args()

    cases = json.loads(CASES_PATH.read_text())
    case_map = {c["case_id"]: c for c in cases}
    flash = json.loads(FLASH_PATH.read_text())
    lite  = json.loads(LITE_PATH.read_text())
    gpt4o = json.loads(GPT4O_PATH.read_text())
    make_figure(flash, lite, case_map, fmt=args.format, gpt4o=gpt4o)
