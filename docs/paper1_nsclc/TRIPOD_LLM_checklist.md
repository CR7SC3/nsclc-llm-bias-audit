# TRIPOD-LLM Reporting Checklist — Paper 1 (NSCLC Counterfactual Audit)

**Guideline:** TRIPOD-LLM (Transparent Reporting of a multivariable prediction model
for Individual Prognosis Or Diagnosis — Large Language Models), the LLM-specific extension
of TRIPOD+AI. Gallifant J, Afshar M, Ameen S, et al. The TRIPOD-LLM reporting guideline
for studies using large language models in health care. *Nat Med*. 2025;31:60-69.
doi:10.1038/s41591-024-03425-5.

**Manuscript audited:** `docs/paper1_nsclc/manuscript_nsclc.md`
**Study type:** Task-based **evaluation / bias audit** of pre-existing, general-purpose LLMs
(no model development, fine-tuning, or training). Development/optimization items are marked
**N/A (evaluation-only study)** with a one-line justification, per TRIPOD-LLM guidance that
the checklist applies to the applicable modality (here: use/evaluation, not development).

**Completion status legend:**
- **ADDRESSED** — the manuscript reports this item; location + substance cited.
- **PARTIAL** — reported but incompletely; what is missing is noted.
- **GAP** — not currently addressed; the bracketed note states what is needed.
- **N/A** — item does not apply to an evaluation-only study of off-the-shelf LLMs.

---

## Title and Abstract

| # | TRIPOD-LLM item | Status | Where addressed / what it says |
|---|---|---|---|
| 1 | **Title** — identify the study as developing/evaluating an LLM, the health outcome/task, and the target population. | ADDRESSED | Title + subtitle (L1-3): "Stigma Without Downgrade: Separating Warranted Socioeconomic Responsiveness From Generated Stigma in LLM Cancer-Treatment Recommendations — A Counterfactual Audit of Six Large Language Models on 1,048 Real-World NSCLC Cases." Names the LLM evaluation, the counterfactual-audit design, the task (treatment recommendations), the population (NSCLC), and n. |
| 2 | **Abstract** — structured summary of objective, data, LLMs evaluated, task, evaluation methods, results, limitations. | ADDRESSED | Structured Abstract: Background, Objective, Methods (cohort, 30 variants, six named LLMs, temperature 0, TOST/sign-test/BH-FDR, the regex-based stigma classifier validated against a single-rater 60-item gold set at κ=0.77, with an independent LLM-judge cross-check at κ=0.57, robustness controls), Results (concordance equivalence, flip rates, two surviving directional tests, SES gradient), Conclusions. Judge-agreement limitation stated in-abstract. |

## Introduction

| # | TRIPOD-LLM item | Status | Where addressed / what it says |
|---|---|---|---|
| 3 | **Background & rationale** — clinical/scientific context, prior LLM work, and why the LLM approach is needed. | ADDRESSED | Introduction (L69-137): deployment context (ambient scribes, EHR-integrated drafting), medico-legal/documentation-integrity framing, prior bias-audit literature (Omar et al. [1], systematic review [2]), and the two named gaps (final-decision-only scoring; undifferentiated soft-bias composite). |
| 4 | **Objectives** — specific objectives/questions the study addresses. | ADDRESSED | Introduction L129-137: three explicit questions (decision change vs. equivalence margin; narrative change race vs. SES; appropriate vs. stigmatizing decomposition and replication). Restated as Objective in Abstract (L15-19). |

## Methods — Data

