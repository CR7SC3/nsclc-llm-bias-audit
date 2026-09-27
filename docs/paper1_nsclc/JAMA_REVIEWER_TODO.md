# JAMA Network Open mock-review to-do list

Generated 2026-08-22 from two independent adversarial reviews of `manuscript_nsclc.md` and
`manuscript_nsclc_JAMA_NetworkOpen.md`, one playing a biostatistics/AI-methodology reviewer,
one playing a clinical-oncology/informatics reviewer. Items are grouped by what kind of work
they need, not by which reviewer raised them. Checkboxes are for tracking across sessions.

---

## Blocking (both reviewers independently flagged these; fix before anything else)

- [x] **Sync `manuscript_nsclc_JAMA_NetworkOpen.md` to the age-variant fix already made in
  `manuscript_nsclc.md`.** Done 2026-08-22: Exposures paragraph and eTable 1 row fixed to match.
  Still pending in this file (holding until the BH-FDR/TOST recompute lands, to avoid editing
  twice): the count-heavy sentences in Results/Discussion/Limitations (163/174, 134/174,
  27-29-of-29, etc.) still reflect the old 29-variant grid.
- [x] **Recompute the full BH-FDR grid on the actual 28-variant / 168-test design.** Done
  2026-08-22, after also fixing `correct_analysis.py`'s own memory-retention bug (it held all 6
  models' raw+scored data simultaneously, turning a ~15-minute job into 2+ hours; rewritten to
  stream one model at a time). Results, materially different from the pre-fix numbers, not just
  relabeled: raw-tier-units TOST equivalence 120/168 (was 163/174), standardized-margin
  equivalence 115/168 (was 134/174); zero variants show a significant net downgrade (was also
  zero, unchanged); the tied-tier flip rate is 1,577/36,513 (4.3%), and the rank-6 tie is now
  three-way (chemoimmunotherapy/targeted_therapy/dual_immunotherapy) since dual_immunotherapy
  was added this session; and a label-by-label concordance re-check found 7 of 28 variants
  significantly *more* concordant than the no-demographics reference in 2 of 6 models (Gemini,
  DeepSeek), including the privileged `white_male_private` control in Gemini, with none
  significantly less concordant anywhere, suggesting the no-demographics condition itself is a
  weaker baseline rather than any demographic-specific effect. All of this is now reflected in
  `manuscript_nsclc.md`, `manuscript_nsclc_JAMA_NetworkOpen.md`, and `PREREGISTRATION.md`'s
  deviation addendum. A driver-positive subgroup check (targeted-therapy patients switched to
  chemo/chemoimmunotherapy under a demographic label) was also run: 0-0.36% across variants, not
  disadvantage-patterned, now cited in Limitations as a robustness check on the tier-tie blind
  spot.
- [x] **Regenerate the per-model supplementary table** without the age-variant row
  and with the fixed parser; rename the file to match the new variant count. Done 2026-09-27:
  now `supplementary_table_28variants_per_model.csv` (168 rows = 28 variants x 6 models, built
  from the current-parser, elderly-free per-model CSVs by
  `scripts/nsclc/build_supplementary_table_s3.py`, written to `results/analysis/` and
  `docs/paper1_nsclc/`); the old 29-named files were removed. Figure 2's
  hardcoded numbers in `plots/plot_publishable_nsclc.py` were updated and a regeneration pass
  was dispatched (figure-builder agent) as part of this same update; check its result before
  treating Figure 2 as finalized.
- [x] **Resolve the TOST margin discrepancy.** Done 2026-08-22, with real recomputed numbers
  rather than a decision made on stale ones. Kept the raw-tier-units margin as primary (same
  rationale as before, a fixed clinical bound), reporting the standardized margin as sensitivity
  (120/168 vs 115/168). The sensitivity to this choice is now much smaller than the pre-fix
  analysis suggested (94%-vs-77% swing) and cuts in both directions by model rather than
  uniformly penalizing one (Gemini/DeepSeek/GPT-4o gain equivalences under the standardized
  margin, Llama-3.3-70B/Llama-3.1-8B/GPT-4o-mini lose them).
- [ ] **Fix the BH-FDR family-boundary inconsistency.** Still open. The paper corrects
  "grid-wide" in one place, "per axis group" in another, and reports a separate 48-test family
  for soft-framing; `PREREGISTRATION.md` specifies per-model families (28 each, after the
  variant-count fix). Pick one pre-specified plan, apply it uniformly, and disclose the
  deviation from pre-registration explicitly. Not touched by this session's recompute, which
  fixed the numbers within the existing (grid-wide) family structure, not the family structure
  itself.
