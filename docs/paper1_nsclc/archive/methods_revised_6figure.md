<!--
Revised Methods, aligned to the locked 6-figure architecture (Fig 1 design; Fig 2 decision
invariance; Fig 3 care intensity; Fig 4 SES-not-race framing; Fig 5 stigma anatomy; Fig 6
robustness + precision filter). Written to match the existing manuscript_nsclc.md Methods
voice. Re-verify numerals against the results files before merge.
-->

## Methods

### Study Design

This is a counterfactual audit of six large language models' (LLMs) first-line treatment
recommendations and response framing on a real-world oncology cohort. Each clinical case is
presented to each model in 30 versions that differ only in a demographic label prepended to an
otherwise identical, demographics-neutral clinical note; all staging, histology, biomarker, and
performance-status information is held constant across the 30 versions of a case. Any systematic
difference in a model's recommendation or narrative framing across variants is therefore
attributable to the demographic label alone (counterfactual fairness [Kusner et al., 2017]). We
separate two axes of bias a priori, a **hard-bias** axis (whether the guideline-concordant
treatment decision changes) and a **soft-bias** axis (whether the language framing changes), and
report an intermediate **care-intensity** layer that sits between them (which treatment options a
response foregrounds, holding the decision fixed). Figure 1 summarizes the end-to-end workflow
(Figure 1A) and the counterfactual variant design (Figure 1B); the results follow a bias-severity
gradient from the invariant decision (Figure 2) through care intensity (Figure 3) to language
framing (Figures 4–5) and its robustness (Figure 6). Throughout, the reference/control is the
**`no_demographics` neutral anchor**; `white_male_private` is treated as a privileged demographic
variant, never as the baseline.

### Data Source and Cohort

The primary cohort is 1,048 real, de-identified non-small-cell lung cancer (NSCLC) cases from the
AACR Project GENIE Biopharma Collaborative (v2.0-public) [5,6], drawn from three academic cancer
centers (Memorial Sloan Kettering [MSK], n=556; Dana-Farber Cancer Institute [DFCI], n=343;
Vanderbilt-Ingram Cancer Center [VICC], n=149). Inclusion criteria were an index NSCLC diagnosis,
known AJCC stage, and at least one documented first-line treatment regimen. The cohort spans Stage
IV (n=594, 56.7%), Stage III (n=251, 23.9%), and Stage I–II (n=203, 19.4%) disease; histology is
predominantly adenocarcinoma (n=884, 84.4%) with squamous (n=123, 11.7%) and not-otherwise-
specified (n=41, 3.9%) carcinoma. The race/ethnicity distribution (Non-Hispanic White 79.1%,
Asian/Pacific Islander 8.4%, Non-Hispanic Black 5.6%, Hispanic/Latinx 1.8%, unknown/other 5.1%)
reflects the demographics of the contributing academic centers rather than the U.S. NSCLC
population. Cohort characteristics are given in Table 1.

GENIE BPC provides structured clinical and genomic fields, not free-text notes. Biomarker status
(EGFR, ALK, ROS1, BRAF, MET exon-14 skipping and amplification, KRAS G12C, ERBB2 exon-20
insertion, RET, NTRK, STK11, KEAP1) was extracted from somatic mutation, structural fusion, and
copy-number files and mapped to each case's sequencing panel; genes not covered by a given panel
were coded `not_on_panel` rather than negative, correcting a false-negative failure mode on
narrower panels. PD-L1 tumor proportion score was resolved from pathology-report-level data for
377 patients (36.0%); cases tested before the era of routine PD-L1 testing (pre-2016) are coded
untested, reflecting real clinical practice rather than missing data. Each structured case profile
was converted into a demographics-neutral free-text consultation note by `gemini-2.5-flash`, using
de-identified CORAL oncology notes as style anchors only; the note-generation prompt excludes any
demographic content, which is added exclusively in the subsequent variant-injection step.

### Counterfactual Variant Design

Thirty demographic variants were injected per case across nine tiers: (A) intersectional race ×
insurance profiles (5 variants, including the `white_male_private` reference variant, replicating
Omar et al.'s design), (B) insurance status alone (5: uninsured, Medicaid, Medicare, Medicare
Advantage, underinsured), (C) race/ethnicity alone (6), (D) geography (2: rural, small community
hospital), (E) age (1: elderly, age 75), (F) immigration/language (2), (G) socioeconomic status
alone (3: unhoused, low-income, high-income), (H) race × socioeconomic-status intersections (2),
and (I) gender/sexual identity (3), 29 variants in total across tiers A–I, plus the
`no_demographics` neutral anchor, for 30 versions per case (grouped, for reporting, into seven
demographic axes). A single bracketed demographic label was prepended to the note (e.g., "[PATIENT
DEMOGRAPHICS: Black female patient, Medicaid]"), with no narrative context beyond the label
itself, isolating the demographic signal from any confounding narrative-style change.

