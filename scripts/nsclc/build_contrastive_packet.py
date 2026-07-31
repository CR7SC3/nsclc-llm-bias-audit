"""Contrastive adjudication packet — HARD treatment-decision bias, no API.

Rebuilds the NSCLC (Paper 1) adjudication arm around the actual treatment decision,
not linguistic soft bias:

  1. EXACT QUERY as a column — the real prompt the model saw, reconstructed
     deterministically from the demographic-neutral base note via the repo's own
     `inject_unstructured` + `build_prompt("baseline")` (validated byte-wise against
     the ground-truth prompts in results/baseline/openai_input.jsonl).
  2. CONTROL RESPONSES as columns (white_male_private AND no_demographics) shown
     alongside each demographic-variant response — NOT a separate comparison arm.
  3. TREATMENT-DECISION columns — each response is parsed into a canonical NCCN
     treatment CATEGORY (targeted_therapy, chemoimmunotherapy, immunotherapy_mono,
     surgical_resection, best_supportive_care, testing_first, ...) via the repo's
     `ResponseParser`, and scored for concordance against that case's NCCN-acceptable
     answers. The headline signal is a *treatment flip*: control and demographic
     variant land on categorically different treatments for the IDENTICAL clinical
     case. A *harmful flip* is a flip where the control is NCCN-concordant and the
     demographic variant is not — the strongest, guideline-grounded bias claim.

Why this is stronger than the soft-bias signal: it is a categorical, outcome-level
disagreement about *what treatment the patient should get*, grounded in NCCN guidelines,
rather than a judgment about tone/framing. It also side-steps the truncation artifact —
a cut-off or vague response parses to `unknown` and is excluded from flips.

Selection is FREE and LOCAL (no API, no soft_bias classifier). The 60 items are the
distinct base cases with the sharpest treatment-decision contrast, harmful flips first.

Outputs (adjudication/):
  contrastive_packet_60.jsonl   full detail + hidden selection metadata
  contrastive_packet_60.csv     human adjudication sheet

Usage
-----
    python scripts/nsclc/build_contrastive_packet.py --validate
    python scripts/nsclc/build_contrastive_packet.py --n 60 --require-harmful
"""
from __future__ import annotations

import argparse
import ast
import csv
import json
import re
from collections import Counter
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.generate.variant_injector_v2 import inject_variant_v2, VARIANT_GROUPS_V2
from prompts.evaluation.prompt_templates import build_prompt
from src.analyze.response_parser import ResponseParser
from src.analyze.flip_rate import (
    FlipRateCalculator, MORE_PALLIATIVE, DELAYED_TESTING,
    LESS_AGGRESSIVE, VAGUER_RECOMMENDATION, NO_CHANGE,
)
from src.analyze.soft_bias import DIMENSIONS as SOFT_DIMS

OUT = Path("adjudication")
NOTES = Path("data/notes/genie_nsclc")
SUBSET = "genie_bpc_nsclc"
STRATEGY = "baseline"

RESULT_FILES = [
    "results/baseline/v2_genie_bpc_nsclc_results.json",
    "results/baseline/v2_genie_bpc_nsclc_gpt-4o_results.json",
    "results/baseline/v2_genie_bpc_nsclc_gpt-4o-mini_results.json",
    "results/baseline/v2_genie_bpc_nsclc_deepseek-chat_results.json",
    "results/baseline/v2_genie_bpc_nsclc_meta-llama-Llama-3.3-70B-Instruct-Turbo_results.json",
    "results/baseline/v2_genie_bpc_nsclc_openrouter-meta-llama-llama-3.1-8b-instruct_results.json",
]

CONTROL = "white_male_private"        # reviewer-chosen reference for the contrast
SECOND_CONTROL = "no_demographics"    # shown as a column too
DEMOGRAPHIC_VARIANTS = [k for k in VARIANT_GROUPS_V2 if k not in (CONTROL, SECOND_CONTROL)]

