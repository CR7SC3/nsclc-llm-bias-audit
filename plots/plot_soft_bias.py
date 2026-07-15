"""EquityGUIDE — Soft bias figures.

Quantifies asymmetric content in LLM responses: clinical trial mentions,
financial/barrier framing, and palliative-care nudges by demographic group.

Usage
-----
    python plot_soft_bias.py               # PNG output
    python plot_soft_bias.py --format pdf
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

# ─── Config ──────────────────────────────────────────────────────────────────

FIGURES_DIR = Path("figures")
N = 165

CHECKPOINT_PATHS = {
    "GPT-4o":      Path("results/baseline/synthetic_structured_gpt-4o_checkpoint.json"),
    "Gemini":      Path("results/baseline/synthetic_structured_results.json"),
    "GPT-4o-mini": Path("results/baseline/synthetic_structured_gpt-4o-mini_results.json"),
}

MINORITY = [
    "black_male_medicaid",
    "black_female_medicaid",
    "latina_female_uninsured",
    "asian_female_medicare",
]

SHORT_LABELS = {
    "black_male_medicaid":     "Black male\n(Medicaid)",
    "black_female_medicaid":   "Black female\n(Medicaid)",
    "latina_female_uninsured": "Latina female\n(uninsured)",
    "asian_female_medicare":   "Asian female\n(Medicare)",
}

# Paul Tol's "bright" scheme — colorblind-safe, distinct
GROUP_COLORS = {
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
    For each minority variant, count cases where:
      - white_male gets X but minority does NOT  (white_advantage)
      - minority gets X but white_male does NOT  (minority_advantage)
    """
    out: dict[str, dict] = {v: {} for v in MINORITY}
    for v in MINORITY:
        wa_trial = wa_cost = wa_sw = wa_bsc = 0
        ma_trial = ma_cost = ma_sw = ma_bsc = 0
        for cd in data.values():
            wt = cd.get("white_male_private", {}).get("response_text", "")
            mt = cd.get(v, {}).get("response_text", "")
            if not wt or not mt:
                continue
            # clinical trial
            if _trial(wt) and not _trial(mt):  wa_trial += 1
            if _trial(mt) and not _trial(wt):  ma_trial += 1
            # cost / financial barrier
            if _cost(wt) and not _cost(mt):    wa_cost += 1
            if _cost(mt) and not _cost(wt):    ma_cost += 1
            # social work
            if _social_work(wt) and not _social_work(mt): wa_sw += 1
            if _social_work(mt) and not _social_work(wt): ma_sw += 1
            # BSC / palliative
            if _bsc(wt) and not _bsc(mt):  wa_bsc += 1
            if _bsc(mt) and not _bsc(wt):  ma_bsc += 1

        out[v] = {
            "trial_white_adv":    wa_trial,
            "trial_minority_adv": ma_trial,
            "trial_net":          wa_trial - ma_trial,   # >0 means white favoured
            "cost_minority_adv":  ma_cost,
            "sw_minority_adv":    ma_sw,
            "bsc_minority_adv":   ma_bsc,
        }
    return out


def load_all() -> dict[str, dict]:
    results = {}
    for label, path in CHECKPOINT_PATHS.items():
        with open(path, encoding="utf-8") as fh:
            results[label] = load_asymmetries(json.load(fh))
    return results


# ─── Plotting helpers ─────────────────────────────────────────────────────────

def _style_ax(ax, title: str = "", ylabel: str = "", pct: bool = True):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_title(title, fontsize=11, fontweight="bold", pad=8)
    ax.set_ylabel(ylabel, fontsize=9)
    if pct:
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.tick_params(axis="both", labelsize=8.5)
    ax.grid(axis="y", color="#e0e0e0", linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)


def pct(n: int) -> float:
    return n / N * 100


# ─── Figure 1: Gemini paternalistic framing ───────────────────────────────────

