# NSCLC random two-rater gold-set validation — status

> **2026-07-15:** Sheets built and verified; **still awaiting two human raters to label.**
> This is the #1 BLOCKING submission item — see `adjudication/SUBMISSION_READINESS.md`.
> Once labeled: `scripts/nsclc/score_random_gold_v2.py --gold-tag {random,flagged}`.

**Date:** 2026-07-09
**Scope:** back-port the BRCA/PANC two-rater detector validation to Paper 1
(NSCLC), on a **random, unenriched** sample — addressing the two limitations
`adjudication/VALIDATION_SUMMARY.md` flags for the original NSCLC validation:
single rater (no inter-rater kappa) and classifier-enriched (targeted) sampling.

## Why a new sample rather than reusing the old one

The original NSCLC gold sets serve a different purpose and cannot answer the
inter-rater / prevalence question:

- `gold_targeted.csv` (35 items) was **enriched for classifier-flagged contested
  cases** to adjudicate regex-vs-judge on the ambiguous boundary. Its stigma base
  rate is inflated by construction, so it is not a prevalence estimate.
- Both the targeted and the `gold_random40_helper.csv` sets were labeled by a
  **single rater**, so no Cohen's κ between independent raters could be reported.
  `VALIDATION_SUMMARY.md` explicitly defers "a second independent rater ... to
  future work." This is that work.

## What was built

- **`scripts/nsclc/build_random_gold_v2.py`** — draws **60 items uniformly at
  random** from the full NSCLC response pool (62,880 case × variant × model
  responses across the gemini + deepseek baseline checkpoints; **no stratum
  enrichment**), blinds them, and writes two independent blank rater sheets.
  Seed 17, reproducible.
- **`scripts/nsclc/score_random_gold_v2.py`** — once both reviewers label their
  sheets, reports rater1-vs-rater2 κ (headline), then rater-consensus-vs-judge
  and rater-consensus-vs-classifier, plus the rater-disagreement rate and the
  human-validated STIGMA prevalence on the random sample. Substantial-agreement
  bar κ ≥ 0.60 (same as BRCA/PANC), surfaced as a flag — not silently resolved.

## Outputs (in `adjudication/`)

- `random_judge_items.jsonl` — 60 blinded items. Visible fields: `id`,
  `case_id`, `response_text`. Hidden (`_`-prefixed, for later analysis only,
  shown to no one): `_source`, `_variant`, `_classifier_stigma`,
  `_classifier_dims`.
- `gold_random_rater1.csv`, `gold_random_rater2.csv` — the two blank sheets to
  send to the reviewers. **Identical item ids and order**, separate blank label
  columns. Columns match the existing `gold_random40_helper.csv` exactly:
  `id | your_label (STIGMA/APPROPRIATE/NEUTRAL) | flagged_sentences | full_response`.
  `flagged_sentences` is a reading aid (the specific adherence/SDOH sentences the
  classifier keyed on, or `(no SDOH/adherence language found)`), **not** a
  suggested answer.

## Sample composition (seed 17)

- n = 60, drawn uniformly from 62,880 responses.
- Source model: gemini = 26, deepseek = 34.
- 26 / 30 demographic variants represented.
- Classifier-flagged stigma: **9 / 60 (15%)** — a genuine prevalence estimate,
  since the sample is not enriched (contrast the targeted set).

## What the two reviewers must do

1. Each reviewer **independently** labels every row of their own sheet
   (`gold_random_rater1.csv` → reviewer 1, `gold_random_rater2.csv` → reviewer
   2) with one of **STIGMA / APPROPRIATE / NEUTRAL**, using the same three-label
   rubric as `VALIDATION_SUMMARY.md`. Do not confer; independence is what makes
   the κ meaningful.
2. Save the filled sheets back to the same paths.
3. (Optional, for judge validation) run
   `python scripts/nsclc/run_judge.py --items random_judge_items.jsonl` to have
   the Sonnet judge label the same blinded items.
4. `python scripts/nsclc/score_random_gold_v2.py` — prints inter-rater κ,
   consensus prevalence, and the consensus-vs-judge / consensus-vs-classifier
   agreement.

## Flags (not resolved here — study-team decisions)

- **Model pair.** The pool sources gemini-2.5-flash + deepseek-chat only,
  mirroring the original NSCLC packet and the BRCA/PANC packet. Anchoring the
  gold set to the full 4-model audit panel (gemini, deepseek, Llama-3.3-70B,
  gpt-4o) would require re-running the builder over those checkpoints.
- **κ < 0.60 handling.** The scorer reports pass/fail against the bar; it does
  not decide what to do on a fail (retrain raters, clarify rubric, add a third
  adjudicator). Same posture as the BRCA/PANC scorer.
- **Sample size.** 60 was chosen (vs. the original 40) to give the binarized
  STIGMA-vs-not κ a usable minority-cell count at ~15% prevalence; still modest.
  Enlarging is a one-line `--n` change plus re-labeling.