### Models

Six LLMs from five model families were evaluated: Gemini-2.5-flash (Google), DeepSeek-chat
(DeepSeek), Llama-3.3-70B-Instruct-Turbo and Llama-3.1-8B-Instruct (Meta, via Together AI and
OpenRouter respectively), and GPT-4o and GPT-4o-mini (OpenAI). All models were queried at
temperature 0 with an identical baseline clinical-recommendation prompt across all 1,048 cases ×
30 variants (31,440 calls per model; 188,640 responses in total); results were checkpointed after
every call and resumed automatically on interruption. Two robustness controls (LLM-free
deterministic template notes and real PubMed Central case-report replication, below) were run on
Gemini and DeepSeek only, owing to per-call cost across the full six-vendor grid; this scope is
disclosed rather than presented as six-vendor representativeness.

### Ground Truth

NCCN Category 1 treatment concordance was determined by a deterministic decision-tree scorer
encoding the NCCN NSCLC guideline [7] (stage, histology, ECOG performance status, resectability,
and the biomarker cascade EGFR/ALK/ROS1/BRAF/MET/RET/NTRK/PD-L1, in priority order), returning the
full set of NCCN-acceptable first-line regimens for each case rather than a single answer, since
multiple Category 1-equivalent options exist for many biomarker profiles (e.g., three ALK
inhibitors, or pembrolizumab monotherapy versus chemoimmunotherapy for high-PD-L1 Stage IV
disease). A response was scored concordant if its parsed treatment category matched any entry in
the case's acceptable-answer set. This scorer requires validation by a board-certified oncologist
before any clinical or patient-facing use and is presented strictly as a research ground-truth
instrument; NCCN guidelines are updated multiple times per year and the encoded logic reflects
versions current as of mid-2026.

### Outcome Measures

**Primary, treatment-recommendation flip rate (confirmatory).** The proportion of cases where a
variant's parsed treatment category differs from the `no_demographics` reference, reported with
Wilson 95% confidence intervals and averaged across the six models (Figure 2B). Averaged across
models, every demographic variant, including the privileged `white_male_private` variant, flips
at ≈17%, i.e. adding any label perturbs the recommendation by the same test–retest/label-salience
floor rather than by demographic content.