| # | TRIPOD-LLM item | Status | Where addressed / what it says |
|---|---|---|---|
| 5 | **Data sources** — describe the source of data and rationale. | ADDRESSED | "Data Source and Cohort" (L169-198): AACR Project GENIE BPC v2.0-public [5,6], structured fields converted to free-text notes by gemini-2.5-flash with CORAL notes as style anchors. METHODS.md §5 gives full pipeline. |
| 6 | **Participants / cases** — eligibility, setting, inclusion/exclusion, how cases were selected. | ADDRESSED | L171-182: three centers (MSK/DFCI/VICC), inclusion criteria (index NSCLC dx, known AJCC stage, ≥1 first-line regimen), stage/histology/race distributions. Table 1 (L360-372). |
| 7 | **Data preparation / preprocessing** — cleaning, harmonization, handling of structured→text conversion, de-identification. | ADDRESSED | L184-198 (biomarker extraction, panel-aware wildtype calling, PD-L1 resolution, note generation); METHODS.md §2 (demographic stripping) and §5 (GENIE pipeline). Data are de-identified at source (GENIE BPC). |
| 8 | **Inputs / predictors (prompt inputs)** — define the inputs presented to the LLM, incl. how demographic/context variables were encoded. | ADDRESSED | "Counterfactual Variant Design" (L200-213): 30 variants across nine tiers, bracketed demographic label prepended; clinical facts held constant. METHODS.md §4 lists all variants + injection mechanism. |
| 9 | **Outcome / reference standard** — define the target/label and how it was determined; blinding of outcome assessment. | ADDRESSED | "Ground Truth" (L234-247): deterministic NCCN Category-1 decision-tree scorer returning an acceptable-answer set; scorer has no access to demographic labels (outcome assessment blind to variant by construction). METHODS.md §8; scorer pinned NCCN NSCLC v6.2026. |
| 10 | **Missing data** — how missing data were handled. | ADDRESSED | "Imputed and missing structured fields" (Limitations): no case is excluded from the denominator; ECOG defaults to 1, untested PD-L1 routes to the chemoimmunotherapy pathway, and unlinked-panel biomarkers default to unknown — each stated explicitly as an imputation applied identically across all demographic variants, not a case exclusion. |

## Methods — LLM / Model

| # | TRIPOD-LLM item | Status | Where addressed / what it says |
|---|---|---|---|
| 11 | **LLM identity & versioning** — name, version, provider, access route, date of access; base vs. fine-tuned. | ADDRESSED | "Models" (L215-232): six LLMs, five families, named with providers and access routes (Together AI, OpenRouter, OpenAI, Google, DeepSeek). All off-the-shelf base models. **PARTIAL sub-point:** exact API snapshot dates/version strings (e.g., `gpt-4o-2024-XX-XX`) not pinned in prose — [add access dates / model snapshot IDs; data-collection window is implied but not dated]. |
| 12 | **Prompt / task specification** — full prompt(s), prompt-engineering strategy, in-context examples, output format. | ADDRESSED | Baseline recommendation prompt described in Methods; verbatim text now reproduced in full in "Supplementary Methods" (new "Verbatim baseline prompt" subsection). |
| 13 | **Inference configuration** — temperature/decoding params, number of runs per input, determinism, context length. | ADDRESSED | Temperature 0, single query per case×variant, 31,440 calls per model, checkpoint/resume (L225-228). Single-run-at-temp-0 limitation disclosed (L742-748). |
| 14 | **Model development / training / fine-tuning** — training data, optimization, hyperparameters, internal validation. | N/A | Evaluation-only study of pre-trained, general-purpose LLMs; no training, fine-tuning, or hyperparameter optimization was performed. |
| 15 | **Model output → decision** — how free-text output was parsed/converted into the scored quantity. | ADDRESSED | "Outcome Measures" (L249-266) + METHODS.md §9 (ResponseParser, 10 canonical categories, first-match-wins ordering, known parser limitations). |

## Methods — Evaluation

