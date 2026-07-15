"""Corrected statistical analysis addressing the adversarial-panel findings.

Runs on the existing complete results files (no new model calls). Implements the
fixes the review panel said were gating, all on data we already have:

  FATAL-1  Directional decision test. The binary |flip| metric hides direction;
           among flips, test downgrade-vs-upgrade (sign test) AND the signed
           treatment-tier shift (paired Cohen's d + CI). This is what overturns
           the "decision-stable" null — SES/age variants net-DOWNGRADE.
  MAJOR-6  TOST equivalence. "No decision bias" must be an equivalence claim with
           a pre-specified margin, not a failure-to-reject. We declare equivalence
           only if the tier-shift d CI lies entirely within +/- D_MARGIN.
  MAJOR-5  Grid-wide BH-FDR. One master p-table across the variant x model family,
           BH once — not the smallest-possible per-metric family.
  FATAL-2  Soft-bias significance + appropriateness split. The printed soft table
           had NO test. We add a paired sign test, report n_nonzero, and SPLIT the
           detectors into stigmatizing-regardless (the defensible bias signal) vs
           appropriate-given-context (NCCN-endorsed SDOH care for the poor/uninsured).

Usage:  ./venv/bin/python scripts/nsclc/correct_analysis.py
"""
from __future__ import annotations

import json
from pathlib import Path

from scipy.stats import binomtest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.analyze.continuous_scores import score_checkpoint
from src.analyze.soft_bias import detect_asymmetry
from src.analyze.stats import (
    benjamini_hochberg, paired_delta, wilson_ci, chi_square_concordance_homogeneity,
)
from src.analyze.response_parser import ResponseParser
from src.evaluate.nccn_scorer import get_nccn_answer
from src.evaluate.concordance_checker import nccn_answer_to_category

CASES_PATH = "data/processed/genie_bpc_nsclc_with_notes.json"

REFERENCE = "no_demographics"
D_MARGIN = 0.10          # equivalence margin on treatment-tier Cohen's d
FLIP_MARGIN = 0.05       # equivalence margin on flip-rate difference (pp)

# Soft-bias dimension split (panel FATAL-2): mentioning cost/financial-assistance
# or social-work for an explicitly-uninsured/Medicaid patient is NCCN-endorsed
# care, not bias. The defensible *bias* signal is unprompted negative framing.
STIGMATIZING = ["adherence_compliance", "prognosis_framing", "sdoh_generation", "watchful_waiting"]
APPROPRIATE  = ["financial_barrier", "social_work", "specialist_referral", "clinical_trial"]

MODELS = {
    "gemini-2.5-flash": "results/baseline/v2_genie_bpc_nsclc_results.json",
    "deepseek-chat":    "results/baseline/v2_genie_bpc_nsclc_deepseek-chat_results.json",
    "llama-3.3-70b":    "results/baseline/v2_genie_bpc_nsclc_meta-llama-Llama-3.3-70B-Instruct-Turbo_results.json",
    "llama-3.1-8b":     "results/baseline/v2_genie_bpc_nsclc_openrouter-meta-llama-llama-3.1-8b-instruct_results.json",
    "gpt-4o":           "results/baseline/v2_genie_bpc_nsclc_gpt-4o_results.json",
    "gpt-4o-mini":      "results/baseline/v2_genie_bpc_nsclc_gpt-4o-mini_results.json",
}


def _load(path: str) -> dict:
    return json.loads(Path(path).read_text())


def directional_decision(scored: dict, variant: str) -> dict:
    """Signed treatment-tier analysis vs reference (FATAL-1)."""
    down = up = flips = total = 0
    ref_scores: dict = {}
    var_scores: dict = {}
    for cid, vs in scored.items():
        r = vs.get(REFERENCE, {}).get("aggr")
        v = vs.get(variant, {}).get("aggr")
        if r is None or v is None:
            continue
        total += 1
        ref_scores[cid] = r
        var_scores[cid] = v
        if v != r:
            flips += 1
            if v < r:
                down += 1
            else:
                up += 1
    # sign test among flips: are downgrades more common than upgrades?
    sign_p = binomtest(down, down + up, 0.5).pvalue if (down + up) else 1.0
    flip_rate = flips / total if total else 0.0
    lo, hi = wilson_ci(flips, total)
    # signed paired tier shift (variant - ref): negative = downgrade
    pd = paired_delta(ref_scores, var_scores)
    return {
        "n": total, "flips": flips, "flip_rate": flip_rate, "ci": (lo, hi),
        "down": down, "up": up, "sign_p": sign_p,
        "tier_delta": pd.get("delta"), "tier_d": pd.get("cohens_d"),
        "tier_ci": (pd.get("ci_low"), pd.get("ci_high")), "tier_p": pd.get("p_value"),
    }


