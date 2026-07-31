# Code-Hallucination Audit + Doc Refresh — Summary (NSCLC / Paper 1)

**Date:** 2026-07-10 · **Request:** "check all my code, make sure there are no hallucinations,
and update all .md files to be up to date."

## Headline
A real clinical bug — **self-introduced in the same-session v6.2026 draft** — was caught and fixed:
the ERBB2/HER2 (NSCL-36) and NRG1 (NSCL-37) nodes returned targeted agents (T-DXd, zongertinib,
sevabertinib, zenocutuzumab) as **first-line**, but the v6.2026 algorithm places those in the
**SUBSEQUENT-therapy** column — first-line is PD-L1-driven systemic therapy. The scorer now falls
those biomarkers through to the PD-L1 branch (same as KRAS G12C). This was flagged by the
human-authored reference doc, which correctly stated the line-of-therapy — the code had contradicted it.

## What was audited and found
- **Clinical claims in `nccn_scorer.py`:** every v6.2026 pathway/agent verified against the extracted
  NCCN PDF text (NSCL-21/24/26/27/30/32/33/36/37). All trial names (FLAURA2, MARIPOSA, eXalt3,
  TRIDENT-1, PHAROS, KEYNOTE-*, CheckMate 816/227, PACIFIC, ALINA) are real and correctly matched.
  No fabricated drugs, trials, or categories.
- **Hardcoded numbers:** 1,048 cases and 31,440 calls verified against the checkpoint on disk;
  "n=209" appears in **no code** (only in now-annotated stale doc claims). Parameters (κ target 0.60,
  McNemar corrections) are legitimate.
- **Two genuine bugs fixed:** (1) atypical-EGFR wrongly credited FLAURA2/MARIPOSA — now NSCL-24
  (afatinib/osimertinib); (2) ERBB2/NRG1 first-line/subsequent-line inversion (above).
  Plus a latent category-map bug (`amivantamab + carboplatin + pemetrexed` was unmapped).

## Rescore (before/after, corrected scorer)
6 vendors, unique-answer concordance. `unknown` parses fell **68%** (parser keyword additions);
absolute concordance −1.7 to −3.0 pp (honest — previously-dropped answers now scored); **the
demographic−reference differential (the bias signal) is stable to <0.5 pp for every vendor.**
Bias findings unchanged. Details: `NCCN_RESCORE_BEFORE_AFTER.md`.

## Docs brought current
- `nccn_nsclc_reference.md` → v6.2026; all 8 mutation rows programmatically verified to match scorer.
- `METHODS.md` → scorer pinned v6.2026; Stage IV cascade updated.
- `NEXT_STEPS.md` → corrected "5 vendors" → **6 vendors at n=1,048** (had omitted llama-3.1-8B).
- `PAPER_FRAME.md` → GPT-4o n=209 → n=1,048; Sonnet arm dropped.
- `STUDY_RUN_PLAN.md` → lineup table refreshed (all 6 complete; Sonnet audit arm struck).
- `PREREGISTRATION.md` → locked text preserved; **dated deviations addendum** added.
- `REVIEWER_ASSESSMENT.md` → dated **status banner** (GPT-4o blocker resolved; rater in progress).
- Adjudication working memos (`NCCN_TREE_COMPARISON.md`, `RESCORE_IMPACT_ANALYSIS.md`) got
  RESOLVED/IMPLEMENTED banners so their pre-fix v1.2025 descriptions aren't misread as current.

## Tests
`test_nccn_scorer.py` + `test_partial_concordance.py`: **81 passed** (added 4: atypical-EGFR NSCL-24;
ERBB2/NRG1/KRAS-G12C first-line = PD-L1, not the targeted agent).

## Scope notes
- Breast/pancreatic scorers (Paper 2) have their own version pins and were not part of this NSCLC audit.
- Dated review/annotation logs left as historical records.

## Consistency check
Scorer, reference doc, METHODS, and rescore report now all agree: **NCCN NSCLC v6.2026, 6 vendors at n=1,048.**
