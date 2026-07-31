"""Run the bias decision-tree over the NSCLC baseline arms and score meaningfulness.

Pipeline
────────
  1. For every regex-flagged response (adherence_compliance OR sdoh_generation) in each
     cached arm, reconstruct grounding (note + injected demographics) and run
     bias_tree.classify() → per-response leaf + harm type.  → results/analysis/bias_tree_verdicts.csv
  2. Corpus quantification: tree-STIGMA rate by stratum with Wilson CI, differential vs
     control, and the regex→tree reclassification (false-positive) breakdown.
  3. Validation: run the tree on the blinded judge items and report agreement + Cohen's
     kappa vs the Sonnet judge's STIGMA labels (and vs the raw regex classifier).
  4. Meaningfulness gates M1–M4 printed at the end.

Cached outputs only — no API calls, no money.

    python scripts/nsclc/run_bias_tree.py
"""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.analyze.bias_tree import classify, build_grounding_text, STIGMA, STIGMA_DIMS
from src.analyze.soft_bias import DIMS
from src.generate.variant_injector_v2 import VARIANT_GROUPS_V2
import finalize_panel as fp  # reuse _wilson, STRATA, ARMS

NOTES = ROOT / "data/notes/genie_nsclc"
OUT = ROOT / "results/analysis"
OUT.mkdir(parents=True, exist_ok=True)

_notecache: dict[str, str] = {}


def _note(base: str) -> str:
    if base not in _notecache:
        p = NOTES / f"{base}.txt"
        _notecache[base] = p.read_text(encoding="utf-8") if p.exists() else ""
    return _notecache[base]


def _regex_flagged(resp: str) -> bool:
    return any(DIMS[k].detect(resp) for k in STIGMA_DIMS)


# ---------------------------------------------------------------------------
# 1 + 2 — corpus pass over the baseline arms
# ---------------------------------------------------------------------------

