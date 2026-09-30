"""Detailed Figure 2 — stigma decomposed into its component behaviors.

For each demographic label, breaks the net stigmatizing signal into the four
classifier dimensions so you can see WHICH stigma behavior fires. Net% per dim =
100 * (#cases variant-adds-dim  -  #cases variant-drops-dim) / n, vs the
no-demographics reference. Faceted by model.

Core stigma composite note (see project memory): adherence_compliance +
sdoh_generation are the core stigma dims; prognosis_framing fires broadly
(ordinary clinical caution); watchful_waiting ~0.

Recomputes from raw results. Output -> figures/manuscript/FigS09_stigma_breakdown_original.png
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
    ("white_male_private", "White male, private"),
    ("black_race_only", "Black"),
    ("black_female_medicaid", "Black female, Medicaid"),
    ("uninsured_only", "Uninsured"),
    ("underinsured_only", "Underinsured"),
    ("low_income_patient", "Low income"),
    ("unhoused_patient", "Unhoused"),
]
# stigma dimensions -> (key, label, color, hatch).  * = core stigma composite dim.
# CVD-safe + grayscale-separable: the two core (starred) dims are warm, the two
# broad/benign dims are cool, and each segment carries a distinct hatch so colour is not
# the sole encoder in the stacked bars (council: dataviz BLOCKER).
DIMS = [
    ("adherence_compliance", "Adherence doubt *", "#8E1B1B", ""),
    ("sdoh_generation",      "Invented SDOH *", "#E69F00", "///"),
    ("prognosis_framing",    "Prognosis framing", "#4C72B0", ".."),
    ("watchful_waiting",     "Watchful waiting", "#55A868", "xx"),
]


def net_by_dim(raw):
    """{variant_key: {dim: net_pct}} vs reference."""
    out = {}
    for vkey, _ in VARIANTS:
        acc = {d: 0 for d, _, _, _ in DIMS}
        n = 0
        for cid, cd in raw.items():
            rt = cd.get(REFERENCE, {}).get("response_text", "")
            vt = cd.get(vkey, {}).get("response_text", "")
            if not rt or not vt:
                continue
            n += 1
            asym = detect_asymmetry(rt, vt)
            for d, _, _, _ in DIMS:
                acc[d] += asym.get(d, 0)
        out[vkey] = {d: (100 * acc[d] / n if n else 0) for d, _, _, _ in DIMS}
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
    gmax = max(sum(max(0, data[nm][vk][d]) for d, _, _, _ in DIMS)
               for nm in names for vk, _ in VARIANTS)
    # eFigure 6: per-model companion to Figure 4B, 2 x 3 grid, rows as in Figure 4A/B
    vorder = list(reversed(VARIANTS))              # most disadvantaged on top
    y = np.arange(len(vorder))
    neg = []
    with plt.rc_context({"font.family": "sans-serif",
                         "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"]}):
        fig, axes = plt.subplots(2, 3, figsize=(10.0, 7.6), sharey=True, sharex=True)
        for ax, name in zip(axes.flat, names):
            left = np.zeros(len(vorder))
            for d, dlabel, color, hatch in DIMS:
                raw_vals = [data[name][vk][d] for vk, _ in vorder]
                neg += [(name, vk, d, v) for (vk, _), v in zip(vorder, raw_vals) if v < 0]
                vals = np.array([max(0, v) for v in raw_vals])
                ax.barh(y, vals, left=left, color=color, edgecolor="k", linewidth=0.4,
                        hatch=hatch, label=dlabel)
                left += vals
            ax.set_title(name, fontsize=12.5, fontweight="bold")
            ax.set_yticks(y); ax.set_yticklabels([lbl for _, lbl in vorder], fontsize=11)
            ax.tick_params(axis="x", labelsize=10.5); ax.tick_params(axis="y", length=0)
            ax.set_xlim(0, gmax * 1.05)
            ax.xaxis.grid(True, ls=":", alpha=0.5); ax.set_axisbelow(True)
            for sp in ("top", "right"):
                ax.spines[sp].set_visible(False)
        axes[0, 0].invert_yaxis()
        for ax in axes[1]:
            ax.set_xlabel("Net % of cases vs reference,\nsummed across dimensions", fontsize=11)
        h, l = axes[0, 0].get_legend_handles_labels()
        fig.legend(h, l, loc="lower center", ncol=4, fontsize=11, frameon=False,
                   bbox_to_anchor=(0.5, -0.045))
        fig.tight_layout(h_pad=1.6)
        fig.savefig(OUT / "FigS09_stigma_breakdown_original.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("wrote", OUT / "FigS09_stigma_breakdown_original.png")
    print(f"negative net values shown as 0: {len(neg)}; most negative:",
          sorted(neg, key=lambda t: t[3])[:3])
    tot = {nm: {lbl: round(sum(max(0, data[nm][vk][d]) for d, _, _, _ in DIMS), 1)
                for vk, lbl in VARIANTS} for nm in names}
    for nm in names:
        print(" ", nm, tot[nm])

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
    tot = np.array([[sum(max(0, data[m][vk][d]) for d, _, _, _ in DIMS) for vk in vkeys]
                    for m in names])               # (model, variant)

    fig, ax = plt.subplots(figsize=(9.5, 5.8))
    left = np.zeros(len(vkeys))
    for d, dlabel, color, hatch in DIMS:
        vals = np.array([np.mean([max(0, data[m][vk][d]) for m in names]) for vk in vkeys])
        ax.barh(y, vals, left=left, color=color, edgecolor="k", linewidth=0.4,
                hatch=hatch, label=dlabel, zorder=1)
        left += vals
    offs = np.linspace(-0.28, 0.28, n)
    for i in range(n):
        ax.scatter(tot[i], y + offs[i], s=15, color="#222", edgecolor="white",
                   linewidth=0.3, zorder=3)
    ax.set_yticks(y); ax.set_yticklabels(vlabs, fontsize=13)
    ax.invert_yaxis()
    ax.tick_params(axis="x", labelsize=12)
    ax.set_xlabel("Net % of cases vs reference, summed across dimensions", fontsize=13)
    dot_proxy = mlines.Line2D([], [], color="#222", marker="o", linestyle="none",
                              markersize=5, markeredgecolor="white", label=f"Per-model total (n={n})")
    handles, _ = ax.get_legend_handles_labels()
    ax.legend(handles=handles + [dot_proxy], loc="lower right", fontsize=11,
              title_fontsize=12, markerscale=1.3, framealpha=0.95, title="Stigma dimension")

    # titleless panel for combine_figures.py -> Figure4 panel B (banner headline -> caption)
    PANELS = Path("figures/manuscript_combined/panels"); PANELS.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(PANELS / "p_stigma_breakdown_avg.png", dpi=200, bbox_inches="tight", facecolor="white")
    print("wrote", PANELS / "p_stigma_breakdown_avg.png")

    ax.set_title("Stigma decomposed by behavior, averaged across models\n"
                 "(* = core stigma composite: adherence doubt + invented SDOH)",
                 fontsize=12, fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUT / "FigS04_stigma_breakdown_avg.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("wrote", OUT / "FigS04_stigma_breakdown_avg.png")


if __name__ == "__main__":
    main()
