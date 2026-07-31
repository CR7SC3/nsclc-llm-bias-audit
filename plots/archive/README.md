# plots/archive/ — superseded plotting scripts

Moved here 2026-07-30 during a `plots/` cleanup. These scripts do **not** feed the
current locked 6-figure manuscript build, its supplements (FigS01–S13), or the poster.
Nothing in the live `plots/` set imports them, and no code under `scripts/`, `src/`, or
`tests/` references them. Kept (not deleted) because 9 were untracked by git and would
otherwise be unrecoverable.

**The live build chain remains in `plots/` (24 scripts):** orchestrator
`plot_publishable_nsclc.py`, compositor `combine_figures.py`, `build_poster_figures.py`,
and the per-panel / supplement generators they call.

## Why each was archived

- **Dropped panels** (removed from the 6-figure plan as redundant): `plot_fig2_forest.py`
  (forest ≈ tier panel), `plot_concordance_heatmap.py` (≈ direction heatmap),
  `regen_dissociation_wide.py` + `draft_fig2_dissociation.py` (dissociation dropped from Fig 2),
  `plot_ladder.py` (mitigation ladder → Discussion only), `plot_stigma_dose_response.py`.
- **Superseded old fig1**: `plot_fig1_dissociation.py`, `plot_fig1_setup.py`.
- **Pilot era**: `plot_genie_pilot50.py`, `plot_genie_concordance.py`,
  `plot_genie_concordance_single.py`.
- **Archived-narrative figures** (already in `figures/archive/not_in_narrative_2026-07/`):
  `plot_advanced_care_race.py`, `plot_advanced_care_other_demographics.py`,
  `plot_note_provenance.py`, `plot_response_highlight.py`.
- **Old draft passes** (pre-`plot_publishable_nsclc.py`): `plot_results.py`,
  `plot_manuscript_figs.py`, `plot_slides_v2.py`, `plot_nccn_flowchart.py`,
  `plot_pmc_realnote.py`, `plot_continuous_scores.py`, `plot_soft_bias.py`,
  `plot_soft_bias_extended.py`, `plot_soft_bias_unstructured.py`, `plot_unstructured.py`,
  `plot_v2_structured.py`, `plot_v2_unstructured.py`, `plot_v3_intervention.py`.

## Restore one

    git mv plots/archive/<name>.py plots/<name>.py     # tracked files
    mv     plots/archive/<name>.py plots/<name>.py     # untracked files
