#!/usr/bin/env python3
"""Build a fresh, diverse example packet for Bhavneet to inductively develop a
stigma/bias rubric from -- NOT drawn from any existing packet (contrastive_packet_60,
gold_flagged_*, gold_random_*, judge_items*, judge_bias_probe_items). Spans all 29
demographic variants and rotates across all 6 models, pairing each selected response
with its no_demographics reference for the same case so the contrast is visible.

For each variant: one "high signal" example and one "low/no signal" example (different
case), so Bhavneet sees both ends of the spectrum, not just pre-filtered "obviously
biased" cases.

Two things this excludes/corrects vs. a naive "most regex dims flagged" pick:
  1. `clinical_trial` is dropped from selection scoring entirely. Its regex
     (`clinical\\s+trial|KEYNOTE|CheckMate|IMpower|NCT\\d|...`) fires on routine
     evidence-citation language ("the KEYNOTE-024 trial demonstrated...") as often as
     on genuine differential trial-referral language, so it was dominating "high
     signal" picks (62% of rows in the first draft) without being a real bias signal
     most of the time. It's still shown in classifier_dims_flagged/flagged_lines for
     transparency, just not used to decide what gets selected.
  2. Selection uses a novelty-weighted score across the remaining 10 dimensions, so a
     candidate whose only flagged dimension is one already well-represented in the
     packet (e.g. the very common treatment_hedging) scores lower than a candidate
     hitting a dimension barely seen yet (e.g. comorbidity_emphasis, sdoh_generation).
     This spreads the 29 "high signal" picks across the full dimension set instead of
     letting the 1-2 loosest regexes dominate.

Run from the EquityGUIDE repo root:
    venv/bin/python scripts/nsclc/build_rubric_discovery_packet.py
"""
from __future__ import annotations

import csv
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # scripts/nsclc/<this file> -> repo root
sys.path.insert(0, str(ROOT))

from src.analyze.soft_bias import DIMENSIONS as SOFT_DIMS, detect_all  # noqa: E402

# Excluded from selection scoring -- see module docstring. Still shown in the output
# columns, just not used to decide what gets picked.
NOISY_DIMS = {"clinical_trial"}
RANKING_DIMS = [d.key for d in SOFT_DIMS if d.key not in NOISY_DIMS]


def _flagged_lines(text: str) -> list[str]:
    """Same extraction used in build_contrastive_packet.py: the exact line(s) that
    tripped each soft-bias dimension, tagged by dimension key."""
    if not text:
        return []
    out, seen = [], set()
    for d in SOFT_DIMS:
        for m in d.pattern.finditer(text):
            ls = text.rfind("\n", 0, m.start()) + 1
            le = text.find("\n", m.start())
            line = text[ls:(le if le != -1 else len(text))].strip()
            key = (d.key, line)
            if line and key not in seen:
                seen.add(key)
                out.append(f"[{d.key}] {line}")
    return out

ARMS = {
    "gemini-2.5-flash": "results/baseline/v2_genie_bpc_nsclc_checkpoint.json",
    "deepseek-chat": "results/baseline/v2_genie_bpc_nsclc_deepseek-chat_checkpoint.json",
    "llama-3.3-70B": "results/baseline/v2_genie_bpc_nsclc_meta-llama-Llama-3.3-70B-Instruct-Turbo_checkpoint.json",
    "llama-3.1-8B": "results/baseline/v2_genie_bpc_nsclc_openrouter-meta-llama-llama-3.1-8b-instruct_checkpoint.json",
    "gpt-4o": "results/baseline/v2_genie_bpc_nsclc_gpt-4o_checkpoint.json",
    "gpt-4o-mini": "results/baseline/v2_genie_bpc_nsclc_gpt-4o-mini_checkpoint.json",
}

VARIANTS = [
    "black_female_medicaid", "black_female_private", "latina_female_uninsured",
    "white_female_medicaid", "white_male_private", "medicaid_only",
    "medicare_advantage_only", "medicare_only", "underinsured_only", "uninsured_only",
    "asian_race_only", "black_race_only", "hispanic_race_only", "middle_eastern_race_only",
    "multiracial_race_only", "native_american_race_only", "rural_patient",
    "small_community_hospital", "immigrant_patient",
    "limited_english_patient", "high_income_patient", "low_income_patient",
    "unhoused_patient", "black_unhoused", "low_income_black", "gay_male_patient",
    "non_binary_patient", "transgender_woman",
]

EXCLUSION_SOURCES = [
    "adjudication/contrastive_packet_60.jsonl",
    "adjudication/flagged_judge_items.jsonl",
    "adjudication/random_judge_items.jsonl",
    "adjudication/judge_items.jsonl",
    "adjudication/judge_bias_probe_items.jsonl",
]


