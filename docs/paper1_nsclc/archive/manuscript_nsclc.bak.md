# Stigma Without Downgrade: Separating Warranted Socioeconomic Responsiveness From Generated Stigma in Large Language Model Cancer-Treatment Recommendations

**A Counterfactual Audit of Six Large Language Models on 1,048 Real-World Non-Small-Cell Lung Cancer Cases**

---

## Abstract

**Background:** Large language models (LLMs) are increasingly embedded in oncology through
ambient clinical scribes and EHR-integrated drafting tools. Prior bias audits typically
score only whether an LLM's final treatment recommendation changes with patient
demographics, potentially missing bias that appears instead in the surrounding clinical
narrative.

**Objective:** To determine, in a large real-world non-small-cell lung cancer (NSCLC)
cohort, whether LLM treatment recommendations change with demographic framing (decision
bias), whether the surrounding narrative changes independently (framing bias), and whether
any framing bias reflects warranted socioeconomic responsiveness, stigmatizing assumptions,
or both.

**Methods:** From 1,048 real, de-identified NSCLC cases (AACR Project GENIE BPC
v2.0-public) we built demographics-neutral clinical notes and generated 30 demographic
variants each (race, insurance, socioeconomic status, gender/identity, plus a
no-demographics reference), holding clinical facts constant. Six LLMs (Gemini-2.5-flash,
DeepSeek-chat, Llama-3.3-70B, Llama-3.1-8B, GPT-4o, GPT-4o-mini) were queried at temperature
0 across all case-by-variant combinations. Outcomes were treatment flip rate, NCCN
concordance (tested for equivalence, TOST), and a soft-framing intensity score decomposed
into stigmatizing (unprompted adherence-doubt, hallucinated social-determinants content)
versus appropriate (NCCN-endorsed financial-counseling/social-work language) components,
each tested with paired sign tests and grid-wide Benjamini-Hochberg (BH) correction (174
model-by-variant comparisons). Stigma labels were adjudicated by an LLM judge (judge–human
agreement 91.7%, PABAK 0.83 on a random n=60 sample; single rater, second pending) and
cross-validated by a deterministic, grounding-aware bias decision-tree (tree–human κ=0.68).
Robustness was assessed on LLM-free template notes, 40 real PubMed Central case reports, and
a natural-prose embedding control.

**Results:** NCCN concordance was statistically equivalent between reference and variants
for most models (29/29 variants for Llama-3.3-70B, Llama-3.1-8B, and GPT-4o; 27/29
DeepSeek-chat; 26/29 GPT-4o-mini; 14/29 Gemini-2.5-flash; deltas -1.0 to +1.1 points). Mean
flip rates ranged 11.7% (GPT-4o) to 22.1% (GPT-4o-mini), and only two of 174 directional
decision tests survived BH correction (both DeepSeek-chat socioeconomic-disadvantage cells).
Between this invariant decision and the language-framing signal sat an intermediate
care-intensity layer: holding the regimen fixed, marginalized-patient notes received fewer
clinical-trial mentions and more de-escalation framing, small in magnitude but directionally
consistent across vendors (mixed-effects, random intercept per model: advanced treatment -1.4
percentage points, 95% CI -2.3 to -0.5, p=0.002; de-escalation +1.1, 95% CI 0.2 to 2.0,
p=0.016), and, unlike the framing signal, this layer was affected by race as well as
socioeconomic status. In contrast, stigmatizing-framing effect sizes showed a consistent
socioeconomic gradient across all six models: race-only variants averaged
Cohen's d=-0.03 to 0.10 (small), while socioeconomic-disadvantage variants averaged d=0.26
to 1.16 (unhoused reaching d=1.43; the largest single effect, d=1.62, for intersectional
latina_female_uninsured in Gemini-2.5-flash). The gradient replicated on template notes,
real PubMed Central notes, and under natural-prose embedding.

**Conclusions:** Demographic framing left guideline-concordant decisions largely stable but
reshaped the narrative in a pattern that, in the language-framing channel, tracked
socioeconomic disadvantage rather than race, independent of note-generation artifacts (race
did contribute to the intermediate care-intensity layer). Audits scoring only the final
recommendation may substantially underestimate bias operating through narrative framing and
care-intensity emphasis; decomposing framing into appropriate SDOH-responsive versus
stigmatizing content is necessary to separate legitimate care coordination from a harmful
stigma signal.

**Keywords:** large language models; artificial intelligence; health equity; algorithmic
bias; clinical decision support; oncology; social determinants of health; stigma


---

## Introduction

Large language models (LLMs) are moving from experimental use into the oncology
workflow itself. Ambient clinical-documentation systems (e.g., Nuance DAX, Abridge) and
electronic health record (EHR)-integrated drafting assistants (e.g., Epic's integration
of GPT-4o for inbox-message drafting) already generate free-text content that is reviewed,
lightly edited, and filed into the permanent medical record at scale. This creates a
documentation-integrity and medico-legal exposure that is distinct from the harm most bias
audits are designed to detect: the risk is not necessarily that an LLM recommends the
wrong regimen, but that a deployed system silently inserts an unwarranted assumption
("patient may have difficulty adhering to treatment," a fabricated housing instability, an
unprompted note about affordability) into the chart of a disadvantaged patient, where it
persists as documented fact for every subsequent clinician who reads that note. This concern
has a direct precedent in the human-clinician literature: stigmatizing language written by
one clinician measurably worsens the attitudes and clinical decisions of the next clinician
who reads that chart [9], and a growing body of work has characterized how frequently such
language appears across clinical note types and how unevenly it is distributed by patient
race and substance-use history [10,11].

Whether LLMs used for medical decision support introduce or amplify such disparities is an
active concern. Omar et al. [1] evaluated nine LLMs across 1,000 emergency-department
cases (500 real, 500 synthetic), each presented in 32 sociodemographic variations, and
reported that cases labeled Black, unhoused, or LGBTQIA+ were directed toward more urgent
or invasive care pathways than a matched no-demographics control. A systematic review of
demographic-bias studies in medical LLMs found that the large majority of included studies
(22 of 24, 91.7%) identified some form of bias, with gender bias reported in 15 of 16
studies and racial/ethnic bias in 10 of 11 [2]. That near-universal "finds bias" result
is itself a methodological problem: a literature in which almost every audit reports bias
against some final-decision metric offers little guidance on which bias mechanisms matter,
which are addressable, and which reflect defensible clinical judgment rather than harm.

Two features of this literature limit what it can tell us, and both stem from where the
measurement is aimed. Most audits score the final decision rather than the language that
carries it, yet a treatment recommendation and the narrative wrapped around it are distinct
outputs with distinct downstream consequences. A recommendation can remain perfectly stable
while arriving with an added, unprompted note questioning a patient's adherence, or a
fabricated claim about their housing; that language does harm on its own terms,
propagating into future encounters, regardless of whether the underlying recommendation
ever changed. An audit that asks only whether the final treatment category flips will
systematically miss this framing-level harm, and will understate the bias that a deployed
ambient-documentation or inbox-drafting system would actually write into a chart.

Even the rarer audits that do reach narrative-level ("soft") bias tend to collapse it into
a single undifferentiated composite, as though all differential language directed at
socioeconomically disadvantaged patients were equally suspect, and it is not. NCCN
guidelines explicitly endorse addressing financial barriers and connecting uninsured or
low-income patients to social work and financial-counseling resources, so raising these for
a patient whose note discloses insurance or housing instability is warranted,
guideline-concordant care rather than bias. Folding that appropriate responsiveness
together with unprompted adherence-doubt or hallucinated social-determinants-of-health
(SDOH) content not only overstates the harm but, more consequentially, leaves a health
system with no way to know what to filter. To our knowledge, no prior audit has separated
socioeconomic responsiveness into an appropriate-care component and a distinct, genuinely
stigmatizing one and asked whether the two behave differently.

This study addresses both limitations using a single design: a large, real-world oncology cohort,
a counterfactual demographic-variant injection structurally similar to the Omar et al.
paradigm, six LLMs from five model families, and an explicit decomposition of narrative
framing into appropriate-care and stigmatizing components, each independently tested for a
socioeconomic-disadvantage gradient and a race-only null. We ask three questions. (1) Does
demographic framing change the LLM's treatment recommendation for non-small-cell lung
cancer (NSCLC), tested against a pre-registered equivalence margin rather than a simple
failure to reject the null? (2) Does demographic framing change the surrounding narrative
independent of the recommendation, and if so, is that change driven by race or by
socioeconomic disadvantage? (3) When narrative framing does change, how much of that change
is clinically defensible SDOH-responsive care, and how much is a separable, stigmatizing
signal, and does that stigmatizing signal survive replication on notes the audited models
did not themselves generate?

