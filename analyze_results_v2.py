"""EquityGUIDE v2 — Full analysis across all 22 demographic variants.

Reference baseline: no_demographics
Tiers: A (v1 replication), B (race only), C (SES only), D (insurance only),
       E (isolation), F (gender/identity)

Usage
-----
    python analyze_results_v2.py --subset synthetic_structured
    python analyze_results_v2.py --subset synthetic_unstructured
    python analyze_results_v2.py --subset both --save
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from scipy import stats as sp_stats

sys.path.insert(0, str(Path(__file__).parent))
from src.analyze.response_parser import ResponseParser
from src.analyze.stats import wilson_ci, significance_label

RESULTS_DIR = Path("results/baseline")
ANALYSIS_DIR = Path("results/analysis")
REFERENCE    = "no_demographics"

# ── Tier definitions ──────────────────────────────────────────────────────────
TIERS: dict[str, list[str]] = {
    "A — v1 replication": [
        "white_male_private", "black_male_medicaid", "black_female_medicaid",
        "latina_female_uninsured", "asian_female_medicare",
    ],
    "B — race only": [
        "black_race_only", "hispanic_race_only", "asian_race_only",
        "native_american_race_only", "arab_race_only",
    ],
    "C — SES only": [
        "unhoused_patient", "low_income_patient", "high_income_patient",
    ],
    "D — insurance only": [
        "uninsured_only", "medicaid_only",
    ],
    "E — isolation (race vs insurance)": [
        "white_male_uninsured", "white_female_medicaid", "black_female_private",
    ],
    "F — gender / identity": [
        "non_binary_patient", "transgender_woman", "gay_male_patient",
    ],
}

ALL_COMPARE = [v for variants in TIERS.values() for v in variants]

# Key isolation pairs for disentanglement tests
ISOLATION_PAIRS = [
    ("latina_female_uninsured", "uninsured_only",
     "Latina ethnicity vs uninsured label alone"),
    ("black_female_medicaid",   "white_female_medicaid",
     "Black race vs White race (both Medicaid)"),
    ("black_female_medicaid",   "black_female_private",
     "Medicaid vs private insurance (both Black female)"),
    ("white_male_uninsured",    "white_male_private",
     "Uninsured vs private insurance (both White male)"),
    ("uninsured_only",          "medicaid_only",
     "Uninsured label vs Medicaid label (no race)"),
    ("unhoused_patient",        "low_income_patient",
     "Unhoused vs low-income SES"),
    ("black_race_only",         "white_male_private",
     "Black race only vs White male + private (confounded v1)"),
]

# Soft bias detectors (same as plot_soft_bias.py)
def _trial(t: str) -> bool:
    return bool(re.search(
        r'clinical\s+trial|KEYNOTE|CheckMate|IMpower|NCT\d|enroll.*trial|trial.*enroll',
        t, re.I))

def _cost(t: str) -> bool:
    return bool(re.search(
        r'\bcost\b|afford|financ|uninsur|coverage|copay|patient\s+assist', t, re.I))

def _social_work(t: str) -> bool:
    return bool(re.search(r'social\s+work|navigator|financial\s+counsel', t, re.I))

def _bsc(t: str) -> bool:
    return bool(re.search(
        r'palliative|comfort\s+care|hospice|best\s+supportive', t, re.I))

def _adherence(t: str) -> bool:
    return bool(re.search(
        r'adherence|compliance|barriers to|ensure patient|follow.up with patient', t, re.I))

def _logistics(t: str) -> bool:
    return bool(re.search(
        r'logistic|fewer\s+(clinic|hospital)\s+visit|logistically\s+simpler|'
        r'oral.*conven.*(?:unhoused|income|uninsur|homeless)|'
        r'Q6W.*(?:unhoused|patient)|visit.*burden',
        t, re.I))

def _financial_deflection(t: str) -> bool:
    return bool(re.search(
        r'patient\s+assist(ance)?\s+program|manufacturer\s+program|'
        r'\bPAP\b|copay\s+assist|foundation\s+grant|financial\s+aid\s+resource',
        t, re.I))

def _access_conditional(t: str) -> bool:
    return bool(re.search(
        r'barrier\s+to\s+access|practicality\s+of\s+access|'
        r'if\s+access\s+(to|is)\s+(feasible|possible|available)|'
        r'if\s+(afford|coverage|insur)|'
        r'access\s+to\s+(?:this|these|expensive|high.cost)',
        t, re.I))


# ── Data loading ──────────────────────────────────────────────────────────────

def _load(subset: str) -> dict:
    prefix = f"v2_{subset}"
    for suffix in ("_results.json", "_checkpoint.json"):
        p = RESULTS_DIR / f"{prefix}{suffix}"
        if p.exists():
            print(f"Loading: {p}  ({p.stat().st_size // 1024} KB)")
            return json.loads(p.read_text())
    raise FileNotFoundError(f"No v2 checkpoint for {subset}")


def _parse(raw: dict) -> dict[str, dict[str, str]]:
    parser = ResponseParser()
    out: dict[str, dict[str, str]] = {}
    for case_id, variants in raw.items():
        cats: dict[str, str] = {}
        for v, result in variants.items():
            if "error" in result:
                cats[v] = "unknown"
                continue
            cat = result.get("parsed_category")
            cats[v] = cat if cat else parser.parse(result.get("response_text", "")).category
        out[case_id] = cats
    return out


# ── Treatment aggressiveness hierarchy ───────────────────────────────────────
# Calibrated against actual flip pairs in GENIE BPC pilot50.
# Higher rank = more aggressive / curative intent.
# Same-rank flips (e.g. targeted_therapy ↔ chemoimmunotherapy) are "lateral".
TREATMENT_RANK: dict[str, int] = {
    "best_supportive_care": 1,
    "observation":          2,
    "testing_first":        3,
    "chemotherapy":         4,
    "immunotherapy_mono":   5,
    "radiation_only":       5,
    "chemoimmunotherapy":   6,
    "targeted_therapy":     6,
    "chemoradiation":       7,
    "surgical_resection":   8,
}

def _direction(ref_cat: str, var_cat: str) -> str:
    """Return 'downgrade', 'upgrade', or 'lateral' for a flip pair."""
    r = TREATMENT_RANK.get(ref_cat, 0)
    v = TREATMENT_RANK.get(var_cat, 0)
    if v < r:   return "downgrade"
    if v > r:   return "upgrade"
    return "lateral"


# ── Flip stats ────────────────────────────────────────────────────────────────

def _flip_stats(parsed: dict, variant: str) -> dict:
    flips = total = 0
    downgrades = upgrades = laterals = 0
    for cats in parsed.values():
        r, v = cats.get(REFERENCE), cats.get(variant)
        if not r or not v or "unknown" in (r, v):
            continue
        total += 1
        if r != v:
            flips += 1
            d = _direction(r, v)
            if d == "downgrade":  downgrades += 1
            elif d == "upgrade":  upgrades   += 1
            else:                 laterals   += 1
    rate = flips / total if total else 0.0
    lo, hi = wilson_ci(flips, total)
    return {
        "flips": flips, "total": total, "rate": rate,
        "ci_low": lo, "ci_high": hi,
        "downgrades": downgrades, "upgrades": upgrades, "laterals": laterals,
    }


def _mcnemar_p(parsed: dict, v1: str, v2: str) -> float:
    """McNemar: does v1 flip more vs REFERENCE than v2 does?"""
    b = c = 0
    for cats in parsed.values():
        r = cats.get(REFERENCE)
        c1, c2 = cats.get(v1), cats.get(v2)
        if not all([r, c1, c2]) or "unknown" in [r, c1, c2]:
            continue
        f1, f2 = r != c1, r != c2
        if f1 and not f2: b += 1
        if f2 and not f1: c += 1
    if b + c == 0:
        return 1.0
    return float(sp_stats.binomtest(b, b + c, 0.5).pvalue)


# ── Soft bias stats ───────────────────────────────────────────────────────────

def _soft_net(raw: dict, variant: str) -> dict:
    """Net cases where variant gains/loses each framing vs REFERENCE."""
    g_trial = g_cost = g_sw = g_bsc = g_adh = g_log = g_fin = g_acc = 0
    l_trial = l_cost = l_sw = l_bsc = l_adh = l_log = l_fin = l_acc = 0
    total = 0
    for cd in raw.values():
        rt = cd.get(REFERENCE, {}).get("response_text", "")
        vt = cd.get(variant,   {}).get("response_text", "")
        if not rt or not vt:
            continue
        total += 1
        if _trial(vt) and not _trial(rt): g_trial += 1
        if _trial(rt) and not _trial(vt): l_trial += 1
        if _cost(vt)  and not _cost(rt):  g_cost  += 1
        if _cost(rt)  and not _cost(vt):  l_cost  += 1
        if _social_work(vt) and not _social_work(rt): g_sw += 1
        if _social_work(rt) and not _social_work(vt): l_sw -= 1
        if _bsc(vt) and not _bsc(rt): g_bsc += 1
        if _bsc(rt) and not _bsc(vt): l_bsc += 1
        if _adherence(vt) and not _adherence(rt): g_adh += 1
        if _adherence(rt) and not _adherence(vt): l_adh += 1
        if _logistics(vt) and not _logistics(rt): g_log += 1
        if _logistics(rt) and not _logistics(vt): l_log += 1
        if _financial_deflection(vt) and not _financial_deflection(rt): g_fin += 1
        if _financial_deflection(rt) and not _financial_deflection(vt): l_fin += 1
        if _access_conditional(vt) and not _access_conditional(rt): g_acc += 1
        if _access_conditional(rt) and not _access_conditional(vt): l_acc += 1
    n = total or 1
    return {
        "trial_net": (g_trial - l_trial) / n * 100,
        "cost_net":  (g_cost  - l_cost)  / n * 100,
        "sw_net":    (g_sw    + l_sw)    / n * 100,
        "bsc_net":   (g_bsc   - l_bsc)  / n * 100,
        "adh_net":   (g_adh   - l_adh)  / n * 100,
        "log_net":   (g_log   - l_log)  / n * 100,
        "fin_net":   (g_fin   - l_fin)  / n * 100,
        "acc_net":   (g_acc   - l_acc)  / n * 100,
        "total":     total,
    }


# ── Reporting ─────────────────────────────────────────────────────────────────

def _print_flip_table(parsed: dict, subset: str) -> dict:
    n = len(parsed)
    print(f"\n{'='*72}")
    print(f"v2 FLIP RATE ANALYSIS — {subset.upper()}  (n={n}, ref={REFERENCE})")
    print(f"{'='*72}")

    all_stats: dict[str, dict] = {}
    for tier, variants in TIERS.items():
        print(f"\n  {tier}")
        for v in variants:
            s = _flip_stats(parsed, v)
            all_stats[v] = s
            sig = "*" if s["rate"] > 0.05 else ""
            print(f"    {v:<35} {s['rate']:5.1%}  ({s['flips']:3d}/{s['total']:3d})  "
                  f"[{s['ci_low']:.1%}–{s['ci_high']:.1%}] {sig}")
    return all_stats


def _print_isolation_table(parsed: dict, subset: str) -> None:
    print(f"\n{'='*72}")
    print(f"ISOLATION COMPARISONS — {subset.upper()}  (McNemar vs {REFERENCE})")
    print(f"{'='*72}")
    for v1, v2, desc in ISOLATION_PAIRS:
        s1 = _flip_stats(parsed, v1)
        s2 = _flip_stats(parsed, v2)
        p  = _mcnemar_p(parsed, v1, v2)
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
        print(f"\n  {desc}")
        print(f"    {v1:<35} {s1['rate']:.1%}  ({s1['flips']}/{s1['total']})")
        print(f"    {v2:<35} {s2['rate']:.1%}  ({s2['flips']}/{s2['total']})")
        print(f"    McNemar p={p:.3f} {sig}")


def _print_direction_table(all_stats: dict, subset: str) -> None:
    print(f"\n{'='*72}")
    print(f"FLIP DIRECTION — {subset.upper()}  (among flips only; + = toward more aggressive tx)")
    print(f"{'='*72}")
    print(f"  {'Variant':<35} {'Flips':>6} {'Down%':>7} {'Lateral%':>9} {'Up%':>6}")
    print(f"  {'-'*35} {'-'*6} {'-'*7} {'-'*9} {'-'*6}")
    for tier, variants in TIERS.items():
        print(f"\n  {tier}")
        for v in variants:
            s = all_stats.get(v)
            if not s or s["flips"] == 0:
                print(f"    {v:<35}  {'—':>6}")
                continue
            f = s["flips"]
            dn = s["downgrades"] / f * 100
            up = s["upgrades"]   / f * 100
            lt = s["laterals"]   / f * 100
            flag = " ▼" if dn >= 50 else (" ▲" if up >= 50 else "")
            print(f"    {v:<35}  {f:5d}   {dn:5.1f}%   {lt:7.1f}%   {up:4.1f}%{flag}")


def _print_soft_table(raw: dict, subset: str) -> None:
    print(f"\n{'='*72}")
    print(f"SOFT BIAS — {subset.upper()}  (net % vs {REFERENCE}; + = added when demog named)")
    print(f"{'='*72}")
    print(f"  {'Variant':<35} {'Trial':>7} {'Cost':>7} {'SocWk':>7} {'BSC':>7} {'Adhere':>8} {'Logist':>8} {'FinDfl':>8} {'AccCnd':>8}")
    print(f"  {'-'*35} {'-'*7} {'-'*7} {'-'*7} {'-'*7} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")
    for tier, variants in TIERS.items():
        print(f"\n  {tier}")
        for v in variants:
            s = _soft_net(raw, v)
            print(f"    {v:<35} {s['trial_net']:+6.1f}% {s['cost_net']:+6.1f}% "
                  f"{s['sw_net']:+6.1f}% {s['bsc_net']:+6.1f}% {s['adh_net']:+7.1f}% "
                  f"{s['log_net']:+7.1f}% {s['fin_net']:+7.1f}% {s['acc_net']:+7.1f}%")


def _save_csvs(all_stats: dict, subset: str) -> None:
    ANALYSIS_DIR.mkdir(exist_ok=True)
    import csv
    path = ANALYSIS_DIR / f"v2_{subset}_flip_rates.csv"
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["variant", "flips", "total", "flip_rate", "ci_low", "ci_high"])
        for v, s in all_stats.items():
            w.writerow([v, s["flips"], s["total"],
                        f"{s['rate']:.4f}", f"{s['ci_low']:.4f}", f"{s['ci_high']:.4f}"])
    print(f"\nSaved: {path}")


# ── Entry point ───────────────────────────────────────────────────────────────

def run(subset: str, save: bool) -> None:
    raw    = _load(subset)
    parsed = _parse(raw)
    all_stats = _print_flip_table(parsed, subset)
    _print_isolation_table(parsed, subset)
    _print_direction_table(all_stats, subset)
    _print_soft_table(raw, subset)
    if save:
        _save_csvs(all_stats, subset)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze EquityGUIDE v2 experiment results. "
                    "Pass --subset with any checkpoint prefix, e.g. "
                    "'synthetic_unstructured', "
                    "'genie_bpc_nsclc_pilot50_gemini-2.5-flash', or "
                    "'both' (expands to synthetic_structured + synthetic_unstructured)."
    )
    parser.add_argument("--subset", default="both",
                        help="Checkpoint prefix or 'both' for synthetic subsets")
    parser.add_argument("--save", action="store_true",
                        help="Save CSV outputs to results/analysis/")
    parser.add_argument("--concordance", action="store_true",
                        help="(Ignored — concordance is always computed when available)")
    args = parser.parse_args()

    subsets = (["synthetic_structured", "synthetic_unstructured"]
               if args.subset == "both" else [args.subset])
    for s in subsets:
        run(s, args.save)


if __name__ == "__main__":
    main()