def load_exclusions() -> set[tuple[str, str]]:
    seen = set()
    # contrastive packet uses base_case_id / demographic_variant
    with open("adjudication/contrastive_packet_60.jsonl") as f:
        for line in f:
            d = json.loads(line)
            seen.add((d.get("base_case_id"), d.get("demographic_variant")))
    # judge item pools use case_id / _variant
    for path in EXCLUSION_SOURCES[1:]:
        p = Path(path)
        if not p.exists():
            continue
        with open(p) as f:
            for line in f:
                d = json.loads(line)
                seen.add((d.get("case_id"), d.get("_variant")))
    return seen


def main():
    random.seed(20260807)
    print("Loading exclusion set from existing packets...")
    excluded = load_exclusions()
    print(f"  {len(excluded)} (case_id, variant) pairs already used elsewhere -- will skip these.")

    print("Loading 6 model checkpoints (this takes a bit, files are large)...")
    checkpoints = {}
    for model, path in ARMS.items():
        print(f"  {model} <- {path}")
        with open(path) as f:
            checkpoints[model] = json.load(f)

    model_order = list(ARMS.keys())
    dim_pick_counts = {d: 0 for d in RANKING_DIMS}  # how often each dim has driven a pick so far
    rows = []
    row_id = 0
    for v_idx, variant in enumerate(VARIANTS):
        candidates = []  # (model, case_id, ranking_dims, all_dims, variant_text, ref_text, nccn_label)
        PER_MODEL_CAP = 12  # cap per model so the pool doesn't fill from one vendor
        for model, ckpt in checkpoints.items():
            case_ids = list(ckpt.keys())
            random.shuffle(case_ids)
            n_from_this_model = 0
            for case_id in case_ids:
                if n_from_this_model >= PER_MODEL_CAP:
                    break
                case = ckpt.get(case_id, {})
                if variant not in case or "no_demographics" not in case:
                    continue
                if (case_id, variant) in excluded:
                    continue
                variant_entry = case[variant]
                ref_entry = case["no_demographics"]
                v_text = variant_entry.get("response_text", "")
                r_text = ref_entry.get("response_text", "")
                if not v_text or not r_text:
                    continue
                flags = detect_all(v_text)
                all_dims = [k for k, v in flags.items() if v]
                ranking_dims = [d for d in all_dims if d not in NOISY_DIMS]
                candidates.append(
                    (model, case_id, ranking_dims, all_dims, v_text, r_text,
                     variant_entry.get("nccn_label", ""))
                )
                n_from_this_model += 1

        if not candidates:
            print(f"  WARNING: no fresh candidates found for variant={variant}")
            continue

        # Round-robin the model assigned to "high signal" across variants so all 6
        # vendors get roughly equal representation, instead of letting a global max
        # always favor whichever model has the highest average stigma rate.
        high_model = model_order[v_idx % len(model_order)]
        low_model = model_order[(v_idx + 3) % len(model_order)]  # offset by half the roster

        high_pool = [c for c in candidates if c[0] == high_model]
        if not high_pool:
            high_pool = candidates  # fall back if this model had no fresh candidate here

        # Novelty-weighted score: reward candidates whose ranking dims are still
        # under-represented among picks so far, instead of just raw dim count. A
        # candidate with zero ranking dims always scores 0, so it can't win "high".
        def novelty_score(c):
            ranking_dims = c[2]
            return sum(1.0 / (1 + dim_pick_counts[d]) for d in ranking_dims)

        high_pool = [c for c in high_pool if c[2]]  # must have >=1 non-noisy dim to be "high"
        if not high_pool:
            # this model had no candidate with any real signal for this variant --
            # fall back to the full candidate pool so the variant isn't skipped
            high_pool = [c for c in candidates if c[2]] or candidates
        high_pool.sort(key=novelty_score, reverse=True)
        high = high_pool[0]
        for d in high[2]:
            dim_pick_counts[d] += 1

        low_pool = [c for c in candidates if c[0] == low_model and c[1] != high[1]]
        if not low_pool:
            low_pool = [c for c in candidates if c[1] != high[1]]
        low_pool.sort(key=lambda c: len(c[2]))  # fewest non-noisy dims = cleanest baseline
        low = low_pool[0] if low_pool else None

        for label, item in (("high_signal", high), ("low_signal", low)):
            if item is None:
                continue
            model, case_id, ranking_dims, dims, v_text, r_text, nccn_label = item
            n_dims = len(dims)
            row_id += 1
            rows.append({
                "id": f"rd{row_id:04d}",
                "sampling_bucket": label,
                "variant": variant,
                "model": model,
                "case_id": case_id,
                "nccn_label": nccn_label,
                "n_classifier_dims_flagged": n_dims,
                "classifier_dims_flagged": ", ".join(dims),
                "flagged_lines": "  |  ".join(_flagged_lines(v_text)),
                "reference_response_no_demographics": r_text,
                "variant_response": v_text,
                "your_bias_type_notes": "",
            })
            excluded.add((case_id, variant))  # don't reuse this case+variant again

    out_path = "adjudication/rubric_discovery_packet.csv"
    fieldnames = list(rows[0].keys())
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"\nWrote {len(rows)} rows ({len(rows)//2} variants covered, high+low signal each)")
    print(f"  -> {out_path}")


if __name__ == "__main__":
    main()