def run_corpus():
    present = {m: p for m, p in fp.ARMS.items() if (ROOT / p).exists()}
    rows = []
    # stratum → counters
    flagged = defaultdict(int)          # regex-flagged responses (tree Gate-0 positive)
    tree_stigma = defaultdict(int)      # tree leaf == STIGMA
    tree_stigma_lbl = defaultdict(int)  # STIGMA when demographic LABEL is added to grounding (ablation)
    total = defaultdict(int)            # all scored responses (denominator)
    reclass = Counter()                 # leaf distribution among regex-flagged
    harm = Counter()
    harm_by = defaultdict(Counter)      # stratum → harm-type counts (descriptive)

    stratum_of = {vk: s for s, vks in fp.STRATA.items() for vk in vks}

    for model, path in present.items():
        d = json.loads((ROOT / path).read_text())
        for cid, variants in d.items():
            if not isinstance(variants, dict):
                continue
            for vk, rec in variants.items():
                if not (isinstance(rec, dict) and rec.get("response_text")):
                    continue
                stratum = stratum_of.get(vk)
                if stratum is None:
                    continue
                resp = rec["response_text"]
                total[stratum] += 1
                if not _regex_flagged(resp):
                    continue
                base = rec.get("base_case_id") or cid
                note = _note(base)
                # Gate-2 grounding is the NOTE ONLY — a demographic label is never, by
                # itself, clinical grounding (rubric core principle).
                v = classify(resp, note)
                # Ablation: if we (wrongly) let the demographic label count as grounding,
                # how many STIGMA verdicts disappear? That gap IS the counterfactual effect.
                v_lbl = classify(resp, build_grounding_text(note, VARIANT_GROUPS_V2.get(vk)))
                flagged[stratum] += 1
                reclass[v.leaf] += 1
                if v.is_stigma:
                    tree_stigma[stratum] += 1
                    harm[v.harm_type] += 1
                    harm_by[stratum][v.harm_type] += 1
                if v_lbl.is_stigma:
                    tree_stigma_lbl[stratum] += 1
                rows.append({
                    "model": model, "base_case_id": base, "variant": vk,
                    "stratum": stratum, "leaf": v.leaf,
                    "harm_type": v.harm_type or "", "driver_dim": v.driver_dim or "",
                    "grounded": int(v.grounded), "weakens_treatment": int(v.weakens_treatment),
                    "gate_path": " > ".join(v.gate_path),
                    "evidence_span": " || ".join(v.evidence_spans)[:500],
                })

    # write verdicts
    csv_path = OUT / "bias_tree_verdicts.csv"
    with open(csv_path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"Wrote {csv_path}  ({len(rows)} flagged responses)")

    # compact per-stratum summary for the figure script (recompute-free plotting)
    summ = OUT / "bias_tree_stratum_summary.csv"
    with open(summ, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["stratum", "total", "regex_flagged", "tree_stigma",
                    "tree_stigma_withlabel", "allocative", "epistemic", "dignitary"])
        for s in fp.STRATA:
            w.writerow([s, total[s], flagged[s], tree_stigma[s], tree_stigma_lbl[s],
                        harm_by[s]["ALLOCATIVE"], harm_by[s]["EPISTEMIC_INJUSTICE"],
                        harm_by[s]["DIGNITARY"]])
    print(f"Wrote {summ}")

    # --- reclassification / false-positive story (M1) ---
    n_flag = sum(reclass.values())
    print(f"\n=== Regex→tree reclassification of {n_flag} regex-flagged responses (M1) ===")
    for leaf, k in reclass.most_common():
        print(f"  {leaf:<24} {k:6d}  ({100*k/n_flag:4.1f}%)")
    kept = reclass[STIGMA]
    print(f"  → tree keeps {100*kept/n_flag:.1f}% as STIGMA; "
          f"reclassifies {100*(n_flag-kept)/n_flag:.1f}% as non-stigma (regex false positives)")
    print(f"  harm-type mix among STIGMA: " +
          ", ".join(f"{h}={k}" for h, k in harm.most_common()))

    # --- per-stratum tree-STIGMA rate + Wilson CI + differential vs control (M3) ---
    ctrl_k = tree_stigma["control"]; ctrl_n = total["control"]
    ctrl_rate = ctrl_k / ctrl_n if ctrl_n else 0.0
    print(f"\n=== Tree-STIGMA rate by stratum (denominator = all responses) ===")
    print(f"  {'stratum':<15}{'rate':>8}{'  95% CI':>16}{'  RD vs ctrl':>13}   (k/n)")
    order = ["black_unhoused", "unhoused", "low_income", "uninsured", "underinsured",
             "race_only", "control"]
    for stratum in order:
        k, n = tree_stigma[stratum], total[stratum]
        p, lo, hi = fp._wilson(k, n)
        rd = p - ctrl_rate
        print(f"  {stratum:<15}{100*p:7.2f}%  [{100*lo:5.2f},{100*hi:5.2f}]  "
              f"{100*rd:+8.2f} pp     ({k}/{n})")

    # regex composite rate for the same denominators, to show the tree only ever downgrades
    print(f"\n=== Regex composite vs tree, headline strata ===")
    for stratum in ["black_unhoused", "unhoused", "control"]:
        rk = flagged[stratum]; n = total[stratum]; tk = tree_stigma[stratum]
        rr = rk / n if n else 0; tr = tk / n if n else 0
        print(f"  {stratum:<15} regex={100*rr:5.2f}%  tree={100*tr:5.2f}%  "
              f"(tree ≤ regex: {'ok' if tk <= rk else 'VIOLATION'})")

    # --- discriminant validity: null-stratum FPR + rate ratio (primary, per psychometrics) ---
    print(f"\n=== Discriminant validity (the metric global κ cannot show) ===")
    cp, clo, chi = fp._wilson(ctrl_k, ctrl_n)
    rp, rlo, rhi = fp._wilson(flagged["control"], ctrl_n)   # regex control rate
    print(f"  control false-positive rate:  regex {100*rp:.2f}%  →  tree {100*cp:.2f}% "
          f"[{100*clo:.2f},{100*chi:.2f}]   ({int(rp/cp) if cp else '∞'}× reduction)")
    for stratum in ["unhoused", "black_unhoused", "low_income"]:
        tr = tree_stigma[stratum] / total[stratum]
        rr_regex = flagged[stratum] / total[stratum]
        ratio_tree = tr / cp if cp else float("inf")
        ratio_regex = rr_regex / rp if rp else float("inf")
        print(f"  {stratum:<15} disadvantaged:control rate-ratio  "
              f"regex {ratio_regex:6.1f}×  →  tree {ratio_tree:8.1f}×")

    # --- Gate-2 ablation: note-only vs note+label grounding (counterfactual effect) ---
    print(f"\n=== Gate-2 ablation: 'a demographic label is not grounding' (STIGMA rate) ===")
    print(f"  {'stratum':<15}{'note-only':>12}{'note+label':>12}{'Δ (label excuses)':>20}")
    for stratum in ["unhoused", "black_unhoused", "low_income", "control"]:
        n = total[stratum]
        a = tree_stigma[stratum] / n if n else 0
        b = tree_stigma_lbl[stratum] / n if n else 0
        print(f"  {stratum:<15}{100*a:11.2f}%{100*b:11.2f}%{100*(a-b):+18.2f} pp")

    return reclass, tree_stigma, total, ctrl_rate, cp


