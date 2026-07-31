# VALIDATION — Figure Audit (Paper 1 NSCLC)

_Generated 2026-07-14; every referenced figure mapped to figures/manuscript/, 6-vendor figures viewed._

## Figure reference → file map
| Ref | File | Status |
|---|---|---|
| Fig 2 | Fig2_concordance_stability.png | OK |
| Fig 4 | Fig4_dissociation_6vendor.png | OK |
| Fig 5 | Fig5_forest_ses_vs_race_6vendor.png | OK |
| Fig 5b | Fig5alt_framing_volcano.png | OK |
| Fig 6 | Fig6_soft_split_harmonized.png | OK |
| Fig 7 | Fig7_stigma_gradient_softened.png | OK |
| Fig 7b | Fig7b_stigma_dose_response.png | OK |
| Fig 8 | Fig8_stigma_breakdown_ORIGINAL_see_caveat.png | OK |
| Fig 9a | Fig9a_circularity_template_notes.png | OK |
| Fig 9b | Fig9b_pmc_real_note_replication.png | OK |
| Fig 9c | Fig9c_natural_embedding_salience_control.png | OK |
| Fig S0 | — | MISSING (no FigS0 on disk; text says 'full breakdown in Figure S0') |
| Fig S_intermodel_agreement | FigS_intermodel_agreement.png | OK |
| Fig caveat-honesty | Fig8 ORIGINAL_see_caveat / FigS1 single_rater_CAVEAT | OK — κ=0.30 & single-rater disclosed in Methods+Results caveat+Limitations |

## Key checks
- **6-vendor figures verified by viewing:** Fig4_dissociation_6vendor.png and Fig5_forest_ses_vs_race_6vendor.png both show all six vendor series (Gemini-2.5-flash, DeepSeek-chat, Llama-3.3-70B, Llama-3.1-8B, GPT-4o, GPT-4o-mini) in the legend.
- **Caveat honesty OK:** the caveat-named files (Fig8_stigma_breakdown_ORIGINAL_see_caveat, FigS1_judge_validation_single_rater_CAVEAT) correspond to caveats the manuscript discloses in-text — κ=0.30 and single-rater validation appear in Abstract, Methods, a dedicated Results caveat paragraph, and Limitations. No hidden overclaim.

## Gaps (BLOCKING for submission)
1. **FigS0 MISSING** — Table 1 text says 'full breakdown in Figure S0' (cohort/PD-L1 breakdown) but no `FigS0*` file exists in figures/manuscript/. Either create it or change the pointer (a `fig_genie_cohort_strata.png` and `FigS2_pmc_note_provenance.png` exist and may serve).
2. **Supplementary Table S3 MISSING** — Table 2 footnote references `supplementary_table_29variants_per_model.csv`; no such file exists anywhere in the repo. Must be generated (the per-model Cohen's d is in results/analysis/*_soft_intensity.csv, so it's a straightforward export) or the footnote removed.

## Non-blocking
- Fig5b is referenced as 'Figure 5b' but the file is `Fig5alt_framing_volcano.png` (naming mismatch, not missing) — fine as long as the caption/figure-list maps 5b→that file at typesetting.
- Duplicate/legacy lowercase figures (fig4_circularity.png, fig4_pmc_replication.png, fig5_natural_ab.png, figS1_judge_validation.png) are superseded by the numbered manuscript versions — a codebase-hygiene item, not a manuscript error.