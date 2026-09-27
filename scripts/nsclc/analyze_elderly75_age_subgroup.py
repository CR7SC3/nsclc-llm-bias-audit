"""elderly_patient_75 age-consistent subgroup re-analysis (Paper 1 NSCLC).

Council finding: elderly_patient_75 only appends an "Age context: elderly
(75+ years old)" label; it never overwrites the real GENIE age_dx baked into
the note (structured "Age at Diagnosis" line, and ~100% of the Gemini-authored
unstructured narrative). 889/1,048 cases (84.8%) have a real age under 75, so
the published flip-rate/Cohen's-d for this variant (Table 2: 17.4%, d=0.054)
is computed mostly on internally self-contradictory notes (label says 75+,
narrative says e.g. 42).

This script re-filters the ALREADY-COLLECTED responses to the subset of cases
whose real age_dx is already >=70 (and, separately, >=75) -- where label and
narrative agree -- and reports flip rate / soft-intensity Cohen's d /
adherence (concordance) delta for that subgroup, using the exact same
functions (_flip_stats, _continuous_stats) and 6-model average as Table 2 and
Supplementary Table S3. No new LLM calls.

Run:  venv/bin/python scripts/nsclc/analyze_elderly75_age_subgroup.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from analyze_results_v2 import _flip_stats, _parse, _continuous_stats  # noqa: E402

RESULTS_DIR = Path("results/baseline")
ANALYSIS_DIR = Path("results/analysis")
NOTES_PATH = Path("data/processed/genie_bpc_nsclc_with_notes.json")
VARIANT = "elderly_patient_75"
REFERENCE = "no_demographics"

MODELS = ["gemini-2.5-flash", "deepseek-chat", "llama-3.3-70B",
          "llama-3.1-8B", "gpt-4o", "gpt-4o-mini"]
SUF = {"gemini-2.5-flash": "", "deepseek-chat": "_deepseek-chat",
       "llama-3.3-70B": "_meta-llama-Llama-3.3-70B-Instruct-Turbo",
       "llama-3.1-8B": "_openrouter-meta-llama-llama-3.1-8b-instruct",
       "gpt-4o": "_gpt-4o", "gpt-4o-mini": "_gpt-4o-mini"}

PUBLISHED_FLIP_PCT = 17.4
PUBLISHED_D = 0.054


def _age_subset(min_age: int) -> set[str]:
    records = json.loads(NOTES_PATH.read_text())
    return {r["case_id"] for r in records if int(r["age_dx"]) >= min_age}


def _load(model: str) -> dict:
    path = RESULTS_DIR / f"v2_genie_bpc_nsclc{SUF[model]}_results.json"
    print(f"  loading {path.name} ({path.stat().st_size // 1024 // 1024} MB)...")
    return json.loads(path.read_text())


def _stats_for_subset(raw: dict, subset_ids: set[str]) -> dict:
    raw_sub = {cid: variants for cid, variants in raw.items() if cid in subset_ids}
    parsed_sub = _parse(raw_sub)
    fstats = _flip_stats(parsed_sub, VARIANT)
    cstats_soft = _continuous_stats(raw_sub, "soft").get(VARIANT, {})
    cstats_adher = _continuous_stats(raw_sub, "adher").get(VARIANT, {})
    return {
        "flip_pct": fstats["rate"] * 100, "flips": fstats["flips"], "total": fstats["total"],
        "soft_d": cstats_soft.get("cohens_d"), "adher_delta": cstats_adher.get("delta"),
    }


def _summarize(per_model: list[dict], label: str, n_cases: int) -> None:
    print(f"\n{'='*72}")
    print(f"elderly_patient_75 SUBGROUP RE-ANALYSIS — {label} (n_cases={n_cases})")
    print(f"{'='*72}")
    for model, s in zip(MODELS, per_model):
        d = s["soft_d"]
        ad = s["adher_delta"]
        print(f"  {model:<14} flip={s['flip_pct']:5.1f}% ({s['flips']:3d}/{s['total']:3d})  "
              f"soft_d={d if d is not None else float('nan'):+.3f}  "
              f"adher_delta={ad if ad is not None else float('nan'):+.3f}")

    flip_rates = [s["flip_pct"] for s in per_model]
    ds = [s["soft_d"] for s in per_model if s["soft_d"] is not None]
    adher_deltas = [s["adher_delta"] for s in per_model if s["adher_delta"] is not None]
    ns = [s["total"] for s in per_model]

    mean_flip = sum(flip_rates) / len(flip_rates)
    mean_d = sum(ds) / len(ds) if ds else float("nan")
    mean_adher = sum(adher_deltas) / len(adher_deltas) if adher_deltas else float("nan")
    mean_n = sum(ns) / len(ns)

    print(f"\n  6-model average: flip={mean_flip:.1f}%  soft_d={mean_d:+.3f}  "
          f"adher_delta={mean_adher:+.3f}  (mean paired n={mean_n:.0f})")
    print(f"  Full-cohort published (Table 2): flip={PUBLISHED_FLIP_PCT:.1f}%  d={PUBLISHED_D:+.3f}")
    print(f"  Delta vs published: flip {mean_flip - PUBLISHED_FLIP_PCT:+.1f}pp  "
          f"d {mean_d - PUBLISHED_D:+.3f}")


def main() -> None:
    subset_70 = _age_subset(70)
    subset_75 = _age_subset(75)
    print(f"Cases with real age_dx >= 70: {len(subset_70)}/1048")
    print(f"Cases with real age_dx >= 75: {len(subset_75)}/1048")

    per_model_70, per_model_75 = [], []
    for model in MODELS:
        raw = _load(model)
        per_model_70.append(_stats_for_subset(raw, subset_70))
        per_model_75.append(_stats_for_subset(raw, subset_75))
        del raw

    _summarize(per_model_70, "real age_dx >= 70", len(subset_70))
    _summarize(per_model_75, "real age_dx >= 75 (exact label match)", len(subset_75))


if __name__ == "__main__":
    main()