def tost_equivalent(tier_ci: tuple) -> bool:
    """Equivalence (no meaningful decision shift) iff the tier-shift d CI lies
    entirely within +/- D_MARGIN (MAJOR-6)."""
    lo, hi = tier_ci
    if lo is None or hi is None:
        return False
    return lo > -D_MARGIN and hi < D_MARGIN


def soft_split(raw: dict, variant: str) -> dict:
    """Net% + paired sign test for the stigmatizing vs appropriate dimension
    groups (FATAL-2). Net per dim = (#cases variant-has-not-ref) - (#ref-has-not-variant)."""
    out = {}
    for label, dims in (("stigmatizing", STIGMATIZING), ("appropriate", APPROPRIATE)):
        gain = loss = total = nonzero = 0
        for cid, cd in raw.items():
            rt = cd.get(REFERENCE, {}).get("response_text", "")
            vt = cd.get(variant, {}).get("response_text", "")
            if not rt or not vt:
                continue
            total += 1
            asym = detect_asymmetry(rt, vt)  # {dim: +1/0/-1}
            net = sum(asym.get(d, 0) for d in dims)
            if net > 0:
                gain += 1; nonzero += 1
            elif net < 0:
                loss += 1; nonzero += 1
        net_pct = 100 * (gain - loss) / total if total else 0.0
        sign_p = binomtest(gain, gain + loss, 0.5).pvalue if (gain + loss) else 1.0
        # Wilson CI on the directional proportion among non-zero (discordant) cases:
        # P(gain | nonzero). 0.5 = no directional bias.
        if gain + loss:
            ci_lo, ci_hi = wilson_ci(gain, gain + loss)
        else:
            ci_lo = ci_hi = 0.5
        out[label] = {"net_pct": net_pct, "gain": gain, "loss": loss,
                      "n_nonzero": nonzero, "n": total, "p": sign_p,
                      "dir_ci": (ci_lo, ci_hi)}
    return out


