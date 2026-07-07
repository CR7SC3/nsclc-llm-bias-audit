"""Export GENIE BPC NSCLC notes for oncologist clinical validation.

Produces three files in results/annotation/:
  note_validation_export_YYYYMMDD.csv    — sent to oncologist (blinded; note only)
  note_validation_answerkey_YYYYMMDD.csv — internal key (note + structured profile)
  note_validation_review_YYYYMMDD.md     — human-readable side-by-side for review

Sampling: stratified by stage × driver × QA-tier (n=40)
  30 QA-PASSED notes across stage strata (I=3, II=3, III=7, IV no-BM=10, IV w-BM=7)
  10 QA-FAILED notes (8 brain-mets failures, 2 other failures)
  Within each stratum: ~40% driver-positive, ~60% driver-negative
  Seed=42 for reproducibility

Literature basis: n=40 follows Omiye et al. 2023 (NPJ Digital Medicine) precedent
for clinical AI equity studies; face validity + factual accuracy rubric.

Usage
-----
    venv/bin/python scripts/nsclc/export_for_note_validation.py
"""

from __future__ import annotations

import csv
import json
import random
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.generate.note_qa import check_note

# ── Paths ────────────────────────────────────────────────────────────────────

_NOTES_FILE = Path("data/processed/genie_bpc_nsclc_with_notes.json")
_OUT_DIR    = Path("results/annotation")
_TODAY      = date.today().strftime("%Y%m%d")

SEED = 42

# ── Stratum targets (QA-PASS pool) ──────────────────────────────────────────
# Key: (stage_bucket, brain_mets)  →  target N
_PASS_TARGETS: dict[tuple, int] = {
    ("I",   False): 3,
    ("II",  False): 3,
    ("III", False): 7,
    ("IV",  False): 10,
    ("IV",  True):  7,
}

# QA-FAIL targets by failure type
_FAIL_BRAIN_N = 8   # brain_mets=True failures
_FAIL_OTHER_N = 2   # all other failure types


# ── Helpers ──────────────────────────────────────────────────────────────────

def _stage_bucket(stage: str) -> str:
    s = stage.upper()
    if s.startswith("IV"):   return "IV"
    if s.startswith("III"):  return "III"
    if s.startswith("II"):   return "II"
    if s.startswith("I"):    return "I"
    return "other"


def _has_driver(profile: dict) -> bool:
    return any([
        str(profile.get("egfr_status", "")).lower() not in ("negative", "unknown", ""),
        profile.get("alk_status") == "positive",
        profile.get("kras_status") == "g12c",
        profile.get("braf_status") == "v600e",
        profile.get("met_status") == "exon_14",
        profile.get("ros1_status") == "positive",
        profile.get("ret_status") == "fusion",
        profile.get("ntrk_status") == "fusion",
    ])


def _driver_summary(profile: dict) -> str:
    pos = []
    if str(profile.get("egfr_status", "")).lower() not in ("negative", "unknown", ""):
        pos.append(f"EGFR {profile['egfr_status']}")
    if profile.get("alk_status") == "positive":   pos.append("ALK+")
    if profile.get("kras_status") == "g12c":      pos.append("KRAS G12C")
    if profile.get("braf_status") == "v600e":     pos.append("BRAF V600E")
    if profile.get("met_status") == "exon_14":    pos.append("MET ex14")
    if profile.get("ros1_status") == "positive":  pos.append("ROS1+")
    if profile.get("ret_status") == "fusion":     pos.append("RET fusion")
    if profile.get("ntrk_status") == "fusion":    pos.append("NTRK fusion")
    neg_keys = [
        ("egfr_status", "negative", "EGFR-"),
        ("alk_status", "negative", "ALK-"),
        ("kras_status", "negative", "KRAS-"),
    ]
    neg = [label for k, v, label in neg_keys if profile.get(k) == v]
    parts = []
    if pos: parts.append("; ".join(pos))
    if neg: parts.append("neg: " + ", ".join(neg))
    return " | ".join(parts) if parts else "no driver data"


def _profile_summary(profile: dict) -> str:
    lines = [
        f"Stage         : {profile.get('stage', 'unknown')}",
        f"Histology     : {profile.get('histology', 'unknown')}",
        f"Brain mets    : {profile.get('brain_mets', False)}",
        f"Smoking       : {profile.get('smoking_history', 'unknown')}",
        f"Molecular     : {_driver_summary(profile)}",
        f"PD-L1         : {profile.get('pdl1_final', 'unknown')}",
        f"TMB           : {profile.get('tmb_category', 'unknown')}",
    ]
    prior = profile.get("prior_cancers")
    if prior:
        lines.append(f"Prior cancers : {', '.join(prior)}")
    return "\n".join(lines)


