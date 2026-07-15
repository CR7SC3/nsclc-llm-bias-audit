# Stigma Without Downgrade: Separating Warranted Socioeconomic Responsiveness From Generated Stigma in Large Language Model Cancer-Treatment Recommendations

**A Counterfactual Audit of Six Large Language Models on 1,048 Real-World Non-Small-Cell Lung Cancer Cases**

---

## Abstract

**Background:** Large language models (LLMs) are increasingly embedded in oncology
workflows through ambient clinical scribes and electronic health record (EHR)-integrated
drafting tools. Prior bias audits typically score only whether an LLM's final treatment
recommendation changes with patient demographics, which may miss bias that instead
appears in the surrounding clinical narrative.

**Objective:** To determine, using a large real-world oncology cohort, whether LLM
treatment recommendations for non-small-cell lung cancer (NSCLC) change with demographic
framing (decision bias), whether the surrounding narrative changes independently
(framing bias), and whether any framing bias reflects warranted socioeconomic
responsiveness, stigmatizing assumptions, or both.

**Methods:** We constructed demographics-neutral clinical notes from 1,048 real,
de-identified NSCLC cases (AACR Project GENIE Biopharma Collaborative, v2.0-public) and
generated 30 demographic variants per case (race, insurance, socioeconomic status,
gender/identity, plus a no-demographics reference), holding clinical facts constant. Six
LLMs (Gemini-2.5-flash, DeepSeek-chat, Llama-3.3-70B, Llama-3.1-8B, GPT-4o, GPT-4o-mini)
were queried at temperature 0 across all case-by-variant combinations. Primary outcomes
were treatment-recommendation flip rate and NCCN guideline concordance (tested for
statistical equivalence, TOST, between reference and each variant), and a continuous
soft-framing intensity score decomposed into a stigmatizing component (unprompted
adherence-doubt, hallucinated social-determinants-of-health content) versus an
appropriate component (NCCN-endorsed financial-counseling/social-work language), each
tested with paired sign tests and grid-wide Benjamini-Hochberg correction (174
model-by-variant comparisons). Stigma labels were adjudicated by an LLM judge validated
against a human-labeled gold set (Cohen's κ=0.30). Robustness was assessed on LLM-free
template notes, 40 real PubMed Central case reports, and a natural-prose demographic
embedding control.

**Results:** NCCN concordance was statistically equivalent between reference and
demographic variants for most models (29/29 variants for Llama-3.3-70B, Llama-3.1-8B, and
GPT-4o; 27/29 DeepSeek-chat; 26/29 GPT-4o-mini; 14/29 Gemini-2.5-flash), with concordance
deltas of -1.0 to +1.1 percentage points across all six models. Mean flip rates ranged
from 11.7% (GPT-4o) to 22.1% (GPT-4o-mini). Of 174 grid-wide directional decision tests,
exactly one survived BH-FDR correction: DeepSeek-chat's underinsured_only variant (94
downgrades vs. 48 upgrades; q=0.0245). Stigmatizing-framing effect sizes showed a
consistent socioeconomic gradient across all six models: race-only variants averaged
Cohen's d=-0.03 to 0.10 (small; not uniformly distinguishable from zero), while
socioeconomic-disadvantage variants averaged d=0.26 to 1.16 across a seven-variant
SES/housing/insurance family (unhoused reaching d=1.43 in DeepSeek-chat; the single largest
effect across all 29 variants and 6 models, d=1.62, occurred for the intersectional
latina_female_uninsured variant in Gemini-2.5-flash). This gradient replicated on template
notes, real PubMed Central notes, and
under natural-prose demographic embedding.