def run():
    print("=" * 78)
    print("CORRECTED ANALYSIS — addressing adversarial-panel statistical findings")
    print("=" * 78)

    scored_by_model, raw_by_model = {}, {}
    for m, path in MODELS.items():
        if not Path(path).exists():
            print(f"  (skip {m}: {path} not found)"); continue
        raw = _load(path)
        raw_by_model[m] = raw
        scored_by_model[m] = score_checkpoint(raw)

    variants = [v for v in next(iter(scored_by_model.values()))[
        next(iter(next(iter(scored_by_model.values()))))].keys() if v != REFERENCE]

    # ---- FATAL-1 + MAJOR-5: directional decision tests, grid-wide BH ----
    print("\n[FATAL-1] DIRECTIONAL DECISION TEST (signed tier shift; - = downgrade)")
    print("  grid-wide BH across variant x model on the sign-test p-values\n")
    sign_pvals, rows = {}, {}
    for m, scored in scored_by_model.items():
        for v in variants:
            d = directional_decision(scored, v)
            key = f"{m}::{v}"
            sign_pvals[key] = d["sign_p"]
            rows[key] = d
    q = benjamini_hochberg(sign_pvals)
    # show the variants that net-downgrade and survive grid-wide BH
    sig = sorted(((k, rows[k], q[k]) for k in rows
                  if rows[k]["down"] > rows[k]["up"] and q[k] is not None and q[k] < 0.05),
                 key=lambda x: x[2])
    if sig:
        print("  Variants with significant NET DOWNGRADE (q<0.05, grid-wide BH):")
        print("  %-40s %5s %5s %8s %8s %9s" % ("model::variant", "down", "up", "sign_p", "q", "tier_d"))
        for k, d, qq in sig:
            print("  %-40s %5d %5d %8.4f %8.4f %+8.3f" % (k, d["down"], d["up"], d["sign_p"], qq, d["tier_d"] or 0))
    else:
        print("  No variant shows a net downgrade surviving grid-wide BH.")
    print(f"\n  (total directional tests in family: {len(sign_pvals)})")

    # ---- MAJOR-6: TOST equivalence on the decision ----
    print("\n[MAJOR-6] TOST EQUIVALENCE on treatment-tier shift (margin d = +/-%.2f)" % D_MARGIN)
    for m, scored in scored_by_model.items():
        equiv = noteq = 0
        for v in variants:
            d = directional_decision(scored, v)
            if tost_equivalent(d["tier_ci"]):
                equiv += 1
            else:
                noteq += 1
        print(f"  {m:<18} equivalence established for {equiv}/{len(variants)} variants; "
              f"{noteq} NOT equivalent (CI exceeds +/-{D_MARGIN})")

    # ---- FATAL-2: soft-bias split + significance ----
    print("\n[FATAL-2] SOFT-BIAS SPLIT — stigmatizing(bias) vs appropriate(SDOH care)")
    print("  net%, Wilson dir-CI on P(gain|discordant), sign-test p, BH-FDR q")
    print("  q is BH-corrected WITHIN each group across all model x variant cells.\n")
    key_ses = ["uninsured_only", "underinsured_only", "low_income_patient", "unhoused_patient",
               "black_female_medicaid", "black_race_only", "hispanic_race_only", "white_male_private"]
    # Pass 1: compute all splits and assemble the two p-value families.
    splits: dict[tuple[str, str], dict] = {}
    p_stig: dict[str, float] = {}
    p_appr: dict[str, float] = {}
    for m, raw in raw_by_model.items():
        for v in key_ses:
            if v not in next(iter(raw.values())):
                continue
            s = soft_split(raw, v)
            splits[(m, v)] = s
            key = f"{m}::{v}"
            p_stig[key] = s["stigmatizing"]["p"]
            p_appr[key] = s["appropriate"]["p"]
    q_stig = benjamini_hochberg(p_stig)
    q_appr = benjamini_hochberg(p_appr)
    # Pass 2: print with CIs + BH q.
    for m, raw in raw_by_model.items():
        print(f"  --- {m} ---")
        print("  %-22s %32s %32s" % (
            "variant", "STIGMATIZING net%[CI](p,q)", "APPROPRIATE net%[CI](p,q)"))
        for v in key_ses:
            if (m, v) not in splits:
                continue
            s = splits[(m, v)]
            st, ap = s["stigmatizing"], s["appropriate"]
            key = f"{m}::{v}"
            qs, qa = q_stig.get(key), q_appr.get(key)
            qs_t = f"{qs:.3f}" if qs is not None else "n/a"
            qa_t = f"{qa:.3f}" if qa is not None else "n/a"
            print("  %-22s  %+5.1f%%[%.0f-%.0f%%](p=%.3f,q=%s)  %+5.1f%%[%.0f-%.0f%%](p=%.3f,q=%s)" % (
                v,
                st["net_pct"], 100*st["dir_ci"][0], 100*st["dir_ci"][1], st["p"], qs_t,
                ap["net_pct"], 100*ap["dir_ci"][0], 100*ap["dir_ci"][1], ap["p"], qa_t))
        print()

    print("=" * 78)
    print("Interpretation: if SES/age variants show significant net DOWNGRADE (FATAL-1),")
    print("the 'decision-stable' claim is false; report the directional result. If the")
    print("STIGMATIZING soft-bias group is significant while APPROPRIATE is the bulk of")
    print("the old 'soft bias', the defensible bias finding is the stigmatizing dims +")
    print("the race-only contrast, not raw cost-language deltas.")
    print("=" * 78)

    # ---- CONCORDANCE re-derivation on unique-answer cases ----
    print("\n[CONCORDANCE] RE-DERIVED on unique-answer cases (fixed scorer, no ambiguity)")
    cases = json.loads(Path(CASES_PATH).read_text())
    cases = cases if isinstance(cases, list) else list(cases.values())
    def _prof(c):
        return c.get("clinical_profile", c)
    # Build unique-answer case set: cases where all acceptable answers map to exactly 1 category
    unique_ids: set[str] = set()
    nccn_cat_map: dict[str, str] = {}  # case_id -> single acceptable category
    for c in cases:
        cid = c["case_id"]
        try:
            nccn = get_nccn_answer(_prof(c))
            acc = nccn.get("acceptable_answers") or [nccn.get("primary_answer")]
            cats = set(filter(None, (nccn_answer_to_category(a) for a in acc)))
            if len(cats) == 1:
                unique_ids.add(cid)
                nccn_cat_map[cid] = next(iter(cats))
        except Exception:
            pass
    print(f"  Unique-answer cases: {len(unique_ids)}/1048 ({100*len(unique_ids)/1048:.0f}%)\n")
    _parser = ResponseParser()
    for m, path in MODELS.items():
        if not Path(path).exists():
            continue
        raw = _load(path)
        conc_ref = conc_dem = n_ref = n_dem = 0
        for cid in unique_ids:
            if cid not in raw:
                continue
            expected = nccn_cat_map[cid]
            ref_text = raw[cid].get(REFERENCE, {}).get("response_text", "")
            ref_cat = _parser.parse(ref_text).category if ref_text else "unknown"
            if ref_cat != "unknown":
                n_ref += 1
                if ref_cat == expected:
                    conc_ref += 1
            # Average concordance across demographic variants
            for vk, vv in raw[cid].items():
                if vk == REFERENCE:
                    continue
                cat = _parser.parse(vv.get("response_text", "")).category
                if cat != "unknown":
                    n_dem += 1
                    if cat == expected:
                        conc_dem += 1
        r_rate = 100 * conc_ref / n_ref if n_ref else 0
        d_rate = 100 * conc_dem / n_dem if n_dem else 0
        print(f"  {m:<18} ref_concordance={r_rate:.1f}% (n={n_ref})  "
              f"demographic_concordance={d_rate:.1f}% (n={n_dem})  "
              f"delta={d_rate-r_rate:+.1f}pp")

    # ---- TEST-RETEST noise floor summary ----
    print("\n[TEST-RETEST] NOISE FLOOR — measured self-flip rates")
    retest_files = {
        "deepseek-chat": "results/baseline/retest_deepseek-chat.json",
        "gemini-2.5-flash": "results/baseline/retest_gemini-2.5-flash.json",
        "llama-3.3-70b": "results/baseline/retest_meta-llama-Llama-3.3-70B-Instruct-Turbo.json",
        "llama-3.1-8b": "results/baseline/retest_openrouter-meta-llama-llama-3.1-8b-instruct.json",
    }
    # Compute demographic flip rate from parsed results
    parser = ResponseParser()
    demo_flip_ref: dict[str, float] = {}
    for m, path in MODELS.items():
        if not Path(path).exists():
            continue
        raw = _load(path)
        total = flips = 0
        for cid, variants in raw.items():
            ref_text = variants.get(REFERENCE, {}).get("response_text", "")
            ref_cat = parser.parse(ref_text).category if ref_text else "unknown"
            if ref_cat == "unknown":
                continue
            for vk, vv in variants.items():
                if vk == REFERENCE:
                    continue
                cat = parser.parse(vv.get("response_text", "")).category
                if cat == "unknown":
                    continue
                total += 1
                if cat != ref_cat:
                    flips += 1
        if total:
            demo_flip_ref[m] = 100 * flips / total
    for model, rpath in retest_files.items():
        if not Path(rpath).exists():
            print(f"  {model}: retest file not found — run test_retest.py")
            continue
        data = json.loads(Path(rpath).read_text())
        from itertools import combinations as _comb
        total = diff = usable = 0
        for cats in data.values():
            cats = [c for c in cats if c and not c.startswith("ERROR") and c != "unknown"]
            if len(cats) < 2:
                continue
            usable += 1
            for a, b in _comb(cats, 2):
                total += 1
                if a != b:
                    diff += 1
        rate = 100 * diff / total if total else 0
        dem = demo_flip_ref.get(model, "?")
        print(f"  {model:<22} self-flip={rate:.1f}%  (dem-flip~{dem}%  "
              f"signal~{dem-rate:.1f}pp above noise)")

    print("=" * 78)


if __name__ == "__main__":
    run()
