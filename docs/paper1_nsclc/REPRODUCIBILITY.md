# Paper 1 (NSCLC): Reproducibility Recipe

End-to-end, linear recipe to reproduce the NSCLC manuscript
(`docs/paper1_nsclc/manuscript_nsclc.md`) from the raw GENIE BPC download
through every canonical figure in `figures/manuscript/`.

This document covers **Paper 1 (NSCLC) only**. Paper 2 (BRCA + PANC) moved to
a separate repository (`EquityGUIDE_BRCA_PANC`) on 2026-07-29 and is out of
scope here. One shared file remains in this repo because Paper 1's mitigation
scripts import from it: `scripts/brca_panc/analyze_omar_metrics_pilot.py`.

All script names, arguments, and input/output paths below were read directly
from the scripts in `scripts/nsclc/`, `src/generate/`, and `plots/`. Where a
detail could not be verified from the code it is flagged as **[VERIFY]**.

---

## 0. Environment

- **Python**: 3.9.6. `venv/` is local and gitignored, not part of a fresh clone -- create your
  own with the Install step below, which pins the same version. All commands below invoke the
  interpreter explicitly as `venv/bin/python` so the pinned environment is used consistently.
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

> **requirements.txt completeness gap:** `requirements.txt` is present but
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
| 4g | `scripts/nsclc/restricted_bias_gap.py` | 6 result files | `results/analysis/v2_genie_bpc_nsclc_restricted_bias_gap_by_variant.csv`, `_restricted_venn_counts.csv` (Fig S12, Supplementary Results) |
| 5 | `plots/combine_figures.py` + `plots/plot_fig3_care_intensity.py` (main), one script per supplementary figure | step-4 CSVs | `figures/manuscript_combined/Figure*.png`, `figures/manuscript/FigS*.png` |
| J | `scripts/nsclc/build_judge_packet.py` → `run_judge.py` | responses + gold | `adjudication/judge_labels.json` (feeds FigS1 + adjudication footnote) |

---

## Step 0: Raw data (ACCESS-GATED)

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

## Step 1: Build the processed cohort

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

## Step 2: Generate free-text notes

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

## Step 3: Per-model experiment runs (the 6-model panel)

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

> **These checkpoints and their final `_results.json` are not committed to
> GitHub**: several are 100-400 MB, over GitHub's per-file limit, and the
> repo's Data Availability statement already covers them ("Generated notes
> and results: available upon reasonable request"). `.gitignore` excludes
> `results/baseline/*.json` (a small set of early pilot results committed
> before the full 6-model run is unaffected). Only the much smaller derived
> CSVs under `results/analysis/` (Step 4) are committed, since those are what
> the manuscript actually cites.

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

