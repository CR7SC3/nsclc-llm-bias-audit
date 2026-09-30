"""Supplement figure: two-vendor mitigation-ladder OVERCORRECTION panel.

Message: naive prompt mitigation drives generated STIGMA to ~0 ONLY by also
erasing WARRANTED SES-responsive care -- the two collapse together. Holds
across two independent vendors (DeepSeek-chat, Gemini-2.5-flash) and every
prompt strategy tested. This is a Discussion/supplement figure supporting
the paper's mitigation-ladder proof-of-concept (see project memory
paper1_mitigation_decision.md): the ladder is NOT a headline win, it is
evidence that naive mitigation is a blunt instrument.

Data source: blinded Sonnet-4.6 judge (PRIMARY estimator), rates are % of
SES-variant x case pairs judged, pooled over the 7 SES variants, n=151 cases
per vendor. Numbers hardcoded per instruction (final, not recomputed here).

Reference/control convention: baseline arm here already reflects the
no_demographics-anchored SES-variant comparison used throughout the paper
(see project memory no_demographics_reference.md) -- there is no
white_male_private row in this figure.

Writes figures/manuscript/FigS11_mitigation_overcorrection.png
Run:  python3 plots/plot_mitigation_overcorrection.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "figures/manuscript"
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "savefig.facecolor": "white",
    "axes.spines.top": False,
    "axes.spines.right": False,
})

# CVD-safe + grayscale-separable: stigma = warm red (matches Fig-series
# C_SES / "Hallucinated SDOH" hue family used elsewhere), warranted care =
# cool blue (matches the "prognosis framing" / benign-dimension hue family).
C_STIGMA = "#C0392B"   # same red/blue as Figure 4A   # warm red -- want this LOW
C_CARE = "#7FB3D5"     # cool blue -- should stay HIGH but doesn't

ARMS = [
    ("baseline", "Baseline"),
    ("fairness", "Fairness"),
    ("structured_extraction", "Structured\nextraction"),
    ("counterfactual_check", "Counter-\nfactual\ncheck"),
    ("stigma_targeted", "Stigma\ntargeted"),
]

DATA = {
    "DeepSeek-chat": {
        "baseline": (17.1, 65.0),
        "fairness": (1.6, 18.3),
        "counterfactual_check": (0.0, 0.2),
        "structured_extraction": (0.0, 0.0),
        "stigma_targeted": (0.0, 0.0),
    },
    "Gemini-2.5-flash": {
        "baseline": (23.9, 59.1),
        "fairness": (0.1, 0.1),
        "counterfactual_check": (0.1, 0.2),
        "structured_extraction": (0.1, 0.0),
        "stigma_targeted": (0.0, 0.0),
    },
}

# arm, vendor for which the decision was unscorable due to output-format
# parser failure (descriptive care/stigma rates still shown, but flagged).
UNSCORABLE = {("Gemini-2.5-flash", "structured_extraction")}


PANEL_LETTER = {"DeepSeek-chat": "A", "Gemini-2.5-flash": "B"}


def draw_panel(ax, vendor):
    d = DATA[vendor]
    n = len(ARMS)
    x = np.arange(n)
    w = 0.36

    stigma_vals = [d[k][0] for k, _ in ARMS]
    care_vals = [d[k][1] for k, _ in ARMS]

    bars_s = ax.bar(x - w / 2, stigma_vals, width=w, color=C_STIGMA,
                     edgecolor="k", linewidth=0.5, label="Stigmatizing language", zorder=3)
    bars_c = ax.bar(x + w / 2, care_vals, width=w, color=C_CARE,
                     edgecolor="k", linewidth=0.5, label="Appropriate care", zorder=3)

    # baseline guide line at baseline warranted-care level
    base_care = d["baseline"][1]
    ax.axhline(base_care, color="#555555", lw=1.0, ls="--", alpha=0.7, zorder=1)

    # value labels
    for rect, val in zip(bars_s, stigma_vals):
        ax.text(rect.get_x() + rect.get_width() / 2, val + 1.0, f"{val:.1f}",
                ha="center", va="bottom", fontsize=10.5, color="#7a1f1f")
    for rect, val in zip(bars_c, care_vals):
        ax.text(rect.get_x() + rect.get_width() / 2, val + 1.0, f"{val:.1f}",
                ha="center", va="bottom", fontsize=10.5, color="#1f3b57")

    # unscorable-arm footnote marker
    for i, (key, _) in enumerate(ARMS):
        if (vendor, key) in UNSCORABLE:
            ax.text(x[i], -9.5, "*", ha="center", va="top", fontsize=15,
                    color="#333", fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels([lbl for _, lbl in ARMS], fontsize=11)
    ax.set_ylim(0, 70)
    ax.set_title(vendor, fontsize=13, fontweight="bold", pad=8)
    ax.text(-0.02, 1.06, PANEL_LETTER[vendor], transform=ax.transAxes, fontsize=16,
            fontweight="bold", ha="right", va="bottom")
    ax.tick_params(axis="y", labelsize=11)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(length=0)


def main():
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.8), sharey=True)

    for ax, vendor in zip(axes, DATA):
        draw_panel(ax, vendor)

    axes[0].set_ylabel("Socioeconomic label \u00d7 case pairs, %", fontsize=12)

    handles, labels = axes[0].get_legend_handles_labels()
    axes[1].legend(handles, labels, loc="center right", fontsize=11.5, frameon=False)

    fig.tight_layout(rect=(0, 0.02, 1, 0.97))

    out_path = OUT / "FigS11_mitigation_overcorrection.png"
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