def fig_paternalistic(data_gemini: dict, fmt: str) -> None:
    """
    Three-panel: cost asymmetry | social work asymmetry | BSC nudge.
    Each bar = minority group, height = % of 165 cases where minority gets
    that framing but white_male does NOT.
    """
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.5), sharey=False)
    fig.suptitle(
        "Gemini 2.5 Flash — Asymmetric Content Added for Minority Patients\n"
        "(% of 165 cases where framing appears for minority but NOT for white male, identical clinical notes)",
        fontsize=11, fontweight="bold", y=1.01,
    )

    measures = [
        ("cost_minority_adv",   "Financial Barrier\nMentioned",       "A"),
        ("sw_minority_adv",     "Social Work / Navigator\nReferral",  "B"),
        ("bsc_minority_adv",    "Palliative / BSC\nContent Added",    "C"),
    ]

    groups = list(MINORITY)
    x = np.arange(len(groups))
    w = 0.6

    for ax, (key, title, panel) in zip(axes, measures):
        vals = [pct(data_gemini[v][key]) for v in groups]
        colors = [GROUP_COLORS[v] for v in groups]
        bars = ax.bar(x, vals, width=w, color=colors, edgecolor="white",
                      linewidth=0.8, zorder=3)
        # value labels
        for bar, val in zip(bars, vals):
            if val >= 1:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                        f"{val:.0f}%", ha="center", va="bottom", fontsize=8.5, fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels([SHORT_LABELS[v] for v in groups], fontsize=8)
        _style_ax(ax, title=f"({panel}) {title}", ylabel="% of cases" if panel == "A" else "")
        ax.set_ylim(0, max(vals) * 1.25 + 3)

    # Shared legend
    handles = [mpatches.Patch(color=GROUP_COLORS[v], label=SHORT_LABELS[v].replace("\n", " "))
               for v in groups]
    fig.legend(handles=handles, loc="lower center", ncol=4, fontsize=8.5,
               frameon=False, bbox_to_anchor=(0.5, -0.06))

    fig.tight_layout()
    out = FIGURES_DIR / f"fig_soft_paternalistic.{fmt}"
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out}")


# ─── Figure 2: Net clinical trial access gap ──────────────────────────────────

def fig_trial_gap(all_data: dict, fmt: str) -> None:
    """
    Diverging bar chart.  For each model × minority group:
      net = (cases where white gets trial but minority doesn't)
           -(cases where minority gets trial but white doesn't)
    Positive = white favoured.  Negative = minority favoured.
    """
    models   = list(CHECKPOINT_PATHS.keys())
    n_models = len(models)
    n_groups = len(MINORITY)

    fig, axes = plt.subplots(1, n_models, figsize=(13, 4.5), sharey=True)
    fig.suptitle(
        "Net Clinical Trial Mention Asymmetry: White Male vs. Minority Patient\n"
        "(positive = white male more likely to receive trial recommendation; "
        "negative = minority more likely)",
        fontsize=11, fontweight="bold", y=1.01,
    )

    x = np.arange(n_groups)
    w = 0.55
    max_abs = 0

    for ax, model in zip(axes, models):
        nets = [all_data[model][v]["trial_net"] for v in MINORITY]
        nets_pct = [pct(n) for n in nets]
        max_abs = max(max_abs, max(abs(v) for v in nets_pct))

        colors = [
            MODEL_COLORS[model] if v >= 0 else "#CCCCCC"
            for v in nets_pct
        ]
        bars = ax.bar(x, nets_pct, width=w, color=colors,
                      edgecolor="white", linewidth=0.8, zorder=3)

        # value labels
        for bar, val in zip(bars, nets_pct):
            offset = 0.4 if val >= 0 else -0.4
            va = "bottom" if val >= 0 else "top"
            if abs(val) >= 0.5:
                ax.text(bar.get_x() + bar.get_width() / 2,
                        val + offset,
                        f"{val:+.1f}%", ha="center", va=va, fontsize=8, fontweight="bold")

        ax.axhline(0, color="#444444", linewidth=0.8, zorder=4)
        ax.set_xticks(x)
        ax.set_xticklabels([SHORT_LABELS[v] for v in MINORITY], fontsize=8)
        _style_ax(ax, title=model, ylabel="Net % cases (white − minority)" if model == models[0] else "")
        ax.set_title(model, fontsize=11, fontweight="bold", pad=8)

    # Uniform y-axis limits
    lim = max(max_abs * 1.3, 8)
    for ax in axes:
        ax.set_ylim(-lim, lim)
        ax.yaxis.set_major_formatter(
            mticker.FuncFormatter(lambda v, _: f"{v:+.0f}%")
        )

    # Direction annotations on first panel
    axes[0].text(-0.55, lim * 0.7, "White male\nfavoured",
                 fontsize=7.5, color="#555555", va="center", style="italic")
    axes[0].text(-0.55, -lim * 0.7, "Minority\nfavoured",
                 fontsize=7.5, color="#555555", va="center", style="italic")

    fig.tight_layout()
    out = FIGURES_DIR / f"fig_soft_trial_gap.{fmt}"
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out}")


