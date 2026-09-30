"""Re-derive every number in the Results paragraph on treatment-decision
stability (Paper 1, NSCLC) from the raw model responses.

Prints: flip rate per model, TOST equivalence counts (raw ±0.10 tier margin and
standardized d = ±0.10), pooled equivalence by variant group, BH-FDR-significant
directional downgrades, and per-model McNemar concordance results.

Uses the repo's own analysis functions (correct_analysis.py and
plot_concordance_by_variant.py); never calls a figure save. The dropped
elderly_patient_75 variant is excluded throughout.

Run:  venv/bin/python scripts/nsclc/verify_decision_results.py
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts" / "nsclc"), str(ROOT / "plots")]

import correct_analysis as CA
import plot_concordance_by_variant as PC  # module import only; its savefig is never called
from src.analyze.continuous_scores import score_checkpoint
from src.analyze.response_parser import ResponseParser
from src.analyze.stats import benjamini_hochberg

REFERENCE = "no_demographics"
DROPPED = "elderly_patient_75"

# Variant groups as defined for the tier-bias figure (plots/plot_tier_bias.py).
DISADVANTAGED = ["latina_female_uninsured", "black_unhoused", "low_income_black", "black_female_medicaid",
                 "uninsured_only", "medicaid_only", "underinsured_only", "medicare_only",
                 "medicare_advantage_only", "white_female_medicaid", "low_income_patient", "unhoused_patient"]
RACE_ONLY = ["black_race_only", "hispanic_race_only", "asian_race_only",
             "native_american_race_only", "middle_eastern_race_only", "multiracial_race_only"]
PRIVILEGED = ["white_male_private", "high_income_patient"]
OTHER = ["immigrant_patient", "limited_english_patient", "non_binary_patient", "transgender_woman",
         "gay_male_patient", "rural_patient", "small_community_hospital"]


def main() -> None:
    parser = ResponseParser()
    uniq, cat_map = PC.build_ground_truth()
    cells, flips, directional_p = {}, {}, {}

    for model, path in CA.MODELS.items():
        raw = CA._load(path)

        # Flip rate: pairs with an "unknown" parse on either side are excluded.
        total = flipped = 0
        for variants in raw.values():
            ref_text = variants.get(REFERENCE, {}).get("response_text", "")
            ref_cat = parser.parse(ref_text).category if ref_text else "unknown"
            if ref_cat == "unknown":
                continue
            for vk, vv in variants.items():
                if vk in (REFERENCE, DROPPED):
                    continue
                cat = parser.parse(vv.get("response_text", "")).category
                if cat == "unknown":
                    continue
                total += 1
                flipped += cat != ref_cat
        flips[model] = 100 * flipped / total

        # Per-model McNemar concordance, BH-FDR across variants within the model.
        res, ref_rate = PC.concordance_by_variant(raw, uniq, cat_map, parser)
        q = benjamini_hochberg({v: res[v][2] for v in PC.ORDER})
        sig = [(v, res[v][0], q[v]) for v in PC.ORDER if q[v] < 0.05]
        print(f"[McNemar] {model:17} reference {ref_rate:.1f}%  significant: "
              + (", ".join(f"{v} {r:.1f}% (q={qq:.3f})" for v, r, qq in sig) or "none"))

        # TOST equivalence and directional sign test per variant.
        scored = score_checkpoint(raw)
        variant_keys = [v for v in scored[next(iter(scored))] if v not in (REFERENCE, DROPPED)]
        for v in variant_keys:
            d = CA.directional_decision(scored, v)
            cells[(model, v)] = (CA.tost_equivalent(d["tier_ci"]),
                                 CA.tost_equivalent_standardized(d["tier_d"], d["n"]), d)
            directional_p[f"{model}::{v}"] = d["sign_p"]
        del raw, scored

    print(f"\n[Flip rate] " + ", ".join(f"{m} {r:.1f}%" for m, r in flips.items()))
    print(f"            range {min(flips.values()):.1f}% to {max(flips.values()):.1f}%, "
          f"mean {sum(flips.values()) / len(flips):.1f}%")

    raw_eq = sum(c[0] for c in cells.values())
    std_eq = sum(c[1] for c in cells.values())
    print(f"\n[TOST] raw ±0.10 tier margin: {raw_eq}/{len(cells)}; standardized d = ±0.10: {std_eq}/{len(cells)}")

    for name, group in [("disadvantaged", DISADVANTAGED), ("race-only", RACE_ONLY),
                        ("privileged (2 variants)", PRIVILEGED), ("white_male_private alone", ["white_male_private"]),
                        ("other", OTHER)]:
        hits = [c[0] for (m, v), c in cells.items() if v in group]
        print(f"[Equivalence by group] {name:26} {sum(hits)}/{len(hits)} = {100 * sum(hits) / len(hits):.1f}%")

    q = benjamini_hochberg(directional_p)
    print("\n[Directional, BH-FDR across all cells] significant:")
    for key in sorted(q, key=q.get):
        if q[key] < 0.05:
            m, v = key.split("::")
            d = cells[(m, v)][2]
            print(f"    {key}  down={d.get('down')} up={d.get('up')}  q={q[key]:.4f}")


if __name__ == "__main__":
    main()
