"""Generate free-text NSCLC clinical notes for GENIE BPC cases.

Pilot first (stratified 50), review, then full cohort.

Usage
-----
    venv/bin/python generate_genie_notes.py --pilot 50
    venv/bin/python generate_genie_notes.py --full
    venv/bin/python generate_genie_notes.py --pilot 50 --review-only   # rebuild report from cache
"""
from __future__ import annotations

import argparse
import json
import logging
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.generate.note_generator import NoteGenerator
from src.generate.note_qa import check_note

logging.basicConfig(level=logging.WARNING, format="%(asctime)s [%(levelname)s] %(message)s")

PROCESSED = Path("data/processed/genie_bpc_nsclc_processed.json")
REVIEW_DIR = Path("results/notes_review")
REVIEW_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Stratified pilot sampling
# ---------------------------------------------------------------------------

def _stage_bucket(stage: str) -> str:
    s = stage.upper()
    if s.startswith("IV"):
        return "IV"
    if s.startswith("III"):
        return "III"
    if s.startswith("II"):
        return "II"
    if s.startswith("I"):
        return "I"
    return "other"


def _driver_status(case: dict) -> str:
    p = case["clinical_profile"]
    if not case.get("biomarkers_available", True):
        return "biomarkers_unknown"
    drivers = [
        p.get("egfr_status") not in ("negative", "unknown"),
        p.get("alk_status") == "positive",
        p.get("ros1_status") == "positive",
        p.get("braf_status") == "v600e",
        p.get("met_status") == "exon_14",
        p.get("ret_status") == "fusion",
        p.get("ntrk_status") == "fusion",
    ]
    return "driver_positive" if any(drivers) else "driver_negative"


def stratified_sample(cases: list[dict], n: int, seed: int = 42) -> list[dict]:
    """Sample n cases stratified by stage bucket x driver status."""
    rng = random.Random(seed)
    strata: dict[tuple, list] = defaultdict(list)
    for c in cases:
        key = (_stage_bucket(c["clinical_profile"]["stage"]), _driver_status(c))
        strata[key].append(c)

    # Proportional allocation with at least 1 per non-empty stratum
    total = len(cases)
    picked: list[dict] = []
    for key, group in strata.items():
        rng.shuffle(group)
        share = max(1, round(n * len(group) / total))
        picked.extend(group[:share])

    rng.shuffle(picked)
    # Trim/pad to exactly n
    if len(picked) > n:
        picked = picked[:n]
    elif len(picked) < n:
        remaining = [c for c in cases if c not in picked]
        rng.shuffle(remaining)
        picked.extend(remaining[: n - len(picked)])
    return picked


# ---------------------------------------------------------------------------
# Review report
# ---------------------------------------------------------------------------

def write_review(cases: list[dict], qa_results: dict, out_path: Path) -> None:
    lines = ["# GENIE BPC NSCLC - Generated Note Review", ""]
    n = len(cases)
    n_pass = sum(1 for r in qa_results.values() if r["passed"])
    n_warn = sum(1 for r in qa_results.values() if r["warnings"])
    lines += [
        f"Total cases: {n}",
        f"Faithfulness + neutrality PASS: {n_pass}/{n} ({100*n_pass/n:.0f}%)",
        f"Cases with soft warnings: {n_warn}/{n}",
        "",
        "---",
        "",
    ]

    for c in cases:
        cid = c["case_id"]
        p = c["clinical_profile"]
        r = qa_results[cid]
        status = "PASS" if r["passed"] else "FAIL"
        lines += [
            f"## {cid}  [{status}]",
            "",
            "**Structured profile (ground truth):**",
            f"- Stage {p.get('stage')}, {p.get('histology')}, brain_mets={p.get('brain_mets')}",
            f"- EGFR={p.get('egfr_status')} ALK={p.get('alk_status')} ROS1={p.get('ros1_status')} "
            f"BRAF={p.get('braf_status')} MET={p.get('met_status')} RET={p.get('ret_status')} "
            f"NTRK={p.get('ntrk_status')} PD-L1={p.get('pdl1_tps_category')}",
            f"- biomarkers_available={c.get('biomarkers_available')}",
            f"- actual_treatment (held out): {c.get('actual_treatment')}",
            "",
        ]
        if r["failures"]:
            lines += ["**FAILURES:**"] + [f"- {f}" for f in r["failures"]] + [""]
        if r["warnings"]:
            lines += ["**warnings:**"] + [f"- {w}" for w in r["warnings"]] + [""]
        lines += [
            "**Generated note:**",
            "```",
            c.get("clean_note", "(none)"),
            "```",
            "",
            "---",
            "",
        ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--pilot", type=int, metavar="N", help="generate N stratified pilot cases")
    g.add_argument("--full", action="store_true", help="generate all included cases")
    ap.add_argument("--review-only", action="store_true",
                    help="skip generation; rebuild report from cached notes")
    ap.add_argument("--model", default="gemini-2.5-flash")
    ap.add_argument("--force", action="store_true",
                    help="regenerate notes even if a cached version exists "
                         "(use after clinical profile changes)")
    args = ap.parse_args()

    all_cases = json.loads(PROCESSED.read_text(encoding="utf-8"))

    if args.pilot:
        cases = stratified_sample(all_cases, args.pilot)
        tag = f"pilot{args.pilot}"
    else:
        cases = all_cases
        tag = "full"

    print(f"Selected {len(cases)} cases ({tag}).")
    strata = Counter((_stage_bucket(c['clinical_profile']['stage']), _driver_status(c)) for c in cases)
    print("Strata (stage x driver):")
    for k, v in sorted(strata.items()):
        print(f"  {k[0]:<5} {k[1]:<20}: {v}")

    gen = NoteGenerator(model_name=args.model)

    if not args.review_only:
        gen.generate_batch(cases, force=args.force)
    else:
        # Load cached notes only
        for c in cases:
            cached = gen._load_cache(c["case_id"])
            c["clean_note"] = cached or ""

    # QA
    qa_results = {
        c["case_id"]: check_note(
            c.get("clean_note", ""),
            c["clinical_profile"],
            c.get("biomarkers_available", True),
        )
        for c in cases
    }

    n = len(cases)
    n_pass = sum(1 for r in qa_results.values() if r["passed"])
    n_fail = n - n_pass
    n_warn = sum(1 for r in qa_results.values() if r["warnings"])
    print(f"\nQA: {n_pass}/{n} pass, {n_fail} fail, {n_warn} with soft warnings")
    if n_fail:
        print("Failure reasons (top):")
        reasons = Counter(f.split(":")[0] for r in qa_results.values() for f in r["failures"])
        for reason, cnt in reasons.most_common(10):
            print(f"  {cnt:>3}  {reason}")

    # Save cases-with-notes JSON
    out_json = Path(f"data/processed/genie_bpc_nsclc_{tag}_with_notes.json")
    out_json.write_text(json.dumps(cases, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSaved: {out_json}")

    review_path = REVIEW_DIR / f"genie_nsclc_{tag}_review.md"
    write_review(cases, qa_results, review_path)
    print(f"Saved: {review_path}")

    if args.full:
        # Also write canonical path used by run_experiment_v2.py
        canonical = Path("data/processed/genie_bpc_nsclc_with_notes.json")
        canonical.write_text(json.dumps(cases, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Saved: {canonical} (canonical for run_experiment_v2.py)")


if __name__ == "__main__":
    main()
