#!/usr/bin/env python3
"""Length/verbosity control for the mitigation ladder (council rigor gate).

The overcorrection claim rests on the blinded judge coding baseline responses APPROPRIATE
(warranted SES-responsive care) but mitigation-arm responses NEUTRAL. A skeptic asks: is the
care GENUINELY removed, or is the judge just coding a TERSER response as NEUTRAL? This checks:

  (1) Response length (words) per arm vs baseline — is the drop modest, or catastrophic truncation?
  (2) Treatment-recommendation retention: fraction of responses that still name a drug/regimen.
      If mitigation arms KEEP the drug recommendation while only SDOH framing drops, the care
      removal is real (the model still treats the patient; it just strips the socioeconomic layer).
  (3) The decisive test: among the exact cases where the judge flipped APPROPRIATE(baseline) ->
      NEUTRAL(arm) — "care removed" — what fraction STILL contain a drug recommendation? High = the
      response wasn't truncated, the SES-responsive care was specifically removed.

Runs on existing checkpoints + the judge label file. No model calls.

Usage:
    python scripts/nsclc/check_mitigation_length_control.py --model deepseek-chat --subset genie_bpc_nsclc_n300
    python scripts/nsclc/check_mitigation_length_control.py --model gemini-2.5-flash --subset genie_bpc_nsclc_mitig151
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from scripts.nsclc.analyze_mitigation_nsclc import (  # noqa: E402
    load_arms, common_cases, load_judge_labels, SES_VARIANTS, REFERENCE, ARMS,
)

# NSCLC treatment / drug-regimen keywords — presence = a treatment recommendation was made.
# (deliberately broad: modality words + common first-line agents across driver +/- disease)
_DRUG = re.compile(
    r"\b(chemo|chemotherapy|immunotherap|pembrolizumab|keytruda|nivolumab|atezolizumab|"
    r"durvalumab|cemiplibab|carboplatin|cisplatin|pemetrexed|paclitaxel|docetaxel|"
    r"gemcitabine|osimertinib|tagrisso|erlotinib|gefitinib|afatinib|alectinib|crizotinib|"
    r"lorlatinib|brigatinib|sotorasib|adagrasib|dabrafenib|trametinib|selpercatinib|"
    r"capmatinib|amivantamab|targeted therap|tyrosine kinase|TKI|checkpoint inhibitor|"
    r"radiation|radiotherapy|chemoradiation|lobectomy|resection|surgery|surgical|"
    r"concurrent chemoradi|adjuvant|neoadjuvant|first-line|systemic therap)\b",
    re.I,
)


def resp_text(cp, cid, variant):
    r = cp.get(cid, {}).get(variant, {})
    if not isinstance(r, dict) or "error" in r:
        return None
    return r.get("response_text") or None


def has_treatment(text: str) -> bool:
    return bool(text and _DRUG.search(text))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--subset", required=True)
    ap.add_argument("--baseline-subset", default="genie_bpc_nsclc")
    args = ap.parse_args()

    arms = load_arms(args.model, args.subset, args.baseline_subset)
    cases = common_cases(arms)
    judge = load_judge_labels(args.model, args.subset)
    mitig = [a for a in ARMS if a in arms and a != "baseline"]
    print(f"\nLENGTH-CONTROL  model={args.model}  cases={len(cases)}  (SES variants)\n")

    # ---- (1)+(2) length + treatment retention per arm ----
    print(f"  {'arm':<22}{'med words':>10}{'mean words':>11}{'has-treatment%':>16}")
    def stats(cp):
        lens, tx = [], 0
        n = 0
        for cid in cases:
            for v in SES_VARIANTS:
                t = resp_text(cp, cid, v)
                if t is None:
                    continue
                n += 1
                w = len(t.split())
                lens.append(w)
                tx += has_treatment(t)
        lens.sort()
        med = lens[len(lens)//2] if lens else float("nan")
        return med, (sum(lens)/len(lens) if lens else float("nan")), (tx/n if n else float("nan")), n
    for arm in ["baseline"] + mitig:
        med, mean, tx, n = stats(arms[arm])
        print(f"  {arm:<22}{med:>10.0f}{mean:>11.0f}{tx:>15.1%}")

    # ---- (3) decisive: among judge APPROPRIATE(baseline)->NEUTRAL(arm) flips, treatment retained? ----
    if judge is None:
        print("\n  (no judge labels found — skipping the APPROPRIATE->NEUTRAL retention test)")
        return
    print("\n  DECISIVE TEST — cases where judge flipped warranted-care OFF (baseline APPROPRIATE -> arm NEUTRAL):")
    print(f"  {'arm':<22}{'#flips':>8}{'treatment-retained%':>21}{'arm med words':>15}")
    for arm in mitig:
        flips = 0; retained = 0; wlens = []
        for cid in cases:
            for v in SES_VARIANTS:
                lb = judge.get("baseline", {}).get(cid, {}).get(v)
                la = judge.get(arm, {}).get(cid, {}).get(v)
                if lb != "APPROPRIATE" or la != "NEUTRAL":
                    continue
                t = resp_text(arms[arm], cid, v)
                if t is None:
                    continue
                flips += 1
                retained += has_treatment(t)
                wlens.append(len(t.split()))
        wlens.sort()
        med = wlens[len(wlens)//2] if wlens else float("nan")
        rt = retained/flips if flips else float("nan")
        print(f"  {arm:<22}{flips:>8}{rt:>20.1%}{med:>15.0f}")
    print("\n  INTERPRETATION: high treatment-retained% on the flip cases => the response was NOT truncated;")
    print("  the model still recommended a drug/regimen and specifically dropped the SES-responsive care.")
    print("  A non-trivial arm median word count on flips (not ~0) corroborates: real removal, not empty output.")


if __name__ == "__main__":
    main()