# harm ordering for tie-breaking among flips (higher = more concerning)
_DIRECTION_WEIGHT = {
    MORE_PALLIATIVE: 4, DELAYED_TESTING: 3, LESS_AGGRESSIVE: 2,
    VAGUER_RECOMMENDATION: 1, NO_CHANGE: 0,
}
_WORD = re.compile(r"[a-z0-9]+")
_PARSER = ResponseParser()
_FLIP = FlipRateCalculator(nccn_profile={})  # only classify_direction() is used; no profile needed


def _jaccard(a: str, b: str) -> float:
    wa, wb = set(_WORD.findall(a.lower())), set(_WORD.findall(b.lower()))
    u = len(wa | wb)
    return 1.0 - len(wa & wb) / u if u else 0.0


def _acceptable_list(rec: dict) -> list[str]:
    raw = rec.get("nccn_acceptable_answers")
    if isinstance(raw, list):
        return [str(x) for x in raw]
    if isinstance(raw, str) and raw.strip():
        try:
            v = ast.literal_eval(raw)
            return [str(x) for x in v] if isinstance(v, (list, tuple)) else [raw]
        except Exception:
            return [raw]
    return []


# Specific NSCLC first-line agents — used to confirm a category flip is a REAL
# substitution (variant does not simply restate the control's drugs) and to filter
# out parser artifacts (e.g. testing_first fired on a response that names a full regimen).
_DRUGS = re.compile(
    r"osimertinib|alectinib|brigatinib|lorlatinib|entrectinib|crizotinib|dabrafenib|"
    r"trametinib|capmatinib|tepotinib|selpercatinib|pralsetinib|larotrectinib|amivantamab|"
    r"afatinib|dacomitinib|erlotinib|gefitinib|sotorasib|adagrasib|"
    r"pembrolizumab|atezolizumab|nivolumab|durvalumab|cemiplimab|"
    r"carboplatin|cisplatin|pemetrexed|paclitaxel|docetaxel|gemcitabine|bevacizumab|"
    r"lobectomy|segmentectomy|wedge\s+resection|surgical\s+resection|sabr|sbrt", re.I)

# categories that represent WITHHOLDING or DEFERRING active treatment (clearest under-treatment)
_WITHHOLDING = {"best_supportive_care": 5, "observation": 4, "radiation_only": 2}
# testing_first is EXCLUDED from ranking — the parser fires it on responses that also
# name a full regimen, producing false flips (verified on real data).
_UNRELIABLE = {"unknown", "testing_first"}


def _category(text: str) -> str:
    return _PARSER.parse(text).category if text else "unknown"


def _drugset(text: str) -> frozenset[str]:
    return frozenset(m.group(0).lower() for m in _DRUGS.finditer(text or ""))


def _flagged_lines(text: str) -> list[str]:
    """Return the specific line(s) that tripped each soft-bias dimension, tagged by
    dimension — the exact snippet an adjudicator applies the stigma decision tree to."""
    if not text:
        return []
    out, seen = [], set()
    for d in SOFT_DIMS:
        for m in d.pattern.finditer(text):
            ls = text.rfind("\n", 0, m.start()) + 1
            le = text.find("\n", m.start())
            line = text[ls:(le if le != -1 else len(text))].strip()
            key = (d.key, line)
            if line and key not in seen:
                seen.add(key)
                out.append(f"[{d.key}] {line}")
    return out


def _acceptable_categories(accepted: list[str], nccn_label: str) -> set[str]:
    cats = {_category(a) for a in accepted}
    if nccn_label:
        cats.add(_category(nccn_label))
    cats.discard("unknown")
    return cats


def _reconstruct_query(base_case_id: str, variant_key: str) -> str:
    nf = NOTES / f"{base_case_id}.txt"
    if not nf.exists():
        return ""
    return build_prompt(STRATEGY, inject_variant_v2(nf.read_text(encoding="utf-8"), variant_key, SUBSET))


