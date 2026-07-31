"""Two-panel minimalist figure: advanced-care (clinical-trial) vs de-escalation (palliative)
recommendation shifts by demographic label, within-case paired net% vs no_demographics.

Reads results/analysis/advanced_care_by_race.csv (from analyze_advanced_care_by_race.py).
Panel A: clinical-trial mention — bars left of 0 = minorities recommended LESS.
Panel B: palliative/BSC de-escalation — bars right of 0 = minorities recommended MORE.
Same variant order both panels so the race (small, A) vs SES (large, B) split is visible.
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "results/analysis/advanced_care_by_race.csv"
OUT = ROOT / "figures/manuscript"; OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "savefig.facecolor": "white",
    "axes.spines.top": False,
    "axes.spines.right": False,
})

C_HARM = "#8E1B1B"    # dark red — significant shift in the harm direction
C_NULL = "#D9D2C7"    # muted grey-tan — not significant
C_OTHER = "#6A9FB5"   # blue — significant but opposite/benign direction

NICE = {
    "race_only_pooled": "All minorities (pooled)",
    "black_race_only": "Black", "hispanic_race_only": "Hispanic",
    "asian_race_only": "Asian", "native_american_race_only": "Native American",
    "middle_eastern_race_only": "Middle Eastern", "multiracial_race_only": "Multiracial",
    "black_female_medicaid": "Black · Medicaid",
    "latina_female_uninsured": "Latina · uninsured",
    "black_unhoused": "Black · unhoused", "low_income_black": "low-income Black",
    "black_female_private": "Black · private ins.",
    "white_male_private": "White male · private", "white_female_medicaid": "White female · Medicaid",
}
# top→bottom draw order (reversed on the y-axis); grouped
ORDER = [
    "black_female_medicaid", "latina_female_uninsured", "black_unhoused",
    "low_income_black", "black_female_private",
    "race_only_pooled", "black_race_only", "hispanic_race_only", "asian_race_only",
    "native_american_race_only", "middle_eastern_race_only", "multiracial_race_only",
    "white_male_private", "white_female_medicaid",
]


def load():
    return {r["variant"]: r for r in csv.DictReader(open(SRC))}


def _color(net: float, p: float, harm_negative: bool) -> str:
    if p >= 0.05:
        return C_NULL
    harmful = (net < 0) if harm_negative else (net > 0)
    return C_HARM if harmful else C_OTHER


def panel(ax, d, net_key, p_key, title, subtitle, harm_negative):
    ys = list(range(len(ORDER)))[::-1]
    for y, v in zip(ys, ORDER):
        r = d[v]
        net = float(r[net_key]); p = float(r[p_key])
        col = _color(net, p, harm_negative)
        pooled = v == "race_only_pooled"
        ax.barh(y, net, height=0.62, color=col,
                edgecolor="#333" if pooled else "none", linewidth=1.1 if pooled else 0,
                zorder=3)
        if p < 0.05:
            off = 0.09 if net >= 0 else -0.09
            ax.text(net + off, y, "*", ha="left" if net >= 0 else "right",
                    va="center", fontsize=11, color="#333", zorder=4)
    ax.axvline(0, color="#333", lw=0.8, zorder=2)
    ax.set_yticks(ys)
    ax.set_yticklabels([NICE[v] for v in ORDER], fontsize=8.2)
    for lbl, v in zip(ax.get_yticklabels(), ORDER):
        if v == "race_only_pooled":
            lbl.set_fontweight("bold")
        if d[v]["group"] == "reference":
            lbl.set_color("#777"); lbl.set_style("italic")
    ax.set_xlabel("net change vs no-demographics (pp)", fontsize=8.6)
    ax.set_title(title, fontsize=11, fontweight="bold", loc="left", pad=22)
    ax.text(0, 1.012, subtitle, transform=ax.transAxes, fontsize=8.2,
            color="#555", va="bottom")
    ax.tick_params(length=0)
    ax.margins(y=0.01)


def main():
    d = load()
    fig, (A, B) = plt.subplots(1, 2, figsize=(10.2, 5.0), sharey=True)

    panel(A, d, "ct_net", "ct_p",
          "A · Advanced treatment", "clinical-trial mention   (< 0 = offered less)",
          harm_negative=True)
    A.set_xlim(-2.8, 2.2)

    panel(B, d, "pall_net", "pall_p",
          "B · De-escalation", "palliative / best-supportive-care   (> 0 = offered more)",
          harm_negative=False)
    B.set_xlim(-2.0, 6.0)

    # shared minimal legend
    from matplotlib.patches import Patch
    leg = [Patch(fc=C_HARM, label="p<0.05, harm direction"),
           Patch(fc=C_OTHER, label="p<0.05, opposite"),
           Patch(fc=C_NULL, label="n.s.")]
    fig.legend(handles=leg, frameon=False, fontsize=8, ncol=3,
               loc="lower center", bbox_to_anchor=(0.5, -0.02))
    fig.text(0.5, 0.955,
             "Race labels shift advanced-care offers only slightly (A); the large de-escalation "
             "shift tracks socioeconomic disadvantage, not race (B).",
             ha="center", fontsize=8.4, color="#333", style="italic")
    fig.tight_layout(rect=(0, 0.03, 1, 0.94))
    out = OUT / "Fig10_advanced_care_by_race.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    fig.savefig(out.with_suffix(".pdf"), bbox_inches="tight")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
