# VALIDATION — Red-Team Adversarial Review (Paper 1 NSCLC)

_JMIR AI / BMC MIDM reviewer persona; generated against docs/paper1_nsclc/manuscript_nsclc.md._

# Peer Review: Kill-Shot Assessment

## 1. Demographic-injection salience artifact
**Quote:** *"Salience-artifact control (Fig 9c): injecting demographic information as a bracketed tag versus weaving it into natural prose produced statistically indistinguishable gradients for both Gemini (unhoused: +69pp tag vs. +74pp prose) and DeepSeek (unhoused: +76pp tag vs. +83pp prose)... ruling out demographic-label conspicuousness as the driver."*
**Ruling: ADEQUATELY DISCLOSED.** Real A/B natural-embedding control with numbers, not just an assertion. Weakness (not disqualifying): only 2 of 6 models, 150 of 1,048 cases — this scope limit is itself disclosed elsewhere but not re-flagged at this specific claim site.

## 2. Single-rater κ=0.30
**Quote:** *"Human-judge agreement was 71% (Cohen's kappa=0.30)... This single-rater validation, and the resulting fair (rather than substantial) agreement level, is a disclosed limitation."* Limitations section repeats it and adds a caveat that ordering is "more robust... but this has not been formally tested."
**Ruling: PARTIALLY DISCLOSED.** κ and single-rater status are disclosed prominently (even in the Results epigraph — good). **Missing:** no citation to Viera & Garrett or Hallgren to anchor "fair agreement" against a standard benchmark, and "2nd rater as future work" is stated as *not done* ("not possible within this study's scope") rather than committed as a concrete future-work plan with a method (blinding protocol, sample size). This is a citation-and-commitment gap, not a suppression — hence partial, not full credit.

## 3. Synthetic-note circularity
**Quote:** *"Three independent controls tested whether the stigma gradient reflected a property of model behavior... Circularity control (Fig 9a)... Real-note replication (Fig 9b): substituting 40 real, open-access PubMed Central NSCLC case reports..."*
**Ruling: ADEQUATELY DISCLOSED.** Both controls present, both cited in Limitations ("both address this concern directly... the strongest available evidence"), both run on 2 vendors with the scope caveat stated explicitly. This is the best-defended kill-shot in the manuscript.

## 4. Preregistration deviation
**Quote:** *"This panel deviates from the pre-registered five-model audit panel (PREREGISTRATION.md)... Claude Sonnet-4.6 was not run to completion due to API credit constraints... Llama-3.1-8B and GPT-4o-mini added as completed, non-preregistered exploratory arms."* Reiterated in Limitations with a robustness claim restricted to the 4 overlapping models.
**Ruling: ADEQUATELY DISCLOSED.** Disclosed in Methods *and* Limitations, reason given, and the authors correctly hedge by re-verifying the headline pattern on the pre-registered-and-complete subset only.

## 5. Unbalanced n / single-region / English-only scope
**Quote:** *"drawn from three academic cancer centers (MSK... DFCI... VICC...)"*; *"Race/ethnicity distribution... reflects the demographics of the contributing academic centers rather than the U.S. NSCLC population generally"*; Limitations: *"Single-institution-mix cohort... not a nationally representative sample."*
**Ruling: PARTIALLY DISCLOSED.** Institutional imbalance and non-representativeness are disclosed twice. **Not disclosed anywhere:** English-only note generation/scope (no mention that GENIE, PMC notes, or prompts are English-language-only, which matters directly for the "immigrant/limited-English" variant tier claiming null effects — an English-only pipeline cannot test that tier's real-world mechanism). This is a gap, not just thin coverage.

---

## Prioritized Fixes

### BLOCKING
1. **Precise stigma percentages stated in Results/Discussion without a hedge at point of use** — e.g., *"unhoused reaching d=1.43... the single largest effect... d=1.62"* and *"unhoused 81.8%... 83.7%"* are reported as fact-like figures in-line; only the Results section epigraph and Limitations carry the κ=0.30 caveat. **Fix:** append "(judge-adjudicated, κ=0.30; read as rank not magnitude)" inline at every headline percentage/d-value claim, not just in one disclaimer paragraph — reviewers will quote the number, not the epigraph.
2. **Missing reliability-statistic citation.** **Fix:** cite Viera & Garrett (2005) or Hallgren (2012) directly next to "fair agreement" so the qualitative label is externally anchored, not self-declared.
3. **English-only scope undisclosed.** **Fix:** add one Limitations sentence: "All notes (synthetic and PMC) are English-language only; the immigrant/limited-English-proficiency variants test a demographic label, not a language-access mechanism."

### MAJOR (non-blocking but must fix before acceptance)
4. **Reference 7 (NCCN guideline version) and Reference 8 (case-source) are unresolved placeholders** in a manuscript whose entire ground truth rests on the NCCN scorer — an editor will not accept with `[Author to insert...]` in the reference list. **Fix:** insert the exact NCCN NSCLC guideline version/date used for scoring before submission.
5. **Second-rater commitment is vague.** **Fix:** replace "not possible within this study's scope" with a concrete protocol stub (e.g., "a second blinded rater will re-annotate the full 35-item set plus an expanded 100-item set post-submission using the same STIGMA/APPROPRIATE/NEUTRAL schema").
6. **GPT-4o "appropriate-care displacement" anomaly** is interpreted (*"real but model-specific anomaly"*) from n=1 model — reads as post-hoc rationalization. **Fix:** soften to "cannot be distinguished from noise given single-model occurrence" rather than asserting a mechanism label.

### MINOR
7. Funding/author-contribution placeholders — fill before submission (editorial, not scientific).
8. Ref 14 (deployment vendor citations) placeholder — fill or cut the specific vendor claims in Introduction.