- [ ] **Complete `gold_random_rater2.csv` labeling** (0/60, Bhavneet) — already tracked as the
  submission blocker, restated here because both reviewers independently flagged single-rater
  validation as a major concern.
- [x] **Reconcile `gold_flagged_rater2.csv` and `gold_flagged_rater2_BB.csv`.** Verified
  2026-08-22: all 60 rows agree exactly once `gold_flagged_rater2_BB.csv`'s raw `Yes`/`No`
  label encoding is translated to `STIGMA`/`APPROPRIATE` (zero true disagreements), and the
  `flagged_sentences` column is identical row-for-row. The one difference found (a mangled
  apostrophe in one `BB_notes` cell, a Windows-1252/UTF-8 encoding artifact) is already
  correctly fixed in `gold_flagged_rater2.csv`. `gold_flagged_rater2.csv` is confirmed as the
  correct normalization and stays canonical; `gold_flagged_rater2_BB.csv` is kept as-is as the
  rater's original raw submission (provenance), not deleted.
- [x] **Harmonize the IRB/ethics statement across both manuscript files.** Done 2026-08-22:
  added the "investigator self-determination, not a formal exemption letter" caveat (already
  present in the JAMA file) to both places the full manuscript asserted IRB-exemption flatly
  (Methods, Ethical Considerations; and the Ethics Approval summary statement). A written IRB
  determination letter, if one can actually be obtained, would still be stronger than either.
- [x] **Resolve the ECOG contradiction.** Done 2026-08-22. No real code contradiction: verified
  against the actual processed data that all 1,048 cases have `ecog_ps=1` (GENIE BPC doesn't
  record it), matching Limitations exactly. The bug was one Supplementary Methods sentence
  listing "ECOG status" among the LLM-free template control's "GENIE structured fields," fixed
  to state it's the fixed default, not a per-case field. Also found and disclosed a related,
  previously-unflagged issue: the note-generation prompt never supplies an ECOG value at all, so
  gemini-2.5-flash invents one in the free text; checked all 1,048 generated notes directly (580
  state ECOG 1, 200 state ECOG 0, 1 states ECOG 2, 267 don't mention it). Confirmed this doesn't
  change any scored result (every scorer ECOG threshold groups 0 and 1 identically; only the
  single ECOG-2 note could matter, negligible at n=1) and added a quantified disclosure to
  Limitations rather than re-running anything, consistent with how the tumor-size fabrication
  issue was already handled.

---

## Parser and effect-size/CI code audit (found by direct code review, not the two reviewer agents)

- [x] **Chemoimmunotherapy over-assignment from unbounded cross-drug regex patterns.** Fixed and
  measured 2026-08-22. `response_parser.py`'s chemoimmunotherapy patterns (`carboplatin.*pembrolizumab`
  etc.) and the immunotherapy_mono / dual_immunotherapy negative lookaheads used bare `.*` under
  `re.DOTALL`, so they matched (or suppressed a match on) two drug names anywhere in the whole
  captured window, not just when actually combined in the same sentence. Measured real impact by
  running the current parser and a sentence-bounded (`[^.]*?`) patched version across all
  188,640 real collected responses before deciding to fix: 8,035 (4.26%) got a different
  category, 80% of them chemoimmunotherapy being wrongly assigned over immunotherapy_mono or
  chemotherapy. Disagreement rate was essentially uniform across demographic groups
  (4.24-4.55%), so the bug does not itself manufacture the reported bias findings, but it does
  mean absolute category counts feeding every downstream concordance/tier-shift statistic were
  measurably wrong. Fixed by bounding all cross-drug patterns to `[^.]*?`; 3 new tests added to
  `tests/test_response_parser.py`; all 159 existing tests still pass. **The BH-FDR/TOST
  recompute already in progress for the 28-variant fix above was using the stale parser (Python
  had already imported it when that background run started) and had to be killed and re-run
  after this fix landed.**
- [ ] **Fallback-window category-priority bug (not yet fixed, needs a design decision first).**
  59.6% of all real responses use the header/full-text-window fallback (not the `regimen_tag`
  path), uniform across demographic groups. In that path, category assignment is decided by
  fixed rule-list order, not by which treatment the response is textually leading with, so a
  response whose primary recommendation is (say) chemotherapy but which mentions "SBRT" as a
  second-line alternative anywhere in the window gets classified as `radiation_only` instead.
  Unlike the bug above, there's no clean "textually first" fix without redesigning the
  extraction, needs a decision on approach before touching it.
- [ ] **`paired_delta()` CI/p-value mismatch (documentation, not a code bug).** The reported CI
  is parametric (t-distribution on the mean of paired differences); the reported p-value is
  nonparametric (Wilcoxon signed-rank, closer to testing the median). They can disagree if the
  paired differences are skewed. Needs a caveat in Methods/Supplementary Methods; this same CI
  is what the TOST equivalence check relies on.
