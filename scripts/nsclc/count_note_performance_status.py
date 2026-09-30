"""Count the ECOG performance status stated in the generated NSCLC notes.

Supports the eMethods "Clinical note generation" disclosure (Paper 1, NSCLC):
the note-generation prompt allowed "performance status discussion", so the
notes the models received (case["clean_note"], the field run_experiment_v2.py
sends) state their own ECOG value, whereas the NCCN scorer assumes ECOG 1 for
every case.

The first "ECOG" phrase in each note (up to 60 characters, within 1 sentence)
is classified as a range (eg, "0-1"), a single score (0-4), or no score; notes
without the word ECOG are counted as giving no ECOG score.

Run:  venv/bin/python scripts/nsclc/count_note_performance_status.py
"""
from pathlib import Path
import collections
import json
import re

ROOT = Path(__file__).resolve().parents[2]
CASES_PATH = ROOT / "data/processed/genie_bpc_nsclc_with_notes.json"


def classify(note: str) -> str:
    m = re.search(r"ECOG[^.\n]{0,60}", note)
    if not m:
        return "no ECOG score"
    phrase = m.group(0)
    if re.search(r"[0-4]\s*[-–]\s*[0-4]", phrase):
        return "range"
    scores = re.findall(r"\b([0-4])\b", phrase)
    return scores[0] if scores else "no ECOG score"


def main():
    cases = json.loads(CASES_PATH.read_text())
    cases = cases if isinstance(cases, list) else list(cases.values())
    counts, examples = collections.Counter(), {}
    for c in cases:
        k = classify(c["clean_note"])
        counts[k] += 1
        examples.setdefault(k, (c["case_id"], re.search(r"ECOG[^.\n]{0,60}", c["clean_note"])))
    print(f"{len(cases):,} notes")
    for k, n in counts.most_common():
        cid, m = examples[k]
        print(f"  {k:14s} {n:>4}   eg {cid}: {m.group(0) if m else '-'}")


if __name__ == "__main__":
    main()
