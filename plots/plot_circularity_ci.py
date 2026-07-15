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
    TEAL, PURPLE = "#2CA6A4", "#8E6CAE"
    specs = [("Gemini", "llm", TEAL, "", "Gemini · LLM note", -1.5),
             ("Gemini", "tmpl", PURPLE, "", "Gemini · template note", -0.5),
             ("DeepSeek", "llm", TEAL, "////", "DeepSeek · LLM note", 0.5),
             ("DeepSeek", "tmpl", PURPLE, "////", "DeepSeek · template note", 1.5)]
    for model, nt, color, hatch, label, off in specs:
        rates = [data[model][g][nt][0] for g in glabels]
        lo = np.clip([data[model][g][nt][0] - data[model][g][nt][1] for g in glabels], 0, None)
        hi = np.clip([data[model][g][nt][2] - data[model][g][nt][0] for g in glabels], 0, None)
        ax.bar(x + off * w, rates, w, yerr=[lo, hi],
               error_kw=dict(ecolor="0.3", lw=0.9, capsize=2),
               color=color, hatch=hatch, edgecolor="k", linewidth=0.5, label=label)
    ax.set_xticks(x); ax.set_xticklabels(glabels)
    ax.set_ylabel("Stigmatizing-language rate (%)")
    ax.set_title("Circularity ruled out: stigma REPLICATES on demographics-neutral,\n"
                 "LLM-free deterministic template notes (95% Wilson CI; same 100 cases)",
                 fontsize=12, fontweight="bold")
    ax.legend(fontsize=9, ncol=2, framealpha=0.95)
    fig.savefig(OUT / "fig4_circularity.png", dpi=150, bbox_inches="tight")
    print("wrote", OUT / "fig4_circularity.png")


if __name__ == "__main__":
    main()