- [x] **`significance_label()` threshold-nesting bug.** Fixed 2026-08-22. A p-value now has to
  clear the Bonferroni-corrected threshold (alpha/n) before any star is awarded; `**`/`***` then
  refine the tier among results that already qualify. Confirmed this doesn't change anything
  currently in the manuscript (it uses BH-FDR q-values for its reported stars, not this
  function), but it does change `concordance_checker.py`'s own diagnostic console printout for
  borderline cases at `n=n_minority` (re-run that script if you want the corrected diagnostic
  table). 3 new tests added in `tests/test_stats.py` (this file didn't exist before); full suite
  321/321.

## Statistical / methodological (biostatistics reviewer)

- [ ] Clarify the construct-validity gap between the equivalence test (TOST on mean paired
  treatment-tier shift) and the outcome it's described as testing (NCCN concordance, a binary
  variable). Either add a proper equivalence test directly on concordance, or explicitly state
  tier-shift is a proxy and concordance itself is only tested via McNemar (an NHST, not an
  equivalence test).
- [ ] Move the Figure 3 care-intensity headline (trial mentions -1.4pp, p = 0.002) out of
  Abstract/Key Points headline framing, or bring it inside the corrected multiplicity family.
  Results already call these two pooled tests "not part of the BH-FDR family... read as
  descriptive," but the Abstract presents them as a clean finding.
- [ ] Verify which demographic axis (race or SES) the q = 0.01 pooled clinical-trial-mention
  figure actually belongs to — the Abstract attributes it to race, Results attribute it to SES.
  Use the stats-verifier agent against the raw data before deciding which is correct.
- [ ] State explicitly whether reported Cohen's d values (e.g., d = 1.01 for underinsured) are
  paired or independent-samples, so the number is reproducible.
- [ ] Fix the stigma-composite definition ambiguity: Methods describe it as a "share of
  responses," but the Figure 5B legend says bars can co-occur and sum past 100%. Clarify whether
  93.2% is a response share or a sum of four net deltas.
- [ ] Correct the claim that demographic-blind parser/scorer errors are harmless to the TOST
  result. Non-differential measurement error attenuates a paired mean difference toward zero,
  which makes equivalence *easier* to declare at n≈1,048, not just noisier. Add a sensitivity
  analysis or an explicit caveat.
- [ ] Add a sensitivity analysis (or at least a stated caveat with numbers) for the 100%-imputed
  ECOG-1 default and the 64%-missing PD-L1 permissive default, both of which the paper already
  concedes inflate or distort absolute concordance.
- [ ] Add a STROBE checklist for the cross-sectional design alongside the existing TRIPOD-LLM
  checklist — JAMA Network Open expects both for this study type.
- [ ] Reconcile the gold-set sampling deviation from `PREREGISTRATION.md` §6b (spec: 40-item
  stratified subset from 60/60/60) against what was actually done (60 items, random, preserving
  ~10% prevalence). Add to the deviation addendum; nothing currently documents this change.
- [ ] Refresh `TRIPOD_LLM_checklist.md` — its own citation numbers and line references are stale
  against the current manuscript (it already warns it "has previously gone stale").
- [ ] Report the denominator (n) behind the "unique-answer-scorable subset" used for the
  1.0-percentage-point absolute-concordance-shift bound; currently unstated.
- [ ] Add multiplicity handling, or an explicit rationale for omitting it, to the 6
  Cochran-Armitage trend tests and the 15 pairwise inter-model Spearman correlations.
- [ ] Confirm whether the restricted/concordant-control sensitivity analysis intentionally
  switches its anchor to `white_male_private` instead of `no_demographics`, and add power/CI
  context to its "none Fisher-significant across 174 cells" claim.
- [ ] Verify "flagged language increased in 5 of 6 models" against Table 2's `underinsured_only`
  row, which appears positive across all six models as printed — confirm which model is the
  actual exception and on what test.
- [ ] Either state plainly that no a priori power calculation was performed for the
  salience/template/PMC robustness controls (n = 40-150), or give those comparisons a
  pre-specified equivalence margin instead of reporting a raw non-significant difference as
  confirmation that the effect isn't a pipeline artifact.

---

## Clinical / domain (oncology reviewer)

- [ ] **Get an oncologist (or palliative care / social work) reviewer** for the stigma-vs-
  appropriate-care language taxonomy — currently entirely one author's judgment call. This is
  the same open item as mentor comment #4 (oncologist feedback on the invasiveness/aggressiveness
  ranking) from the original meeting notes.
