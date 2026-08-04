# figures/manuscript_combined/: NSCLC paper, 6-figure main architecture

Composites built by `plots/combine_figures.py` (Method-A paste: each source
plot becomes a panel, with bold A/B/C/D labels in a header band), except
Figure 3, which is built standalone by `plots/plot_fig3_care_intensity.py`.
Regenerate with `python3 plots/combine_figures.py` (Figures 1, 2, 4, 5, 6)
and `python3 plots/plot_fig3_care_intensity.py` (Figure 3).

**Titles stripped.** Panels are composited from TITLELESS source plots in `panels/`,
regenerated with the interpretive banner titles ("Fig N | …") and footnote captions
suppressed: those belong in the caption. Kept on-figure: axis labels, legends,
per-model subplot names, and inline stats (Δ/TOST, trend z/p, CIs). Figure 1's two
schematics (one BioRender export, one counterfactual-design panel from
`figures/manuscript/Fig02_counterfactual_design.png`) have no baked-in
banners and are used as-is.

This is the set actually embedded in `docs/paper1_nsclc/manuscript_nsclc.md`
(see its `## Figures` section). Full captions are in `CAPTIONS.md` in this folder.

| Combined figure | Theme | Panels (source) | Built by |
|---|---|---|---|
| Figure1_study_design.png | Study design and counterfactual audit workflow | **A** `Fig1A_Experimental_Design_v2.png` (BioRender) · **B** `figures/manuscript/Fig02_counterfactual_design.png` | `combine_figures.py` |
| Figure2_decision_stability.png | Decision stable under demographics (flips are a noise floor) | **A** `panels/p_concordance_stability.png` · **B** `panels/p_flip_avg.png` · **C** `panels/p_flip_heatmap.png` (full-width) | `combine_figures.py` |
| Figure3_care_intensity.png | Care intensity is the intermediate bias layer | built standalone, not from `panels/` | `plot_fig3_care_intensity.py` |
| Figure4_ses_not_race.png | Framing shift is socioeconomic, not racial | **A** `panels/p_volcano.png` · **B** `panels/p_intermodel.png` · **C** `panels/p_tier_bias.png` | `combine_figures.py` |
| Figure5_stigma_anatomy.png | Anatomy of the stigma signal | **A** `panels/p_soft_split_avg.png` · **B** `panels/p_stigma_breakdown_avg.png` · **C** `panels/p_gradient.png` | `combine_figures.py` |
| Figure6_robustness_precision_filter.png | Signal survives note-source, salience, and a stricter definition | **A** `panels/p_template.png` · **B** `panels/p_pmc.png` · **C** `panels/p_natural.png` · **D** `panels/p_bias_tree.png` | `combine_figures.py` |

Cohort → **Table 1** (already in the manuscript); the cohort plot stays in the supplement.

## Draft caveats (these are Method-A paste composites, not camera-ready)
- Banner titles/footnotes are stripped, but a couple of **structural internal sub-labels**
  survive: the dissociation panel keeps its own "(A) Treatment selection / (B) Response
  framing", so it reads as internal (A)/(B) nested under the outer figure letter. Method B
  would relabel these into one flat scheme.
- **Figure 6D** uses the *full 4-panel* bias-tree, and its internal panel titles were
  claim-length so they got stripped too (the sub-plots are now unlabeled inside). The locked
  plan calls for a **condensed single-panel** headline there (needs a new drawer in
  `plot_bias_tree.py`), deferred to the camera-ready pass.
- Panel density (model strips inside a single panel) should get a pass before submission;
  not re-checked since the panel set last changed.
- Figure 1 is the exception: both panels are BioRender/static rasters, so this paste **is**
  the camera-ready approach for it (re-export from BioRender as PDF/SVG if possible).

This 6-figure scheme is what `docs/paper1_nsclc/manuscript_nsclc.md` currently embeds
(confirmed by grep of its `## Figures` section); the renumbering pass described in the
memory note `paper1_figure_grouping` has already run. That memory is stale and should be
updated to match.
