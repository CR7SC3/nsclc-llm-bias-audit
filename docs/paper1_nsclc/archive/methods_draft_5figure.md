<!--
DRAFT Methods section — JMIR AI style, aligned to the locked 5-figure architecture
(Fig 1 design; Fig 2 decision stability [4-panel v4]; Fig 3 SES-not-race;
Fig 4 stigma anatomy; Fig 5 robustness + precision filter).

NOT yet merged into manuscript_nsclc.md. Numbers carried over from the existing
Methods/Results; re-verify against results files (stats-verifier) before merge.
Figure-number mapping vs. the old interim numbering is noted in-line as <!-- was Fig N -->.
-->

## Methods

### Study Design

This was a counterfactual audit of six large language models' (LLMs) first-line
treatment recommendations and response framing on a real-world non–small-cell lung
cancer (NSCLC) cohort. Each clinical case was presented to each model in 30 versions
that differed only in a demographic label prepended to an otherwise identical,
demographics-neutral clinical note; all staging, histology, biomarker, and
performance-status information was held constant across the 30 versions of a given
case. Any systematic difference in a model's recommendation or narrative framing
across variants is therefore attributable to the demographic label alone
(counterfactual fairness [Kusner et al., 2017]). We separated two axes of bias a
priori: a **hard-bias** axis (whether the treatment decision changes) and a
**soft-bias** axis (whether the language framing changes). Figure 1 summarizes the
end-to-end workflow (Figure 1A) and the counterfactual variant design (Figure 1B).

Reporting follows the TRIPOD-LLM guidance for studies of generative language models
in health (completed checklist, Multimedia Appendix). Confirmatory outcomes and the
equivalence margin were specified before analysis (Preregistration, project
repository); analyses labeled exploratory are identified as such throughout.

### Ethical Considerations

This study used de-identified records available under data-use agreement from the
AACR Project GENIE Biopharma Collaborative (BPC) and did not involve identifiable
patient information or direct patient contact; it did not constitute human-subjects
research. The NCCN concordance scorer is a research instrument only and is explicitly
not validated for clinical or patient-facing use. No treatment decision in this study
affected a real patient.

### Data Source and Cohort

The primary cohort was 1,048 real, de-identified NSCLC cases from AACR Project GENIE
BPC (v2.0-public) [5,6], drawn from three academic cancer centers (Memorial Sloan
Kettering, n=556; Dana-Farber Cancer Institute, n=343; Vanderbilt-Ingram Cancer
Center, n=149). Inclusion criteria were an index NSCLC diagnosis, known AJCC stage,
and ≥1 documented first-line regimen. The cohort spanned Stage IV (n=594, 56.7%),
Stage III (n=251, 23.9%), and Stage I–II (n=203, 19.4%) disease; histology was
predominantly adenocarcinoma (n=884, 84.4%), with squamous (n=123, 11.7%) and
not-otherwise-specified (n=41, 3.9%) carcinoma. The race/ethnicity distribution
(Non-Hispanic White 79.1%, Asian/Pacific Islander 8.4%, Non-Hispanic Black 5.6%,
Hispanic/Latinx 1.8%, unknown/other 5.1%) reflects the contributing academic centers
rather than the U.S. NSCLC population. Cohort characteristics are summarized in Table 1.

GENIE BPC provides structured clinical and genomic fields, not free-text notes.
Biomarker status (EGFR, ALK, ROS1, BRAF, MET exon-14 skipping and amplification, KRAS
G12C, ERBB2 exon-20 insertion, RET, NTRK, STK11, KEAP1) was extracted from somatic
mutation, structural fusion, and copy-number files and mapped to each case's
sequencing panel; genes not covered by a given panel were coded `not_on_panel` rather
than negative, correcting a false-negative failure mode on narrower panels. PD-L1
tumor proportion score was resolved from pathology-report-level data for 377 patients
(36.0%); cases tested before routine PD-L1 testing (pre-2016) were coded untested,
reflecting real practice rather than missing data.

### Clinical Note Generation

Because GENIE BPC contains no free text, each structured case profile was converted
into a single demographics-neutral consultation note by `gemini-2.5-flash` (temperature
0), using de-identified CORAL oncology notes as style anchors only. The note-generation
prompt explicitly excluded any demographic content; demographic signal was introduced
exclusively in the downstream variant-injection step (below), so note construction and
demographic manipulation were fully decoupled. Two upstream controls (LLM-free template
notes and real published notes; Robustness Controls) confirm the findings are not an
artifact of this generation step.

### Counterfactual Variant Design

