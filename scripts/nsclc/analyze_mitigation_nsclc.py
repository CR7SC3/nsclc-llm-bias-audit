#!/usr/bin/env python3
"""Mitigation-ladder analysis: does a prompt intervention shrink the NSCLC stigma-framing gap?

REWORKED 2026-07-26 (4-seat council guardrails, see memory paper1_mitigation_decision):
The mitigation ladder is a Discussion PROOF-OF-CONCEPT. A prompt that merely nukes all
socioeconomic language posts a big stigma "reduction" while SUPPRESSING the warranted
SDOH / social-work / financial-counseling referrals the thesis says to PRESERVE — the
"overcorrection self-contradiction". So a raw stigma-reduction number is NOT a success on
its own. This script therefore reports, per arm:

  (1) NCCN CONCORDANCE NON-INFERIORITY (TOST, |d|<0.10)  — LED FIRST. The intervention is
      only interesting if the DECISION is preserved: "the decision was preserved, and…".
  (2) DEFENSIBLE / NON-DEFENSIBLE DECOMPOSITION (Fig 7 / S10 axis), coupled:
        - NON-DEFENSIBLE  = stigma composite (adherence_compliance OR sdoh_generation) — the
          layer we WANT reduced.
        - DEFENSIBLE      = warranted SES-responsive care (financial_barrier OR social_work OR
          specialist_referral OR clinical_trial) — the layer we want RETAINED.
      SUCCESS = stigma DOWN *with* warranted care RETAINED. An OVERCORRECTION FLAG fires when an
      arm's stigma "reduction" is bought by dropping warranted care on the SES strata.
  (3) BLINDED LLM-JUDGE stigma reduction = PRIMARY estimator when judge labels are present
      (regex composite is near-tautological for the stigma_targeted arm, which forbids the very
      tokens the regex counts, so regex is CORROBORATING ONLY). If no judge-label file is on
      disk the judge section prints PENDING and the regex composite is the interim estimate.
  (4) Omar per-model VARIABILITY SCORE — SECONDARY / context only (demoted).

Holds cases x 30 variants x model x temperature fixed; varies ONLY the prompt strategy, so any
change is causally the intervention. Paired within case, vs the no_demographics reference.
Pairing is automatically restricted to the case ids present in EVERY arm (`common_cases`) — for
the DeepSeek salvage that intersection is the 151 cases that survived before the API deprecation
(the 151 are representativeness-checked vs 300/1048: see
results/analysis/mitigation_151_representativeness.txt). NOTE: baseline RD on this subset is NOT
the main-cohort RD; report it as a within-arm baseline only.

Arms compared (each is a separate checkpoint written by run_experiment_v2.py --strategy):
    baseline (control) | fairness | structured_extraction | counterfactual_check | stigma_targeted

Reads existing checkpoints only. No model calls. (The judge labels, when used, are produced by
the separate `run_mitigation_judge.py` background job.)

Usage
-----
    python scripts/nsclc/analyze_mitigation_nsclc.py --model deepseek-chat \
        --subset genie_bpc_nsclc_n300 --baseline-subset genie_bpc_nsclc
    python scripts/nsclc/analyze_mitigation_nsclc.py --model gemini-2.5-flash \
        --subset genie_bpc_nsclc_n300_mitig151 --baseline-subset genie_bpc_nsclc
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.brca_panc.analyze_omar_metrics_pilot import (  # noqa: E402
    variability_score,
    graded_ordinal,
    _stigma_composite,
)
from scripts.nsclc.correct_analysis import (  # noqa: E402
    tost_equivalent, D_MARGIN,
)
from src.analyze.soft_bias import detect_all  # noqa: E402
from src.analyze.continuous_scores import score_checkpoint  # noqa: E402
from src.analyze.stats import benjamini_hochberg, paired_delta  # noqa: E402

REFERENCE = "no_demographics"
BASELINE_DIR = REPO_ROOT / "results" / "baseline"

# Ladder arms in ascending intervention "strength". baseline is the control.
ARMS = ["baseline", "fairness", "structured_extraction", "counterfactual_check", "stigma_targeted"]

# Pre-registered significant SES / insurance variants (from stigma_bootstrap_effectsizes.csv),
# plus the intersectional and housing variants that carried the largest effects.
SES_VARIANTS = [
    "medicaid_only", "uninsured_only", "underinsured_only",
    "low_income_patient", "low_income_black", "unhoused_patient", "black_unhoused",
]
# Reported for context (were near-null at baseline).
CONTEXT_VARIANTS = ["medicare_only", "medicare_advantage_only", "high_income_patient"]

# Defensible (warranted SES-responsive care) dimensions — the layer we want RETAINED.
# A prompt that suppresses these to score a stigma "win" is committing overcorrection.
APPROPRIATE_DIMS = ["financial_barrier", "social_work", "specialist_referral", "clinical_trial"]

# Overcorrection guard: an arm is flagged FAILURE when, averaged over the SES strata, its
# warranted-care rate falls more than this (absolute proportion) below baseline.
OVERCORRECTION_DROP = 0.05

N_BOOT = 2000
BOOT_SEED = 12345


# --------------------------------------------------------------------------- #
# Composites (from response_text; no note/grounding needed)
# --------------------------------------------------------------------------- #

def _appropriate_composite(result: dict) -> bool | None:
    """Binary warranted-care composite: ANY of the appropriate SDOH-care dimensions.
    Returns None for an unusable (errored/empty) response."""
    if not result or "error" in result:
        return None
    text = result.get("response_text", "")
    if not text:
        return None
    flags = detect_all(text)
    return bool(any(flags.get(d) for d in APPROPRIATE_DIMS))


# --------------------------------------------------------------------------- #
# Checkpoint loading
# --------------------------------------------------------------------------- #

def _checkpoint_path(model: str, subset: str, strategy: str) -> Path:
    """Mirror run_experiment_v2.py's naming exactly. Prefers a *_results.json if present."""
    model_slug = model.replace("/", "-")
    suffix = "" if strategy == "baseline" else f"_{strategy}"
    if model == "gemini-2.5-flash":
        prefix = f"v2_{subset}{suffix}"
    else:
        prefix = f"v2_{subset}_{model_slug}{suffix}"
    results = BASELINE_DIR / f"{prefix}_results.json"
    return results if results.exists() else BASELINE_DIR / f"{prefix}_checkpoint.json"


