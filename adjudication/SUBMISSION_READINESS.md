# SUBMISSION READINESS: EquityGUIDE Paper 1 (NSCLC)
_Single source of truth for what remains before submission · 2026-07-15_
_Target: medRxiv preprint → JMIR AI (primary) / BMC MIDM (backup)_

## Verdict: **NOT YET, but close. The science is done and validated; what remains is editorial.**

A four-seat validation deep-dive (stats / figures / red-team / codebase; details in
`VALIDATION_REPORT.md` + the four `archive/VALIDATION_*.md` files) confirmed the manuscript's
quantitative claims reproduce **exactly** from the results files: flip-rate means 6/6,
Table 2 Cohen's d 8/8, cohort N / stage / histology / site / EGFR / PD-L1, and the full
concordance table. The central finding (race≈0, monotone SES gradient, decision-stable /
framing-shifted dissociation) is sound and robust. No fabricated numbers were found. The
blockers below are disclosure, missing supplementary artifacts, and housekeeping: none
change a result.

---

## BLOCKING: must clear before submission

| # | Item | Why it blocks | Effort | Owner |
|---|---|---|---|---|
| B1 | **Second blinded rater labels the random gold set** (`gold_random_rater{1,2}.csv`), then run `score_random_gold_v2.py --gold-tag random` | Single-rater status (even at κ=0.57, PABAK 0.83) is a top reviewer risk; the sheet is built but unlabeled. Longest lead time (needs a human). | ~half-day of a second rater | Alvaro + 1 rater (lab-mate/mentor; clinician stronger) |
| B2 | **Fill reference placeholders 7, 8, 14** (Funding: RESOLVED, states no external funding) | An editor will not accept a manuscript with `[Author to insert…]` in the reference list. Ref 7 = **NCCN NSCLC v6.2026** (scorer is pinned there). Ref 8 = CancerGUIDE dataset. Ref 14 = deployment-vendor sources. | ~1 hr | Alvaro |
| B3 | **Generate the two missing supplementary artifacts** the manuscript already cites: **FigS0** (cohort/PD-L1 breakdown) and **Supplementary Table S3** (`supplementary_table_29variants_per_model.csv`) | Both are referenced in-text but do not exist on disk. S3 is a straightforward export from `results/analysis/*_soft_intensity.csv` (per-model Cohen's d already there). | ~1–2 hr | Alvaro / me |
| B4 | **Add inline single-rater hedge at every headline stigma number** (not just the Results epigraph + Limitations), e.g. "(single-rater validated, κ=0.57; read as rank not magnitude)" | Reviewers quote the number, not the disclaimer paragraph. | ~30 min | Alvaro / me |
| B5 | **Cite a reliability benchmark** (Viera & Garrett 2005 or Hallgren 2012) next to "fair agreement," and replace "not possible within this study's scope" with a concrete 2nd-rater protocol stub | Anchors the κ label externally; converts a vague limitation into a committed plan. | ~20 min | Alvaro / me |
| B6 | **Disclose English-only scope** in Limitations (one sentence) | Bears directly on the immigrant / limited-English variant tier's null claim: an English-only pipeline tests a label, not a language-access mechanism. Currently undisclosed. | ~10 min | me |
| B7 | **`git add` + commit the manuscript** (`docs/paper1_nsclc/manuscript_nsclc.md` is currently untracked) | Not under version control. | 2 min | Alvaro |

---

## DECISION REQUIRED (not blocking, but choose before finalizing numbers)

| # | Decision | Options | Recommendation |
|---|---|---|---|
| D1 | **Scorer version for reported concordance** | Manuscript numbers are frozen at the pre-rescore **v1.2025** scorer (verified exact match to `baseline_concordance.json`). The scorer is now **v6.2026**. | **Keep the frozen v1.2025 numbers + add ONE footnote** stating a v6.2026 re-score shifts absolute concordance by −3.0 to +0.4pp and leaves every demographic−reference differential unchanged within 0.5pp (`archive/NCCN_RESCORE_BEFORE_AFTER.md`). Full refresh is optional and changes no conclusion. |
| D2 | **Reconcile 5 Table 1 biomarker counts** that differ by 1–4 cases from a quick status-field recount (KRAS G12C 120 vs 116, ALK 43 vs 42, MET14 23 vs 22, ROS1 20 vs 19, RET 15 vs 14) | Manuscript's own extraction logic vs. the recount. | Confirm which extraction the manuscript used and make Table 1 self-consistent. Small, but a careful reviewer will re-add the column. |

---

## NICE-TO-HAVE (post-submission or reviewer-response)

- **A4: case-clustered CIs** (bootstrap / cluster-robust) instead of pooled Wilson intervals. A reviewer bootstrap already showed Wilson understates uncertainty on this repeated-measures design. Closes a real statistical objection; strong to have ready for revision.
- **README circularity reframe**: move the note-provenance / template + PMC rebuttal to the top (exposition only; evidence already exists).
- **Soften the GPT-4o "appropriate-care displacement" anomaly**: it's an n=1-model observation; phrase as "cannot be distinguished from noise" rather than asserting a mechanism.
- **Fix duplicated `## Discussion` header** in the manuscript.
- **Archive housekeeping** (non-manuscript): move superseded `results/baseline/*n300_gpt-4o*` (old n=209) and dropped `*claude-sonnet-5*` stubs to an `archive/` folder so a repo-inspecting reviewer isn't confused. Do not delete.

---

## What is already DONE (don't re-litigate)
- ✅ 6-vendor confirmatory panel complete at n=1,048 (all arms verified on disk).
- ✅ GPT-4o folded into analysis + 6-vendor figures (A2).
- ✅ Claude Sonnet audit arm dropped; claude-sonnet-4-6 retained only as blinded judge (A3).
- ✅ NCCN scorer reconciled to v6.2026 (atypical-EGFR, ERBB2/NRG1 line-of-therapy fixes; 81 tests pass).
- ✅ Full manuscript draft written and in-repo (A6).
- ✅ Every headline quantitative claim independently reproduced from results files.
- ✅ Robustness controls (template notes, PMC real notes, natural-embedding A/B) present and cited.

## Critical-path order
**B1 first** (longest lead time: recruit + label), in parallel with B2–B7 and D1–D2 (all quick).
When B1's κ lands, drop it into the Judge-Validation + Limitations sections, resolve D1's footnote,
and the manuscript is submission-ready for medRxiv + JMIR AI.
