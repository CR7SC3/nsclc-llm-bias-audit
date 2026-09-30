"""Bias decision-tree manuscript figures.

Two figures, recomputed from the driver's compact summary + the human label set:

  FigS10_bias_tree_decomposition.png        (2x2)  A precision-filter + harm-typology story
    A  reclassification of regex flags (STIGMA / contextual / appropriate)
    B  per-stratum STIGMA rate, regex vs tree, Wilson 95% CI (the control collapse)
    C  harm-type decomposition per stratum (descriptive — unvalidated)
    D  Gate-2 ablation: 'a demographic label is not grounding' (counterfactual effect)

  FigS06_bias_tree_validation.png   agreement vs the human rater (tree / regex / judge)

Inputs : results/analysis/bias_tree_stratum_summary.csv  (written by run_bias_tree.py)
         adjudication/gold_random_rater1_alvaro.csv + random_judge_{items,labels}
Run    : python scripts/nsclc/run_bias_tree.py   # first, to refresh the summary
         python plots/plot_bias_tree.py
Output : figures/manuscript/FigS10_bias_tree_decomposition.png , FigS06_bias_tree_validation.png
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import csv
import json
import math
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from src.analyze.bias_tree import classify

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "figures/manuscript"; OUT.mkdir(parents=True, exist_ok=True)
SUMMARY = ROOT / "results/analysis/bias_tree_stratum_summary.csv"

# Unified typography across all Fig-5 panels (A/B/C/D): one family, one size.
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans"],
    "font.size": 10,
    "savefig.facecolor": "white",
    "axes.spines.top": False,
    "axes.spines.right": False,
})

# strata display order (disadvantage → control) + nice labels
ORDER = ["unhoused", "black_unhoused", "low_income", "underinsured", "uninsured",
         "race_only", "control"]
NICE = {"unhoused": "unhoused", "black_unhoused": "Black +\nunhoused",
        "low_income": "low\nincome", "underinsured": "under-\ninsured",
        "uninsured": "uninsured", "race_only": "race\nonly", "control": "control"}

C_TREE = "#E69F00"      # orange — robustness condition (non-model palette; was red -> clashed with DeepSeek)
C_REGEX = "#adadad"     # gray baseline — raw regex flags (shared baseline color)
C_ALLOC = "#8E1B1B"; C_EPIST = "#D65C5C"; C_DIGN = "#E8A87C"
C_STIG = "#8E1B1B"; C_CTX = "#E8A87C"; C_APP = "#C9B79C"
C_LABEL = "#6A9FB5"     # note+label ablation


def _wilson(k, n, z=1.96):
    if n == 0:
        return 0.0, 0.0, 0.0
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / d
    return p, max(0.0, c - h), min(1.0, c + h)


def load():
    rows = {r["stratum"]: {k: int(v) if k != "stratum" else v for k, v in r.items()}
            for r in csv.DictReader(open(SUMMARY))}
    return rows


def fig_main(d):
    """eFigure 10: 2 x 2 decision-tree decomposition. Titleless (panel letters only);
    strata run control -> most disadvantaged, as in eFigure 2D; Helvetica, 11-12 pt."""
    _rc = plt.rcParams.copy()
    plt.rcParams.update({"font.family": "sans-serif",
                         "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"], "font.size": 12})
    LBL = {"unhoused": "Unhoused", "black_unhoused": "Black +\nunhoused",
           "low_income": "Low\nincome", "underinsured": "Under-\ninsured",
           "uninsured": "Un-\ninsured", "race_only": "Race /\nethnicity\nonly", "control": "Control"}
    LBL["unhoused"] = "Un-\nhoused"
    order = list(reversed(ORDER))
    fig, ax = plt.subplots(2, 2, figsize=(11.6, 8.4))
    A, B, C, D = ax[0, 0], ax[0, 1], ax[1, 0], ax[1, 1]

    # --- A: reclassification of all keyword-classifier flags -------------------
    tot_flag = sum(d[s]["regex_flagged"] for s in d)
    stig = sum(d[s]["tree_stigma"] for s in d)
    reclass = tot_flag - stig
    parts = [("Retained as\nstigmatizing", stig, C_STIG, "white"),
             ("Reclassified\nas benign", reclass, C_APP, "#333")]
    left = 0
    for lab, val, col, tc in parts:
        A.barh(0, val, left=left, color=col, edgecolor="white")
        A.text(left + val / 2, 0, f"{lab}\n{val:,} ({100*val/tot_flag:.0f}%)",
               ha="center", va="center", fontsize=12, color=tc)
        left += val
    A.set_xlim(0, tot_flag); A.set_ylim(-0.6, 0.6)
    A.set_yticks([]); A.set_xlabel("Responses flagged by the keyword classifier, No.")
    A.spines["left"].set_visible(False)

    # --- B: stigma rate by stratum, keyword classifier vs tree, Wilson CI -------
    xs = range(len(order)); w = 0.38
    for i, s in enumerate(order):
        rp, rlo, rhi = _wilson(d[s]["regex_flagged"], d[s]["total"])
        tp, tlo, thi = _wilson(d[s]["tree_stigma"], d[s]["total"])
        B.bar(i - w/2, 100*rp, w, color=C_REGEX, edgecolor="k", linewidth=0.4,
              yerr=[[100*(rp-rlo)], [100*(rhi-rp)]], capsize=2, ecolor="#555",
              label="Keyword classifier" if i == 0 else None)
        B.bar(i + w/2, 100*tp, w, color=C_TREE, edgecolor="k", linewidth=0.4,
              yerr=[[100*(tp-tlo)], [100*(thi-tp)]], capsize=2, ecolor="#555",
              label="Decision tree" if i == 0 else None)
    B.set_xticks(list(xs)); B.set_xticklabels([LBL[s] for s in order], fontsize=10.5)
    B.set_ylabel("Stigmatizing-language rate (%)")
    B.legend(frameon=False, fontsize=11, loc="upper left")

    # --- C: harm-type decomposition (descriptive) ------------------------------
    strata_c = [s for s in order if d[s]["tree_stigma"] > 0]
    for i, s in enumerate(strata_c):
        n = d[s]["total"]
        a = 100*d[s]["allocative"]/n; e = 100*d[s]["epistemic"]/n; g = 100*d[s]["dignitary"]/n
        C.bar(i, a, color=C_ALLOC, label="Allocative" if i == 0 else None)
        C.bar(i, e, bottom=a, color=C_EPIST, label="Epistemic" if i == 0 else None)
        C.bar(i, g, bottom=a+e, color=C_DIGN, label="Dignitary" if i == 0 else None)
    C.set_xticks(range(len(strata_c))); C.set_xticklabels([LBL[s] for s in strata_c], fontsize=10.5)
    C.set_ylabel("Stigmatizing-language rate\nby harm type (%)")
    C.legend(frameon=False, fontsize=11, loc="upper left")

    # --- D: label-as-grounding ablation ---------------------------------------
    strata_d = [s for s in order if s != "race_only"]
    w = 0.38
    for i, s in enumerate(strata_d):
        note = 100*d[s]["tree_stigma"]/d[s]["total"]
        lbl = 100*d[s]["tree_stigma_withlabel"]/d[s]["total"]
        D.bar(i - w/2, note, w, color=C_TREE, edgecolor="k", linewidth=0.4,
              label="Label not counted as grounding (primary)" if i == 0 else None)
        D.bar(i + w/2, lbl, w, color=C_LABEL, edgecolor="k", linewidth=0.4,
              label="Label counted as grounding" if i == 0 else None)
    D.set_xticks(range(len(strata_d))); D.set_xticklabels([LBL[s] for s in strata_d], fontsize=10.5)
    D.set_ylabel("Stigmatizing-language rate (%)")
    D.legend(frameon=False, fontsize=11, loc="upper left")

    for axx, letter in ((A, "A"), (B, "B"), (C, "C"), (D, "D")):
        for sp in ("top", "right"):
            axx.spines[sp].set_visible(False)
        axx.text(-0.12, 1.04, letter, transform=axx.transAxes, fontsize=16,
                 fontweight="bold", va="bottom")
    fig.tight_layout(h_pad=2.2, w_pad=2.5)
    out = OUT / "FigS10_bias_tree_decomposition.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    plt.rcParams.update(_rc)
    print(f"Wrote {out}")
    for s in order:
        print(f"  {s:15s} keyword {100*d[s]['regex_flagged']/d[s]['total']:.2f}%  tree {100*d[s]['tree_stigma']/d[s]['total']:.2f}%"
              f"  tree+label {100*d[s]['tree_stigma_withlabel']/d[s]['total']:.2f}%")
    print(f"  flagged {tot_flag}, retained {stig}, reclassified {reclass}")


def fig_panel_B(d):
    """Standalone version of sub-panel B (regex vs. tree, control collapse) for use as
    the single Figure 5D panel. combine_figures.py stamps the outer 'D' letter, so no
    sub-letter here; the finding stays in the caption."""
    order = list(reversed(ORDER))   # control -> most disadvantaged, as in panels A to C
    _rc = plt.rcParams.copy()
    plt.rcParams.update({"font.family": "sans-serif",
                         "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
                         "font.size": 14})
    fig, B = plt.subplots(figsize=(8.0, 4.8))
    xs = range(len(order))
    w = 0.38
    for i, s in enumerate(order):
        rp, rlo, rhi = _wilson(d[s]["regex_flagged"], d[s]["total"])
        tp, tlo, thi = _wilson(d[s]["tree_stigma"], d[s]["total"])
        B.bar(i - w/2, 100*rp, w, color=C_REGEX, edgecolor="k", linewidth=0.5,
              yerr=[[100*(rp-rlo)], [100*(rhi-rp)]], capsize=2, ecolor="#888",
              label="Keyword classifier" if i == 0 else None)
        B.bar(i + w/2, 100*tp, w, color=C_TREE, edgecolor="k", linewidth=0.5,
              yerr=[[100*(tp-tlo)], [100*(thi-tp)]], capsize=2, ecolor="#555",
              label="Decision tree" if i == 0 else None)
    # single-line labels so the standardized 30° tilt reads cleanly (fig_main keeps NICE two-line)
    FLAT = {"unhoused": "Unhoused", "black_unhoused": "Black + unhoused",
            "low_income": "Low income", "underinsured": "Underinsured",
            "uninsured": "Uninsured", "race_only": "Race / ethnicity only", "control": "Control"}
    B.set_xticks(list(xs)); B.set_xticklabels([FLAT[s] for s in order], rotation=40,
                                              ha="right", rotation_mode="anchor", fontsize=13)
    B.set_ylabel("Stigmatizing-language rate (%)", fontsize=14)
    B.set_yticks(range(0, 51, 10)); B.tick_params(axis="y", labelsize=14)
    B.set_title("All 6 models", fontsize=14, fontweight="bold")
    B.grid(axis="y", alpha=0.25); B.set_axisbelow(True)
    B.legend(framealpha=0.95, loc="upper left", fontsize=11)
    # full box around the axes (match panels A/B/C); global rcParams hide top/right
    for sp in B.spines.values():
        sp.set_visible(True)
    # fixed geometry so all Fig-5 panels share one height and their x-axes align
    # (single-axis box, identical to panel A). No tight bbox.
    B.set_position([0.105, 0.26, 0.88, 0.64])
    PANELS = ROOT / "figures/manuscript_combined/panels"; PANELS.mkdir(parents=True, exist_ok=True)
    fig.savefig(PANELS / "p_bias_tree.png", dpi=200)
    plt.close(fig)
    plt.rcParams.update(_rc)   # leave the other bias-tree figures on their own style
    print(f"Wrote {PANELS/'p_bias_tree.png'} (sub-panel B only)")


def fig_validation():
    """Agreement vs the human rater on the classifier-blind random set."""
    items = {json.loads(l)["id"]: json.loads(l)
             for l in (ROOT / "adjudication/random_judge_items.jsonl").read_text().splitlines() if l.strip()}
    judge = json.loads((ROOT / "adjudication/random_judge_labels.json").read_text())
    rows = list(csv.DictReader(open(ROOT / "adjudication/gold_random_rater1_alvaro.csv")))
    lc = next(c for c in rows[0] if c.startswith("your_label"))

    def note(cid):
        p = ROOT / f"data/notes/genie_nsclc/{cid}.txt"
        return p.read_text() if p.exists() else ""

    human, tree, regex, jud = [], [], [], []
    for r in rows:
        it = items.get(r["id"])
        if not it or not r[lc].strip():
            continue
        if it.get("_variant") == "elderly_patient_75":  # dropped from the study design
            continue
        v = classify(it["response_text"], note(it["case_id"]))
        human.append(1 if r[lc].strip().upper().startswith("STIGMA") else 0)
        tree.append(1 if v.is_stigma else 0)
        regex.append(1 if str(it.get("_classifier_stigma")).lower() == "true" else 0)
        jud.append(1 if judge.get(r["id"]) == "STIGMA" else 0)

    def kappa(a, b):
        n = len(a); po = sum(x == y for x, y in zip(a, b)) / n
        pa, pb = sum(a)/n, sum(b)/n; pe = pa*pb + (1-pa)*(1-pb)
        return (po-pe)/(1-pe) if pe != 1 else 1.0

    import numpy as np
    H = np.array(human)
    raters = [("Decision\ntree", np.array(tree), C_TREE),
              ("Keyword\nclassifier", np.array(regex), C_REGEX),
              ("LLM\njudge", np.array(jud), "#6A9FB5")]
    rng = np.random.default_rng(20260928)
    n = len(H)
    stats = []
    for lab, X, col in raters:
        k = kappa(list(X), list(H))
        bs = []
        for _ in range(4000):   # percentile bootstrap over the 58 responses
            i = rng.integers(0, n, n)
            if H[i].min() == H[i].max() and X[i].min() == X[i].max():
                continue
            bs.append(kappa(list(X[i]), list(H[i])))
        lo, hi = np.percentile(bs, [2.5, 97.5])
        agree = 100 * (X == H).mean()
        stats.append((lab, k, lo, hi, agree, col))
        print(f"  {lab.replace(chr(10), ' '):20s} kappa {k:.2f} [{lo:.2f}, {hi:.2f}]  agreement {agree:.1f}%")
    _rc = plt.rcParams.copy()
    plt.rcParams.update({"font.family": "sans-serif",
                         "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"], "font.size": 12})
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(8.6, 4.2))
    for i, (lab, k, lo, hi, agree, col) in enumerate(stats):
        a1.bar(i, k, 0.6, color=col, edgecolor="k", linewidth=0.5,
               yerr=[[k - lo], [hi - k]], capsize=4, ecolor="0.25")
        a1.text(i + 0.33, k, f"{k:.2f}", va="center", ha="left", fontsize=11)
        a2.bar(i, agree, 0.6, color=col, edgecolor="k", linewidth=0.5)
        a2.text(i, agree + 1, f"{agree:.1f}", ha="center", va="bottom", fontsize=11)
    for ax in (a1, a2):
        ax.set_xticks(range(3)); ax.set_xticklabels([t[0] for t in stats], fontsize=11)
        ax.tick_params(axis="x", length=0)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    a1.set_ylabel("Cohen \u03ba vs human rater"); a1.set_ylim(0, 1.05)
    a2.set_ylabel("Agreement with human rater, %"); a2.set_ylim(0, 105)
    fig.tight_layout(w_pad=3, rect=(0, 0, 1, 0.95))
    fig.text(0.005, 0.99, "A", fontsize=15, fontweight="bold", va="top")
    fig.text(a2.get_position().x0 - 0.09, 0.99, "B", fontsize=15, fontweight="bold", va="top")
    print(f"  n={n}, human STIGMA={int(H.sum())}")
    out = OUT / "FigS06_bias_tree_validation.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    plt.rcParams.update(_rc)
    print(f"Wrote {out}")


if __name__ == "__main__":
    d = load()
    fig_main(d)
    fig_panel_B(d)
    fig_validation()
