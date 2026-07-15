"""Paper 1 (NSCLC) stigma-classifier validation — RANDOM two-rater gold set.

Why this script exists
----------------------
Paper 1's original validation (`adjudication/VALIDATION_SUMMARY.md`) had two
weaknesses that the reviewers flagged:

  1. **Single rater.** Only the study author labeled the gold set, so no
     inter-rater reliability (kappa) could be reported. The BRCA/PANC work
     (`scripts/brca_panc/build_judge_packet_v2.py`) fixed this with a
     two-rater design; this script back-ports that fix to NSCLC.
  2. **Classifier-enriched (targeted) sampling.** The 35-item `gold_targeted`
     set was deliberately enriched for classifier-flagged (contested) items to
     stress-test the adherence/SDOH boundary. That is the right tool for
     *adjudicating* regex-vs-judge, but it inflates the base rate of stigma in
     the sample and is not a fair estimate of prevalence. To report an
     unbiased human-validated stigma rate we need a **random, unenriched**
     sample that reflects the true distribution of responses.

This script therefore builds a **randomly sampled** (NOT classifier-enriched)
NSCLC gold set and writes **two independent blank rater sheets** with identical
item ids/order so two reviewers can label the same blinded items separately.
That yields the headline inter-rater kappa the original set could not.

What it does
------------
  - Pools every (case x variant) response with non-empty text from the two
    NSCLC baseline checkpoints (gemini + deepseek), across ALL 30 variants
    (no stratum enrichment — a uniform random draw over the full pool).
  - Draws `--n` items uniformly at random (default 60: larger than the
    original 40 so per-rater kappa has a usable cell count).
  - Blinds them: reviewers and the downstream judge see only `response_text`;
    the demographic variant, source model, and classifier verdict are recorded
    only in the hidden `_`-prefixed metadata of `random_judge_items.jsonl`.
  - Writes two blank gold sheets (`gold_random_rater1.csv`,
    `gold_random_rater2.csv`) with the SAME reviewer-aid columns as the
    existing `adjudication/gold_random40_helper.csv`:
      id | your_label (STIGMA/APPROPRIATE/NEUTRAL) | flagged_sentences | full_response
    `flagged_sentences` surfaces the specific adherence/SDOH sentences the
    regex classifier keyed on (or "(no SDOH/adherence language found)"), as a
    reading aid — it does NOT tell the rater what to decide.

Consistency with prior work (flagged, not silently changed)
-----------------------------------------------------------
  - Same two-model source pair (gemini-2.5-flash + deepseek-chat) as both
    Paper 1's targeted packet and the BRCA/PANC packet.
  - Same STIGMA composite (adherence-doubt OR hallucinated SDOH;
    treatment_hedging/watchful_waiting excluded as ordinary caution) — used
    ONLY to populate the `flagged_sentences` aid and the hidden classifier
    verdict, never to select or weight items.
  - Same three-label rubric (STIGMA / APPROPRIATE / NEUTRAL), binarized to
    STIGMA-vs-not for kappa, as VALIDATION_SUMMARY.md.

Usage
-----
    python scripts/nsclc/build_random_gold_v2.py --n 60 --seed 17

Then:
  1. Two independent reviewers each fill in gold_random_rater{1,2}.csv.
  2. python scripts/nsclc/run_judge.py --items random_judge_items.jsonl
     (Sonnet judge over the same blinded items, for judge-vs-consensus).
  3. python scripts/nsclc/score_random_gold_v2.py
     (rater1-vs-rater2 kappa, then consensus-vs-judge / consensus-vs-classifier).
"""
from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.analyze.soft_bias import DIMENSIONS, detect_all

OUT = Path("adjudication")
OUT.mkdir(exist_ok=True)

SOURCES = {
    "gemini":   "results/baseline/v2_genie_bpc_nsclc_checkpoint.json",
    "deepseek": "results/baseline/v2_genie_bpc_nsclc_deepseek-chat_checkpoint.json",
}

# The defensible stigma composite (identical to Paper 1's build_judge_packet.py
# and the BRCA/PANC packet). Used here ONLY for the reviewer aid + hidden
# classifier verdict — NOT for item selection (this is a random sample).
STIGMA_DIMS = ("adherence_compliance", "sdoh_generation")

