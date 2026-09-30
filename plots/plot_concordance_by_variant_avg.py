"""Supplemental figure — NCCN concordance by demographic label, pooled across all
six models into a single panel for easier visual reading.

Averaging raw per-model rates produces huge error bars because the models sit at
very different concordance levels (~90% vs ~50%); that between-model spread
swamps any demographic effect. Pooling matched (case × model) pairs removes that
nuisance level so a real demographic signal (if any) becomes visible:

  FigS02_concordance_by_variant_avg_paired.png
      pool every (case × model) matched pair; exact-binomial (McNemar) test of
      variant vs reference per label, BH-FDR across labels. Bar = pooled
      concordance rate with Wilson CI.

Run:  python3 plots/plot_concordance_by_variant_avg.py
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"]})
from scipy.stats import binomtest

from src.analyze.response_parser import ResponseParser
from src.analyze.stats import benjamini_hochberg, wilson_ci
from plots.plot_concordance_by_variant import (
    build_ground_truth, MODELS, ORDER, NICE, REFERENCE,
)

OUT = Path("figures/manuscript"); OUT.mkdir(parents=True, exist_ok=True)
BAR_COLOR = "#4C72B0"
BELOW_COLOR = "#BBBBBB"
SES = "#C1272D"; RACE = "#6A51A3"; OTHER = "#1B7837"; REFC = "#666666"
GROUPS = [   # same 9 categories, order and colours as Figure 1B (regen_flip_avg.py)
    ("Income / housing", ["low_income_patient", "unhoused_patient"], SES),
    ("Insurance", ["underinsured_only", "uninsured_only", "medicaid_only", "medicare_only",
                   "medicare_advantage_only"], SES),
    ("Race + disadvantage", ["low_income_black", "black_unhoused", "black_female_medicaid",
                             "latina_female_uninsured"], SES),
    ("Race / ethnicity only", ["black_race_only", "hispanic_race_only", "asian_race_only",
                               "native_american_race_only", "middle_eastern_race_only",
                               "multiracial_race_only"], RACE),
    ("Geography", ["rural_patient", "small_community_hospital"], OTHER),
    ("Immigration / language", ["immigrant_patient", "limited_english_patient"], OTHER),
    ("Gender / sexual identity", ["transgender_woman", "non_binary_patient", "gay_male_patient"], OTHER),
    ("Matched counterexamples", ["black_female_private", "white_female_medicaid"], REFC),
    ("Privileged comparators", ["white_male_private", "high_income_patient"], REFC),
]


def load_all():
    """Return {model: raw_results_dict} for every available model."""
    raws = {}
    for name, path in MODELS.items():
        if not Path(path).exists():
            print("skip", name); continue
        raws[name] = json.loads(Path(path).read_text())
    return raws


# ─────────────── pooled case×model matched-pair (McNemar) ───────────────────
def fig_paired(raws, uniq, cat_map, parser):
    # accumulate over every (case, model): reference vs variant correctness
    correct = {v: 0 for v in ORDER}; total = {v: 0 for v in ORDER}
    b = {v: 0 for v in ORDER}   # ref-correct, var-wrong
    c = {v: 0 for v in ORDER}   # var-correct, ref-wrong
    ref_correct = ref_total = 0
    for name, raw in raws.items():
        for cid in uniq:
            if cid not in raw:
                continue
            exp = cat_map[cid]
            rt = raw[cid].get(REFERENCE, {}).get("response_text", "")
            rcat = parser.parse(rt).category if rt else "unknown"
            r_ok = (rcat == exp) if rcat != "unknown" else None
            if r_ok is not None:
                ref_total += 1; ref_correct += int(r_ok)
            for v in ORDER:
                cat = parser.parse(raw[cid].get(v, {}).get("response_text", "")).category
                if cat == "unknown":
                    continue
                v_ok = (cat == exp)
                total[v] += 1; correct[v] += int(v_ok)
                if r_ok is not None and v_ok != r_ok:
                    if r_ok and not v_ok:
                        b[v] += 1
                    else:
                        c[v] += 1
    ref_rate = 100 * ref_correct / ref_total if ref_total else 0

    praw = {v: (binomtest(b[v], b[v] + c[v], 0.5).pvalue if (b[v] + c[v]) else 1.0) for v in ORDER}
    q = benjamini_hochberg(praw)
    rate = {v: 100 * correct[v] / total[v] if total[v] else 0 for v in ORDER}
    ci = {v: wilson_ci(correct[v], total[v]) if total[v] else (0, 0) for v in ORDER}
    ref_ci = wilson_ci(ref_correct, ref_total)

    # rows grouped into the 9 label categories and colours used in Figure 1
    rows, ylab, ycol, spans = [], [], [], []
    for gname, keys, col in GROUPS:
        start = len(rows)
        for v in keys:
            rows.append(v); ylab.append(NICE[v]); ycol.append(col)
        spans.append((gname, start, len(rows), col))
    assert sorted(rows) == sorted(ORDER) and len(rows) == 28

    fig, ax = plt.subplots(figsize=(7.2, 9.6))
    y = np.arange(len(rows))
    ax.axvspan(100 * ref_ci[0], 100 * ref_ci[1], color="0.88", zorder=0)
    ax.axvline(ref_rate, color="k", ls="--", lw=1.1, zorder=1)
    for i, v in enumerate(rows):
        ax.errorbar(rate[v], i, xerr=[[rate[v] - 100 * ci[v][0]], [100 * ci[v][1] - rate[v]]],
                    fmt="o", ms=6.5, color=ycol[i], ecolor=ycol[i], elinewidth=1.3, capsize=2.5,
                    markeredgecolor="white", markeredgewidth=0.6, zorder=3)
        if q[v] is not None and q[v] < 0.05:
            ax.plot(100 * ci[v][1] + 0.5, i, marker="*", ms=11, color="k", zorder=4)
        elif praw[v] < 0.05:
            ax.plot(100 * ci[v][1] + 0.45, i, marker="o", ms=4, color="k", zorder=4)
    for gname, s0, e0, col in spans:
        if s0:
            ax.axhline(s0 - 0.5, color="#cccccc", lw=0.8, zorder=0)
        ax.text(1.02, (s0 + e0 - 1) / 2, gname.replace(" / ", " /\n") if e0 - s0 <= 2 else gname,
                transform=ax.get_yaxis_transform(), va="center", ha="left",
                fontsize=10, color=col, fontweight="bold", linespacing=1.1)
    ax.set_yticks(y); ax.set_yticklabels(ylab, fontsize=11.5)
    for t, col in zip(ax.get_yticklabels(), ycol):
        t.set_color(col)
    ax.invert_yaxis(); ax.set_ylim(len(rows) - 0.4, -0.6)
    ax.set_xlim(66, 78)
    ax.tick_params(axis="x", labelsize=11); ax.tick_params(axis="y", length=0)
    ax.set_xlabel("NCCN guideline concordance (%)", fontsize=12)
    ax.text(ref_rate, -0.9, f"Reference {ref_rate:.1f}%", ha="center", va="bottom", fontsize=10.5)
    ax.xaxis.grid(True, ls=":", alpha=0.5); ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "FigS02_concordance_by_variant_avg_paired.png", dpi=200, bbox_inches="tight")
    print(f"pooled reference {ref_rate:.2f}% [{100*ref_ci[0]:.2f}, {100*ref_ci[1]:.2f}] (n={ref_total})")
    print("uncorrected P<.05:", [(v, round(rate[v], 2), round(praw[v], 4), round(q[v], 3)) for v in ORDER if praw[v] < 0.05])
    nsig = sum(1 for v in ORDER if q[v] is not None and q[v] < 0.05)
    print("wrote", OUT / "FigS02_concordance_by_variant_avg_paired.png",
          f"(pooled ref={ref_rate:.1f}%; BH-significant labels: {nsig})")

    # Honest diagnostic: how close does anything get? Sort by raw p, show the
    # discordant-pair counts (b=ref-correct/var-wrong, c=var-correct/ref-wrong).
    print("\n  strongest per-label signals (pooled McNemar, sorted by raw p):")
    print(f"    {'label':<26} {'rate':>6} {'delta':>7} {'b':>5} {'c':>5} {'raw p':>8} {'BH q':>8}")
    for v in sorted(ORDER, key=lambda v: praw[v])[:8]:
        qv = q[v]
        print(f"    {v:<26} {rate[v]:5.1f}% {rate[v]-ref_rate:+6.1f} "
              f"{b[v]:5d} {c[v]:5d} {praw[v]:8.3f} {('%.3f'%qv) if qv is not None else '   n/a':>8}")


def main():
    uniq, cat_map = build_ground_truth()
    parser = ResponseParser()
    raws = load_all()
    fig_paired(raws, uniq, cat_map, parser)


if __name__ == "__main__":
    main()