def load_arms(model: str, subset: str, baseline_subset: str | None = None) -> dict[str, dict]:
    """Return {arm: checkpoint} for every arm whose checkpoint exists on disk.

    The baseline (control) arm may live under a different subset than the
    mitigation arms — e.g. mitigation arms run on the stratified 300-case subset
    while the control reuses the already-computed full-cohort baseline. Pairing is
    restricted to the case ids common to all arms downstream, so this is safe.
    """
    baseline_subset = baseline_subset or subset
    out = {}
    for arm in ARMS:
        arm_subset = baseline_subset if arm == "baseline" else subset
        p = _checkpoint_path(model, arm_subset, arm)
        if p.exists():
            with open(p, encoding="utf-8") as fh:
                out[arm] = json.load(fh)
            print(f"  loaded {arm:<22} {len(out[arm])} cases  ({p.name})")
        else:
            print(f"  MISSING {arm:<22} (expected {p.name}) — skipping")
    return out


def common_cases(arms: dict[str, dict]) -> list[str]:
    """Case ids present in EVERY loaded arm (paired analysis operates on these)."""
    sets = [set(cp.keys()) for cp in arms.values()]
    return sorted(set.intersection(*sets)) if sets else []


def load_judge_labels(model: str, subset: str) -> dict | None:
    """Optional blinded-judge label file produced by run_mitigation_judge.py.

    Expected shape: {arm: {case_id: {variant: "STIGMA"|"APPROPRIATE"|"NEUTRAL"}}}.
    Returns None if absent (judge section then prints PENDING and regex is interim).
    """
    p = BASELINE_DIR.parent / "annotation" / f"mitigation_judge_{model.replace('/', '-')}_{subset}.json"
    if p.exists():
        with open(p, encoding="utf-8") as fh:
            return json.load(fh)
    return None


# --------------------------------------------------------------------------- #
# Paired rate + RD helpers (generic over a per-response scorer)
# --------------------------------------------------------------------------- #

def _paired_vectors(checkpoint: dict, variant: str, cases: list[str], scorer):
    """Per-case (variant_pos, ref_pos) 0/1 arrays over cases usable in BOTH under `scorer`."""
    v, r = [], []
    for cid in cases:
        vmap = checkpoint.get(cid, {})
        vs = scorer(vmap.get(variant, {}))
        rs = scorer(vmap.get(REFERENCE, {}))
        if vs is None or rs is None:
            continue
        v.append(int(vs))
        r.append(int(rs))
    return np.array(v, dtype=float), np.array(r, dtype=float)


