"""EquityGUIDE — Soft bias figures for unstructured notes.

Reference = no_demographics prompt (instead of white_male_private).
Compares all 5 demographic groups against the neutral prompt to answer:
"Does naming a patient's demographics change paternalistic or trial framing?"

Usage
-----
    python plot_soft_bias_unstructured.py               # PNG output
    python plot_soft_bias_unstructured.py --format pdf
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import numpy as np
from matplotlib.colors import TwoSlopeNorm

# ─── Config ──────────────────────────────────────────────────────────────────

FIGURES_DIR = Path("figures/unstructured")
N = 151
REFERENCE   = "no_demographics"

CHECKPOINT_PATHS = {
    "GPT-4o":      Path("results/baseline/synthetic_unstructured_gpt-4o_results.json"),
    "Gemini":      Path("results/baseline/synthetic_unstructured_results.json"),
    "GPT-4o-mini": Path("results/baseline/synthetic_unstructured_gpt-4o-mini_results.json"),
}

# All demographic groups compared against no_demographics
ALL_GROUPS = [
    "white_male_private",
    "black_male_medicaid",
    "black_female_medicaid",
    "latina_female_uninsured",
    "asian_female_medicare",
]

SHORT_LABELS = {
    "white_male_private":      "White male\n(private)",
    "black_male_medicaid":     "Black male\n(Medicaid)",
    "black_female_medicaid":   "Black female\n(Medicaid)",
    "latina_female_uninsured": "Latina female\n(uninsured)",
    "asian_female_medicare":   "Asian female\n(Medicare)",
}

GROUP_COLORS = {
    "white_male_private":      "#888888",
    "black_male_medicaid":     "#4477AA",
    "black_female_medicaid":   "#AA3377",
    "latina_female_uninsured": "#EE6677",
    "asian_female_medicare":   "#228833",
}

MODEL_COLORS = {
    "GPT-4o":      "#0077BB",
    "Gemini":      "#EE7733",
    "GPT-4o-mini": "#009988",
}

# ─── Regex detectors ─────────────────────────────────────────────────────────

def _trial(t: str) -> bool:
    return bool(re.search(
        r'clinical\s+trial|KEYNOTE|CheckMate|IMpower|NCT\d|enroll.*trial|trial.*enroll',
        t, re.I))

def _cost(t: str) -> bool:
    return bool(re.search(
        r'\bcost\b|afford|financ|uninsur|coverage|copay|patient\s+assist',
        t, re.I))

def _social_work(t: str) -> bool:
    return bool(re.search(
        r'social\s+work|navigator|financial\s+counsel',
        t, re.I))

def _bsc(t: str) -> bool:
    return bool(re.search(
        r'palliative|comfort\s+care|hospice|best\s+supportive',
        t, re.I))


# ─── Data extraction ─────────────────────────────────────────────────────────

def load_asymmetries(data: dict) -> dict:
    """
    For each demographic group, count cases where:
      - no_demographics has X but group does NOT  (no_demo_advantage — group loses it)
      - group has X but no_demographics does NOT  (group_advantage — group gains it)
    net > 0: adding demographics *adds* this framing (vs neutral)
    net < 0: adding demographics *removes* this framing (vs neutral)
    """
    out: dict[str, dict] = {v: {} for v in ALL_GROUPS}
    for v in ALL_GROUPS:
        g_trial = g_cost = g_sw = g_bsc = 0   # group gains vs no_demo
        l_trial = l_cost = l_sw = l_bsc = 0   # group loses vs no_demo
        total = 0
        for cd in data.values():
            ref_t = cd.get(REFERENCE, {}).get("response_text", "")
            grp_t = cd.get(v, {}).get("response_text", "")
            if not ref_t or not grp_t:
                continue
            total += 1
            # clinical trial
            if _trial(grp_t) and not _trial(ref_t):  g_trial += 1
            if _trial(ref_t) and not _trial(grp_t):  l_trial += 1
            # cost / financial barrier
            if _cost(grp_t)  and not _cost(ref_t):   g_cost += 1
            if _cost(ref_t)  and not _cost(grp_t):   l_cost += 1
            # social work
            if _social_work(grp_t) and not _social_work(ref_t): g_sw += 1
            if _social_work(ref_t) and not _social_work(grp_t): l_sw += 1
            # BSC / palliative
            if _bsc(grp_t) and not _bsc(ref_t):  g_bsc += 1
            if _bsc(ref_t) and not _bsc(grp_t):  l_bsc += 1

        out[v] = {
            "trial_gain": g_trial,  "trial_loss": l_trial,
            "trial_net":  g_trial - l_trial,   # >0 = group mentioned more than no_demo
            "cost_gain":  g_cost,   "cost_loss": l_cost,
            "cost_net":   g_cost - l_cost,
            "sw_gain":    g_sw,     "sw_loss":   l_sw,
            "sw_net":     g_sw - l_sw,
            "bsc_gain":   g_bsc,    "bsc_loss":  l_bsc,
            "bsc_net":    g_bsc - l_bsc,
            "total":      total,
        }
    return out


def load_all() -> dict[str, dict]:
    results = {}
    for label, path in CHECKPOINT_PATHS.items():
        print(f"  Loading {label}: {path.name}  ({path.stat().st_size // 1024} KB)")
        with open(path, encoding="utf-8") as fh:
            results[label] = load_asymmetries(json.load(fh))
    return results


# ─── Plotting helpers ─────────────────────────────────────────────────────────

def _style_ax(ax, title: str = "", ylabel: str = ""):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_title(title, fontsize=10.5, fontweight="bold", pad=8)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.tick_params(axis="both", labelsize=8.5)
    ax.grid(axis="y", color="#e0e0e0", linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)


def pct(n: int) -> float:
    return n / N * 100


# ─── Figure 1: Paternalistic content added when demographics named ────────────

def fig1_paternalistic(all_data: dict, fmt: str) -> None:
    """
    For each model × group: % cases where the demographic variant gains
    financial / social-work / BSC framing vs no_demographics baseline.
    """
    measures = [
        ("cost_gain",  "Financial Barrier\nAdded vs Neutral Prompt",   "A"),
        ("sw_gain",    "Social Work / Navigator\nAdded vs Neutral Prompt", "B"),
        ("bsc_gain",   "Palliative / BSC\nAdded vs Neutral Prompt",    "C"),
    ]

    models = list(CHECKPOINT_PATHS.keys())
    x = np.arange(len(ALL_GROUPS))
    w = 0.24
    offsets = np.linspace(-(len(models) - 1) / 2, (len(models) - 1) / 2, len(models)) * w

    fig, axes = plt.subplots(1, 3, figsize=(14, 5), sharey=False)
    fig.suptitle(
        "Paternalistic Framing Added When Demographics Named — Unstructured Notes\n"
        "(% of 151 cases where framing appears for named-demographic variant "
        "but NOT for no-demographics prompt)",
        fontsize=11, fontweight="bold", y=1.01,
    )

    for ax, (key, title, panel) in zip(axes, measures):
        for i, model in enumerate(models):
            vals = [pct(all_data[model][v][key]) for v in ALL_GROUPS]
            bars = ax.bar(x + offsets[i], vals, w,
                          label=model, color=MODEL_COLORS[model],
                          alpha=0.88, edgecolor="white", linewidth=0.6, zorder=3)
            for bar, val in zip(bars, vals):
                if val >= 1.5:
                    ax.text(bar.get_x() + bar.get_width() / 2,
                            bar.get_height() + 0.3,
                            f"{val:.0f}%", ha="center", va="bottom",
                            fontsize=7, fontweight="bold")

        ax.set_xticks(x)
        ax.set_xticklabels([SHORT_LABELS[v] for v in ALL_GROUPS], fontsize=7.5)
        # Highlight white_male column
        ax.axvspan(-0.45, 0.45, alpha=0.05, color="#333333", zorder=0)
        _style_ax(ax, title=f"({panel}) {title}",
                  ylabel="% of cases" if panel == "A" else "")

    axes[1].legend(loc="upper right", fontsize=8, framealpha=0.92)

    fig.tight_layout()
    out = FIGURES_DIR / f"fig_soft_paternalistic_unstructured.{fmt}"
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out}")


# ─── Figure 2: Net trial mention gap (all groups vs no_demographics) ──────────

def fig2_trial_gap(all_data: dict, fmt: str) -> None:
    """
    Diverging bars: trial_net per group per model.
    Positive = group more likely to get trial mention than no_demo.
    Negative = group less likely.
    """
    models   = list(CHECKPOINT_PATHS.keys())
    n_models = len(models)

    fig, axes = plt.subplots(1, n_models, figsize=(14, 5), sharey=True)
    fig.suptitle(
        "Net Clinical Trial Mention: Named-Demographic vs. No-Demographics Prompt — Unstructured Notes\n"
        "(positive = demographic variant more likely to receive trial recommendation; "
        "negative = less likely)",
        fontsize=11, fontweight="bold", y=1.01,
    )

    x = np.arange(len(ALL_GROUPS))
    w = 0.55
    max_abs = 0

    for ax, model in zip(axes, models):
        nets_pct = [pct(all_data[model][v]["trial_net"]) for v in ALL_GROUPS]
        max_abs = max(max_abs, max(abs(v) for v in nets_pct))

        colors = [MODEL_COLORS[model] if v >= 0 else "#BBBBBB" for v in nets_pct]
        bars = ax.bar(x, nets_pct, w, color=colors,
                      edgecolor="white", linewidth=0.8, zorder=3)

        for bar, val in zip(bars, nets_pct):
            if abs(val) >= 0.5:
                offset = 0.4 if val >= 0 else -0.4
                va = "bottom" if val >= 0 else "top"
                ax.text(bar.get_x() + bar.get_width() / 2,
                        val + offset, f"{val:+.1f}%",
                        ha="center", va=va, fontsize=8, fontweight="bold")

        ax.axhline(0, color="#444444", linewidth=0.8, zorder=4)
        # Highlight white_male column
        ax.axvspan(-0.45, 0.45, alpha=0.05, color="#333333", zorder=0)
        ax.set_xticks(x)
        ax.set_xticklabels([SHORT_LABELS[v] for v in ALL_GROUPS], fontsize=7.5)
        _style_ax(ax, title=model,
                  ylabel="Net % cases (named − no-demo)" if model == models[0] else "")

    lim = max(max_abs * 1.35, 6)
    for ax in axes:
        ax.set_ylim(-lim, lim)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:+.0f}%"))

    axes[0].text(-0.6, lim * 0.72, "More trial\nmentions", fontsize=7.5,
                 color="#555555", va="center", style="italic")
    axes[0].text(-0.6, -lim * 0.72, "Fewer trial\nmentions", fontsize=7.5,
                 color="#555555", va="center", style="italic")
    axes[0].text(0, -lim * 0.25, "White\nmale", fontsize=6.5,
                 color="#555555", ha="center", style="italic")

    fig.tight_layout()
    out = FIGURES_DIR / f"fig_soft_trial_gap_unstructured.{fmt}"
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out}")


# ─── Figure 3: Absolute trial mention rates per group ────────────────────────

def fig3_trial_absolute(all_data: dict, fmt: str) -> None:
    """
    Raw % of cases mentioning clinical trials, per group per model.
    Lets us see whether groups are above/below the no-demographics baseline.
    """
    models = list(CHECKPOINT_PATHS.keys())
    x = np.arange(len(ALL_GROUPS) + 1)  # +1 for no_demographics column
    labels = list(ALL_GROUPS) + [REFERENCE]
    xlabels = [SHORT_LABELS[v] for v in ALL_GROUPS] + ["No demo-\ngraphics"]
    colors_x = [GROUP_COLORS[v] for v in ALL_GROUPS] + ["#BBBBBB"]

    w = 0.24
    offsets = np.linspace(-(len(models) - 1) / 2, (len(models) - 1) / 2, len(models)) * w

    fig, ax = plt.subplots(figsize=(11, 5))

    # Compute absolute rates by re-reading from the checkpoint asymmetry dict
    # We can derive: rate = (gain + shared) / total — but we need total and shared counts.
    # Simpler: just recompute from raw data
    raw_rates: dict[str, dict[str, float]] = {m: {} for m in models}

    for label, path in CHECKPOINT_PATHS.items():
        with open(path, encoding="utf-8") as fh:
            ckpt = json.load(fh)
        for v in labels:
            hits = sum(
                1 for cd in ckpt.values()
                if _trial(cd.get(v, {}).get("response_text", ""))
            )
            raw_rates[label][v] = hits / N * 100

    for i, model in enumerate(models):
        vals = [raw_rates[model][v] for v in labels]
        bars = ax.bar(x + offsets[i], vals, w,
                      label=model, color=MODEL_COLORS[model],
                      alpha=0.88, edgecolor="white", linewidth=0.6, zorder=3)
        # Reference line at no_demographics rate for this model
        ref_rate = raw_rates[model][REFERENCE]
        ax.hlines(ref_rate,
                  xmin=x[0] + offsets[i] - w / 2,
                  xmax=x[-2] + offsets[i] + w / 2,
                  colors=MODEL_COLORS[model], linestyles="--", lw=1.0, alpha=0.55)

    ax.set_xticks(x)
    ax.set_xticklabels(xlabels, fontsize=8.5)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.set_ylabel("% of cases mentioning clinical trials")

    # Separate the no_demographics column
    ax.axvline(len(ALL_GROUPS) - 0.5, color="#999999", lw=0.8, ls=":", alpha=0.6)
    ax.text(len(ALL_GROUPS) - 0.3, ax.get_ylim()[0] + 1, "<- demographic variants",
            fontsize=7, color="#888888")

    # Highlight white_male column
    ax.axvspan(-0.45, 0.45, alpha=0.05, color="#333333", zorder=0)

    ax.legend(loc="upper right", framealpha=0.92)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.grid(True, lw=0.4, alpha=0.5, zorder=0)
    ax.set_title(
        "Absolute Clinical Trial Mention Rate by Demographic Variant — Unstructured Notes\n"
        "Dashed lines = each model's no-demographics baseline  (n = 151 cases)",
        pad=9
    )

    fig.tight_layout()
    out = FIGURES_DIR / f"fig_soft_trial_rates_unstructured.{fmt}"
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out}")


# ─── Figure 4: Summary heatmap ───────────────────────────────────────────────

def fig4_summary_heatmap(all_data: dict, fmt: str) -> None:
    """
    Net soft-bias asymmetry (named group vs no_demographics) for all
    models × measures × groups.
    Positive = naming the demographic adds this framing.
    Negative = naming the demographic removes this framing.
    """
    measures_meta = [
        ("trial_net", "Clinical trial\nmention net"),
        ("cost_net",  "Financial barrier\nnet"),
        ("sw_net",    "Social work\nreferral net"),
        ("bsc_net",   "Palliative/BSC\nnet"),
    ]
    models = list(CHECKPOINT_PATHS.keys())

    row_labels = []
    matrix = []

    for model in models:
        for key, label in measures_meta:
            row_labels.append(f"{model}\n{label.split(chr(10))[0]}")
            vals = [pct(all_data[model][v][key]) for v in ALL_GROUPS]
            matrix.append(vals)

    mat = np.array(matrix, dtype=float)
    nrows, ncols = mat.shape

    fig, ax = plt.subplots(figsize=(9, 8))
    fig.suptitle(
        "Soft Bias Summary — Unstructured Notes  (reference = no-demographics prompt)\n"
        "Positive = naming demographics adds this framing; "
        "negative = naming demographics removes it",
        fontsize=10.5, fontweight="bold",
    )

    vmax = max(abs(np.nanmin(mat)), abs(np.nanmax(mat)), 2)
    norm = TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)
    im = ax.imshow(mat, cmap="RdBu_r", norm=norm, aspect="auto")

    for i in range(nrows):
        for j in range(ncols):
            v = mat[i, j]
            txt = f"{v:+.1f}%" if abs(v) >= 0.5 else "0"
            color = "white" if abs(v) > vmax * 0.5 else "#333333"
            ax.text(j, i, txt, ha="center", va="center",
                    fontsize=8.5, fontweight="bold", color=color)

    ax.set_xticks(range(ncols))
    ax.set_xticklabels([SHORT_LABELS[v].replace("\n", " ") for v in ALL_GROUPS],
                       fontsize=9, rotation=15, ha="right")
    ax.set_yticks(range(nrows))
    ax.set_yticklabels(row_labels, fontsize=8)

    # Separators between models
    for i in [4, 8]:
        ax.axhline(i - 0.5, color="white", linewidth=2)

    # Model labels on left
    for mi, model in enumerate(models):
        mid = mi * 4 + 1.5
        ax.annotate(model, xy=(-0.55, mid), xycoords=("data", "data"),
                    fontsize=9, fontweight="bold", ha="right", va="center",
                    annotation_clip=False, color=MODEL_COLORS[model])

    # Highlight white_male column
    ax.add_patch(plt.Rectangle((-0.5, -0.5), 1, nrows,
                                fill=False, edgecolor="#555555",
                                lw=1.5, clip_on=False, zorder=5, linestyle="--"))

    cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label("Net % of cases", fontsize=9)
    cbar.ax.tick_params(labelsize=8)
    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.tight_layout()
    out = FIGURES_DIR / f"fig_soft_heatmap_unstructured.{fmt}"
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", default="png", choices=["png", "pdf", "svg"])
    fmt = parser.parse_args().format

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({
        "font.family":       "sans-serif",
        "font.sans-serif":   ["Helvetica", "Arial", "DejaVu Sans"],
        "figure.facecolor":  "white",
        "axes.facecolor":    "white",
        "savefig.facecolor": "white",
    })

    print("\nLoading checkpoint data...")
    all_data = load_all()

    print("\nPrinting soft bias summary (vs no_demographics):")
    for model in CHECKPOINT_PATHS:
        print(f"\n  {model}")
        for v in ALL_GROUPS:
            d = all_data[model][v]
            print(f"    {v:<30}  trial_net={d['trial_net']:+d}  "
                  f"cost_net={d['cost_net']:+d}  "
                  f"sw_net={d['sw_net']:+d}  "
                  f"bsc_net={d['bsc_net']:+d}")

    print("\nGenerating figures...")
    fig1_paternalistic(all_data, fmt)
    fig2_trial_gap(all_data, fmt)
    fig3_trial_absolute(all_data, fmt)
    fig4_summary_heatmap(all_data, fmt)
    print(f"\nAll figures saved to {FIGURES_DIR}/")


if __name__ == "__main__":
    main()
