# Archived gold sets (superseded, NOT deleted)

**Archived 2026-07-15.** These are the earlier single-rater gold sets. They are
kept for provenance and because the **targeted set is the only evidence for the
regex over-counting argument** (human sided with judge 12/17 on contested cases).
Superseded as the *representative* validation by the random-60 two-rater set
(`../gold_random_rater1_alvaro.csv` + `../gold_random_rater2.csv`); see
`RANDOM60_VALIDATION.md` (also archived here 2026-07-29).

- `gold_targeted.csv` (+ helpers) — 35-item set, **enriched for classifier-flagged
  contested cases**. Human-vs-judge kappa=0.30, human-vs-regex kappa=0.21. Base
  rate inflated by construction (NOT a prevalence estimate). Its purpose was
  contested-boundary adjudication, not reliability.
- `gold_random40_helper.csv` (+ .numbers) — 40-item single-rater representative
  set. Human-vs-judge kappa=0.47, human-vs-regex kappa=0.44.

To restore: move the file back up to `adjudication/`. `score_gold.py` expects
`gold_targeted.csv` at the original path.

---

## Archived 2026-07-29 — adjudication/ trimmed to manuscript-essential files

The parent `adjudication/` folder was cleaned to hold only what the NSCLC (Paper 1)
manuscript pipeline reads plus the reviewer-cited evidence. The following working
files were moved here (reversible — move any back up to `adjudication/` to restore).
Nothing was deleted.

**July-10 code-audit + NCCN-rescore memos** (all self-labeled RESOLVED/IMPLEMENTED;
the durable result — bias findings unchanged under the v6.2026 scorer — is preserved
in `VALIDATION_stats.md` and, in the manuscript, as the frozen-v1.2025 footnote):
- `AUDIT_SUMMARY_2026-07-10.md`
- `CODE_AUDIT_FINDINGS.md`
- `NCCN_RESCORE_BEFORE_AFTER.md`
- `NCCN_TREE_COMPARISON.md` (self-labeled RESOLVED, pre-implementation record)
- `RESCORE_IMPACT_ANALYSIS.md` (self-labeled IMPLEMENTED, decision record)
- `nccn_tree_comparison.csv` (data behind the two NCCN memos)

**Validation deep-dive detail files** (the four review-seat files consolidated into
the kept `../VALIDATION_REPORT.md`, plus the interim status notes):
- `VALIDATION_stats.md`, `VALIDATION_figures.md`, `VALIDATION_redteam.md`, `VALIDATION_codebase.md`
- `RANDOM60_VALIDATION.md` (interim single-rater representative result)
- `RANDOM_TWO_RATER_STATUS.md` (two-rater status; live status is tracked in `../SUBMISSION_READINESS.md`)

**Duplicates / binary working copies / orphans** (not read by any script or doc):
- `after_concordance.json`, `baseline_concordance.json` — duplicate the repo-root
  copies; `baseline` is byte-identical to root, `after` DIFFERS from root (root is the
  pipeline-canonical copy). Kept here for provenance.
- `gold_random_rater1.numbers` — Apple Numbers working copy; the exported
  `../gold_random_rater1_alvaro.csv` is what the code reads.
- `claims_manifest.csv`, `claims_manifest.json` — unreferenced validation artifact.

Kept in `adjudication/`: judge/bias-tree pipeline I/O (`judge_items.jsonl`,
`judge_labels.json`, `random_judge_{items,labels}`, `gold_random_rater1_alvaro.csv`,
`gold_template.csv`, `judge_bias_probe_items.jsonl`, `flagged_judge_items.jsonl`,
`contrastive_packet_60.{csv,jsonl}`), the reviewer-cited two-rater gold sets
(`gold_random_rater{1,2}.csv`, `gold_flagged_rater{1,2}.csv`), and the consolidated
validation record (`VALIDATION_REPORT.md`, `VALIDATION_SUMMARY.md`, `SUBMISSION_READINESS.md`).
