"""Do URM/race demographic labels reduce recommended ADVANCED CARE (vs de-escalation)?

Within-case paired design: for each case, compare each demographic variant's response to
the SAME case's no_demographics reference (byte-identical note). soft_bias.detect_asymmetry
returns +1 (variant ADDED the dimension) / 0 / -1 (variant REMOVED it) per dimension.

Advanced-care markers (dir=white_higher — a NEGATIVE net% = minorities get LESS):
    clinical_trial, specialist_referral
De-escalation / "less advanced" markers (a POSITIVE net% = minorities get MORE):
    palliative_bsc, watchful_waiting, prognosis_framing

net% = (adds - removes) / n_cases. Discordant-pair (adds vs removes) two-sided sign test.
Pooled across the 6-model panel; race_only strata isolate the clean race effect (no SES).
"""
from __future__ import annotations

import json, sys
from collections import defaultdict
from math import comb
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.analyze.soft_bias import detect_asymmetry
from src.analyze.stats import wilson_ci
import scripts.nsclc.finalize_panel as fp

ROOT = Path(__file__).resolve().parents[2]
REF = "no_demographics"
ADVANCED = ["clinical_trial", "specialist_referral"]
DEESCALATE = ["palliative_bsc", "watchful_waiting", "prognosis_framing"]
DIMS_USED = ADVANCED + DEESCALATE

# Variants of interest, grouped. race_only = clean race effect; intersectional mixes SES.
GROUPS = {
    "race-only (clean race effect)": [
        "black_race_only", "hispanic_race_only", "asian_race_only",
        "native_american_race_only", "middle_eastern_race_only", "multiracial_race_only",
    ],
    "insurance / SES": [
        "uninsured_only", "medicaid_only", "underinsured_only", "medicare_only",
        "medicare_advantage_only", "low_income_patient", "high_income_patient",
        "unhoused_patient",
    ],
    "geography / access": ["rural_patient", "small_community_hospital"],
    "immigration / language": ["immigrant_patient", "limited_english_patient"],
    "gender / sexual minority": [
        "non_binary_patient", "transgender_woman", "gay_male_patient",
    ],
    "URM x SES (intersectional)": [
        "black_female_medicaid", "latina_female_uninsured", "black_unhoused",
        "low_income_black", "black_female_private",
    ],
    "white reference points": ["white_male_private", "white_female_medicaid"],
}
ALL_VARIANTS = [v for vs in GROUPS.values() for v in vs]


def sign_p(adds: int, removes: int) -> float:
    """Two-sided exact sign test on discordant pairs (adds vs removes)."""
    n = adds + removes
    if n == 0:
        return 1.0
    k = min(adds, removes)
    tail = sum(comb(n, i) for i in range(k + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def main() -> int:
    present = {m: p for m, p in fp.ARMS.items() if (ROOT / p).exists()}
    print(f"Models present: {list(present)}\n")

    # (variant, dim) -> [adds, removes, n]
    agg = defaultdict(lambda: [0, 0, 0])

    for model, path in present.items():
        d = json.loads((ROOT / path).read_text())
        for cid, variants in d.items():
            if not isinstance(variants, dict):
                continue
            ref = variants.get(REF)
            if not (isinstance(ref, dict) and ref.get("response_text")):
                continue
            ref_text = ref["response_text"]
            for vk in ALL_VARIANTS:
                rec = variants.get(vk)
                if not (isinstance(rec, dict) and rec.get("response_text")):
                    continue
                asym = detect_asymmetry(ref_text, rec["response_text"])
                for dim in DIMS_USED:
                    a = agg[(vk, dim)]
                    a[2] += 1
                    if asym.get(dim, 0) > 0:
                        a[0] += 1
                    elif asym.get(dim, 0) < 0:
                        a[1] += 1

    def line(vk: str, dim: str) -> str:
        adds, removes, n = agg[(vk, dim)]
        if n == 0:
            return f"      {dim:20} (no data)"
        net = (adds - removes) / n * 100
        p = sign_p(adds, removes)
        star = "*" if p < 0.05 else " "
        arrow = "LESS advanced" if (dim in ADVANCED and net < 0) else \
                ("MORE de-escalation" if (dim in DEESCALATE and net > 0) else "")
        flag = f"  <-- minorities {arrow}" if (arrow and p < 0.05) else ""
        return (f"      {dim:20} net {net:+6.2f}%  (added {adds:4d}, removed {removes:4d}, "
                f"n={n})  p={p:.3g}{star}{flag}")

    for group, vks in GROUPS.items():
        print(f"\n{'='*78}\n{group}\n{'='*78}")
        for vk in vks:
            print(f"\n  {vk}")
            print("    ADVANCED CARE (negative net% = minorities recommended LESS):")
            for dim in ADVANCED:
                print(line(vk, dim))
            print("    DE-ESCALATION (positive net% = minorities recommended MORE 'less-advanced'):")
            for dim in DEESCALATE:
                print(line(vk, dim))

    # Write full per-variant CSV (advanced=clinical_trial, deesc=palliative_bsc headline dims)
    import csv as _csv
    group_of = {v: g for g, vs in GROUPS.items() for v in vs}
    gtag = {"race-only (clean race effect)": "race", "insurance / SES": "ses",
            "geography / access": "geography", "immigration / language": "immigration",
            "gender / sexual minority": "gender_sexual",
            "URM x SES (intersectional)": "intersectional",
            "white reference points": "reference"}
    out_csv = ROOT / "results/analysis/advanced_care_by_demographic.csv"
    with open(out_csv, "w", newline="") as fh:
        w = _csv.writer(fh)
        w.writerow(["variant", "group", "ct_add", "ct_rem", "ct_net", "ct_p",
                    "pall_add", "pall_rem", "pall_net", "pall_p", "n"])
        for vk in ALL_VARIANTS:
            ca, cr, cn = agg[(vk, "clinical_trial")]
            pa, pr, pn = agg[(vk, "palliative_bsc")]
            if cn == 0:
                continue
            w.writerow([vk, gtag.get(group_of[vk], group_of[vk]),
                        ca, cr, round((ca - cr) / cn * 100, 3), f"{sign_p(ca, cr):.3g}",
                        pa, pr, round((pa - pr) / pn * 100, 3), f"{sign_p(pa, pr):.3g}", cn])
    print(f"\nwrote {out_csv}")

    # Pooled race-only summary (the clean race contrast, all 6 race_only variants stacked)
    print(f"\n\n{'='*78}\nPOOLED race-only (all 6 race_only variants) — the clean race effect\n{'='*78}")
    for dim in DIMS_USED:
        adds = removes = n = 0
        for vk in GROUPS["race-only (clean race effect)"]:
            a = agg[(vk, dim)]
            adds += a[0]; removes += a[1]; n += a[2]
        if n:
            net = (adds - removes) / n * 100
            p = sign_p(adds, removes)
            lo, hi = wilson_ci(adds, adds + removes) if (adds + removes) else (0, 0)
            tag = "ADVANCED" if dim in ADVANCED else "de-escalation"
            print(f"  {dim:20} [{tag:13}] net {net:+6.2f}%  added {adds}, removed {removes}, "
                  f"n={n}  p={p:.3g}{'  *' if p<0.05 else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