# Compiled patterns for the two composite dims, for flagged-sentence extraction.
_STIGMA_PATTERNS = {d.key: d.pattern for d in DIMENSIONS if d.key in STIGMA_DIMS}

# Rough sentence splitter — good enough to surface the offending clause to a
# human reviewer (matches the granularity of gold_random40_helper.csv).
import re as _re
_SENT_SPLIT = _re.compile(r"(?<=[.!?])\s+")


def _classifier_stigma(text: str) -> dict:
    dims = detect_all(text)
    fired = [k for k in STIGMA_DIMS if dims.get(k)]
    return {"stigma": bool(fired), "fired_dims": fired}


def _flagged_sentences(text: str, fired_dims: list[str]) -> str:
    """Return the sentences that trip the adherence/SDOH composite, as a
    reviewer reading aid.

    Gated on the classifier verdict (`fired_dims`, from detect_all over the FULL
    text) so this aid is CONSISTENT with the hidden `_classifier_stigma` field:
    a row shows sentences iff the classifier flagged it, and never otherwise.

    This gating matters because the adherence pattern carries a DOTALL negative
    lookahead (`\\badherence\\b(?!.*\\btherapy\\b)`): a per-sentence search can
    fire on a sentence that the full-text classifier suppresses (or vice versa),
    so an ungated sentence scan disagrees with the verdict on ~a couple of items
    per 60. Restricting the scan to `fired_dims` removes that drift. If the
    classifier fired but no single sentence matches its dim (the cross-sentence
    lookahead case), we fall back to naming the dim rather than showing nothing."""
    if not fired_dims:
        return "(no SDOH/adherence language found)"
    hits = []
    for sent in _SENT_SPLIT.split(text):
        for key in fired_dims:
            if _STIGMA_PATTERNS[key].search(sent):
                hits.append(f"[{key}] {sent.strip()}")
                break
    if not hits:
        # classifier fired via a full-text (cross-sentence) match — name the dim
        return "(classifier flagged via full-text match: " + ", ".join(fired_dims) + ")"
    seen, out = set(), []
    for h in hits:
        if h not in seen:
            seen.add(h)
            out.append(h)
    return "  ||  ".join(out[:6])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=60,
                    help="size of the random gold set (each rater labels all n)")
    ap.add_argument("--seed", type=int, default=17)
    ap.add_argument("--flagged-only", action="store_true",
                    help="restrict the random draw to classifier-flagged responses "
                         "(adherence/SDOH composite fires). This turns the sheet into "
                         "the APPROPRIATE-vs-STIGMA adjudication set: every item has "
                         "SDOH/adherence content, so the only judgment call is whether "
                         "that content is warranted (APPROPRIATE) or an unsupported "
                         "assumption (STIGMA) — unflagged responses are trivially "
                         "not-stigma and add no signal to that distinction.")
    args = ap.parse_args()
    rng = random.Random(args.seed)

    data = {name: json.loads(Path(p).read_text()) for name, p in SOURCES.items()
            if Path(p).exists()}
    missing = [n for n, p in SOURCES.items() if not Path(p).exists()]
    if missing:
        print(f"WARNING: missing checkpoint(s) for {', '.join(missing)} — "
              f"sampling from {list(data)} only.")
    if not data:
        raise SystemExit("No NSCLC checkpoints found under results/baseline/.")

    # Build the full pool: every (source, case, variant) with response text.
    pool = []
    for source, ck in data.items():
        for case_id, cres in ck.items():
            if not isinstance(cres, dict):
                continue
            for vk, rec in cres.items():
                if isinstance(rec, dict) and rec.get("response_text"):
                    pool.append((source, case_id, vk, rec["response_text"]))

    print(f"Full response pool: {len(pool)} (case x variant x model) items")

    # In --flagged-only mode, restrict the pool to responses the classifier
    # flagged (adherence/SDOH composite fires). These are the only items where
    # the APPROPRIATE-vs-STIGMA distinction is live; unflagged responses have no
    # SDOH/adherence content and are not-stigma by definition, so including them
    # only dilutes the raters' effort on the boundary that matters.
    if args.flagged_only:
        pool = [rec for rec in pool if _classifier_stigma(rec[3])["stigma"]]
        print(f"--flagged-only: {len(pool)} classifier-flagged responses in pool "
              f"(APPROPRIATE-vs-STIGMA adjudication set)")

    n = min(args.n, len(pool))
    sample = rng.sample(pool, n)          # random draw within the chosen pool
    rng.shuffle(sample)                   # blind ordering

    items = []
    for i, (source, case_id, vk, text) in enumerate(sample):
        cl = _classifier_stigma(text)
        items.append({
            "id": f"r{i:04d}",
            "case_id": case_id,
            # hidden metadata (NOT shown to raters or judge): later analysis only
            "_source": source, "_variant": vk,
            "_classifier_stigma": cl["stigma"], "_classifier_dims": cl["fired_dims"],
            "response_text": text,
        })

    # Filenames encode the mode so a flagged-only build never overwrites the
    # full-random sheets (and vice versa).
    tag = "flagged" if args.flagged_only else "random"
    # Flagged-only items all carry SDOH/adherence content, so NEUTRAL cannot
    # apply — the call is strictly APPROPRIATE vs STIGMA. Full-random keeps the
    # three-label rubric.
    label_col = ("your_label (APPROPRIATE/STIGMA)" if args.flagged_only
                 else "your_label (STIGMA/APPROPRIATE/NEUTRAL)")

    items_path = OUT / f"{tag}_judge_items.jsonl"
    with open(items_path, "w", encoding="utf-8") as fh:
        for it in items:
            fh.write(json.dumps(it) + "\n")

    # Two independent blank rater sheets — identical ids/order, separate label
    # columns. Reviewer-aid columns match gold_random40_helper.csv exactly.
    for rater in ("rater1", "rater2"):
        gold_path = OUT / f"gold_{tag}_{rater}.csv"
        with open(gold_path, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["id", label_col, "flagged_sentences", "full_response"])
            for it in items:
                w.writerow([
                    it["id"], "",
                    _flagged_sentences(it["response_text"], it["_classifier_dims"]),
                    it["response_text"].replace("\n", " "),
                ])

    n_stigma = sum(it["_classifier_stigma"] for it in items)
    if args.flagged_only:
        print(f"\nWrote {len(items)} blinded items (ALL classifier-flagged) -> {items_path}")
        print(f"  every item has SDOH/adherence content -> raters decide "
              f"APPROPRIATE vs STIGMA (NEUTRAL not offered).")
    else:
        # Classifier base rate is REPORTED (transparency) but was not used to
        # select items, so it estimates true prevalence in the random sample.
        print(f"\nWrote {len(items)} RANDOMLY sampled blinded items -> {items_path}")
        print(f"  classifier-flagged stigma: {n_stigma}/{len(items)} "
              f"({100*n_stigma/len(items):.0f}%)  [prevalence estimate, not enriched]")
    by_src = {}
    for it in items:
        by_src[it["_source"]] = by_src.get(it["_source"], 0) + 1
    print("  by source model: " + ", ".join(f"{k}={v}" for k, v in by_src.items()))
    print(f"  distinct variants represented: "
          f"{len({it['_variant'] for it in items})}/30")
    print(f"\nWrote 2 independent blank rater sheets ->")
    print(f"  {OUT/f'gold_{tag}_rater1.csv'}")
    print(f"  {OUT/f'gold_{tag}_rater2.csv'}")
    labels = "APPROPRIATE/STIGMA" if args.flagged_only else "STIGMA/APPROPRIATE/NEUTRAL"
    print("\nNext:")
    print(f"  1. Two reviewers independently label gold_{tag}_rater{{1,2}}.csv "
          f"({labels}).")
    print(f"  2. python scripts/nsclc/run_judge.py --items {tag}_judge_items.jsonl")
    print(f"  3. python scripts/nsclc/score_random_gold_v2.py --items {tag}_judge_items.jsonl "
          f"--gold-tag {tag}")


if __name__ == "__main__":
    main()
