"""Per-model (NEVER-pooled) advanced-care / de-escalation net% per demographic variant.

Companion to analyze_advanced_care_by_race.py (which pools across vendors). This variant
obeys the pre-registration's per-model rule (H4: never pool across vendors). Emits one row
per (variant, model) so the directional consistency across the 6 vendors can be shown with
per-model dots rather than a single pooled bar — the honest presentation, since per-model
BH-FDR leaves the individual effects non-significant while the harm DIRECTION replicates in
most vendors.

Outcomes (headline dims, matching the pooled script):
    clinical_trial (advanced care)  -> harm = net < 0 (offered LESS)
    palliative_bsc (de-escalation)  -> harm = net > 0 (offered MORE)

Output: results/analysis/advanced_care_per_model.csv
        columns: variant, group, model, ct_net, pall_net, n
"""
from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.analyze.soft_bias import detect_asymmetry
import scripts.nsclc.finalize_panel as fp

REF = "no_demographics"
CT_DIM = "clinical_trial"
PALL_DIM = "palliative_bsc"

# Demographic panel variants, grouped (same order/labels as the pooled figure), reference last.
# Race-only axis included so care-intensity coverage matches the 29-variant design (no silent
# axis drop): reviewers correctly flagged that race must be evaluated or explicitly justified.
GROUPS = {
    "ses": ["unhoused_patient", "medicaid_only", "medicare_only", "medicare_advantage_only",
            "underinsured_only", "uninsured_only", "low_income_patient", "high_income_patient"],
    "race": ["black_race_only", "hispanic_race_only", "asian_race_only",
             "native_american_race_only", "middle_eastern_race_only", "multiracial_race_only"],
    "geography": ["small_community_hospital", "rural_patient"],
    "immigration": ["limited_english_patient", "immigrant_patient"],
    "gender_sexual": ["transgender_woman", "gay_male_patient", "non_binary_patient"],
    "reference": ["white_male_private", "white_female_medicaid"],
}
GROUP_OF = {v: g for g, vs in GROUPS.items() for v in vs}
ALL_VARIANTS = list(GROUP_OF)


def main() -> int:
    present = {m: p for m, p in fp.ARMS.items() if (ROOT / p).exists()}
    print(f"Models present ({len(present)}): {list(present)}")

    # (model, variant, dim) -> [adds, removes, n]
    agg = defaultdict(lambda: [0, 0, 0])
    for model, path in present.items():
        d = json.loads((ROOT / path).read_text())
        for _cid, variants in d.items():
            if not isinstance(variants, dict):
                continue
            ref = variants.get(REF)
            if not (isinstance(ref, dict) and ref.get("response_text")):
                continue
            for vk in ALL_VARIANTS:
                rec = variants.get(vk)
                if not (isinstance(rec, dict) and rec.get("response_text")):
                    continue
                asym = detect_asymmetry(ref["response_text"], rec["response_text"])
                for dim in (CT_DIM, PALL_DIM):
                    a = agg[(model, vk, dim)]
                    a[2] += 1
                    if asym.get(dim, 0) > 0:
                        a[0] += 1
                    elif asym.get(dim, 0) < 0:
                        a[1] += 1

    out = ROOT / "results/analysis/advanced_care_per_model.csv"
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["variant", "group", "model", "ct_net", "pall_net", "n"])
        for vk in ALL_VARIANTS:
            for model in present:
                ca, cr, cn = agg[(model, vk, CT_DIM)]
                pa, pr, pn = agg[(model, vk, PALL_DIM)]
                if cn == 0:
                    continue
                w.writerow([vk, GROUP_OF[vk], model,
                            round((ca - cr) / cn * 100, 3),
                            round((pa - pr) / pn * 100, 3), cn])
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
