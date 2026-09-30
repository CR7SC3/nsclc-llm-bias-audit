"""Exploratory eFigure: stigmatizing-language gradient in NSCLC vs the breast (BRCA) and
pancreatic (PANC) cancer pilots.

Pilot cohorts (EXPLORATORY): 49 BRCA and 50 PANC GENIE BPC cases, run through the same
29-version design in Gemini-2.5-flash and DeepSeek-chat only. The dropped age label
(elderly_patient_75) is present in the pilot files but belongs to no stratum, so it is
excluded. NSCLC rates are the full 1,048-case cohort from panel_stigma_rates.csv.

Scoring is identical to Figure 4C: the core stigma composite (adherence doubt OR invented
SDOH content) via scripts.nsclc.finalize_panel._is_stigma, strata from finalize_panel.STRATA
(control = no-demographics reference pooled with White male privately insured; race or
ethnicity only = the 6 race-only labels). Error bars are Wilson 95% CIs on pooled responses.

Pilot results live in the separate Paper 2 folder (EquityGUIDE_BRCA_PANC); read-only here.
Output -> figures/manuscript/FigS13_multicancer_pilot.png
Run:  python3 plots/plot_multicancer_pilot.py
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from scripts.nsclc.finalize_panel import STRATA, _is_stigma, _wilson

plt.rcParams.update({"font.family": "sans-serif",
                     "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
                     "font.size": 12})

OUT = Path("figures/manuscript"); OUT.mkdir(parents=True, exist_ok=True)
PILOT = Path.home() / "Documents/EquityGUIDE_BRCA_PANC/results/baseline"
FILES = {
    ("Gemini-2.5-flash", "BRCA"): PILOT / "v2_genie_bpc_brca_pilot50_results.json",
    ("DeepSeek-chat", "BRCA"): PILOT / "v2_genie_bpc_brca_pilot50_deepseek-chat_results.json",
    ("Gemini-2.5-flash", "PANC"): PILOT / "v2_genie_bpc_panc_pilot50_results.json",
    ("DeepSeek-chat", "PANC"): PILOT / "v2_genie_bpc_panc_pilot50_deepseek-chat_results.json",
}
NSCLC_KEY = {"Gemini-2.5-flash": "gemini-2.5-flash", "DeepSeek-chat": "deepseek-chat"}
ORDER = ["control", "race_only", "uninsured", "underinsured", "low_income",
         "black_unhoused", "unhoused"]
LABEL = {"control": "Control", "race_only": "Race / ethnicity only", "uninsured": "Uninsured",
         "underinsured": "Underinsured", "low_income": "Low income",
         "black_unhoused": "Black + unhoused", "unhoused": "Unhoused"}
CANCERS = [("NSCLC", "#adadad"), ("BRCA", "#CC79A7"), ("PANC", "#0072B2")]
CANCER_NAME = {"NSCLC": "Lung (NSCLC, n = 1,048)", "BRCA": "Breast (n = 49)",
               "PANC": "Pancreatic (n = 50)"}


def pilot_rates(path):
    d = json.loads(Path(path).read_text())
    out = {}
    for s in ORDER:
        k = n = 0
        for cres in d.values():
            for vk in STRATA[s]:
                r = cres.get(vk)
                if isinstance(r, dict) and r.get("response_text"):
                    n += 1
                    k += _is_stigma(r["response_text"])
        p, lo, hi = _wilson(k, n)
        out[s] = (100 * p, 100 * lo, 100 * hi, k, n)
    return out, len(d)


def main():
    syn = pd.read_csv("results/analysis/panel_stigma_rates.csv")
    models = ["Gemini-2.5-flash", "DeepSeek-chat"]
    rates = {}
    for m in models:
        sub = syn[syn.model == NSCLC_KEY[m]].set_index("stratum")
        rates[(m, "NSCLC")] = {s: (100 * sub.loc[s, "rate"], 100 * sub.loc[s, "ci_low"],
                                   100 * sub.loc[s, "ci_high"], None, None) for s in ORDER}
        for c in ("BRCA", "PANC"):
            rates[(m, c)], ncase = pilot_rates(FILES[(m, c)])
            print(f"{m} {c}: {ncase} cases")

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.0), sharey=True)
    x = np.arange(len(ORDER)); w = 0.27
    for ax, m in zip(axes, models):
        for j, (c, col) in enumerate(CANCERS):
            r = rates[(m, c)]
            v = [r[s][0] for s in ORDER]
            lo = np.clip([r[s][0] - r[s][1] for s in ORDER], 0, None)
            hi = np.clip([r[s][2] - r[s][0] for s in ORDER], 0, None)
            ax.bar(x + (j - 1) * w, v, w, yerr=[lo, hi], color=col, edgecolor="k",
                   linewidth=0.5, error_kw=dict(ecolor="0.3", lw=0.9, capsize=2),
                   label=CANCER_NAME[c])
        ax.set_title(m, fontsize=13, fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels([LABEL[s] for s in ORDER], rotation=40, ha="right",
                           rotation_mode="anchor", fontsize=11)
        ax.set_ylim(0, 100); ax.set_yticks(range(0, 101, 20))
        ax.grid(axis="y", alpha=0.25); ax.set_axisbelow(True)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    axes[0].set_ylabel("Stigmatizing-language rate (%)")
    axes[0].legend(frameon=False, fontsize=11, loc="upper left")
    for ax, letter in zip(axes, "AB"):
        ax.text(-0.02, 1.04, letter, transform=ax.transAxes, fontsize=16,
                fontweight="bold", ha="right", va="bottom")
    fig.tight_layout(w_pad=2.0)
    out = OUT / "FigS13_multicancer_pilot.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    print("wrote", out)

    print("\nstratum rates (%, Wilson 95% CI) and unhoused - control gap:")
    for m in models:
        for c, _ in CANCERS:
            r = rates[(m, c)]
            row = "  ".join(f"{s} {r[s][0]:.1f} [{r[s][1]:.1f}, {r[s][2]:.1f}]" for s in ORDER)
            print(f"  {m:17s} {c:5s} gap {r['unhoused'][0] - r['control'][0]:+.1f}  | {row}")


if __name__ == "__main__":
    main()
