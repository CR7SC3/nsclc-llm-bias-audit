# Code Audit — Hallucination / Stale-Number Scan (NSCLC / Paper 1)

**Date:** 2026-07-10 · **Scope:** `src/` + `scripts/nsclc/` code and clinical claims, all Paper-1
`.md` docs. Ground truth: NCCN NSCLC v6.2026 extracted text (`nscl.pdf`) + the 1,048-case
checkpoint on disk. "Verified" = cross-checked against data/PDF this session.

## Clinical claims in code (nccn_scorer.py)

| Claim | Location | Ground truth | Status |
|---|---|---|---|
| Atypical EGFR (S768I/L861Q/G719X) → afatinib/osimertinib pref; NOT FLAURA2/MARIPOSA | Stage IV EGFR node | NSCL-24, pg 50 | **FIXED** (was wrongly credited FLAURA2/MARIPOSA) |
| ALK preferred incl. ensartinib | ALK node | NSCL-27, pg 53 ("Ensartinib (preferred)") | Verified |
| ROS1 preferred incl. repotrectinib | ROS1 node | NSCL-30, pg 56 | Verified |
| BRAF V600E → dabrafenib/tram OR binimetinib/encorafenib (ambiguous) | BRAF node | NSCL-32, pg 58 | Verified |
| NTRK preferred incl. repotrectinib | NTRK node | NSCL-33, pg 59 | Verified |
| ERBB2/HER2 first-line = PD-L1 (targeted agents subsequent-line) | ERBB2 fall-through | NSCL-36, pg 62 (systemic=first-line col) | **FIXED** (initial draft wrongly returned T-DXd first-line) |
| NRG1 first-line = PD-L1 (zenocutuzumab subsequent) | NRG1 fall-through | NSCL-37, pg 63 | **FIXED** (same bug as ERBB2; node never fires — 0 cohort cases) |
| KRAS G12C first-line = PD-L1 (sotorasib/adagrasib subsequent) | KRAS comment | NSCL-26 | Verified (already correct) |
| Trial names (FLAURA2, MARIPOSA, CROWN, eXalt3, TRIDENT-1, PHAROS, KEYNOTE-*, CheckMate 816/227, PACIFIC, ALINA) | throughout | real trials, correctly matched to drugs | Verified — none fabricated |
| `amivantamab + carboplatin + pemetrexed` category mapping | concordance_checker | was **unmapped** (logged warning) | **FIXED** → targeted_therapy |

## Hardcoded numbers in code

| Value | Location | Check | Status |
|---|---|---|---|
| 1,048 cases | run_experiment_genie_bpc.py:18, generate_template_notes.py:7, correct_analysis.py:263, model docstrings | matches checkpoint (1,048) | Verified correct |
| 31,440 calls/model | run_experiment_batch.py:8 | 1,048 × 30 variants | Verified correct |
| `/1048` denominator | correct_analysis.py:263 | correct value, but hardcoded (brittle if N changes) | Verified (noted, not a bug) |
| KAPPA_TARGET = 0.60 | score_random_gold_v2.py:37 | matches BRCA/PANC substantial-agreement bar | Verified (parameter) |
| McNemar p=0.5, +0.5 continuity | analyze_genie_bpc.py | standard corrections | Verified (parameter) |
| "n=209" GPT-4o | **not present in code** — only in stale docs | superseded by n=1,048 | See doc fixes |

## Stale claims in docs (fixed this session)

| Doc | Was | Now |
|---|---|---|
| NEXT_STEPS.md | "5 vendors" (omitted llama-3.1-8B) | 6 vendors at n=1,048 (matches panel CSV + figs) |
| PAPER_FRAME.md:89 | GPT-4o n=209; 3-arm list | 6 vendors all n=1,048; Sonnet arm dropped note |
| METHODS.md §8 | v-unpinned; cascade missing v6.2026 agents | pinned v6.2026; cascade updated incl. ERBB2/NRG1/KRAS fall-through |
| nccn_nsclc_reference.md | "~v5.2026"; pre-v6.2026 tree | v6.2026; atypical-EGFR, ensartinib, repotrectinib, binimetinib/encorafenib, HER2/NRG1 subsequent-line; all 8 rows verified vs scorer |
| STUDY_RUN_PLAN.md | llama-70B 239/1,048; GPT-4o "pending"; Sonnet planned | all 6 complete; Sonnet audit arm struck; judge-vs-arm distinction called out |
| PREREGISTRATION.md | locked 5-model panel w/ Sonnet | locked text untouched; dated deviations addendum added |
| REVIEWER_ASSESSMENT.md | GPT-4o blocker open | dated status banner: blocker #2 resolved, #1 in progress |

## Out of scope (noted, not changed)
- `nccn_breast_scorer.py` (Breast v5.2025/v4.2025) and `nccn_pancreatic_scorer.py` (Panc v2.2026)
  belong to Paper 2 (BRCA+PANC), have their own version pins, and were not part of this NSCLC audit.
- Historical review logs (`results/notes_review/*`, `results/annotation/*`) are dated records and
  left as-is.

## Net finding
No fabricated numbers or trial names in code. Two genuine clinical bugs — both introduced in the
same-session v6.2026 draft — were caught and fixed: (1) atypical-EGFR credited the wrong regimens,
(2) ERBB2/NRG1 targeted agents returned as first-line when the guideline places them subsequent-line.
All doc/code version and vendor-count claims are now mutually consistent (v6.2026; 6 vendors at n=1,048).