We position this work against three related lines of inquiry. Omar et al.'s [1]
emergency-department paradigm established the counterfactual demographic-injection method
this study extends to a guideline-anchored oncology setting; where their intersectional
urgency effects span multiple sociodemographic axes, our design isolates whether an
oncology-specific, NCCN-anchored ground truth reproduces a similar pattern and, if so,
whether it is attributable to race or to socioeconomic status specifically. A separate line
of work on socioeconomic status and clinical-trial-screening language [3] has reported "soft"
SES effects as a monolithic harm signal across a large ensemble of models and trial
protocols; we show, using the appropriate/stigmatizing decomposition below, that this signal
is mostly appropriate, guideline-endorsed care once decomposed, with a smaller stigmatizing
residue. Finally, work on stigmatizing language inherited from clinician-authored input text
[4] differs from our finding in mechanism: that work shows LLMs inherit and amplify
stigmatizing language already present in a clinical note, whereas the stigmatizing content
in this study is generated unprompted by the LLM from a bare demographic label added to a
note that, by construction, contained no such content beforehand.

---

## Methods

### Study Design

This is a counterfactual audit of six LLMs' treatment recommendations and response
framing on a real-world oncology cohort. Each clinical case is presented to each model in
30 versions that differ only in a demographic label prepended to an otherwise identical,
demographics-neutral clinical note; all staging, histology, biomarker, and performance
status information is held constant across all 30 versions of a given case. Any
systematic difference in the model's recommendation or narrative framing across variants
is attributable to the demographic label alone. Figure 1 summarizes the end-to-end
study workflow, and Figure 2 the counterfactual variant design.

### Data Source and Cohort

The primary cohort is 1,048 real, de-identified non-small-cell lung cancer (NSCLC) cases
from the AACR Project GENIE Biopharma Collaborative (v2.0-public) [5,6], drawn from three
academic cancer centers (Memorial Sloan Kettering \[MSK\], n=556; Dana-Farber Cancer
Institute \[DFCI\], n=343; Vanderbilt-Ingram Cancer Center \[VICC\], n=149). Inclusion
criteria were an index NSCLC diagnosis, known AJCC stage, and at least one documented
first-line treatment regimen. The cohort spans Stage IV (n=594, 56.7%), Stage III (n=251,
23.9%), and Stage I-II (n=203, 19.4%) disease; histology is predominantly adenocarcinoma
(n=884, 84.4%) with squamous (n=123, 11.7%) and not-otherwise-specified (n=41, 3.9%)
carcinoma. Race/ethnicity distribution (Non-Hispanic White 79.1%, Asian/Pacific Islander
8.4%, Non-Hispanic Black 5.6%, Hispanic/Latinx 1.8%, unknown/other 5.1%) reflects the
demographics of the contributing academic centers rather than the U.S. NSCLC population
generally.

GENIE BPC provides structured clinical and genomic fields, not free-text clinical notes.
Biomarker status (EGFR, ALK, ROS1, BRAF, MET exon 14 skipping and amplification, KRAS
G12C, ERBB2 exon 20 insertion, RET, NTRK, STK11, KEAP1) was extracted from somatic
mutation, structural fusion, and copy-number files and mapped to each case's sequencing
panel; genes not covered by a given panel were coded `not_on_panel` rather than negative,
correcting a false-negative failure mode on narrower panels (e.g., an 11-panel gene-list
lookup covering panels from 31 to 468 genes). PD-L1 tumor proportion score (TPS) was
resolved from pathology-report-level data for 377 patients (36.0%); an additional cohort
tested prior to the era of routine PD-L1 testing (pre-2016) is coded as untested,
reflecting real clinical practice rather than missing data.

Each structured case profile was converted into a demographics-neutral free-text
consultation note by `gemini-2.5-flash`, using de-identified CORAL oncology notes as
style anchors only; the note-generation prompt explicitly excludes any demographic
content, which is added exclusively in the subsequent variant-injection step.

### Counterfactual Variant Design

Thirty demographic variants were injected per case across nine tiers: (A) intersectional
race x insurance profiles (5 variants, including the `white_male_private` reference
variant, replicating Omar et al.'s design), (B) insurance status alone (5 variants:
uninsured, Medicaid, Medicare, Medicare Advantage, underinsured), (C) race/ethnicity alone
(6 variants), (D) geography (2 variants: rural, small community hospital), (E) age (1
variant: elderly, age 75), (F) immigration/language (2 variants), (G) socioeconomic status
alone (3 variants: unhoused, low-income, high-income), (H) race x socioeconomic status
intersections (2 variants), and (I) gender/sexual identity (3 variants), 29 variants in
total across tiers A-I, plus the `no_demographics` neutral-anchor control, for 30 total. For unstructured notes, a single bracketed
demographic label was prepended to the note (e.g., "\[PATIENT DEMOGRAPHICS: Black female
patient, Medicaid\]"); no narrative context beyond the label itself was added, isolating
the demographic signal from any confounding narrative style change.

### Models

Six LLMs from five model families were evaluated: Gemini-2.5-flash (Google), DeepSeek-chat
(DeepSeek), Llama-3.3-70B-Instruct-Turbo and Llama-3.1-8B-Instruct (Meta, via Together AI
and OpenRouter respectively), GPT-4o and GPT-4o-mini (OpenAI). All models were queried at
temperature 0 with an identical baseline clinical-recommendation prompt across all 1,048
cases x 30 variants (31,440 calls per model); results were checkpointed after every call
and resumed automatically on interruption. Two robustness controls (LLM-free deterministic
template notes and real PubMed Central case-report replication, below) were run on Gemini
and DeepSeek only, due to per-call cost constraints across the full 6-vendor grid; this
scope limitation is disclosed here rather than presented as a claim of representativeness
across all six vendors for those two controls.

### Ground Truth

NCCN Category 1 treatment concordance was determined by a deterministic decision-tree
scorer encoding the NCCN NSCLC guideline [7] (stage, histology, ECOG performance status,
resectability, and the biomarker cascade EGFR/ALK/ROS1/BRAF/MET/RET/NTRK/PD-L1, in
priority order), returning the full set of NCCN-acceptable first-line regimens for each
case rather than a single answer, since multiple Category 1-equivalent options exist for
many biomarker profiles (e.g., three ALK inhibitors, or pembrolizumab monotherapy versus
chemoimmunotherapy for high-PD-L1 Stage IV disease). A response was scored concordant if
its parsed treatment category matched any entry in the case's acceptable-answer set. This
scorer requires validation by a board-certified oncologist before any clinical or
patient-facing use and is presented here strictly as a research ground-truth instrument;
NCCN guidelines are updated multiple times per year and the encoded logic reflects
guideline versions current as of mid-2026.

### Outcome Measures

**Primary: treatment-recommendation flip rate.** The proportion of cases where a
variant's parsed treatment category differs from the `no_demographics` reference,
reported with Wilson 95% confidence intervals.

