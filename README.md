# EquityGUIDE

**Counterfactual audit of demographic bias in large language model cancer treatment recommendations**

EquityGUIDE tests whether AI oncology decision-support systems produce equitable treatment recommendations when two patients share identical clinical facts but differ only in race, insurance status, socioeconomic status, or other demographic characteristics. The core design is counterfactual: the same clinical note is sent to the model 30 times, once per demographic variant, with all biomarker and staging information held constant. Any difference in the treatment recommendation is attributable solely to demographic framing.

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

1,048 real de-identified non-small cell lung cancer cases from the AACR Project GENIE Biopharma Collaborative (v2.0-public). Cases are drawn from five academic cancer centers. Inclusion criteria: index cancer, non-small-cell histology, known AJCC stage, at least one documented Line 1 regimen.

| Characteristic | N (%) |
|----------------|-------|
| Total cases | 1,048 |
| Stage IV | 594 (56.7%) |
| Stage III | 251 (23.9%) |
| Stage I–II | 203 (19.4%) |
| Adenocarcinoma | 884 (84.4%) |
| Squamous | 123 (11.7%) |
| Biomarkers available | ~85% |

Demographic distribution reflects real-world academic cancer center populations: White (80.7%), Asian (8.2%), Black or African American (5.8%), Other/Unknown (5.3%).

---

## Design

### Counterfactual variant injection

Each clinical note is sent to the model in 30 versions:

| Tier | Focus | Variants |
|------|-------|---------|
| A — Race × Insurance | Intersectional (primary contribution) | 4 |
| B — Insurance only | Cancer's #1 documented disparity driver | 5 |
| C — Race / ethnicity only | Surgery rates, trial enrollment | 6 |
| D — Geography | Rural access, community hospital | 2 |
| E — Age | Elderly undertreatment | 1 |
| F — Immigration / Language | Access barriers, SDOH | 2 |
| G — SES only | Housing, income | 3 |
| H — Race × SES | Intersectional (Omar et al. comparability) | 2 |
| I — Gender / sexual identity | LGBTQ+ | 3 |
| Reference | White male, private insurance | 1 |
| Control | No demographics | 1 |

For unstructured notes, a single bracketed demographic label is prepended to the otherwise-identical note. For structured notes, demographic fields are replaced in-place via regex. All clinical content — stage, histology, biomarkers, ECOG performance status, brain metastasis status — is held constant across all 30 versions.

### Outcome measures

**Primary — Flip rate:** proportion of cases where the model's treatment category changes relative to the no-demographics control. Reported with Wilson 95% confidence intervals.

**Secondary — NCCN concordance:** for cases with scorable ground-truth labels, proportion of responses concordant with NCCN Category 1 guidelines. Compared across variants by Fisher's exact test.

**Tertiary — Soft bias:** 11 dimensions of differential framing that do not change the treatment category but signal inequitable content — including clinical trial mention rate, cost framing, social work referral, treatment hedging, prognosis framing, and unsolicited SDOH generation.

### Statistical framework

- Flip rates: Wilson score 95% CI; chi-square homogeneity across variants
- Concordance: Fisher's exact (one-tailed, minority < reference); Bonferroni correction per analysis family
- Soft bias: Fisher's exact OR with Cornfield 95% CI; McNemar within-case paired asymmetry

---

## Pilot Results (n = 50 GENIE BPC NSCLC cases)

A stratified pilot of 50 real de-identified GENIE BPC NSCLC cases × 30 variants = 1,500 LLM calls. Model: `gemini-2.5-flash-lite`. All calls completed with 0 errors and 100% parse rate.

**Selected flip rates (vs. no-demographics control)**

| Variant | Flip rate | 95% CI |
|---------|-----------|--------|
| Elderly patient (75+) | 30% | [18.6%, 44.6%] |
| Immigrant patient | 30% | [18.6%, 44.6%] |
| Latina female, uninsured | 28% | [17.5%, 41.7%] |
| Low income + Black | 28% | [17.5%, 41.7%] |
| Native American (race only) | 26% | [15.9%, 39.6%] |
| White male, private ins. (reference) | 20% | [11.2%, 33.0%] |

The reference demographic variant (white male, private insurance) itself shows a 20% flip rate relative to no demographics, confirming that any demographic framing — not only minority framing — destabilizes model outputs on real clinical notes.

**Soft bias — clinical trial mentions**

All minority variants showed reduced clinical trial mention rates relative to the no-demographics control. `black_race_only` and `black_unhoused` showed deficits of −20 percentage points. This effect persisted even when race was the only piece of demographic information present in the note.

