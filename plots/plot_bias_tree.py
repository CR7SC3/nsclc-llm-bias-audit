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
    fig, ax = plt.subplots(2, 2, figsize=(12.4, 9.2))
    A, B, C, D = ax[0, 0], ax[0, 1], ax[1, 0], ax[1, 1]

    # --- A: reclassification of all regex flags -------------------------------
    tot_flag = sum(d[s]["regex_flagged"] for s in d)
    stig = sum(d[s]["tree_stigma"] for s in d)
    # contextual + appropriate = flagged − stigma; split via harm-free remainder
    # (contextual count isn't in summary; derive appropriate_contextual vs appropriate
    #  from verdicts is overkill — show STIGMA vs reclassified split)
    reclass = tot_flag - stig
    parts = [("kept as STIGMA", stig, C_STIG),
             ("reclassified as benign\n(false positives removed)", reclass, C_APP)]
    left = 0
    for lab, val, col in parts:
        A.barh(0, val, left=left, color=col, edgecolor="white")
        A.text(left + val / 2, 0, f"{lab}\n{val:,} ({100*val/tot_flag:.0f}%)",
               ha="center", va="center", fontsize=9.5,
               color="white" if col == C_STIG else "#333", fontweight="bold")
        left += val
    A.set_xlim(0, tot_flag); A.set_ylim(-0.6, 0.6)
    A.set_yticks([]); A.set_xlabel(f"{tot_flag:,} regex-flagged responses", fontsize=9.5)
    A.set_title("A  Tree reclassifies 41% of regex flags as benign",
                fontsize=11, fontweight="bold", loc="left")

    # --- B: per-stratum STIGMA rate, regex vs tree, Wilson CI ------------------
    xs = range(len(ORDER))
    w = 0.38
    for i, s in enumerate(ORDER):
        rp, rlo, rhi = _wilson(d[s]["regex_flagged"], d[s]["total"])
        tp, tlo, thi = _wilson(d[s]["tree_stigma"], d[s]["total"])
        B.bar(i - w/2, 100*rp, w, color=C_REGEX,
              yerr=[[100*(rp-rlo)], [100*(rhi-rp)]], capsize=2, ecolor="#888",
              label="regex" if i == 0 else None)
        B.bar(i + w/2, 100*tp, w, color=C_TREE,
              yerr=[[100*(tp-tlo)], [100*(thi-tp)]], capsize=2, ecolor="#555",
              label="tree" if i == 0 else None)
    B.set_xticks(list(xs)); B.set_xticklabels([NICE[s] for s in ORDER], fontsize=8)
    B.set_ylabel("STIGMA rate (%)", fontsize=9.5)
    B.legend(frameon=False, fontsize=9)
    B.set_title("B  Tree removes control false positives, sharpens gradient",
                fontsize=11, fontweight="bold", loc="left")
    B.annotate("control:\n2.18% to 0.02%", xy=(6, 1.5), xytext=(4.4, 18),
               fontsize=8.2, color="#8E1B1B",
               arrowprops=dict(arrowstyle="->", color="#8E1B1B", lw=1))

    # --- C: harm-type decomposition (descriptive) -----------------------------
    strata_c = [s for s in ORDER if d[s]["tree_stigma"] > 0]
    xs2 = range(len(strata_c))
    for i, s in enumerate(strata_c):
        n = d[s]["total"]
        a = 100*d[s]["allocative"]/n; e = 100*d[s]["epistemic"]/n; g = 100*d[s]["dignitary"]/n
        C.bar(i, a, color=C_ALLOC, label="Allocative" if i == 0 else None)
        C.bar(i, e, bottom=a, color=C_EPIST, label="Epistemic injustice" if i == 0 else None)
        C.bar(i, g, bottom=a+e, color=C_DIGN, label="Dignitary" if i == 0 else None)
    C.set_xticks(list(xs2)); C.set_xticklabels([NICE[s] for s in strata_c], fontsize=8)
    C.set_ylabel("STIGMA rate by harm type (%)", fontsize=9.5)
    C.legend(frameon=False, fontsize=8.5, loc="upper right")
    C.set_title("C  Harm-type decomposition  (descriptive — unvalidated)",
                fontsize=11, fontweight="bold", loc="left")

    # --- D: Gate-2 ablation ---------------------------------------------------
    strata_d = ["unhoused", "black_unhoused", "low_income", "underinsured", "uninsured", "control"]
    xs3 = range(len(strata_d)); w = 0.38
    for i, s in enumerate(strata_d):
        note = 100*d[s]["tree_stigma"]/d[s]["total"]
        lbl = 100*d[s]["tree_stigma_withlabel"]/d[s]["total"]
        D.bar(i - w/2, note, w, color=C_TREE, label="note-only (correct)" if i == 0 else None)
        D.bar(i + w/2, lbl, w, color=C_LABEL, label="note + demographic label" if i == 0 else None)
    D.set_xticks(list(xs3)); D.set_xticklabels([NICE[s] for s in strata_d], fontsize=8)
    D.set_ylabel("STIGMA rate (%)", fontsize=9.5)
    D.legend(frameon=False, fontsize=8.5)
    D.set_title("D  A demographic label is not grounding (Gate-2 ablation)",
                fontsize=11, fontweight="bold", loc="left")
    D.text(0.98, 0.62, "gap = label 'excuses'\nfabricated concern\n(counterfactual effect)",
           transform=D.transAxes, ha="right", fontsize=8, color="#555", style="italic")

    fig.suptitle("Bias decision tree — a deterministic precision filter over regex-flagged oncology recommendations",
                 fontsize=12.5, fontweight="bold", y=0.995)
    fig.tight_layout(rect=[0, 0, 1, 0.98])
    out = OUT / "FigS10_bias_tree_decomposition.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    print(f"Wrote {out}")


