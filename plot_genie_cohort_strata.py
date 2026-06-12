"""EquityGUIDE — GENIE BPC NSCLC full-cohort stratification figure.

Multi-panel overview of the 1,048-case cohort by clinical & demographic metadata:
  Stage · Histology · Driver status · Stage IV PD-L1 · Institution ·
  Sex · Race/ethnicity · Age · Smoking · Actionable driver breakdown.

Usage
-----
    venv/bin/python plot_genie_cohort_strata.py
    venv/bin/python plot_genie_cohort_strata.py --format pdf
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

FIGURES_DIR = Path("figures")
FIGURES_DIR.mkdir(exist_ok=True)
COHORT_PATH = Path("data/processed/genie_bpc_nsclc_processed.json")

C = {
    "blue": "#4477AA", "red": "#EE6677", "green": "#228833",
    "yellow": "#CCBB44", "purple": "#AA3377", "cyan": "#66CCEE",
    "grey": "#999999", "orange": "#EE9944",
}


def stage_bucket(s: str) -> str:
    s = (s or "").upper()
    for k in ("IV", "III", "II", "I"):
        if s.startswith(k):
            return k
    return "?"


def driver_status(c: dict) -> str:
    p = c["clinical_profile"]
    if not c.get("biomarkers_available", True):
        return "Unknown"
    flags = [
        p.get("egfr_status") not in ("negative", "unknown", "not_on_panel"),
        p.get("alk_status") == "positive",
        p.get("ros1_status") == "positive",
        p.get("braf_status") == "v600e",
        p.get("met_status") == "exon_14",
        p.get("ret_status") == "fusion",
        p.get("ntrk_status") == "fusion",
        p.get("kras_status") == "g12c",
    ]
    return "Driver +" if any(flags) else "Driver-neg"


def actionable_driver(c: dict) -> str | None:
    p = c["clinical_profile"]
    if p.get("egfr_status") not in ("negative", "unknown", "not_on_panel"):
        return "EGFR"
    if p.get("alk_status") == "positive":
        return "ALK"
    if p.get("ros1_status") == "positive":
        return "ROS1"
    if p.get("braf_status") == "v600e":
        return "BRAF"
    if p.get("met_status") == "exon_14":
        return "MET ex14"
    if p.get("ret_status") == "fusion":
        return "RET"
    if p.get("ntrk_status") == "fusion":
        return "NTRK"
    if p.get("kras_status") == "g12c":
        return "KRAS G12C"
    return None


def age_bucket(a) -> str:
    try:
        a = float(a)
    except (TypeError, ValueError):
        return "?"
    if a < 50:
        return "<50"
    if a < 60:
        return "50–59"
    if a < 70:
        return "60–69"
    if a < 80:
        return "70–79"
    return "80+"


def barh(ax, counts, order, title, color, n, pct=True):
    vals = [counts.get(k, 0) for k in order]
    y = np.arange(len(order))[::-1]
    ax.barh(y, vals, color=color, edgecolor="white", linewidth=0.6)
    for yi, v in zip(y, vals):
        lab = f"{v}" + (f"  ({v/n:.0%})" if pct else "")
        ax.text(v + max(vals) * 0.015, yi, lab, va="center", fontsize=8.5)
    ax.set_yticks(y)
    ax.set_yticklabels(order, fontsize=9)
    ax.set_xlim(0, max(vals) * 1.22)
    ax.set_title(title, fontsize=10.5, fontweight="bold", loc="left")
    ax.tick_params(axis="x", labelsize=8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def main(fmt="png"):
    cases = json.loads(COHORT_PATH.read_text())
    n = len(cases)

    fig, axes = plt.subplots(2, 4, figsize=(20, 10))
    fig.subplots_adjust(hspace=0.35, wspace=0.55)
    ax = axes.flatten()

    # 1. Stage
    sc = Counter(stage_bucket(c["clinical_profile"]["stage"]) for c in cases)
    barh(ax[0], sc, ["I", "II", "III", "IV"], "Stage", C["blue"], n)

    # 2. Histology
    hc = Counter(c["clinical_profile"].get("histology") for c in cases)
    barh(ax[1], hc, ["adenocarcinoma", "squamous", "nos"],
         "Histology", C["green"], n)

    # 3. Driver status
    dc = Counter(driver_status(c) for c in cases)
    barh(ax[2], dc, ["Driver-neg", "Driver +", "Unknown"],
         "Biomarker driver status", C["purple"], n)

    # 4. Actionable driver breakdown (driver+ only)
    adc = Counter(d for c in cases if (d := actionable_driver(c)))
    order_ad = [k for k, _ in adc.most_common()]
    barh(ax[3], adc, order_ad, "Actionable driver (driver+ cases)",
         C["red"], n, pct=False)

    # 5. Stage IV PD-L1
    iv = [c for c in cases if stage_bucket(c["clinical_profile"]["stage"]) == "IV"]
    pc = Counter(c["clinical_profile"].get("pdl1_tps_category", "?") for c in iv)
    barh(ax[4], pc, ["high", "intermediate", "low", "unknown"],
         f"PD-L1 (Stage IV, n={len(iv)})", C["yellow"], len(iv))

    # 6. Institution
    ic = Counter(c.get("institution") for c in cases)
    barh(ax[5], ic, [k for k, _ in ic.most_common()],
         "Institution", C["cyan"], n)

    # 7. Race / ethnicity
    rc = Counter(c["demographics"].get("race_ethnicity", "?") for c in cases)
    order_r = [k for k, _ in rc.most_common()][:6]
    barh(ax[6], rc, order_r, "Race / ethnicity (real)", C["orange"], n)

    # 8. Age at diagnosis
    agc = Counter(age_bucket(c.get("age_dx")) for c in cases)
    barh(ax[7], agc, ["<50", "50–59", "60–69", "70–79", "80+"],
         "Age at diagnosis", C["grey"], n)

    fig.suptitle(
        f"GENIE BPC NSCLC cohort stratification — {n} cases "
        f"(3 institutions: MSK, DFCI, VICC)",
        fontsize=14, fontweight="bold", y=0.98)

    out = FIGURES_DIR / f"fig_genie_cohort_strata.{fmt}"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--format", choices=["png", "pdf"], default="png")
    main(ap.parse_args().format)
