"""Backfill validated NCCN labels into existing experiment result JSONs.

The runner now attaches `nccn_label` + `nccn_acceptable_answers` to every result
record, but runs produced before that change lack them (so adherence reports as
un-scoreable). This stamps the labels in place, keyed by each record's
`base_case_id` (falling back to the case_id prefix), without re-running anything.

Usage
-----
    venv/bin/python scripts/nsclc/backfill_nccn_labels.py results/baseline/v2_genie_bpc_nsclc_pilot50_deepseek-chat_results.json
    venv/bin/python scripts/nsclc/backfill_nccn_labels.py results/baseline/v2_genie_bpc_nsclc_pilot50_deepseek-chat_*.json
    venv/bin/python scripts/nsclc/backfill_nccn_labels.py <files...> --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.generate.nccn_labels import load_nccn_index, nccn_fields


def _case_key(case_id: str, result: dict) -> str:
    """Best available base case id for label lookup."""
    bc = result.get("base_case_id")
    if bc:
        return bc
    # variant full ids look like "<case>__<variant>__<strategy>"; strip the suffix
    return case_id.split("__")[0]


def backfill_file(path: Path, idx: dict, dry_run: bool) -> tuple[int, int]:
    data = json.loads(path.read_text(encoding="utf-8"))
    stamped = total = 0
    for case_id, variants in data.items():
        for variant, result in variants.items():
            if not isinstance(result, dict) or "error" in result:
                continue
            total += 1
            key = _case_key(case_id, result)
            fields = nccn_fields(idx, key)
            if fields["nccn_label"] is not None:
                result.update(fields)
                stamped += 1
    if not dry_run:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return stamped, total


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("files", nargs="+", help="Result/checkpoint JSON files to stamp")
    ap.add_argument("--dry-run", action="store_true", help="Report only; do not write")
    args = ap.parse_args()

    idx = load_nccn_index()
    if not idx:
        sys.exit("No NCCN ground-truth file found — nothing to backfill.")
    print(f"Loaded {len(idx)} NCCN labels.\n")

    for f in args.files:
        p = Path(f)
        if not p.exists():
            print(f"  SKIP (missing): {p}")
            continue
        stamped, total = backfill_file(p, idx, args.dry_run)
        tag = "(dry-run) " if args.dry_run else ""
        print(f"  {tag}{p.name}: stamped {stamped}/{total} records")


if __name__ == "__main__":
    main()
