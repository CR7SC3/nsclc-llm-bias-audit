"""Case-clustered bootstrap CIs for the per-stratum stigma rates.

Companion to finalize_panel.py. The panel CSV reports Wilson intervals on
*pooled response counts*: for multi-variant strata (race_only = 6 variants,
control = 2 variants) that treats a case's several variant responses as
independent, understating uncertainty in this repeated-measures design.

This script recomputes each stratum's stigma rate with a bootstrap that
resamples the *case* (not the response) — the actual unit of independence —
so within-case correlation is respected. For single-variant strata (unhoused,
low_income, ...) each case contributes one response, so the clustered CI
essentially reproduces Wilson; for race_only/control it correctly widens.

Stigma composite = adherence_compliance OR sdoh_generation (pre-registered),
identical to finalize_panel.py. Runs on cached checkpoints only: no API calls.

Usage
-----
    python scripts/nsclc/bootstrap_panel_ci.py
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import numpy as np
from src.analyze.soft_bias import detect_all

STIGMA = ("adherence_compliance", "sdoh_generation")
OUT = Path("results/analysis"); OUT.mkdir(parents=True, exist_ok=True)
N_BOOT = 10000
SEED = 20260715

# identical arm map + strata to finalize_panel.py (kept in sync deliberately)
ARMS = {
    "gemini-2.5-flash": "results/baseline/v2_genie_bpc_nsclc_checkpoint.json",
    "deepseek-chat":    "results/baseline/v2_genie_bpc_nsclc_deepseek-chat_checkpoint.json",
    "llama-3.3-70B":    "results/baseline/v2_genie_bpc_nsclc_meta-llama-Llama-3.3-70B-Instruct-Turbo_checkpoint.json",
    "llama-3.1-8B":     "results/baseline/v2_genie_bpc_nsclc_openrouter-meta-llama-llama-3.1-8b-instruct_checkpoint.json",
    "gpt-4o":           "results/baseline/v2_genie_bpc_nsclc_gpt-4o_checkpoint.json",
    "gpt-4o-mini":      "results/baseline/v2_genie_bpc_nsclc_gpt-4o-mini_checkpoint.json",
}

STRATA = {
    "unhoused":       ["unhoused_patient"],
    "black_unhoused": ["black_unhoused"],
    "low_income":     ["low_income_patient"],
    "underinsured":   ["underinsured_only"],
    "uninsured":      ["uninsured_only"],
    "race_only":      ["black_race_only", "hispanic_race_only", "asian_race_only",
                       "native_american_race_only", "middle_eastern_race_only", "multiracial_race_only"],
    "control":        ["white_male_private", "no_demographics"],
}


def _wilson(k: int, n: int, z: float = 1.96):
    if n == 0:
        return (0.0, 0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / d
    return p, max(0.0, centre - half), min(1.0, centre + half)


def _is_stigma(text: str) -> bool:
    d = detect_all(text)
    return any(d.get(s) for s in STIGMA)


def _case_matrices(ck_path: str):
    """For each stratum, a per-case (k_flags, n_responses) array over that
    stratum's variants. Cases are the rows; the bootstrap resamples rows."""
    d = json.loads(Path(ck_path).read_text())
    cases = list(d.values())
    mats = {}
    for stratum, vks in STRATA.items():
        k = np.zeros(len(cases), dtype=np.int32)  # stigma responses for this case
        n = np.zeros(len(cases), dtype=np.int32)  # scored responses for this case
        for i, cres in enumerate(cases):
            for vk in vks:
                r = cres.get(vk)
                if isinstance(r, dict) and r.get("response_text"):
                    n[i] += 1
                    k[i] += _is_stigma(r["response_text"])
        mats[stratum] = (k, n)
    return mats, len(cases)


def _cluster_ci(k: np.ndarray, n: np.ndarray, rng: np.random.Generator):
    """Case-clustered percentile bootstrap for pooled rate sum(k)/sum(n).

    Vectorized in row-chunks: each resample draws `ncases` cases with
    replacement and recomputes the pooled proportion over their responses."""
    ncases = len(k)
    rates = np.empty(N_BOOT)
    done = 0
    while done < N_BOOT:
        b = min(1000, N_BOOT - done)
        idx = rng.integers(0, ncases, size=(b, ncases))
        ksum = k[idx].sum(axis=1)
        nsum = n[idx].sum(axis=1)
        rates[done:done + b] = np.where(nsum > 0, ksum / np.maximum(nsum, 1), 0.0)
        done += b
    lo, hi = np.percentile(rates, [2.5, 97.5])
    return float(lo), float(hi)


def main():
    present = {m: p for m, p in ARMS.items() if Path(p).exists()}
    print(f"Arms found: {', '.join(present)}\n")
    rng = np.random.default_rng(SEED)

    rows = []
    for model, path in present.items():
        mats, ncases = _case_matrices(path)
        print(f"=== {model}  (n={ncases} cases) ===")
        print(f"  {'stratum':14s} {'rate':>6s}  {'clustered 95% CI':>18s}     {'Wilson 95% CI':>18s}")
        for stratum, (k, n) in mats.items():
            K, N = int(k.sum()), int(n.sum())
            p, wlo, whi = _wilson(K, N)
            clo, chi = _cluster_ci(k, n, rng)
            nvar = len(STRATA[stratum])
            flag = "  <-- pooled" if nvar > 1 else ""
            print(f"  {stratum:14s} {100*p:5.1f}%  [{100*clo:4.1f}, {100*chi:4.1f}]     "
                  f"[{100*wlo:4.1f}, {100*whi:4.1f}]{flag}")
            rows.append([model, stratum, K, N, f"{p:.4f}",
                         f"{clo:.4f}", f"{chi:.4f}", f"{wlo:.4f}", f"{whi:.4f}",
                         nvar, ncases])
        print()

    csv_path = OUT / "panel_stigma_rates_clustered.csv"
    with open(csv_path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["model", "stratum", "k", "n_responses", "rate",
                    "ci_low_clustered", "ci_high_clustered",
                    "ci_low_wilson", "ci_high_wilson", "n_variants", "n_cases"])
        w.writerows(rows)
    print(f"Wrote {csv_path}  ({N_BOOT} resamples, seed {SEED})")


if __name__ == "__main__":
    main()