**Primary: NCCN guideline concordance.** Tested for statistical equivalence between the
no-demographics reference and each demographic variant using two one-sided tests (TOST)
on the paired treatment-tier shift (Cohen's d), with a pre-specified equivalence margin of
d=±0.10; equivalence is declared only when the tier-shift 95% CI lies entirely within this
margin, not merely on a failure to reject a null of no difference.

**Primary: directional decision test.** Among cases where the treatment category
changed, a signed treatment-aggressiveness-tier shift (1=best supportive care to 8=surgical
resection) was tested with a paired sign test (downgrade vs. upgrade), correcting for
multiplicity with a single grid-wide Benjamini-Hochberg (BH) false discovery rate procedure
across the full model x variant family (6 models x 29 non-reference variants = 174 tests),
not per-model or per-metric families.

**Secondary: soft-framing intensity and appropriate/stigmatizing decomposition.** A
continuous soft-framing intensity score was computed per response from eight linguistic
dimensions (financial-barrier language, social-work referral, specialist/multidisciplinary
referral, clinical-trial mention, adherence/compliance doubt, unprompted
social-determinants-of-health \[SDOH\] generation, prognosis framing, and watchful-waiting
suggestion), each detected via a keyword/pattern classifier and adjudicated by an LLM judge
(Claude Sonnet-4.6). A ninth dimension (palliative/best-supportive-care framing) is
detected by the same classifier but excluded from this composite because it fires on
clinically appropriate end-of-life discussion independent of demographic framing and was
not part of the pre-registered stigmatizing/appropriate partition. Consistent with NCCN guidance that financial-counseling and
social-work referral are appropriate, guideline-endorsed responses to disclosed
insurance/socioeconomic barriers, the eight dimensions were partitioned a priori into a
**stigmatizing** composite (adherence/compliance doubt, prognosis framing, unprompted SDOH
generation, watchful-waiting) and an **appropriate** composite (financial-barrier
language, social-work referral, specialist referral, clinical-trial mention). Each
composite's net percentage (proportion of cases where the variant response added the
framing relative to the reference, minus the proportion where it was removed) was tested
with a paired sign test and BH-FDR corrected within its own family across all model x
variant cells. Effect sizes (Cohen's d) for the continuous soft-framing score were computed
per variant per model against the no-demographics reference.

**Secondary: dose-response trend test.** To test formally whether the stigmatizing-rate
gradient across disadvantage strata (Figure 5C) is monotone rather than merely visually
suggestive, a Cochran-Armitage trend test was applied per model across the five ordered
socioeconomic-disadvantage strata (control < uninsured < underinsured < low-income <
unhoused), using ordinal tier scores 0-4 as the trend variable. Race-only was excluded from
the ladder (it carries no socioeconomic disadvantage) and instead compared to control
directly, as in the primary race-only-vs-SES effect-size analysis above.

**Secondary: cross-model agreement.** To assess whether the reported dissociation
reflects a shared demographic-response mechanism rather than idiosyncratic behavior of one
model, the 29-variant induced soft-framing-effect vector (Cohen's d per variant) was
compared pairwise across all six models using Spearman rank correlation.

### Judge Validation

Following precedent for LLM-based detection of biased/stigmatizing language at scale in
clinical text [12], the keyword/pattern classifier and the LLM judge were validated against
human gold labels along two axes. The primary, *representative* gold set comprised 60
responses drawn uniformly at random (seed 17) from the Gemini and DeepSeek arms — preserving
the natural stigma prevalence (~10%) — labeled by the study author (single rater) blinded to
demographic variant into STIGMA / APPROPRIATE / NEUTRAL, then binarized to STIGMA vs.
not-STIGMA. On this representative set, judge–human agreement was 91.7% (Cohen's kappa=0.57,
PABAK 0.83), regex–human agreement was 95.0% (kappa=0.77, PABAK 0.90), and the
deterministic bias decision-tree (below)–human agreement was 93.3% (kappa=0.68, PABAK 0.87).
At the observed ~10% prevalence, with only 6–9 items in the STIGMA cell, the kappa point
estimates are base-rate–fragile (a single disagreement shifts kappa by ~0.10) and cannot
statistically rank the three instruments; raw agreement and PABAK are therefore the stable,
reportable quantities. A second, *enriched* gold set of 35 classifier-flagged (contested) items
supplies the over-counting evidence: on the 17 items where the regex classifier and judge
disagreed, the human rater sided with the judge in 12/17 cases (judge–human kappa=0.30,
regex–human kappa=0.21 on this enriched, harder set), indicating the regex classifier
systematically over-counts stigma. All reported stigma rates use judge-adjudicated labels.
Both gold sets were labeled by a single rater; a second independent blinded rater
(RANDOM60 gold sheets are prepared) is pending, and this single-rater validation is a
disclosed limitation (see Limitations) rather than a resolved validation.

### Bias Decision-Tree Precision Filter

To test whether the regex composite's stigma signal survives a stricter, grounding-aware
definition of stigma, each regex-flagged response was additionally routed through a
deterministic bias decision-tree (`src/analyze/bias_tree.py`; method write-up
`docs/bias_tree_method.md`) that renders the human adjudication rubric
(`decision_tree_rubric.md`; counterfactual fairness, Kusner et al. 2017) as an explicit
gate cascade: Gate 0, does any adherence/SDOH pattern fire (this gate *is* the regex
composite, so the tree's recall is bounded by the regex — it can only reclassify flagged
responses, never recover a stigma the regex missed); Gate 1, is the framing a negative
assumption (an adherence/reliability doubt, an asserted SDOH barrier, or treatment weakened
for a social reason) rather than supportive language; Gate 2, is the concern grounded in the
clinical note itself or in generic all-patients (regimen-universal) counseling; and Gate 3,
does it impute an invented *individual* defect rather than offer a pure resource. The central
rule is that **a demographic label is never, by itself, clinical grounding** — grounding is
checked against the note only, so "given the patient is unhoused, adherence may be
challenging" is not grounded merely because "unhoused" was the injected label. Responses
surviving all gates are labeled STIGMA and further assigned a descriptive harm subtype
(allocative, epistemic injustice, or dignitary). The tree is a precision-and-interpretability
instrument, not the primary detector: all headline stigma rates in this manuscript remain the
judge-adjudicated regex composite, and the tree is reported only as a discriminant-validity
cross-check and harm-type decomposition (Results; the harm subtypes are descriptive and
unvalidated — see Limitations).

### Robustness Controls

Three controls tested whether the stigma gradient was an artifact of the note-generation
or demographic-injection pipeline rather than a property of model behavior. **(1) LLM-free
template-note replication:** a subset of 100 cases (Gemini and DeepSeek only) was
re-notated using fully deterministic, non-LLM string templates in place of the
gemini-2.5-flash-generated free-text notes, and re-run through the full 30-variant
pipeline. **(2) Real clinical-note replication:** 40 open-access PubMed Central NSCLC case
reports (Gemini and DeepSeek only) were substituted for the GENIE-derived synthetic notes
and re-run through the same variant-injection and stigma-detection pipeline. **(3)
Natural-embedding salience control:** for a subset of 150 cases, demographic information
was injected either as the standard bracketed tag (e.g., "\[PATIENT DEMOGRAPHICS:
...\]") or woven into natural prose within the note body, to test whether the stigma
gradient depended on the conspicuousness of the demographic signal rather than its
content.

### Statistical Software and Reproducibility

All analyses were implemented in Python (scipy, pandas) and are reproducible from the
project repository (`scripts/nsclc/analyze_results_v2.py`, `scripts/nsclc/
correct_analysis.py`, `plots/plot_circularity_ci.py`, `plots/plot_pmc_replication.py`).
Wilson score confidence intervals were used throughout for proportions (rather than the
normal approximation) given proportions near 0 and 1 at moderate sample sizes. Because
the design is repeated-measures, each case contributes several responses to the pooled
race-only (six variants) and control (two variants) strata, so per-stratum stigma rates
were additionally re-estimated with a case-clustered percentile bootstrap (10,000
resamples, resampling on the case rather than the response;
`scripts/nsclc/bootstrap_panel_ci.py`) to confirm the Wilson intervals were not
anticonservative under within-case correlation. Clustered and Wilson 95% intervals
agreed to within 0.2 percentage points for every model and stratum (Supplementary Table
S4, `results/analysis/panel_stigma_rates_clustered.csv`), including the pooled strata, so
the Wilson intervals are reported. Grid-wide BH-FDR correction was applied once across
each metric family described above, not per-model or per-figure, to avoid understating
the effective multiple-comparisons burden.

### Ethical Considerations

This study used de-identified, publicly-available-under-data-use-agreement GENIE BPC
records and did not involve identifiable patient information or direct patient contact.
The NCCN concordance scorer is a research instrument only and is explicitly not validated
for clinical or patient-facing use. No treatment decisions in this study affected real
patients.

---

## Results

*All stigmatizing-language rates and net% figures reported below are judge-adjudicated
labels, validated against single-rater human gold labels (representative random sample,
n=60: 91.7% judge–human agreement, PABAK 0.83; Cohen's kappa base-rate–limited; see
Methods). They should be read as an internal comparison across variants and models within
this design, not as precise absolute measurements.*

### Table 1. Cohort Description

The audited cohort comprised 1,048 real, de-identified NSCLC cases from three GENIE BPC
academic centers (MSK 53.1%, DFCI 32.7%, VICC 14.2%). Stage distribution was IV 56.7%
(n=594), III 23.9% (n=251), and I-II 19.4% (n=203); histology was adenocarcinoma 84.4%
(n=884), squamous 11.7% (n=123), and not-otherwise-specified 3.9% (n=41). Race/ethnicity
was 79.1% Non-Hispanic White, 8.4% Asian/Pacific Islander, 5.6% Non-Hispanic Black, 1.8%
Hispanic/Latinx, and 5.1% other/unknown, reflecting the demographics of the contributing
academic centers. Actionable driver mutations were present in 43% of cases (EGFR n=224,
KRAS G12C n=116, ALK n=42, MET exon 14 n=22, ROS1 n=19, RET n=14, BRAF n=11, NTRK n=2);
PD-L1 TPS was available for 36.0% (377/1,048) of the cohort, with the remainder
untested, predominantly reflecting sequencing performed before PD-L1 testing became
routine (full breakdown in Supplementary Figure S1).

### Demographic Framing Leaves the Treatment Decision Largely Stable While Reshaping Its Narrative (Figures 2 and 4)

Across all six models, the treatment-recommendation flip rate relative to the
no-demographics reference did not vary systematically across the 29 demographic variants;
every variant's flip rate for a given model overlapped that model's own mean flip rate
across all variants (Figure 2B). Mean flip rates ranged from 11.7% (GPT-4o) to 22.1%
(GPT-4o-mini), with intermediate rates for DeepSeek-chat (13.3%), Llama-3.3-70B (14.5%),
Llama-3.1-8B (17.5%), and Gemini-2.5-flash (19.7%), a range consistent with each model's
baseline decision-instability floor rather than a demographic-specific effect.

In sharp contrast, the added soft-framing intensity of each response (Cohen's d in
framing score, relative to the no-demographics reference) fanned out systematically by
socioeconomic tier within every model (Figure 4C): race-only and no-demographics-adjacent
variants clustered near d=0, while socioeconomic-disadvantage variants (unhoused,
underinsured, uninsured, low-income) showed materially larger effect sizes, with the
largest single effect reaching d=1.62 (Gemini-2.5-flash, latina_female_uninsured;
underinsured_only alone reached d=1.55 in the same model). This
dissociation, a stable decision paired with demographically-patterned narrative
framing, is the central empirical pattern this study reports.

### Care-Intensity Emphasis Shifts Against Marginalized Patients, an Intermediate Layer Between the Invariant Decision and the Framing Signal (Figure 3)

Between the discrete guideline-concordant decision (unchanged) and the language-framing
signal (below) lies an intermediate layer: which treatment options a response foregrounds,
holding the primary regimen fixed. We scored, per response, whether it mentioned a clinical
trial (advanced treatment) or palliative/best-supportive care (de-escalation), as a
within-case net change versus the no-demographics reference; reduced trial mention and
increased de-escalation under a marginalization label were defined a priori as the harm
direction. Because the six vendors are correlated, we tested this with a linear mixed-effects
model carrying a random intercept per model, fit on the per-(variant x model) aggregate cells
so that neither the 1,048 cases nor the six vendors are treated as independent trials. Pooled
across the marginalized variants, model responses shifted a small but statistically robust
amount in the harm direction: advanced treatment -1.4 percentage points (95% CI -2.3 to -0.5;
p=0.002) and de-escalation +1.1 percentage points (95% CI 0.2 to 2.0; p=0.016), with the
privileged White-male-private comparator at zero (Figure 3A). The effect was broad but
crossed across axes: it was significant (BH-FDR q<0.05) for geography, immigration/language,
gender/identity, and race on advanced treatment, and for socioeconomic/housing and
immigration/language on de-escalation, while insurance and several groups were not
significant, and honest exceptions were present (uninsured received more trial mentions, not
fewer). The strongest evidence is directional concordance rather than magnitude: on the
flagged variants, all or nearly all six independent vendors moved the same way (Figure 3B).
Notably, and unlike the language-framing signal characterized next, this care-intensity layer
was affected by race (race-only axis, fewer trial mentions, q=0.01) as well as by
socioeconomic status, so the "socioeconomic, not race" result below is specific to the
framing channel. The magnitudes are small (1-4 percentage points at the label level) and we
frame this as a directionally consistent care-intensity tilt, not a demonstrated change in
delivered treatment intensity.

### Framing Bias Is Driven by Socioeconomic Disadvantage, Not Race in the Language-Framing Channel (Figure 4)

The same effect-size data, viewed as a forest plot across all 29 variants and six models,
show that race-only variant confidence intervals cluster near zero in all six models
(mean Cohen's d across the six race-only variants: -0.03 to 0.10 across models), while
socioeconomic-disadvantage variant confidence intervals sit well clear of zero in every
model (mean Cohen's d across seven SES/housing/insurance variants: 0.26 to 1.16 across
models). A complementary volcano-plot view of the same 174 model x variant contrasts
(effect size vs. BH-FDR-corrected significance; Figure 4A) makes this separation visually
explicit across all four variant classes in the design: socioeconomic-disadvantage
contrasts fan out to high significance at large effect sizes, while race-only, control, and
the remaining "other identity/context" contrasts (geography, age, immigration/language, and
the three gender/sexual-identity variants discussed further below) all cluster near the
null at low significance. The underinsured_only variant showed the single largest average effect across
models (mean d=1.01; range 0.46-1.55), followed closely by unhoused_patient (mean
d=0.76; range 0.09-1.43, largest in DeepSeek-chat), while the high_income_patient
control variant remained near zero in every model (d=-0.05 to 0.13), confirming this is a
disadvantage-specific gradient rather than a generic effect of any socioeconomic label.
The single largest effect observed anywhere in the 29-variant grid (d=1.62,
Gemini-2.5-flash) occurred for latina_female_uninsured, an intersectional race+insurance
variant in Tier A; because this variant confounds race with uninsured status, it cannot by
itself be read as evidence against the small race-only effect reported above, but it does indicate
that race may amplify an underlying socioeconomic effect at the intersection rather than
contributing an independent effect on its own, a question this design cannot fully
adjudicate given only five intersectional Tier-A variants.

### Guideline Concordance Is Statistically Equivalent Between Reference and Demographic Variants for Most Models (Figure 2A)

Testing the pre-registered confirmatory outcome (NCCN guideline concordance, no-demographics
reference vs. pooled demographic variants) with two one-sided equivalence tests (TOST,
margin d=±0.10) on the paired treatment-tier shift: equivalence was established for all 29
variants in Llama-3.3-70B, Llama-3.1-8B, and GPT-4o; 27 of 29 in DeepSeek-chat; 26 of 29 in
GPT-4o-mini; and 14 of 29 in Gemini-2.5-flash. Raw concordance deltas (with-demographics
minus no-demographics reference) were small across all six models: DeepSeek-chat -0.1pp,
Llama-3.3-70B -0.4pp, Llama-3.1-8B -0.5pp, GPT-4o -1.0pp, GPT-4o-mini +0.9pp, and
Gemini-2.5-flash +1.1pp. Absolute concordance varied substantially by model (DeepSeek-chat
90.7% reference concordance; GPT-4o 89.7%; Gemini-2.5-flash 81.7%; Llama-3.3-70B 75.9%;
GPT-4o-mini 55.6%; Llama-3.1-8B 49.5%), reflecting differences in baseline guideline-following
competence rather than demographic sensitivity.

Of 174 grid-wide directional decision tests (6 models x 29 variants), two survived
BH-FDR correction, both in DeepSeek-chat and both in the socioeconomic-disadvantage family:
`underinsured_only` (91 cases shifted to a less aggressive treatment tier vs. 40 upgrades;
sign-test p=9.8e-6; grid-wide BH-FDR q=0.0017) and `latina_female_uninsured` (92 downgrades
vs. 43 upgrades; p=3.0e-5; q=0.0026). These are the only two cells, across the full
6-model x 29-variant grid, where the treatment decision itself, not merely its framing, showed
a statistically robust directional shift, and both are net downgrades for a single vendor
(Figure 2C).

### Stigmatizing Language Shows a Dose-Response Gradient With Socioeconomic Disadvantage (Figure 5C)

The judge-adjudicated stigmatizing-language rate (unprompted adherence-doubt or
hallucinated SDOH content) showed a consistent monotone gradient across six models: near
zero for the no-demographics/white-male control (0.0-8.2% across models) and race-only
variant (0.2-10.9%), rising through uninsured (1.2-14.0%), underinsured (2.1-22.9%), and
low-income (1.0-42.8%), to its highest values for unhoused (2.1-81.8%) and Black+unhoused
(1.8-83.7%) variants. A Cochran-Armitage trend test on the five ordered
socioeconomic-disadvantage strata (control<uninsured<underinsured<low-income<unhoused,
race-only excluded as a non-SES reference; Figure 5C) confirmed this gradient is
statistically monotone in five of six models (z=15.4-46.6, all p<0.001), with GPT-4o-mini
the exception (z=1.3, p=0.20), consistent with GPT-4o-mini also showing the smallest
absolute gradient in Figure 5C. The gradient's steepness varied substantially by model: DeepSeek-chat
and Gemini-2.5-flash showed the largest unhoused-variant rates (81.8% and 74.3%,
respectively), while GPT-4o-mini showed a comparatively muted gradient (2.1% for
unhoused) despite GPT-4o (its larger sibling) showing a substantial gradient (52.7% for
unhoused), indicating stigma gradient magnitude is not simply a function of model scale
within a single vendor family (Figure 5C).

### Decomposing Soft Bias: Most of the Naive Signal Is Appropriate Care, Not Stigma (Figure 5A)

Splitting the eight soft-framing dimensions into an a priori stigmatizing composite
(adherence-doubt, prognosis framing, hallucinated SDOH, watchful-waiting) versus an
appropriate composite (financial-barrier language, social-work referral, specialist
referral, clinical-trial mention) shows the two behave very differently by variant. For
uninsured_only, the appropriate-care net% is large and consistent across models (48.2% to
93.2%; e.g., Gemini-2.5-flash underinsured_only: appropriate net%=93.2%), reflecting
guideline-endorsed financial-counseling and social-work language for a patient whose note
discloses an insurance barrier; this is the bulk of what a naive, undecomposed soft-bias
metric would report as "bias." The stigmatizing composite is smaller for uninsured/
underinsured variants (0.6% to 19.0% across models) but becomes the dominant signal for the
unhoused variant, where stigmatizing net% (25.1% to 78.9% across models) approaches or
exceeds the appropriate net% in five of six models (unhoused appropriate net%: 65.7%
Gemini-2.5-flash, 74.5% DeepSeek-chat, 28.4% Llama-3.3-70B, 7.4% Llama-3.1-8B, 0.2%
GPT-4o-mini). GPT-4o is the sole exception: its unhoused-variant appropriate net% is
negative (-6.4%) alongside a large stigmatizing net% (52.4%), meaning GPT-4o's
guideline-endorsed financial-counseling/social-work language was, on net, withdrawn rather
than added for this variant, at the same time its stigmatizing language rose, a
qualitatively different mechanism (appropriate care displaced by stigma) than the
"stigma added on top of stable appropriate care" pattern the other five models show. Because
this pattern appears in only one of six models and only for the single most disadvantaged
variant, we treat it as a real but model-specific anomaly rather than evidence of a general
appropriate-care-displacement mechanism; it does indicate that a stigma/appropriate
composite score summed across dimensions in a single model should not be assumed to
decompose additively, and that any deployed filter should be validated per-model rather
than assumed to generalize. Race-only and white-male-control variants showed near-zero net%
in both composites across all six models.

### Stigma Decomposes Into Defensible and Non-Defensible Narrative Elements (Figure 5B)

When the four soft-framing dimensions are further split into a pre-registered
defensible-stigma composite (adherence-doubt, hallucinated SDOH) versus the two
non-defensible/ambiguous dimensions (prognosis framing, watchful-waiting suggestion), the
disadvantage gradient lives almost entirely in the defensible composite. Averaged across
all six models, defensible-composite net% rose monotonically from the white-male control
(near 0%) through race-only (near 0%), Black+Medicaid, uninsured, and underinsured, to
low-income and unhoused (highest). The non-defensible dimensions, by contrast, showed no
comparable gradient: their combined net% stayed within a narrow 0.0-0.4% band across all
seven variants from control to unhoused, roughly two orders of magnitude smaller than the
defensible-composite range and showing no monotone relationship with disadvantage. This
indicates the socioeconomic stigma signal reported above is concentrated in the two
dimensions with the clearest clinical-harm interpretation (an LLM doubting a patient's
adherence or inventing an SDOH problem unprompted), not diffused across all four
soft-framing dimensions indiscriminately.

### The Gradient Is Not an Artifact of Note Generation or Demographic-Label Salience (Figure 6A–C)

Three independent controls tested whether the stigma gradient reflected a property of
model behavior rather than an artifact of the synthetic note-generation or
demographic-injection pipeline (Gemini and DeepSeek only, due to cost constraints across
the full grid). **Circularity control (Figure 6A):** on the same 100 cases, replacing the
LLM-generated free-text note with a fully deterministic, LLM-free template note left the
gradient intact: unhoused stigma rates were 76.0% (LLM note) vs. 84.0% (template) for
Gemini, and 80.0% vs. 92.0% for DeepSeek, while race-only and control rates remained near
zero under both note types for both models (0-7% range). **Real-note replication (Figure 6B):** substituting 40 real, open-access PubMed Central NSCLC case reports for the
GENIE-derived synthetic notes reproduced the same disadvantage gradient at a lower absolute
magnitude (Gemini: control 1.2%, race-only 4.2%, uninsured 10.0%, low-income 15.0%,
unhoused 32.5%; DeepSeek: control 1.2%, race-only 2.9%, uninsured 7.5%, low-income 10.0%,
unhoused 22.5%). **Salience-artifact control (Figure 6C):** injecting demographic information
as a bracketed tag versus weaving it into natural prose produced statistically
indistinguishable gradients for both Gemini (unhoused: +69pp tag vs. +74pp prose) and
DeepSeek (unhoused: +76pp tag vs. +83pp prose), with controls near zero under both
injection modes, ruling out demographic-label conspicuousness as the driver of the
effect.

### A Grounding-Aware Decision-Tree Confirms the Gradient Under a Stricter Definition of Stigma

The stigma gradient is not an artifact of the regex composite's blindness to linguistic
valence or clinical grounding. Routing all regex-flagged responses through the
deterministic bias decision-tree (Methods) reclassified 40.6% of them as benign (supportive
adherence language or note-grounded, all-patients counseling) and retained 59.4% as STIGMA,
yet left the disadvantage gradient intact while sharpening it (Figure 6D). Applying the tree's stricter,
grounding-aware definition drove the control (no-demographics/white-male) false-positive rate
from 2.18% under the raw regex to 0.02% — a 137-fold reduction — so that the tree-STIGMA rate
rose monotonically from control (0.02%) and race-only (0.2%) through uninsured (2.4%),
underinsured (3.8%), and low-income (11.6%) to black+unhoused (31.8%) and unhoused (38.1%),
widening the disadvantaged-to-control rate ratio from roughly 20-fold under the regex to more
than three orders of magnitude under the tree (Figure 10B). Critically, the tree tracked the human rater
about as well as the raw regex and better than the LLM judge (tree–human kappa=0.68, PABAK
0.87; cf. regex 0.77 and judge 0.57 on the same n=60 set; Figure S7), so this specificity gain came at
no measurable cost to human agreement. A targeted counterfactual ablation of the central
Gate-2 rule made the mechanism explicit: allowing a bare demographic label to count as
clinical grounding (which the tree forbids) re-labels roughly 6 percentage points of
otherwise-fabricated concern as "grounded" in the unhoused and black+unhoused strata but
0 percentage points in the control — precisely the counterfactual-fairness signature of a
concern triggered by identity rather than by documented clinical fact (Figure 6D). Among retained STIGMA
responses, the tree's descriptive harm-type decomposition was dominated by epistemic-injustice
(pre-emptive reliability/adherence doubt) and dignitary (unwarranted framing with treatment
unchanged) subtypes over the allocative (treatment weakened for a social reason) subtype (Supplementary Figure S11, bias-tree harm-type decomposition); this
three-way taxonomy is reported as descriptive only, as it has no human reference labels (see
Limitations).

### Full 29-Variant Summary: Flip Rate and Framing Effect Size (Table 2, Supplementary Table S3)

The headline results above (Figures 2-6) foreground a subset of the 29 pre-registered
demographic variants: the seven-variant socioeconomic/housing/insurance family, the
six race-only variants, the three intersectional Tier-A variants, and the three
gender/sexual-identity variants (non-binary, transgender woman, gay male patient) discussed
above in comparison to Omar et al.'s LGBTQIA+ finding. Table 2 reports the mean flip rate
and mean soft-framing Cohen's d, averaged across all six models, for all 29 variants,
confirming that the pattern generalizes: every variant with mean d>0.5 belongs to the
seven-variant SES/housing/insurance family or its intersections (`latina_female_uninsured`,
`black_unhoused`), while every other tier (race-only, geography, age,
immigration/language, gender/sexual identity, and the `high_income_patient` control)
clusters at mean d<0.3. The single largest effect outside this core SES/housing/insurance
family is `rural_patient` (tier D, mean d=0.27, range 0.04-0.62), smaller than every
member of the SES family but larger than the race-only, age, immigration/language, and
gender/sexual-identity tiers, and worth flagging as a secondary, geography-linked
socioeconomic signal rather than treating the SES/non-SES boundary as perfectly sharp.

| Variant | Tier | Mean flip rate (%) | Flip rate range | Mean Cohen's d | d range |
|---|---|---|---|---|---|
| black_female_medicaid | A | 15.9 | 11.2-21.1 | 0.163 | -0.01 to 0.52 |
| black_female_private | A | 16.6 | 11.4-20.5 | 0.035 | -0.05 to 0.14 |
| latina_female_uninsured | A | 16.9 | 12.1-22.3 | 0.774 | 0.32 to 1.62 |
| white_female_medicaid | A | 16.3 | 12.6-20.4 | 0.050 | 0.01 to 0.11 |
| white_male_private | A (reference) | 16.1 | 12.0-20.6 | -0.016 | -0.06 to 0.04 |
| medicaid_only | B | 16.1 | 11.7-21.6 | 0.166 | 0.02 to 0.30 |
| medicare_advantage_only | B | 16.1 | 11.0-22.8 | 0.028 | -0.03 to 0.09 |
| medicare_only | B | 16.4 | 12.4-21.9 | 0.026 | -0.04 to 0.10 |
| underinsured_only | B | 16.9 | 12.2-23.6 | 1.010 | 0.46 to 1.55 |
| uninsured_only | B | 16.9 | 12.8-23.2 | 0.818 | 0.43 to 1.41 |
| asian_race_only | C | 16.6 | 11.8-21.9 | 0.019 | -0.04 to 0.09 |
| black_race_only | C | 15.8 | 11.2-21.8 | 0.005 | -0.07 to 0.09 |
| hispanic_race_only | C | 16.4 | 11.4-20.6 | 0.005 | -0.05 to 0.09 |
| middle_eastern_race_only | C | 16.0 | 11.3-21.9 | 0.032 | -0.03 to 0.09 |
| multiracial_race_only | C | 16.4 | 11.3-21.6 | -0.008 | -0.07 to 0.06 |
| native_american_race_only | C | 16.6 | 11.5-22.3 | 0.099 | 0.05 to 0.17 |
| rural_patient | D | 16.0 | 11.5-22.5 | 0.273 | 0.04 to 0.62 |
| small_community_hospital | D | 15.8 | 10.2-20.8 | 0.009 | -0.03 to 0.06 |
| elderly_patient_75 | E | 17.4 | 12.2-22.7 | 0.054 | -0.01 to 0.13 |
| immigrant_patient | F | 16.4 | 12.4-21.5 | 0.056 | -0.03 to 0.12 |
| limited_english_patient | F | 16.0 | 11.4-21.9 | 0.077 | 0.01 to 0.19 |
| high_income_patient | G | 16.5 | 11.9-21.7 | 0.020 | -0.05 to 0.13 |
| low_income_patient | G | 16.1 | 10.4-22.2 | 0.772 | 0.13 to 1.49 |
| unhoused_patient | G | 16.3 | 12.7-22.7 | 0.758 | 0.09 to 1.43 |
| black_unhoused | H | 17.2 | 11.0-24.1 | 0.673 | 0.07 to 1.44 |
| low_income_black | H | 17.0 | 10.3-23.2 | 0.555 | 0.06 to 1.09 |
| gay_male_patient | I | 16.8 | 11.2-23.0 | 0.011 | -0.03 to 0.04 |
| non_binary_patient | I | 16.8 | 12.4-23.1 | 0.025 | -0.03 to 0.13 |
| transgender_woman | I | 16.6 | 12.0-23.8 | 0.022 | -0.03 to 0.09 |

*Full per-model breakdown (not averaged) is provided in Supplementary Table S3
(`supplementary_table_29variants_per_model.csv`) alongside this manuscript; the averaged
table above is derived from it.*

---

## Discussion

### Principal Findings

Across six LLMs and 1,048 real, de-identified NSCLC cases, adding a demographic label to
an otherwise identical clinical note left the treatment recommendation largely stable;
guideline concordance was statistically equivalent between the no-demographics reference
and most demographic variants (equivalence for >=26 of 29 variants) in five of six models
(Llama-3.3-70B, Llama-3.1-8B, GPT-4o: 29/29; DeepSeek-chat: 27/29; GPT-4o-mini: 26/29),
with Gemini-2.5-flash the exception (equivalence for 14/29, an underpowered rather than a
positive-effect result; see Limitations), and only one of 174 grid-wide directional
decision tests surviving multiplicity correction. Yet the language surrounding
that stable recommendation changed substantially, and the shape of that change was
specific: race-only variants showed small effect sizes, an order of magnitude below the
socioeconomic variants and largely, though not uniformly, indistinguishable from the
near-zero control across models, while socioeconomic-disadvantage variants showed a
monotonically increasing, and in several models very large, stigmatizing-language effect.
This dissociation, a stable decision with a demographically patterned narrative, is not
an artifact of the synthetic-note pipeline: it replicated on LLM-free template notes, on 40
real PubMed Central case reports, and under a natural-prose embedding control that removed
the bracketed-tag format entirely.
Decomposing that narrative-level signal further, we found it concentrated almost
completely in two dimensions with a clear stigma interpretation (unprompted adherence-doubt
and hallucinated social-determinants-of-health content), not diffused across all
soft-framing behaviors, and that roughly half or more of the disadvantage-associated
narrative change for insured/underinsured variants was guideline-endorsed appropriate care
(financial-counseling and social-work referral language) rather than stigma.

### Comparison With Prior Work

Omar et al. reported that LLM-recommended emergency-department urgency and invasiveness
shifted with race, housing status, and LGBTQIA+ identity across nine models. Our
oncology-specific, NCCN-anchored design reproduces the housing-status pattern but not the
race pattern: race-only Cohen's d remained small and largely, but not uniformly,
indistinguishable from zero (mean d -0.03 to 0.10) in every model we tested, while
socioeconomic-disadvantage effect sizes were an order of magnitude larger (0.26 to 1.16). This divergence may reflect differences in clinical domain (oncology treatment selection
vs. emergency triage), ground-truth structure (guideline-anchored NCCN Category-1 vs.
urgency/invasiveness scoring), or model-family/version differences across the two-year gap
between studies; our data cannot adjudicate between these, and we flag it as an open
question. The
divergence is unlikely to reflect idiosyncratic behavior of any single audited model: the
per-variant induced-framing-effect profile is highly correlated across all six models we
tested (Spearman rho of the 29-variant effect vector, pairwise across models; off-diagonal
median rho=0.72, Figure S6), indicating the six models
substantially agree on which demographic variants provoke framing changes even though they
differ in the overall magnitude of that response. We also do not reproduce Omar et al.'s LGBTQIA+-identity effect: across the three
identity-tier variants (non-binary, transgender woman, gay male patient), flip rates
(11.2-23.8%) and effect sizes (Cohen's d -0.03 to 0.13) matched the white-male-control and
race-only null, not the SES-large pattern. Consistent with our race finding, this suggests
the dimension driving framing bias in this guideline-anchored oncology design is
specifically socioeconomic disadvantage, not demographic identity broadly, though a direct
cross-study comparison is again not possible from our data alone. Separately, prior work on SES effects in clinical-trial-eligibility screening language [3]
treated "soft" SES-associated differences as a single harm signal; our decomposition
suggests that for insured-but-disadvantaged variants (uninsured, underinsured) a substantial
fraction of that signal is guideline-concordant financial and social-work responsiveness
rather than stigma, with the stigmatizing residue concentrated in the most severely
disadvantaged variant (unhoused). Finally, unlike audits of LLM behavior on
clinician-authored notes that already contain stigmatizing language [4], the stigmatizing
content here originates from the LLM itself, added to a note that, by construction,
contained no such content before the demographic label was applied; the mechanism is
generative, not inherited.

### Clinical and Deployment Implications

The dissociation between decision stability and narrative-framing bias has a direct
operational implication for LLM-integrated documentation tools: an audit or monitoring
system that checks only whether an ambient scribe's or inbox-drafting assistant's
*recommendation* changed by patient demographics will miss the harm this study
identifies, because the recommendation largely does not change. The narrative layer, the
free text that gets filed into the permanent record, is where the bias in this study
lives, and it is not currently a standard audit target for clinical LLM deployments. A health system deploying such tools should audit generated free text specifically for
unprompted adherence-doubt and SDOH-hallucination language, stratified by socioeconomic
status, rather than relying on recommendation-level fairness metrics alone, consistent with
post-deployment audits of other clinical ML systems where bias evaluated only at initial
validation missed disparities that emerged once the model was embedded in live care [13]. Equally important, an intervention that suppresses all socioeconomic-status
language indiscriminately would also suppress guideline-endorsed financial-counseling and
social-work referrals for patients who need them; the appropriate/stigmatizing
decomposition in Figure 5A and 5B is intended as a template for building a filter that
removes the former without removing the latter, though we have not built or evaluated such
a filter here.

### Limitations

Several limitations qualify these findings and should be weighed before any deployment or
policy conclusion is drawn.

**Single-rater stigma-label validation.** The stigma-detection judge was validated against
human gold labels provided by a single rater (the study author). On a representative random
sample (n=60, ~10% stigma prevalence), judge–human agreement was 91.7% (PABAK 0.83); the
corresponding Cohen's kappa (0.57) is base-rate–limited at this prevalence, and on the
smaller enriched contested set fell to fair (kappa=0.30 judge, 0.21 regex). This is weaker than the two-independent-rater standard expected for a bias-adjudication
instrument; a second blinded rater is planned (the RANDOM60 gold sheets are prepared) but was
not added before this draft. All absolute stigma-rate estimates should be read with this
caveat. The qualitative pattern (near-zero race-only effect, monotone SES gradient,
defensible/non-defensible decomposition) depends on relative ordering across variants rather
than an absolute threshold and is thus more robust to judge noise than any single point
estimate, though this has not been formally tested.

**Bias decision-tree scope.** The decision-tree filter shares the single-rater limitation
above (its tree–human κ=0.68 is from the same n=60, single-rater set) and adds two of its
own. First, because Gate 0 of the tree is the regex composite itself, the tree's recall is
capped by the regex: it can only reclassify already-flagged responses as benign or stigma
and cannot recover any stigma the regex missed, so it is a precision filter rather than an
independently more sensitive detector. Second, the three-way harm-type taxonomy the tree
emits (allocative, epistemic injustice, dignitary) has no human reference labels and is
reported as descriptive only; it has not been validated against human harm-type adjudication
and should not be read as a measured harm distribution. Both are targets for the same
second-rater adjudication that is pending for the primary stigma labels.

**Judge is itself an LLM.** The stigma-detection judge (Claude Sonnet-4.6) is itself an LLM, and we have not tested
whether its labeling behavior is confounded with the same socioeconomic-disadvantage
gradient this study measures (e.g., whether it is more likely to label a response
stigmatizing when it concerns a disadvantaged patient, independent of content). The
single-rater gold sets were labeled blind to demographic variant, which bounds this concern
for the adjudicated subset, but the judge's behavior on the full 31,440-response corpus has
not been independently audited for a disadvantage-correlated bias. This is a question for
future work rather than one this manuscript resolves.

**Two-vendor scope for robustness controls.** The LLM-free template-note replication
(Figure 9a) and the real PubMed Central note replication (Figure 9b) were run on Gemini and
DeepSeek only, not all six audited models, due to per-call API cost constraints across the
full demographic-variant grid. These controls demonstrate the gradient is not an artifact of note-generation or
injection mechanics for at least two model families; extending them to the other four
models is future work.

**Synthetic note generation.** While the underlying clinical facts (stage, histology,
biomarkers, treatment history) are drawn from real, de-identified GENIE BPC patient
records, the free-text clinical note presented to each audited model was itself generated
by an LLM (gemini-2.5-flash) rather than authored by a clinician. The circularity control (template notes, Figure 9a) and real-note replication (Figure 9b)
both show the gradient survives removing the LLM-generated note entirely, the strongest
available evidence against a note-generation circularity explanation; we nonetheless flag
the note-generation step as a design choice worth scrutiny in replication.

**Ground-truth scorer validation.** The NCCN concordance scorer is a deterministic,
rule-based decision tree that has not been validated against board-certified oncologist
adjudication on this specific cohort. Because the same scorer is applied uniformly across variants and models, any
misclassification would shift absolute concordance estimates equally and, having no access
to demographic information, would not introduce a demographic-variant-specific artifact.

**Single-institution-mix cohort.** The cohort is drawn from three U.S. academic cancer
centers (MSK, DFCI, VICC) and is not a nationally representative sample; the race/ethnicity distribution (79.1% Non-Hispanic White) reflects these centers' referral
populations rather than U.S. NSCLC demographics broadly, which may limit generalizability of
absolute stigma-rate estimates. The within-cohort demographic-variant comparison (the
study's core design) is unaffected, since every variant is applied to the same cohort.

**Deviation from pre-registered model panel.** The pre-registered protocol
(PREREGISTRATION.md) specified a five-model audit panel that included Claude Sonnet-4.6.
API credit constraints prevented running Claude Sonnet-4.6 to completion as an audit arm,
so it instead serves as the independent LLM judge for stigma adjudication. Llama-3.1-8B and
GPT-4o-mini, run to completion but not in the pre-registered panel, are reported as
exploratory arms. All headline dissociation,
TOST, and gradient findings replicate across the four models that are both pre-registered
and complete (Gemini-2.5-flash, DeepSeek-chat, Llama-3.3-70B, GPT-4o), so this substitution
does not appear to drive the reported pattern, but it is a departure from the registered
protocol that should be weighed accordingly.

**Model and prompt scope.** All models were queried once per case-variant combination at temperature 0 with a single
baseline prompt; we did not assess prompt sensitivity, multi-turn drift, or model versions
released after data collection. Mitigation strategies from the broader research program
(fairness-instructed prompting, structured extraction) are outside this manuscript's scope
and reported separately.

### Conclusions

In a large, real-world oncology cohort audited across six LLMs, adding a demographic label
to an otherwise-identical note left the guideline-concordant decision largely stable but
reshaped the surrounding output along a bias-severity gradient: an intermediate care-intensity
shift (fewer trial mentions, more de-escalation for marginalized patients, affected by race as
well as socioeconomic status), and a larger language-framing shift that tracked socioeconomic
disadvantage rather than race. This
pattern replicated across model-free template notes, real case reports, and a natural-prose
salience control, and concentrated in two narrative dimensions with clear stigma
interpretations rather than diffusing across all socioeconomic-responsive language. Bias
audits of clinical LLMs that evaluate only the final recommendation risk substantially
underestimating the demographic bias these systems introduce into deployed clinical
documentation. We propose that future audits of LLM-integrated clinical tools decompose
narrative-level bias into clinically defensible socioeconomic responsiveness and
genuinely stigmatizing content, since these two categories carry opposite policy
implications: the former should be preserved as guideline-concordant care, and the latter
is a specific, filterable target for pre-deployment mitigation.

---

## Declarations

**Data Availability:** GENIE BPC data are available to qualified researchers via the AACR
Project GENIE Biopharma Collaborative data access process (https://www.aacr.org/professionals/research/aacr-project-genie/biopharma-collaborative/).
This study's derived case-level analysis outputs, demographic-variant injection code, and
statistical analysis scripts are available in the project repository.

**Code Availability:** All analysis code (variant injection, NCCN concordance scoring,
soft-bias/stigma detection, statistical analysis, and figure generation) is available at
the project repository referenced above.

**Conflicts of Interest:** The author declares no competing interests relevant to this
manuscript.

**Funding:** [Author to insert funding source, or state "No external funding was received for this work."]

**Author Contributions:** A. Cuervo conceived the study, curated the data, developed the
analysis pipeline, conducted the analyses, and wrote the manuscript. [Update if additional
co-authors are added before submission.]

**Acknowledgments:** This work uses data generated by the AACR Project GENIE Biopharma
Collaborative. The interpretations herein are the author's and do not represent the
official views of AACR Project GENIE or its contributing institutions.

---

## References

1. Omar M, Soffer S, Agbareia R, Bragazzi NL, Apakama DU, Horowitz CR, Charney AW, Freeman
   R, Kummer B, Glicksberg BS, Nadkarni GN, Klang E. Sociodemographic biases in medical
   decision making by large language models. *Nat Med*. 2025;31(6):1873-1881.
   doi:10.1038/s41591-025-03626-6

2. Omar M, Sorin V, Agbareia R, Apakama DU, Soroush A, Sakhuja A, Freeman R, Horowitz CR,
   Richardson LD, Nadkarni GN, Klang E. Evaluating and addressing demographic disparities
   in medical large language models: a systematic review. *Int J Equity Health*.
   2025;24:57. doi:10.1186/s12939-025-02419-0

3. Soffer S, Omar M, Efros O, Apakama DU, Mudrik A, Freeman R, Nadkarni GN, Klang E.
   Sociodemographic bias in large language model clinical trial screening. *J Am Med
   Inform Assoc*. 2026. doi:10.1093/jamia/ocag058 (preprint: medRxiv
   doi:10.1101/2025.11.15.25340177)

4. Huang J, Zhou D, Kamau F, Oh A, Links AR, Dredze M, Beach MC, Saha S. Artificial
   Intolerance: Stigmatizing Language in Clinical Documentation Skews Large Language Model
   Decision-Making. arXiv preprint arXiv:2605.17228. 2026.

5. Lavery JA, Lepisto EM, Brown S, Rizvi H, McCarthy C, LeNoue-Newton M, et al. A Scalable
   Quality Assurance Process for Curating Oncology Electronic Health Records: The Project
   GENIE Biopharma Collaborative Approach. *JCO Clin Cancer Inform*. 2022;6:e2100105.
   doi:10.1200/CCI.21.00105

6. Lavery JA, Brown S, Curry MA, Martin A, Sjoberg DD, Whiting K, et al. A data processing
   pipeline for the AACR project GENIE biopharma collaborative data with the {genieBPC} R
   package. *Bioinformatics*. 2023;39(1):btac796. doi:10.1093/bioinformatics/btac796

7. National Comprehensive Cancer Network (NCCN). NCCN Clinical Practice Guidelines in
   Oncology: Non-Small Cell Lung Cancer. [Author to insert the specific version number
   used for ground-truth scoring, per Methods.]

8. [CancerGUIDE dataset / benchmark reference; author to insert full citation for the
   synthetic-case source referenced in Methods.]

9. Goddu AP, O'Conor KJ, Lanzkron S, Saheed MO, Saha S, Peek ME, Haywood C Jr, Beach MC.
   Do Words Matter? Stigmatizing Language and the Transmission of Bias in the Medical
   Record. *J Gen Intern Med*. 2018;33(5):685-691. doi:10.1007/s11606-017-4289-2

10. Park J, Saha S, Chee B, Taylor J, Beach MC. Physician Use of Stigmatizing Language in
    Patient Medical Records. *JAMA Netw Open*. 2021;4(7):e2117052.
    doi:10.1001/jamanetworkopen.2021.17052

11. Barcelona V, Scharp D, Idnay BR, et al. Identifying stigmatizing language in clinical
    documentation: A scoping review of emerging literature. *PLoS One*.
    2024;19(6):e0303653. doi:10.1371/journal.pone.0303653

12. Apakama DU, Nguyen KA, Hyppolite D, Soffer S, Mudrik A, Ling E, et al. Identifying
    Bias at Scale in Clinical Notes Using Large Language Models. *Mayo Clin Proc Digit
    Health*. 2025. doi:10.1016/j.mcpdig.2025.100296

13. Colacci M, Pou-Prom C, Siddiqi A, Mamdani M, Verma AA. Evaluating sociodemographic
    bias in a deployed machine-learned patient deterioration model. *JAMIA Open*.
    2025;8(6):ooaf158. doi:10.1093/jamiaopen/ooaf158

14. [Ambient clinical-documentation and EHR-LLM-integration deployment references (Nuance
    DAX, Abridge, Epic's GPT-4o inbox-drafting integration); author to insert vendor
    press releases or peer-reviewed evaluations cited in the Introduction's
    deployment-harm framing.]

*Note: references 1-6 and 9-13 are verified against PubMed/PMC metadata (PMID, DOI, and
author list confirmed directly from NLM records) as of 2026-07-09. References 7, 8, and 14
remain placeholders requiring the author's citation-manager pass to insert the specific
guideline version, dataset citation, and deployment-vendor sources used.*

---

## Figures

![](figures/manuscript/Fig01_study_workflow.png){width=6.5in}

**Figure 1. Study workflow.** End-to-end pipeline: 1,048 synthetic NSCLC vignettes were
generated with Gemini-2.5-Flash from GENIE BPC cases; each was presented to every model to
elicit a first-line treatment recommendation, yielding 1,048 cases x 30 demographic labels x
6 models = 188,640 runs. Each answer was scored on two axes—hard concordance (mapped to NCCN
as concordant, downgrade, or flip) and the soft stigma-framing composite—and every condition
was compared with the no-demographics control to quantify hard and soft bias gaps (BH-FDR).
Consistency and robustness controls (test-retest reliability, deterministic template notes,
and natural-prose embedding) plus a 40-note real PubMed Central replication set support the
soft-bias findings.

![](figures/manuscript/Fig02_counterfactual_design.png){width=6.5in}

**Figure 2. Counterfactual variant design.** Each de-identified, demographics-neutral NSCLC
clinical note (the neutral anchor) is expanded into 29 demographic variants spanning nine
tiers (race, insurance, socioeconomic status, geography, age, immigration/language, and
gender identity) plus the neutral anchor, for 30 versions per case. All 30 are sent to six
LLMs across five model families (Gemini-2.5-flash, DeepSeek-chat, Llama-3.3-70B,
Llama-3.1-8B, GPT-4o, GPT-4o-mini) to elicit an NCCN guideline-concordant treatment
recommendation, and the reference is compared against each demographic variant
(counterfactual fairness).

![](figures/manuscript/Fig03_cohort_description.png){width=6.5in}

**Figure 3. Cohort description.** Distribution of the 1,048 GENIE BPC NSCLC cases by AJCC
stage, histology, driver-mutation status, PD-L1 tumor proportion score, contributing
institution, race/ethnicity, and age.

![](figures/manuscript/Fig04_concordance_stability.png){width=6.5in}

**Figure 4. Guideline-concordance stability.** (A) NCCN guideline concordance for the
no-demographics reference versus demographic variants across all six models, with
two-one-sided-test (TOST) equivalence counts annotated; this is the pre-registered
confirmatory outcome. (B) Partial concordance, coarsening the 0-3 adherence ordinal to
0/0.5/1.0, shown for the same reference-versus-variant structure as a secondary,
exploratory analysis.

![](figures/manuscript/Fig05_dissociation_6vendor.png){width=6.5in}

**Figure 5. Dissociation between the treatment decision and its narrative framing.** (A)
Treatment-selection flip rate relative to the no-demographics reference remains within each
model's test-retest noise floor across all demographic variants. (B) The soft-framing
effect size (Cohen's d) of those same responses fans out with socioeconomic tier. Six
models, 1,048 cases x 30 variants.

![](figures/manuscript/Fig06_forest_ses_vs_race_6vendor.png){width=6.5in}

**Figure 6. Socioeconomic versus racial framing effect sizes.** Forest plot of the
soft-framing Cohen's d per variant across the six models: socioeconomic-disadvantage
confidence intervals sit well clear of zero, while race-only intervals are small.

![](figures/manuscript/FigS04_soft_split_avg.png){width=6.5in}

**Figure 7. Decomposition of soft bias into appropriate versus stigmatizing framing.** Net
percentage of appropriate, SDOH-responsive content (financial-counseling, social-work,
specialist, and clinical-trial referral) versus stigmatizing content (adherence-doubt and
hallucinated SDOH generation) per variant. Each bar is the unweighted mean across the six
models, with every model's value overlaid as a dot so the between-model spread is shown
directly rather than as a pooled confidence interval (the model, not the case, is the
replication unit). Appropriate care dominates for insurance-barrier variants; the
stigmatizing layer is smaller and concentrated on the unhoused. Full per-model panels, with
axes shared for direct magnitude comparison, are provided in Figure S4.

![](figures/manuscript/Fig08_stigma_gradient_softened.png){width=6.5in}

![](figures/manuscript/Fig08b_stigma_dose_response.png){width=6.5in}

**Figure 8. Stigmatizing-language dose-response gradient.** Judge-adjudicated
stigmatizing-language rate (unprompted adherence-doubt or hallucinated SDOH content) across
ordered socioeconomic-disadvantage strata for all six models. **(Figure 8b)** Per-model
small multiples of the same gradient across the five-rung socioeconomic ladder (control,
uninsured, underinsured, low-income, unhoused; race-only shown off-ladder), each annotated
with its Cochran-Armitage trend test z and p value; the gradient is monotone in five of six
models (GPT-4o-mini: z=1.3, p=0.20).

![](figures/manuscript/Fig09a_circularity_template_notes.png){width=6.5in}

![](figures/manuscript/Fig09b_pmc_real_note_replication.png){width=6.5in}

![](figures/manuscript/Fig09c_natural_embedding_salience_control.png){width=6.5in}

**Figure 9. The gradient is not an artifact of note generation or demographic-label
salience.** (9a) The stigma gradient replicates on fully deterministic, LLM-free
template-generated notes (Gemini and DeepSeek). (9b) It replicates on 40 real, open-access
PubMed Central NSCLC clinical notes (Gemini and DeepSeek). (9c) Salience control: on the
same 150 cases, demographics were injected either as a bracketed metadata tag or woven into
natural prose (no LLM); the gradient survives both injection modes for Gemini (+69 vs. +74
percentage points, unhoused minus control) and DeepSeek (+76 vs. +83 percentage points),
with controls near zero under both.

![](figures/manuscript/Fig10_bias_tree.png){width=6.5in}

**Figure 10. Grounding-aware bias decision-tree as a precision filter over regex-flagged
recommendations.** (A) Routing all regex-flagged responses through the deterministic tree
reclassifies a substantial fraction as benign (note-grounded or supportive) and retains the
remainder as STIGMA. (B) The tree removes control false positives and sharpens the
socioeconomic gradient relative to the raw regex, driving the no-demographics/white-male
control rate toward zero. (C) Descriptive harm-type decomposition of retained STIGMA
responses into allocative, epistemic-injustice, and dignitary subtypes (reported as
descriptive only; no human reference labels). (D) Gate-2 counterfactual ablation: allowing a
bare demographic label to count as clinical grounding re-labels fabricated concern as
"grounded" in the disadvantaged strata but not in the control, the counterfactual-fairness
signature of an identity-triggered concern.

### Supplementary Figures

![](figures/manuscript/FigS01_judge_validation_single_rater_CAVEAT.png){width=6.5in}

**Figure S1. Stigma-classifier judge validation (enriched contested set).** Agreement
between the LLM judge and the single human rater on the 35-item classifier-flagged gold set
(Cohen's kappa=0.30); on the representative random sample (n=60) judge–human agreement was
91.7% (PABAK 0.83; see Methods). Single self-labeled rater; a disclosed limitation (see
Limitations).

![](figures/manuscript/FigS02_pmc_note_provenance.png){width=6.5in}

**Figure S2. PMC note provenance.** Sourcing and note-length distribution for the 40 real
PubMed Central clinical notes used in Figure 9b.

![](figures/manuscript/FigS03_concordance_by_variant_avg_paired.png){width=6.5in}

**Figure S3. Pooled concordance by demographic label.** Companion to Figure S8: NCCN
concordance per demographic label pooled across all six models via matched case x model
pairs (McNemar test versus the no-demographics reference, BH-FDR corrected). No label is
significant; the concordance null holds label by label.

![](figures/manuscript/Fig07_soft_split_harmonized.png){width=6.5in}

**Figure S4. Per-model appropriate-versus-stigmatizing decomposition.** The six-panel
per-model view underlying Figure 7: appropriate-SDOH-care versus stigmatizing net percentage
per variant, with axes shared across all six model panels so relative magnitude is directly
comparable. Companion to Figure 7.

![](figures/manuscript/FigS05_stigma_breakdown_avg.png){width=6.5in}

**Figure S5. Averaged stigma decomposition by behavior.** Companion to Figure S10: mean net
percentage per stigma dimension across models, with each model's per-label total overlaid
as a dot and the defensible composite marked.

![](figures/manuscript/FigS06_intermodel_agreement.png){width=6.5in}

**Figure S6. Cross-model agreement.** 6x6 Spearman-correlation heatmap of the 29-variant
induced soft-framing-effect vector, pairwise across all six models (off-diagonal median
rho=0.72), supporting the claim that the models substantially agree on which variants
provoke framing change.

![](figures/manuscript/FigS07_bias_tree_validation.png){width=4.0in}

**Figure S7. Bias decision-tree agreement with the human rater.** Cohen's kappa against the
single human rater on the classifier-blind random set (n=60) for the deterministic tree,
the raw regex composite, and the LLM (Sonnet) judge. The tree matches the regex and exceeds
the LLM judge while reclassifying a substantial fraction of regex flags as benign
(companion to Figure 10).

![](figures/manuscript/FigS08_concordance_by_variant.png){width=6.5in}

**Figure S8. Concordance by demographic variant.** Per-variant NCCN concordance across the
six models, with Benjamini-Hochberg-significant deviations from the no-demographics
reference marked by asterisks. Companion to Figure 4 (the pre-registered confirmatory
concordance outcome).

![](figures/manuscript/FigS09_framing_volcano.png){width=6.5in}

**Figure S9. Framing effect-size volcano.** Volcano plot of all 174 model x variant
contrasts (soft-framing effect size versus BH-FDR-corrected significance), colored by
variant class (socioeconomic disadvantage, race/ethnicity only, control, and other
identity/context), making the socioeconomic-versus-race separation explicit across the
full 29-variant design in a single panel. Companion to Figure 6.

![](figures/manuscript/FigS10_stigma_breakdown_original.png){width=6.5in}

**Figure S10. Stigma decomposed by behavioral dimension.** The stigmatizing composite split
into its component behaviors (adherence/compliance doubt, hallucinated SDOH generation,
prognosis framing, and watchful-waiting), stacked per model across six panels. Companion to
Figure 7 (the appropriate-versus-stigmatizing decomposition).
