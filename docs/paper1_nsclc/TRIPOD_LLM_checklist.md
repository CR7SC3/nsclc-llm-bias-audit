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
| 2 | **Abstract** — structured summary of objective, data, LLMs evaluated, task, evaluation methods, results, limitations. | ADDRESSED | Structured Abstract (L7-64): Background, Objective, Methods (cohort, 30 variants, six named LLMs, temperature 0, TOST/sign-test/BH-FDR, judge validation κ=0.30, robustness controls), Results (concordance equivalence, flip rates, one surviving directional test, SES gradient), Conclusions. Judge-agreement limitation stated in-abstract. |

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
| 10 | **Missing data** — how missing data were handled. | PARTIAL | PD-L1 untested coded as untested reflecting practice (L190-193); ECOG defaults to 1, PD-L1 missing 56%, 23 unlinked-panel cases (METHODS.md §5 "Known limitations"). **Missing: no explicit statement of how missing structured fields propagate into the concordance denominator in the manuscript body** — [add one sentence in Methods or point to METHODS.md §5]. |

## Methods — LLM / Model

| # | TRIPOD-LLM item | Status | Where addressed / what it says |
|---|---|---|---|
| 11 | **LLM identity & versioning** — name, version, provider, access route, date of access; base vs. fine-tuned. | ADDRESSED | "Models" (L215-232): six LLMs, five families, named with providers and access routes (Together AI, OpenRouter, OpenAI, Google, DeepSeek). All off-the-shelf base models. **PARTIAL sub-point:** exact API snapshot dates/version strings (e.g., `gpt-4o-2024-XX-XX`) not pinned in prose — [add access dates / model snapshot IDs; data-collection window is implied but not dated]. |
| 12 | **Prompt / task specification** — full prompt(s), prompt-engineering strategy, in-context examples, output format. | PARTIAL | Baseline recommendation prompt described (L225-227; METHODS.md §6 "Baseline"). **Missing from manuscript: the verbatim prompt text is not reproduced in the paper** — [add the full baseline prompt to a Supplement, or cite `prompts/evaluation/prompt_templates.py`]. |
| 13 | **Inference configuration** — temperature/decoding params, number of runs per input, determinism, context length. | ADDRESSED | Temperature 0, single query per case×variant, 31,440 calls per model, checkpoint/resume (L225-228). Single-run-at-temp-0 limitation disclosed (L742-748). |
| 14 | **Model development / training / fine-tuning** — training data, optimization, hyperparameters, internal validation. | N/A | Evaluation-only study of pre-trained, general-purpose LLMs; no training, fine-tuning, or hyperparameter optimization was performed. |
| 15 | **Model output → decision** — how free-text output was parsed/converted into the scored quantity. | ADDRESSED | "Outcome Measures" (L249-266) + METHODS.md §9 (ResponseParser, 10 canonical categories, first-match-wins ordering, known parser limitations). |

## Methods — Evaluation

| # | TRIPOD-LLM item | Status | Where addressed / what it says |
|---|---|---|---|
| 16 | **Evaluation methods / analysis** — statistical methods, performance/fairness metrics, equivalence testing, multiplicity control. | ADDRESSED | "Outcome Measures" (L249-301) + "Statistical Software" (L332-341): flip rate + Wilson CIs; TOST equivalence (margin d=±0.10); grid-wide BH-FDR over 174 tests; paired sign tests; Cochran-Armitage trend; Spearman cross-model agreement. |
| 17 | **Fairness / subgroup evaluation** — how demographic subgroups/counterfactuals were defined and compared. | ADDRESSED | Core design: 29 non-reference demographic variants vs. no-demographics reference; race-only-vs-SES contrast; appropriate/stigmatizing decomposition (L268-295). This is the study's central axis. |
| 18 | **Human evaluation / annotation** — annotator number, expertise, instructions, blinding, agreement. | PARTIAL | "Judge Validation" (L303-314): single rater (study author), blinded to variant, 35-item gold set, κ=0.30 (human-judge) / 0.21 (human-regex). Disclosed as single-rater limitation (L675-685). **PARTIAL because single-rater and fair (not substantial) agreement fall below the two-independent-rater norm** — honestly flagged, not concealed; no second rater added [would require a second blinded annotator to close]. |
| 19 | **LLM-as-judge** — if an LLM adjudicated outputs, identify it, its prompt, and validation against humans; risk of correlated bias. | ADDRESSED | Judge = Claude Sonnet-4.6 (L273-274), validated against the human gold set (L303-314); the risk that the judge's own labeling correlates with the disadvantage gradient is explicitly flagged as unresolved (L687-697). **Judge prompt text itself not reproduced** — [add to Supplement]. |
| 20 | **Uncertainty / robustness / sensitivity analyses** — robustness checks, ablations, sensitivity to design choices. | ADDRESSED | "Robustness Controls" (L316-330): (1) LLM-free template notes, (2) 40 PubMed Central real notes, (3) natural-prose salience control. Two-vendor scope of controls disclosed (L699-705). |
| 21 | **Sample size / power** — justification for number of cases/queries or acknowledgment of power limits. | PARTIAL | Full-cohort n=1,048 × 30 variants stated; Gemini's 14/29 equivalence explicitly framed as "underpowered rather than a positive-effect result" (L593, L727-731). **No formal a priori power calculation reported** — [note it was not performed, or add post-hoc power for the equivalence margin]. |

## Open Science / Reproducibility

