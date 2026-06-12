# EquityGUIDE

**Counterfactual audit of demographic bias in large language model cancer treatment recommendations**

EquityGUIDE tests whether AI oncology decision-support systems produce equitable treatment recommendations when two patients share identical clinical facts but differ only in race, insurance status, socioeconomic status, or other demographic characteristics — and evaluates prompting strategies to reduce that bias. The core design is counterfactual: the same clinical note is sent to the model 30 times, once per demographic variant, with all biomarker and staging information held constant. Any difference in the treatment recommendation is attributable solely to demographic framing. Mitigation strategies including fairness-instructed prompting, guideline-grounded reasoning, and structured demographic-blind extraction are tested against the same case set to measure whether bias can be reduced without sacrificing clinical accuracy.

---

## Background

Large language models are increasingly deployed in clinical decision support. Whether these systems perpetuate or amplify existing health disparities is an open and urgent question. Prior work (Omar et al., *Nature Medicine* 2025) demonstrated LLM bias in general medical Q&A; EquityGUIDE extends this to cancer-specific, guideline-grounded, counterfactual evaluation using real de-identified oncology cases.

---

## Datasets

### CancerGUIDE (synthetic)

316 synthetic NSCLC cases from Lozano et al. (Microsoft, HuggingFace 2024) with NCCN Category 1 ground-truth treatment labels. Spans Stages I–IV, stratified by stage, histology, biomarker profile, and ECOG performance status. Available in two formats:

- `synthetic_structured` (165 cases) — templated EHR-style with explicit field labels
- `synthetic_unstructured` (151 cases) — free-text narrative consultation notes

### GENIE BPC NSCLC (real, de-identified)

1,048 real de-identified non-small cell lung cancer cases from the AACR Project GENIE Biopharma Collaborative (v2.0-public). Cases are drawn from five academic cancer centers (DFCI, MSK, VICC, and others). Inclusion criteria: index cancer, non-small-cell histology, known AJCC stage, at least one documented Line 1 regimen.

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

Demographic distribution reflects real-world academic cancer center populations: White (80.7%), Asian (8.2%), Black or African American (5.8%), Other/Unknown (5.3%).

**Clinical enrichment added for this study** (beyond standard GENIE BPC fields):

- **Gene panel-aware biomarker calling** — each sample is mapped to its sequencing panel (11 panels in `equityGUIDEoncopanel/`). Genes not covered by a given panel are marked `not_on_panel` rather than negative, correcting false-negative driver calls on small panels (e.g., VICC-01-SOLIDTUMOR covers 31 genes)
- **PD-L1 TPS from pathology reports** — 377 patients with actual percentage from `pathology_report_level_dataset.csv`; an additional ~80 with binary result from `data_clinical_sample.txt`; 501 not tested (pre-2016 sequencing, before routine PD-L1 testing — reflects real clinical practice)
- **At-diagnosis metastatic sites** — 8 organ-specific fields from `data_clinical_patient.txt`, capturing sites present at initial consultation rather than ever-present disease
- **Prior malignancy history** from `cancer_level_dataset_non_index.csv`
- **ERBB2 exon 20 insertions, MET amplification, STK11/KEAP1 loss-of-function** — added as actionable and immunotherapy-resistance biomarkers respectively
- **NCCN scorer updated** with neoadjuvant/perioperative IO for resectable Stage II/IIIA (CheckMate 816, KEYNOTE-671, AEGEAN), EGFR/ALK gating for neoadjuvant IO, and adjuvant alectinib (ALINA) for ALK+ resected Stage II/IIIA

---

## Design

### Counterfactual variant injection

Each clinical note is sent to the model in 30 versions across 6 tiers:

| Tier | Focus | Variants |
|------|-------|---------|
| A — v1 replication | Intersectional race × insurance profiles | 5 |
| B — Race only | Single-axis race labels (Omar et al. comparability) | 5 |
| C — SES only | Housing, income | 3 |
| D — Insurance only | Uninsured, Medicaid | 2 |
| E — Isolation | Race vs. insurance disentanglement | 3 |
| F — Gender / identity | Non-binary, transgender, gay | 3 |
| Reference | No demographics | 1 |

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

A stratified pilot of 50 real de-identified GENIE BPC NSCLC cases × 30 variants = 1,500 LLM calls per model. Three models completed:

### Flip rates

| Variant | Flash | Flash-Lite |
|---------|-------|-----------|
| `native_american_race_only` | 20.5% | 27.7% |
| `unhoused_patient` | 19.6% | 17.4% |
| `latina_female_uninsured` | 19.0% | 28.9% |
| `medicaid_only` | 17.4% | 31.2% |
| `low_income_patient` | 18.2% | 25.5% |
| `high_income_patient` | 15.9% | 17.0% |

Flash-Lite shows ~8 percentage points higher flip rates on average. The more capable Flash model has lower flip rates but a more insidious soft bias pattern.

### Flip direction

Among flips, race and SES-disadvantaged groups are systematically **downgraded** toward less aggressive treatment; LGBTQIA+ groups are systematically **upgraded**. Both are bias operating in opposite directions.

| Variant | Down% | Up% |
|---------|-------|-----|
| `unhoused_patient` | 77.8% ▼ | 22.2% |
| `black_race_only` | 75.0% ▼ | 25.0% |
| `low_income_patient` | 75.0% ▼ | 25.0% |
| `medicaid_only` | 75.0% ▼ | 25.0% |
| `transgender_woman` | 33.3% | 66.7% ▲ |
| `gay_male_patient` | 40.0% | 60.0% ▲ |