**Conclusions:** Across six LLMs and 1,048 real NSCLC cases, demographic framing left
guideline-concordant treatment decisions largely stable but reshaped the surrounding
narrative in a pattern that tracked socioeconomic disadvantage, not race, independent of
note-generation artifacts. Audits scoring only the final recommendation may substantially
underestimate demographic bias operating through narrative framing. Decomposing framing
bias into appropriate SDOH-responsive content and stigmatizing content is necessary to
avoid conflating legitimate socioeconomic care coordination with a genuinely harmful,
separable stigma signal.

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
wrong regimen, but that a deployed system silently inserts an unwarranted assumption —
"patient may have difficulty adhering to treatment," a fabricated housing instability, an
unprompted note about affordability — into the chart of a disadvantaged patient, where it
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
— 22 of 24 (91.7%) — identified some form of bias, with gender bias reported in 15 of 16
studies and racial/ethnic bias in 10 of 11 [2]. That near-universal "finds bias" result
is itself a methodological problem: a literature in which almost every audit reports bias
against some final-decision metric offers little guidance on which bias mechanisms matter,
which are addressable, and which reflect defensible clinical judgment rather than harm.

We identify two gaps in this literature that this study is designed to close.

**First, existing audits overwhelmingly score the final decision, not the language that
carries it.** A treatment recommendation and the narrative that accompanies it are
different outputs with different downstream consequences. A stable recommendation
delivered with an added, unprompted note questioning a patient's adherence, or a
fabricated claim about a patient's housing status, causes harm through the note itself —
propagating into future encounters — independent of whether the underlying recommendation
changed. Audits that score only whether the final treatment category flips will
systematically miss this framing-level harm, understating the bias that a deployed
ambient-documentation or inbox-drafting system would actually introduce into a chart.

**Second, when audits do measure narrative-level ("soft") bias, they typically report it
as a single undifferentiated composite.** Not all differential language directed at
socioeconomically disadvantaged patients is stigmatizing. NCCN guidelines explicitly
endorse addressing financial barriers and referring uninsured or low-income patients to
social work and financial-counseling resources — mentioning these resources for a patient
whose note discloses insurance or housing instability is warranted, guideline-concordant
care, not bias. A soft-bias metric that lumps this appropriate responsiveness together
with unprompted adherence-doubt or hallucinated social-determinants-of-health (SDOH)
content will overstate the harm, and — more importantly — will not tell a health system
what to filter. To our knowledge, no prior audit has partitioned socioeconomic
responsiveness into an appropriate-care component and a separable, genuinely stigmatizing
component and tested whether they behave differently.

This study addresses both gaps using a single design: a large, real-world oncology cohort,
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
signal — and does that stigmatizing signal survive replication on notes the audited models
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
is attributable to the demographic label alone.

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
intersections (2 variants), and (I) gender/sexual identity (3 variants) — 29 variants in
total across tiers A-I — plus the `no_demographics` neutral-anchor control, for 30 total. For unstructured notes, a single bracketed
demographic label was prepended to the note (e.g., "\[PATIENT DEMOGRAPHICS: Black female
patient, Medicaid\]"); no narrative context beyond the label itself was added, isolating
the demographic signal from any confounding narrative style change.

### Models

Six LLMs from five model families were evaluated: Gemini-2.5-flash (Google), DeepSeek-chat
(DeepSeek), Llama-3.3-70B-Instruct-Turbo and Llama-3.1-8B-Instruct (Meta, via Together AI
and OpenRouter respectively), GPT-4o and GPT-4o-mini (OpenAI). This panel deviates from the
pre-registered five-model audit panel (PREREGISTRATION.md), which specified Claude
Sonnet-4.6 in place of Llama-3.1-8B and GPT-4o-mini; Claude Sonnet-4.6 was not run to
completion due to API credit constraints at data-collection time and is excluded from this
manuscript, with Llama-3.1-8B and GPT-4o-mini added as completed, non-preregistered
exploratory arms. This deviation is disclosed here as a departure from the registered
protocol. All models were queried at
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

**Primary — treatment-recommendation flip rate.** The proportion of cases where a
variant's parsed treatment category differs from the `no_demographics` reference,
reported with Wilson 95% confidence intervals.