# ── Sampling ─────────────────────────────────────────────────────────────────

def sample_cases(cases: list[dict], rng: random.Random) -> tuple[list[dict], list[dict]]:
    """Return (pass_sample, fail_sample) according to plan targets."""

    # Run QA on all cases (skip generation failures)
    qa_pass: dict[tuple, list[dict]] = defaultdict(list)   # (stage_bucket, brain_mets) -> cases
    fail_brain: list[dict] = []
    fail_other: list[dict] = []

    for c in cases:
        if c.get("_note_gen_failed") or not c.get("clean_note", "").strip():
            continue
        profile = c["clinical_profile"]
        qa = check_note(c["clean_note"], profile, c.get("biomarkers_available", True))
        c["_qa"] = qa
        stage_b = _stage_bucket(str(profile.get("stage", "unknown")))
        brain   = bool(profile.get("brain_mets"))

        if qa["passed"]:
            key = (stage_b, brain)
            if key in _PASS_TARGETS:
                qa_pass[key].append(c)
        else:
            is_brain_fail = any("brain_mets=True" in f for f in qa["failures"])
            if is_brain_fail:
                fail_brain.append(c)
            else:
                fail_other.append(c)

    # Sample PASS strata with driver-balance preference
    pass_sample: list[dict] = []
    for key, target in _PASS_TARGETS.items():
        pool = sorted(qa_pass[key], key=lambda c: c["case_id"])
        rng.shuffle(pool)
        # Prefer ~40% driver-positive
        driver_pos = [c for c in pool if _has_driver(c["clinical_profile"])]
        driver_neg = [c for c in pool if not _has_driver(c["clinical_profile"])]
        n_pos = max(1, round(target * 0.4)) if driver_pos else 0
        n_neg = target - n_pos
        picked = driver_pos[:n_pos] + driver_neg[:n_neg]
        # Pad from remainder if short
        if len(picked) < target:
            used = set(id(c) for c in picked)
            extras = [c for c in pool if id(c) not in used]
            picked += extras[:target - len(picked)]
        pass_sample.extend(picked[:target])

    # Sample FAIL cases
    rng.shuffle(fail_brain)
    rng.shuffle(fail_other)
    fail_sample = fail_brain[:_FAIL_BRAIN_N] + fail_other[:_FAIL_OTHER_N]

    return pass_sample, fail_sample


# ── Export helpers ────────────────────────────────────────────────────────────

_RUBRIC_COLS = [
    "plausibility_1to5",     # Does this read like a real oncology consult note? (1=implausible, 5=realistic)
    "factual_accuracy",      # Do stage/histology/biomarkers match the profile? (Pass/Fail)
    "completeness",          # Any clinically critical facts absent from note? (Pass/Fail)
    "treatment_naive_ok",    # Does the note correctly represent a treatment-naive consult? (Pass/Fail)
    "demographic_neutral",   # Any race/insurance/SES language detected? (Pass/Fail)
    "reviewer_comments",     # Free text
]


def write_export_csv(rows: list[dict], path: Path) -> None:
    """Blinded export — note only, no ground truth."""
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["row_id", "qa_tier", "note_text"] + _RUBRIC_COLS)
        for r in rows:
            writer.writerow([r["row_id"], r["qa_tier"], r["note_text"]] + [""] * len(_RUBRIC_COLS))


def write_answerkey_csv(rows: list[dict], path: Path) -> None:
    """Internal answer key with structured profile."""
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "row_id", "case_id", "qa_tier",
            "stage", "histology", "brain_mets", "driver_positive",
            "driver_summary", "pdl1", "tmb",
            "qa_failures", "qa_warnings",
            "note_text",
        ])
        for r in rows:
            p = r["profile"]
            writer.writerow([
                r["row_id"], r["case_id"], r["qa_tier"],
                p.get("stage"), p.get("histology"), p.get("brain_mets"),
                _has_driver(p), _driver_summary(p),
                p.get("pdl1_final"), p.get("tmb_category"),
                "; ".join(r["qa"]["failures"]),
                "; ".join(r["qa"]["warnings"]),
                r["note_text"],
            ])


