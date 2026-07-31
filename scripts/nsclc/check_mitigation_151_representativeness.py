#!/usr/bin/env python3
"""151-case representativeness gate for the DeepSeek mitigation salvage.

Compares the baseline SES stigma gradient and site composition across:
  151  = intersection of cases present in ALL 4 mitigation arms (the salvage set)
  300  = the n300 mitigation subset
  1048 = the full-cohort DeepSeek baseline
Baseline stigma is scored from the FULL-COHORT deepseek baseline checkpoint
(the same control the mitigation analysis pairs against).
"""
from __future__ import annotations
import json, sys
from pathlib import Path
from collections import Counter

REPO = Path("/Users/alvarocuervo/Documents/EquityGUIDE")
sys.path.insert(0, str(REPO))
from scripts.brca_panc.analyze_omar_metrics_pilot import _stigma_composite  # noqa

BASE = REPO / "results" / "baseline"
REF = "no_demographics"
SES = ["medicaid_only","uninsured_only","underinsured_only","low_income_patient",
       "low_income_black","unhoused_patient","black_unhoused"]
CTRL = ["white_male_private","no_demographics"]

arms = {
 "structured_extraction":"v2_genie_bpc_nsclc_n300_deepseek-chat_structured_extraction_results.json",
 "fairness":"v2_genie_bpc_nsclc_n300_deepseek-chat_fairness_checkpoint.json",
 "counterfactual_check":"v2_genie_bpc_nsclc_n300_deepseek-chat_counterfactual_check_checkpoint.json",
 "stigma_targeted":"v2_genie_bpc_nsclc_n300_deepseek-chat_stigma_targeted_checkpoint.json",
}
full = json.load(open(BASE/"v2_genie_bpc_nsclc_deepseek-chat_checkpoint.json"))
n300 = json.load(open(BASE/"v2_genie_bpc_nsclc_n300_deepseek-chat_structured_extraction_results.json"))

# intersection of full-30 cases across arms
sets=[]
for f in arms.values():
    d=json.load(open(BASE/f))
    sets.append({c for c,v in d.items() if isinstance(v,dict) and len(v)>=30})
inter = set.intersection(*sets)
cases_151 = sorted(inter)
cases_300 = sorted(n300.keys())
cases_1048 = sorted(full.keys())
print(f"151={len(cases_151)}  300={len(cases_300)}  1048={len(cases_1048)}")
print(f"151 ⊆ 300? {set(cases_151).issubset(cases_300)}   300 ⊆ 1048? {set(cases_300).issubset(cases_1048)}")

def site(cid:str)->str:
    # genie_NSCLC_GENIE-DFCI-000013_3  ->  DFCI ; GENIE-MSK-P-... -> MSK ; GENIE-VICC-.. -> VICC
    for s in ("DFCI","MSK","VICC","UHN","PROV","MDA"):
        if f"GENIE-{s}" in cid: return s
    return "OTHER"

def site_mix(cases):
    c=Counter(site(x) for x in cases); n=len(cases)
    return {k: f"{v} ({100*v/n:.0f}%)" for k,v in sorted(c.items(), key=lambda kv:-kv[1])}

def rate(cases, variant):
    """baseline stigma rate for a variant over given cases (scored from full-cohort baseline)."""
    vals=[]
    for cid in cases:
        s=_stigma_composite(full.get(cid,{}).get(variant,{}))
        if s is not None: vals.append(int(s))
    return (sum(vals)/len(vals) if vals else float("nan")), len(vals)

print("\n=== SITE COMPOSITION ===")
for label,cs in [("151",cases_151),("300",cases_300),("1048",cases_1048)]:
    print(f"  {label:>4}: {site_mix(cs)}")

print("\n=== BASELINE STIGMA RATE by variant (scored on full-cohort DeepSeek baseline) ===")
print(f"  {'variant':<20}{'151':>14}{'300':>14}{'1048':>14}")
ref151=rate(cases_151,REF)[0]; ref300=rate(cases_300,REF)[0]; ref1048=rate(cases_1048,REF)[0]
for v in CTRL+SES:
    r1,n1=rate(cases_151,v); r3,n3=rate(cases_300,v); rf,nf=rate(cases_1048,v)
    print(f"  {v:<20}{r1:>7.3f}(n{n1:>3}){r3:>7.3f}(n{n3:>3}){rf:>7.3f}(n{nf:>4})")

print("\n=== GRADIENT: RD vs no_demographics (variant_rate - ref_rate) ===")
print(f"  {'variant':<20}{'RD@151':>10}{'RD@300':>10}{'RD@1048':>10}")
for v in SES:
    r1=rate(cases_151,v)[0]-ref151; r3=rate(cases_300,v)[0]-ref300; rf=rate(cases_1048,v)[0]-ref1048
    print(f"  {v:<20}{r1:>+10.3f}{r3:>+10.3f}{rf:>+10.3f}")
# summary gradient scalar: mean RD over SES variants
def meanRD(cases, ref):
    return sum(rate(cases,v)[0]-ref for v in SES)/len(SES)
print(f"\n  mean SES RD:   151={meanRD(cases_151,ref151):+.3f}   "
      f"300={meanRD(cases_300,ref300):+.3f}   1048={meanRD(cases_1048,ref1048):+.3f}")