**Primary — NCCN guideline concordance.** Tested for statistical equivalence between the
no-demographics reference and each demographic variant using two one-sided tests (TOST)
on the paired treatment-tier shift (Cohen's d), with a pre-specified equivalence margin of
d=±0.10; equivalence is declared only when the tier-shift 95% CI lies entirely within this
margin, not merely on a failure to reject a null of no difference.

**Primary — directional decision test.** Among cases where the treatment category
changed, a signed treatment-aggressiveness-tier shift (1=best supportive care to 8=surgical
resection) was tested with a paired sign test (downgrade vs. upgrade), correcting for
multiplicity with a single grid-wide Benjamini-Hochberg (BH) false discovery rate procedure
across the full model x variant family (6 models x 29 non-reference variants = 174 tests),
not per-model or per-metric families.

**Secondary — soft-framing intensity and appropriate/stigmatizing decomposition.** A
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

**Secondary — dose-response trend test.** To test formally whether the stigmatizing-rate
gradient across disadvantage strata (Figure 7) is monotone rather than merely visually
suggestive, a Cochran-Armitage trend test was applied per model across the five ordered
socioeconomic-disadvantage strata (control < uninsured < underinsured < low-income <
unhoused), using ordinal tier scores 0-4 as the trend variable. Race-only was excluded from
the ladder (it carries no socioeconomic disadvantage) and instead compared to control
directly, as in the primary race-only-vs-SES effect-size analysis above.

**Secondary — cross-model agreement.** To assess whether the reported dissociation
reflects a shared demographic-response mechanism rather than idiosyncratic behavior of one
model, the 29-variant induced soft-framing-effect vector (Cohen's d per variant) was
compared pairwise across all six models using Spearman rank correlation.

### Judge Validation

Following precedent for LLM-based detection of biased/stigmatizing language at scale in
clinical text [12], the keyword/pattern classifier was validated against a 35-item gold set
of model responses, enriched for classifier-flagged (contested) items from the Gemini and
DeepSeek arms, labeled by the study author (single rater) blinded to demographic variant into
STIGMA / APPROPRIATE / NEUTRAL, then binarized to STIGMA vs. not-STIGMA for agreement
analysis. Human-judge agreement was 71% (Cohen's kappa=0.30); human-regex agreement was
51% (kappa=0.21). On the 17 items where the regex classifier and judge disagreed, the
human rater sided with the judge in 12/17 cases, indicating the regex classifier
systematically over-counts stigma; all reported stigma rates use judge-adjudicated labels.
This single-rater validation, and the resulting fair (rather than substantial) agreement
level, is a disclosed limitation (see Limitations) rather than a resolved validation.

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
the design is repeated-measures — each case contributes several responses to the pooled
race-only (six variants) and control (two variants) strata — per-stratum stigma rates
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
labels validated against a single-rater, 35-item targeted gold set (Cohen's kappa=0.30,
fair agreement; see Methods). They should be read as an internal comparison across
variants and models within this design, not as precise absolute measurements.*

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
routine (full breakdown in Figure S0).

### Demographic Framing Leaves the Treatment Decision Largely Stable While Reshaping Its Narrative (Figure 4)

Across all six models, the treatment-recommendation flip rate relative to the
no-demographics reference did not vary systematically across the 29 demographic variants;
every variant's flip rate for a given model overlapped that model's own mean flip rate
across all variants (Figure 4A). Mean flip rates ranged from 11.7% (GPT-4o) to 22.1%
(GPT-4o-mini), with intermediate rates for DeepSeek-chat (13.3%), Llama-3.3-70B (14.5%),
Llama-3.1-8B (17.5%), and Gemini-2.5-flash (19.7%) — a range consistent with each model's
baseline decision-instability floor rather than a demographic-specific effect.

In sharp contrast, the added soft-framing intensity of each response (Cohen's d in
framing score, relative to the no-demographics reference) fanned out systematically by
socioeconomic tier within every model (Figure 4B): race-only and no-demographics-adjacent
variants clustered near d=0, while socioeconomic-disadvantage variants (unhoused,
underinsured, uninsured, low-income) showed materially larger effect sizes, with the
largest single effect reaching d=1.62 (Gemini-2.5-flash, latina_female_uninsured;
underinsured_only alone reached d=1.55 in the same model). This
dissociation — a stable decision paired with demographically-patterned narrative
framing — is the central empirical pattern this study reports.

### Framing Bias Is Driven by Socioeconomic Disadvantage, Not Race (Figure 5)

The same effect-size data, viewed as a forest plot across all 29 variants and six models,
show that race-only variant confidence intervals cluster near zero in all six models
(mean Cohen's d across the six race-only variants: -0.03 to 0.10 across models), while
socioeconomic-disadvantage variant confidence intervals sit well clear of zero in every
model (mean Cohen's d across seven SES/housing/insurance variants: 0.26 to 1.16 across
models). A complementary volcano-plot view of the same 174 model x variant contrasts
(effect size vs. BH-FDR-corrected significance; Figure 5b) makes this separation visually
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
contributing an independent effect on its own — a question this design cannot fully
adjudicate given only five intersectional Tier-A variants.

### Guideline Concordance Is Statistically Equivalent Between Reference and Demographic Variants for Most Models (Figure 2)

Testing the pre-registered confirmatory outcome — NCCN guideline concordance, no-demographics
reference vs. pooled demographic variants — with two one-sided equivalence tests (TOST,
margin d=±0.10) on the paired treatment-tier shift: equivalence was established for all 29
variants in Llama-3.3-70B, Llama-3.1-8B, and GPT-4o; 27 of 29 in DeepSeek-chat; 26 of 29 in
GPT-4o-mini; and 14 of 29 in Gemini-2.5-flash. Raw concordance deltas (with-demographics
minus no-demographics reference) were small across all six models: DeepSeek-chat -0.1pp,
Llama-3.3-70B -0.4pp, Llama-3.1-8B -0.5pp, GPT-4o -1.0pp, GPT-4o-mini +0.9pp, and
Gemini-2.5-flash +1.1pp. Absolute concordance varied substantially by model (DeepSeek-chat
90.7% reference concordance; GPT-4o 89.7%; Gemini-2.5-flash 81.7%; Llama-3.3-70B 75.9%;
GPT-4o-mini 55.6%; Llama-3.1-8B 49.5%), reflecting differences in baseline guideline-following
competence rather than demographic sensitivity.

Of 174 grid-wide directional decision tests (6 models x 29 variants), exactly one survived
BH-FDR correction: DeepSeek-chat's `underinsured_only` variant showed a significant net
downgrade (94 cases shifted to a less aggressive treatment tier vs. 48 upgrades; sign-test
p=0.0001; grid-wide BH-FDR q=0.0245). This is the only demographic variant, across the
full 6-model x 29-variant grid, where the treatment decision itself — not merely its
framing — showed a statistically robust directional shift.

### Stigmatizing Language Shows a Dose-Response Gradient With Socioeconomic Disadvantage (Figure 7)

The judge-adjudicated stigmatizing-language rate (unprompted adherence-doubt or
hallucinated SDOH content) showed a consistent monotone gradient across six models: near
zero for the no-demographics/white-male control (0.0-8.2% across models) and race-only
variant (0.2-10.9%), rising through uninsured (1.2-14.0%), underinsured (2.1-22.9%), and
low-income (1.0-42.8%), to its highest values for unhoused (2.1-81.8%) and Black+unhoused
(1.8-83.7%) variants. A Cochran-Armitage trend test on the five ordered
socioeconomic-disadvantage strata (control<uninsured<underinsured<low-income<unhoused,
race-only excluded as a non-SES reference; Figure 7b) confirmed this gradient is
statistically monotone in five of six models (z=15.4-46.6, all p<0.001), with GPT-4o-mini
the exception (z=1.3, p=0.20) — consistent with GPT-4o-mini also showing the smallest
absolute gradient in Figure 7. The gradient's steepness varied substantially by model — DeepSeek-chat
and Gemini-2.5-flash showed the largest unhoused-variant rates (81.8% and 74.3%,
respectively), while GPT-4o-mini showed a comparatively muted gradient (2.1% for
unhoused) despite GPT-4o (its larger sibling) showing a substantial gradient (52.7% for
unhoused) — indicating stigma gradient magnitude is not simply a function of model scale
within a single vendor family.

### Decomposing Soft Bias: Most of the Naive Signal Is Appropriate Care, Not Stigma (Figure 6)

Splitting the eight soft-framing dimensions into an a priori stigmatizing composite
(adherence-doubt, prognosis framing, hallucinated SDOH, watchful-waiting) versus an
appropriate composite (financial-barrier language, social-work referral, specialist
referral, clinical-trial mention) shows the two behave very differently by variant. For
uninsured_only, the appropriate-care net% is large and consistent across models (48.2% to
93.2%; e.g., Gemini-2.5-flash underinsured_only: appropriate net%=93.2%), reflecting
guideline-endorsed financial-counseling and social-work language for a patient whose note
discloses an insurance barrier — this is the bulk of what a naive, undecomposed soft-bias
metric would report as "bias." The stigmatizing composite is smaller for uninsured/
underinsured variants (0.6% to 19.0% across models) but becomes the dominant signal for the
unhoused variant, where stigmatizing net% (25.1% to 78.9% across models) approaches or
exceeds the appropriate net% in five of six models (unhoused appropriate net%: 65.7%
Gemini-2.5-flash, 74.5% DeepSeek-chat, 28.4% Llama-3.3-70B, 7.4% Llama-3.1-8B, 0.2%
GPT-4o-mini). GPT-4o is the sole exception: its unhoused-variant appropriate net% is
negative (-6.4%) alongside a large stigmatizing net% (52.4%), meaning GPT-4o's
guideline-endorsed financial-counseling/social-work language was, on net, withdrawn rather
than added for this variant, at the same time its stigmatizing language rose — a
qualitatively different mechanism (appropriate care displaced by stigma) than the
"stigma added on top of stable appropriate care" pattern the other five models show. Because
this pattern appears in only one of six models and only for the single most disadvantaged
variant, we treat it as a real but model-specific anomaly rather than evidence of a general
appropriate-care-displacement mechanism; it does indicate that a stigma/appropriate
composite score summed across dimensions in a single model should not be assumed to
decompose additively, and that any deployed filter should be validated per-model rather
than assumed to generalize. Race-only and white-male-control variants showed near-zero net%
in both composites across all six models.

### Stigma Decomposes Into Defensible and Non-Defensible Narrative Elements (Figure 8)

When the four soft-framing dimensions are further split into a pre-registered
defensible-stigma composite (adherence-doubt, hallucinated SDOH) versus the two
non-defensible/ambiguous dimensions (prognosis framing, watchful-waiting suggestion), the
disadvantage gradient lives almost entirely in the defensible composite. Averaged across
all six models, defensible-composite net% rose monotonically from the white-male control
(near 0%) through race-only (near 0%), Black+Medicaid, uninsured, and underinsured, to
low-income and unhoused (highest). The non-defensible dimensions, by contrast, showed no
comparable gradient: their combined net% stayed within a narrow 0.0-0.4% band across all
seven variants from control to unhoused — roughly two orders of magnitude smaller than the
defensible-composite range and showing no monotone relationship with disadvantage. This
indicates the socioeconomic stigma signal reported above is concentrated in the two
dimensions with the clearest clinical-harm interpretation (an LLM doubting a patient's
adherence or inventing an SDOH problem unprompted), not diffused across all four
soft-framing dimensions indiscriminately.

### The Gradient Is Not an Artifact of Note Generation or Demographic-Label Salience (Figure 9)

Three independent controls tested whether the stigma gradient reflected a property of
model behavior rather than an artifact of the synthetic note-generation or
demographic-injection pipeline (Gemini and DeepSeek only, due to cost constraints across
the full grid). **Circularity control (Fig 9a):** on the same 100 cases, replacing the
LLM-generated free-text note with a fully deterministic, LLM-free template note left the
gradient intact — unhoused stigma rates were 76.0% (LLM note) vs. 84.0% (template) for
Gemini, and 80.0% vs. 92.0% for DeepSeek, while race-only and control rates remained near
zero under both note types for both models (0-7% range). **Real-note replication (Fig
9b):** substituting 40 real, open-access PubMed Central NSCLC case reports for the
GENIE-derived synthetic notes reproduced the same disadvantage gradient at a lower absolute
magnitude (Gemini: control 1.2%, race-only 4.2%, uninsured 10.0%, low-income 15.0%,
unhoused 32.5%; DeepSeek: control 1.2%, race-only 2.9%, uninsured 7.5%, low-income 10.0%,
unhoused 22.5%). **Salience-artifact control (Fig 9c):** injecting demographic information
as a bracketed tag versus weaving it into natural prose produced statistically
indistinguishable gradients for both Gemini (unhoused: +69pp tag vs. +74pp prose) and
DeepSeek (unhoused: +76pp tag vs. +83pp prose), with controls near zero under both
injection modes — ruling out demographic-label conspicuousness as the driver of the
effect.

### Full 29-Variant Summary: Flip Rate and Framing Effect Size (Table 2, Supplementary Table S3)

The five headline results above (Figures 4-9) foreground a subset of the 29 pre-registered
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
family is `rural_patient` (tier D, mean d=0.27, range 0.04-0.62) — smaller than every
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
an otherwise identical clinical note left the treatment recommendation largely stable —
guideline concordance was statistically equivalent between the no-demographics reference
and most demographic variants (equivalence for >=26 of 29 variants) in five of six models
(Llama-3.3-70B, Llama-3.1-8B, GPT-4o: 29/29; DeepSeek-chat: 27/29; GPT-4o-mini: 26/29),
with Gemini-2.5-flash the exception (equivalence for 14/29, an underpowered rather than a
positive-effect result — see Limitations), and only one of 174 grid-wide directional
decision tests surviving multiplicity correction. Yet the language surrounding
that stable recommendation changed substantially, and the shape of that change was
specific: race-only variants showed small effect sizes — an order of magnitude below the
socioeconomic variants and largely, though not uniformly, indistinguishable from the
near-zero control across models, while socioeconomic-disadvantage variants showed a
monotonically increasing, and in several models very large, stigmatizing-language effect.
This dissociation — a stable decision with a demographically patterned narrative — is not
an artifact of the synthetic-note pipeline: it replicated on LLM-free deterministic
template notes, on 40 real PubMed Central case reports, and under a natural-prose
demographic-embedding control that removed the conspicuous bracketed-tag format entirely.
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
race pattern: race-only Cohen's d remained small and largely — but not uniformly —
indistinguishable from zero (mean d -0.03 to 0.10) in every model we tested, while
socioeconomic-disadvantage effect sizes were an order of magnitude larger (0.26 to 1.16). This divergence may reflect differences in clinical domain (oncology
treatment selection vs. emergency triage), ground-truth structure (a guideline-anchored,
Category-1 NCCN answer set vs. urgency/invasiveness scoring), or genuine
model-family/version differences given the two-year gap between studies; we do not have
data to adjudicate between these explanations and flag it as an open question. The
divergence is unlikely to reflect idiosyncratic behavior of any single audited model: the
per-variant induced-framing-effect profile is highly correlated across all six models we
tested (Spearman rho of the 29-variant effect vector, pairwise across models; off-diagonal
median rho=0.72, Supplementary Figure S_intermodel_agreement), indicating the six models
substantially agree on which demographic variants provoke framing changes even though they
differ in the overall magnitude of that response. We also do
not reproduce Omar et al.'s LGBTQIA+-identity effect: across the three identity-tier
variants in our design (non-binary, transgender woman, gay male patient), flip rates
(11.2-23.8% across models) and soft-framing effect sizes (Cohen's d -0.03 to 0.13) were
comparable to the white-male-control and race-only null, not to the SES-large pattern —
consistent with our race finding, this suggests the demographic dimension driving framing
bias in this oncology, guideline-anchored design is specifically socioeconomic
disadvantage, not demographic identity broadly, though again a direct comparison across
these two studies' differing clinical domains and model vintages is not possible from our
data alone. Separately,
prior work on socioeconomic-status effects in clinical-trial-eligibility screening
language [3] has treated "soft" SES-associated differences as a single harm signal; our
appropriate/stigmatizing decomposition suggests that, at least in this design, a
substantial fraction of that signal for insured-but-disadvantaged variants (uninsured,
underinsured) is guideline-concordant financial and social-work responsiveness rather than
stigma, while the stigmatizing residue is concentrated specifically in the most severely
disadvantaged variant (unhoused). Finally, unlike audits of LLM behavior on
clinician-authored notes that already contain stigmatizing language [4], the stigmatizing
content here originates from the LLM itself, added to a note that, by construction,
contained no such content before the demographic label was applied — the mechanism is
generative, not inherited.

### Clinical and Deployment Implications

The dissociation between decision stability and narrative-framing bias has a direct
operational implication for LLM-integrated documentation tools: an audit or monitoring
system that checks only whether an ambient scribe's or inbox-drafting assistant's
*recommendation* changed by patient demographics will miss the harm this study
identifies, because the recommendation largely does not change. The narrative layer — the
free text that gets filed into the permanent record — is where the bias in this study
lives, and it is not currently a standard audit target for clinical LLM deployments. A
health system deploying such tools should audit generated free text specifically for
unprompted adherence-doubt and SDOH-hallucination language, stratified by patient
socioeconomic status, rather than relying solely on outcome/recommendation-level fairness
metrics — a lesson consistent with post-deployment audits of other clinical ML systems,
which have found that bias evaluated only at the point of initial validation can miss
disparities that emerge once a model is embedded in live care processes [13]. Equally important, an intervention that suppresses all socioeconomic-status
language indiscriminately would also suppress guideline-endorsed financial-counseling and
social-work referrals for patients who need them — the appropriate/stigmatizing
decomposition in Figure 6 and Figure 8 is intended as a template for building a filter that
removes the former without removing the latter, though we have not built or evaluated such
a filter here.

### Limitations

Several limitations qualify these findings and require disclosure before any deployment or
policy conclusion is drawn from this work.

**Single-rater stigma-label validation.** The stigma-detection judge was validated against
a 35-item gold set labeled by a single rater (the study author), achieving fair, not
substantial, agreement with the judge (Cohen's kappa=0.30) and with the underlying regex
classifier (kappa=0.21). This is a materially weaker validation than the two-independent-rater
standard typically expected for a bias-adjudication instrument, and it was not
possible within this study's scope to add a second blinded rater before this draft. All
absolute stigma-rate estimates in this manuscript should be read with this caveat in mind;
the qualitative pattern (near-zero race-only effect, monotone SES gradient, defensible/
non-defensible decomposition) is more robust to judge noise than any single point estimate,
since it depends on relative ordering across variants rather than an absolute threshold,
but this has not been formally tested.

**Judge is itself an LLM.** The stigma-detection judge used to adjudicate contested
keyword/pattern-classifier hits (Claude Sonnet-4.6) is itself a large language model, and
we have not tested whether the judge's own labeling behavior is confounded with the same
socioeconomic-disadvantage gradient this study measures — for example, whether the judge
is systematically more or less likely to label a response as stigmatizing when it concerns
a disadvantaged patient, independent of the response's actual content. The human-rater gold
set used for judge validation (Cohen's kappa=0.30) was labeled blind to demographic variant,
which bounds this concern for the adjudicated subset, but the judge's case-by-case behavior
on the full 31,440-response corpus has not been independently audited for a
disadvantage-correlated labeling bias. This is a substantive methodological question for
future work rather than one this manuscript resolves.

**Two-vendor scope for robustness controls.** The LLM-free template-note replication
(Figure 9a) and the real PubMed Central note replication (Figure 9b) were run on Gemini and
DeepSeek only, not all six audited models, due to per-call API cost constraints across the
full demographic-variant grid. These two controls demonstrate that the gradient is not an
artifact of note-generation or demographic-injection mechanics for at least two model
families; we cannot rule out a note-generation artifact specific to the other four models
without extending these controls to them, which is future work.

**Synthetic note generation.** While the underlying clinical facts (stage, histology,
biomarkers, treatment history) are drawn from real, de-identified GENIE BPC patient
records, the free-text clinical note presented to each audited model was itself generated
by an LLM (gemini-2.5-flash) rather than authored by a clinician. The circularity control
(template notes, Figure 9a) and the real-note replication (Figure 9b) both address this
concern directly and both show the gradient survives removing the LLM-generated note
entirely, which is the strongest available evidence against a note-generation circularity
explanation; we nonetheless flag the underlying note-generation step as a design choice
worth scrutiny in replication.

**Ground-truth scorer validation.** The NCCN concordance scorer is a deterministic,
rule-based decision tree that has not been validated against board-certified oncologist
adjudication on this specific cohort. Misclassifications in the scorer would affect
absolute concordance estimates for all models equally (since the same scorer is applied
uniformly across variants and models) but would not be expected to introduce a
demographic-variant-specific artifact, since the scorer has no access to demographic
information.

**Single-institution-mix cohort.** The cohort is drawn from three U.S. academic cancer
centers (MSK, DFCI, VICC) and is not a nationally representative sample; race/ethnicity
distribution in particular (79.1% Non-Hispanic White) reflects these centers' referral
populations rather than U.S. NSCLC demographics broadly, which may limit the generalizability
of absolute stigma-rate estimates, though the within-cohort demographic-variant comparison
(the study's core design) is unaffected by this since every variant is applied to the same
cohort.

**Deviation from pre-registered model panel.** The pre-registered audit panel
(PREREGISTRATION.md) specified five models including Claude Sonnet-4.6; Claude Sonnet-4.6
was not completed due to API credit constraints and does not appear in this manuscript.
Llama-3.1-8B and GPT-4o-mini, run to completion but not in the original pre-registered
panel, are reported here as exploratory, non-preregistered arms. All headline
dissociation, TOST, and gradient findings replicate across the four models that are both
pre-registered and complete (Gemini-2.5-flash, DeepSeek-chat, Llama-3.3-70B, GPT-4o), so
this substitution does not appear to drive the reported pattern, but it is a departure
from the registered protocol that should be weighed accordingly.

**Model and prompt scope.** All models were queried once per case-variant combination at
temperature 0 with a single baseline prompt; we did not assess prompt sensitivity,
multi-turn conversational drift, or newer model versions released after this study's data
collection concluded. The mitigation strategies referenced in the project's broader
research program (fairness-instructed prompting, structured extraction) are outside the
scope of this manuscript's primary analysis and are reported separately.

### Conclusions

In a large, real-world oncology cohort audited across six large language models, adding a
demographic label to an otherwise-identical clinical note left the guideline-concordant
treatment decision largely stable but reshaped the accompanying clinical narrative in a
pattern that tracked socioeconomic disadvantage, not race — a pattern that replicated
across model-free template notes, real clinical case reports, and a natural-language
salience control, and that concentrated in two narrative dimensions with clear stigma
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

8. [CancerGUIDE dataset / benchmark reference — author to insert full citation for the
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
    DAX, Abridge, Epic's GPT-4o inbox-drafting integration) — author to insert vendor
    press releases or peer-reviewed evaluations cited in the Introduction's
    deployment-harm framing.]

*Note: references 1-6 and 9-13 are verified against PubMed/PMC metadata (PMID, DOI, and
author list confirmed directly from NLM records) as of 2026-07-09. References 7, 8, and 14
remain placeholders requiring the author's citation-manager pass to insert the specific
guideline version, dataset citation, and deployment-vendor sources used.*