Thirty versions were created per case (Figure 1B): 29 demographic variants across nine
tiers plus a `no_demographics` neutral anchor. The tiers were (A) intersectional
race × insurance profiles (5 variants, including the `white_male_private` reference,
replicating Omar et al.'s design), (B) insurance status alone (5: uninsured, Medicaid,
Medicare, Medicare Advantage, underinsured), (C) race/ethnicity alone (6), (D) geography
(2: rural, small community hospital), (E) age (1: elderly, age 75), (F)
immigration/language (2), (G) socioeconomic status alone (3: unhoused, low-income,
high-income), (H) race × socioeconomic-status intersections (2), and (I) gender/sexual
identity (3). A single bracketed demographic label was prepended to the note (e.g.,
"[PATIENT DEMOGRAPHICS: Black female patient, Medicaid]"), with no narrative context
beyond the label itself, isolating the demographic signal from any confounding
narrative-style change. This yielded 1,048 × 30 = 31,440 queries per model.

### Models and Querying

Six LLMs from five model families were evaluated: Gemini-2.5-flash (Google),
DeepSeek-chat (DeepSeek), Llama-3.3-70B-Instruct-Turbo and Llama-3.1-8B-Instruct (Meta,
via Together AI and OpenRouter, respectively), and GPT-4o and GPT-4o-mini (OpenAI). All
models were queried at temperature 0 with an identical baseline
clinical-recommendation prompt across all 31,440 case × variant combinations, for
6 × 31,440 = 188,640 model responses. Calls were checkpointed after every response and
resumed automatically on interruption. Model versions, endpoints, and the full prompt
are given in the Multimedia Appendix. Two robustness controls (template notes and
real-note replication) were run on Gemini and DeepSeek only, owing to per-call cost
across the full six-vendor grid; this scope is disclosed rather than presented as
six-vendor representativeness.

### Outcome Measures

Every response was scored on the hard-bias (decision) and soft-bias (framing) axes.

**Hard bias — treatment-recommendation flip rate (confirmatory).** The proportion of
cases in which a variant's parsed treatment category differed from the `no_demographics`
reference, with Wilson 95% CIs. Averaged across the six models, the flip rate is
invariant to demographic content — every variant, and the privileged
`white_male_private` reference, perturbs the recommendation by the same ~17% test–retest/
label-salience floor (Figure 2B). <!-- was Fig 5 dissociation left -->

