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
| 1 | **Title** — identify the study as developing/evaluating an LLM, the health outcome/task, and the target population. | ADDRESSED | Title (L1): "Sociodemographic Bias in LLM Lung Cancer Treatment Recommendations and Rationales." Names the LLM evaluation, the task (treatment recommendations and rationales), and the population (lung cancer). It does not name the counterfactual-audit design or the appropriate/stigma decomposition the way an earlier draft title did — consider whether a more dissociation-forward title better satisfies this item's "identify the study as evaluating" intent before submission. |
| 2 | **Abstract** — structured summary of objective, data, LLMs evaluated, task, evaluation methods, results, limitations. | ADDRESSED | Structured Abstract (L9-49): Background (L11-14), Objectives (L16-18), Methods (L20-24: 1,048-case GENIE BPC cohort, 29 demographic variants across nine categories, 30 versions/case with the no-demographics reference, six LLMs, 188,640 responses), Results (L26-39: 163/174 comparisons within the ±0.10 equivalence margin, framing dissociation by SES vs. race up to d=1.01, unhoused flagged language 2%→47% raw / 38% grounding-aware, flagged "single-rater validated and provisional; see Limitations" [L38, current wording as of this revision — a prior draft said "provisional pending a second rater," now stale since one of two second-rater packets has since landed]), Conclusions (L41-46). **Note (verified accurate):** the abstract does **not** name any of the six LLMs individually (it says only "Six state-of-the-art LLMs"), and it does **not** use the terms "TOST," "sign-test," or "BH-FDR" anywhere — those method names are confined to the main-text Methods (Outcome Measures, L217-225) and do not appear in the Abstract at all. It also does not state the validation kappa values (0.77/0.57/0.68); those live only in Methods (Judge Validation, L227-242) and Limitations (L614-641). Item status is unaffected (the abstract still discloses the single-rater validation limitation in-text at L38), but the prior description of what the abstract literally says overstated its statistical/model-naming specificity. |

## Introduction

| # | TRIPOD-LLM item | Status | Where addressed / what it says |
|---|---|---|---|
| 3 | **Background & rationale** — clinical/scientific context, prior LLM work, and why the LLM approach is needed. | ADDRESSED | Introduction (L54-68): deployment context (ambient scribes, EHR-integrated drafting), documentation-persistence framing, prior bias-audit literature (Omar et al. [1], systematic review [2]), and the two named measurement gaps (decision-only scoring; undifferentiated soft-bias composite). |
| 4 | **Objectives** — specific objectives/questions the study addresses. | ADDRESSED | Introduction L66 ("We ask, in sequence: ..."): three explicit questions (decision change vs. equivalence margin; narrative change race vs. SES; appropriate-vs-stigmatizing decomposition and cross-note replication). Restated as Objectives in Abstract (L16-19). |

## Methods — Data

