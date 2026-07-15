"""Generate the current, frame-aligned manuscript/presentation figures.

Committed to the dissociation thesis (see PAPER_FRAME.md). Sources for each figure
are noted inline. Numbers are the CONFIRMED full-panel values (Gemini/DeepSeek/Llama
n=1,048; judge-adjudicated stigma). Outputs -> figures/manuscript/.

Run:  python3 plots/plot_manuscript_figs.py
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from src.analyze.stats import wilson_ci

OUT = Path("figures/manuscript"); OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.size": 12, "axes.sphalf" if False else "axes.grid": False,
                     "figure.dpi": 150, "savefig.bbox": "tight"})
MODELS = ["gemini-2.5-flash", "deepseek-chat", "llama-3.3-70B", "llama-3.1-8B", "gpt-4o", "gpt-4o-mini"]
MC = {"gemini-2.5-flash": "#4C72B0", "deepseek-chat": "#C44E52", "llama-3.3-70B": "#55A868",
      "llama-3.1-8B": "#937860", "gpt-4o": "#8172B3", "gpt-4o-mini": "#CCB974"}
ML = {"gemini-2.5-flash": "Gemini-2.5-flash", "deepseek-chat": "DeepSeek-chat",
      "llama-3.3-70B": "Llama-3.3-70B", "llama-3.1-8B": "Llama-3.1-8B",
      "gpt-4o": "GPT-4o", "gpt-4o-mini": "GPT-4o-mini"}


def fig1_concordance():
    """F1 — task competence & decision stability. Source: corrected-panel concordance
    (unique-answer cases) + TOST equivalence counts."""
    # ref_concordance, demographic_concordance (%)
    ref = {"gemini-2.5-flash": 81.7, "deepseek-chat": 90.7, "llama-3.3-70B": 75.9, "llama-3.1-8B": 49.5, "gpt-4o": 89.7, "gpt-4o-mini": 55.6}
    dem = {"gemini-2.5-flash": 82.8, "deepseek-chat": 90.6, "llama-3.3-70B": 75.5, "llama-3.1-8B": 49.0, "gpt-4o": 88.7, "gpt-4o-mini": 56.4}
    n_ref = {"gemini-2.5-flash": 590, "deepseek-chat": 601, "llama-3.3-70B": 598, "llama-3.1-8B": 570, "gpt-4o": 603, "gpt-4o-mini": 585}
    n_dem = {"gemini-2.5-flash": 17119, "deepseek-chat": 17425, "llama-3.3-70B": 17311, "llama-3.1-8B": 16635, "gpt-4o": 17437, "gpt-4o-mini": 17022}
    tost = {"gemini-2.5-flash": "14/29", "deepseek-chat": "27/29", "llama-3.3-70B": "29/29", "llama-3.1-8B": "29/29", "gpt-4o": "29/29", "gpt-4o-mini": "26/29"}

    def _ci(rate, n):  # (minus, plus) in pp for yerr
        lo, hi = wilson_ci(round(rate/100*n), n)
        return rate - 100*lo, 100*hi - rate

    x = np.arange(len(MODELS)); w = 0.36
    fig, ax = plt.subplots(figsize=(8, 5))
    err_ref = np.array([_ci(ref[m], n_ref[m]) for m in MODELS]).T
    err_dem = np.array([_ci(dem[m], n_dem[m]) for m in MODELS]).T
    ekw = dict(ecolor="0.3", lw=1.0, capsize=3)
    ax.bar(x - w/2, [ref[m] for m in MODELS], w, yerr=err_ref, error_kw=ekw,
           label="No-demographics (reference)",
           color=[MC[m] for m in MODELS], alpha=0.55, edgecolor="k", linewidth=0.6)
    ax.bar(x + w/2, [dem[m] for m in MODELS], w, yerr=err_dem, error_kw=ekw,
           label="With demographics",
           color=[MC[m] for m in MODELS], alpha=1.0, edgecolor="k", linewidth=0.6)
    for i, m in enumerate(MODELS):
        d = dem[m] - ref[m]
        ax.text(i, max(ref[m], dem[m]) + 4.5, f"Δ={d:+.1f} pp\nTOST {tost[m]} equiv.",
                ha="center", va="bottom", fontsize=10)
    ax.set_xticks(x); ax.set_xticklabels([ML[m] for m in MODELS])
    ax.set_ylabel("Concordance with NCCN guideline label (%)")
    ax.set_ylim(0, 105)
    ax.set_title("NCCN concordance by model", fontsize=14, fontweight="bold")
    ax.legend(loc="lower right", fontsize=10, framealpha=0.9)
    fig.savefig(OUT / "fig1_concordance.png"); plt.close(fig)
    print("wrote", OUT / "fig1_concordance.png")


def fig2_soft_split():
    """F2 — the money figure. Appropriate (warranted SDOH care) vs Stigmatizing net%.
    Source: corrected-panel soft-split (FATAL-2), net% vs no-demographics reference."""
    # (variant_label, appropriate net%, stigmatizing net%) per model
    variants = ["uninsured", "underinsured", "low income", "unhoused",
                "black+medicaid", "race-only", "white-male ctrl"]
    data = {
        "gemini-2.5-flash": dict(appr=[88.9, 93.2, 87.5, 65.7, 37.6, -1.8, 1.0],
                                 stig=[9.6, 19.0, 39.5, 71.1, 12.9, 2.7, 0.6]),
        "deepseek-chat":    dict(appr=[84.5, 86.0, 73.0, 74.5, 9.8, -1.8, -1.9],
                                 stig=[3.7, 9.8, 7.9, 78.9, 6.3, 0.6, -0.6]),
        "llama-3.3-70B":    dict(appr=[51.6, 76.1, 58.9, 28.4, -0.2, -0.4, -2.4],
                                 stig=[0.6, 1.8, 11.5, 40.2, 0.9, -0.3, -0.1]),
        "llama-3.1-8B":     dict(appr=[32.1, 27.3, 21.4, 7.4, 11.9, -2.7, -0.5],
                                 stig=[6.9, 7.6, 8.6, 25.1, 5.1, 4.3, 2.9]),
        "gpt-4o":           dict(appr=[60.4, 62.8, 49.2, -6.4, 1.0, -3.0, 1.0],
                                 stig=[5.3, 11.2, 32.3, 52.4, 0.8, 0.3, 0.2]),
        "gpt-4o-mini":      dict(appr=[3.2, 1.8, 5.9, 0.2, 0.4, 0.1, 0.0],
                                 stig=[0.5, 0.4, 1.2, 2.0, 0.2, 0.1, 0.0]),
    }
    fig, axes = plt.subplots(1, len(MODELS), figsize=(4.6 * len(MODELS), 5), sharey=True)
    y = np.arange(len(variants)); h = 0.38
    for ax, m in zip(axes, MODELS):
        ax.barh(y + h/2, data[m]["appr"], h, color="#7FB3D5", edgecolor="k",
                linewidth=0.5, label="Appropriate SDOH care")
        ax.barh(y - h/2, data[m]["stig"], h, color="#C0392B", edgecolor="k",
                linewidth=0.5, label="Stigmatizing")
        ax.axvline(0, color="k", lw=0.8)
        ax.set_title(ML[m], color=MC[m], fontweight="bold")
        ax.set_xlabel("Net % vs. no-demographics")
        ax.set_yticks(y); ax.set_yticklabels(variants)
        ax.invert_yaxis()
    axes[0].legend(loc="lower right", fontsize=9, framealpha=0.9)
    fig.suptitle("The naive 'soft bias' is MOSTLY appropriate care (blue); the real bias "
                 "is a smaller,\nseparable STIGMATIZING layer (red) concentrated on the "
                 "most disadvantaged", fontsize=12, fontweight="bold", y=1.06)
    fig.tight_layout(rect=(0, 0, 1, 0.98))
    fig.savefig(OUT / "fig2_soft_split.png"); plt.close(fig)
    print("wrote", OUT / "fig2_soft_split.png")


def fig3_stigma_gradient():
    """F3 — stigma dose-response gradient + cross-vendor robustness.
    Source: results/analysis/panel_stigma_rates.csv (judge-adjudicated composite:
    adherence-doubt OR hallucinated SDOH)."""
    df = pd.read_csv("results/analysis/panel_stigma_rates.csv")
    order = ["control", "race_only", "uninsured", "underinsured", "low_income",
             "black_unhoused", "unhoused"]
    nice = {"control": "white-male\ncontrol", "race_only": "race-only",
            "uninsured": "uninsured", "underinsured": "underinsured",
            "low_income": "low income", "black_unhoused": "Black +\nunhoused",
            "unhoused": "unhoused"}
    x = np.arange(len(order)); w = 0.8 / len(MODELS)
    fig, ax = plt.subplots(figsize=(13, 5.5))
    for j, m in enumerate(MODELS):
        sub = df[df.model == m].set_index("stratum")
        rates = [sub.loc[s, "rate"] * 100 for s in order]
        lo = [(sub.loc[s, "rate"] - sub.loc[s, "ci_low"]) * 100 for s in order]
        hi = [(sub.loc[s, "ci_high"] - sub.loc[s, "rate"]) * 100 for s in order]
        ax.bar(x + (j - (len(MODELS)-1)/2)*w, rates, w, yerr=[lo, hi], capsize=2, color=MC[m],
               edgecolor="k", linewidth=0.5, label=ML[m])
    ax.axvspan(-0.5, 1.5, color="0.9", zorder=0)
    ax.text(0.5, ax.get_ylim()[1]*0.92, "controls ≈ 0", ha="center", fontsize=10,
            style="italic", color="0.3")
    ax.set_xticks(x); ax.set_xticklabels([nice[s] for s in order])
    ax.set_ylabel("Stigmatizing-language rate (%)")
    ax.set_title("Stigma scales with socioeconomic disadvantage — and is ~0 for race "
                 "alone and\nthe white-male control. Direction-consistent across six "
                 "models.", fontsize=12, fontweight="bold")
    ax.legend(fontsize=10, framealpha=0.9)
    fig.savefig(OUT / "fig3_stigma_gradient.png"); plt.close(fig)
    print("wrote", OUT / "fig3_stigma_gradient.png")


def fig4_circularity():
    """F4 — circularity control (C2). Stigma replicates on LLM-free deterministic
    template notes. Source: project memory C2 result (same 100 cases)."""
    groups = ["unhoused", "Black+unhoused", "race-only", "control"]
    # (LLM-note %, template-note %) per model
    ds = dict(llm=[80, 83, 1, 0], tmpl=[92, 92, 1, 0])
    gm = dict(llm=[76, 69, 2, 0], tmpl=[84, 79, 2, 0])
    x = np.arange(len(groups)); w = 0.2
    fig, ax = plt.subplots(figsize=(9.5, 5))
    ax.bar(x - 1.5*w, gm["llm"], w, color="#4C72B0", alpha=0.55, edgecolor="k",
           linewidth=0.5, label="Gemini · LLM note")
    ax.bar(x - 0.5*w, gm["tmpl"], w, color="#4C72B0", edgecolor="k", linewidth=0.5,
           label="Gemini · template note")
    ax.bar(x + 0.5*w, ds["llm"], w, color="#C44E52", alpha=0.55, edgecolor="k",
           linewidth=0.5, label="DeepSeek · LLM note")
    ax.bar(x + 1.5*w, ds["tmpl"], w, color="#C44E52", edgecolor="k", linewidth=0.5,
           label="DeepSeek · template note")
    ax.set_xticks(x); ax.set_xticklabels(groups)
    ax.set_ylabel("Stigmatizing-language rate (%)")
    ax.set_title("Circularity ruled out: stigma REPLICATES on demographics-neutral,\n"
                 "LLM-free deterministic template notes (slightly higher on terser notes)",
                 fontsize=12, fontweight="bold")
    ax.legend(fontsize=9, ncol=2, framealpha=0.9)
    fig.savefig(OUT / "fig4_circularity.png"); plt.close(fig)
    print("wrote", OUT / "fig4_circularity.png")


def figS1_judge_validation():
    """S1 — judge/classifier validation. Source: score_gold.py on 35-item gold set."""
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5), gridspec_kw={"width_ratios": [1, 1.1]})
    # left: agreement + kappa
    comps = ["Human vs\nJudge (Sonnet)", "Human vs\nRegex"]
    agree = [71, 51]; kappa = [0.30, 0.21]
    xb = np.arange(len(comps))
    a1.bar(xb, agree, 0.5, color=["#2E86C1", "#B03A2E"], edgecolor="k", linewidth=0.6)
    for i, (ag, k) in enumerate(zip(agree, kappa)):
        a1.text(i, ag + 1.5, f"{ag}%\nκ={k:.2f}", ha="center", fontsize=11)
    a1.set_xticks(xb); a1.set_xticklabels(comps)
    a1.set_ylabel("Agreement (%)"); a1.set_ylim(0, 100)
    a1.set_title("Agreement with human", fontsize=11, fontweight="bold")
    # right: contested cases
    a2.bar(["sided with\nJudge", "sided with\nRegex"], [12, 5], 0.5,
           color=["#2E86C1", "#B03A2E"], edgecolor="k", linewidth=0.6)
    a2.text(0, 12.3, "12", ha="center", fontsize=12); a2.text(1, 5.3, "5", ha="center", fontsize=12)
    a2.set_ylabel("Contested items (n=17)"); a2.set_ylim(0, 15)
    a2.set_title("Contested cases (regex over-counts)", fontsize=11, fontweight="bold")
    fig.suptitle("Judge validation", fontsize=13, fontweight="bold")
    fig.savefig(OUT / "figS1_judge_validation.png"); plt.close(fig)
    print("wrote", OUT / "figS1_judge_validation.png")


if __name__ == "__main__":
    fig1_concordance()
    fig2_soft_split()
    fig3_stigma_gradient()
    fig4_circularity()
    figS1_judge_validation()
    print("\nAll manuscript figures written to", OUT)
