"""F4 (circularity control) with 95% Wilson CIs, recomputed from data.

Compares the stigma rate (defensible composite: adherence-doubt OR hallucinated
SDOH) on LLM-generated notes vs. LLM-free deterministic template notes, on the
SAME 100 cases, for Gemini and DeepSeek. Error bars = 95% Wilson CI.

Output -> figures/manuscript/fig4_circularity.png
Run:  python3 plots/plot_circularity_ci.py
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import json
import numpy as np
import matplotlib.pyplot as plt

from src.analyze.soft_bias import detect_all
from src.analyze.stats import wilson_ci

# Unified typography across all Fig-5 panels (A/B/C/D): one family, one size.
# eFigure 2 panels share one font, one size and one panel geometry (8.0 x 4.8 in)
# so the 2 x 2 composite prints near 6 pt at journal width.
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 14,
})

OUT = Path("figures/manuscript"); OUT.mkdir(parents=True, exist_ok=True)
STIGMA = ("adherence_compliance", "sdoh_generation")  # defensible composite
# ordered by increasing disadvantage, as in panels B to D
GROUPS = [("white_male_private", "White male, private"), ("black_race_only", "Black"),
          ("black_unhoused", "Black + unhoused"), ("unhoused_patient", "Unhoused")]
FILES = {
    "Gemini": {"llm": "results/baseline/v2_genie_bpc_nsclc_results.json",
               "tmpl": "results/baseline/v2_genie_bpc_nsclc_templates100_results.json"},
    "DeepSeek": {"llm": "results/baseline/v2_genie_bpc_nsclc_deepseek-chat_results.json",
                 "tmpl": "results/baseline/v2_genie_bpc_nsclc_templates100_deepseek-chat_results.json"},
}


def stigma_rate(raw, ids, vkey):
    k = n = 0
    for cid in ids:
        txt = raw.get(cid, {}).get(vkey, {}).get("response_text", "")
        if not txt:
            continue
        n += 1
        f = detect_all(txt)
        if any(f.get(d) for d in STIGMA):
            k += 1
    lo, hi = wilson_ci(k, n) if n else (0, 0)
    return 100 * k / n if n else 0, 100 * lo, 100 * hi, n


def main():
    # 100-case set = template cases (shared across models)
    ids = list(json.loads(Path(FILES["DeepSeek"]["tmpl"]).read_text()).keys())
    data = {}
    for model, paths in FILES.items():
        llm = json.loads(Path(paths["llm"]).read_text())
        tmpl = json.loads(Path(paths["tmpl"]).read_text())
        data[model] = {}
        for vkey, glabel in GROUPS:
            data[model][glabel] = {
                "llm": stigma_rate(llm, ids, vkey),
                "tmpl": stigma_rate(tmpl, ids, vkey),
            }
        print(model, "n cases:", data[model]["Unhoused"]["tmpl"][3])

    glabels = [g for _, g in GROUPS]
    x = np.arange(len(glabels)); w = 0.38
    C_MAIN, C_ALT = "#adadad", "#E69F00"   # grey = original condition, orange = alternative
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 4.8), sharey=True)
    for ax, (model, full) in zip(axes, [("Gemini", "Gemini-2.5-flash"), ("DeepSeek", "DeepSeek-chat")]):
        for nt, color, label, off in [("llm", C_MAIN, "LLM-generated note", -0.5),
                                      ("tmpl", C_ALT, "Template note (no LLM)", 0.5)]:
            r = [data[model][g][nt] for g in glabels]
            ax.bar(x + off * w, [v[0] for v in r], w,
                   yerr=[np.clip([v[0] - v[1] for v in r], 0, None),
                         np.clip([v[2] - v[0] for v in r], 0, None)],
                   error_kw=dict(ecolor="0.3", lw=0.9, capsize=2),
                   color=color, edgecolor="k", linewidth=0.5, label=label)
        ax.set_title(full, fontsize=14, fontweight="bold")
        ax.set_xticks(x); ax.set_xticklabels([g.replace(" + ", " +\n") for g in glabels], rotation=40, ha="right", rotation_mode="anchor", fontsize=12)
        ax.set_ylim(0, 118); ax.set_yticks(range(0, 101, 20))   # headroom for the legend
        ax.grid(axis="y", alpha=0.25); ax.set_axisbelow(True)
    axes[0].set_ylabel("Stigmatizing-language rate (%)")
    axes[0].legend(framealpha=0.95, loc="upper left", fontsize=11)
    axes[0].set_position([0.105, 0.26, 0.41, 0.64])
    axes[1].set_position([0.575, 0.26, 0.41, 0.64])
    PANELS = Path("figures/manuscript_combined/panels"); PANELS.mkdir(parents=True, exist_ok=True)
    fig.savefig(PANELS / "p_template.png", dpi=200)
    fig.savefig(OUT / "fig4_circularity.png", dpi=150)
    print("wrote", OUT / "fig4_circularity.png")


if __name__ == "__main__":
    main()
