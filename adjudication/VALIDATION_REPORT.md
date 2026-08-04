# VALIDATION REPORT: EquityGUIDE Paper 1 (NSCLC)
_Consolidated deep-dive across four review seats · 2026-07-15_

This report merges the stats-verifier, figure-audit, red-team, and codebase-audit seats
(detailed files: `archive/VALIDATION_stats.md`, `archive/VALIDATION_figures.md`, `archive/VALIDATION_redteam.md`,
`archive/VALIDATION_codebase.md`). Every number was recomputed from `results/` or `data/processed/`;
nothing is asserted from memory.

## Bottom line
The manuscript's **quantitative claims are sound and reproducible.** Every flip-rate mean (6/6),
every spot-checked Table 2 Cohen's d (8/8), the max-effect values, cohort N / stage / histology /
site / EGFR / PD-L1 counts, and the concordance table all reproduce **exactly** from the results
files. The core scientific finding (race≈0, monotone SES gradient, decision-stable / framing-shifted
dissociation) is verified and robust. What blocks submission is **not the science**: it is a small
set of editorial/disclosure gaps and two missing supplementary artifacts.

## The scorer-version question: RESOLVED
The manuscript's concordance numbers were computed with the **pre-rescore scorer (NSCLC v1.2025)**
and match `baseline_concordance.json` exactly. This week's correction to **v6.2026** changes absolute
concordance by −3.0 to +0.4pp (five vendors drop, llama-3.1-8b rises +0.4) but leaves the **demographic−reference deltas (the actual bias signal)
within 0.5pp**. The single BH-FDR decision survivor (deepseek::underinsured net downgrade) reproduces
in direction and significance; only its exact counts are scorer-version-dependent (94/40→ manuscript's
94/48 under v1.2025; 91/40 under v6.2026).

**Recommendation (low-risk):** keep the frozen v1.2025 numbers and add ONE footnote:
*"Concordance was scored against NCCN NSCLC v1.2025; re-scoring against v6.2026 shifts absolute
concordance by between −3.0pp and +0.4pp across the six vendors and leaves every
demographic−reference differential unchanged within 0.5pp
(see adjudication/archive/NCCN_RESCORE_BEFORE_AFTER.md)."* This preserves a clean frozen analysis while
disclosing the update. Full refresh is the alternative but is more work for no change to conclusions.

## Per-seat verdicts

### Stats (33 claims): PASS
- Flip means 6/6 exact; Table 2 Cohen's d 8/8 exact; N/stage/histology/site/EGFR/BRAF/NTRK/PD-L1 exact.
- Minor: 5 biomarker counts differ by 1–4 cases (KRAS G12C 120 vs 116, ALK 43 vs 42, MET14 23 vs 22,
  ROS1 20 vs 19, RET 15 vs 14), a status-field counting-convention difference, not a data error.
  Reconcile the Table 1 / Abstract counts to the manuscript's own extraction logic before submission.

### Figures: 2 BLOCKING GAPS
- 11/13 referenced figures present and correct; both 6-vendor figures visually confirmed to show 6 vendors.
- Caveat files honestly reflected in text.
- **MISSING: FigS0** (cohort/PD-L1 breakdown, cited in Table 1 text).
- **MISSING: Supplementary Table S3** (`supplementary_table_29variants_per_model.csv`, cited in Table 2 footnote).

### Red-team: 3 BLOCKING disclosure fixes
1. Inline single-rater hedge (κ=0.57, PABAK 0.83) at EVERY headline percentage/d-value (currently only in the epigraph + Limitations).
2. Cite Viera & Garrett (2005) or Hallgren (2012) next to the agreement descriptor.
3. Disclose English-only scope (bears directly on the immigrant/limited-English null tier).
- Well-defended already: circularity (both controls), prereg deviation, salience artifact.

### Codebase: 1 BLOCKING + hygiene
- All 4 Methods-named scripts exist; scorer pinned v6.2026.
- **BLOCKING: reference placeholders 7 (→ NCCN v6.2026), 8 (CancerGUIDE), 14 (deployment vendors), + Funding.**
- **Manuscript is UNTRACKED in git**: `git add docs/paper1_nsclc/manuscript_nsclc.md`.
- Hygiene (non-blocking): stale n=209 gpt-4o files + dropped sonnet-5 stubs in results/baseline are archive candidates. Paper1/Paper2 separation clean.

## Consolidated action list → see SUBMISSION_READINESS.md
