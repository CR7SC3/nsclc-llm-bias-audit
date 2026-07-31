"""Restricted (control-concordant) bias-gap analysis — Claude-Council verdict.

Implements the collaborator's two-part frame WITHOUT new model calls, reusing the
existing validated scorers on the 6 raw baseline checkpoints:

  PART 1 (Net Bias effect)  — absolute NCCN concordance per demographic label,
                              on the FULL scoreable denominator (marginal). Keeps
                              demographic UPGRADES visible.

  PART 2 (Bias gap vs control)
    HARD endpoint — restricted to the CONTROL-concordant subset (cases where the
                    no_demographics reference is guideline-concordant). On that
                    subset control-concordance == 1 by construction, so the
                    label-attributable harm is the one-sided DOWNGRADE rate
                    P(variant discordant | control concordant); reported with a
                    Wilson CI. Delta_concordance_restricted = -downgrade_rate.
                    The FULL-sample disparity (rate - ref_rate) + Fisher p is ALSO
                    emitted as a labelled MARGINAL/SENSITIVITY row — NOT the harm
                    metric (it is contaminated by already-discordant controls).
    SOFT endpoint — stigmatizing-framing net% + paired sign test on the FULL
                    sample (primary); the same net% on the control-concordant
                    subset is emitted only as a flagged ROBUSTNESS column.

Council rulings honoured:
  * Control = no_demographics (the neutral anchor), never white_male_private.
  * "Concordant" = the PRE-REGISTERED binary from concordance_checker:
    llm_category in acceptable_cats (adherence {2,3} -> partial 1.0), i.e. the
    Fig2 binary — NOT strict adherence==3. This is the definition-drift guard the
    council flagged as risk #1: the mask must match Fig2's binary rate. We source
    nccn_label / nccn_acceptable_answers from each stored record (what the model
    was scored against) and map with nccn_answer_to_category, exactly as
    concordance_checker does.
  * SOFT stays FULL as primary (restriction only costs power, no estimand gain).

Outputs:
  results/analysis/v2_genie_bpc_nsclc_restricted_bias_gap_by_variant.csv
  results/analysis/v2_genie_bpc_nsclc_restricted_venn_counts.csv

Usage:  ./venv/bin/python scripts/nsclc/restricted_bias_gap.py
"""
from __future__ import annotations

import csv
import gc
import json
from pathlib import Path

from scipy.stats import binomtest, fisher_exact

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.analyze.response_parser import ResponseParser
from src.analyze.soft_bias import DIMENSIONS
from src.analyze.stats import wilson_ci
from src.evaluate.concordance_checker import nccn_answer_to_category

# Line-buffer stdout so progress is visible in the redirected log (block-buffering
# otherwise hides all prints until the process exits).
try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

REFERENCE = "no_demographics"
OUT_DIR = Path("results/analysis")

# Pre-registered defensible composite (matches finalize_panel.py STIGMA and the
# starred dimensions in plot_stigma_breakdown.py / Figure 4, S4, S9). An earlier
# version of this list matched correct_analysis.py's broader 4-dim split instead;
# that list is not the paper's pre-registered composite, so it undercounted the
# restricted soft-bias signal (80/174 significant cells vs. 93/174 on this list).
STIGMATIZING = ["adherence_compliance", "sdoh_generation"]
# Only the stigmatizing dimension detectors — precomputed once per response text
# (detect_asymmetry would re-scan all 11 dims on BOTH texts every call, so the
# reference text got re-scanned once per variant; this avoids that O(variants) blow-up).
_STIG_DIMS = [d for d in DIMENSIONS if d.key in STIGMATIZING]


def _stig_flags(text: str) -> tuple[bool, ...]:
    """Fire the stigmatizing detectors on one response text (once)."""
    return tuple(d.detect(text) for d in _STIG_DIMS)


def _stig_net(ref_f: tuple, var_f: tuple) -> int:
    """Net stigmatizing asymmetry: +1 variant-has-not-ref, -1 ref-has-not-variant."""
    return sum((1 if (v and not r) else -1 if (r and not v) else 0)
               for r, v in zip(ref_f, var_f))

MODELS = {
    "gemini-2.5-flash": "results/baseline/v2_genie_bpc_nsclc_results.json",
    "deepseek-chat":    "results/baseline/v2_genie_bpc_nsclc_deepseek-chat_results.json",
    "llama-3.3-70b":    "results/baseline/v2_genie_bpc_nsclc_meta-llama-Llama-3.3-70B-Instruct-Turbo_results.json",
    "llama-3.1-8b":     "results/baseline/v2_genie_bpc_nsclc_openrouter-meta-llama-llama-3.1-8b-instruct_results.json",
    "gpt-4o":           "results/baseline/v2_genie_bpc_nsclc_gpt-4o_results.json",
    "gpt-4o-mini":      "results/baseline/v2_genie_bpc_nsclc_gpt-4o-mini_results.json",
}

