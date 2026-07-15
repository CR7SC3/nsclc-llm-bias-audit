"""Supplemental figure — NCCN concordance by demographic label, pooled across all
six models into a single panel for easier visual reading.

Averaging raw per-model rates produces huge error bars because the models sit at
very different concordance levels (~90% vs ~50%); that between-model spread
swamps any demographic effect. Pooling matched (case × model) pairs removes that
nuisance level so a real demographic signal (if any) becomes visible:

  FigS_concordance_by_variant_avg_paired.png
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
import matplotlib.pyplot as plt
from scipy.stats import binomtest

from src.analyze.response_parser import ResponseParser
from src.analyze.stats import benjamini_hochberg, wilson_ci
from plots.plot_concordance_by_variant import (
    build_ground_truth, MODELS, ORDER, NICE, REFERENCE,
)

OUT = Path("figures/manuscript"); OUT.mkdir(parents=True, exist_ok=True)
BAR_COLOR = "#4C72B0"
BELOW_COLOR = "#BBBBBB"


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
    order = sorted(ORDER, key=lambda v: rate[v])

    fig, ax = plt.subplots(figsize=(9.5, 10.5))
    y = np.arange(len(order))
    lo = [rate[v] - 100 * ci[v][0] for v in order]
    hi = [100 * ci[v][1] - rate[v] for v in order]
    colors = [BAR_COLOR if rate[v] >= ref_rate else BELOW_COLOR for v in order]
    ax.barh(y, [rate[v] for v in order], xerr=[lo, hi],
            error_kw=dict(ecolor="0.3", lw=0.9, capsize=2),
            color=colors, edgecolor="k", linewidth=0.4)
    for i, v in enumerate(order):
        sx = 100 * ci[v][1] + 1.5
        if q[v] is not None and q[v] < 0.05:
            ax.text(sx, i, "★", va="center", fontsize=12, color="#B8860B")
        elif praw[v] < 0.05:
            ax.text(sx, i, "☆", va="center", fontsize=12, color="#B8860B")
    ax.set_yticks(y); ax.set_yticklabels([NICE[v] for v in order], fontsize=9)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_title("NCCN concordance by demographic label",
                 fontsize=12.5, fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUT / "FigS_concordance_by_variant_avg_paired.png", dpi=150, bbox_inches="tight")
    nsig = sum(1 for v in ORDER if q[v] is not None and q[v] < 0.05)
    print("wrote", OUT / "FigS_concordance_by_variant_avg_paired.png",
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
