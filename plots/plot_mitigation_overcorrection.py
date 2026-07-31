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
C_STIGMA = "#D96666"   # warm red -- want this LOW
C_CARE = "#4C72B0"     # cool blue -- should stay HIGH but doesn't

ARMS = [
    ("baseline", "baseline"),
    ("fairness", "fairness"),
    ("structured_extraction", "structured\nextraction"),
    ("counterfactual_check", "counterfactual\ncheck"),
    ("stigma_targeted", "stigma-\ntargeted"),
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
                     edgecolor="k", linewidth=0.5, label="Generated stigma", zorder=3)
    bars_c = ax.bar(x + w / 2, care_vals, width=w, color=C_CARE,
                     edgecolor="k", linewidth=0.5, label="Warranted SES-responsive care", zorder=3)

    # baseline guide line at baseline warranted-care level
    base_care = d["baseline"][1]
    ax.axhline(base_care, color=C_CARE, lw=1.0, ls="--", alpha=0.55, zorder=1)
    ax.text(n - 1 + w / 2 + 0.12, base_care, f"baseline\ncare = {base_care:.1f}%",
            fontsize=7.2, color=C_CARE, va="center", ha="left", alpha=0.85)

    # value labels
    for rect, val in zip(bars_s, stigma_vals):
        ax.text(rect.get_x() + rect.get_width() / 2, val + 1.0, f"{val:.1f}",
                ha="center", va="bottom", fontsize=8.2, fontweight="bold", color="#7a1f1f")
    for rect, val in zip(bars_c, care_vals):
        ax.text(rect.get_x() + rect.get_width() / 2, val + 1.0, f"{val:.1f}",
                ha="center", va="bottom", fontsize=8.2, fontweight="bold", color="#2b3f66")

    # unscorable-arm footnote marker
    for i, (key, _) in enumerate(ARMS):
        if (vendor, key) in UNSCORABLE:
            ax.text(x[i], -6.5, "*", ha="center", va="top", fontsize=13,
                    color="#333", fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels([lbl for _, lbl in ARMS], fontsize=9)
    ax.set_ylim(0, 70)
    ax.set_title(f"({PANEL_LETTER[vendor]})  {vendor}", fontsize=10.5, fontweight="bold", pad=8)
    ax.tick_params(axis="y", labelsize=8.5)
    ax.tick_params(length=0)


def main():
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 5.0), sharey=True)

    for ax, vendor in zip(axes, DATA):
        draw_panel(ax, vendor)

    axes[0].set_ylabel("% of SES-variant x case pairs (blinded judge)", fontsize=9.5)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=2, fontsize=9,
               frameon=False, bbox_to_anchor=(0.5, 1.02))

    fig.suptitle("Naive prompt mitigation erases warranted care while removing stigma "
                 "(both vendors)", fontsize=12, fontweight="bold", y=1.10)

    fig.text(0.5, -0.04,
              "* Gemini structured_extraction: NCCN decision unscorable (output format); "
              "care/stigma rates shown are still descriptively valid.\n"
              "Blinded Sonnet-4.6 judge, primary estimator; rates pooled over 7 SES variants, "
              "n=151 cases per vendor. Reference row = no_demographics (definitional zero anchor).",
              ha="center", va="top", fontsize=7.4, color="#555555", style="italic")

    fig.tight_layout(rect=(0, 0.02, 1, 1))

    out_path = OUT / "FigS11_mitigation_overcorrection.png"
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