_parser = ResponseParser()


def _acceptable_cats(rec: dict) -> tuple[str | None, set[str], bool]:
    """Reproduce concordance_checker's acceptable-category set from a stored record.

    Returns (primary_cat, acceptable_cats, scoreable). Uses the record's own
    nccn_label / nccn_acceptable_answers — the ground truth the model was scored
    against — mapped by nccn_answer_to_category (same mapping the checker uses).
    """
    primary = rec.get("nccn_label")
    if not primary or primary in ("NOT_IMPLEMENTED", ""):
        return None, set(), False
    primary_cat = nccn_answer_to_category(primary)
    if primary_cat is None:
        return None, set(), False
    acc = {primary_cat}
    for a in (rec.get("nccn_acceptable_answers") or []):
        c = nccn_answer_to_category(a)
        if c:
            acc.add(c)
    return primary_cat, acc, True


def _concordant(rec: dict, acc: set[str]) -> bool | None:
    """Pre-registered binary: llm_category in acceptable_cats. None if not scoreable."""
    text = rec.get("response_text", "") if rec else ""
    if not text:
        return None
    cat = _parser.parse(text).category
    if cat in ("unknown", "error", None):
        return None
    return cat in acc


def analyse_model(model: str, raw: dict) -> tuple[list[dict], dict]:
    """Return (per-variant rows, venn-count dict) for one model.

    Single parse pass: concordance and stigmatizing-asymmetry are each computed
    once per (case, variant), then all aggregation is pure counting over id sets.
    """
    variants = [v for v in next(iter(raw.values())).keys() if v != REFERENCE]

    # Per-case reference concordance + acceptable-cat set (computed once).
    ref_conc: dict[str, bool | None] = {}
    acc_by_case: dict[str, set[str]] = {}
    ref_text_by_case: dict[str, str] = {}
    scoreable_ids: set[str] = set()
    for cid, vd in raw.items():
        ref_rec = vd.get(REFERENCE)
        if ref_rec is None:
            continue
        _pc, acc, scoreable = _acceptable_cats(ref_rec)
        if not scoreable:
            continue
        scoreable_ids.add(cid)
        acc_by_case[cid] = acc
        ref_conc[cid] = _concordant(ref_rec, acc)
        ref_text_by_case[cid] = ref_rec.get("response_text", "")

    ctrl_conc_ids = {cid for cid in scoreable_ids if ref_conc.get(cid) is True}

    # ref concordance rate on the full scoreable set (for disparity).
    ref_scoreable = [cid for cid in scoreable_ids if ref_conc.get(cid) is not None]
    ref_conc_n = sum(1 for cid in ref_scoreable if ref_conc[cid])
    ref_disc_n = len(ref_scoreable) - ref_conc_n
    ref_rate = ref_conc_n / len(ref_scoreable) if ref_scoreable else 0.0

    # Single pass: concordant flag + stigmatizing net per (case, variant).
    # Reference stigmatizing flags computed ONCE per case (not per variant).
    conc: dict[str, dict[str, bool | None]] = {}
    stig: dict[str, dict[str, int]] = {}
    for cid in scoreable_ids:
        acc = acc_by_case[cid]
        rt = ref_text_by_case[cid]
        ref_f = _stig_flags(rt) if rt else None
        cc, ss = {}, {}
        for v in variants:
            rec = raw[cid].get(v)
            cc[v] = _concordant(rec, acc)
            vt = rec.get("response_text", "") if rec else ""
            if ref_f is not None and vt:
                ss[v] = _stig_net(ref_f, _stig_flags(vt))
            else:
                ss[v] = None
        conc[cid] = cc
        stig[cid] = ss

    rows = []
    nested_both = []  # per-variant count of (ref concordant AND variant concordant)
    for v in variants:
        # ---- Part 1: full absolute concordance for this variant ----
        full_ids = [cid for cid in scoreable_ids if conc[cid][v] is not None]
        n_full = len(full_ids)
        conc_full_n = sum(1 for cid in full_ids if conc[cid][v])
        abs_conc_full = conc_full_n / n_full if n_full else 0.0
        disparity_full = abs_conc_full - ref_rate

        # Fisher 2x2: [[ref_conc, ref_disc], [var_conc, var_disc]] on full scoreable
        var_disc_n = n_full - conc_full_n
        try:
            _odds, disparity_p = fisher_exact(
                [[ref_conc_n, ref_disc_n], [conc_full_n, var_disc_n]])
        except ValueError:
            disparity_p = 1.0

        # ---- Part 2 HARD: restricted to control-concordant subset ----
        sub = [cid for cid in ctrl_conc_ids if conc[cid][v] is not None]
        n_ctrl = len(sub)
        both_n = sum(1 for cid in sub if conc[cid][v])
        downgrade_n = n_ctrl - both_n
        downgrade_rate = downgrade_n / n_ctrl if n_ctrl else 0.0
        dr_lo, dr_hi = wilson_ci(downgrade_n, n_ctrl) if n_ctrl else (0.0, 0.0)
        delta_conc_restricted = -downgrade_rate
        nested_both.append(both_n)

        # ---- SOFT: stigmatizing net% + sign test (full primary, restricted robustness) ----
        soft_net_full, soft_p_full = _soft_net(stig, v, scoreable_ids)
        soft_net_restr, soft_p_restr = _soft_net(stig, v, ctrl_conc_ids)

        rows.append({
            "model": model,
            "variant": v,
            "n_full": n_full,
            "n_ctrl_concordant": n_ctrl,
            "downgrade_n": downgrade_n,
            "downgrade_rate_restricted": round(downgrade_rate, 5),
            "dr_ci_low": round(dr_lo, 5),
            "dr_ci_high": round(dr_hi, 5),
            "delta_concordance_restricted": round(delta_conc_restricted, 5),
            "abs_concordance_full": round(abs_conc_full, 5),
            "ref_concordance_full": round(ref_rate, 5),
            "disparity_full": round(disparity_full, 5),
            "disparity_full_p_fisher": round(disparity_p, 5),
            "soft_net_full": round(soft_net_full, 3),
            "soft_net_full_p": round(soft_p_full, 5),
            "soft_net_restricted": round(soft_net_restr, 3),
            "soft_net_restricted_p": round(soft_p_restr, 5),
        })

    venn = {
        "model": model,
        "n_total": len(raw),
        "n_scoreable": len(scoreable_ids),
        "n_ctrl_concordant": len(ctrl_conc_ids),
        # mean over variants of (control-concordant AND variant-concordant)
        "n_ctrl_concordant_and_variant_concordant": round(sum(nested_both) / len(nested_both)) if nested_both else 0,
    }
    return rows, venn