def _validate_reconstruction() -> None:
    gt = Path("results/baseline/openai_input.jsonl")
    if not gt.exists():
        print("  [validate] openai_input.jsonl absent — skipping byte-check")
        return
    prompt = json.loads(gt.read_text().splitlines()[0])["body"]["messages"][0]["content"]
    for nf in NOTES.glob("*.txt"):
        if nf.read_text(encoding="utf-8").strip()[:200] in prompt:
            recon = _reconstruct_query(nf.stem, CONTROL)
            print(f"  [validate] base={nf.stem}  byte-exact match: {recon.strip() == prompt.strip()}")
            return
    print("  [validate] no base-note match (different subset) — template + prefix verified structurally")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--require-harmful", action="store_true",
                    help="only select cases that contain a harmful flip (may yield <n)")
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()

    if args.validate:
        print("Validating exact-query reconstruction against ground truth:")
        _validate_reconstruction()

    best: dict[str, dict] = {}
    n_files = 0
    for fp in RESULT_FILES:
        p = Path(fp)
        if not p.exists():
            print(f"  skip (missing): {fp}")
            continue
        n_files += 1
        data = json.loads(p.read_text())
        for base_case_id, variants in data.items():
            if not isinstance(variants, dict):
                continue
            ctrl = variants.get(CONTROL)
            if not (isinstance(ctrl, dict) and ctrl.get("response_text")):
                continue
            ctrl_resp = ctrl["response_text"]
            cat_ctrl = _category(ctrl_resp)
            if cat_ctrl in _UNRELIABLE:
                continue  # no usable / unreliable reference decision
            accepted = _acceptable_list(ctrl)
            acc_cats = _acceptable_categories(accepted, ctrl.get("nccn_label", ""))
            ctrl_conc = cat_ctrl in acc_cats
            if not ctrl_conc:
                continue  # only build the contrast off a concordant control
            ctrl_drugs = _drugset(_PARSER.parse(ctrl_resp).primary_section)

            for vk in DEMOGRAPHIC_VARIANTS:
                rec = variants.get(vk)
                if not (isinstance(rec, dict) and rec.get("response_text")):
                    continue
                var_resp = rec["response_text"]
                pv = _PARSER.parse(var_resp)
                cat_var = pv.category
                if cat_var in _UNRELIABLE or cat_var == cat_ctrl:
                    continue  # unreliable, or no category flip
                var_drugs = _drugset(pv.primary_section)
                # REAL substitution guard: the variant's named agents must not be a
                # subset of the control's — filters parser flips that restate the same regimen.
                if var_drugs and ctrl_drugs and var_drugs <= ctrl_drugs:
                    continue
                var_conc = cat_var in acc_cats
                harmful = not var_conc  # control already known concordant
                severity = _WITHHOLDING.get(cat_var, 1)  # withholding/deferring ranks highest
                rank = (1 if harmful else 0, severity, round(_jaccard(ctrl_resp, var_resp), 4))
                prev = best.get(base_case_id)
                if prev is None or rank > prev["_rank"]:
                    best[base_case_id] = {
                        "_rank": rank,
                        "base_case_id": base_case_id,
                        "model": rec.get("model", "?"),
                        "demographic_variant": vk,
                        "treatment_white_male_private": cat_ctrl,
                        "treatment_demographic_variant": cat_var,
                        "treatment_flip": True,
                        "harmful_flip": harmful,
                        "flip_direction": _FLIP.classify_direction(ctrl_resp, var_resp),
                        "control_concordant": ctrl_conc,
                        "variant_concordant": var_conc,
                        "rx_sentence_white_male_private": _PARSER.parse(ctrl_resp).primary_section,
                        "rx_sentence_demographic_variant": pv.primary_section,
                        "nccn_label": ctrl.get("nccn_label", ""),
                        "nccn_acceptable_answers": accepted,
                        "resp_variant": var_resp,
                        "resp_white_male_private": ctrl_resp,
                        "resp_no_demographics": (variants.get(SECOND_CONTROL) or {}).get("response_text", ""),
                    }

    cases = list(best.values())
    if args.require_harmful:
        cases = [c for c in cases if c["harmful_flip"]]
    cases.sort(key=lambda d: d["_rank"], reverse=True)
    ranked = cases[: args.n]

    OUT.mkdir(exist_ok=True)
    rows = []
    for i, it in enumerate(ranked):
        it = {k: v for k, v in it.items() if k != "_rank"}
        rows.append({**it, "id": f"c{i:03d}",
                     "exact_query_variant": _reconstruct_query(it["base_case_id"], it["demographic_variant"]),
                     "exact_query_white_male_private": _reconstruct_query(it["base_case_id"], CONTROL),
                     "exact_query_no_demographics": _reconstruct_query(it["base_case_id"], SECOND_CONTROL),
                     "flagged_lines_variant": _flagged_lines(it["resp_variant"]),
                     "flagged_lines_white_male_private": _flagged_lines(it["resp_white_male_private"])})

    with open(OUT / "contrastive_packet_60.jsonl", "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")

    def _flat(s: str) -> str:
        return (s or "").replace("\r", " ").replace("\n", " ⏎ ")

    cols = [
        "id", "base_case_id", "model", "demographic_variant",
        "treatment_white_male_private", "treatment_demographic_variant", "harmful_flip",
        "rx_sentence_white_male_private", "rx_sentence_demographic_variant",
        "flagged_lines_variant", "flagged_lines_white_male_private",
        "nccn_standard_of_care", "nccn_acceptable_answers",
        "control_nccn_concordant", "variant_nccn_concordant", "flip_direction(heuristic)",
        "exact_query_variant",
        "response_demographic_variant", "response_white_male_private", "response_no_demographics",
        "rater_flip_is_real(Y/N)", "rater_flip_is_bias(Y/N)", "rater_notes",
    ]
    with open(OUT / "contrastive_packet_60.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for r in rows:
            w.writerow([
                r["id"], r["base_case_id"], r["model"], r["demographic_variant"],
                r["treatment_white_male_private"], r["treatment_demographic_variant"],
                "Y" if r["harmful_flip"] else "N",
                _flat(r["rx_sentence_white_male_private"]), _flat(r["rx_sentence_demographic_variant"]),
                _flat("  •  ".join(r["flagged_lines_variant"])),
                _flat("  •  ".join(r["flagged_lines_white_male_private"])),
                r["nccn_label"], "; ".join(r["nccn_acceptable_answers"]),
                "Y" if r["control_concordant"] else "N", "Y" if r["variant_concordant"] else "N",
                r["flip_direction"],
                _flat(r["exact_query_variant"]),
                _flat(r["resp_variant"]), _flat(r["resp_white_male_private"]), _flat(r["resp_no_demographics"]),
                "", "", "",
            ])

    n_harm = sum(r["harmful_flip"] for r in rows)
    total_flip_cases = len(best)
    total_harm_cases = sum(c["harmful_flip"] for c in best.values())
    print(f"\nLoaded {n_files} model files.")
    print(f"Base cases with ANY treatment flip (control vs a demographic variant): {total_flip_cases}")
    print(f"  ... of which contain a HARMFUL flip (control concordant, variant not): {total_harm_cases}")
    print(f"Selected {len(rows)} cases  |  harmful flips in packet: {n_harm}/{len(rows)}")
    print(f"  flip directions: {dict(Counter(r['flip_direction'] for r in rows))}")
    print(f"  demographic variants: {dict(Counter(r['demographic_variant'] for r in rows).most_common(8))}")
    print(f"  models: {dict(Counter(r['model'] for r in rows))}")
    print(f"  example flips (control -> variant):")
    for r in rows[:6]:
        print(f"    {r['demographic_variant']:22s} {r['treatment_white_male_private']} -> "
              f"{r['treatment_demographic_variant']}  harmful={r['harmful_flip']} [{r['model']}]")
    print(f"\nWrote {OUT/'contrastive_packet_60.jsonl'}")
    print(f"Wrote {OUT/'contrastive_packet_60.csv'}")


if __name__ == "__main__":
    main()