**Anthropic (Sonnet) arm:** use the Message Batches runner (50% cheaper,
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

## Step 4: Analysis (no API calls; runs on cached checkpoints)

### 4a. Per-model figure-input CSVs (feeds Figs 4, 5, 5b)
```bash
# Run once per subset/model; --save writes results/analysis/v2_genie_bpc_nsclc[_<model>]_*.csv
venv/bin/python scripts/nsclc/analyze_results_v2.py --subset genie_bpc_nsclc --save
# ...repeat --subset genie_bpc_nsclc_<model> for each of the other five arms
```
Produces `..._soft_intensity.csv` (Cohen's d + BH q per variant) and
`..._flip_rates.csv` (flip rate + Wilson CI): the exact files
`plots/plot_publishable_nsclc.py` reads (`BASE = results/analysis/v2_genie_bpc_nsclc`).

### 4b. Corrected confirmatory statistics (Fig 4 equivalence annotations, Results text)
```bash
venv/bin/python scripts/nsclc/correct_analysis.py       # prints to stdout
```
Directional decision test (sign test + signed tier-shift d/CI), TOST
equivalence with pre-specified margin, grid-wide BH-FDR, and the
soft-bias defensible-vs-stigma split. Console report: capture stdout for the
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

### 4e. Partial concordance (feeds Fig 2 panel B, secondary/exploratory)
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

## Step 5: Figures

The manuscript's **6 main figures** live in `figures/manuscript_combined/`
(`Figure1_study_design.png` … `Figure6_robustness_precision_filter.png`).
Five of the six are composited by `plots/combine_figures.py` from titleless
panel sources in `figures/manuscript_combined/panels/`; Figure 3 is built
standalone by `plots/plot_fig3_care_intensity.py`. See
`figures/manuscript_combined/README.md` for the exact panel-to-source-script
table and `figures/manuscript_combined/CAPTIONS.md` for the full captions.

```bash
venv/bin/python plots/combine_figures.py
venv/bin/python plots/plot_fig3_care_intensity.py
```

The **12 supplementary figures** are written directly into
`figures/manuscript/` by dedicated scripts in `plots/`, one script per figure
(a few scripts also emit a titleless panel copy into
`figures/manuscript_combined/panels/` for reuse in a main figure):

| Supp. figure | Canonical file | Generator |
|---|---|---|
| Fig S1 | `FigS01_pmc_note_provenance.png` | `plots/plot_pmc_provenance.py` |
| Fig S2 | `FigS02_concordance_by_variant_avg_paired.png` | `plots/plot_concordance_by_variant_avg.py` |
| Fig S3 | `FigS03_soft_split_avg.png` | `plots/plot_publishable_nsclc.py` (`fig6_soft_split_avg()`; also feeds Figure 5A panel) |
| Fig S4 | `FigS04_stigma_breakdown_avg.png` | `plots/plot_stigma_breakdown.py` (also feeds Figure 5B panel) |
| Fig S5 | `FigS05_intermodel_agreement.png` | `plots/plot_intermodel_agreement.py` (also feeds Figure 4B panel) |
| Fig S6 | `FigS06_bias_tree_validation.png` | `plots/plot_bias_tree.py` |
| Fig S7 | `FigS07_concordance_by_variant.png` | `plots/plot_concordance_by_variant.py` |
| Fig S8 | `FigS08_framing_volcano.png` | `plots/plot_framing_volcano.py` (also feeds Figure 4A panel) |
| Fig S9 | `FigS09_stigma_breakdown_original.png` | `plots/plot_stigma_breakdown.py` |
| Fig S10 | `FigS10_bias_tree_decomposition.png` | `plots/plot_bias_tree.py` (also feeds Figure 6D panel, condensed) |
| Fig S11 | `FigS11_mitigation_overcorrection.png` | `plots/plot_mitigation_overcorrection.py` |
| Fig S12 | `FigS12_restricted_control_attrition.png` | `plots/plot_restricted_attrition.py` (reads `results/analysis/v2_genie_bpc_nsclc_restricted_venn_counts.csv`, from `scripts/nsclc/restricted_bias_gap.py`) |

Authoritative figure↔legend mapping and navigation aid:
`figures/manuscript/NARRATIVE_ORDER.md`.

> **Reproducibility note.** As of 2026-07-31 every script above writes the
> exact filename the manuscript currently cites (verified against the
> manuscript's `## Figures` and `### Supplementary Figures` sections). Several
> had drifted from their cited filename after a manual renumbering pass and
> were corrected in place. `figures/archive/` holds superseded renders from
> earlier naming schemes; nothing there is cited by the current manuscript.

---

## Step J: Judge validation track (stigma-inflation footnote)

```bash
venv/bin/python scripts/nsclc/build_judge_packet.py     # -> adjudication/judge_items.jsonl
venv/bin/python scripts/nsclc/run_judge.py              # -> adjudication/judge_labels.json (Sonnet, batch)
```
`finalize_panel.py` reads `adjudication/judge_labels.json` if present for the
classifier-vs-judge inflation footnote. **Open item:** the 60-item gold set is a
single self-labeled rater (κ=0.57, PABAK 0.83). Two second-rater packets exist
for this: `adjudication/gold_flagged_rater{1,2}.csv` (classifier-flagged/contested
subset, n=60) is complete (kappa 0.386, labeled by a co-author); the
representative sample `adjudication/gold_random_rater{1,2}.csv` (n=60, the
sample underlying the headline kappa=0.57) is still unlabeled and is required
before the judge-dependent results are called fully validated. Re-score with
`venv/bin/python scripts/nsclc/score_random_gold_v2.py --gold-tag random` (and
`--gold-tag flagged`) once labeled.

---

## Canonical manuscript inputs under `results/`

The manuscript draws its numbers/figures from these files (all under
`results/`). Figure numbers below are the current 6-main + 12-supplementary
scheme (see `figures/manuscript/NARRATIVE_ORDER.md`), not the interim
numbering used in earlier drafts of this document.

- `results/baseline/v2_genie_bpc_nsclc[_<model>]_checkpoint.json`: the six raw
  model-output checkpoints (panel source of truth; **not distributed via
  GitHub**, see the note under Step 3).
- `results/analysis/v2_genie_bpc_nsclc[_<model>]_soft_intensity.csv` and
  `_flip_rates.csv`: per-model effect sizes / flip rates (Figures 2-5).
- `results/analysis/panel_stigma_rates.csv` and
  `panel_stigma_rates_clustered.csv`: per-stratum stigma gradient (Figure 5,
  Figures S3, S4, S9).
- `results/analysis/v2_genie_bpc_nsclc_partial_concordance_summary.csv`:
  partial-concordance sensitivity check (background/exploratory; not currently
  cited by a numbered figure in the manuscript text).
- `results/analysis/v2_genie_bpc_nsclc[_<model>]_{adherence,concordance_rates}.csv`:
  concordance null (Figure 2, Table 2).
- `results/analysis/v2_genie_bpc_nsclc_restricted_bias_gap_by_variant.csv` and
  `_restricted_venn_counts.csv`: restricted-to-concordant-control sensitivity
  analysis (Figure S12, Supplementary Results). Computed with the pre-registered
  2-dimension stigma composite (`adherence_compliance`, `sdoh_generation`);
  do not substitute an older copy of this CSV computed with a broader composite.
- `adjudication/judge_labels.json`: judge adjudication (Figure S6 + footnote).

Robustness tracks (Figure 6) additionally use:
`data/processed/genie_bpc_nsclc_templates_with_notes.json` (6A, circularity
control), `data/processed/pmc_nsclc_with_notes.json` (6B, PMC replication),
and `data/processed/genie_bpc_nsclc_natural150_with_notes.json` (6C, salience
control), with their analysis CSVs under `results/analysis/` (`v2_pmc_nsclc_*`,
natural-embedding outputs).

Do not treat any `synthetic_structured*` / `synthetic_unstructured*` files as
manuscript inputs: those are the earlier CancerGUIDE synthetic-note track,
superseded by the GENIE (`v2_genie_bpc_nsclc*`) runs for this paper.
