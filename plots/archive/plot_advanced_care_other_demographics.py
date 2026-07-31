"""Supplementary two-panel figure: advanced-care (clinical-trial) vs de-escalation (palliative)
recommendation shifts across the NON-race demographic axes — insurance/SES, geography,
immigration/language, and gender/sexual minority. Within-case paired net% vs no_demographics.

Companion to Fig10 (race). Reads results/analysis/advanced_care_by_demographic.csv.
Panel A: clinical-trial mention — bars left of 0 = variant recommended LESS advanced treatment.
Panel B: palliative/BSC de-escalation — bars right of 0 = variant recommended MORE de-escalation.
Same variant order both panels; high-income / white-private controls anchored at the bottom.
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "results/analysis/advanced_care_by_demographic.csv"
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
    "uninsured_only": "uninsured", "medicaid_only": "Medicaid",
    "underinsured_only": "underinsured", "medicare_only": "Medicare",
    "medicare_advantage_only": "Medicare Advantage", "low_income_patient": "low-income",
    "high_income_patient": "high-income", "unhoused_patient": "unhoused",
    "rural_patient": "rural", "small_community_hospital": "community hospital",
    "immigrant_patient": "immigrant", "limited_english_patient": "limited-English",
    "non_binary_patient": "non-binary", "transgender_woman": "transgender woman",
    "gay_male_patient": "gay male",
    "white_male_private": "White male · private", "white_female_medicaid": "White female · Medicaid",
}
# section header rows (blank spacers) -> label; drawn top→bottom
SECTIONS = [
    ("insurance / SES", ["unhoused_patient", "medicaid_only", "medicare_only",
                          "medicare_advantage_only", "underinsured_only", "uninsured_only",
                          "low_income_patient", "high_income_patient"]),
    ("geography / access", ["small_community_hospital", "rural_patient"]),
    ("immigration / language", ["limited_english_patient", "immigrant_patient"]),
    ("gender / sexual minority", ["transgender_woman", "gay_male_patient", "non_binary_patient"]),
    ("reference", ["white_male_private", "white_female_medicaid"]),
]


def load():
    return {r["variant"]: r for r in csv.DictReader(open(SRC))}


def _color(net: float, p: float, harm_negative: bool) -> str:
    if p >= 0.05:
        return C_NULL
    harmful = (net < 0) if harm_negative else (net > 0)
    return C_HARM if harmful else C_OTHER


def _rows():
    """Yield (y, kind, key) top→bottom; variant order preserved, no section headers."""
    items = [("bar", v) for _, vks in SECTIONS for v in vks]
    n = len(items)
    for i, (kind, key) in enumerate(items):
        yield n - 1 - i, kind, key   # top row highest y


def panel(ax, d, net_key, p_key, title, subtitle, harm_negative, xlim):
    ytick, ylab = [], []
    all_y = [y for y, _, _ in _rows()]
    for y, kind, key in _rows():
        r = d[key]
        net = float(r[net_key]); p = float(r[p_key])
        ax.barh(y, net, height=0.66, color=_color(net, p, harm_negative), zorder=3)
        if p < 0.05:
            off = 0.12 if net >= 0 else -0.12
            ax.text(net + off, y, "*", ha="left" if net >= 0 else "right",
                    va="center", fontsize=10.5, color="#333", zorder=4)
        ytick.append(y); ylab.append(NICE[key])
    ax.axvline(0, color="#333", lw=0.8, zorder=2)
    ax.set_yticks(ytick); ax.set_yticklabels(ylab, fontsize=8.2)
    for lbl, (_, kind, key) in zip(ax.get_yticklabels(),
                                   [(y, k, v) for y, k, v in _rows() if k == "bar"]):
        if d[key]["group"] == "reference":
            lbl.set_color("#777"); lbl.set_style("italic")
    ax.set_xlim(*xlim)
    ax.set_xlabel("net change vs no-demographics (pp)", fontsize=8.6)
    ax.set_title(title, fontsize=11, fontweight="bold", loc="left", pad=22)
    ax.text(0, 1.012, subtitle, transform=ax.transAxes, fontsize=8.2,
            color="#555", va="bottom")
    ax.tick_params(length=0)
    ax.set_ylim(min(all_y) - 0.7, max(all_y) + 0.9)


def main():
    d = load()
    fig, (A, B) = plt.subplots(1, 2, figsize=(10.6, 5.4), sharey=True)

    panel(A, d, "ct_net", "ct_p",
          "A · Advanced treatment", "clinical-trial mention   (< 0 = offered less)",
          harm_negative=True, xlim=(-3.9, 3.4))
    panel(B, d, "pall_net", "pall_p",
          "B · De-escalation", "palliative / best-supportive-care   (> 0 = offered more)",
          harm_negative=False, xlim=(-1.6, 6.6))

    from matplotlib.patches import Patch
    leg = [Patch(fc=C_HARM, label="p<0.05, harm direction"),
           Patch(fc=C_OTHER, label="p<0.05, opposite / benign"),
           Patch(fc=C_NULL, label="n.s.")]
    fig.legend(handles=leg, frameon=False, fontsize=8, ncol=3,
               loc="lower center", bbox_to_anchor=(0.5, -0.015))
    fig.tight_layout(rect=(0, 0.03, 1, 0.97))
    out = OUT / "FigS6_advanced_care_other_demographics.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    fig.savefig(out.with_suffix(".pdf"), bbox_inches="tight")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