def fig_panel_B(d):
    """Standalone version of sub-panel B (regex vs. tree, control collapse) for use as
    the single Figure 5D panel. combine_figures.py stamps the outer 'D' letter, so no
    sub-letter here; the finding stays in the caption."""
    fig, B = plt.subplots(figsize=(6.6, 5.2))
    xs = range(len(ORDER))
    w = 0.38
    for i, s in enumerate(ORDER):
        rp, rlo, rhi = _wilson(d[s]["regex_flagged"], d[s]["total"])
        tp, tlo, thi = _wilson(d[s]["tree_stigma"], d[s]["total"])
        B.bar(i - w/2, 100*rp, w, color=C_REGEX, edgecolor="k", linewidth=0.5,
              yerr=[[100*(rp-rlo)], [100*(rhi-rp)]], capsize=2, ecolor="#888",
              label="regex flag" if i == 0 else None)
        B.bar(i + w/2, 100*tp, w, color=C_TREE, edgecolor="k", linewidth=0.5,
              yerr=[[100*(tp-tlo)], [100*(thi-tp)]], capsize=2, ecolor="#555",
              label="grounded bias tree" if i == 0 else None)
    # single-line labels so the standardized 30° tilt reads cleanly (fig_main keeps NICE two-line)
    FLAT = {"unhoused": "unhoused", "black_unhoused": "Black + unhoused",
            "low_income": "low income", "underinsured": "underinsured",
            "uninsured": "uninsured", "race_only": "race-only", "control": "control"}
    B.set_xticks(list(xs)); B.set_xticklabels([FLAT[s] for s in ORDER], rotation=30,
                                              ha="right", rotation_mode="anchor")   # standardized 30° tilt
    B.set_ylabel("STIGMA rate (%)")   # unified-size label (match panels A/B/C)
    B.set_yticks(range(0, 51, 20))   # 20% gridlines (match panel C)
    B.grid(axis="y", alpha=0.25); B.set_axisbelow(True)   # grey gridlines (match panel C)
    B.legend(framealpha=0.95)   # standardized: framed, inherits unified 10 pt (match panel A)
    # full box around the axes (match panels A/B/C); global rcParams hide top/right
    for sp in B.spines.values():
        sp.set_visible(True)
    # fixed geometry so all Fig-5 panels share one height and their x-axes align
    # (single-axis box, identical to panel A). No tight bbox.
    B.set_position([0.10, 0.16, 0.87, 0.78])
    PANELS = ROOT / "figures/manuscript_combined/panels"; PANELS.mkdir(parents=True, exist_ok=True)
    fig.savefig(PANELS / "p_bias_tree.png", dpi=200)
    plt.close(fig)
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
        v = classify(it["response_text"], note(it["case_id"]))
        human.append(1 if r[lc].strip().upper().startswith("STIGMA") else 0)
        tree.append(1 if v.is_stigma else 0)
        regex.append(1 if str(it.get("_classifier_stigma")).lower() == "true" else 0)
        jud.append(1 if judge.get(r["id"]) == "STIGMA" else 0)

    def kappa(a, b):
        n = len(a); po = sum(x == y for x, y in zip(a, b)) / n
        pa, pb = sum(a)/n, sum(b)/n; pe = pa*pb + (1-pa)*(1-pb)
        return (po-pe)/(1-pe) if pe != 1 else 1.0

    ks = [("tree", kappa(tree, human), C_TREE),
          ("regex", kappa(regex, human), C_REGEX),
          ("Sonnet\njudge", kappa(jud, human), "#6A9FB5")]
    fig, ax = plt.subplots(figsize=(4.6, 4.2))
    for i, (lab, k, col) in enumerate(ks):
        ax.bar(i, k, 0.6, color=col)
        ax.text(i, k + 0.02, f"{k:.2f}", ha="center", fontsize=10, fontweight="bold")
    ax.set_xticks(range(3)); ax.set_xticklabels([l for l, _, _ in ks], fontsize=9.5)
    ax.set_ylabel("Cohen's κ vs human rater", fontsize=9.5)
    ax.set_ylim(0, 1)
    ax.set_title(f"Agreement with human rater\n(classifier-blind random set, n={len(human)})",
                 fontsize=10.5, fontweight="bold")
    fig.text(0.5, -0.02, "Tree matches regex and beats the LLM judge — while removing 41% of flags as benign.",
             ha="center", fontsize=7.6, color="#555", style="italic")
    fig.tight_layout()
    out = OUT / "FigS06_bias_tree_validation.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    print(f"Wrote {out}")


if __name__ == "__main__":
    d = load()
    fig_main(d)
    fig_panel_B(d)
    fig_validation()