### Soft bias — key signals (Gemini Flash)

| Signal | Strongest variants |
|--------|--------------------|
| Trial de-emphasis | `uninsured_only` −12%, `non_binary_patient` −12%, `black_race_only` −10% |
| Cost framing | `latina_female_uninsured` +18%, `low_income_patient` +10% |
| Adherence concern | `unhoused_patient` +6%, `low_income_patient` +4%, `native_american` +4% |
| Financial deflection | `low_income_patient` +6%, `latina_female_uninsured` +6% |
| Access conditionalization | `low_income_patient` +6%, `latina_female_uninsured` +4% |
| Regimen logistics | `unhoused_patient` +8%, `low_income_patient` +6% |

The SES gradient (unhoused > low-income > 0 for high-income) is consistent across all soft bias dimensions. Race-only variants show minimal financial/logistics signal — access bias is driven by insurance and SES labels, not race alone.

### Flash vs. Flash-Lite soft bias

The two models fail in opposite directions on clinical trial framing. Flash **removes** trial mentions for marginalized patients (−10 to −12%); Flash-Lite **adds** them performatively (+6 to +22%). Both are bias; Flash's pattern is more clinically harmful.

---

## Models Tested

| Model | Provider | Pilot50 status |
|-------|----------|----------------|
| `gemini-2.5-flash` | Google | Complete |
| `gemini-2.5-flash-lite` | Google | Complete |
| `gpt-4o` | OpenAI | In progress |
| `llama-3.3-70b-versatile` | Groq / Meta | Pending (Together.ai for full run) |

All models use the same pipeline, prompt, and variant set. The factory in `src/models/factory.py` routes model names to the appropriate API client. Supported: Gemini, OpenAI, Anthropic, Groq (free tier), Together.ai.

---

## Repository Structure

```
EquityGUIDE/
├── src/
│   ├── generate/
│   │   ├── load_cases.py              # CancerGUIDE loading + demographic stripping
│   │   ├── load_genie_bpc.py          # GENIE BPC NSCLC processing (14-file merge)
│   │   ├── note_generator.py          # LLM-based free-text note generation
│   │   ├── variant_injector.py        # V1 variant injection (6 intersectional profiles)
│   │   └── variant_injector_v2.py     # V2 variant injection (30 variants, 6 tiers)
│   ├── analyze/
│   │   ├── response_parser.py         # LLM response → 10-class treatment category
│   │   └── stats.py                   # Wilson CI, Fisher exact, McNemar
│   └── models/
│       ├── factory.py                 # Model routing (Gemini, OpenAI, Anthropic, Groq, Together)
│       ├── gemini_model.py
│       ├── openai_model.py
│       ├── anthropic_model.py
│       ├── groq_model.py
│       └── together_model.py
├── prompts/
│   └── evaluation/
│       └── prompt_templates.py        # baseline, fairness, guideline_grounded, structured_extraction
├── equityGUIDEoncopanel/              # 11 gene panel definitions + gene matrix
├── run_experiment_v2.py               # Main experiment runner
├── generate_genie_notes.py            # Free-text note generation for GENIE BPC cases
├── analyze_results_v2.py              # Full analysis: flip rate, direction, isolation, soft bias
├── data/
│   ├── genie_bpc/nsclc/               # Raw GENIE BPC source files (data use agreement required)
│   ├── processed/                     # Processed case JSON files
│   └── notes/genie_nsclc/             # Cached LLM-generated free-text notes
├── results/
│   ├── baseline/                      # Experiment results JSON files
│   └── analysis/                      # CSV outputs (flip rates, soft bias, concordance)
└── docs/
    ├── METHODS.md                     # Full technical methods documentation
    └── genie_bpc_pipeline.md          # GENIE BPC pipeline walkthrough with examples
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
```

### CancerGUIDE experiment

```bash
python run_experiment_v2.py --subset synthetic_unstructured --model gemini-2.5-flash
python analyze_results_v2.py --subset synthetic_unstructured --save
```

### GENIE BPC experiment

Raw GENIE BPC files are available under data use agreement from [genie.cbioportal.org](https://genie.cbioportal.org). Place source files in `data/genie_bpc/nsclc/` and gene panel files in `equityGUIDEoncopanel/`, then:

```bash
# Step 1: Process raw GENIE BPC files
python src/generate/load_genie_bpc.py

# Step 2: Generate free-text notes (cached per case)
python generate_genie_notes.py --pilot 50
python generate_genie_notes.py --full

# Step 3: Run experiment
python run_experiment_v2.py --subset genie_bpc_nsclc_pilot50 --model gemini-2.5-flash

# Step 4: Analyze
python analyze_results_v2.py --subset genie_bpc_nsclc_pilot50 --save
```

---

## Data Availability

- **CancerGUIDE cases:** publicly available at [huggingface.co/datasets/microsoft/CancerGUIDE](https://huggingface.co/datasets/microsoft/CancerGUIDE)
- **GENIE BPC data:** available under data use agreement from the AACR Project GENIE Biopharma Collaborative ([genie.cbioportal.org](https://genie.cbioportal.org))
- **Generated notes and results:** available upon reasonable request

---

## Contact

Alvaro Cuervo — alvaro.cuervo@yale.edu