# ---------------------------------------------------------------------------
# 3 — validation vs the Sonnet judge (M2)
# ---------------------------------------------------------------------------

def _kappa(a, b):
    n = len(a)
    if not n:
        return float("nan")
    po = sum(x == y for x, y in zip(a, b)) / n
    pa1 = sum(a) / n; pb1 = sum(b) / n
    pe = pa1 * pb1 + (1 - pa1) * (1 - pb1)
    return (po - pe) / (1 - pe) if pe != 1 else 1.0


def _pabak(a, b):
    """Prevalence-adjusted bias-adjusted kappa = 2*po - 1 (robust to skewed base rates)."""
    n = len(a)
    return (2 * (sum(x == y for x, y in zip(a, b)) / n) - 1) if n else float("nan")


def validate_human():
    """Triangulate tree / regex / judge against the human rater on the CLASSIFIER-BLIND
    random sample (the correct, non-circular reference). Reproduces the psychometrics
    council check. Requires the filled human label CSV."""
    human_p = ROOT / "adjudication/gold_random_rater1_alvaro.csv"
    items_p = ROOT / "adjudication/random_judge_items.jsonl"
    judge_p = ROOT / "adjudication/random_judge_labels.json"
    if not (human_p.exists() and items_p.exists()):
        print("\n(no human random-set labels — skipping human triangulation)")
        return None
    import csv as _csv
    items = {json.loads(l)["id"]: json.loads(l)
             for l in items_p.read_text().splitlines() if l.strip()}
    judge = json.loads(judge_p.read_text()) if judge_p.exists() else {}
    rows = list(_csv.DictReader(open(human_p)))
    lbl_col = next(c for c in rows[0] if c.startswith("your_label"))

    human, tree, regex, jud = [], [], [], []
    for r in rows:
        jid = r["id"]; it = items.get(jid)
        if not it or not r[lbl_col].strip():
            continue
        v = classify(it["response_text"], _note(it["case_id"]))
        human.append(1 if r[lbl_col].strip().upper().startswith("STIGMA") else 0)
        tree.append(1 if v.is_stigma else 0)
        regex.append(1 if str(it.get("_classifier_stigma")).lower() == "true" else 0)
        jud.append(1 if judge.get(jid) == "STIGMA" else 0)

    n = len(human)
    print(f"\n=== Triangulation vs HUMAN rater on {n} classifier-blind random items ===")
    print(f"  {'pair':<16}{'kappa':>8}{'PABAK':>8}{'agree':>8}")
    for name, x in [("tree vs human", tree), ("regex vs human", regex), ("judge vs human", jud)]:
        ag = sum(p == q for p, q in zip(x, human)) / n
        print(f"  {name:<16}{_kappa(x, human):8.3f}{_pabak(x, human):8.3f}{ag:8.3f}")
    print(f"  (human STIGMA prevalence {sum(human)}/{n}; note single non-blinded rater — "
          f"two-rater flagged-set adjudication still required)")
    return _kappa(tree, human), _kappa(regex, human)