def write_review_md(rows: list[dict], path: Path) -> None:
    """Human-readable markdown with note + profile side by side."""
    lines = [
        "# GENIE BPC NSCLC — Oncologist Note Validation Review",
        "",
        f"**Date:** {_TODAY}  |  **N:** {len(rows)} cases  |  **Seed:** {SEED}",
        "",
        "## Instructions",
        "",
        "For each case, rate the generated clinical note using the 5-item rubric:",
        "",
        "1. **Plausibility (1–5):** Does this read like a real oncology consult note?",
        "   `1=implausible, 3=plausible with concerns, 5=indistinguishable from real`",
        "2. **Factual accuracy (Pass/Fail):** Do the stage, histology, and biomarkers",
        "   match the structured profile shown?",
        "3. **Completeness (Pass/Fail):** Are there clinically critical facts in the profile",
        "   that are absent from the note (aside from demographics)?",
        "4. **Treatment-naive (Pass/Fail):** Does the note correctly represent an initial",
        "   consultation for a treatment-naive patient?",
        "5. **Demographic neutrality (Pass/Fail):** Any race, insurance, or SES language?",
        "",
        "QA tier key: **PASS** = automated checks passed | **FAIL** = automated check(s) failed",
        "",
        "---",
        "",
    ]

    for r in rows:
        tier_badge = r["qa_tier"]
        lines += [
            f"## Case {r['row_id']}  [{tier_badge}]",
            "",
            "### Structured Profile (Ground Truth)",
            "```",
            _profile_summary(r["profile"]),
            "```",
        ]
        if r["qa"]["failures"]:
            lines += [
                "",
                f"**QA failures:** {'; '.join(r['qa']['failures'])}",
            ]
        if r["qa"]["warnings"]:
            lines += [
                f"**QA warnings:** {'; '.join(r['qa']['warnings'])}",
            ]
        lines += [
            "",
            "### Generated Note",
            "",
            r["note_text"],
            "",
            "### Reviewer Ratings",
            "",
            "| Item | Rating |",
            "|---|---|",
            "| Plausibility (1–5) |  |",
            "| Factual accuracy (Pass/Fail) |  |",
            "| Completeness (Pass/Fail) |  |",
            "| Treatment-naive (Pass/Fail) |  |",
            "| Demographic neutrality (Pass/Fail) |  |",
            "| Comments |  |",
            "",
            "---",
            "",
        ]

    path.write_text("\n".join(lines), encoding="utf-8")


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    _OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading cases…")
    cases = json.loads(_NOTES_FILE.read_text(encoding="utf-8"))
    print(f"  {len(cases)} cases loaded.")

    rng = random.Random(SEED)
    pass_sample, fail_sample = sample_cases(cases, rng)

    # Shuffle so QA tier isn't obvious from ordering
    all_sampled = pass_sample + fail_sample
    rng.shuffle(all_sampled)

    # Build row dicts
    rows = []
    for i, c in enumerate(all_sampled, start=1):
        qa = c.get("_qa", {"passed": True, "failures": [], "warnings": []})
        rows.append({
            "row_id":    i,
            "case_id":   c["case_id"],
            "qa_tier":   "PASS" if qa["passed"] else "FAIL",
            "note_text": c.get("clean_note", "").strip(),
            "profile":   c["clinical_profile"],
            "qa":        qa,
        })

    n_pass = sum(1 for r in rows if r["qa_tier"] == "PASS")
    n_fail = sum(1 for r in rows if r["qa_tier"] == "FAIL")

    # Strata summary
    from collections import Counter
    strata = Counter()
    for c in pass_sample:
        p = c["clinical_profile"]
        bucket = _stage_bucket(str(p.get("stage", "?")))
        brain  = bool(p.get("brain_mets"))
        driver = "driver+" if _has_driver(p) else "driver-"
        strata[f"Stage {bucket} brain={brain} {driver}"] += 1

    print(f"\nSampled {n_pass} PASS + {n_fail} FAIL = {len(rows)} total cases")
    print("\nPass-pool strata:")
    for k, v in sorted(strata.items()):
        print(f"  {v:>2}  {k}")

    # Write outputs
    export_path = _OUT_DIR / f"note_validation_export_{_TODAY}.csv"
    key_path    = _OUT_DIR / f"note_validation_answerkey_{_TODAY}.csv"
    review_path = _OUT_DIR / f"note_validation_review_{_TODAY}.md"

    write_export_csv(rows, export_path)
    write_answerkey_csv(rows, key_path)
    write_review_md(rows, review_path)

    print(f"\nExport CSV   : {export_path}  ({len(rows)} rows)")
    print(f"Answer key   : {key_path}")
    print(f"Review doc   : {review_path}")
    print()
    print("Next steps:")
    print("  1. Send note_validation_export CSV + review_md to oncologist")
    print("  2. After review returns, merge ratings back into the answerkey CSV")
    print("  3. Run full experiment: venv/bin/python scripts/nsclc/run_experiment_v2.py --subset genie_bpc_nsclc")


if __name__ == "__main__":
    main()