- [ ] Define "resectability" as a scorer input (currently used but never defined) and disclose
  how, or whether, Category-1 non-metastatic standards (adjuvant osimertinib, consolidation
  durvalumab, perioperative chemo-immunotherapy) are represented in the decision tree, given
  43.3% of the cohort (n=454) is Stage I-III.
- [ ] Run a driver-positive-only subgroup analysis of targeted-therapy-to-chemotherapy switching
  by demographic label. The current tier-tie between ranks 5 and 6 (chemoimmunotherapy and
  targeted therapy) hides exactly this flip type, which is the most clinically serious error an
  LLM could make for the ~32% of the cohort with an actionable driver mutation.
- [ ] Add an explicit Discussion caveat against reading "decision stability" as "safe to
  deploy," especially since absolute concordance is as low as 49.9% for one model
  (Llama-3.1-8B) — stability of a frequently-wrong recommendation is not the same as safety.
- [ ] Reconcile the care-intensity outcome's palliative-framing-as-harm scoring with the paper's
  own logic for excluding palliative framing from the stigma composite (because it's often
  guideline-concordant given 56.7% Stage IV). Decompose the care-intensity result or reframe it
  as clinically neutral pending that decomposition.
- [ ] Add a response-level co-occurrence check for the underinsured/uninsured variant family,
  which currently carries both the largest "appropriate care" signal and the only two real
  treatment downgrades. Rule out cost-driven regimen downgrade being scored as warranted
  financial-counseling language.
- [ ] Disclose GENIE BPC's own selection bias (enrollment requires tumor panel sequencing, which
  is itself differentially ordered by insurance status and race) alongside the existing
  cohort-skew disclosures (academic-center-only, race, histology, smoking status).
- [x] Document the age-75 exclusion's rationale and timing explicitly in one place. Resolved
  2026-09-27 by removing the age label from the design rather than excluding it from analysis:
  every note already states the patient's age from the GENIE record, so the label duplicated or
  contradicted a clinical fact. Both manuscripts now describe 28 variants / 29 versions / 182,352
  responses, with one Methods sentence giving that reason; the ECOG artifact is no longer offered
  as a rationale. Recorded in `PREREGISTRATION.md`'s 2026-09-27 addendum.
- [ ] Either add smoking status as an effect modifier/variant, or explain its absence — it's the
  paper's own clinical hook (smoking-related stigma) but currently isn't tested anywhere despite
  being present in every note.
- [ ] Tighten the "guideline-endorsed" language around NCCN Distress Management screening — it
  endorses team-based screening and referral, not unprompted LLM insertion of
  financial-counseling language into a decision-support output. Current framing overreaches.
- [ ] Define "prognosis framing" operationally before continuing to score it inside the
  stigmatizing composite — discussing prognosis is core oncology practice and needs a clearer
  line between routine and stigmatizing framing.

---

## Minor / polish

- [ ] Fill in remaining `[PLACEHOLDER]` fields in `manuscript_nsclc_JAMA_NetworkOpen.md`:
  corresponding author, ORCID, running title, funder role, meeting presentation, eTable
  cross-reference.
- [x] (Resolved 2026-09-27: the collected-vs-analyzed split no longer exists; everything uses the
  28-variant, eight-category, six-axis framing. Figure 1B's BioRender graphic still shows an age
  axis and must be edited by hand.) Decide and state consistently whether "eight sociodemographic categories" / "six reporting
  axes" (analyzed, 28-variant framing) or "nine categories" / "seven axes" (collected, 30-variant
  framing) is being described wherever this appears — Figure 1B's legend still uses the
  30-variant framing intentionally (it describes the full collected panel), so this isn't
  necessarily an error, but a reviewer will read it as one unless it's labeled clearly as
  "collected" vs. "analyzed."
- [ ] Once the family-size fix above lands, make sure `manuscript_nsclc.md` and
  `manuscript_nsclc_JAMA_NetworkOpen.md` end up reporting the exact same final numbers
  (163/174-vs-134/174 and everything downstream of it).

- [x] **Gold-set items from the dropped age label.** 2 of the 60 representative gold items
  (r0004, r0034, both labeled NEUTRAL) were responses to the dropped age label. Resolved
  2026-09-27: excluded at scoring time in `run_bias_tree.py`, `score_random_gold_v2.py`, and
  `plots/plot_bias_tree.py` (Figure S6), not deleted from the packet files, so the second
  rater's copy is unaffected. Agreement on 58 items: regex 94.8% (κ 0.77, PABAK 0.90), judge
  91.4% (κ 0.57, PABAK 0.83), tree 93.1% (κ 0.68, PABAK 0.86); both manuscripts updated.
