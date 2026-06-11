"""EquityGUIDE — Publication figures for unstructured concordance analysis.

Uses no_demographics as the reference baseline (instead of white_male_private).
Reads directly from checkpoint JSONs and recomputes flip rates.

Usage
-----
    python plot_unstructured.py               # PNG output (default)
    python plot_unstructured.py --format pdf
    python plot_unstructured.py --format svg
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).parent))
from src.analyze.response_parser import ResponseParser

# ─── Configuration ───────────────────────────────────────────────────────────

RESULTS_DIR  = Path("results/baseline")
FIGURES_DIR  = Path("figures/unstructured")
SUBSET       = "synthetic_unstructured"
REFERENCE    = "no_demographics"

MODELS: dict[str, str] = {
    "gpt-4o":           "GPT-4o",
    "gemini-2.5-flash": "Gemini 2.5 Flash",
    "gpt-4o-mini":      "GPT-4o-mini",
}

ALL_VARIANTS = [
    "white_male_private",
    "black_male_medicaid",
    "black_female_medicaid",
    "latina_female_uninsured",
    "asian_female_medicare",
    "no_demographics",
]
COMPARE_VARIANTS = [v for v in ALL_VARIANTS if v != REFERENCE]

GROUP_LABELS = {
    "white_male_private":      "White male\n(private ins.)",
    "black_male_medicaid":     "Black male\n(Medicaid)",
    "black_female_medicaid":   "Black female\n(Medicaid)",
    "latina_female_uninsured": "Latina female\n(uninsured)",
    "asian_female_medicare":   "Asian female\n(Medicare)",
    "no_demographics":         "No demographics",
}

MODEL_COLORS = {
    "gpt-4o":           "#0077BB",
    "gemini-2.5-flash": "#EE7733",
    "gpt-4o-mini":      "#009988",
}

plt.rcParams.update({
    "font.family":       "sans-serif",
    "font.size":         10,
    "axes.titlesize":    11,
    "axes.labelsize":    10,
    "xtick.labelsize":   8.5,
    "ytick.labelsize":   8.5,
    "legend.fontsize":   8.5,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "figure.dpi":        150,
})


# ─── Data loading ────────────────────────────────────────────────────────────

def _checkpoint_path(slug: str) -> Path:
    prefix = SUBSET if slug == "gemini-2.5-flash" else f"{SUBSET}_{slug.replace('/', '-')}"
    for suffix in ("_results.json", "_checkpoint.json"):
        p = RESULTS_DIR / f"{prefix}{suffix}"
        if p.exists():
            return p
    raise FileNotFoundError(f"No checkpoint for {slug}")


def _parse_categories(checkpoint: dict) -> dict[str, dict[str, str]]:
    """Return {case_id: {variant: category}} from a checkpoint dict."""
    parser = ResponseParser()
    out: dict[str, dict[str, str]] = {}
    for case_id, variants in checkpoint.items():
        cats: dict[str, str] = {}
        for variant, result in variants.items():
            if "error" in result:
                cats[variant] = "unknown"
                continue
            # Some models already store parsed_category
            cat = result.get("parsed_category")
            if cat:
                cats[variant] = cat
            else:
                cats[variant] = parser.parse(result.get("response_text", "")).category
        out[case_id] = cats
    return out


def load_all() -> dict[str, dict[str, dict[str, str]]]:
    """Return {slug: {case_id: {variant: category}}}."""
    data: dict[str, dict[str, dict[str, str]]] = {}
    for slug in MODELS:
        try:
            path = _checkpoint_path(slug)
            print(f"Loading {slug}: {path.name}  ({path.stat().st_size // 1024} KB)")
            raw = json.loads(path.read_text())
            data[slug] = _parse_categories(raw)
        except FileNotFoundError as e:
            print(f"[warn] {e}")
    return data


# ─── Flip computation ────────────────────────────────────────────────────────

def _wilson_ci(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    if n == 0:
        return 0.0, 0.0
    p = k / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    margin = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return float(max(0.0, centre - margin)), float(min(1.0, centre + margin))


def compute_flips(data: dict[str, dict[str, str]]) -> dict[str, dict]:
    """
    For each compare variant, compute flip rate vs REFERENCE (no_demographics).
    Returns {variant: {flips, total, rate, ci_low, ci_high, p_value}}.
    """
    results: dict[str, dict] = {}
    for v in COMPARE_VARIANTS:
        flips = 0
        total = 0
        for cats in data.values():
            ref_cat = cats.get(REFERENCE)
            var_cat = cats.get(v)
            if ref_cat is None or var_cat is None:
                continue
            if ref_cat == "unknown" or var_cat == "unknown":
                continue
            total += 1
            if ref_cat != var_cat:
                flips += 1
        rate = flips / total if total else 0.0
        ci_lo, ci_hi = _wilson_ci(flips, total)
        # One-sided binomial test: is flip rate > 0?
        p = float(stats.binomtest(flips, total, 0.5, alternative="less").pvalue) if total else 1.0
        results[v] = dict(flips=flips, total=total, rate=rate,
                          ci_low=ci_lo, ci_high=ci_hi, p_value=p)
    return results


def all_flip_stats(all_data: dict) -> dict[str, dict[str, dict]]:
    """Return {slug: {variant: stats}}."""
    return {slug: compute_flips(data) for slug, data in all_data.items()}


# ─── Shared helpers ──────────────────────────────────────────────────────────

def _bar_setup(n_models: int, n_groups: int, width: float = 0.24):
    x = np.arange(n_groups)
    offsets = np.linspace(-(n_models - 1) / 2, (n_models - 1) / 2, n_models) * width
    return x, offsets, width


def _save(fig: plt.Figure, name: str, fmt: str) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / f"{name}.{fmt}"
    fig.savefig(path, dpi=300, bbox_inches="tight")
    print(f"Saved: {path}")
    plt.close(fig)


# ─── Figure 1: Flip rates (no_demographics as reference) ─────────────────────

def fig1_flip_rates(flip_stats: dict, fmt: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))

    slugs = [s for s in MODELS if s in flip_stats]
    n_groups = len(COMPARE_VARIANTS)
    x, offsets, w = _bar_setup(len(slugs), n_groups)

    for i, slug in enumerate(slugs):
        stats_d = flip_stats[slug]
        rates = [stats_d.get(v, {}).get("rate", np.nan) for v in COMPARE_VARIANTS]
        ci_lo = [stats_d.get(v, {}).get("ci_low",  np.nan) for v in COMPARE_VARIANTS]
        ci_hi = [stats_d.get(v, {}).get("ci_high", np.nan) for v in COMPARE_VARIANTS]
        yerr = [[r - lo for r, lo in zip(rates, ci_lo)],
                [hi - r  for r, hi in zip(rates, ci_hi)]]
        ax.bar(x + offsets[i], rates, w,
               label=MODELS[slug], color=MODEL_COLORS[slug], alpha=0.88, zorder=3,
               yerr=yerr, capsize=3,
               error_kw={"linewidth": 0.8, "ecolor": "#333333", "alpha": 0.7})

    # Highlight white_male_private column with a subtle background
    wmp_idx = COMPARE_VARIANTS.index("white_male_private")
    ax.axvspan(wmp_idx - 0.45, wmp_idx + 0.45, alpha=0.06, color="#333333", zorder=0)
    ax.text(wmp_idx, -0.035, "White male\n(reference\ngroup)", ha="center",
            va="top", fontsize=7, color="#555555", style="italic",
            transform=ax.get_xaxis_transform())

    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))
    ax.set_ylabel("Flip rate vs. no-demographics baseline")
    ax.set_xticks(x)
    ax.set_xticklabels([GROUP_LABELS[v] for v in COMPARE_VARIANTS])
    ax.legend(loc="upper right", framealpha=0.92)
    ax.set_ylim(0, 0.95)
    ax.yaxis.grid(True, lw=0.4, alpha=0.5, zorder=0)
    ax.set_title(
        "Treatment Category Flip Rate — Unstructured Notes\n"
        "Reference = no-demographics prompt  (n = 151 cases × 6 variants; bars show 95% Wilson CI)",
        pad=9
    )
    ax.text(
        0.01, 0.97,
        "Flip = LLM treatment category differs from its own no-demographics response",
        transform=ax.transAxes, va="top", ha="left", fontsize=7.5, color="#555555",
        style="italic",
        bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8, ec="#cccccc")
    )

    fig.tight_layout()
    _save(fig, "fig1_flip_rates_no_demo_ref", fmt)


# ─── Figure 2: Cross-model heatmap ───────────────────────────────────────────

def fig2_heatmap(flip_stats: dict, fmt: str) -> None:
    slugs       = [s for s in MODELS if s in flip_stats]
    model_labels = [MODELS[s] for s in slugs]
    group_labels = [GROUP_LABELS[v] for v in COMPARE_VARIANTS]

    n_m = len(slugs)
    n_g = len(COMPARE_VARIANTS)

    rate_matrix = np.full((n_m, n_g), np.nan)
    for i, slug in enumerate(slugs):
        for j, v in enumerate(COMPARE_VARIANTS):
            rate_matrix[i, j] = flip_stats[slug].get(v, {}).get("rate", np.nan)

    fig, ax = plt.subplots(figsize=(10, 3.2))

    vmax = float(np.nanmax(rate_matrix))
    im = ax.imshow(rate_matrix, cmap="YlOrRd", vmin=0, vmax=vmax, aspect="auto")
    cbar = fig.colorbar(im, ax=ax, shrink=0.85, pad=0.02)
    cbar.set_label("Flip rate vs.\nno-demo baseline", fontsize=7.5)
    cbar.ax.tick_params(labelsize=7)
    cbar.ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))

    ax.set_xticks(range(n_g))
    ax.set_xticklabels(group_labels, fontsize=8)
    ax.set_yticks(range(n_m))
    ax.set_yticklabels(model_labels, fontsize=9)

    # Border white_male_private column
    wmp_idx = COMPARE_VARIANTS.index("white_male_private")
    ax.add_patch(plt.Rectangle((wmp_idx - 0.5, -0.5), 1, n_m,
                                fill=False, edgecolor="black", lw=2.0,
                                clip_on=False, zorder=5))
    ax.text(wmp_idx, n_m - 0.1, "traditional\nreference", ha="center",
            va="bottom", fontsize=6.5, color="#444444")

    for ii in range(n_m):
        for jj in range(n_g):
            v = rate_matrix[ii, jj]
            if not np.isnan(v):
                color = "white" if v > vmax * 0.62 else "black"
                ax.text(jj, ii, f"{v:.0%}", ha="center", va="center",
                        fontsize=9, color=color, fontweight="bold")

    ax.set_title(
        "Cross-Model Flip Rate Heatmap — Unstructured NSCLC Notes\n"
        "Reference = no-demographics prompt  (boxed column = traditional reference group)",
        pad=8, fontsize=10
    )

    fig.tight_layout()
    _save(fig, "fig2_flip_rate_heatmap", fmt)


# ─── Figure 3: White-male premium (flip rate of white_male vs no_demo) ───────
#
# This answers: do models treat white male patients differently from the
# demographically-neutral default — and does that differ from how minority
# groups are treated?

def fig3_wmp_vs_minority(flip_stats: dict, fmt: str) -> None:
    slugs = [s for s in MODELS if s in flip_stats]
    fig, ax = plt.subplots(figsize=(9, 4.5))

    n_groups = len(COMPARE_VARIANTS)
    x, offsets, w = _bar_setup(len(slugs), n_groups)

    for i, slug in enumerate(slugs):
        rates = [flip_stats[slug].get(v, {}).get("rate", np.nan) for v in COMPARE_VARIANTS]
        ax.bar(x + offsets[i], rates, w,
               label=MODELS[slug], color=MODEL_COLORS[slug], alpha=0.88, zorder=3)

    # Draw reference line for white_male_private per model
    wmp_idx = COMPARE_VARIANTS.index("white_male_private")
    for i, slug in enumerate(slugs):
        wmp_rate = flip_stats[slug].get("white_male_private", {}).get("rate", np.nan)
        if not np.isnan(wmp_rate):
            ax.hlines(wmp_rate,
                      xmin=x[0] + offsets[i] - w / 2,
                      xmax=x[-1] + offsets[i] + w / 2,
                      colors=MODEL_COLORS[slug], linestyles="--", lw=1.0, alpha=0.5)

    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))
    ax.set_ylabel("Flip rate vs. no-demographics baseline")
    ax.set_xticks(x)
    ax.set_xticklabels([GROUP_LABELS[v] for v in COMPARE_VARIANTS])
    ax.legend(framealpha=0.92)
    ax.yaxis.grid(True, lw=0.4, alpha=0.5, zorder=0)
    ax.set_ylim(0, 0.95)

    # Shade white_male column
    ax.axvspan(wmp_idx - 0.45, wmp_idx + 0.45, alpha=0.06, color="#333333", zorder=0)

    ax.set_title(
        "Flip Rate by Demographic Group — Unstructured Notes\n"
        "Dashed lines = white male (private) flip rate per model  "
        "(reference = no-demographics prompt)",
        pad=9
    )

    fig.tight_layout()
    _save(fig, "fig3_group_comparison", fmt)


# ─── Figure 4: Summary table ─────────────────────────────────────────────────

def fig4_summary_table(flip_stats: dict, fmt: str) -> None:
    rows = []
    for slug, label in MODELS.items():
        fs = flip_stats.get(slug)
        if fs is None:
            continue
        rates = [fs.get(v, {}).get("rate", np.nan) for v in COMPARE_VARIANTS]
        wmp   = fs.get("white_male_private", {}).get("rate", np.nan)
        minority_rates = [fs.get(v, {}).get("rate", np.nan)
                          for v in COMPARE_VARIANTS if v != "white_male_private"]
        mean_minority = float(np.nanmean(minority_rates))
        max_flip = float(np.nanmax(rates))
        cases_any = sum(
            1 for case_cats in _raw_data[slug].values()
            if any(case_cats.get(REFERENCE) != case_cats.get(v)
                   and case_cats.get(REFERENCE) not in (None, "unknown")
                   and case_cats.get(v) not in (None, "unknown")
                   for v in COMPARE_VARIANTS)
        )
        total = len(_raw_data[slug])
        rows.append({
            "Model":                    label,
            "White male\nflip rate":    f"{wmp:.1%}",
            "Mean minority\nflip rate": f"{mean_minority:.1%}",
            "Peak flip\nrate":          f"{max_flip:.1%}",
            "Cases with\n≥1 flip":      f"{cases_any}/{total}  ({cases_any/total:.0%})",
        })

    fig, ax = plt.subplots(figsize=(11, 2.2))
    ax.axis("off")
    col_labels = list(rows[0].keys())
    cell_data  = [[row[c] for c in col_labels] for row in rows]
    row_colors = [[MODEL_COLORS[slug] + "33"] * len(col_labels)
                  for slug in MODELS if slug in flip_stats]

    tbl = ax.table(
        cellText=cell_data,
        colLabels=col_labels,
        cellLoc="center",
        loc="center",
        cellColours=row_colors,
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    tbl.scale(1, 2.0)
    for (r, c), cell in tbl.get_celld().items():
        if r == 0:
            cell.set_facecolor("#444444")
            cell.set_text_props(color="white", fontweight="bold")
        cell.set_edgecolor("#dddddd")

    ax.set_title(
        "Cross-Model Summary — Unstructured NSCLC Notes  "
        "(n = 151 cases, reference = no-demographics prompt)",
        pad=14, fontsize=11, fontweight="bold"
    )
    fig.tight_layout()
    _save(fig, "fig4_summary_table", fmt)


# ─── Entry point ─────────────────────────────────────────────────────────────

_raw_data: dict = {}


def main() -> None:
    global _raw_data

    parser = argparse.ArgumentParser()
    parser.add_argument("--format", choices=["pdf", "png", "svg"], default="png")
    args = parser.parse_args()

    fmt = args.format
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    print("\nLoading checkpoints...")
    _raw_data = load_all()

    print("\nComputing flip rates (reference = no_demographics)...")
    flip = all_flip_stats(_raw_data)

    print("\nFlip rate summary:")
    for slug, label in MODELS.items():
        if slug not in flip:
            continue
        fs = flip[slug]
        print(f"\n  {label}")
        for v in COMPARE_VARIANTS:
            s = fs.get(v, {})
            print(f"    {v:<30} {s.get('rate', 0):.1%}  "
                  f"({s.get('flips', 0)}/{s.get('total', 0)})")

    print("\nGenerating figures...")
    fig1_flip_rates(flip, fmt)
    fig2_heatmap(flip, fmt)
    fig3_wmp_vs_minority(flip, fmt)
    fig4_summary_table(flip, fmt)

    print(f"\nAll figures saved to {FIGURES_DIR}/")


if __name__ == "__main__":
    main()