def _soft_net(stig: dict, variant: str, ids) -> tuple[float, float]:
    """Stigmatizing-framing net% + paired sign p from the precomputed table."""
    gain = loss = total = 0
    for cid in ids:
        net = stig.get(cid, {}).get(variant)
        if net is None:
            continue
        total += 1
        if net > 0:
            gain += 1
        elif net < 0:
            loss += 1
    net_pct = 100 * (gain - loss) / total if total else 0.0
    sign_p = binomtest(gain, gain + loss, 0.5).pvalue if (gain + loss) else 1.0
    return net_pct, sign_p


GAP_COLS = [
    "model", "variant", "n_full", "n_ctrl_concordant", "downgrade_n",
    "downgrade_rate_restricted", "dr_ci_low", "dr_ci_high",
    "delta_concordance_restricted", "abs_concordance_full", "ref_concordance_full",
    "disparity_full", "disparity_full_p_fisher", "soft_net_full", "soft_net_full_p",
    "soft_net_restricted", "soft_net_restricted_p",
]
VENN_COLS = ["model", "n_total", "n_scoreable", "n_ctrl_concordant",
             "n_ctrl_concordant_and_variant_concordant"]


def run():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    gap_path = OUT_DIR / "v2_genie_bpc_nsclc_restricted_bias_gap_by_variant.csv"
    venn_path = OUT_DIR / "v2_genie_bpc_nsclc_restricted_venn_counts.csv"

    print("=" * 78)
    print("RESTRICTED (control-concordant) BIAS-GAP — Council verdict: restrict-hard, full-soft")
    print("  concordant := llm_category in acceptable_cats (pre-registered Fig2 binary)")
    print("=" * 78)

    n_rows = 0
    with gap_path.open("w", newline="") as gf, venn_path.open("w", newline="") as vf:
        gw = csv.DictWriter(gf, fieldnames=GAP_COLS)
        gw.writeheader()
        vw = csv.DictWriter(vf, fieldnames=VENN_COLS)
        vw.writeheader()
        for model, path in MODELS.items():
            if not Path(path).exists():
                print(f"  (skip {model}: {path} not found)")
                continue
            import time
            t0 = time.time()
            raw = json.loads(Path(path).read_text())
            rows, venn = analyse_model(model, raw)
            gw.writerows(rows)
            vw.writerow(venn)
            gf.flush(); vf.flush()
            n_rows += len(rows)
            ref_rate = rows[0]["ref_concordance_full"] if rows else 0.0
            print(f"  {model:<18} scoreable={venn['n_scoreable']:>4}  "
                  f"control-concordant={venn['n_ctrl_concordant']:>4} "
                  f"({100*venn['n_ctrl_concordant']/venn['n_scoreable']:.1f}%)  "
                  f"ref_conc(in-acc)={100*ref_rate:.1f}%  [{time.time()-t0:.0f}s]")
            del raw, rows
            gc.collect()  # release ~416MB before loading next model

    print("-" * 78)
    print(f"  wrote {gap_path}  ({n_rows} rows)")
    print(f"  wrote {venn_path}")
    print("=" * 78)


if __name__ == "__main__":
    run()
