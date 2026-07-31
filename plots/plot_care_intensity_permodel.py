"""Fig 2C directional panel: per-model care-intensity shifts (NEVER pooled).

Two sub-panels over the non-race demographic axes, variants shared on the y-axis:
  left  = advanced treatment (clinical-trial mention),  harm = net < 0 (offered LESS)
  right = de-escalation (palliative / BSC),              harm = net > 0 (offered MORE)

Each variant row shows the 6 per-vendor net% as dots (no pooling), the cross-vendor mean
as a diamond, and a k/6 count of vendors in the harm direction at the row's harm edge.
Deliberately NO significance stars: per-model BH-FDR leaves individual effects
non-significant; the honest signal is DIRECTIONAL consistency across vendors.

Reads results/analysis/advanced_care_per_model.csv.
Writes a titleless panel to figures/manuscript_combined/panels/p_care_intensity.png
(the A/B/C letter is stamped by combine_figures.py) and a standalone copy to
figures/manuscript/Fig02C_care_intensity_permodel.png.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "results/analysis/advanced_care_per_model.csv"
PANELS = ROOT / "figures/manuscript_combined/panels"; PANELS.mkdir(parents=True, exist_ok=True)
MAN = ROOT / "figures/manuscript"; MAN.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "savefig.facecolor": "white",
    "axes.spines.top": False,
    "axes.spines.right": False,
})

C_DOT = "#9AA7B0"      # per-vendor dots (neutral grey-blue)
C_MEAN = "#8E1B1B"     # cross-vendor mean diamond
C_HARM_BG = "#F3E4E1"  # faint harm-side shading

NICE = {
    "uninsured_only": "uninsured", "medicaid_only": "Medicaid",
    "underinsured_only": "underinsured", "medicare_only": "Medicare",
    "medicare_advantage_only": "Medicare Advantage", "low_income_patient": "low-income",
    "high_income_patient": "high-income", "unhoused_patient": "unhoused",
    "rural_patient": "rural", "small_community_hospital": "community hospital",
    "immigrant_patient": "immigrant", "limited_english_patient": "limited-English",
    "non_binary_patient": "non-binary", "transgender_woman": "transgender woman",
    "gay_male_patient": "gay male",
    "white_male_private": "White male · private",
    "white_female_medicaid": "White female · Medicaid",
}
# top -> bottom draw order (reference anchored at the bottom)
ORDER = ["unhoused_patient", "medicaid_only", "medicare_only", "medicare_advantage_only",
         "underinsured_only", "uninsured_only", "low_income_patient", "high_income_patient",
         "small_community_hospital", "rural_patient", "limited_english_patient",
         "immigrant_patient", "transgender_woman", "gay_male_patient", "non_binary_patient",
         "white_male_private", "white_female_medicaid"]
REFERENCE = {"white_male_private", "white_female_medicaid"}


def load():
    # variant -> {model: (ct_net, pall_net)}
    d = defaultdict(dict)
    models = []
    for r in csv.DictReader(open(SRC)):
        d[r["variant"]][r["model"]] = (float(r["ct_net"]), float(r["pall_net"]))
        if r["model"] not in models:
            models.append(r["model"])
    return d, models


def panel(ax, d, models, idx, title, subtitle, harm_negative, xlim):
    n = len(ORDER)
    ys = {vk: n - 1 - i for i, vk in enumerate(ORDER)}
    # harm-side shading
    if harm_negative:
        ax.axvspan(xlim[0], 0, color=C_HARM_BG, zorder=0)
    else:
        ax.axvspan(0, xlim[1], color=C_HARM_BG, zorder=0)
    jit = [(-0.24 + 0.48 * k / (len(models) - 1)) for k in range(len(models))]
    ytick, ylab = [], []
    for vk in ORDER:
        y = ys[vk]
        vals = [d[vk][m][idx] for m in models if m in d[vk]]
        for k, m in enumerate([m for m in models if m in d[vk]]):
            ax.plot(d[vk][m][idx], y + jit[k], "o", ms=3.4, color=C_DOT,
                    alpha=0.9, zorder=3, mew=0)
        if vals:
            mean = sum(vals) / len(vals)
            ax.plot(mean, y, "D", ms=6.2, color=C_MEAN, zorder=4, mew=0)
            harm = sum(1 for v in vals if (v < 0 if harm_negative else v > 0))
            xedge = xlim[0] + 0.015 * (xlim[1] - xlim[0]) if harm_negative else \
                xlim[1] - 0.015 * (xlim[1] - xlim[0])
            ha = "left" if harm_negative else "right"
            col = "#8E1B1B" if (harm >= 3 and vk not in REFERENCE) else "#999"
            ax.text(xedge, y, f"{harm}/{len(vals)}", ha=ha, va="center",
                    fontsize=7.0, color=col, zorder=4)
        ytick.append(y); ylab.append(NICE[vk])
    ax.axvline(0, color="#333", lw=0.8, zorder=2)
    ax.set_yticks(ytick); ax.set_yticklabels(ylab, fontsize=8.2)
    for lbl, vk in zip(ax.get_yticklabels(), ORDER):
        if vk in REFERENCE:
            lbl.set_color("#777"); lbl.set_style("italic")
    ax.set_xlim(*xlim)
    ax.set_ylim(-0.7, n - 0.3)
    ax.set_xlabel("per-vendor net change vs no-demographics (pp)", fontsize=8.4)
    ax.set_title(title, fontsize=16, fontweight="bold", loc="left", pad=22)
    ax.text(0, 1.012, subtitle, transform=ax.transAxes, fontsize=12,
            color="#555", va="bottom")
    ax.tick_params(length=0)


def main():
    d, models = load()

    # Side-by-side panel (Fig 2B): Advanced treatment | De-escalation share the y-axis
    # (variant rows line up) so the panel sits in the top row beside the concordance panel.
    figp, (Ap, Bp) = plt.subplots(1, 2, figsize=(11.4, 6.6), sharey=True)
    shared_xlim = (-4.5, 7.0)   # both subpanels share one scale so equal bar length == equal pp
    panel(Ap, d, models, 0, "Advanced treatment",
          "clinical-trial mention   (shaded = offered less)",
          harm_negative=True, xlim=shared_xlim)
    panel(Bp, d, models, 1, "De-escalation",
          "palliative / best-supportive-care   (shaded = offered more)",
          harm_negative=False, xlim=shared_xlim)
    Bp.tick_params(labelleft=False)   # shared strata labels on the left sub-panel only
    figp.tight_layout(rect=(0, 0, 1, 0.99), w_pad=3.0)
    p_panel = PANELS / "p_care_intensity.png"
    figp.savefig(p_panel, dpi=200, bbox_inches="tight")
    print(f"wrote {p_panel}")

    # Standalone stacked copy (Advanced treatment over De-escalation) for the supplement.
    fig, (A, B) = plt.subplots(2, 1, figsize=(5.4, 10.6))
    panel(A, d, models, 0, "Advanced treatment",
          "clinical-trial mention   (shaded = offered less)",
          harm_negative=True, xlim=(-4.2, 3.6))
    panel(B, d, models, 1, "De-escalation",
          "palliative / best-supportive-care   (shaded = offered more)",
          harm_negative=False, xlim=(-2.0, 7.0))
    fig.tight_layout(rect=(0, 0, 1, 0.99), h_pad=3.0)
    fig.savefig(MAN / "Fig02C_care_intensity_permodel.png", dpi=200, bbox_inches="tight")
    fig.savefig(MAN / "Fig02C_care_intensity_permodel.pdf", bbox_inches="tight")


if __name__ == "__main__":
    main()