| # | TRIPOD-LLM item | Status | Where addressed / what it says |
|---|---|---|---|
| 16 | **Evaluation methods / analysis** — statistical methods, performance/fairness metrics, equivalence testing, multiplicity control. | ADDRESSED | "Outcome Measures" (L249-301) + "Statistical Software" (L332-341): flip rate + Wilson CIs; TOST equivalence (margin d=±0.10); grid-wide BH-FDR over 174 tests; paired sign tests; Cochran-Armitage trend; Spearman cross-model agreement. |
| 17 | **Fairness / subgroup evaluation** — how demographic subgroups/counterfactuals were defined and compared. | ADDRESSED | Core design: 29 non-reference demographic variants vs. no-demographics reference; race-only-vs-SES contrast; appropriate/stigmatizing decomposition (L268-295). This is the study's central axis. |
| 18 | **Human evaluation / annotation** — annotator number, expertise, instructions, blinding, agreement. | PARTIAL | "Judge Validation" (L303-314): single rater (study author), blinded to variant, 60-item gold set (natural ~10% stigma prevalence), judge–human agreement 91.7% (κ=0.57, PABAK 0.83). Disclosed as single-rater limitation (L675-685). **PARTIAL because single-rater falls below the two-independent-rater norm** — honestly flagged, not concealed; no second rater added [would require a second blinded annotator to close]. |
| 19 | **LLM-as-judge** — if an LLM adjudicated outputs, identify it, its prompt, and validation against humans; risk of correlated bias. | ADDRESSED | Judge = Claude Sonnet-4.6, validated against the human gold set; the risk that the judge's own labeling correlates with the disadvantage gradient is explicitly flagged as unresolved; verbatim judge rubric now reproduced in full in "Supplementary Methods" (new "Verbatim judge rubric" subsection). |
| 20 | **Uncertainty / robustness / sensitivity analyses** — robustness checks, ablations, sensitivity to design choices. | ADDRESSED | "Robustness Controls" (L316-330): (1) LLM-free template notes, (2) 40 PubMed Central real notes, (3) natural-prose salience control. Two-vendor scope of controls disclosed (L699-705). |
| 21 | **Sample size / power** — justification for number of cases/queries or acknowledgment of power limits. | ADDRESSED | Full-cohort n=1,048 × 30 variants stated; Gemini's 23/29 equivalence is characterized by its actual tier-shift CIs (small, tight, non-directional, present even for the privileged comparator) rather than asserted as "underpowered." "Model and prompt scope" (Limitations) now states explicitly that no formal a priori power calculation was performed and that sample size was fixed by cohort availability, not derived from a target effect size. |

## Open Science / Reproducibility

| # | TRIPOD-LLM item | Status | Where addressed / what it says |
|---|---|---|---|
| 22 | **Data availability.** | ADDRESSED | Declarations "Data Availability" (L771-774): GENIE BPC via AACR access process (URL given); derived case-level outputs + variant-injection + analysis code in project repository. |
| 23 | **Code availability.** | ADDRESSED | Declarations "Code Availability" (L776-778) and Methods L332-336 (named scripts). **PARTIAL sub-point:** repository is referenced but no public URL/DOI is pasted — [insert repo URL / Zenodo DOI before submission]. |
| 24 | **Protocol / pre-registration** — availability of protocol/registration and any deviations. | ADDRESSED | PREREGISTRATION.md referenced; the five-model→six-model panel deviation (Claude Sonnet-4.6 dropped; Llama-3.1-8B, GPT-4o-mini added exploratory) is disclosed in Methods (L219-232) and Limitations (L733-741). |
| 25 | **Funding & conflicts of interest.** | ADDRESSED | Declarations (L780-783): COI "none"; Funding states no external funding was received. |
| 26 | **Ethical approval / governance** — IRB/ethics determination, data-use agreement, consent or waiver. | ADDRESSED | "Ethical Considerations" states de-identified secondary analysis under the GENIE BPC data-use agreement, no patient contact, and that this did not constitute human-subjects research requiring IRB review — no formal IRB determination was sought. |

## Results

