# figures/manuscript/: NSCLC figure set in manuscript narrative order

Working title: *Stigma Without Downgrade: Separating Warranted Socioeconomic
Responsiveness From Generated Stigma in Large Language Model Cancer-Treatment
Recommendations.* Target: JMIR AI.

**Main figures live in `figures/manuscript_combined/`, not in this folder.**
This folder (`figures/manuscript/`) now holds only the supplementary figures
(`FigS01…FigS12`) plus the two source schematics that Figure 1 is built from.
Full captions for the main figures are in
`figures/manuscript_combined/CAPTIONS.md`; the panel-source build table is in
`figures/manuscript_combined/README.md`. This file was previously the index
for an interim 10-main-figure set under this folder: that set has since been
superseded by the 6-figure architecture below, confirmed against what
`docs/paper1_nsclc/manuscript_nsclc.md` actually embeds.

## Main figures (in `figures/manuscript_combined/`)

| # | File | Legend |
|---|------|--------|
| 1 | Figure1_study_design.png | Study design and counterfactual audit workflow. (A) End-to-end pipeline: 1,048 GENIE BPC cases → demographics-neutral note → 29 demographic labels + no-demographics control (30 conditions × 1,048 cases = 31,440 queries) → 6 models = 188,640 responses → hard (NCCN concordance) + soft (stigma-framing) scoring vs. control (BH-FDR). (B) Counterfactual variant design across nine tiers / seven demographic axes. |
| 2 | Figure2_decision_stability.png | Demographic labels do not change the guideline-concordant treatment decision. (A) NCCN concordance, reference vs. variants, six models, TOST equivalence (pre-registered confirmatory outcome). (B) Flip rate vs. reference: ≈17% for every variant including the privileged comparator, a noise floor, not demographic instability. (C) Per-model net aggressiveness-tier shift by variant. |
| 3 | Figure3_care_intensity.png | Care intensity is the intermediate bias layer: with the guideline-concordant decision held constant (Fig 2), the treatment options a response foregrounds (trial mention, de-escalation language) shift against marginalized patients across several axes. (A) mixed-effects net change by axis group. (B) per-label detail. |
| 4 | Figure4_ses_not_race.png | The framing shift is socioeconomic, not racial. (A) Volcano of all 174 model×variant framing contrasts. (B) Inter-model agreement (Spearman ρ) of the framing-effect vector. (C) Mean added framing intensity by axis: income/housing and insurance elevated, race/ethnicity ≈0. |
| 5 | Figure5_stigma_anatomy.png | Anatomy of the stigma signal. (A) Appropriate SDOH-responsive content vs. stigmatizing content, net % by stratum. (B) Stigmatizing signal decomposed into 4 classifier dimensions (2 starred = pre-registered defensible composite). (C) Judge-adjudicated stigmatizing-language rate, Cochran-Armitage trend across 5 ordered SES strata (significant increasing trend in 5/6 models). |
| 6 | Figure6_robustness_precision_filter.png | Signal is robust to note generation and label salience, and survives a stricter definition. (A) circularity control on LLM-free template notes. (B) real-note replication on 40 PMC case reports. (C) salience control (bracketed tag vs. natural prose). (D) grounding-aware bias decision-tree (condensed); full 4-panel decomposition in FigS10. |

## Supplementary figures (in this folder, `figures/manuscript/`)

Legends below are condensed from the manuscript's own captions
(`docs/paper1_nsclc/manuscript_nsclc.md`, Supplementary Figures section):
that is the authoritative wording; this table is a navigation aid.

| # | File | Legend |
|---|------|--------|
| S1 | FigS01_pmc_note_provenance.png | Sourcing/length distribution for the 40 real PMC notes used in Figure 6B. |
| S2 | FigS02_concordance_by_variant_avg_paired.png | Pooled NCCN concordance per demographic label (matched case×model pairs, McNemar vs. reference, BH-FDR). No label significant. Companion to Figure S7. |
| S3 | FigS03_soft_split_avg.png | Model-averaged appropriate-vs-stigmatizing decomposition underlying Figure 5A (bar = mean of six models, per-model dots). Companion to Figure 5A. |
| S4 | FigS04_stigma_breakdown_avg.png | Averaged stigma decomposition by behavior, mean net % per dimension, defensible composite marked. Companion to Figure S9. |
| S5 | FigS05_intermodel_agreement.png | 6×6 Spearman heatmap of the 29-variant induced framing-effect vector (off-diagonal median ρ=0.72). |
| S6 | FigS06_bias_tree_validation.png | Bias-tree agreement (Cohen's κ) with the human rater vs. raw regex and the LLM judge, n=60 blind set. Companion to Figure 6D. |
| S7 | FigS07_concordance_by_variant.png | Per-variant NCCN concordance, six models, BH-FDR-significant deviations from reference marked. Companion to Figure 4. |
| S8 | FigS08_framing_volcano.png | Volcano of all 174 model×variant framing contrasts (effect size vs. BH-FDR), colored by variant class. Companion to Figure 6. |
| S9 | FigS09_stigma_breakdown_original.png | Stigma composite split into 4 component behaviors, stacked per model across six panels. Companion to Figure 5A. |
| S10 | FigS10_bias_tree_decomposition.png | Full 4-panel bias decision-tree: (A) flag reclassification, (B) per-stratum STIGMA rate regex vs. tree, (C) descriptive harm-type decomposition, (D) Gate-2 counterfactual ablation. Expands the condensed Figure 6D. Companion to Figure 6D and Figure S6. |
| S11 | FigS11_mitigation_overcorrection.png | Naive prompt-level mitigation overcorrects (exploratory, DeepSeek + Gemini, n=151): every mitigation prompt drives judge-labeled stigma to near zero only by converting warranted SES-responsive care into neutral boilerplate; guideline treatment tier unchanged throughout. Referenced in Discussion and Table S12. |
| S12 | FigS12_restricted_control_attrition.png | Attrition schematic for the restricted-to-concordant-control sensitivity analysis: each model's full 1,048-case scoreable cohort split into control-concordant (597–872 per model) vs. excluded. Restricting the hard-endpoint bias-gap to this subset finds no harm gradient (0/174 Fisher-significant); the soft framing signal (pre-registered 2-dim composite) holds and concentrates on the same SES-disadvantage variants (93/174 significant). See Supplementary Methods and Supplementary Results. |

## Notes
- Figure 6's panels A–C (circularity control, PMC replication, natural-prose salience) use a
  consistent color convention across the panel: template/baseline vs. real-note vs.
  natural-embedding conditions: see the panel source scripts in `plots/` for the exact keys.

## Archived (not in the manuscript narrative)
Moved to `figures/archive/not_in_narrative_2026-07/` (reversible): `Fig10_advanced_care_by_race`,
`FigS6_advanced_care_other_demographics`, `FigS_flip_direction`, `FigS_note_provenance`,
`FigS_response_highlight` (png + pdf each). These are uncited candidates, not part of the paper.

## Still open (repo-side, not a figure-formatting fix)
- **Judge validation**: a second independent rater on the retained 60-item gold set
  is still pending; disclosed as a single-rater limitation in Methods.