# ─── Figure 3: Summary heatmap ────────────────────────────────────────────────

def fig_summary_heatmap(all_data: dict, fmt: str) -> None:
    """
    Rows = soft measure × model (12 rows).
    Columns = 4 minority groups.
    Cell = % of cases showing asymmetry, coloured by direction:
      orange = white advantaged | blue = minority advantaged (paternalistic burden)
    """
    measures_meta = [
        ("trial_net",          "Clinical trial\nmention gap",   "Trial"),
        ("cost_minority_adv",  "Financial barrier\nadded for minority",  "Cost"),
        ("sw_minority_adv",    "Social work referral\nadded for minority", "SW"),
        ("bsc_minority_adv",   "Palliative/BSC added\nfor minority",      "BSC"),
    ]
    models = list(CHECKPOINT_PATHS.keys())

    # Build matrix: (model × measure) × group
    row_labels = []
    matrix = []
    is_net = []   # True if this row uses trial_net (can be negative)

    for model in models:
        for key, full_label, short in measures_meta:
            row_labels.append(f"{model}\n{short}")
            vals = [all_data[model][v][key] for v in MINORITY]
            matrix.append([pct(abs(v)) * np.sign(v) for v in vals])
            is_net.append(key == "trial_net")

    mat = np.array(matrix)
    nrows, ncols = mat.shape

    fig, ax = plt.subplots(figsize=(8, 8))
    fig.suptitle(
        "Soft Bias Summary — Asymmetric Content by Model and Minority Group\n"
        "(% of 165 cases; orange = white male advantaged; purple = minority patient burdened)",
        fontsize=10.5, fontweight="bold",
    )

    # Custom diverging: positive = orange (white advantaged for trial, or minority burdened for others)
    #                   negative = gray-blue (minority advantaged for trial)
    from matplotlib.colors import TwoSlopeNorm
    vmax = np.nanmax(np.abs(mat))
    norm = TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)

    im = ax.imshow(mat, cmap="RdBu_r", norm=norm, aspect="auto")

    # Cell text
    for i in range(nrows):
        for j in range(ncols):
            v = mat[i, j]
            txt = f"{v:+.0f}%" if abs(v) >= 1 else "0"
            color = "white" if abs(v) > vmax * 0.5 else "#333333"
            ax.text(j, i, txt, ha="center", va="center", fontsize=8.5,
                    fontweight="bold", color=color)

    # Axes
    ax.set_xticks(range(ncols))
    ax.set_xticklabels([SHORT_LABELS[v].replace("\n", " ") for v in MINORITY],
                       fontsize=9, rotation=15, ha="right")
    ax.set_yticks(range(nrows))
    ax.set_yticklabels(row_labels, fontsize=8.5)

    # Horizontal separators between models
    for i in [4, 8]:
        ax.axhline(i - 0.5, color="white", linewidth=2)

    # Model group brackets on y-axis
    for mi, model in enumerate(models):
        mid = mi * 4 + 1.5
        ax.annotate(
            model,
            xy=(-0.5, mid),
            xycoords=("data", "data"),
            fontsize=9, fontweight="bold",
            ha="right", va="center",
            annotation_clip=False,
            color=MODEL_COLORS[model],
        )

    cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label("% of cases", fontsize=9)
    cbar.ax.tick_params(labelsize=8)

    ax.tick_params(left=False, bottom=False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.tight_layout()
    out = FIGURES_DIR / f"fig_soft_heatmap.{fmt}"
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out}")


