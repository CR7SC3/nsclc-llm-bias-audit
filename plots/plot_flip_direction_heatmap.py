"""Flip-direction heatmap: per-variant, per-model net treatment-tier shift.

Rows = demographic variants (grouped by stratum), cols = 6 models.
Color = net% = 100*(upgrades - downgrades)/n vs the no-demographics reference,
on the ordinal treatment-tier scale (src/analyze/continuous_scores.py).
  RED  = net downgrade  (less aggressive / "worse")
  BLUE = net upgrade    (more aggressive)
Sign-test per cell; grid-wide Benjamini-Hochberg across all variant×model cells.
  filled star  = survives BH q<0.05
  open dot     = uncorrected p<0.05 only

Run:  venv/bin/python plots/plot_flip_direction_heatmap.py
Out:  figures/manuscript/FigS_flip_direction.png (+ .pdf)
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from scipy.stats import binomtest
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.analyze.continuous_scores import aggressiveness_score

OUT = Path("figures/manuscript"); OUT.mkdir(parents=True, exist_ok=True)
PANELS = Path("figures/manuscript_combined/panels"); PANELS.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "figure.dpi": 150, "savefig.bbox": "tight", "figure.facecolor": "white",
})

CKPT = {
 "Gemini-2.5-flash": "results/baseline/v2_genie_bpc_nsclc_checkpoint.json",
 "DeepSeek-chat":    "results/baseline/v2_genie_bpc_nsclc_deepseek-chat_checkpoint.json",
 "Llama-3.3-70B":    "results/baseline/v2_genie_bpc_nsclc_meta-llama-Llama-3.3-70B-Instruct-Turbo_checkpoint.json",
 "Llama-3.1-8B":     "results/baseline/v2_genie_bpc_nsclc_openrouter-meta-llama-llama-3.1-8b-instruct_checkpoint.json",
 "GPT-4o":           "results/baseline/v2_genie_bpc_nsclc_gpt-4o_checkpoint.json",
 "GPT-4o-mini":      "results/baseline/v2_genie_bpc_nsclc_gpt-4o-mini_checkpoint.json",
}
REF = "no_demographics"

# grouped, ordered variant rows (stratum -> [(key, pretty)])
GROUPS = [
 ("Socioeconomic disadvantage", [
   ("underinsured_only", "Underinsured"), ("uninsured_only", "Uninsured"),
   ("medicaid_only", "Medicaid"), ("low_income_patient", "Low income"),
   ("low_income_black", "Low income, Black"), ("latina_female_uninsured", "Latina, uninsured"),
   ("black_unhoused", "Black + unhoused"), ("unhoused_patient", "Unhoused"),
   ("rural_patient", "Rural"), ("small_community_hospital", "Small community hospital"),
   ("immigrant_patient", "Immigrant"), ("limited_english_patient", "Limited English"),
   ("black_female_medicaid", "Black female, Medicaid")]),
 ("Race / ethnicity only", [
   ("black_race_only", "Black"), ("hispanic_race_only", "Hispanic"),
   ("asian_race_only", "Asian"), ("native_american_race_only", "Native American"),
   ("middle_eastern_race_only", "Middle Eastern"), ("multiracial_race_only", "Multiracial")]),
 ("Gender / identity", [
   ("transgender_woman", "Transgender woman"), ("non_binary_patient", "Non-binary"),
   ("gay_male_patient", "Gay male"), ("black_female_private", "Black female, private")]),
 ("Insurance / age (other)", [
   ("medicare_only", "Medicare"), ("medicare_advantage_only", "Medicare Advantage"),
   ("elderly_patient_75", "Elderly (75+)"), ("white_female_medicaid", "White female, Medicaid")]),
 ("Privileged / advantage", [
   ("high_income_patient", "High income"), ("white_male_private", "White male, private")]),
]


def tier(v):
    return aggressiveness_score(v.get("response_text", "")) if isinstance(v, dict) else None


def _draw_heatmap(ax, M, rows, labels, models, groupspans, bh, pval, norm, transpose):
    """Draw the annotated net-shift heatmap. transpose=False -> variants on rows,
    models on columns (portrait); transpose=True -> models on rows, variants on
    columns (landscape, for the Figure-2 panel)."""
    ncol = len(models)
    im = ax.imshow(M.T if transpose else M, cmap="RdBu", norm=norm, aspect="auto")
    if not transpose:
        ax.set_xticks(range(ncol)); ax.set_xticklabels(models, rotation=30, ha="right", fontsize=9)
        ax.set_yticks(range(len(rows))); ax.set_yticklabels(labels, fontsize=8.5)
    else:
        ax.set_xticks(range(len(rows))); ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8.0)
        ax.set_yticks(range(ncol)); ax.set_yticklabels(models, fontsize=9)
    ax.tick_params(length=0)
    afs = 6.2 if transpose else 7.0
    for i, key in enumerate(rows):
        for j, m in enumerate(models):
            if np.isnan(M[i, j]): continue
            val = M[i, j]
            sig_bh = bh.get((key, m), 1) < 0.05
            unc = pval.get(key, {}).get(m, 1) < 0.05
            txt = f"{val:+.1f}" + ("·" if (unc and not sig_bh) else "")
            tc = "white" if abs(val) > 3.0 else "#222"
            xx, yy = (i, j) if transpose else (j, i)
            ax.text(xx, yy, txt, ha="center", va="center", fontsize=afs,
                    color=tc, fontweight="bold" if sig_bh else "normal")
            if sig_bh:  # font-free star marker in the corner
                mx, my = (i + 0.30, j - 0.32) if transpose else (j + 0.33, i - 0.30)
                ax.plot(mx, my, marker="*", ms=6 if transpose else 7,
                        color="white", markeredgecolor="k", markeredgewidth=0.4,
                        zorder=6, clip_on=False)
    for gname, s, e in groupspans:
        if not transpose:
            if s > 0:
                ax.axhline(s - 0.5, color="k", lw=1.4)
            ax.text(-0.34, (s + e - 1) / 2, gname, transform=ax.get_yaxis_transform(),
                    ha="center", va="center", rotation=90, fontsize=8.5, fontweight="bold",
                    color="#555", clip_on=False)
        else:
            if s > 0:
                ax.axvline(s - 0.5, color="k", lw=1.4)
            ax.text((s + e - 1) / 2, 1.015, gname, transform=ax.get_xaxis_transform(),
                    ha="center", va="bottom", fontsize=8.0, fontweight="bold",
                    color="#555", clip_on=False)
    if not transpose:
        for j in range(1, ncol):
            ax.axvline(j - 0.5, color="white", lw=1.0)
        ax.set_xlim(-0.5, ncol - 0.5)
    else:
        for j in range(1, ncol):
            ax.axhline(j - 0.5, color="white", lw=1.0)
        ax.set_ylim(ncol - 0.5, -0.5)
    return im


def main():
    models = list(CKPT)
    # net%[variant][model], p[variant][model]
    net, pval = {}, {}
    for m, f in CKPT.items():
        if not Path(f).exists():
            print("missing", m); continue
        d = json.load(open(f))
        counts = {}
        for cid, cd in d.items():
            rt = tier(cd.get(REF, {}))
            if rt is None: continue
            for var, v in cd.items():
                if var == REF: continue
                vt = tier(v)
                if vt is None: continue
                a = counts.setdefault(var, [0, 0, 0])
                if vt < rt: a[0] += 1
                elif vt > rt: a[1] += 1
                else: a[2] += 1
        for var, (dn, up, sm) in counts.items():
            n = dn + up + sm
            net.setdefault(var, {})[m] = 100 * (up - dn) / n if n else 0.0
            pval.setdefault(var, {})[m] = binomtest(dn, dn + up, 0.5).pvalue if (dn + up) else 1.0

    # grid-wide BH across all filled cells
    cells = [(var, m) for grp in GROUPS for var, _ in grp[1] for m in models
             if var in pval and m in pval[var]]
    ps = sorted((pval[v][m], v, m) for v, m in cells)
    K = len(ps); bh = {}
    prev = 1.0
    for rank, (p, v, m) in enumerate(reversed(ps), 1):
        k = K - rank + 1
        prev = min(prev, p * K / k); bh[(v, m)] = prev

    # build matrix + row labels with group separators
    rows, labels, groupspans = [], [], []
    r = 0
    for gname, items in GROUPS:
        start = r
        for key, pretty in items:
            rows.append(key); labels.append(pretty); r += 1
        groupspans.append((gname, start, r))
    M = np.full((len(rows), len(models)), np.nan)
    for i, key in enumerate(rows):
        for j, m in enumerate(models):
            if key in net and m in net[key]:
                M[i, j] = net[key][m]

    vmax = 5.0
    norm = TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)

    # ---- Landscape panel for combine_figures.py (Fig 2D): models on rows, variants
    # on columns so the annotated cells get width and the grid reads full-width along
    # the figure bottom. Titleless — banner + footnotes belong to the caption.
    figL, axL = plt.subplots(figsize=(16.5, 5.4))
    imL = _draw_heatmap(axL, M, rows, labels, models, groupspans, bh, pval, norm, transpose=True)
    cbL = figL.colorbar(imL, ax=axL, fraction=0.018, pad=0.045, extend="both")
    cbL.set_label("Net treatment-tier shift\nvs no-demographics (%)", fontsize=8.5)
    # significance-glyph key moved to the caption (per figure edit).
    figL.tight_layout()
    figL.savefig(PANELS / "p_flip_heatmap.png", dpi=200, bbox_inches="tight")
    plt.close(figL)
    print("wrote", PANELS / "p_flip_heatmap.png")

    # ---- Portrait standalone supplement (FigS): variants on rows, models on columns.
    fig, ax = plt.subplots(figsize=(8.2, 12.0))
    im = _draw_heatmap(ax, M, rows, labels, models, groupspans, bh, pval, norm, transpose=False)
    cb = fig.colorbar(im, ax=ax, fraction=0.030, pad=0.02, extend="both")
    cb.set_label("Net treatment-tier shift vs no-demographics (%)", fontsize=9)

    ax.set_title("Direction of treatment change by demographic variant and model\n"
                 "net% = upgrades − downgrades   (red = less aggressive / “worse”,  blue = more aggressive)",
                 fontsize=11.5, fontweight="bold", pad=16)

    # marker + source legend at the bottom
    ax.plot(0.005, -0.105, marker="*", ms=8, color="white", markeredgecolor="k",
            markeredgewidth=0.5, transform=ax.transAxes, clip_on=False)
    ax.text(0.022, -0.105,
            "= survives grid-wide Benjamini-Hochberg q<0.05      · = uncorrected sign-test p<0.05 only",
            transform=ax.transAxes, fontsize=8, color="#333", va="center")
    ax.text(0.0, -0.128,
            "1,048 GENIE NSCLC cases × 6 models. Tier scale 1 = best supportive care … 8 = surgical resection. "
            "Most cells sit near 0 (decision stable).",
            transform=ax.transAxes, fontsize=7.2, color="#666", va="center")

    fig.tight_layout()
    fig.subplots_adjust(bottom=0.12)
    fig.savefig(OUT / "FigS_flip_direction.png", dpi=300)
    fig.savefig(OUT / "FigS_flip_direction.pdf")
    print("wrote", OUT / "FigS_flip_direction.png")


if __name__ == "__main__":
    main()
