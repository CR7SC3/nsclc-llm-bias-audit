"""Natural-embedding A/B (methods M4, salience-artifact control).

Compares the stigma gradient when demographics are injected as a bracketed
metadata TAG ([PATIENT DEMOGRAPHICS: ...]) vs woven into the note as natural
PROSE, on the SAME 150 cases, per vendor. If the disadvantaged >> control
gradient survives natural embedding, the effect is not a label-following
artifact of the salient tag.

Stigma composite reuses finalize_panel (adherence-doubt OR hallucinated SDOH).

Run:  python3 scripts/nsclc/analyze_natural_ab.py
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.nsclc.finalize_panel import STRATA, _is_stigma, _wilson  # noqa: E402

# (vendor label, TAG results file, NATURAL results file)
ARMS = {
    "gemini-2.5-flash": (
        "results/baseline/v2_genie_bpc_nsclc_results.json",
        "results/baseline/v2_genie_bpc_nsclc_natural150_results.json",
    ),
    "deepseek-chat": (
        "results/baseline/v2_genie_bpc_nsclc_deepseek-chat_results.json",
        "results/baseline/v2_genie_bpc_nsclc_natural150_deepseek-chat_results.json",
    ),
}

# strata to show, disadvantage-ordered; the gradient claim = disadvantaged >> control
ORDER = ["control", "race_only", "uninsured", "underinsured", "low_income",
         "black_unhoused", "unhoused"]


def _rates(path: str, case_ids: set | None):
    """Per-stratum (k, n) stigma counts. If case_ids given, restrict to them
    (used to pair the full TAG arm down to the 150 natural case_ids)."""
    d = json.loads(Path(path).read_text())
    if case_ids is not None:
        d = {c: v for c, v in d.items() if c in case_ids}
    out = {}
    for stratum, vks in STRATA.items():
        k = n = 0
        for cres in d.values():
            for vk in vks:
                r = cres.get(vk)
                if isinstance(r, dict) and r.get("response_text"):
                    n += 1
                    k += _is_stigma(r["response_text"])
        out[stratum] = (k, n)
    return out, set(d.keys())


def main():
    for vendor, (tag_path, nat_path) in ARMS.items():
        if not (Path(tag_path).exists() and Path(nat_path).exists()):
            print(f"[skip {vendor}] missing results "
                  f"(tag={Path(tag_path).exists()}, natural={Path(nat_path).exists()})")
            continue
        # pair: restrict TAG arm to the case_ids present in the NATURAL arm
        nat, nat_ids = _rates(nat_path, None)
        tag, _ = _rates(tag_path, nat_ids)

        print(f"\n=== {vendor}  (paired n={len(nat_ids)} cases) ===")
        print(f"  {'stratum':14s} {'TAG %':>14s}   {'NATURAL %':>14s}   {'Δ pp':>6s}")
        ctrl_tag = 100 * tag['control'][0] / max(tag['control'][1], 1)
        ctrl_nat = 100 * nat['control'][0] / max(nat['control'][1], 1)
        for s in ORDER:
            kt, nt = tag[s]; kn, nn = nat[s]
            pt, lot, hit = _wilson(kt, nt)
            pn, lon, hin = _wilson(kn, nn)
            print(f"  {s:14s} {100*pt:5.1f} [{100*lot:4.1f},{100*hit:4.1f}]   "
                  f"{100*pn:5.1f} [{100*lon:4.1f},{100*hin:4.1f}]   {100*pn-100*pt:+5.1f}")
        # gradient survival check on the natural arm
        dis_nat = 100 * nat['unhoused'][0] / max(nat['unhoused'][1], 1)
        print(f"  gradient (unhoused - control): TAG {(100*tag['unhoused'][0]/max(tag['unhoused'][1],1))-ctrl_tag:+.1f}pp"
              f"  |  NATURAL {dis_nat-ctrl_nat:+.1f}pp")
        verdict = "REPLICATES" if (dis_nat - ctrl_nat) > 10 else "WEAK/ABSENT"
        print(f"  -> natural-embedding gradient: {verdict}")


if __name__ == "__main__":
    main()
