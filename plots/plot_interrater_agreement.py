#!/usr/bin/env python3
"""Human-vs-human inter-rater agreement, Packet B (classifier-flagged/contested
subset, n=60). Rater1 = study author, Rater2 = Bhavneet Bhinder (co-author),
both blinded to variant. Companion to Figure S6 (classifier/judge vs single
human rater) -- this is the first plot of rater-vs-rater agreement itself.

Non-destructive: writes panels/p_interrater_agreement.png. Run from repo root.
"""
from pathlib import Path
import csv
from collections import Counter
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

LABEL_COL = "your_label (APPROPRIATE/STIGMA)"
PANELS = Path("figures/manuscript_combined/panels")
OUT_PANEL = PANELS / "p_interrater_agreement.png"

RED = "#C1272D"


def _load(path):
    d = {}
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            lab = (row.get(LABEL_COL) or "").strip()
            if lab:
                d[row["id"]] = lab
    return d


def _kappa(a, b):
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return po, (po - pe) / (1 - pe) if pe != 1 else 1.0


def main():
    r1 = _load("adjudication/gold_flagged_rater1.csv")
    r2 = _load("adjudication/gold_flagged_rater2.csv")
    common = sorted(set(r1) & set(r2))
    c = Counter((r1[i], r2[i]) for i in common)
    n = len(common)

    a = [1 if r1[i] == "STIGMA" else 0 for i in common]
    b = [1 if r2[i] == "STIGMA" else 0 for i in common]
    agreement, kappa = _kappa(a, b)

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(9.5, 4.0), gridspec_kw={"width_ratios": [1, 1.5]}
    )

    # ---- Panel A: 2x2 confusion matrix ----
    labels = ["APPROPRIATE", "STIGMA"]
    mat = np.array([
        [c[("APPROPRIATE", "APPROPRIATE")], c[("APPROPRIATE", "STIGMA")]],
        [c[("STIGMA", "APPROPRIATE")], c[("STIGMA", "STIGMA")]],
    ])
    vmax = mat.max()
    for i in range(2):
        for j in range(2):
            v = mat[i, j]
            shade = 0.15 + 0.65 * (v / vmax)
            ax1.add_patch(plt.Rectangle((j, 1 - i), 1, 1, facecolor=RED, alpha=shade,
                                         edgecolor="white", linewidth=2))
            text_color = "white" if shade > 0.55 else "#333333"
            ax1.text(j + 0.5, 1.5 - i, str(v), ha="center", va="center",
                      fontsize=20, fontweight="bold", color=text_color)
    ax1.set_xlim(0, 2); ax1.set_ylim(0, 2)
    ax1.set_xticks([0.5, 1.5]); ax1.set_yticks([0.5, 1.5])
    ax1.set_xticklabels(labels, fontsize=9)
    ax1.set_yticklabels(labels[::-1], fontsize=9, rotation=90, va="center")
    ax1.set_xlabel("Bhavneet (rater 2)", fontsize=9.5)
    ax1.set_ylabel("Alvaro (rater 1)", fontsize=9.5)
    ax1.set_title(f"n = {n} contested-subset items", fontsize=9.5, pad=8)
    for spine in ax1.spines.values():
        spine.set_visible(False)
    ax1.tick_params(length=0)

    # ---- Panel B: kappa on the standard interpretation scale ----
    bands = [
        (0.00, 0.20, "#f2f2f2", "slight"),
        (0.20, 0.40, "#e0e0e0", "fair"),
        (0.40, 0.60, "#cccccc", "moderate"),
        (0.60, 0.80, "#f6c6c6", "substantial"),
        (0.80, 1.00, "#e39494", "almost\nperfect"),
    ]
    for lo, hi, color, label in bands:
        ax2.barh(0, hi - lo, left=lo, height=0.5, color=color, edgecolor="white")
        ax2.text((lo + hi) / 2, -0.55, label, ha="center", va="top", fontsize=7.5, color="#555555")
    ax2.text(kappa, 0.42, f"κ = {kappa:.3f}\n{agreement*100:.1f}% agreement",
              ha="center", va="bottom", fontsize=10, fontweight="bold", color=RED)
    ax2.set_xlim(0, 1)
    ax2.set_ylim(-0.9, 0.9)
    ax2.set_yticks([])
    ax2.set_xlabel("Cohen's kappa (Landis & Koch bands)", fontsize=9.5)
    ax2.set_title("Rater 1 vs. rater 2 agreement", fontsize=9.5, pad=8)
    for spine in ["top", "right", "left"]:
        ax2.spines[spine].set_visible(False)

    fig.suptitle("Inter-rater agreement, contested/classifier-flagged subset (Packet B)",
                  fontsize=11.5, fontweight="bold", y=1.02)
    fig.tight_layout()
    PANELS.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PANEL, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote {OUT_PANEL}")
    print(f"agreement={agreement*100:.1f}%  kappa={kappa:.3f}  n={n}")
    print("confusion matrix (rows=rater1, cols=rater2):")
    print(mat)


if __name__ == "__main__":
    main()
