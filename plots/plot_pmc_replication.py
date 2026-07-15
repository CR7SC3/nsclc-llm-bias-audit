"""PMC replication RESULT — does the stigma gradient hold on real notes?

Compares the stigma rate (adherence-doubt OR hallucinated SDOH) on the synthetic
GENIE cohort (n=1,048, from panel_stigma_rates.csv) vs. the 40 real open-access
PubMed Central case reports, for Gemini and DeepSeek, by disadvantage stratum.
Error bars = 95% Wilson CI. Same stratum aggregation as panel_stigma_rates.csv.

Output -> figures/manuscript/fig4_pmc_replication.png
Run:  python3 plots/plot_pmc_replication.py
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from src.analyze.soft_bias import detect_all
from src.analyze.stats import wilson_ci

OUT = Path("figures/manuscript"); OUT.mkdir(parents=True, exist_ok=True)
# Shared note-type palette across the Fig 9 robustness panels (9a/9b/9c) so
# each note source reads as its own colour; vendor stays encoded by panel + title.
NOTE_COLORS = {
    "synthetic": "#2CA6A4",   # teal   — synthetic stigma baseline (LLM / TAG notes)
    "template":  "#8E6CAE",   # purple — circularity control (deterministic template notes)
    "real":      "#E8833A",   # orange — real PubMed Central notes
    "prose":     "#4C9F70",   # green  — natural-prose embedding
}
STIGMA = ("adherence_compliance", "sdoh_generation")
# stratum -> variant keys (matches panel_stigma_rates.csv aggregation)
STRATA = {
    "control": ["white_male_private", "no_demographics"],
    "race-only": ["black_race_only", "hispanic_race_only", "asian_race_only",
                  "native_american_race_only", "middle_eastern_race_only",
                  "multiracial_race_only"],
    "uninsured": ["uninsured_only"],
    "low income": ["low_income_patient"],
    "unhoused": ["unhoused_patient"],
}
# panel_stigma_rates.csv stratum names
SYN_NAME = {"control": "control", "race-only": "race_only", "uninsured": "uninsured",
            "low income": "low_income", "unhoused": "unhoused"}
PMC = {"Gemini": "results/baseline/v2_pmc_nsclc_results.json",
       "DeepSeek": "results/baseline/v2_pmc_nsclc_deepseek-chat_results.json"}
SYN_MODEL = {"Gemini": "gemini-2.5-flash", "DeepSeek": "deepseek-chat"}
MC = {"Gemini": "#4C72B0", "DeepSeek": "#C44E52"}


def pmc_rate(raw, vkeys):
    k = n = 0
    for cid, cd in raw.items():
        for vk in vkeys:
            txt = cd.get(vk, {}).get("response_text", "")
            if not txt:
                continue
            n += 1
            if any(detect_all(txt).get(d) for d in STIGMA):
                k += 1
    lo, hi = wilson_ci(k, n) if n else (0, 0)
    return 100 * k / n if n else 0, 100 * lo, 100 * hi


def main():
    syn = pd.read_csv("results/analysis/panel_stigma_rates.csv")
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2), sharey=True)
    labels = list(STRATA.keys())
    x = np.arange(len(labels)); w = 0.38
    for ax, model in zip(axes, PMC):
        raw = json.loads(Path(PMC[model]).read_text())
        # synthetic (from panel csv)
        sub = syn[syn.model == SYN_MODEL[model]].set_index("stratum")
        syn_r = [sub.loc[SYN_NAME[s], "rate"] * 100 for s in labels]
        syn_lo = [(sub.loc[SYN_NAME[s], "rate"] - sub.loc[SYN_NAME[s], "ci_low"]) * 100 for s in labels]
        syn_hi = [(sub.loc[SYN_NAME[s], "ci_high"] - sub.loc[SYN_NAME[s], "rate"]) * 100 for s in labels]
        # PMC real
        pmc = [pmc_rate(raw, STRATA[s]) for s in labels]
        pmc_r = [p[0] for p in pmc]
        pmc_lo = [p[0] - p[1] for p in pmc]
        pmc_hi = [p[2] - p[0] for p in pmc]
        ax.bar(x - w/2, syn_r, w, yerr=[syn_lo, syn_hi],
               error_kw=dict(ecolor="0.3", lw=0.9, capsize=2),
               color=NOTE_COLORS["synthetic"], edgecolor="k", linewidth=0.5,
               label="Synthetic notes (n=1,048)")
        ax.bar(x + w/2, pmc_r, w, yerr=[np.clip(pmc_lo, 0, None), np.clip(pmc_hi, 0, None)],
               error_kw=dict(ecolor="0.3", lw=0.9, capsize=2),
               color=NOTE_COLORS["real"], edgecolor="k", linewidth=0.5,
               label="Real PMC notes (n=40)")
        ax.set_title(model, color=MC[model], fontweight="bold")
        ax.set_xticks(x); ax.set_xticklabels(labels, rotation=15)
        ax.set_xlabel("Disadvantage stratum")
        ax.legend(fontsize=9, framealpha=0.95)
    axes[0].set_ylabel("Stigmatizing-language rate (%)")
    fig.suptitle("The stigma gradient replicates on real notes\n"
                 "Synthetic GENIE cohort vs 40 real PubMed Central case reports "
                 "(95% Wilson CI)", fontsize=12, fontweight="bold", y=1.03)
    fig.tight_layout(rect=(0, 0, 1, 0.99))
    fig.savefig(OUT / "fig4_pmc_replication.png", dpi=150, bbox_inches="tight")
    print("wrote", OUT / "fig4_pmc_replication.png")
    # print the numbers
    for model in PMC:
        raw = json.loads(Path(PMC[model]).read_text())
        print(f"\n{model} PMC real-note stigma rate:")
        for s in labels:
            r, lo, hi = pmc_rate(raw, STRATA[s])
            print(f"  {s:12s} {r:5.1f}% [{lo:.1f}, {hi:.1f}]")


if __name__ == "__main__":
    main()
