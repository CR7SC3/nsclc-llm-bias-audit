"""EquityGUIDE — continuous (1–10) equity-score figure.

Visualizes the headline DeepSeek result: implicit soft-bias *framing* shifts
strongly across demographics (and survives BH-FDR), while the model's explicit
1–10 ratings do not. Two panels share the demographic y-axis:

  Left  — soft-bias framing intensity Δ vs no_demographics (95% CI), FDR-sig highlighted.
  Right — aggressive-systemic-therapy eligibility Δ (model-emitted rating), same scale.

Usage
-----
    venv/bin/python plot_continuous_scores.py
    venv/bin/python plot_continuous_scores.py --format pdf
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

ANALYSIS = Path("results/analysis")
FIGURES  = Path("figures")
SOFT_CSV   = ANALYSIS / "v2_genie_bpc_nsclc_pilot50_deepseek-chat_soft_intensity.csv"
RATING_CSV = ANALYSIS / "v2_genie_bpc_nsclc_pilot50_deepseek-chat_rating_rating_aggressive.csv"

SIG_COLOR  = "#c0392b"   # FDR-significant
NS_COLOR   = "#aab7c4"   # not significant
REF        = "no_demographics"


def _load(path: Path) -> dict[str, dict]:
    out = {}
    with open(path, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["variant"] == REF:
                continue
            out[r["variant"]] = {
                "delta": float(r["delta"]),
                "lo":    float(r["ci_low"]),
                "hi":    float(r["ci_high"]),
                "q":     float(r["q_value_bh"]) if r.get("q_value_bh") else None,
            }
    return out


def _panel(ax, data: dict[str, dict], order: list[str], title: str, xlabel: str) -> None:
    ys = range(len(order))
    for y, v in zip(ys, order):
        d = data.get(v)
        if not d:
            continue
        sig = d["q"] is not None and d["q"] < 0.05
        color = SIG_COLOR if sig else NS_COLOR
        # CI as error bar around the delta
        ax.errorbar(d["delta"], y,
                    xerr=[[d["delta"] - d["lo"]], [d["hi"] - d["delta"]]],
                    fmt="o", color=color, ecolor=color, elinewidth=1.4,
                    capsize=2.5, markersize=5, zorder=3)
        if sig:
            ax.annotate("★", (d["hi"], y), xytext=(4, 0),
                        textcoords="offset points", va="center",
                        color=SIG_COLOR, fontsize=9)
    ax.axvline(0, color="#333333", lw=1, zorder=1)
    ax.set_yticks(list(ys))
    ax.set_yticklabels(order, fontsize=8)
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.set_xlabel(xlabel, fontsize=9)
    ax.grid(axis="x", color="#eeeeee", zorder=0)
    ax.invert_yaxis()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--format", default="png", choices=["png", "pdf"])
    args = ap.parse_args()

    soft   = _load(SOFT_CSV)
    rating = _load(RATING_CSV)

    # Order variants by soft-bias delta (descending = most disadvantaging at top)
    order = sorted(soft, key=lambda v: soft[v]["delta"], reverse=True)

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(12, 9), sharey=True)

    _panel(axL, soft, order,
           "Implicit soft-bias framing",
           "Δ disadvantage-framing dimensions vs no-demographics")
    _panel(axR, rating, order,
           "Explicit model rating",
           "Δ aggressive-systemic eligibility (1–10)")
    axR.tick_params(labelleft=False)

    legend = [
        mpatches.Patch(color=SIG_COLOR, label="BH-FDR significant (q < 0.05)"),
        mpatches.Patch(color=NS_COLOR,  label="not significant"),
    ]
    fig.legend(handles=legend, loc="lower center", ncol=2, frameon=False,
               fontsize=9, bbox_to_anchor=(0.5, -0.01))

    fig.suptitle(
        "DeepSeek bias is in implicit framing, not explicit ratings\n"
        "GENIE BPC NSCLC pilot (n=50 cases × 29 demographic variants, paired vs no-demographics)",
        fontsize=12.5, fontweight="bold",
    )
    fig.tight_layout(rect=(0, 0.02, 1, 0.96))

    FIGURES.mkdir(exist_ok=True)
    out = FIGURES / f"fig_continuous_scores_deepseek.{args.format}"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
