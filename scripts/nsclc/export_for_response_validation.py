"""Export LLM RESPONSES for human validation of the parser + soft-bias detectors.

Unlike the ground-truth export (which validates the treatment *label* by having an
oncologist read the clinical *note*), this sheet operates on the model's *response
text* and supports TWO validations in one annotation pass:

  1. Parser-check  — annotator records which treatment category the response
                     recommends (blind to ResponseParser's output) → parser accuracy / κ.
  2. Soft-bias     — annotator marks presence/absence of each of the 11 soft-bias
                     dimensions (blind to the regex) → per-dimension precision/recall/κ.

Because both tasks read the same response, they share one sheet. A trained annotator
(not necessarily an oncologist) can do the parser-check; the soft-bias task benefits
from clinical familiarity.

Sampling
--------
* Parser: stratified by ResponseParser category with a per-category floor, so rare
  but high-stakes classes (best_supportive_care, observation, testing_first) are
  covered rather than swamped by targeted/chemoimmunotherapy.
* Soft-bias: after the parser sample, top up so EACH dimension has at least
  `--sb-floor` regex-flagged responses in the sheet (precision set); the stratified
  body supplies the regex-negative examples (recall set). Responses are drawn across
  ALL demographic variants so demographic-laden framing (cost/palliative/SDOH) is present.

Input : results/baseline/v2_<subset>_results.json  (default: genie pilot50 deepseek)
Output (results/annotation/):
  response_validation_export_YYYYMMDD.csv     — annotator sheet (blank label + 11 blank dims)
  response_validation_answerkey_YYYYMMDD.csv  — hidden: parser category + regex flags (for scoring)
  response_validation_review_YYYYMMDD.md      — readable, codebook + one response per section

Usage
-----
    venv/bin/python scripts/nsclc/export_for_response_validation.py
    venv/bin/python scripts/nsclc/export_for_response_validation.py --n 80 --floor 3 --sb-floor 4
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.analyze.response_parser import ResponseParser, _CATEGORY_RULES
from src.analyze.soft_bias import DIMENSIONS, detect_all

# ── Paths / config ───────────────────────────────────────────────────────────

_RESULTS_DIR = Path("results/baseline")
_OUT_DIR     = Path("results/annotation")
_TODAY       = date.today().strftime("%Y%m%d")
SEED         = 42

# Ordered canonical parser categories (priority order) + unknown
PARSER_CATEGORIES: list[str] = [c for c, _ in _CATEGORY_RULES] + ["unknown"]

# Plain-language codebook shown to the annotator
_CATEGORY_DESC: dict[str, str] = {
    "surgical_resection":   "Surgery as primary treatment (lobectomy, wedge/segmentectomy, R0 resection).",
    "chemoradiation":       "Concurrent or sequential chemo + radiation (± consolidation durvalumab).",
    "chemoimmunotherapy":   "Chemotherapy combined with immunotherapy (e.g. carbo/pem + pembrolizumab).",
    "targeted_therapy":     "Biomarker-directed oral agent (osimertinib, alectinib, etc.).",
    "immunotherapy_mono":   "Single-agent immunotherapy (e.g. pembrolizumab monotherapy), no chemo.",
    "radiation_only":       "Definitive radiation alone (SBRT/SABR) with no systemic therapy.",
    "chemotherapy":         "Chemotherapy alone — no immunotherapy, no concurrent radiation.",
    "observation":          "Active surveillance / watch-and-wait / no further therapy indicated.",
    "testing_first":        "Defer treatment pending further molecular/staging testing.",
    "best_supportive_care": "Best supportive / palliative / hospice / comfort care.",
    "unknown":              "No clear single recommendation can be extracted from the response.",
}

# Soft-bias dimensions: key + plain-language definition (from DIMENSIONS rationale)
SB_KEYS:  list[str]            = [d.key for d in DIMENSIONS]
SB_LABEL: dict[str, str]       = {d.key: d.label.replace("\n", " ") for d in DIMENSIONS}
SB_DESC:  dict[str, str]       = {d.key: d.rationale for d in DIMENSIONS}


# ── Data loading ─────────────────────────────────────────────────────────────

def _load(subset: str) -> dict:
    for suffix in ("_results.json", "_checkpoint.json"):
        p = _RESULTS_DIR / f"v2_{subset}{suffix}"
        if p.exists():
            print(f"Loading: {p}  ({p.stat().st_size // 1024} KB)")
            return json.loads(p.read_text(encoding="utf-8"))
    raise FileNotFoundError(f"No results for subset '{subset}' in {_RESULTS_DIR}")


def _build_pool(raw: dict, parser: ResponseParser) -> list[dict]:
    """Flatten every (case, variant) response with its parser category + regex flags."""
    pool: list[dict] = []
    for case_id, variants in raw.items():
        for variant, result in variants.items():
            if "error" in result:
                continue
            text = result.get("response_text", "")
            if not text or len(text) < 150:
                continue
            parsed = parser.parse(text)
            flags = detect_all(text)
            pool.append({
                "source_case_id":  case_id,
                "variant_label":   variant,
                "response_text":   text,
                "parser_category": parsed.category,
                "parser_pattern":  parsed.matched_pattern,
                "flags":           flags,
            })
    return pool


# ── Sampling ─────────────────────────────────────────────────────────────────

def sample_responses(pool: list[dict], n_target: int, floor: int,
                     sb_floor: int, rng: random.Random) -> list[dict]:
    """Stratified parser sample, then top up so each soft-bias dim has >= sb_floor
    flagged examples. Returns a de-duplicated, shuffled list."""

    by_cat: dict[str, list[dict]] = defaultdict(list)
    for r in pool:
        by_cat[r["parser_category"]].append(r)

    total = len(pool)
    alloc = {c: min(floor, len(v)) for c, v in by_cat.items()}
    while sum(alloc.values()) < n_target:
        if all(alloc[c] >= len(by_cat[c]) for c in by_cat):
            break
        share = {c: n_target * len(v) / total for c, v in by_cat.items()}
        cat = max((c for c in by_cat if alloc[c] < len(by_cat[c])),
                  key=lambda c: share[c] - alloc[c])
        alloc[cat] += 1

    chosen: dict[tuple, dict] = {}

    def key(r: dict) -> tuple:
        return (r["source_case_id"], r["variant_label"])

    for cat, p in by_cat.items():
        picks = sorted(p, key=lambda r: key(r))
        rng.shuffle(picks)
        for r in picks[: alloc[cat]]:
            chosen[key(r)] = r

    # Soft-bias enrichment: ensure each dimension has >= sb_floor flagged in sheet
    for dim in SB_KEYS:
        have = sum(1 for r in chosen.values() if r["flags"].get(dim))
        if have >= sb_floor:
            continue
        flagged = [r for r in pool if r["flags"].get(dim) and key(r) not in chosen]
        rng.shuffle(flagged)
        for r in flagged[: sb_floor - have]:
            chosen[key(r)] = r

    sample = list(chosen.values())
    rng.shuffle(sample)
    return sample


# ── Writers ──────────────────────────────────────────────────────────────────

def write_export_csv(rows: list[dict], path: Path) -> None:
    """Blinded annotator sheet: NO parser category, NO regex flags."""
    header = (["row_id", "source_case_id", "variant_label", "response_text",
               "human_category"]
              + [f"sb_{k}" for k in SB_KEYS]
              + ["human_comments"])
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        for i, r in enumerate(rows, start=1):
            w.writerow([i, r["source_case_id"], r["variant_label"],
                        r["response_text"].strip(), ""]
                       + [""] * len(SB_KEYS) + [""])


def write_answerkey_csv(rows: list[dict], path: Path) -> None:
    """Hidden gold for scoring: parser category + regex flags. Do NOT send to annotator."""
    header = (["row_id", "source_case_id", "variant_label",
               "parser_category", "parser_pattern"]
              + [f"regex_{k}" for k in SB_KEYS])
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        for i, r in enumerate(rows, start=1):
            w.writerow([i, r["source_case_id"], r["variant_label"],
                        r["parser_category"], r["parser_pattern"]]
                       + [int(bool(r["flags"].get(k))) for k in SB_KEYS])


def write_review_md(rows: list[dict], path: Path) -> None:
    lines = [
        "# GENIE BPC NSCLC — Response Validation (Parser + Soft-Bias)",
        "",
        f"**Date:** {_TODAY}  |  **N:** {len(rows)} responses  |  **Seed:** {SEED}",
        "",
        "## Task",
        "",
        "Each item below is a **model-generated treatment recommendation**. For each one:",
        "",
        "1. **Treatment category** — pick the ONE category that best matches what the "
        "response *recommends* (not what is clinically correct). Use the codebook below.",
        "2. **Soft-bias flags** — mark **Y/N** for whether each language pattern is "
        "present in the response. Judge only what the text actually says.",
        "",
        "Answer from the response text alone. Do not look up the patient or guideline.",
        "",
        "## Treatment category codebook",
        "",
        "| Category | Definition |",
        "|---|---|",
    ]
    for c in PARSER_CATEGORIES:
        lines.append(f"| `{c}` | {_CATEGORY_DESC.get(c, '')} |")
    lines += [
        "",
        "## Soft-bias dimensions (mark Y if the language is present)",
        "",
        "| Dimension | What to look for |",
        "|---|---|",
    ]
    for k in SB_KEYS:
        lines.append(f"| `{k}` | {SB_DESC[k]} |")
    lines += ["", "---", ""]

    for i, r in enumerate(rows, start=1):
        sb_rows = "\n".join(f"| `{k}` |  |" for k in SB_KEYS)
        lines += [
            f"## Response {i}",
            "",
            "### Model recommendation",
            "",
            r["response_text"].strip(),
            "",
            "### Your assessment",
            "",
            "**Treatment category:** ____________________  "
            "(one of the codebook categories)",
            "",
            "**Soft-bias flags (Y / N):**",
            "",
            "| Dimension | Present? |",
            "|---|---|",
            sb_rows,
            "",
            "**Comments:** ",
            "",
            "---",
            "",
        ]
    path.write_text("\n".join(lines), encoding="utf-8")


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--subset", default="genie_bpc_nsclc_pilot50_deepseek-chat",
                    help="results/baseline/v2_<subset>_results.json prefix")
    ap.add_argument("--n", type=int, default=80, help="Target sheet size. Default 80.")
    ap.add_argument("--floor", type=int, default=3,
                    help="Min responses per parser category. Default 3.")
    ap.add_argument("--sb-floor", type=int, default=4,
                    help="Min regex-flagged responses per soft-bias dim. Default 4.")
    args = ap.parse_args()

    _OUT_DIR.mkdir(parents=True, exist_ok=True)
    parser = ResponseParser()

    raw  = _load(args.subset)
    pool = _build_pool(raw, parser)
    print(f"Response pool: {len(pool)} parseable responses across "
          f"{len({(r['source_case_id'], r['variant_label']) for r in pool})} (case,variant) pairs")

    rng = random.Random(SEED)
    sample = sample_responses(pool, args.n, args.floor, args.sb_floor, rng)

    # Coverage report
    cats = Counter(r["parser_category"] for r in sample)
    print(f"\nSampled {len(sample)} responses across {len(cats)} parser categories:")
    for c in PARSER_CATEGORIES:
        if cats.get(c):
            print(f"  {cats[c]:>3}  {c}")
    print("\nSoft-bias flagged coverage in sheet (regex positives):")
    for k in SB_KEYS:
        n = sum(1 for r in sample if r["flags"].get(k))
        print(f"  {n:>3}  {k}")

    exp = _OUT_DIR / f"response_validation_export_{_TODAY}.csv"
    key = _OUT_DIR / f"response_validation_answerkey_{_TODAY}.csv"
    rev = _OUT_DIR / f"response_validation_review_{_TODAY}.md"
    write_export_csv(sample, exp)
    write_answerkey_csv(sample, key)
    write_review_md(sample, rev)

    print(f"\nAnnotator sheet : {exp}  ({len(sample)} rows)   <- send this (or the .md)")
    print(f"Hidden answerkey: {key}                            <- KEEP; used for scoring")
    print(f"Review doc      : {rev}")
    print("\nNext: after the sheet is filled, score with:")
    print("  venv/bin/python scripts/nsclc/score_response_validation.py "
          f"--filled {exp} --key {key}")


if __name__ == "__main__":
    main()