| # | TRIPOD-LLM item | Status | Where addressed / what it says |
|---|---|---|---|
| 27 | **Participants / flow** — case counts through the pipeline; descriptive characteristics. | ADDRESSED | Table 1 (L360-372): stage, histology, race/ethnicity, driver-mutation and PD-L1 availability counts. Cohort derivation in Methods L171-182. |
| 28 | **Model performance / main results** — primary and secondary results with uncertainty. | ADDRESSED | Results L374-525: flip rates with ranges, TOST equivalence counts per model, the two BH-FDR-surviving directional tests (both DeepSeek-chat: underinsured_only q=0.0017, latina_female_uninsured q=0.0026), SES effect sizes, dose-response gradient, decomposition, robustness controls. Table 2 (L545-575) gives all 29 variants. |
| 29 | **Fairness / subgroup results** — subgroup/counterfactual results reported. | ADDRESSED | Figures 4-9 narrative (L374-525): race-only null vs. SES gradient, intersectional latina_female_uninsured d=1.62, appropriate/stigmatizing split, defensible/non-defensible split. |
| 30 | **Reporting of errors / failure modes** — qualitative failure analysis or notable error patterns. | ADDRESSED | GPT-4o appropriate-care-displacement anomaly (L476-485); parser known-misclassification risks (METHODS.md §9). |

## Discussion

| # | TRIPOD-LLM item | Status | Where addressed / what it says |
|---|---|---|---|
| 31 | **Interpretation** — of results in context of prior evidence and objectives. | ADDRESSED | "Principal Findings" (L585-608) and "Comparison With Prior Work" (L610-647): dissociation interpreted vs. Omar et al. [1], clinical-trial-screening work [3], inherited-stigma work [4]. |
| 32 | **Limitations** — of the study/data/LLM, incl. bias/generalizability. | ADDRESSED | "Cohort representativeness and generalizability scope" (Limitations): single-rater validation, LLM-judge confound, two-vendor control scope, synthetic notes, scorer validation, single-institution-mix cohort, histology/smoking under-representation, English-language/US-specific/NSCLC-only scope, preregistration deviation, model/prompt scope, ordinal-scale ties, parser validity. |
| 33 | **Usability / deployment / clinical implications & risks.** | ADDRESSED | "Clinical and Deployment Implications": audit the narrative layer not just the decision; do not indiscriminately suppress SES language; decomposition as a filter template; a point-of-care sentence for the clinician reviewing an AI-drafted note before co-signing. |
| 34 | **Generalizability** — extent to which findings transfer to other settings/populations/models. | ADDRESSED | "Cohort representativeness and generalizability scope" (Limitations): cohort non-representativeness, two-vendor control scope, and an explicit statement that the pipeline is English-language and U.S.-specific and that transfer to other languages, health systems, countries, or cancer types is untested. |

## Other Information

| # | TRIPOD-LLM item | Status | Where addressed / what it says |
|---|---|---|---|
| 35 | **Supplementary material** — availability of supplements/appendices. | ADDRESSED | Supplementary Table S3 (per-model 29-variant CSV), Figure S0, S_intermodel_agreement referenced. |
| 36 | **Guideline adherence statement** — statement that a reporting guideline (TRIPOD-LLM) was followed, with completed checklist. | ADDRESSED | New "Reporting Guideline" subsection in Methods names TRIPOD-LLM and cites this completed checklist as a supplement. |

---

## Summary of open GAPs (author action before submission)

Items 10, 12, 19, 21, 25, 26, 32, 34, and 36 are now ADDRESSED (see table above) and removed
from this list. Remaining -- both require author-supplied information this audit cannot infer
from the repository (model identifiers in the code are floating aliases like `gemini-2.5-flash`,
not dated snapshots, and the results files are not git-tracked, so neither the exact API
version nor the run dates can be recovered from the repo itself):

1. **Item 11 (Versioning):** pin API model snapshot IDs and data-collection/access dates.
2. **Item 23 (Open science):** paste the public repository URL/DOI -- requires the author to make the repo public and optionally mint a DOI.

*Prepared as a TRIPOD-LLM reporting supplement for the NSCLC counterfactual-audit manuscript.
"ADDRESSED" reflects the manuscript state at the revision cited above; re-verify line
numbers after any edit.*
