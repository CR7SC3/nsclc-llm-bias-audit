# Paper 1 (NSCLC) — Reproducibility Recipe

End-to-end, linear recipe to reproduce the NSCLC manuscript
(`docs/paper1_nsclc/manuscript_nsclc.md`) from the raw GENIE BPC download
through every canonical figure in `figures/manuscript/`.

This document covers **Paper 1 (NSCLC) only**. Paper 2 (BRCA + PANC) lives
under `scripts/brca_panc/` and `manuscript_brca_panc/` and is out of scope
here.

All script names, arguments, and input/output paths below were read directly
from the scripts in `scripts/nsclc/`, `src/generate/`, and `plots/`. Where a
detail could not be verified from the code it is flagged as **[VERIFY]**.

---

## 0. Environment

- **Python**: 3.9.6 (the committed `venv/` is CPython 3.9.6; see
  `venv/pyvenv.cfg`). All commands below invoke the interpreter explicitly as
  `venv/bin/python` so the pinned environment is used.
- **Install**:
  ```bash
  python3.9 -m venv venv
  venv/bin/pip install -r requirements.txt
  # Additional runtime deps NOT yet pinned in requirements.txt (see note):
  venv/bin/pip install anthropic openai groq synapseclient
  ```
- **API keys** (`.env`, loaded via `python-dotenv`; see `.env.example`):
  provider keys are needed only for steps that make model calls (note
  generation, experiment runs, judge). Pure-analysis and figure steps read
  cached results and need no keys.
- **Sanity check**: `venv/bin/python test_setup.py` verifies dependencies,
  API-key reachability, and that every `src/` module imports.

> **requirements.txt completeness gap** — `requirements.txt` is present but
> does **not** pin four packages the code imports directly:
> `anthropic` (Sonnet arm + judge), `openai` (GPT-4o / GPT-4o-mini arms),
> `groq` (Groq-hosted arms), and `synapseclient` (raw GENIE download).
> Install them manually (line above) until they are added to the pins.
> Everything else the NSCLC pipeline imports (`pandas`, `numpy`, `scipy`,
> `matplotlib`, `seaborn`, `scikit-learn`, `google-genai`, `datasets`,
> `python-dotenv`, `tqdm`, `jsonschema`, `requests`) is already pinned.

---

## Pipeline at a glance

| Step | Script | Input | Output |
|------|--------|-------|--------|
| 0 | `download_genie_bpc.py` (root) | Synapse (access-gated) | `data/genie_bpc/nsclc/*.csv`, `*.txt` |
| 0b | `inspect_genie_bpc.py` (root) | `data/genie_bpc/nsclc/` | schema/coverage report (stdout) |
| 1 | `src/generate/load_genie_bpc.py` | `data/genie_bpc/nsclc/` | `data/processed/genie_bpc_nsclc_processed.json` (1,048 cases) |
| 2 | `scripts/nsclc/generate_genie_notes.py` | processed JSON | `data/processed/genie_bpc_nsclc_with_notes.json` |
| 3 | `scripts/nsclc/run_experiment_genie_bpc.py` (×6 models; Sonnet via `run_experiment_batch.py`) | processed cases + variant injector | `results/baseline/v2_genie_bpc_nsclc[_<model>]_checkpoint.json` |
| 4a | `scripts/nsclc/analyze_results_v2.py --save` | per-model checkpoints | `results/analysis/v2_genie_bpc_nsclc[_<model>]_{soft_intensity,flip_rates}.csv` |
| 4b | `scripts/nsclc/correct_analysis.py` | per-model checkpoints | corrected stats (TOST / directional / soft split) → **stdout** |
| 4c | `scripts/nsclc/finalize_panel.py` | 6 checkpoints (`ARMS` map) | `results/analysis/panel_stigma_rates.csv` |
| 4d | `scripts/nsclc/bootstrap_panel_ci.py` | 6 checkpoints (`ARMS` map) | `results/analysis/panel_stigma_rates_clustered.csv` |
| 4e | `scripts/nsclc/analyze_partial_concordance.py` | 6 result files | `results/analysis/v2_genie_bpc_nsclc_partial_concordance_summary.csv` |
| 4f | `scripts/nsclc/analyze_genie_bpc.py --save` | per-model checkpoints | Omar-style per-model `*_adherence.csv`, `*_concordance_rates.csv`, `*_case_detail.csv` |
| 5 | `plots/plot_publishable_nsclc.py` (+ per-figure upstream scripts) | step-4 CSVs | `figures/manuscript/Fig*.png` |
| J | `scripts/nsclc/build_judge_packet.py` → `run_judge.py` | responses + gold | `adjudication/judge_labels.json` (feeds FigS1 + adjudication footnote) |

---

## Step 0 — Raw data (ACCESS-GATED)