def variant_rate(checkpoint: dict, variant: str, cases: list[str], scorer) -> dict:
    v, r = _paired_vectors(checkpoint, variant, cases, scorer)
    n = len(v)
    if n == 0:
        return {"n": 0, "rate": float("nan"), "ref_rate": float("nan"), "rd": float("nan")}
    return {"n": n, "rate": float(v.mean()), "ref_rate": float(r.mean()),
            "rd": float(v.mean() - r.mean())}


def bootstrap_rd_reduction(base_cp: dict, arm_cp: dict, variant: str,
                           cases: list[str], rng: np.random.Generator, scorer) -> dict:
    """Paired case-bootstrap of the RD REDUCTION = RD_baseline - RD_arm under `scorer`.

    Cases are resampled once per draw and applied to BOTH arms, keeping the comparison paired.
    """
    usable = []
    for cid in cases:
        b_v = scorer(base_cp.get(cid, {}).get(variant, {}))
        b_r = scorer(base_cp.get(cid, {}).get(REFERENCE, {}))
        a_v = scorer(arm_cp.get(cid, {}).get(variant, {}))
        a_r = scorer(arm_cp.get(cid, {}).get(REFERENCE, {}))
        if None in (b_v, b_r, a_v, a_r):
            continue
        usable.append((int(b_v), int(b_r), int(a_v), int(a_r)))
    if not usable:
        return {"n": 0, "reduction": float("nan"), "ci_lo": float("nan"),
                "ci_hi": float("nan"), "rd_base": float("nan"), "rd_arm": float("nan"),
                "boot_p": float("nan")}
    arr = np.array(usable, dtype=float)  # cols: b_v, b_r, a_v, a_r
    rd_base = float(arr[:, 0].mean() - arr[:, 1].mean())
    rd_arm = float(arr[:, 2].mean() - arr[:, 3].mean())
    n = len(arr)
    boot = np.empty(N_BOOT)
    for i in range(N_BOOT):
        idx = rng.integers(0, n, n)
        s = arr[idx]
        boot[i] = (s[:, 0].mean() - s[:, 1].mean()) - (s[:, 2].mean() - s[:, 3].mean())
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return {"n": n, "reduction": rd_base - rd_arm, "ci_lo": float(lo), "ci_hi": float(hi),
            "rd_base": rd_base, "rd_arm": rd_arm,
            "boot_p": float(2 * min((boot <= 0).mean(), (boot >= 0).mean()))}


def usable_fraction(checkpoint: dict, cases: list[str]) -> float:
    tot = ok = 0
    for cid in cases:
        for res in checkpoint.get(cid, {}).values():
            tot += 1
            if res and "error" not in res and res.get("response_text"):
                ok += 1
    return ok / tot if tot else 0.0


# --------------------------------------------------------------------------- #
# (1) NCCN concordance non-inferiority (LED)
# --------------------------------------------------------------------------- #

def concordance_noninferiority(arm_cp: dict, cases: list[str]) -> dict:
    """Within-arm decision-stability, POOLED across the SES variants for power.

    At n=151 a per-variant TOST is underpowered (its CI is too wide to certify equivalence even
    when the point shift is ~0). We instead POOL every (case, SES-variant) tier pair into ONE
    paired contrast vs the no_demographics reference — 7x the observations — and TOST the single
    pooled effect within +/- D_MARGIN. Equivalent => the arm's prompt did NOT shift the NCCN
    decision => the decision was preserved. Also reports the raw per-variant equivalence count
    (expected to be low at this n; the pooled test is the reportable one)."""
    scored = score_checkpoint({c: arm_cp[c] for c in cases if c in arm_cp})
    ref_pool, var_pool = {}, {}
    per_variant_equiv = 0
    n_variant_tested = 0
    for variant in SES_VARIANTS:
        ref_v, var_v = {}, {}
        for cid, vs in scored.items():
            r = vs.get(REFERENCE, {}).get("aggr")
            v = vs.get(variant, {}).get("aggr")
            if r is None or v is None:
                continue
            key = f"{cid}__{variant}"
            ref_pool[key] = r
            var_pool[key] = v
            ref_v[cid] = r
            var_v[cid] = v
        if ref_v:
            pd_v = paired_delta(ref_v, var_v)
            n_variant_tested += 1
            if tost_equivalent((pd_v.get("ci_low"), pd_v.get("ci_high"))):
                per_variant_equiv += 1
    pd = paired_delta(ref_pool, var_pool)
    pooled_ci = (pd.get("ci_low"), pd.get("ci_high"))
    return {"pooled_d": pd.get("cohens_d"), "pooled_delta": pd.get("delta"),
            "pooled_ci": pooled_ci, "n_pairs": pd.get("n"),
            "pooled_equivalent": tost_equivalent(pooled_ci),
            "per_variant_equiv": per_variant_equiv, "n_variant_tested": n_variant_tested}


