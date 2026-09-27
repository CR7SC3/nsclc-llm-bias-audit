"""Case-clustered permutation Cochran-Armitage trend test for the stigma gradient.

Reproduces the test described in manuscript_nsclc.md Supplementary Methods
("Statistical detail: care-intensity mixed model and trend-test permutation null"):
a Cochran-Armitage trend test per model across five ordered strata (control <
uninsured < underinsured < low income < unhoused), significance assessed by a
case-clustered permutation null (2,000 permutations per model), each permutation
independently reshuffling one case's own five stratum assignments so each case's
response set is preserved while any true trend is destroyed.

No such reproducible implementation existed in the repo prior to this script
(an adversarial review flagged this as MUST-FIX #8); this is a from-scratch,
from-first-principles implementation, not a patch to prior (unfound) code.

Usage: venv/bin/python scripts/nsclc/cochran_armitage_trend.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.analyze.soft_bias import detect_all

STIGMA_DIMS = ("adherence_compliance", "sdoh_generation")

ARMS = {
    "gemini-2.5-flash": "results/baseline/v2_genie_bpc_nsclc_checkpoint.json",
    "deepseek-chat":    "results/baseline/v2_genie_bpc_nsclc_deepseek-chat_checkpoint.json",
    "llama-3.3-70B":    "results/baseline/v2_genie_bpc_nsclc_meta-llama-Llama-3.3-70B-Instruct-Turbo_checkpoint.json",
    "llama-3.1-8B":     "results/baseline/v2_genie_bpc_nsclc_openrouter-meta-llama-llama-3.1-8b-instruct_checkpoint.json",
    "gpt-4o":           "results/baseline/v2_genie_bpc_nsclc_gpt-4o_checkpoint.json",
    "gpt-4o-mini":      "results/baseline/v2_genie_bpc_nsclc_gpt-4o-mini_checkpoint.json",
}

# Ordered strata, control first: scores 0..4
STRATA = ["no_demographics", "uninsured_only", "underinsured_only",
          "low_income_patient", "unhoused_patient"]
SCORES = np.arange(len(STRATA))

N_PERM = 2000
SEED = 17  # matches the gold-set seed used elsewhere in this project for consistency


def is_stigma(text: str) -> bool:
    if not text:
        return False
    hits = detect_all(text)
    return any(hits.get(d, False) for d in STIGMA_DIMS)


def ca_statistic(outcomes: np.ndarray, groups: np.ndarray) -> float:
    """Cochran-Armitage z-statistic. outcomes: 0/1 array. groups: 0..K-1 array."""
    K = len(STRATA)
    n = np.array([(groups == i).sum() for i in range(K)], dtype=float)
    k = np.array([outcomes[groups == i].sum() for i in range(K)], dtype=float)
    N = n.sum()
    p_bar = k.sum() / N
    s = SCORES.astype(float)
    T = np.sum(s * (k - n * p_bar))
    var = p_bar * (1 - p_bar) * (np.sum(n * s * s) - (np.sum(n * s) ** 2) / N)
    if var <= 0:
        return 0.0
    return T / np.sqrt(var)


def run_model(name: str, path: str) -> dict:
    raw = json.loads(Path(path).read_text())
    # Build per-case, per-stratum outcome; keep only cases with all 5 strata present.
    case_outcomes = []  # list of length-5 arrays (one per case, in STRATA order)
    for cid, variants in raw.items():
        row = []
        ok = True
        for v in STRATA:
            rec = variants.get(v)
            if rec is None:
                ok = False
                break
            row.append(1 if is_stigma(rec.get("response_text", "")) else 0)
        if ok:
            case_outcomes.append(row)
    case_outcomes = np.array(case_outcomes, dtype=int)  # (n_cases, 5)
    n_cases = case_outcomes.shape[0]

    outcomes_flat = case_outcomes.flatten()
    groups_flat = np.tile(np.arange(len(STRATA)), n_cases)
    z_obs = ca_statistic(outcomes_flat, groups_flat)

    rng = np.random.default_rng(SEED)
    z_null = np.empty(N_PERM)
    for i in range(N_PERM):
        # Permute each case's own 5 stratum labels independently (not swapping
        # across cases), destroying the trend while preserving each case's
        # response set exactly as the manuscript's protocol specifies.
        permuted = np.array([rng.permutation(row) for row in case_outcomes])
        z_null[i] = ca_statistic(permuted.flatten(), groups_flat)

    # Two-sided empirical p-value against the permutation null.
    p_perm = (np.sum(np.abs(z_null) >= abs(z_obs)) + 1) / (N_PERM + 1)
    rates = {v: case_outcomes[:, j].mean() for j, v in enumerate(STRATA)}
    return {"n_cases": n_cases, "z": z_obs, "p_perm": p_perm, "rates": rates}


def main() -> None:
    print(f"Case-clustered permutation Cochran-Armitage trend test "
          f"({N_PERM} permutations, seed={SEED})")
    print(f"Strata (scores 0-4): {STRATA}\n")
    for name, path in ARMS.items():
        if not Path(path).exists():
            print(f"  {name}: checkpoint not found ({path}), skipped")
            continue
        r = run_model(name, path)
        rate_str = "  ".join(f"{v.split('_')[0]}={r['rates'][v]*100:.1f}%" for v in STRATA)
        print(f"{name:18s} n={r['n_cases']:4d}  z={r['z']:+7.2f}  "
              f"p_perm={r['p_perm']:.4f}  {rate_str}")


if __name__ == "__main__":
    main()