**Primary, NCCN guideline concordance (confirmatory).** Tested for statistical equivalence between
the no-demographics reference and each demographic variant using two one-sided tests (TOST) on the
paired treatment-tier shift (Cohen's d), with a pre-specified equivalence margin of d = ±0.10;
equivalence is declared only when the tier-shift 95% CI lies entirely within the margin, not on a
failure to reject a null of no difference (Figure 2A). Equivalence holds on 27–29/29 variants for
five models and 23/29 for Gemini-2.5-flash; the non-equivalent variants are underpowered
(tier-shift CIs extend past the margin but with deltas < 1.1 pp) rather than demonstrating a
demographic shift, so the claim is reported per-model.

**Primary, directional decision test (confirmatory).** Among cases where the treatment category
changed, a signed treatment-aggressiveness-tier shift (1 = best supportive care … 8 = surgical
resection) was tested with a paired sign test (downgrade vs. upgrade), corrected with a single
grid-wide Benjamini-Hochberg (BH) false-discovery-rate procedure across the full model × variant
family (6 models × 29 non-reference variants = 174 tests). The per-model, per-variant net tier
shift is shown in Figure 2C; two cells survive correction (DeepSeek, underinsured and
Latina-uninsured) and the residual signal is small and concentrated on socioeconomic-disadvantage
variants.

**Secondary, care-intensity direction (Figure 3).** Holding the primary regimen fixed, we scored
whether each response mentioned a clinical trial (advanced treatment) or palliative /
best-supportive care (de-escalation), as a within-case net change versus the `no_demographics`
reference detected by `src.analyze.soft_bias.detect_asymmetry` and aggregated per (variant, model)
cell. Reduced trial mention and increased de-escalation under a marginalization label were defined
a priori as the harm direction. To avoid pseudo-replicating the six correlated vendors, the
inferential test is a **linear mixed-effects model with a random intercept per model**
(`net_change ~ 1 + (1 | model)`), fit on the per-(variant × model) aggregate cells, collapsing the
case dimension into each cell's net percentage, with per-axis-group effects BH-FDR-corrected
across the axis-group family; the accompanying descriptive evidence is the cross-vendor sign
concordance (k of 6 vendors in the harm direction). The race-only axis is included in this
analysis so that care-intensity coverage matches the full variant design. Pooled across
marginalized labels, advanced treatment shifts −1.4 pp (95% CI −2.3, −0.5; p = 0.002) and
de-escalation +1.1 pp (95% CI 0.2, 2.0; p = 0.016); the privileged comparator is null.

**Secondary, soft-framing intensity and appropriate/stigmatizing decomposition (Figures 4–5).** A
continuous soft-framing intensity score was computed per response from eight linguistic dimensions
(financial-barrier language, social-work referral, specialist/multidisciplinary referral,
clinical-trial mention, adherence/compliance doubt, unprompted social-determinants-of-health
[SDOH] generation, prognosis framing, and watchful-waiting), each detected via a keyword/pattern
classifier and adjudicated by an LLM judge (Claude Sonnet-4.6). A ninth dimension
(palliative/best-supportive-care framing) is detected but excluded from this composite because it
fires on clinically appropriate end-of-life discussion independent of demographic framing.
Consistent with NCCN guidance that financial-counseling and social-work referral are appropriate
responses to disclosed socioeconomic barriers, the eight dimensions were partitioned a priori into
a **stigmatizing** composite (adherence/compliance doubt, prognosis framing, unprompted SDOH
generation, watchful-waiting) and an **appropriate** composite (financial-barrier language,
social-work referral, specialist referral, clinical-trial mention); the pre-registered defensible
stigma composite is adherence-doubt plus hallucinated SDOH. Each composite's net percentage (cases
adding the framing minus cases removing it, vs. reference) was tested with a paired sign test and
BH-FDR-corrected within its own family (Figure 5A–B). Per-variant, per-model effect sizes (Cohen's
d) for the continuous score against the reference localize the framing shift to the socioeconomic
axes (Figure 4A, 4C); the marginal race effect at fixed SES (Black + unhoused minus unhoused) is
−0.08 (95% CI −0.18, +0.01; ns), isolating the race increment with disadvantage held constant
(Figure 4C inset).

**Secondary, dose-response trend (Figure 5C).** To test whether the stigmatizing-rate gradient
across disadvantage strata is monotone rather than visually suggestive, a Cochran-Armitage trend
test was applied per model across the five ordered socioeconomic-disadvantage strata (control <
uninsured < underinsured < low income < unhoused), using ordinal tier
scores as the trend variable. The monotone-with-disadvantage direction was pre-registered
(hypotheses H2/H3), and the ordinal ranking follows an external SES-severity rationale fixed before
the per-stratum rates were seen, so the test is confirmatory of a pre-registered direction rather
than an ordering fit to the data. The test showed a significant increasing trend in five of six models (p < 0.001; GPT-4o-mini z = 1.3,
p = 0.20). Race-only carries no socioeconomic disadvantage and is excluded from the ladder, instead
compared to control directly.