| # | TRIPOD-LLM item | Status | Where addressed / what it says |
|---|---|---|---|
| 5 | **Data sources** — describe the source of data and rationale. | ADDRESSED | "Data Source and Cohort" (L93-102, L160-168): AACR Project GENIE BPC v2.0-public [5,6], structured fields converted to free-text notes by gemini-2.5-flash using de-identified CORAL oncology notes [32] as style anchors only. |
| 6 | **Participants / cases** — eligibility, setting, inclusion/exclusion, how cases were selected. | ADDRESSED | L93-102: three centers (MSK/DFCI/VICC), inclusion criteria (index NSCLC diagnosis, known AJCC stage, ≥1 first-line regimen), stage/histology/race distributions. Table 1 (L104-153). |
| 7 | **Data preparation / preprocessing** — cleaning, harmonization, handling of structured→text conversion, de-identification. | ADDRESSED | L160-168: biomarker extraction with panel-aware not_on_panel coding (avoiding a false-negative on narrow panels), PD-L1 resolution, note generation. Data are de-identified at source (GENIE BPC). |
| 8 | **Inputs / predictors (prompt inputs)** — define the inputs presented to the LLM, incl. how demographic/context variables were encoded. | ADDRESSED | "Counterfactual Variant Design" (L170-190): 29 variants across nine sociodemographic categories plus the no_demographics anchor (30 versions/case), a single bracketed demographic tag prepended, clinical facts held constant. |
| 9 | **Outcome / reference standard** — define the target/label and how it was determined; blinding of outcome assessment. | ADDRESSED | "Reference Standard" (L201-216): deterministic NCCN Category-1 decision-tree scorer returning an acceptable-answer set, blind to demographic label by construction; scorer pinned to NSCLC v6.2026, with the v1.2025→v6.2026 rescoring delta disclosed (L211-215: -3.0 to +0.4 pp per model in absolute concordance, an asymmetric range, not ±3.0 pp; every demographic-vs-reference differential unchanged within 0.5 pp). |
| 10 | **Missing data** — how missing data were handled. | ADDRESSED | Panel-aware `not_on_panel` coding (L163); Limitations NCCN-scorer paragraph (L660-670): ECOG defaults to 1 (not recorded in GENIE BPC), untested PD-L1 routes to the chemoimmunotherapy pathway, unlinked-panel biomarkers default to unknown — each an imputation applied identically across all demographic variants, not a case exclusion. |

## Methods — LLM / Model

| # | TRIPOD-LLM item | Status | Where addressed / what it says |
|---|---|---|---|
| 11 | **LLM identity & versioning** — name, version, provider, access route, date of access; base vs. fine-tuned. | PARTIAL | "Models" (L192-199): six LLMs, five families, named with providers. **GAP:** exact API snapshot IDs/dates (e.g., a dated `gpt-4o-2024-XX-XX` string) are not pinned in prose — the code's model identifiers are floating aliases (`gemini-2.5-flash`, etc.), not dated snapshots, and this cannot be reconstructed from the repository alone. Author action required before submission. |
| 12 | **Prompt / task specification** — full prompt(s), prompt-engineering strategy, in-context examples, output format. | ADDRESSED | Baseline recommendation prompt summarized in Methods; verbatim text reproduced in full under "Verbatim baseline prompt" (Supplementary Methods, L1049-1069). |
| 13 | **Inference configuration** — temperature/decoding params, number of runs per input, determinism, context length. | ADDRESSED | Temperature 0, one query per case × variant, 31,440 calls/model (L192-199). Single-run-at-temp-0 limitation disclosed in the design-scope paragraph of Limitations (L704-716: "prompt sensitivity, multi-turn drift, and newer model versions were not tested"). |
| 14 | **Model development / training / fine-tuning** — training data, optimization, hyperparameters, internal validation. | N/A | Evaluation-only study of pre-trained, general-purpose LLMs; no training, fine-tuning, or hyperparameter optimization was performed. |
| 15 | **Model output → decision** — how free-text output was parsed/converted into the scored quantity. | ADDRESSED | "Outcome Measures" (L217-226) describes conversion to treatment category and framing score; parser construction and known limitations (no drug-name negation handling, unvalidated against an independent human-coded gold set) are disclosed in Limitations (L643-656). |

## Methods — Evaluation

