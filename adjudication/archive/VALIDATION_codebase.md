# VALIDATION — Codebase / Reproducibility Audit (Paper 1 NSCLC)

_Generated 2026-07-15._

## Methods-named scripts (all EXIST)
| Script (Methods) | Path | Status |
|---|---|---|
| analyze_results_v2.py | scripts/nsclc/analyze_results_v2.py | OK |
| correct_analysis.py | scripts/nsclc/correct_analysis.py | OK |
| plot_circularity_ci.py | plots/plot_circularity_ci.py | OK |
| plot_pmc_replication.py | plots/plot_pmc_replication.py | OK |

All four scripts the manuscript Methods names are present and runnable (correct_analysis.py was executed this session for the sign-test reproduction).

## Reference placeholders (BLOCKING — editor will reject with `[Author to insert...]` in refs)
| Ref | Placeholder | Action |
|---|---|---|
| 7 | NCCN guideline version ('[Author to insert the specific version number]') | Insert **NCCN NSCLC v6.2026** — the scorer is now pinned there (`src/evaluate/nccn_scorer.py:22 NCCN_GUIDELINE_VERSION="NSCLC v6.2026"`). |
| 8 | CancerGUIDE dataset/benchmark citation | Insert full citation for the synthetic-case source referenced in Methods. |
| 14 | Deployment-vendor sources (Nuance DAX, Abridge, Epic GPT-4o) | Insert vendor/peer-reviewed sources, or soften the Introduction deployment claims to not need them. |
| Funding | '[Author to insert funding source...]' | Fill or state 'No external funding.' |

## Git tracking
- **`docs/paper1_nsclc/manuscript_nsclc.md` is UNTRACKED (`??`).** It was written to disk this session from the artifact store but never `git add`-ed. Add + commit so the manuscript is under version control.

## Repo hygiene (non-blocking; reader-confusion risk)
- **Stale n=209 GPT-4o files still present:** `results/baseline/v2_genie_bpc_nsclc_n300_gpt-4o_{checkpoint,results}.json`. The analysis correctly uses the full `v2_genie_bpc_nsclc_gpt-4o_*` (n=1,048) files; the n300 files are superseded and could confuse a reader/reviewer inspecting the repo. Recommend moving to an `archive/` folder (do not delete).
- **Dropped Claude-Sonnet arm stubs still present:** `results/baseline/v2_genie_bpc_nsclc_claude-sonnet-5_{checkpoint,results,batch_manifest}.json` + `sonnet5_batch_pilot25_*.log` (25-case stub). Manuscript correctly excludes this arm; files are archive-worthy.
- **Paper1/Paper2 separation: CLEAN** — no BRCA/PANC files misfiled in scripts/nsclc, results/analysis, or figures/manuscript.
- Legacy lowercase duplicate figures (fig4_circularity.png etc.) superseded by numbered manuscript versions — archive candidates.