| # | TRIPOD-LLM item | Status | Where addressed / what it says |
|---|---|---|---|
| 22 | **Data availability.** | ADDRESSED | Declarations "Data Availability" (L771-774): GENIE BPC via AACR access process (URL given); derived case-level outputs + variant-injection + analysis code in project repository. |
| 23 | **Code availability.** | ADDRESSED | Declarations "Code Availability" (L776-778) and Methods L332-336 (named scripts). **PARTIAL sub-point:** repository is referenced but no public URL/DOI is pasted — [insert repo URL / Zenodo DOI before submission]. |
| 24 | **Protocol / pre-registration** — availability of protocol/registration and any deviations. | ADDRESSED | PREREGISTRATION.md referenced; the five-model→six-model panel deviation (Claude Sonnet-4.6 dropped; Llama-3.1-8B, GPT-4o-mini added exploratory) is disclosed in Methods (L219-232) and Limitations (L733-741). |
| 25 | **Funding & conflicts of interest.** | PARTIAL | Declarations (L780-783): COI "none"; Funding is a bracketed placeholder [Author to insert funding source or "no external funding"]. **GAP on funding until author fills the placeholder.** |
| 26 | **Ethical approval / governance** — IRB/ethics determination, data-use agreement, consent or waiver. | GAP | "Ethical Considerations" (L343-349) states de-identified public GENIE data, no patient contact, no real treatment decisions — but does **not** state an explicit IRB/human-subjects determination (exempt / non-human-subjects / not-required). **GAP — add an explicit determination sentence** (see the ethics-replacement text delivered alongside this checklist). |

## Results

| # | TRIPOD-LLM item | Status | Where addressed / what it says |
|---|---|---|---|
| 27 | **Participants / flow** — case counts through the pipeline; descriptive characteristics. | ADDRESSED | Table 1 (L360-372): stage, histology, race/ethnicity, driver-mutation and PD-L1 availability counts. Cohort derivation in Methods L171-182. |
| 28 | **Model performance / main results** — primary and secondary results with uncertainty. | ADDRESSED | Results L374-525: flip rates with ranges, TOST equivalence counts per model, the single BH-FDR-surviving directional test (DeepSeek underinsured, q=0.0245), SES effect sizes, dose-response gradient, decomposition, robustness controls. Table 2 (L545-575) gives all 29 variants. |
| 29 | **Fairness / subgroup results** — subgroup/counterfactual results reported. | ADDRESSED | Figures 4-9 narrative (L374-525): race-only null vs. SES gradient, intersectional latina_female_uninsured d=1.62, appropriate/stigmatizing split, defensible/non-defensible split. |
| 30 | **Reporting of errors / failure modes** — qualitative failure analysis or notable error patterns. | ADDRESSED | GPT-4o appropriate-care-displacement anomaly (L476-485); parser known-misclassification risks (METHODS.md §9). |

## Discussion

| # | TRIPOD-LLM item | Status | Where addressed / what it says |
|---|---|---|---|
| 31 | **Interpretation** — of results in context of prior evidence and objectives. | ADDRESSED | "Principal Findings" (L585-608) and "Comparison With Prior Work" (L610-647): dissociation interpreted vs. Omar et al. [1], clinical-trial-screening work [3], inherited-stigma work [4]. |
| 32 | **Limitations** — of the study/data/LLM, incl. bias/generalizability. | ADDRESSED (with one scope gap) | "Limitations" (L670-748): single-rater validation, LLM-judge confound, two-vendor control scope, synthetic notes, scorer validation, single-institution-mix cohort, preregistration deviation, model/prompt scope. **GAP: English-language / US-only / NSCLC-only generalizability bound is not stated as its own limitation** — [add the scope sentence delivered alongside this checklist]. |
| 33 | **Usability / deployment / clinical implications & risks.** | ADDRESSED | "Clinical and Deployment Implications" (L649-668): audit the narrative layer not just the decision; do not indiscriminately suppress SES language; decomposition as a filter template (not built/evaluated here). |
| 34 | **Generalizability** — extent to which findings transfer to other settings/populations/models. | PARTIAL | Cohort non-representativeness (L725-731) and two-vendor control scope (L699-705) covered; broader language/geography/cancer-type transfer bound **not yet stated** — [close via the scope limitation sentence]. |

## Other Information

| # | TRIPOD-LLM item | Status | Where addressed / what it says |
|---|---|---|---|
| 35 | **Supplementary material** — availability of supplements/appendices. | ADDRESSED | Supplementary Table S3 (per-model 29-variant CSV, L577-579), Figure S0, S_intermodel_agreement referenced. |
| 36 | **Guideline adherence statement** — statement that a reporting guideline (TRIPOD-LLM) was followed, with completed checklist. | GAP | Not currently in the manuscript. **GAP — add the one-sentence Methods addition (below) naming TRIPOD-LLM and citing this completed checklist supplement.** |

---

## Summary of open GAPs (author action before submission)

1. **Item 26 (Ethics):** add explicit IRB/human-subjects determination sentence.
2. **Item 32/34 (Scope limitation):** add English-language / US-only / NSCLC-only generalizability sentence.
3. **Item 36 (Guideline statement):** add the TRIPOD-LLM adherence sentence citing this file.
4. **Item 12/19 (Prompts):** reproduce the verbatim baseline prompt and judge prompt in a Supplement.
5. **Item 11 (Versioning):** pin API model snapshot IDs and data-collection/access dates.
6. **Item 23/25 (Open science):** paste the public repository URL/DOI and resolve the Funding placeholder.
7. **Items 10, 21:** brief statements on missing-data propagation into the concordance denominator and on the absence of a formal a priori power calculation.

*Prepared as a TRIPOD-LLM reporting supplement for the NSCLC counterfactual-audit manuscript.
"ADDRESSED" reflects the manuscript state at the revision cited above; re-verify line
numbers after any edit.*
