# EquityGUIDE

**Counterfactual audit of demographic bias in large language model cancer treatment recommendations**

EquityGUIDE tests whether AI oncology decision-support systems produce equitable treatment recommendations when two patients share identical clinical facts but differ only in race, insurance status, socioeconomic status, or other demographic characteristics — and evaluates prompting strategies to reduce that bias. The core design is counterfactual: the same clinical note is sent to the model 30 times, once per demographic variant, with all biomarker and staging information held constant. Any difference in the treatment recommendation is attributable solely to demographic framing. Mitigation strategies including fairness-instructed prompting, guideline-grounded reasoning, and structured demographic-blind extraction are tested against the same case set to measure whether bias can be reduced without sacrificing clinical accuracy.

> **A note on provenance and circularity.** The GENIE BPC cases are real, de-identified *structured* oncology records, but the free-text consultation notes sent to the models are **LLM-generated**: `gemini-2.5-flash` renders each structured case into a demographics-neutral note, using de-identified CORAL oncology notes as style anchors only. Because one audited model (Gemini) helps author the input text, circularity is ruled out empirically — the socioeconomic stigma gradient replicates at essentially the same magnitude on (1) fully deterministic, **LLM-free template notes** and (2) **real published PMC clinical notes** the models never generated (see the note-source controls in the manuscript, `docs/paper1_nsclc/manuscript_nsclc.md`, Figure 6A-C).

---

## Background

Large language models are increasingly deployed in clinical decision support. Whether these systems perpetuate or amplify existing health disparities is an open and urgent question. Prior work (Omar et al., *Nature Medicine* 2025) demonstrated LLM bias in general medical Q&A; EquityGUIDE extends this to cancer-specific, guideline-grounded, counterfactual evaluation using a large real-world oncology cohort with model-generated consultation notes (see the provenance note above).

---

## Datasets

### CancerGUIDE (synthetic)

316 synthetic NSCLC cases from Lozano et al. (Microsoft, HuggingFace 2024) with NCCN Category 1 ground-truth treatment labels. Spans Stages I–IV, stratified by stage, histology, biomarker profile, and ECOG performance status. Available in two formats:

- `synthetic_structured` (165 cases) — templated EHR-style with explicit field labels
- `synthetic_unstructured` (151 cases) — free-text narrative consultation notes

### GENIE BPC NSCLC (real, de-identified)

1,048 real de-identified non-small cell lung cancer cases from the AACR Project GENIE Biopharma Collaborative (v2.0-public). Cases are drawn from three academic cancer centers: Memorial Sloan Kettering (MSK, n=556), Dana-Farber Cancer Institute (DFCI, n=343), and Vanderbilt-Ingram Cancer Center (VICC, n=149). Inclusion criteria: index cancer, non-small-cell histology, known AJCC stage, at least one documented Line 1 regimen.

| Characteristic | N (%) |
|----------------|-------|
| Total cases | 1,048 |
| Stage IV | 594 (56.7%) |
| Stage III | 251 (23.9%) |
| Stage I–II | 203 (19.4%) |
| Adenocarcinoma | 884 (84.4%) |
| Squamous | 123 (11.7%) |
| Biomarkers available | 1,025 (97.8%) |
| PD-L1 TPS available | 377 (36.0%) |

