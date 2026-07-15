"""Run partial-concordance (secondary/exploratory) analysis on the GENIE BPC
NSCLC cohort, mirroring the reference-vs-with-demographics structure used in
Fig2_concordance_stability.

For every (case, variant) pair this computes the 0/0.5/1.0 partial-concordance
score via _PARTIAL_CONCORDANCE_MAP applied to the existing 0-3 adherence
ordinal (adherence_scorer.compute_adherence_score), the SAME scorer already
used for the binary concordant_primary/concordant_any columns in
scripts/nsclc/analyze_genie_bpc.py and for Fig2's binary rates. This keeps the
partial metric strictly a coarsening of the already-validated pipeline (per
the "Collapse existing adherence ordinal" design decision) rather than a new
scoring path.

Secondary / exploratory: NOT a pre-registered confirmatory outcome. See
docs/METHODS.md section 12.

Usage:
  venv/bin/python scripts/nsclc/analyze_partial_concordance.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.analyze.response_parser import ResponseParser
from src.analyze.adherence_scorer import compute_adherence_score, _PARTIAL_CONCORDANCE_MAP
from src.analyze.stats import wilson_ci, paired_delta

REFERENCE = "no_demographics"

MODELS = {
    "gemini-2.5-flash": "results/baseline/v2_genie_bpc_nsclc_results.json",
    "deepseek-chat":    "results/baseline/v2_genie_bpc_nsclc_deepseek-chat_results.json",
    "llama-3.3-70B":    "results/baseline/v2_genie_bpc_nsclc_meta-llama-Llama-3.3-70B-Instruct-Turbo_results.json",
    "llama-3.1-8B":     "results/baseline/v2_genie_bpc_nsclc_openrouter-meta-llama-llama-3.1-8b-instruct_results.json",
    "gpt-4o":           "results/baseline/v2_genie_bpc_nsclc_gpt-4o_results.json",
    "gpt-4o-mini":      "results/baseline/v2_genie_bpc_nsclc_gpt-4o-mini_results.json",
}

OUT_DIR = Path("results/analysis")
OUT_DIR.mkdir(parents=True, exist_ok=True)

_parser = ResponseParser()


def _partial_score(response_text: str, nccn_label: str | None, nccn_acceptable: list | None) -> float | None:
    if not response_text:
        return None
    parsed = _parser.parse(response_text)
    adh = compute_adherence_score(parsed.category, nccn_label, nccn_acceptable)
    if adh is None:
        return None
    return _PARTIAL_CONCORDANCE_MAP[adh]


def process_model(model: str, path: str) -> dict:
    p = Path(path)
    if not p.exists():
        print(f"  (skip {model}: {path} not found)")
        return {}
    print(f"Loading {model}: {path} ...")
    raw = json.loads(p.read_text())

    # per-case: {case_id: {variant: partial_score_or_None}}
    per_case_variant: dict[str, dict[str, float]] = {}
    for case_id, variants in raw.items():
        row = {}
        for variant_label, result in variants.items():
            if "error" in result:
                continue
            text = result.get("response_text", "")
            score = _partial_score(text, result.get("nccn_label"),
                                    result.get("nccn_acceptable_answers") or [])
            if score is not None:
                row[variant_label] = score
        per_case_variant[case_id] = row

    ref_scores = {cid: v[REFERENCE] for cid, v in per_case_variant.items() if REFERENCE in v}

    # aggregate reference rate/n (Fig2 "ref" bar): mean partial score * 100 as a "% partial concordance"
    ref_vals = np.array(list(ref_scores.values()))
    ref_mean_pct = 100 * ref_vals.mean() if len(ref_vals) else float("nan")
    ref_n = len(ref_vals)

    # aggregate "with demographics" rate/n: pool ALL non-reference variant scores (matches
    # Fig2's n_dem which pools all 29 demographic variants)
    dem_vals = []
    for cid, v in per_case_variant.items():
        for variant_label, score in v.items():
            if variant_label != REFERENCE:
                dem_vals.append(score)
    dem_vals = np.array(dem_vals)
    dem_mean_pct = 100 * dem_vals.mean() if len(dem_vals) else float("nan")
    dem_n = len(dem_vals)

    # per-variant breakdown + paired stats vs reference (for the detail CSV)
    all_variants = sorted({vk for v in per_case_variant.values() for vk in v} - {REFERENCE})
    per_variant_rows = []
    for variant in [REFERENCE] + all_variants:
        var_scores = {cid: v[variant] for cid, v in per_case_variant.items() if variant in v}
        vals = np.array(list(var_scores.values()))
        n = len(vals)
        if n == 0:
            continue
        mean = float(vals.mean())
        if variant == REFERENCE:
            per_variant_rows.append({
                "model": model, "variant": variant, "n": n,
                "partial_concordance_mean": round(mean, 4),
                "paired_delta_vs_reference": None, "paired_ci_low": None,
                "paired_ci_high": None, "paired_p_value_wilcoxon": None,
            })
            continue
        pd_stats = paired_delta(ref_scores, var_scores)
        per_variant_rows.append({
            "model": model, "variant": variant, "n": n,
            "partial_concordance_mean": round(mean, 4),
            "paired_delta_vs_reference": round(pd_stats["delta"], 4) if pd_stats["delta"] is not None else None,
            "paired_ci_low": round(pd_stats["ci_low"], 4) if pd_stats["ci_low"] is not None else None,
            "paired_ci_high": round(pd_stats["ci_high"], 4) if pd_stats["ci_high"] is not None else None,
            "paired_p_value_wilcoxon": pd_stats["p_value"],
        })

    return {
        "model": model,
        "ref_mean_pct": ref_mean_pct, "ref_n": ref_n,
        "dem_mean_pct": dem_mean_pct, "dem_n": dem_n,
        "per_variant_rows": per_variant_rows,
    }


def main():
    summary_rows = []
    all_variant_rows = []
    for model, path in MODELS.items():
        result = process_model(model, path)
        if not result:
            continue
        summary_rows.append({
            "model": result["model"],
            "ref_partial_concordance_pct": round(result["ref_mean_pct"], 2),
            "n_ref": result["ref_n"],
            "dem_partial_concordance_pct": round(result["dem_mean_pct"], 2),
            "n_dem": result["dem_n"],
            "delta_pp": round(result["dem_mean_pct"] - result["ref_mean_pct"], 2),
        })
        all_variant_rows.extend(result["per_variant_rows"])
        print(f"  {model:<18} ref={result['ref_mean_pct']:.2f}% (n={result['ref_n']})  "
              f"dem={result['dem_mean_pct']:.2f}% (n={result['dem_n']})  "
              f"delta={result['dem_mean_pct']-result['ref_mean_pct']:+.2f}pp")

    summary_df = pd.DataFrame(summary_rows)
    variant_df = pd.DataFrame(all_variant_rows)

    summary_path = OUT_DIR / "v2_genie_bpc_nsclc_partial_concordance_summary.csv"
    variant_path = OUT_DIR / "v2_genie_bpc_nsclc_partial_concordance_by_variant.csv"
    summary_df.to_csv(summary_path, index=False)
    variant_df.to_csv(variant_path, index=False)
    print(f"\nwrote {summary_path}")
    print(f"wrote {variant_path}")


if __name__ == "__main__":
    main()