# ─── Figure 4: Gemini absolute trial mention rates ────────────────────────────

def fig_trial_absolute(fmt: str) -> None:
    """
    Raw trial mention rates per variant for Gemini — shows Latina/Asian drop
    even in absolute terms, not just relative to white.
    """
    # Precomputed from data extraction
    rates = {
        "white_male_private":      65.5,
        "black_male_medicaid":     67.3,
        "black_female_medicaid":   64.2,
        "latina_female_uninsured": 61.2,
        "asian_female_medicare":   61.2,
        "no_demographics":         (101/165)*100,
    }
    labels_order = list(rates.keys())
    vals = [rates[v] for v in labels_order]
    colors_list = [
        "#888888",          # white_male — reference
        GROUP_COLORS["black_male_medicaid"],
        GROUP_COLORS["black_female_medicaid"],
        GROUP_COLORS["latina_female_uninsured"],
        GROUP_COLORS["asian_female_medicare"],
        "#BBBBBB",          # no_demographics
    ]
    xlabels = [
        "White male\n(private)",
        "Black male\n(Medicaid)",
        "Black female\n(Medicaid)",
        "Latina female\n(uninsured)",
        "Asian female\n(Medicare)",
        "No demo-\ngraphics",
    ]

    fig, ax = plt.subplots(figsize=(8, 4))
    x = np.arange(len(vals))
    bars = ax.bar(x, vals, color=colors_list, edgecolor="white", linewidth=0.8,
                  width=0.6, zorder=3)

    # Reference line at white_male rate
    ax.axhline(rates["white_male_private"], color="#333333",
               linewidth=1.1, linestyle="--", zorder=4, label="White male reference")

    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.5,
                f"{val:.1f}%", ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(xlabels, fontsize=9)
    _style_ax(ax,
              title="Gemini 2.5 Flash — Clinical Trial Mention Rate by Demographic Variant\n"
                    "(% of 165 identical clinical notes where LLM included a clinical trial recommendation)",
              ylabel="% of cases mentioning clinical trials")
    ax.set_ylim(50, 75)
    ax.legend(fontsize=8.5, frameon=False)

    fig.tight_layout()
    out = FIGURES_DIR / f"fig_soft_trial_rates.{fmt}"
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", default="png", choices=["png", "pdf", "svg"])
    fmt = parser.parse_args().format

    FIGURES_DIR.mkdir(exist_ok=True)
    plt.rcParams.update({
        "font.family":      "sans-serif",
        "font.sans-serif":  ["Helvetica", "Arial", "DejaVu Sans"],
        "figure.facecolor": "white",
        "axes.facecolor":   "white",
        "savefig.facecolor": "white",
        "axes.labelcolor":  "#222222",
        "xtick.color":      "#222222",
        "ytick.color":      "#222222",
    })

    print("Loading checkpoint data...")
    all_data = load_all()

    print("Generating figures...")
    fig_paternalistic(all_data["Gemini"], fmt)
    fig_trial_gap(all_data, fmt)
    fig_summary_heatmap(all_data, fmt)
    fig_trial_absolute(fmt)
    print("\nDone.")


if __name__ == "__main__":
    main()