**Soft bias — cost framing**

`low_income_patient` (+38 pp), `uninsured_only` (+18 pp), and `elderly_patient_75` (+16 pp) showed large increases in unsolicited financial framing relative to the no-demographics control.

---

## Repository Structure

```
EquityGUIDE/
├── src/
│   ├── generate/
│   │   ├── load_cases.py              # CancerGUIDE loading + demographic stripping
│   │   ├── load_genie_bpc.py          # GENIE BPC NSCLC processing (6-file merge)
│   │   ├── note_generator.py          # LLM-based free-text note generation
│   │   ├── variant_injector.py        # V1 variant injection (6 profiles)
│   │   └── variant_injector_v2.py     # V2 variant injection (30 variants)
│   ├── evaluate/
│   │   ├── nccn_scorer.py             # NCCN pathway scorer (Stages I–IV)
│   │   └── response_parser.py         # LLM response → 10-class treatment category
│   ├── analyze/
│   │   ├── flip_rate.py               # Flip rate computation + Wilson CIs
│   │   ├── soft_bias.py               # 11-dimension soft bias detector
│   │   ├── adherence_scorer.py        # 0–3 ordinal adherence scoring
│   │   └── stats.py                   # Wilson CI, Fisher exact, chi-square, Bonferroni
│   └── models/
│       └── factory.py                 # Model abstraction (Gemini, GPT-4o, GPT-4o-mini)
├── prompts/
│   └── evaluation/
│       └── prompt_templates.py        # baseline, fairness, guideline_grounded, structured_extraction
├── run_experiment_v2.py               # Main experiment runner (30 variants, all subsets)
├── run_experiment_genie_bpc.py        # GENIE BPC runner
├── generate_genie_notes.py            # Free-text note generation for GENIE BPC cases
├── analyze_results_v2.py              # CancerGUIDE analysis
├── analyze_genie_bpc.py               # GENIE BPC analysis
├── plot_genie_pilot50.py              # Three-panel bias figure
├── data/
│   ├── genie_bpc/nsclc/               # Raw GENIE BPC source files (data use agreement required)
│   ├── processed/                     # Processed case JSON files
│   └── notes/genie_nsclc/             # Cached LLM-generated free-text notes
├── results/
│   ├── baseline/                      # Experiment checkpoints and final results
│   └── analysis/                      # CSV outputs (flip rates, soft bias, concordance)
├── figures/                           # Output figures
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

Set `GOOGLE_API_KEY` (Gemini) or `OPENAI_API_KEY` in a `.env` file. See `.env.example`.

### CancerGUIDE experiment

```bash
# Run all 30 variants on synthetic structured notes
python run_experiment_v2.py --subset synthetic_structured --model gemini-2.5-flash

# Analyze results
python analyze_results_v2.py --subset synthetic_structured --save
```

### GENIE BPC experiment

Raw GENIE BPC files are available under data use agreement from [genie.cbioportal.org](https://genie.cbioportal.org). Place the six NSCLC source files in `data/genie_bpc/nsclc/`, then:

```bash
# Step 1: Process raw GENIE BPC files into structured cases
python src/generate/load_genie_bpc.py

# Step 2: Generate free-text notes (LLM call, results cached per case)
python generate_genie_notes.py --pilot 50
python generate_genie_notes.py --full

# Step 3: Run experiment
python run_experiment_v2.py --subset genie_bpc_nsclc_pilot50 --model gemini-2.5-flash

# Step 4: Analyze and plot
python analyze_results_v2.py --subset genie_bpc_nsclc_pilot50_gemini-2.5-flash --save
python plot_genie_pilot50.py
```

---

## Data Availability

- **CancerGUIDE cases:** publicly available at [huggingface.co/datasets/microsoft/CancerGUIDE](https://huggingface.co/datasets/microsoft/CancerGUIDE)
- **GENIE BPC data:** available under data use agreement from the AACR Project GENIE Biopharma Collaborative ([genie.cbioportal.org](https://genie.cbioportal.org))
- **Generated notes and results:** available upon reasonable request

---

## Citation

If you use this code or methodology, please cite:

> Cuervo A, Cuervo S. EquityGUIDE: Counterfactual audit of demographic bias in LLM cancer treatment recommendations. 2026. https://github.com/CR7SC3/EquityGUIDE

---

## Contact

Alvaro Cuervo — alvaro.cuervo@yale.edu
