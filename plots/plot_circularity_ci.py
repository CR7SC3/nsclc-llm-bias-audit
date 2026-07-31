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
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans"],
    "font.size": 10,
})

OUT = Path("figures/manuscript"); OUT.mkdir(parents=True, exist_ok=True)
STIGMA = ("adherence_compliance", "sdoh_generation")  # defensible composite
GROUPS = [("unhoused_patient", "unhoused"), ("black_unhoused", "Black+unhoused"),
          ("black_race_only", "race-only"), ("white_male_private", "control")]
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
        print(model, "n cases:", data[model]["unhoused"]["tmpl"][3])

    glabels = [g for _, g in GROUPS]
    x = np.arange(len(glabels)); w = 0.2
    fig, ax = plt.subplots(figsize=(9.8, 5.2))
    # note-type by colour (teal = synthetic LLM note, purple = template/circularity
    # control); vendor by hatch (Gemini solid, DeepSeek hatched)
    # shared gray baseline (original LLM note) + Fig 5A claim color (light blue = template note)
    C_MAIN, C_ALT = "#adadad", "#E69F00"   # grey = original note · orange = robustness condition (non-model palette)
    specs = [("Gemini", "llm", C_MAIN, "", "Gemini · LLM note", -1.5),
             ("Gemini", "tmpl", C_ALT, "", "Gemini · template note", -0.5),
             ("DeepSeek", "llm", C_MAIN, "////", "DeepSeek · LLM note", 0.5),
             ("DeepSeek", "tmpl", C_ALT, "////", "DeepSeek · template note", 1.5)]
    for model, nt, color, hatch, label, off in specs:
        rates = [data[model][g][nt][0] for g in glabels]
        lo = np.clip([data[model][g][nt][0] - data[model][g][nt][1] for g in glabels], 0, None)
        hi = np.clip([data[model][g][nt][2] - data[model][g][nt][0] for g in glabels], 0, None)
        ax.bar(x + off * w, rates, w, yerr=[lo, hi],
               error_kw=dict(ecolor="0.3", lw=0.9, capsize=2),
               color=color, hatch=hatch, edgecolor="k", linewidth=0.5, label=label)
    ax.set_xticks(x); ax.set_xticklabels(glabels, rotation=30, ha="right", rotation_mode="anchor")   # standardized 30° tilt
    ax.set_ylabel("Stigmatizing-language rate (%)")
    ax.set_ylim(0, 125)   # headroom so the legend clears the ~92% bars
    ax.set_yticks(range(0, 101, 20))
    ax.grid(axis="y", alpha=0.25); ax.set_axisbelow(True)   # grey 20% gridlines (match panel C)
    ax.legend(ncol=2, framealpha=0.95, loc="upper center",
              columnspacing=1.2, handletextpad=0.5, handlelength=1.6, borderaxespad=0.4)
    # titleless panel for combine_figures.py (Fig 5A); banner goes to the caption.
    # Fixed geometry so all Fig-5 panels share one height and their x-axes align
    # (single-axis box). No tight bbox — the axes rectangle is what fixes alignment.
    PANELS = Path("figures/manuscript_combined/panels"); PANELS.mkdir(parents=True, exist_ok=True)
    fig.set_size_inches(6.6, 5.2)
    ax.set_position([0.10, 0.16, 0.87, 0.78])
    fig.savefig(PANELS / "p_template.png", dpi=200)
    # restore layout for the standalone banner figure
    fig.set_size_inches(9.8, 5.2)
    ax.set_title("Circularity ruled out: stigma REPLICATES on demographics-neutral,\n"
                 "LLM-free deterministic template notes (95% Wilson CI; same 100 cases)",
                 fontsize=12, fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUT / "fig4_circularity.png", dpi=150, bbox_inches="tight")
    print("wrote", OUT / "fig4_circularity.png")


if __name__ == "__main__":
    main()