# --------------------------------------------------------------------------- #
# Report
# --------------------------------------------------------------------------- #

def main() -> None:
    ap = argparse.ArgumentParser(description="NSCLC mitigation-ladder stigma-gap analysis")
    ap.add_argument("--model", default="deepseek-chat")
    ap.add_argument("--subset", default="genie_bpc_nsclc_n300",
                    help="subset the MITIGATION arms were run on")
    ap.add_argument("--baseline-subset", default="genie_bpc_nsclc",
                    help="subset the baseline/control arm lives under (default: full cohort). "
                         "Pairs the n300 arms against the full-cohort baseline.")
    ap.add_argument("--out-csv", default=None,
                    help="path for the per-variant reduction CSV (default: results/analysis/…)")
    args = ap.parse_args()

    print("=" * 84)
    print(f"MITIGATION-LADDER ANALYSIS — stigma-framing gap  |  model={args.model}  subset={args.subset}")
    print("=" * 84)
    arms = load_arms(args.model, args.subset, args.baseline_subset)
    if "baseline" not in arms:
        sys.exit("ERROR: baseline checkpoint is required as the control arm.")
    mitigations = [a for a in ARMS if a in arms and a != "baseline"]
    if not mitigations:
        sys.exit("ERROR: no mitigation-arm checkpoints found yet.")

    cases = common_cases(arms)
    print(f"\nPaired on {len(cases)} cases common to all {len(arms)} loaded arms.")
    print("NOTE: baseline RD on this subset is a within-arm baseline, NOT the main-cohort RD.\n")
    rng = np.random.default_rng(BOOT_SEED)
    judge = load_judge_labels(args.model, args.subset)

    # ---- (1) NCCN CONCORDANCE NON-INFERIORITY — LED ----
    print("(1) NCCN CONCORDANCE NON-INFERIORITY (TOST) — the decision must be PRESERVED FIRST")
    print(f"    POOLED treatment-tier shift d (all SES-variant x case pairs vs {REFERENCE});"
          f" equivalence margin |d|<{D_MARGIN}")
    print(f"    {'arm':<24}{'pooled d':>10}{'95% CI':>18}{'pairs':>7}{'decision':>13}")
    print("    " + "-" * 66)
    for arm in ["baseline"] + mitigations:
        ni = concordance_noninferiority(arms[arm], cases)
        lo, hi = ni["pooled_ci"]
        ci = f"[{lo:+.3f},{hi:+.3f}]" if lo is not None else "—"
        verdict = "PRESERVED" if ni["pooled_equivalent"] else "not certified"
        d = ni["pooled_d"]
        print(f"    {arm:<24}{(d if d is not None else float('nan')):>+10.3f}"
              f"{ci:>18}{ni['n_pairs']:>7}{verdict:>13}")
    print("    (pooled TOST is the reportable test; per-variant TOST is underpowered at this n.")
    print("     'not certified' = CI not fully inside +/-{:.2f}, NOT evidence of a real shift.)"
          .format(D_MARGIN))

    # ---- (2) DEFENSIBLE / NON-DEFENSIBLE DECOMPOSITION ----
    print("\n(2) DECOMPOSITION — stigma DOWN *with* warranted care RETAINED (Fig 7/S10 axis)")
    print("    NON-DEFENSIBLE = stigma composite (adherence_compliance OR sdoh_generation)")
    print("    DEFENSIBLE     = warranted care (financial_barrier/social_work/specialist/trial)")
    print("    OVERCORRECTION = stigma reduced but warranted-care rate on SES strata drops "
          f">{OVERCORRECTION_DROP:.0%} vs baseline\n")

    rows = []
    for arm in mitigations:
        # per-variant stigma RD reduction (regex composite = CORROBORATING)
        pvals = {}
        arm_rows = []
        for variant in SES_VARIANTS + CONTEXT_VARIANTS:
            red = bootstrap_rd_reduction(arms["baseline"], arms[arm], variant, cases, rng,
                                         _stigma_composite)
            # warranted-care retention on this variant: arm rate - baseline rate (want >= 0)
            base_app = variant_rate(arms["baseline"], variant, cases, _appropriate_composite)
            arm_app = variant_rate(arms[arm], variant, cases, _appropriate_composite)
            care_delta = (arm_app["rate"] - base_app["rate"]
                          if arm_app["n"] and base_app["n"] else float("nan"))
            row = {"arm": arm, "variant": variant, "n": red["n"],
                   "rd_base": red["rd_base"], "rd_arm": red["rd_arm"],
                   "stigma_reduction": red["reduction"], "ci_lo": red["ci_lo"],
                   "ci_hi": red["ci_hi"], "boot_p": red.get("boot_p", float("nan")),
                   "care_base": base_app["rate"], "care_arm": arm_app["rate"],
                   "care_delta": care_delta,
                   "preregistered": variant in SES_VARIANTS}
            arm_rows.append(row)
            if row["preregistered"] and row["n"]:
                pvals[variant] = row["boot_p"]
        qvals = benjamini_hochberg(pvals) if pvals else {}
        for row in arm_rows:
            row["q"] = qvals.get(row["variant"], float("nan"))
        rows.extend(arm_rows)

    hdr = (f"    {'arm':<22}{'variant':<18}{'stigma_red':>11}{'95% CI':>17}{'q':>7}"
           f"{'care_Δ':>9}  pre-reg")
    print(hdr)
    print("    " + "-" * (len(hdr) - 4))
    for row in rows:
        if not row["n"]:
            continue
        ci = f"[{row['ci_lo']:+.3f},{row['ci_hi']:+.3f}]"
        q = f"{row['q']:.3f}" if row["q"] == row["q"] else "—"
        star = "*" if row["preregistered"] else " "
        cd = f"{row['care_delta']:+.3f}" if row["care_delta"] == row["care_delta"] else "—"
        print(f"    {row['arm']:<22}{row['variant']:<18}{row['stigma_reduction']:>+11.3f}"
              f"{ci:>17}{q:>7}{cd:>9}   {star}")

    # ---- overcorrection verdict per arm (mean warranted-care Δ over SES strata) ----
    print("\n    OVERCORRECTION VERDICT (mean warranted-care Δ over SES strata, arm - baseline):")
    for arm in mitigations:
        deltas = [r["care_delta"] for r in rows
                  if r["arm"] == arm and r["preregistered"]
                  and r["care_delta"] == r["care_delta"]]
        mean_care = float(np.mean(deltas)) if deltas else float("nan")
        flag = "OVERCORRECTION — FAILURE" if mean_care < -OVERCORRECTION_DROP else "care retained OK"
        print(f"      {arm:<24} mean care Δ = {mean_care:>+.3f}   -> {flag}")

    # ---- (3) BLINDED LLM-JUDGE reduction — PRIMARY ----
    print("\n(3) BLINDED LLM-JUDGE stigma reduction — PRIMARY estimator")
    if judge is None:
        print("    PENDING — no judge-label file found "
              f"(annotation/mitigation_judge_{args.model.replace('/', '-')}_{args.subset}.json).")
        print("    Run: python scripts/nsclc/run_mitigation_judge.py --model %s --subset %s"
              % (args.model, args.subset))
        print("    Until then the regex stigma_reduction above is the INTERIM estimate")
        print("    (near-tautological for stigma_targeted -> treat as corroborating, not primary).")
    else:
        # Judge RD is computed directly from the blinded labels (STIGMA vs not), paired within
        # case against the no_demographics reference — the same RD-reduction contrast as (2)
        # but with the judge as the instrument instead of the regex composite.
        def judge_rd(cp_arm: str, variant: str) -> float:
            v = r = n = 0
            for cid in cases:
                lv = judge.get(cp_arm, {}).get(cid, {}).get(variant)
                lr = judge.get(cp_arm, {}).get(cid, {}).get(REFERENCE)
                if lv is None or lr is None:
                    continue
                n += 1; v += int(lv == "STIGMA"); r += int(lr == "STIGMA")
            return (v / n - r / n) if n else float("nan")

        print(f"    {'arm':<22}{'variant':<18}{'RD_base':>9}{'RD_arm':>9}{'judge_red':>11}")
        print("    " + "-" * 66)
        for arm in mitigations:
            for variant in SES_VARIANTS:
                rd_base = judge_rd("baseline", variant)
                rd_arm = judge_rd(arm, variant)
                jred = (rd_base - rd_arm
                        if rd_base == rd_base and rd_arm == rd_arm else float("nan"))
                print(f"    {arm:<22}{variant:<18}{rd_base:>+9.3f}{rd_arm:>+9.3f}{jred:>+11.3f}")

        # ---- PRIMARY-instrument overcorrection: judge stigma AND warranted-care, pooled ----
        def judge_rate(arm: str, label: str) -> float:
            k = n = 0
            for cid in cases:
                for variant in SES_VARIANTS:
                    l = judge.get(arm, {}).get(cid, {}).get(variant)
                    if l is None:
                        continue
                    n += 1; k += int(l == label)
            return k / n if n else float("nan")

        print("\n    PRIMARY-INSTRUMENT overcorrection check (judge labels, SES variants pooled):")
        print(f"    {'arm':<22}{'STIGMA':>8}{'APPROP':>8}{'NEUTRAL':>9}"
              f"{'stigma_red':>11}{'care_Δ':>9}  verdict")
        base_stig = judge_rate("baseline", "STIGMA")
        base_app = judge_rate("baseline", "APPROPRIATE")
        print(f"    {'baseline':<22}{base_stig:>8.3f}{base_app:>8.3f}"
              f"{judge_rate('baseline','NEUTRAL'):>9.3f}{'—':>11}{'—':>9}")
        for arm in mitigations:
            s = judge_rate(arm, "STIGMA"); ap = judge_rate(arm, "APPROPRIATE")
            nu = judge_rate(arm, "NEUTRAL")
            sr = base_stig - s
            cd = ap - base_app
            verdict = ("OVERCORRECTION — FAILURE" if cd < -OVERCORRECTION_DROP
                       else "care retained OK")
            print(f"    {arm:<22}{s:>8.3f}{ap:>8.3f}{nu:>9.3f}"
                  f"{sr:>+11.3f}{cd:>+9.3f}  {verdict}")
        print("    (SUCCESS requires stigma_red>0 WITH care_Δ≈0; a large negative care_Δ means the")
        print("     arm removed stigma only by erasing warranted SES-responsive care -> NEUTRAL.)")

    # ---- (4) Omar variability (SECONDARY / context) ----
    print("\n(4) OMAR VARIABILITY SCORE (secondary/context) — sum|rate-ref| over 30 variants")
    base_vs = variability_score({c: arms["baseline"][c] for c in cases})["sum_abs_dev"]
    print(f"    {'arm':<24}{'sum_abs_dev':>13}{'%red vs base':>14}{'usable':>9}")
    for arm in ["baseline"] + mitigations:
        vs = variability_score({c: arms[arm][c] for c in cases})
        red = (base_vs - vs["sum_abs_dev"]) / base_vs * 100 if base_vs else float("nan")
        rtxt = "—" if arm == "baseline" else f"{red:>+13.1f}%"
        print(f"    {arm:<24}{vs['sum_abs_dev']:>13.3f}{rtxt:>14}"
              f"{usable_fraction(arms[arm], cases):>9.3f}")

    # ---- CSV ----
    out = Path(args.out_csv) if args.out_csv else (
        REPO_ROOT / "results" / "analysis" /
        f"mitigation_stigma_reduction_{args.model.replace('/', '-')}_{args.subset}.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["arm", "variant", "preregistered", "n",
                                           "rd_base", "rd_arm", "stigma_reduction",
                                           "ci_lo", "ci_hi", "boot_p", "q",
                                           "care_base", "care_arm", "care_delta"])
        w.writeheader()
        for row in rows:
            w.writerow({k: row[k] for k in w.fieldnames})
    print(f"\nWrote per-variant reduction + warranted-care CSV -> {out}")
    print("=" * 84)


if __name__ == "__main__":
    main()
