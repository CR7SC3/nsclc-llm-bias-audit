"""Detect within-category drug-tier downgrades that category-level flip
detection misses entirely.

Motivation
----------
response_parser.py buckets responses into coarse categories (e.g.
"targeted_therapy" covers both osimertinib and erlotinib). The main flip
metric (analyze_results_v2.py::_flip_stats) only fires when a variant's
CATEGORY differs from the reference's. So if a case's ground-truth branch
offers a preferred drug (e.g. osimertinib) and an older/cheaper "other
recommended" alternative for the SAME actionable mutation (e.g. erlotinib —
see DRUG_TIER_BY_PRIMARY in src/evaluate/nccn_scorer.py), a demographic
variant getting steered from the preferred to the other-recommended drug is
currently invisible: both are "targeted_therapy", so category-level flip
detection reports no_change.

This script quantifies how often that actually happens in already-collected
data. It is a read-only exploratory analysis — it does NOT feed the
manuscript pipeline. Run it, read the printed summary, and decide from there
whether/how to wire a tier-downgrade signal into the real flip metric.

Usage
-----
    venv/bin/python scripts/nsclc/detect_drug_tier_downgrade.py \\
        results/baseline/v2_genie_bpc_nsclc_checkpoint.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.analyze.response_parser import ResponseParser  # noqa: E402
from src.evaluate.nccn_scorer import DRUG_TIER_BY_PRIMARY, drug_tier  # noqa: E402

REFERENCE_VARIANT = "no_demographics"
_parser = ResponseParser()

# Component-keyword signature for every drug/combo string appearing in
# DRUG_TIER_BY_PRIMARY, so a combo like "carboplatin + pemetrexed +
# pembrolizumab" can be matched against free text regardless of word order
# or connective phrasing ("carboplatin, pemetrexed, and pembrolizumab").
_KEYWORD_OVERRIDES = {
    "nab-paclitaxel": r"nab.?paclitaxel|paclitaxel\s+protein.bound",
}


def _signature(drug_or_combo: str) -> dict[str, re.Pattern]:
    parts = [p.strip() for p in drug_or_combo.split("+")]
    sig = {}
    for p in parts:
        pat = _KEYWORD_OVERRIDES.get(p, re.escape(p))
        sig[p] = re.compile(pat, re.IGNORECASE)
    return sig


# {primary_answer: {drug_or_combo: {component: compiled_pattern}}}
_SIGNATURES: dict[str, dict[str, dict[str, re.Pattern]]] = {
    primary: {d: _signature(d) for d in tiers}
    for primary, tiers in DRUG_TIER_BY_PRIMARY.items()
}


def _match_drug(primary_answer: str, text: str) -> str | None:
    """Return the drug/combo string (a DRUG_TIER_BY_PRIMARY key) whose full
    component signature is present in *text*, preferring the candidate with
    the most components (most specific match). None if no candidate's full
    signature is present."""
    candidates = _SIGNATURES.get(primary_answer, {})
    best, best_n = None, 0
    for drug, sig in candidates.items():
        if all(pat.search(text) for pat in sig.values()):
            if len(sig) > best_n:
                best, best_n = drug, len(sig)
    return best


def _extracted_text(parsed) -> str:
    return parsed.regimen_tag or parsed.primary_section or ""


def analyze(checkpoint_path: Path) -> None:
    data = json.loads(checkpoint_path.read_text())

    eligible = 0
    unclear = 0  # ground-truth branch is tiered but drug couldn't be matched on one/both sides
    downgrades = 0
    category_masked = 0  # downgrades where category ALSO stayed the same (the blind spot)
    by_variant = defaultdict(lambda: {"eligible": 0, "downgrades": 0})
    examples = []

    for case_id, variants in data.items():
        ref = variants.get(REFERENCE_VARIANT)
        if not (isinstance(ref, dict) and ref.get("response_text")):
            continue
        primary = (ref.get("nccn_label") or "").strip()
        if primary not in DRUG_TIER_BY_PRIMARY:
            continue

        ref_parsed = _parser.parse(ref["response_text"])
        ref_drug = _match_drug(primary, _extracted_text(ref_parsed))
        ref_tier = drug_tier(primary, ref_drug) if ref_drug else None

        for vk, rec in variants.items():
            if vk == REFERENCE_VARIANT or not (isinstance(rec, dict) and rec.get("response_text")):
                continue
            var_parsed = _parser.parse(rec["response_text"])
            var_drug = _match_drug(primary, _extracted_text(var_parsed))
            var_tier = drug_tier(primary, var_drug) if var_drug else None

            if ref_tier is None or var_tier is None:
                unclear += 1
                continue

            eligible += 1
            by_variant[vk]["eligible"] += 1
            is_downgrade = ref_tier == "preferred" and var_tier == "other_recommended"
            if is_downgrade:
                downgrades += 1
                by_variant[vk]["downgrades"] += 1
                same_category = ref_parsed.category == var_parsed.category
                if same_category:
                    category_masked += 1
                if len(examples) < 10:
                    examples.append({
                        "case_id": case_id, "variant": vk, "primary_answer": primary,
                        "ref_drug": ref_drug, "var_drug": var_drug,
                        "same_category": same_category,
                        "category": f"{ref_parsed.category} -> {var_parsed.category}",
                    })

    print(f"=== {checkpoint_path.name} ===")
    print(f"eligible (case,variant) pairs on a tiered branch with a matched drug both sides: {eligible}")
    print(f"unclear (tiered branch, drug not confidently matched on one/both sides):        {unclear}")
    print(f"tier downgrades (preferred -> other_recommended):                                {downgrades}"
          f"  ({100*downgrades/eligible:.2f}% of eligible)" if eligible else "")
    print(f"  of which category-level flip detection would report NO CHANGE (the blind spot): "
          f"{category_masked}/{downgrades}" if downgrades else "")
    print("\nBy variant (top 15 by downgrade count):")
    ranked = sorted(by_variant.items(), key=lambda kv: -kv[1]["downgrades"])
    for vk, c in ranked[:15]:
        if c["downgrades"]:
            print(f"  {vk:28s} {c['downgrades']:4d}/{c['eligible']:5d}"
                  f"  ({100*c['downgrades']/c['eligible']:.1f}%)")
    print("\nExamples:")
    for e in examples:
        print(f"  {e['case_id']:45s} {e['variant']:22s} "
              f"{e['ref_drug']} -> {e['var_drug']}  "
              f"category {e['category']}  same_category={e['same_category']}")
    print()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("checkpoints", nargs="+", type=Path)
    args = ap.parse_args()
    for p in args.checkpoints:
        analyze(p)
