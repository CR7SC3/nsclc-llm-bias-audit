"""Count category flips hidden by tied treatment tiers, and targeted-therapy
switches in driver-positive cases.

Supports the eMethods "Tied treatment tiers" paragraphs and eTable 4 (Paper 1,
NSCLC). Excludes the dropped elderly_patient_75 variant (ORDER holds the 28
analyzed labels). A variant-reference pair is used only when both responses
parse, matching the pairwise exclusion in scripts/nsclc/correct_analysis.py.

Tied flips: the variant's treatment category differs from the no-demographics
reference's, but both map to the same rank in TREATMENT_RANK, so the flip is
invisible on the 1-8 tier scale.

Driver switches: among cases with a first-line-targetable driver (EGFR, ALK,
ROS1, BRAF, MET, or RET positive, or NTRK fusion; 334 cases, matching the
Table 1 footnote), restricted to case x model pairs whose reference response
recommends targeted therapy, the share of labeled responses that switch to
chemotherapy or chemoimmunotherapy.

Run:  venv/bin/python scripts/nsclc/count_tied_and_driver_switches.py
"""
from pathlib import Path
import collections
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.analyze.response_parser import ResponseParser
from src.analyze.continuous_scores import TREATMENT_RANK
from plots.plot_concordance_by_variant import MODELS, ORDER, REFERENCE, CASES_PATH

NEG = {"", "negative", "unknown", "none", "not_on_panel", "nan"}
DRIVER_KEYS = ["egfr_status", "alk_status", "ros1_status", "braf_status",
               "met_status", "ret_status"]
SWITCH_TO = {"chemotherapy", "chemoimmunotherapy"}


def driver_cases(cases):
    out = set()
    for c in cases:
        cp = c["clinical_profile"]
        if any(str(cp.get(k, "")).lower() not in NEG for k in DRIVER_KEYS) \
                or cp.get("ntrk_status") == "fusion":
            out.add(c["case_id"])
    return out


def main():
    cases = json.loads(Path(CASES_PATH).read_text())
    cases = cases if isinstance(cases, list) else list(cases.values())
    drivers = driver_cases(cases)
    parser = ResponseParser()

    flips, tied = collections.Counter(), collections.Counter()
    tied_pairs = collections.Counter()
    sw = collections.defaultdict(lambda: [0, 0])
    tref_pairs = 0
    for model, path in MODELS.items():
        raw = json.loads(Path(path).read_text())
        for cid, res in raw.items():
            rc = parser.parse(res.get(REFERENCE, {}).get("response_text", "")).category
            if rc == "unknown":
                continue
            targeted_ref = cid in drivers and rc == "targeted_therapy"
            tref_pairs += targeted_ref
            for v in ORDER:
                vc = parser.parse(res.get(v, {}).get("response_text", "")).category
                if vc == "unknown":
                    continue
                if vc != rc:
                    flips[model] += 1
                    if TREATMENT_RANK.get(vc) == TREATMENT_RANK.get(rc):
                        tied[model] += 1
                        tied_pairs[tuple(sorted((rc, vc)))] += 1
                if targeted_ref:
                    sw[v][0] += vc in SWITCH_TO
                    sw[v][1] += 1
        print(f"{model:18s} category flips {flips[model]:>6,}  tied {tied[model]:>4,} "
              f"({100 * tied[model] / flips[model]:.1f}%)", flush=True)

    nf, nt = sum(flips.values()), sum(tied.values())
    print(f"TOTAL category flips {nf:,}  tied {nt:,} ({100 * nt / nf:.1f}%)")
    for pair, k in tied_pairs.most_common():
        print(f"  {pair[0]} vs {pair[1]}: {k:,} ({100 * k / nt:.1f}%)")

    k = sum(a for a, _ in sw.values()); n = sum(b for _, b in sw.values())
    rate = {v: 100 * a / b for v, (a, b) in sw.items() if b}
    print(f"\ndriver-positive cases {len(drivers)}; case x model pairs with targeted "
          f"reference {tref_pairs:,}; switches {k} of {n:,} ({100 * k / n:.2f}%)")
    print(f"  per-label range {min(rate.values()):.2f}-{max(rate.values()):.2f}%; "
          f"unhoused {rate['unhoused_patient']:.2f}%, uninsured {rate['uninsured_only']:.2f}%, "
          f"white_male_private {rate['white_male_private']:.2f}%")


if __name__ == "__main__":
    main()