**Hard bias — NCCN guideline concordance (confirmatory).** NCCN Category 1 concordance
was tested for statistical equivalence between the no-demographics reference and each
demographic variant using two one-sided tests (TOST) on the paired treatment-tier shift
(Cohen's d), with a pre-specified equivalence margin of d = ±0.10; equivalence was
declared only when the tier-shift 95% CI lay entirely within the margin, not on a mere
failure to reject a null of no difference (Figure 2A). <!-- was Fig 4 -->

**Hard bias — directional decision test (confirmatory).** Among cases whose treatment
category changed, a signed treatment-aggressiveness-tier shift (1 = best supportive
care … 8 = surgical resection) was tested with a paired sign test (downgrade vs.
upgrade), corrected with a single grid-wide Benjamini-Hochberg (BH) false-discovery-rate
procedure across the full model × variant family (6 models × 29 non-reference variants =
174 tests). The per-model, per-variant net tier shift is shown in Figure 2C.

**Hard bias — care-intensity direction (exploratory).** As a directional sub-analysis
of treatment intensity, we computed the per-vendor net change, relative to the
reference, in whether a response mentioned a clinical trial (advanced treatment) or
palliative/best-supportive care (de-escalation), never pooled across vendors (Figure 2D).
No individual vendor effect is BH-significant; the panel reports directional consistency
across vendors (k/6 count) and is interpreted as an exploratory tilt, not a decision change.

**Soft bias — framing intensity and appropriate/stigmatizing decomposition
(secondary).** A continuous soft-framing intensity score was computed per response from
eight linguistic dimensions (financial-barrier language, social-work referral,
specialist/multidisciplinary referral, clinical-trial mention, adherence/compliance
doubt, unprompted social-determinants-of-health [SDOH] generation, prognosis framing,
watchful-waiting), each detected by a keyword/pattern classifier and adjudicated by an
LLM judge (Claude Sonnet-4.6). A ninth dimension (palliative/best-supportive-care
framing) was detected but excluded from the composite, as it fires on clinically
appropriate end-of-life discussion independent of demographic framing. Consistent with
NCCN guidance that financial-counseling and social-work referral are appropriate
responses to disclosed socioeconomic barriers, the eight dimensions were partitioned a
priori into a **stigmatizing** composite (adherence/compliance doubt, prognosis framing,
unprompted SDOH generation, watchful-waiting) and an **appropriate** composite
(financial-barrier language, social-work referral, specialist referral, clinical-trial
mention). Each composite's net percentage (cases adding the framing minus cases removing
it, vs. reference) was tested with a paired sign test, BH-FDR-corrected within its own
family (Figure 4A, 4B). Per-variant, per-model effect sizes (Cohen's d) for the
continuous score against the reference localize the framing shift to socioeconomic
rather than racial axes (Figure 3A, 3C). <!-- was Figs 6, 7 -->

**Soft bias — dose-response trend (secondary).** To test whether the stigmatizing-rate
gradient across disadvantage strata (Figure 4C) is monotone rather than visually
suggestive, a Cochran-Armitage trend test was applied per model across the five ordered
socioeconomic-disadvantage strata (control < uninsured < underinsured < low-income <
unhoused), with ordinal tier scores 0–4. Race-only carries no socioeconomic disadvantage
and was excluded from the ladder, instead compared to control directly. <!-- was Fig 8 -->

**Cross-model agreement (secondary).** To assess whether the dissociation reflects a
shared demographic-response mechanism rather than one model's idiosyncrasy, the
29-variant induced soft-framing-effect vector (Cohen's d per variant) was compared
pairwise across the six models with Spearman rank correlation (Figure 3B).

### Judge Validation

Following precedent for LLM-based detection of stigmatizing clinical language at scale
[12], the classifier and judge were validated against human gold labels on two sets. The
primary *representative* set was 60 responses drawn uniformly at random (seed 17) from
the Gemini and DeepSeek arms — preserving the natural ~10% stigma prevalence — labeled by
the study author (single rater), blinded to variant, into STIGMA/APPROPRIATE/NEUTRAL and
binarized to STIGMA vs. not. Judge–human agreement was 91.7% (κ = 0.57, PABAK 0.83),
regex–human 95.0% (κ = 0.77, PABAK 0.90), and decision-tree–human 93.3% (κ = 0.68, PABAK
0.87). At ~10% prevalence (6–9 STIGMA items), κ point estimates are base-rate-fragile and
cannot rank the instruments; raw agreement and PABAK are the stable reportable
quantities. A second *enriched* set of 35 classifier-flagged items supplied the
over-counting evidence: on the 17 items where regex and judge disagreed, the human sided
with the judge in 12/17, indicating the regex classifier systematically over-counts
stigma. All reported stigma rates use judge-adjudicated labels. Both sets were
single-rater; a second blinded rater is pending, a disclosed limitation.

### Bias Decision-Tree Precision Filter

To test whether the stigma signal survives a stricter, grounding-aware definition, each
regex-flagged response was routed through a deterministic bias decision-tree
(`src/analyze/bias_tree.py`) rendering the human adjudication rubric as an explicit gate
cascade: Gate 0, does any adherence/SDOH pattern fire (this gate *is* the regex
composite, so tree recall is bounded by regex — it can only reclassify flagged responses,
never recover a missed stigma); Gate 1, is the framing a negative assumption rather than
supportive language; Gate 2, is the concern grounded in the clinical note itself (or in
generic all-patients counseling) rather than in the demographic label alone; Gate 3, does
it impute an invented individual defect rather than offer a pure resource. The central
rule is that **a demographic label is never, by itself, clinical grounding**. Responses
surviving all gates are labeled STIGMA and assigned a descriptive harm subtype
(allocative, epistemic-injustice, or dignitary). The tree is a precision-and-
interpretability cross-check, not the primary detector; headline stigma rates remain the
judge-adjudicated regex composite (Figure 5D). <!-- was bias-tree Results -->

### Robustness Controls

Three controls tested whether the gradient was an artifact of the note-generation or
injection pipeline rather than model behavior (Gemini and DeepSeek). **(1) LLM-free
template-note replication** (Figure 5A): cases were re-notated with fully deterministic,
non-LLM string templates in place of the generated free-text notes and re-run through the
full 30-variant pipeline, ruling out circularity from LLM note generation. **(2) Real
clinical-note replication** (Figure 5B): 40 open-access PubMed Central NSCLC case reports
were substituted for the synthetic notes and re-run through the same pipeline; the
gradient's direction was preserved on genuine clinical prose, with magnitude attenuated
at this small sample (n=40). **(3) Natural-embedding salience control** (Figure 5C): for
150 cases, demographics were injected either as the standard bracketed tag or woven into
natural prose, testing whether the gradient depended on the conspicuousness of the
demographic signal rather than its content; the gradient survived both injection modes.

### Statistical Analysis

Analyses were implemented in Python (scipy, pandas). Wilson score CIs were used
throughout for proportions given values near 0 and 1 at moderate sample sizes. Because
the design is repeated-measures, each case contributes several responses to the pooled
race-only (six variants) and control (two variants) strata; per-stratum stigma rates were
re-estimated with a case-clustered percentile bootstrap (10,000 resamples, resampling on
the case) to confirm the Wilson intervals were not anticonservative under within-case
correlation. Clustered and Wilson 95% intervals agreed to within 0.2 percentage points
for every model and stratum (Supplementary Table S4). Grid-wide BH-FDR correction was
applied once across each metric family (not per-model or per-figure) to avoid understating
the multiple-comparisons burden. Model averages for the flip-rate panel (Figure 2B) are
the mean of the six per-model rates with 95% CIs across models.

### Reproducibility

The complete pipeline — case construction, variant injection, multi-model querying,
soft-bias/stigma detection, statistical analysis, and figure generation — is available in
the project repository, with per-call checkpointing for exact re-execution. Confirmatory
outcomes and the equivalence margin were specified in advance (Preregistration).