| # | TRIPOD-LLM item | Status | Where addressed / what it says |
|---|---|---|---|
| 16 | **Evaluation methods / analysis** — statistical methods, performance/fairness metrics, equivalence testing, multiplicity control. | PARTIAL | "Outcome Measures" (L217-226) + "Statistical Software and Reproducibility" (L270-278): flip rate + Wilson CIs; TOST equivalence; grid-wide BH-FDR over 174 tests; paired sign tests; Cochran-Armitage trend; Spearman cross-model agreement. **Flag for author reconciliation:** the equivalence margin is stated as "±0.10 tier-scale units" (raw mean tier difference) at L219/L304/L936ish in the main text, while the pre-registration (`PREREGISTRATION.md`) defines it as Cohen's d = ±0.10 (a standardized effect size), and the exploratory mitigation analysis reports its own TOST result in Cohen's d (L603, L1349-1354) against a margin still labeled "tier-scale units." These are not interchangeable units unless the tier-shift SD≈1, which is unverified. Reconcile to one unit/margin before submission — this is the primary decision-stability claim, not a footnote-level detail. |
| 17 | **Fairness / subgroup evaluation** — how demographic subgroups/counterfactuals were defined and compared. | ADDRESSED | Core design: 29 non-reference demographic variants vs. no-demographics reference; race-only-vs-SES contrast; appropriate/stigmatizing decomposition (Outcome Measures, L223; Results L396-427). |
| 18 | **Human evaluation / annotation** — annotator number, expertise, instructions, blinding, agreement. | PARTIAL | "Judge Validation" (L227-245): the 60-item gold set was labeled by a single rater (the study author), blinded to variant, at ~10% natural STIGMA prevalence; regex-human 95.0% (κ=0.77, PABAK 0.90), judge-human 91.7% (κ=0.57, PABAK 0.83), tree-human 93.3% (κ=0.68, PABAK 0.87). A second rater has since scored one of two planned validation packets: the classifier-flagged/contested subset (n=60, 71.7% agreement, κ=0.386; Limitations L622-641). That rater is a co-author, blinded to variant but not a fully independent third party — disclosed explicitly as a practical deviation (L626-628). The representative packet underlying the headline agreement figures (`gold_random_rater2.csv`) remains unlabeled. **PARTIAL because the two-independent-rater norm is not met**, and the completed second-rater check (co-author, contested subset) found the raw classifier over-counts on that hard tail (43/60 concordant items, 27.9% consensus STIGMA vs. the classifier's 100%-positive rate by construction) — honestly disclosed, not concealed, but still open pending a genuinely independent rater and the representative-packet result. |
| 19 | **LLM-as-judge** — if an LLM adjudicated outputs, identify it, its prompt, and validation against humans; risk of correlated bias. | ADDRESSED | Judge = Claude Sonnet-4.6, validated against the single-rater human gold set (L227-245); the risk that the judge's own labeling correlates with the disadvantage gradient is flagged as unresolved beyond the adjudicated subset (Limitations, L636-641). Verbatim judge rubric reproduced in full under "Verbatim judge rubric" (Supplementary Methods, L1072-1094). |
| 20 | **Uncertainty / robustness / sensitivity analyses** — robustness checks, ablations, sensitivity to design choices. | ADDRESSED | "Robustness Controls" (L259-269): (1) LLM-free template notes, (2) 40 PubMed Central real notes, (3) natural-prose salience control. Results in "The gradient is robust to pipeline artifacts and to a stricter definition" (L428-471). Two-vendor scope of all three controls disclosed (Limitations, L674-691). |
| 21 | **Sample size / power** — justification for number of cases/queries or acknowledgment of power limits. | ADDRESSED | Full-cohort n=1,048 × 30 versions/case (29 variants + no-demographics reference) stated throughout Methods (Study Design L76-91; Models L194-196, 31,440 calls/model). Design-scope paragraph of Limitations (L704-716; "no formal a priori power calculation" at L714) states explicitly that no formal a priori power calculation was performed, that the design was fixed by GENIE BPC cohort availability rather than a target effect size, and that realized per-model sample sizes (n>1,000 paired comparisons/variant) yield narrow CIs in practice. |

## Open Science / Reproducibility

| # | TRIPOD-LLM item | Status | Where addressed / what it says |
|---|---|---|---|
| 22 | **Data availability.** | ADDRESSED | Declarations "Data Availability" (L740-745): GENIE BPC via AACR access process (URL given); derived case-level outputs, variant-injection code, and analysis scripts at a stated repository URL; raw per-model response files available on request. |
| 23 | **Code availability.** | ADDRESSED | Declarations "Code Availability" (L759-761): `https://github.com/CR7SC3/nsclc-llm-bias-audit`, MIT license. This closes the prior GAP (repo URL was previously unpasted). **Author action before submission:** confirm the repository is actually public (not just referenced) — this checklist can verify the manuscript states a URL, not that the URL currently resolves; consider minting a Zenodo DOI for a citable, versioned snapshot at submission time rather than a live URL that can change. |
| 24 | **Protocol / pre-registration** — availability of protocol/registration and any deviations. | ADDRESSED | Declarations "Pre-Registration" (L747-753): `PREREGISTRATION.md`, honestly framed as "a repository-hosted record with an author-declared lock date, not a third-party-timestamped registry entry." The five-model→six-model panel deviation (Claude Sonnet-4.6 dropped from the confirmatory arm, retained as judge; Llama-3.1-8B, GPT-4o-mini added exploratory) is disclosed in the design-scope paragraph of Limitations (L704-709). |
| 25 | **Funding & conflicts of interest.** | ADDRESSED | Declarations (L763-768): COI "none"; Funding states no external funding was received. |
| 26 | **Ethical approval / governance** — IRB/ethics determination, data-use agreement, consent or waiver. | ADDRESSED | "Ethical Considerations" (L279-287) and Declarations "Ethics Approval" (L755-757): de-identified secondary analysis under the GENIE BPC data-use agreement, no patient contact, self-determined as not constituting human-subjects research requiring IRB review. **Advisory note (not a checklist gap, but likely to be raised by a JMIR AI editor):** this is an investigator self-determination, not a formal IRB exemption letter; some journals require the latter even for de-identified secondary-data studies — confirm your institution's policy permits self-determination, or obtain a formal exemption letter before submission. |

## Results

| # | TRIPOD-LLM item | Status | Where addressed / what it says |
|---|---|---|---|
| 27 | **Participants / flow** — case counts through the pipeline; descriptive characteristics. | ADDRESSED | Table 1 (L104-153): institution, age, sex, race/ethnicity, AJCC stage, histology, smoking history, biomarker-positive status, PD-L1 availability. Cohort derivation cross-referenced in "Cohort" (L290-296). |
| 28 | **Model performance / main results** — primary and secondary results with uncertainty. | ADDRESSED | "The treatment decision stays stable..." (L297-316): flip rates with ranges, per-model TOST equivalence counts (29/29/28/27/27/23), two BH-FDR-surviving directional tests (both DeepSeek-chat). Table 2 (L472-517) gives all 29 variants' mean flip rate and Cohen's d. |
| 29 | **Fairness / subgroup results** — subgroup/counterfactual results reported. | ADDRESSED | "Framing diverges with socioeconomic disadvantage, not race" (L340-395) and "The signal splits into appropriate care and a distinct stigma residue" (L396-427): race-only null vs. SES gradient, intersectional latina_female_uninsured d=1.62, appropriate/stigmatizing split. |
| 30 | **Reporting of errors / failure modes** — qualitative failure analysis or notable error patterns. | ADDRESSED | GPT-4o unhoused-arm exception (L409-413): explicitly framed as "we cannot distinguish a genuine displacement mechanism ... from model-specific idiosyncrasy or noise," not asserted as a confirmed mechanism from an n=1-model observation. Parser known-misclassification risk disclosed in Limitations (L649-651). |

## Discussion

| # | TRIPOD-LLM item | Status | Where addressed / what it says |
|---|---|---|---|
| 31 | **Interpretation** — of results in context of prior evidence and objectives. | ADDRESSED | "Principal Findings" (L525-546) and "Comparison With Prior Work" (L549-573): dissociation interpreted against Omar et al. [1], clinical-trial-screening work [3], inherited-stigma work [4]. |
| 32 | **Limitations** — of the study/data/LLM, incl. bias/generalizability. | ADDRESSED | "Limitations" (L614-717), six paragraphs: single-rater/second-rater status of the stigma measurement; scoring-pipeline caveats (tier scale, parser, classifier false positives); NCCN scorer/GENIE gaps (ECOG, PD-L1, biomarker panel); robustness-control scope and LLM-generated-note fabrication risk; cohort generalizability; design-scope deviations (model panel, no power calculation, exploratory mitigation arm). |
| 33 | **Usability / deployment / clinical implications & risks.** | ADDRESSED | "Clinical and Deployment Implications" (L576-600): audit the narrative layer, not just the decision; do not indiscriminately suppress SES language; the decomposition as a candidate audit instrument; a point-of-care note for the clinician reviewing an AI-drafted note before co-signing. |
| 34 | **Generalizability** — extent to which findings transfer to other settings/populations/models. | ADDRESSED | Limitations, generalizability paragraph (L693-703): three-center cohort skewing Non-Hispanic White/adenocarcinoma-enriched/smoker-under-representative; pipeline stated as English-language and U.S.-specific; transfer to other languages, health systems, countries, or cancer types explicitly untested. |

## Other Information

| # | TRIPOD-LLM item | Status | Where addressed / what it says |
|---|---|---|---|
| 35 | **Supplementary material** — availability of supplements/appendices. | ADDRESSED | Supplementary Methods (L1035-1193, nine named subsections: statistical detail; verbatim baseline prompt [L1049]; verbatim judge rubric [L1072]; three robustness-control protocols — PMC real-note, template-note, natural-prose; and three further protocols — mitigation-prompt, restricted-to-concordant-control, pooled label-level concordance), Supplementary Results (L1195-1240), Supplementary Figures S1-S12 with Tables S1-S3 (L1242-1391). **Correction:** the prior version of this row cited "Supplementary Table S3 (per-model 29-variant CSV)" and a nonexistent "Figure S0" — the per-model 29-variant CSV is actually **Table S1** (L1302, `supplementary_table_29variants_per_model.csv`); **Table S3** (L1357-1380) is the unrelated exploratory mitigation-ladder results table; there is no Figure S0 in the current manuscript (figures run S1-S12 only). |
| 36 | **Guideline adherence statement** — statement that a reporting guideline (TRIPOD-LLM) was followed, with completed checklist. | ADDRESSED | "Study Design" (L88-91) names TRIPOD-LLM and cites this checklist file by path as a supplement. |

---

## Summary of open GAPs (author action before submission)

Item 23 (public code URL) is now ADDRESSED and removed from this list since the prior audit.
Item 16 is downgraded from ADDRESSED to PARTIAL in this revision — not because reporting is
missing, but because a genuine internal-consistency defect was found (see row 16) that a TRIPOD
reviewer would treat as incomplete equivalence-testing reporting until resolved. Two items
remain open, both requiring information this audit cannot supply from the repository alone:

1. **Item 11 (Versioning):** pin API model snapshot IDs and data-collection/access dates —
   the code's model identifiers are floating aliases (e.g. `gemini-2.5-flash`), not dated
   snapshots, and results files are not git-tracked, so neither the exact API version nor the
   run dates can be recovered from the repository itself.
2. **Item 16 (Evaluation methods — equivalence margin unit):** reconcile the TOST margin to one
   unit (raw tier-scale units vs. Cohen's d) across the pre-registration, the main decision test,
   and the exploratory mitigation test, and correct whichever of the three is currently
   mislabeled.

Also flagged as author-judgment items, not blocking GAPs: item 1 (title framing), item 23
(confirm the repo is actually public / consider a DOI snapshot), and item 26 (self-determined
vs. formal IRB exemption) — see the notes inline in each row above.

*Prepared as a TRIPOD-LLM reporting supplement for the NSCLC counterfactual-audit manuscript.
"ADDRESSED" reflects the manuscript state as of this revision (2026-08-03); re-verify line
numbers after any further edit — this file has previously gone stale after unrelated
manuscript rewrites and should be regenerated, not hand-patched, whenever the title, abstract,
or Limitations section changes materially.*
