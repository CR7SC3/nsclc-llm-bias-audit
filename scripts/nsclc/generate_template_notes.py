"""Build deterministic-template note files for the circularity control arm.

Writes processed `*_with_notes.json` files whose `clean_note` field is rendered
by `src.generate.template_note_generator` (NO LLM) instead of Gemini. These plug
directly into run_experiment_v2 via the registered subset names:

    genie_bpc_nsclc_templates      -> all 1,048 cases
    genie_bpc_nsclc_templates100   -> stratified 100-case control subset

Usage
-----
    python scripts/nsclc/generate_template_notes.py            # builds both files
    python scripts/nsclc/generate_template_notes.py --n 100    # change stratified subset size
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.generate.template_note_generator import render_note

SRC = Path("data/processed/genie_bpc_nsclc_with_notes.json")
OUT_FULL = Path("data/processed/genie_bpc_nsclc_templates_with_notes.json")
OUT_SUB = Path("data/processed/genie_bpc_nsclc_templates100_with_notes.json")


def _stage_bucket(stage: str) -> str:
    s = (stage or "").upper()
    for p in ("IV", "III", "II", "I"):
        if s.startswith(p):
            return p
    return "other"


def _stratified(cases: list[dict], n: int, seed: int = 17) -> list[dict]:
    """Sample n cases stratified by stage bucket, proportionally."""
    rng = random.Random(seed)
    buckets: dict[str, list[dict]] = {}
    for c in cases:
        buckets.setdefault(_stage_bucket(c["clinical_profile"].get("stage")), []).append(c)
    out: list[dict] = []
    total = len(cases)
    for b, members in buckets.items():
        k = max(1, round(n * len(members) / total))
        rng.shuffle(members)
        out.extend(members[:k])
    rng.shuffle(out)
    return out[:n]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=100, help="stratified control subset size")
    args = ap.parse_args()

    cases = json.loads(SRC.read_text(encoding="utf-8"))
    if isinstance(cases, dict):
        cases = list(cases.values())

    # Replace clean_note in place with the deterministic render; keep every other
    # field (case_id, clinical_profile, labels join keys) untouched.
    for c in cases:
        c["clean_note"] = render_note(c)
        c["note_source"] = "deterministic_template"

    OUT_FULL.write_text(json.dumps(cases, indent=1), encoding="utf-8")
    sub = _stratified(cases, args.n)
    OUT_SUB.write_text(json.dumps(sub, indent=1), encoding="utf-8")

    print(f"Wrote {len(cases)} template notes -> {OUT_FULL}")
    print(f"Wrote {len(sub)} stratified control notes -> {OUT_SUB}")
    print("\nSample render (case 0):\n" + "-" * 60)
    print(cases[0]["clean_note"])


if __name__ == "__main__":
    main()