**Secondary, cross-model agreement (Figure 4B).** To assess whether the framing dissociation
reflects a shared demographic-response mechanism rather than one model's idiosyncrasy, the
29-variant induced soft-framing-effect vector (Cohen's d per variant) was compared pairwise across
the six models with Spearman rank correlation; the off-diagonal median is ρ = 0.72, strong within
the Gemini/Llama/DeepSeek cluster (ρ = 0.82–0.91) and weaker for the GPT family (ρ = 0.58–0.62).

### Judge Validation

Following precedent for LLM-based detection of stigmatizing clinical language at scale [12], the
keyword/pattern classifier and the LLM judge were validated against a human gold set. The gold
set comprised 60 responses drawn uniformly at random (seed
17) from the Gemini and DeepSeek arms, preserving the natural stigma prevalence (~10%), labeled by
the study author (single rater), blinded to demographic variant, into STIGMA / APPROPRIATE /
NEUTRAL, then binarized to STIGMA vs. not. On this set, judge–human agreement was 91.7% (Cohen's
kappa = 0.57, PABAK 0.83), regex–human agreement 95.0% (kappa = 0.77, PABAK 0.90), and the
deterministic bias decision-tree (below)–human agreement 93.3% (kappa = 0.68, PABAK 0.87); because
the tree only ever downgrades a regex-flagged response, a flagged response that the tree does not
adjudicate retains its stigma flag. At the observed ~10% prevalence (6–9 items in the STIGMA cell), the kappa point estimates are
base-rate-fragile and cannot statistically rank the three instruments; raw agreement and PABAK are
therefore the stable, reportable quantities. Reported stigma rates use the raw regex composite
(adherence doubt OR hallucinated social-determinants content). The gold set was labeled by a
single rater; a second independent blinded rater is pending, a disclosed limitation.

### Bias Decision-Tree Precision Filter

To test whether the stigma signal survives a stricter, grounding-aware definition, each
regex-flagged response was routed through a deterministic bias decision-tree (`src/analyze/
bias_tree.py`) that renders the human adjudication rubric as an explicit gate cascade: Gate 0, does
any adherence/SDOH pattern fire (this gate is the regex composite, so tree recall is bounded by the
regex, it can only reclassify flagged responses, never recover a missed stigma); Gate 1, is the
framing a negative assumption rather than supportive language; Gate 2, is the concern grounded in
the clinical note itself (or in generic all-patients counseling) rather than in the demographic
label alone; and Gate 3, does it impute an invented individual defect rather than offer a pure
resource. The central rule is that a demographic label is never, by itself, clinical grounding.
Responses surviving all gates are labeled STIGMA and assigned a descriptive harm subtype
(allocative, epistemic-injustice, or dignitary). The tree rubric was specified before per-cell
outcomes; it is a precision-and-interpretability cross-check, not the primary detector, headline
stigma rates remain the judge-adjudicated regex composite. Routed over the flags, the tree
reclassifies 40.6% as benign and, as the conservative primary estimate, sits below the raw regex
flag (an upper bound) at every stratum while removing flags proportionally more in low-disadvantage
strata; the socioeconomic gradient survives the stricter definition (Figure 6D).

### Robustness Controls

Three controls tested whether the stigma gradient was an artifact of the note-generation or
demographic-injection pipeline rather than a property of model behavior (Gemini and DeepSeek).
**(1) LLM-free template-note replication (Figure 6A):** cases were re-notated with fully
deterministic, non-LLM string templates in place of the `gemini-2.5-flash`-generated free-text
notes and re-run through the full 30-variant pipeline, ruling out circularity from LLM note
generation. **(2) Real clinical-note replication (Figure 6B):** 40 open-access PubMed Central NSCLC
case reports were substituted for the synthetic notes and re-run through the same pipeline; the
gradient's direction is preserved on genuine clinical prose, with magnitude attenuated (roughly
halved) at n = 40 and correspondingly wide confidence intervals, a real but partial replication.
**(3) Natural-embedding salience control (Figure 6C):** for 150 cases, demographics were injected
either as the standard bracketed tag or woven into natural prose, testing whether the gradient
depended on the conspicuousness of the demographic signal rather than its content; the gradient
survives both injection modes.

### Statistical Software and Reproducibility

All analyses were implemented in Python (scipy, statsmodels, pandas) and are reproducible from the
project repository (`scripts/nsclc/analyze_results_v2.py`, `scripts/nsclc/
analyze_advanced_care_per_model.py`, `plots/plot_fig3_care_intensity.py`,
`plots/plot_circularity_ci.py`, `plots/plot_pmc_replication.py`). Wilson score confidence intervals
were used throughout for proportions given values near 0 and 1 at moderate sample sizes. Because
the design is repeated-measures, each case contributes several responses to the pooled race-only
(six variants) and control (two variants) strata, so per-stratum stigma rates were re-estimated
with a case-clustered percentile bootstrap (10,000 resamples, resampling on the case;
`scripts/nsclc/bootstrap_panel_ci.py`) to confirm the Wilson intervals were not anticonservative
under within-case correlation; clustered and Wilson 95% intervals agreed to within 0.2 percentage
points for every model and stratum (Supplementary Table S4). For the care-intensity outcome (Figure
3), inference used a linear mixed-effects model with a random intercept per model on the per-(variant
× model) aggregate cells, so the six correlated vendors are not treated as independent trials.
Grid-wide BH-FDR correction was applied once across each metric family described above, not
per-model or per-figure, to avoid understating the effective multiple-comparisons burden.

### Ethical Considerations

This study used de-identified, publicly-available-under-data-use-agreement GENIE BPC records and did
not involve identifiable patient information or direct patient contact. The NCCN concordance scorer
is a research instrument only and is explicitly not validated for clinical or patient-facing use. No
treatment decisions in this study affected real patients.
