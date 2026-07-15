"""Detailed Figure 2 — stigma decomposed into its component behaviors.

For each demographic label, breaks the net stigmatizing signal into the four
classifier dimensions so you can see WHICH stigma behavior fires. Net% per dim =
100 * (#cases variant-adds-dim  -  #cases variant-drops-dim) / n, vs the
no-demographics reference. Faceted by model.

Defensible-composite note (see project memory): adherence_compliance +
sdoh_generation are the defensible stigma dims; prognosis_framing fires broadly
(ordinary clinical caution); watchful_waiting ~0.

Recomputes from raw results. Output -> figures/manuscript/fig2_stigma_breakdown.png
Run:  python3 plots/plot_stigma_breakdown.py
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

from src.analyze.soft_bias import detect_asymmetry

OUT = Path("figures/manuscript"); OUT.mkdir(parents=True, exist_ok=True)
REFERENCE = "no_demographics"
MODELS = {
    "Gemini-2.5-flash": "results/baseline/v2_genie_bpc_nsclc_results.json",
    "DeepSeek-chat":    "results/baseline/v2_genie_bpc_nsclc_deepseek-chat_results.json",
    "Llama-3.3-70B":    "results/baseline/v2_genie_bpc_nsclc_meta-llama-Llama-3.3-70B-Instruct-Turbo_results.json",
    "Llama-3.1-8B":     "results/baseline/v2_genie_bpc_nsclc_openrouter-meta-llama-llama-3.1-8b-instruct_results.json",
    "GPT-4o":           "results/baseline/v2_genie_bpc_nsclc_gpt-4o_results.json",
    "GPT-4o-mini":      "results/baseline/v2_genie_bpc_nsclc_gpt-4o-mini_results.json",
}
# variant key -> display label, ordered by disadvantage
VARIANTS = [
    ("white_male_private", "white-male ctrl"),
    ("black_race_only", "race-only"),
    ("black_female_medicaid", "Black + medicaid"),
    ("uninsured_only", "uninsured"),
    ("underinsured_only", "underinsured"),
    ("low_income_patient", "low income"),
    ("unhoused_patient", "unhoused"),
]
# stigma dimensions -> (label, color).  * = defensible-composite dim
DIMS = [
    ("adherence_compliance", "Adherence doubt *", "#8E1B1B"),
    ("sdoh_generation",      "Hallucinated SDOH *", "#D65C5C"),
    ("prognosis_framing",    "Prognosis framing", "#E8A87C"),
    ("watchful_waiting",     "Watchful waiting", "#C9B79C"),
]


def net_by_dim(raw):
    """{variant_key: {dim: net_pct}} vs reference."""
    out = {}
    for vkey, _ in VARIANTS:
        acc = {d: 0 for d, _, _ in DIMS}
        n = 0
        for cid, cd in raw.items():
            rt = cd.get(REFERENCE, {}).get("response_text", "")
            vt = cd.get(vkey, {}).get("response_text", "")
            if not rt or not vt:
                continue
            n += 1
            asym = detect_asymmetry(rt, vt)
            for d, _, _ in DIMS:
                acc[d] += asym.get(d, 0)
        out[vkey] = {d: (100 * acc[d] / n if n else 0) for d, _, _ in DIMS}
    return out


def main():
    data = {}
    for name, path in MODELS.items():
        if not Path(path).exists():
            print("skip", name); continue
        raw = json.loads(Path(path).read_text())
        data[name] = net_by_dim(raw)
        print(f"computed {name}")

    names = list(data.keys())
    # global max (summed across dims) for a shared, fair x-axis
    gmax = max(sum(max(0, data[nm][vk][d]) for d, _, _ in DIMS)
               for nm in names for vk, _ in VARIANTS)
    fig, axes = plt.subplots(1, len(names), figsize=(5.4 * len(names), 5.6),
                             sharey=True, sharex=True)
    if len(names) == 1:
        axes = [axes]
    y = np.arange(len(VARIANTS))
    for ax, name in zip(axes, names):
        left = np.zeros(len(VARIANTS))
        for d, dlabel, color in DIMS:
            vals = np.array([max(0, data[name][vk][d]) for vk, _ in VARIANTS])
            ax.barh(y, vals, left=left, color=color, edgecolor="k", linewidth=0.3,
                    label=dlabel)
            left += vals
        ax.set_title(name, fontweight="bold")
        ax.set_xlabel("Net % of cases, summed across dimensions")
        ax.set_yticks(y); ax.set_yticklabels([lbl for _, lbl in VARIANTS])
        ax.invert_yaxis()
        ax.set_xlim(0, gmax * 1.05)
    axes[0].legend(loc="lower right", fontsize=9, framealpha=0.95, title="Stigma dimension")
    fig.suptitle("Stigma decomposed by behavior (* = defensible composite: "
                 "adherence-doubt + hallucinated SDOH)", fontsize=13, fontweight="bold", y=1.02)
    fig.tight_layout(rect=(0, 0, 1, 0.99))
    fig.savefig(OUT / "fig2_stigma_breakdown.png", dpi=150, bbox_inches="tight")
    print("wrote", OUT / "fig2_stigma_breakdown.png")

    render_avg(data)


def render_avg(data):
    """Averaged-across-models supplement (single panel): stacked MEAN net% by
    stigma dimension per demographic label, with each model's per-label TOTAL
    (summed over dimensions) overlaid as a dot. No confidence interval: with only
    six models the model -- not the case -- is the replication unit, so we show the
    per-model spread directly rather than a pooled CI that would understate it (a
    per-model panel version is the main Fig 8)."""
    names = list(data)
    n = len(names)
    vorder = list(reversed(VARIANTS))              # most disadvantaged on top
    vkeys = [k for k, _ in vorder]
    vlabs = [l for _, l in vorder]
    y = np.arange(len(vkeys))

    # mean stacked composition + per-model total (sum of positive dims)
    tot = np.array([[sum(max(0, data[m][vk][d]) for d, _, _ in DIMS) for vk in vkeys]
                    for m in names])               # (model, variant)

    fig, ax = plt.subplots(figsize=(9.5, 5.8))
    left = np.zeros(len(vkeys))
    for d, dlabel, color in DIMS:
        vals = np.array([np.mean([max(0, data[m][vk][d]) for m in names]) for vk in vkeys])
        ax.barh(y, vals, left=left, color=color, edgecolor="k", linewidth=0.4,
                label=dlabel, zorder=1)
        left += vals
    offs = np.linspace(-0.28, 0.28, n)
    for i in range(n):
        ax.scatter(tot[i], y + offs[i], s=15, color="#222", edgecolor="white",
                   linewidth=0.3, zorder=3)
    ax.set_yticks(y); ax.set_yticklabels(vlabs, fontsize=9.5)
    ax.invert_yaxis()
    ax.set_xlabel("Net % of cases, summed across dimensions  "
                  "(stacked bar = mean of 6 models; dots = per-model total; no CI)",
                  fontsize=8.5)
    ax.set_title("Stigma decomposed by behavior, averaged across models\n"
                 "(* = defensible composite: adherence-doubt + hallucinated SDOH)",
                 fontsize=12, fontweight="bold")
    dot_proxy = mlines.Line2D([], [], color="#222", marker="o", linestyle="none",
                              markersize=5, markeredgecolor="white", label=f"Per-model total (n={n})")
    handles, _ = ax.get_legend_handles_labels()
    ax.legend(handles=handles + [dot_proxy], loc="lower right", fontsize=8,
              framealpha=0.95, title="Stigma dimension")
    fig.tight_layout()
    fig.savefig(OUT / "FigS_stigma_breakdown_avg.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("wrote", OUT / "FigS_stigma_breakdown_avg.png")


if __name__ == "__main__":
    main()