GENIE BPC is **not public**. It is released to qualified researchers through
the AACR Project GENIE Biopharma Collaborative data-access process
(<https://www.aacr.org/professionals/research/aacr-project-genie/biopharma-collaborative/>).
The manuscript's Data Availability statement documents this. You must have
Synapse credentials with BPC access before Step 0 will succeed.

```bash
# Prompts for Synapse username + password/PAT; skips already-downloaded files.
venv/bin/python download_genie_bpc.py
# Optional schema/coverage sanity report:
venv/bin/python inspect_genie_bpc.py
```

Downloads land in `data/genie_bpc/{nsclc,brca,panc}/` with original filenames.
(The download/inspect scripts cover all three cohorts because they are shared
infrastructure across Paper 1 and Paper 2; only the `nsclc/` subfolder is used
here.)

Required NSCLC files (per `src/generate/load_genie_bpc.py`):
`patient_level_dataset.csv`, `cancer_level_dataset_index.csv`,
`cancer_panel_test_level_dataset.csv`, `regimen_cancer_level_dataset.csv`,
`data_mutations_extended.txt`, `data_fusions.txt`.

---

## Step 1 — Build the processed cohort

```bash
venv/bin/python src/generate/load_genie_bpc.py
# -> data/processed/genie_bpc_nsclc_processed.json
```

Merges demographics, staging, biomarker profile, and first-line regimen into
one flat case list. Inclusion: index cancer, non-small-cell histology, known
AJCC stage, ≥1 Line-1 regimen → **1,048 cases** (the cohort N reported in
Fig 1 / Table 1). Known limitations baked in: ECOG PS defaults to 1 and PD-L1
TPS is "unknown" (GENIE BPC does not carry these); see the script docstring.

---

## Step 2 — Generate free-text notes

```bash
# Stratified pilot first (review, then full):
venv/bin/python scripts/nsclc/generate_genie_notes.py --pilot 50
venv/bin/python scripts/nsclc/generate_genie_notes.py --full
```

Default generation model: `gemini-2.5-flash` (override with `--model`).
Full run writes `data/processed/genie_bpc_nsclc_full_with_notes.json` and the
canonical `data/processed/genie_bpc_nsclc_with_notes.json`. QA runs via
`src/generate/note_qa.check_note`.

> Note: the primary GENIE experiment (Step 3) injects demographic variants
> directly into the `structured_note` field, so the experiment does not strictly
> depend on the free-text notes; the notes support the note-validation and
> robustness tracks (PMC / template / natural-embedding controls, Fig 9).

---

## Step 3 — Per-model experiment runs (the 6-model panel)

Each model is run through the same 22-variant (v2) demographic-injection
pipeline on all 1,048 cases. Cached, resumable checkpoints; re-running skips
completed cases.

```bash
# One command per model (writes results/baseline/v2_genie_bpc_nsclc[_<model>]_checkpoint.json)
venv/bin/python scripts/nsclc/run_experiment_genie_bpc.py --cohort nsclc --model gemini-2.5-flash
venv/bin/python scripts/nsclc/run_experiment_genie_bpc.py --cohort nsclc --model deepseek-chat
venv/bin/python scripts/nsclc/run_experiment_genie_bpc.py --cohort nsclc --model meta-llama/Llama-3.3-70B-Instruct-Turbo
venv/bin/python scripts/nsclc/run_experiment_genie_bpc.py --cohort nsclc --model openrouter/meta-llama/llama-3.1-8b-instruct
venv/bin/python scripts/nsclc/run_experiment_genie_bpc.py --cohort nsclc --model gpt-4o
venv/bin/python scripts/nsclc/run_experiment_genie_bpc.py --cohort nsclc --model gpt-4o-mini
```

Add `--dry-run --limit 5` first to validate wiring without spending credit.
The exact `--model` strings must resolve to the checkpoint filenames the
downstream `ARMS` maps expect (see `scripts/nsclc/finalize_panel.py`):

| model (panel label) | checkpoint file under `results/baseline/` |
|---|---|
| gemini-2.5-flash | `v2_genie_bpc_nsclc_checkpoint.json` |
| deepseek-chat | `v2_genie_bpc_nsclc_deepseek-chat_checkpoint.json` |
| llama-3.3-70B | `v2_genie_bpc_nsclc_meta-llama-Llama-3.3-70B-Instruct-Turbo_checkpoint.json` |
| llama-3.1-8B | `v2_genie_bpc_nsclc_openrouter-meta-llama-llama-3.1-8b-instruct_checkpoint.json` |
| gpt-4o | `v2_genie_bpc_nsclc_gpt-4o_checkpoint.json` |
| gpt-4o-mini | `v2_genie_bpc_nsclc_gpt-4o-mini_checkpoint.json` |

**Anthropic (Sonnet) arm** — use the Message Batches runner (50% cheaper,
byte-identical prompts, same checkpoint schema/path). Default is a safe dry
run; `--submit` actually spends:

```bash
venv/bin/python scripts/nsclc/run_experiment_batch.py --subset genie_bpc_nsclc \
    --model claude-sonnet-5 --limit-cases 30          # dry run + cost estimate
venv/bin/python scripts/nsclc/run_experiment_batch.py --subset genie_bpc_nsclc \
    --model claude-sonnet-5 --submit                  # submit + poll + collect
```

**[VERIFY]** The manuscript's headline panel is the six vendors in the table
above (`finalize_panel.py` `ARMS`). Confirm whether Sonnet-5 is an additional
manuscript arm or a robustness-only arm before treating its checkpoint as a
panel input.

---

## Step 4 — Analysis (no API calls; runs on cached checkpoints)

### 4a. Per-model figure-input CSVs (feeds Figs 4, 5, 5b)
```bash
# Run once per subset/model; --save writes results/analysis/v2_genie_bpc_nsclc[_<model>]_*.csv
venv/bin/python scripts/nsclc/analyze_results_v2.py --subset genie_bpc_nsclc --save
# ...repeat --subset genie_bpc_nsclc_<model> for each of the other five arms
```
Produces `..._soft_intensity.csv` (Cohen's d + BH q per variant) and
`..._flip_rates.csv` (flip rate + Wilson CI) — the exact files
`plots/plot_publishable_nsclc.py` reads (`BASE = results/analysis/v2_genie_bpc_nsclc`).

### 4b. Corrected confirmatory statistics (Fig 4 equivalence annotations, Results text)
```bash
venv/bin/python scripts/nsclc/correct_analysis.py       # prints to stdout
```
Directional decision test (sign test + signed tier-shift d/CI), TOST
equivalence with pre-specified margin, grid-wide BH-FDR, and the
soft-bias defensible-vs-stigma split. Console report — capture stdout for the
manuscript's numeric claims.

### 4c/4d. Panel stigma gradient (feeds Figs 6, 7, 7b)
```bash
venv/bin/python scripts/nsclc/finalize_panel.py         # -> results/analysis/panel_stigma_rates.csv
venv/bin/python scripts/nsclc/bootstrap_panel_ci.py     # -> results/analysis/panel_stigma_rates_clustered.csv
```
Stigma composite = `adherence_compliance OR sdoh_generation` (pre-registered).
`finalize_panel` gives per-stratum rates + Wilson CIs; `bootstrap_panel_ci`
re-derives case-clustered CIs (N_BOOT=10000, SEED=20260715) that correctly
widen the multi-variant strata.

### 4e. Partial concordance (feeds Fig 2 panel B — secondary/exploratory)
```bash
venv/bin/python scripts/nsclc/analyze_partial_concordance.py
# -> results/analysis/v2_genie_bpc_nsclc_partial_concordance_summary.csv
```

### 4f. Omar-style per-model summary (concordance null, Fig 2A / Fig 3 / Table 2)
```bash
venv/bin/python scripts/nsclc/analyze_genie_bpc.py --cohort nsclc --model gemini-2.5-flash --save
# ...repeat --model for each arm
```
Writes `*_adherence.csv`, `*_concordance_rates.csv`, `*_flip_rates.csv`,
`*_case_detail.csv` per model.

---

## Step 5 — Figures

`plots/plot_publishable_nsclc.py` is the orchestrator: it writes the numbered
canonical set directly into `figures/manuscript/`. For each target it uses
`_regen_or_skip(dst, generator_script, [upstream_source_png])` — if the
canonical `Fig*.png` already exists it is kept; otherwise it copies the named
upstream render; otherwise it tells you which generator to rerun.

```bash
venv/bin/python plots/plot_publishable_nsclc.py
```

The three robustness panels (Fig 9) and a few others are produced by dedicated
upstream scripts, then folded in by the orchestrator:

| Manuscript figure | Canonical file | Generator |
|---|---|---|
| Fig 1 | `Fig1_cohort_description.png` | `plots/plot_genie_cohort_strata.py` |
| Fig 2 | `Fig2_concordance_stability.png` | `plot_publishable_nsclc.py` (+ 4e for panel B) |
| Fig 3 | `Fig3_concordance_by_variant.png` | `plots/plot_concordance_by_variant.py` |
| Fig 4 | `Fig4_dissociation_6vendor.png` | `plot_publishable_nsclc.py` (reads 4a CSVs) |
| Fig 5 | `Fig5_forest_ses_vs_race_6vendor.png` | `plot_publishable_nsclc.py` (reads 4a CSVs) |
| Fig 5b | `Fig5alt_framing_volcano.png` | `plots/plot_framing_volcano.py` |
| Fig 6 | `Fig6_soft_split_harmonized.png` | `plot_publishable_nsclc.py` (reads `panel_stigma_rates.csv`) |
| Fig 7 | `Fig7_stigma_gradient_softened.png` | `plot_publishable_nsclc.py` |
| Fig 7b | `Fig7b_stigma_dose_response.png` | `plots/plot_stigma_dose_response.py` |
| Fig 8 | `Fig8_stigma_breakdown_ORIGINAL_see_caveat.png` | `plots/plot_stigma_breakdown.py` |
| Fig 9a | `Fig9a_circularity_template_notes.png` | `plots/plot_circularity_ci.py` |
| Fig 9b | `Fig9b_pmc_real_note_replication.png` | `plots/plot_pmc_replication.py` |
| Fig 9c | `Fig9c_natural_embedding_salience_control.png/.pdf` | `plots/plot_natural_ab.py` |
| Fig S1 | `FigS1_judge_validation_single_rater_CAVEAT.png` | judge track (Step J) |
| Fig S2 | `FigS2_pmc_note_provenance.png` | `plots/plot_pmc_provenance.py` |
| Fig S3 | `FigS_concordance_by_variant_avg_paired.png` | `plots/plot_concordance_by_variant_avg.py` |
| Fig S4 | `FigS_soft_split_avg.png` | `plot_publishable_nsclc.py` |
| Fig S5 | `FigS_stigma_breakdown_avg.png` | `plots/plot_stigma_breakdown.py` |
| Fig S6 | `FigS_intermodel_agreement.png` | `plots/plot_intermodel_agreement.py` |

Authoritative figure↔legend mapping: `figures/manuscript/NARRATIVE_ORDER.md`.

> The lowercase source renders that the orchestrator can copy from
> (`fig4_circularity.png`, `fig4_pmc_replication.png`, `fig5_natural_ab.png`,
> `figS1_judge_validation.png`, `fig_genie_cohort_strata.png`) were moved to
> `figures/archive/manuscript_superseded/` during repo cleanup. The canonical
> numbered files already exist, so the orchestrator keeps them as-is. To
> regenerate a canonical figure from scratch, rerun its generator from the
> table above (which re-emits the lowercase render into `figures/manuscript/`),
> then rerun `plot_publishable_nsclc.py`.

---

## Step J — Judge validation track (Fig S1 + stigma-inflation footnote)

```bash
venv/bin/python scripts/nsclc/build_judge_packet.py     # -> adjudication/judge_items.jsonl
venv/bin/python scripts/nsclc/run_judge.py              # -> adjudication/judge_labels.json (Sonnet, batch)
```
`finalize_panel.py` reads `adjudication/judge_labels.json` if present for the
classifier-vs-judge inflation footnote. **Open item (per NARRATIVE_ORDER.md):**
FigS1 is a single self-labeled rater (κ=0.30); a second independent rater on
`adjudication/gold_random40_helper.csv` is required before the judge-dependent
results are called validated.

---

## Canonical manuscript inputs under `results/`

The manuscript draws its numbers/figures from these files (all under
`results/`):

- `results/baseline/v2_genie_bpc_nsclc[_<model>]_checkpoint.json` — the six raw
  model-output checkpoints (panel source of truth).
- `results/analysis/v2_genie_bpc_nsclc[_<model>]_soft_intensity.csv` and
  `_flip_rates.csv` — per-model effect sizes / flip rates (Figs 4, 5, 5b).
- `results/analysis/panel_stigma_rates.csv` and
  `panel_stigma_rates_clustered.csv` — per-stratum stigma gradient (Figs 6, 7, 7b).
- `results/analysis/v2_genie_bpc_nsclc_partial_concordance_summary.csv` —
  Fig 2 panel B.
- `results/analysis/v2_genie_bpc_nsclc[_<model>]_{adherence,concordance_rates}.csv` —
  concordance null (Fig 2A, Fig 3, Table 2).
- `adjudication/judge_labels.json` — judge adjudication (FigS1 + footnote).

Robustness tracks (Fig 9) additionally use:
`data/processed/genie_bpc_nsclc_templates_with_notes.json` (9a),
`data/processed/pmc_nsclc_with_notes.json` (9b), and
`data/processed/genie_bpc_nsclc_natural150_with_notes.json` (9c), with their
analysis CSVs under `results/analysis/` (`v2_pmc_nsclc_*`, natural-embedding
outputs).

Do not treat any `synthetic_structured*` / `synthetic_unstructured*` files as
manuscript inputs — those are the earlier CancerGUIDE synthetic-note track,
superseded by the GENIE (`v2_genie_bpc_nsclc*`) runs for this paper.