def validate():
    items_p = ROOT / "adjudication/judge_items.jsonl"
    labels_p = ROOT / "adjudication/judge_labels.json"
    if not (items_p.exists() and labels_p.exists()):
        print("\n(no judge items/labels — skipping M2 validation)")
        return None
    items = {json.loads(l)["id"]: json.loads(l)
             for l in items_p.read_text().splitlines() if l.strip()}
    labels = json.loads(labels_p.read_text())

    judge, tree, regex = [], [], []
    fj, ft, fr = [], [], []   # conditional on regex-flagged (the only stratum tree ≠ regex)
    confusion = Counter()
    for jid, lab in labels.items():
        it = items.get(jid)
        if not it:
            continue
        v = classify(it["response_text"], _note(it["case_id"]))  # note-only grounding
        j = 1 if lab == "STIGMA" else 0
        t = 1 if v.is_stigma else 0
        r = 1 if str(it.get("_classifier_stigma")).lower() == "true" else 0
        judge.append(j); tree.append(t); regex.append(r)
        if r:  # regex-positive subset
            fj.append(j); ft.append(t); fr.append(r)
        confusion[(f"judge={lab}", f"tree={v.leaf}")] += 1

    n = len(judge)
    def _agree(a, b): return sum(x == y for x, y in zip(a, b)) / n if n else float("nan")
    print(f"\n=== Validation vs Sonnet judge on {n} blinded items (M2) ===")
    print(f"  judge STIGMA rate : {100*sum(judge)/n:.1f}%")
    print(f"  tree  STIGMA rate : {100*sum(tree)/n:.1f}%")
    print(f"  regex STIGMA rate : {100*sum(regex)/n:.1f}%")
    print(f"  tree  vs judge : agreement={100*_agree(tree, judge):.1f}%  kappa={_kappa(tree, judge):.3f}")
    print(f"  regex vs judge : agreement={100*_agree(regex, judge):.1f}%  kappa={_kappa(regex, judge):.3f}")
    # sensitivity / specificity of the tree against the judge as reference
    tp = sum(t and j for t, j in zip(tree, judge))
    fn = sum((not t) and j for t, j in zip(tree, judge))
    fp_ = sum(t and (not j) for t, j in zip(tree, judge))
    tn = sum((not t) and (not j) for t, j in zip(tree, judge))
    sens = tp / (tp + fn) if (tp + fn) else float("nan")
    spec = tn / (tn + fp_) if (tn + fp_) else float("nan")
    print(f"  tree vs judge  : sensitivity={100*sens:.0f}%  specificity={100*spec:.0f}%  "
          f"(TP={tp} FN={fn} FP={fp_} TN={tn})")
    # Conditional on regex-flagged — where tree and regex actually differ. On the full
    # mixed set global κ is dominated by the shared Gate-0 behavior and cannot move.
    if fj:
        print(f"  conditional on the {len(fj)} regex-FLAGGED items (tree≠regex here):")
        print(f"    tree  vs judge : agreement={100*_agree_sub(ft, fj):.1f}%  kappa={_kappa(ft, fj):.3f}")
        print(f"    regex vs judge : agreement={100*_agree_sub(fr, fj):.1f}%  kappa={_kappa(fr, fj):.3f}")
    return _kappa(tree, judge), _kappa(regex, judge)


def _agree_sub(a, b):
    return sum(x == y for x, y in zip(a, b)) / len(a) if a else float("nan")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    reclass, tree_stigma, total, ctrl_rate, ctrl_fpr = run_corpus()
    validate()               # vs LLM judge (context + conditional-on-flagged)
    human = validate_human() # vs human rater on the classifier-blind random set (primary)

    # --- Scorecard: sanity checks (S) + the real validation (V) ---
    n_flag = sum(reclass.values())
    kept_frac = reclass[STIGMA] / n_flag if n_flag else 0
    disadv_rate = tree_stigma["unhoused"] / total["unhoused"] if total["unhoused"] else 0
    print("\n" + "=" * 66)
    print("SCORECARD — sanity checks (not validation) + criterion validity")
    print("=" * 66)
    print("  Sanity checks (necessary, not sufficient):")
    print(f"    S1 separation    : tree keeps {100*kept_frac:.0f}% of flags as STIGMA "
          f"(reclassifies {100*(1-kept_frac):.0f}% as benign)")
    print(f"    S2 tree ≤ regex  : holds by construction (tree only downgrades flags)")
    print(f"    S3 differential  : unhoused {100*disadv_rate:.1f}% > control {100*ctrl_rate:.2f}% "
          f"(directional; guaranteed once control≈0)")
    print("  Criterion validity (the actual evidence):")
    print(f"    V1 null-stratum specificity : control FPR → {100*ctrl_fpr:.2f}% "
          f"(the discriminant-validity headline)")
    if human is not None:
        th, rh = human
        print(f"    V2 agreement vs HUMAN       : tree κ={th:.2f}  (judge-vs-human is the proxy; "
              f"regex κ={rh:.2f})")
    else:
        print(f"    V2 agreement vs HUMAN       : PENDING — needs two-rater flagged-set labels")
    print(f"    V3 harm-type subtypes       : UNVALIDATED — descriptive only until human-labeled")


if __name__ == "__main__":
    main()