Demographic distribution reflects real-world academic cancer center populations: White (80.7% by race, all ethnicities; 79.3% when restricted to non-Hispanic White, the figure used in the manuscript's Table 1), Asian (8.2%), Black or African American (5.8%), Other/Unknown (5.3%).

**Clinical enrichment added for this study** (beyond standard GENIE BPC fields):

- **Gene panel-aware biomarker calling** — each sample is mapped to its sequencing panel (11 panels in `data/genie_bpc/nsclc/equityGUIDEoncopanel/`). Genes not covered by a given panel are marked `not_on_panel` rather than negative, correcting false-negative driver calls on small panels (e.g., VICC-01-SOLIDTUMOR covers 31 genes)
- **PD-L1 TPS from pathology reports** — 377 patients with actual percentage from `pathology_report_level_dataset.csv`; an additional ~80 with binary result from `data_clinical_sample.txt`; 501 not tested (pre-2016 sequencing, before routine PD-L1 testing — reflects real clinical practice)
- **At-diagnosis metastatic sites** — 8 organ-specific fields from `data_clinical_patient.txt`, capturing sites present at initial consultation rather than ever-present disease
- **Prior malignancy history** from `cancer_level_dataset_non_index.csv`
- **ERBB2 exon 20 insertions, MET amplification, STK11/KEAP1 loss-of-function** — added as actionable and immunotherapy-resistance biomarkers respectively
- **NCCN scorer updated** with neoadjuvant/perioperative IO for resectable Stage II/IIIA (CheckMate 816, KEYNOTE-671, AEGEAN), EGFR/ALK gating for neoadjuvant IO, and adjuvant alectinib (ALINA) for ALK+ resected Stage II/IIIA

---

## Design

### Counterfactual variant injection

Each clinical note is sent to the model in 30 versions: a no-demographics control, a privileged comparator (white male, private insurance), and 28 demographic-labeled variants across 9 tiers (`src/generate/variant_injector_v2.py`):

| Tier | Focus | Variants |
|------|-------|---------|
| Reference | No demographics (control) | 1 |
| — | Privileged comparator (white male, private insurance) | 1 |
| A | Race × insurance (intersectional) | 4 |
| B | Insurance only | 5 |
| C | Race only | 6 |
| D | Geography (rural, small community hospital) | 2 |
| E | Age (elderly) | 1 |
| F | Immigration / language | 2 |
| G | SES only (unhoused, low income, high income) | 3 |
| H | Race × SES (intersectional) | 2 |
| I | Gender / identity | 3 |
| **Total** | | **30** |

For unstructured notes, a single bracketed demographic label is prepended to the otherwise-identical note:

```
[PATIENT DEMOGRAPHICS: Black female patient, Medicaid]
```

All clinical content — stage, histology, biomarkers, ECOG performance status, metastatic sites — is held constant across all 30 versions.

### GENIE BPC clinical note construction

Each real GENIE BPC case is transformed into a free-text consultation note through a 4-step pipeline:

1. **12-file merge** — structured case dict from `load_genie_bpc.py` integrating staging, histology, biomarkers, PD-L1, TMB, metastatic sites, and prior cancer history
2. **Gene panel-aware wildtype calling** — false negatives suppressed on small panels
3. **LLM note generation** — `gemini-2.5-flash` converts the structured profile into a demographics-neutral free-text NSCLC consultation note using de-identified CORAL oncology notes as style anchors only
4. **Variant injection** — 29 demographic labels prepended one at a time; control version has no label

### Outcome measures

**Primary — Flip rate:** proportion of cases where the model's treatment category changes relative to the no-demographics control. Reported with Wilson 95% confidence intervals. Treatment categories: `surgical_resection`, `chemoradiation`, `chemoimmunotherapy`, `targeted_therapy`, `immunotherapy_mono`, `chemotherapy`, `radiation_only`, `observation`, `testing_first`, `best_supportive_care`.

**Primary — Flip direction:** among flips, whether the variant recommendation is a clinical downgrade (toward less aggressive treatment), upgrade, or lateral shift. Calibrated against a clinical aggressiveness hierarchy (BSC=1 → surgical resection=8). This distinguishes systematic downgrading of disadvantaged patients from random instability.

**Secondary — NCCN concordance:** proportion of responses concordant with NCCN Category 1 guidelines, compared across variants by Fisher's exact test.

**Tertiary — Soft bias:** 8 dimensions of differential framing that do not change the treatment category but signal inequitable content:

| Dimension | Signal |
|-----------|--------|
| Clinical trial mention | Trial referral rate added/removed |
| Cost framing | Financial language added |
| Social work referral | Navigator/social work mention |
| Best supportive care framing | Palliative/hospice language |
| Adherence concern | Compliance/adherence assumptions added (paternalism marker) |
| Regimen logistics modification | Oral/fewer-visit regimen chosen for social reasons |
| Financial program deflection | Redirected to PAPs/charity rather than recommending drug |
| Access conditionalization | Standard-of-care made contingent on affordability |

### Statistical framework

- Flip rates: Wilson score 95% CI; chi-square homogeneity across variants
- Concordance: Fisher's exact (one-tailed); Bonferroni correction per analysis family
- Soft bias: net % vs. no-demographics reference; McNemar within-case paired asymmetry at full scale

---

## Pilot Results (n = 50 GENIE BPC NSCLC cases)

> **Superseded snapshot.** The numbers in this section come from an early three-model pilot (Gemini Flash, Gemini Flash-Lite, GPT-4o) on 50 cases. They are retained as a development record and are **superseded by the full n = 1,048, six-model study** reported in the manuscript (`docs/paper1_nsclc/manuscript_nsclc.md`). Do not cite these as the study's results.

A stratified pilot of 50 real de-identified GENIE BPC NSCLC cases × 30 variants = 1,500 LLM calls per model. Three models completed.

### NCCN concordance

Concordance is computed against NCCN Category 1 guidelines using the full set of acceptable answers per case (multiple valid first-line options exist for many profiles, e.g., pembrolizumab monotherapy or chemoimmunotherapy for high PD-L1 Stage IV adenocarcinoma).

| Model | Overall concordance |
|-------|-------------------|
| GPT-4o | **84.3%** |
| Gemini Flash | **77.1%** |
| Gemini Flash-Lite | **70.0%** |

GPT-4o matches or exceeds the CancerGUIDE synthetic benchmark (~80%) on real de-identified cases. Flash-Lite is the weakest across all tiers.

### Flip rates (overall average across all variants)

| Model | Overall flip rate |
|-------|-----------------|
| Gemini Flash-Lite | 23.9% |
| Gemini Flash | 16.5% |
| GPT-4o | 11.4% |

Selected variant-level rates:

| Variant | Flash | Flash-Lite | GPT-4o |
|---------|-------|-----------|--------|
| `native_american_race_only` | 20.5% | 27.7% | 13.6% |
| `unhoused_patient` | 19.6% | 17.4% | 11.4% |
| `latina_female_uninsured` | 19.0% | 28.9% | 11.1% |
| `medicaid_only` | 17.4% | 31.2% | 9.1% |
| `low_income_patient` | 18.2% | 25.5% | 11.1% |
| `high_income_patient` | 15.9% | 17.0% | 6.8% |

### Flip direction

Among flips, race and SES-disadvantaged groups are systematically **downgraded** toward less aggressive treatment; LGBTQIA+ groups are systematically **upgraded**. Both are bias operating in opposite directions. This pattern is consistent across Flash and Flash-Lite; GPT-4o tends to upgrade SES groups rather than downgrade them.

| Variant | Flash Down% | Flash Up% |
|---------|------------|----------|
| `unhoused_patient` | 77.8% ▼ | 22.2% |
| `black_race_only` | 75.0% ▼ | 25.0% |
| `low_income_patient` | 75.0% ▼ | 25.0% |
| `medicaid_only` | 75.0% ▼ | 25.0% |
| `transgender_woman` | 33.3% | 66.7% ▲ |
| `gay_male_patient` | 40.0% | 60.0% ▲ |

### Three distinct failure modes

The pilot reveals that the three models represent qualitatively different bias patterns — not a simple better/worse ranking:

| Model | Hard flips | Concordance | Soft bias |
|-------|-----------|-------------|-----------|
| Flash-Lite | Highest (24%) | Lowest (70%) | Moderate |
| Flash | Moderate (17%) | Mid (77%) | Directional (downgrades race/SES; trial de-emphasis) |
| GPT-4o | Lowest (11%) | Highest (84%) | **Most extreme** (cost/adherence language) |

**The central finding:** reducing flip rate does not reduce bias — it shifts it from hard clinical decisions to language. GPT-4o appears safest by the headline metric but generates the most extreme soft bias, including `uninsured_only` +88% cost framing, `low_income_patient` +45% adherence concern, and `latina_female_uninsured` +54% cost language.

### Soft bias — key signals

| Signal | Flash | Flash-Lite | GPT-4o |
|--------|-------|-----------|--------|
| Trial de-emphasis (`uninsured_only`) | −12% | +10% | −4% |
| Trial de-emphasis (`black_race_only`) | −10% | +6% | −13% |
| Cost framing (`low_income_patient`) | +10% | +48% | **+62%** |
| Cost framing (`uninsured_only`) | +12% | +32% | **+88%** |
| Adherence concern (`unhoused_patient`) | +6% | +12% | **+43%** |
| Financial deflection (`uninsured_only`) | +2% | +16% | **+35%** |

Flash and Flash-Lite fail in opposite directions on trial mentions: Flash removes them for marginalized patients; Flash-Lite adds them performatively. GPT-4o's cost and adherence signals are 3–7× larger than Flash's on SES variants.

The SES gradient (unhoused > low-income > 0 for high-income) is consistent across all soft bias dimensions and all three models. Race-only variants show minimal financial/logistics signal — access bias is primarily driven by insurance and SES labels.

---

## Mitigation Results (synthetic unstructured, n=151 cases)

Three prompting strategies were tested against the baseline on the CancerGUIDE synthetic unstructured subset: fairness-instructed prompting, guideline-grounded reasoning, and structured demographic-blind extraction. Hard flip rates are reported elsewhere; the table below shows the effect on soft bias for key SES and insurance variants.

### Effect on soft bias (net % vs. no-demographics; + = language added for variant)

| Strategy | Trial (`uninsured_only`) | Cost (`uninsured_only`) | Adhere (`low_income`) | FinDfl (`uninsured_only`) |
|----------|------------------------|-----------------------|----------------------|--------------------------|
| Baseline | −3% | +63% | +12% | +53% |
| Fairness prompt | −23% | −1% | −1% | 0% |
| Guideline-grounded | −56% | **+97%** | **+74%** | +32% |
| Structured extraction | −80% | −1% | +5% | +1% |

### Key findings

**Fairness prompt and structured extraction eliminate soft bias.** Both strategies reduce cost framing, adherence concern, financial deflection, and access conditionalization to near zero across all SES and insurance variants — even though both strategies *increase* hard flip rates relative to baseline.

**Guideline-grounded prompting amplifies soft bias.** Asking the model to reason through NCCN pathways step-by-step nearly doubles cost language (`uninsured_only` +63% → +97%) and introduces large adherence signals that are absent at baseline (`low_income_patient` +12% → +74%). Structured clinical reasoning appears to activate more demographic stereotyping, not less.

**Race and gender variants show near-zero soft bias under all strategies** — consistent with the GENIE BPC finding that soft bias is driven by SES and insurance labels, not race or gender alone.

**The mitigation trade-off:** No single strategy reduces both hard flips and soft bias simultaneously. The strategies that eliminate soft bias increase decision instability; the strategy that increases soft bias most (guideline-grounded) also produces the highest flip rates. This inversion is the central finding of the mitigation analysis.

---

## Models Tested

The full study audits **six LLMs from five model families**, each run over all 1,048 GENIE BPC NSCLC cases × 30 variants (temperature 0, single pass). Headline concordance, flip-rate, and stigma-gradient results are reported in the manuscript (`docs/paper1_nsclc/manuscript_nsclc.md`).

| Model | Provider | Status (n = 1,048) |
|-------|----------|--------------------|
| `gemini-2.5-flash` | Google | Complete |
| `deepseek-chat` | DeepSeek | Complete |
| `llama-3.3-70b` | Meta | Complete |
| `llama-3.1-8b` | Meta | Complete |
| `gpt-4o` | OpenAI | Complete |
| `gpt-4o-mini` | OpenAI | Complete |

All models use the same pipeline, prompt, and variant set. The factory in `src/models/factory.py` routes model names to the appropriate API client (Gemini, OpenAI, DeepSeek, Anthropic, Groq, Together.ai/OpenRouter).

---

## Repository Structure

```
EquityGUIDE/
├── src/
│   ├── generate/
│   │   ├── load_genie_bpc.py          # GENIE BPC NSCLC processing (14-file merge)
│   │   ├── note_generator.py          # LLM-based free-text note generation
│   │   ├── variant_injector.py        # V1 variant injection (6 intersectional profiles)
│   │   └── variant_injector_v2.py     # V2 variant injection (30 variants, 6 tiers)
│   ├── analyze/
│   │   ├── response_parser.py         # LLM response → 10-class treatment category
│   │   ├── soft_bias.py               # Stigma/framing dimension detectors
│   │   └── stats.py                   # Wilson CI, Fisher exact, McNemar
│   ├── evaluate/
│   │   ├── nccn_scorer.py             # NCCN Category 1 guideline scorer
│   │   ├── concordance_checker.py     # Guideline concordance binary (feeds Fig 2)
│   │   └── runner.py
│   ├── models/
│   │   ├── factory.py                 # Model routing (Gemini, OpenAI, Anthropic, Groq, Together, DeepSeek, OpenRouter)
│   │   ├── gemini_model.py
│   │   ├── openai_model.py
│   │   ├── anthropic_model.py
│   │   ├── groq_model.py
│   │   ├── together_model.py
│   │   └── deepseek_model.py
│   └── utils/
├── prompts/
│   └── evaluation/
│       └── prompt_templates.py        # baseline, fairness, guideline_grounded, structured_extraction
├── data/genie_bpc/nsclc/equityGUIDEoncopanel/  # 11 gene panel definitions + gene matrix
├── scripts/
│   └── nsclc/                         # NSCLC pipeline scripts
│       ├── run_experiment_v2.py       # Main experiment runner
│       ├── generate_genie_notes.py    # Free-text note generation for GENIE BPC cases
│       ├── analyze_results_v2.py      # Full analysis: flip rate, direction, isolation, soft bias
│       ├── restricted_bias_gap.py     # Restricted-to-concordant-control sensitivity analysis
│       └── ...                        # experiment/analysis/export/validation scripts
├── download_genie_bpc.py              # Download GENIE BPC NSCLC source files
├── inspect_genie_bpc.py               # GENIE BPC schema inspector
├── data/
│   ├── genie_bpc/nsclc/               # Raw GENIE BPC source files (data use agreement required)
│   ├── coral/                         # De-identified CORAL notes (style anchors only)
│   ├── processed/                     # Processed case JSON files
│   └── notes/genie_nsclc/             # Cached LLM-generated free-text notes
├── results/
│   ├── baseline/                      # Raw experiment results JSON (not on GitHub, see Data Availability)
│   └── analysis/                      # CSV outputs (flip rates, soft bias, concordance) — what the manuscript cites
├── plots/                             # Figure-generating scripts (one per figure)
├── figures/
│   ├── manuscript_combined/           # The 6 main manuscript figures + build script
│   └── manuscript/                    # The 12 supplementary figures
└── docs/
    ├── METHODS.md                     # Full technical methods documentation
    ├── genie_bpc_pipeline.md          # GENIE BPC pipeline walkthrough with examples
    └── paper1_nsclc/                  # Manuscript and reproducibility docs
        ├── manuscript_nsclc.md                          # The manuscript itself (source of truth)
        ├── Sociodemographic_Bias_NSCLC_manuscript.docx  # Compiled manuscript (Word build)
        ├── REPRODUCIBILITY.md                           # This paper's reproduction recipe
        ├── PREREGISTRATION.md
        ├── TRIPOD_LLM_checklist.md
        ├── supplementary_table_29variants_per_model.csv # Supplementary Table S3
        └── archive/                                     # Superseded drafts and internal working notes
```

---

## Reproducing the Experiment

### Requirements

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Add API keys to a `.env` file:

```
GOOGLE_API_KEY=...
OPENAI_API_KEY=...
GROQ_API_KEY=...          # free tier, rate-limited
TOGETHER_API_KEY=...      # optional, for full Llama runs
ANTHROPIC_API_KEY=...     # optional
DEEPSEEK_API_KEY=...      # for the deepseek-chat arm
```

### CancerGUIDE experiment (archived pilot phase — not runnable from the main tree)

CancerGUIDE was this project's early pilot dataset, used to sanity-check the NCCN scorer before
the study moved to the real, 1,048-case GENIE BPC cohort below. It backs no result in the
manuscript (cited only as a benchmark comparator, ref [8]) and its data/loader have been moved
to `archive/cancerguide_pilot/` to keep the main tree focused on the GENIE BPC study. To rerun
it, first move `archive/cancerguide_pilot/data/{raw,processed,variants}/*` back to `data/` and
`archive/cancerguide_pilot/src/generate/load_cases.py` back to `src/generate/`, then:

```bash
python scripts/nsclc/run_experiment_v2.py --subset synthetic_unstructured --model gemini-2.5-flash
python scripts/nsclc/analyze_results_v2.py --subset synthetic_unstructured --save
```

### GENIE BPC experiment

Raw GENIE BPC files are available under data use agreement from [genie.cbioportal.org](https://genie.cbioportal.org). Place source files in `data/genie_bpc/nsclc/` and gene panel files in `data/genie_bpc/nsclc/equityGUIDEoncopanel/`, then:

```bash
# Step 1: Process raw GENIE BPC files
python src/generate/load_genie_bpc.py

# Step 2: Generate free-text notes (cached per case)
python scripts/nsclc/generate_genie_notes.py --pilot 50
python scripts/nsclc/generate_genie_notes.py --full

# Step 3: Run experiment
python scripts/nsclc/run_experiment_v2.py --subset genie_bpc_nsclc_pilot50 --model gemini-2.5-flash

# Step 4: Analyze
python scripts/nsclc/analyze_results_v2.py --subset genie_bpc_nsclc_pilot50 --save
```

---

## Data Availability

- **CancerGUIDE cases:** publicly available at [huggingface.co/datasets/microsoft/CancerGUIDE](https://huggingface.co/datasets/microsoft/CancerGUIDE)
- **GENIE BPC data:** available under data use agreement from the AACR Project GENIE Biopharma Collaborative ([genie.cbioportal.org](https://genie.cbioportal.org))
- **Generated notes and derived analysis outputs** (`data/notes/`, `results/analysis/`): in this repository
- **Raw per-model response files** (`results/baseline/`, hundreds of MB per model): not in this repository, available upon reasonable request

---

## License

Code in this repository is released under the [MIT License](LICENSE). GENIE BPC
data are not covered by this license and require a separate data use agreement
(see Data Availability above).

## Contact

Alvaro Cuervo — alvaro.cuervo@yale.edu
