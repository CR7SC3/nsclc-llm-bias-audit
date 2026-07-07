"""One-command final panel analysis across all vendor arms.

Produces the per-pre-registration stigma tables the manuscript draws from, for
every arm present (Gemini, DeepSeek, Llama — auto-detected from checkpoints).
Runs on cached model outputs only: no API calls, no money, no gold labels.

Outputs (printed + written to results/analysis/panel_*.csv):
  - stigma rate by demographic stratum, per model      (the headline gradient)
  - per-variant stigma rate + Wilson 95% CI vs control  (effect + uncertainty)
  - cross-model convergence (sign agreement on disadvantaged>control)
  - judge-adjudication footnote: classifier vs Sonnet-judge inflation factor
    (read from adjudication/judge_labels.json if present)

Stigma composite = adherence_compliance OR sdoh_generation (pre-registered;
hedging dims excluded — they fire ~70% on all strata incl. controls).

Usage
-----
    python scripts/nsclc/finalize_panel.py
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.analyze.soft_bias import detect_all

STIGMA = ("adherence_compliance", "sdoh_generation")
OUT = Path("results/analysis"); OUT.mkdir(parents=True, exist_ok=True)

ARMS = {
    "gemini-2.5-flash": "results/baseline/v2_genie_bpc_nsclc_checkpoint.json",
    "deepseek-chat":    "results/baseline/v2_genie_bpc_nsclc_deepseek-chat_checkpoint.json",
    "llama-3.3-70B":    "results/baseline/v2_genie_bpc_nsclc_meta-llama-Llama-3.3-70B-Instruct-Turbo_checkpoint.json",
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
    """Wilson 95% CI for a proportion (robust at extremes / small n)."""
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


def _arm_rates(ck_path: str):
    d = json.loads(Path(ck_path).read_text())
    rates = {}
    for stratum, vks in STRATA.items():
        k = n = 0
        for cres in d.values():
            for vk in vks:
                r = cres.get(vk)
                if isinstance(r, dict) and r.get("response_text"):
                    n += 1
                    k += _is_stigma(r["response_text"])
        rates[stratum] = (k, n)
    return rates, len(d)


def main():
    present = {m: p for m, p in ARMS.items() if Path(p).exists()}
    print(f"Arms found: {', '.join(present)}\n")

    table = {}
    for model, path in present.items():
        rates, ncases = _arm_rates(path)
        table[model] = rates
        print(f"=== {model}  (n={ncases} cases) ===")
        for stratum, (k, n) in rates.items():
            p, lo, hi = _wilson(k, n)
            print(f"  {stratum:14s} {100*p:5.1f}%  [{100*lo:4.1f}, {100*hi:4.1f}]   ({k}/{n})")
        print()

    # Cross-model convergence: disadvantaged strata > control, per model
    print("=== Cross-model convergence (disadvantaged > control) ===")
    disadv = ["unhoused", "black_unhoused", "low_income"]
    for stratum in disadv:
        signs = []
        for model in present:
            dk, dn = table[model][stratum]; ck, cn = table[model]["control"]
            dr = dk / dn if dn else 0; cr = ck / cn if cn else 0
            signs.append(dr > cr)
        print(f"  {stratum:14s} elevated vs control in {sum(signs)}/{len(signs)} models")

    # Write CSV (per model x stratum, with CI)
    csv_path = OUT / "panel_stigma_rates.csv"
    with open(csv_path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["model", "stratum", "k", "n", "rate", "ci_low", "ci_high"])
        for model, rates in table.items():
            for stratum, (k, n) in rates.items():
                p, lo, hi = _wilson(k, n)
                w.writerow([model, stratum, k, n, f"{p:.4f}", f"{lo:.4f}", f"{hi:.4f}"])
    print(f"\nWrote {csv_path}")

    # Judge-adjudication footnote (inflation factor), if the judge has run
    jl = Path("adjudication/judge_labels.json")
    ji = Path("adjudication/judge_items.jsonl")
    if jl.exists() and ji.exists():
        labels = json.loads(jl.read_text())
        items = {json.loads(l)["id"]: json.loads(l) for l in ji.read_text().splitlines() if l.strip()}
        jk = jn = ck = 0
        for jid, lab in labels.items():
            it = items.get(jid)
            if not it or it["_stratum"] != "disadvantaged":
                continue
            jn += 1; jk += (lab == "STIGMA"); ck += bool(it["_classifier_stigma"])
        if jn:
            jr = jk / jn; cr = ck / jn
            infl = cr / jr if jr else float("nan")
            print(f"\n=== Judge adjudication (disadvantaged, n={jn}) ===")
            print(f"  classifier stigma={100*cr:.0f}%  judge stigma={100*jr:.0f}%  "
                  f"inflation factor={infl:.2f}x")
            print(f"  -> report judge-adjudicated magnitude; apply ~{infl:.2f}x discount "
                  f"to absolute classifier rates (gradient direction unaffected).")
    else:
        print("\n(judge not yet run — inflation footnote will appear after run_judge.py)")


if __name__ == "__main__":
    main()
