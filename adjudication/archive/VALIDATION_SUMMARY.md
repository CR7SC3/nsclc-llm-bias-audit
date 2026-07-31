<!-- STATUS 2026-07-15: The 35-item targeted set described here is ARCHIVED to
adjudication/archive/ and SUPERSEDED as the representative validation by the
random-60 set (see archive/RANDOM60_VALIDATION.md). This document is retained as the record
of the targeted set's contested-case over-counting evidence (human sided with judge
12/17), which the random-60 set does not replace. Manuscript headline kappa is held
pending the second rater on gold_random_rater2.csv. -->

# Judge / Classifier Validation — Gold-Label Adjudication

**Status:** final for preprint (Option A, single-rater self-labeled gold set).
**Date:** 2026-07-01. **Rater:** A. Cuervo (study author). **Source data:**
`adjudication/gold_targeted.csv` (labels), `adjudication/judge_labels.json`
(Sonnet-4.6 judge), regex classifier flags in `adjudication/judge_items.jsonl`.
Reproduce with `python3 score_gold.py`.

## Design

To validate the stigma classifier without recruiting human clinician raters
(Option A), the study author labeled a **35-item targeted gold set** — items
enriched for classifier-flagged (contested) responses drawn from the Gemini and
DeepSeek arms. Items were presented blinded to demographic variant. Each item was
assigned one of three labels — **STIGMA**, **APPROPRIATE** (warranted SDOH-responsive
care), or **NEUTRAL** (no SDOH/adherence content) — operationalizing the corrected
stigma construct (adherence-doubt OR hallucinated/unwarranted SDOH assumption).
For agreement analysis, labels were binarized to **STIGMA vs. not-STIGMA**.

Gold-label distribution: **10 STIGMA / 17 APPROPRIATE / 8 NEUTRAL** (n=35).

## Results

| Comparison | % agreement | Cohen's κ |
|---|---|---|
| Human vs. LLM judge (Sonnet-4.6) | 71% | **0.30** |
| Human vs. regex classifier | 51% | 0.21 |

**Contested-case adjudication.** On the 17 items where the regex classifier flagged
STIGMA but the judge labeled APPROPRIATE, the human rater sided with the **judge in
12/17** cases and the regex in 5/17. The regex classifier **systematically over-counts
stigma**; the judge-adjudicated rate is the more accurate estimate. **All reported
stigma rates use judge-adjudicated labels**, not raw classifier flags.

**Disagreement structure.** Human–judge disagreement is confined entirely to the
appropriate-vs-stigma boundary within SDOH-flagged responses. On non-SDOH items the
human and judge agreed **20/20**; the 5 both-STIGMA cases also agreed. The 10
disagreements split **symmetrically** (5 human-STIGMA/judge-APPROPRIATE, 5 the reverse),
indicating no directional bias between rater and judge — only noise on an intrinsically
ambiguous boundary.

## Interpretation & limitation

The judge outperforms the regex classifier and corrects its over-counting, justifying
the use of judge-adjudicated stigma rates throughout. The modest absolute agreement
(κ=0.30, "fair") reflects genuine ambiguity in distinguishing *warranted* SDOH-responsive
care from *stigmatizing* assumption — the same distinction the models themselves navigate
imperfectly, and the substantive crux of this work. The validation is single-rater
(Option A, by design, to avoid the human-recruiting bottleneck); a second independent
rater to report inter-rater reliability is deferred to future work.
