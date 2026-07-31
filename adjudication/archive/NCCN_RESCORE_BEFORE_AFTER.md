# NCCN Tree Update + Rescore — Before/After Robustness Report

**Date:** 2026-07-10 (rev. — includes ERBB2/NRG1 line-of-therapy correction)
**Change set:** `src/evaluate/nccn_scorer.py`, `src/evaluate/concordance_checker.py`,
`src/analyze/response_parser.py` (+ `tests/test_nccn_scorer.py`)
**Ground truth:** NCCN NSCLC **v6.2026** (`nscl.pdf`), verified against extracted algorithm text
**Scoring pipeline:** replicated `correct_analysis.py` exactly — concordance on unique-answer
cases (all acceptable answers map to a single category), `unknown` parses excluded from the
denominator, demographic concordance averaged across the non-reference variants.

## What changed in the code
1. **Version re-pinned** `NSCLC v1.2025` → **`NSCLC v6.2026`** (now matches the PDF).
2. **Atypical EGFR (S768I/L861Q/G719X) split into its own NSCL-24 node** — afatinib/osimertinib
   (preferred) + dacomitinib/erlotinib/gefitinib. Previously these 19 cases were mis-routed to the
   exon19del/L858R node and credited FLAURA2 + MARIPOSA, which NCCN does **not** indicate for
   atypical mutations. *(correctness fix, verified against NSCL-24 text)*
3. **Newly-preferred first-line agents added:** ensartinib (ALK NSCL-27), repotrectinib (ROS1
   NSCL-30 + NTRK NSCL-33), binimetinib+encorafenib (BRAF NSCL-32 — node now correctly ambiguous
   with two co-preferred combos). All three confirmed in the **FIRST-LINE THERAPY** column.
4. **ERBB2/HER2 (NSCL-36) and NRG1 (NSCL-37) handled correctly as SUBSEQUENT-line drivers.**
   NSCL-36/37 both list **systemic therapy (PD-L1-directed) as FIRST-LINE**; the HER2 agents
   (fam-trastuzumab deruxtecan, zongertinib, sevabertinib) and zenocutuzumab appear only in the
   **SUBSEQUENT THERAPY** column. Treatment-naive first-line ERBB2/NRG1 cases therefore fall
   through to the PD-L1/chemo-IO branch — same as KRAS G12C. *(This corrects an over-eager first
   draft that had returned the targeted agents as first-line; the 18 stage-IV ERBB2 cases are now
   scored on the correct PD-L1 pathway.)*
5. **12+ response-parser keywords added** so first-line answers naming afatinib, dacomitinib,
   erlotinib, gefitinib, ensartinib, repotrectinib, binimetinib, encorafenib, sotorasib, adagrasib,
   zongertinib, sevabertinib, zenocutuzumab, or trastuzumab-deruxtecan are recognized as
   `targeted_therapy` instead of falling to `unknown`.
6. **Category-map bug fixed:** `amivantamab + carboplatin + pemetrexed` (the exon20ins answer) was
   previously **unmapped** (logged "Unmapped NCCN answer") → now `targeted_therapy`.

All 52 scorer tests pass, including 4 new ones (atypical-EGFR NSCL-24; ERBB2/NRG1/KRAS-G12C
first-line = PD-L1, not the targeted agent).

## Before → After concordance (6 vendors, n_unique 607 → 609 cases)

| Model | Reference concordance | Demographic concordance | Unknown parses | **Differential (dem − ref)** |
|---|---|---|---|---|
| gemini-2.5-flash | 81.7% → 78.8% (-2.9) | 82.8% → 79.8% (-3.0) | 501 → 8 | +1.1 → +1.0 pp |
| deepseek-chat | 90.7% → 89.0% (-1.7) | 90.6% → 88.5% (-2.1) | 184 → 1 | -0.1 → -0.5 pp |
| llama-3.3-70b | 75.9% → 73.9% (-2.0) | 75.5% → 73.8% (-1.7) | 301 → 27 | -0.4 → -0.1 pp |
| llama-3.1-8b | 49.5% → 49.9% (+0.4) | 49.0% → 49.5% (+0.6) | 1005 → 772 | -0.5 → -0.4 pp |
| gpt-4o | 89.7% → 86.7% (-3.0) | 88.7% → 85.7% (-3.0) | 170 → 3 | -1.0 → -1.0 pp |
| gpt-4o-mini | 55.6% → 53.1% (-2.4) | 56.4% → 54.2% (-2.3) | 603 → 84 | +0.9 → +1.0 pp |

## What moved, and what did not
- **`unknown` parses fell 68%** (2764 → 895 across all vendors×cases) — the
  parser keywords are doing their job; legitimate targeted-therapy answers are no longer discarded.
- **Absolute concordance dropped slightly (−1.7 to −3.0 pp for most vendors; llama-3.1-8b +0.4).**
  This is the *honest* direction: the previously-`unknown` responses that are now scored are **not**
  all concordant, so folding them into the denominator lowers the rate. The old numbers were modestly
  inflated by silently dropping hard-to-parse answers.
- **The differential (demographic − reference) is stable — every vendor moves ≤0.4 pp**
  (gemini +1.1→+1.0, deepseek −0.1→−0.5, llama-70B −0.4→−0.1, llama-8B −0.5→−0.4,
  gpt-4o −1.0→−1.0, gpt-4o-mini +0.9→+1.0). This is the key robustness result: the scorer/parser
  gaps were **demographic-blind** (they mis-scored every variant of a case identically), so they
  cancel in the variant-vs-reference contrast that the paper's bias claims rest on.

## Bottom line
Updating the tree to v6.2026 and fixing the parser **does not change the study's bias findings**.
It (a) removes a genuine correctness bug (atypical EGFR), (b) closes 68% of the
unexplained `unknown` parses, (c) scores ERBB2/NRG1 on the correct line-of-therapy pathway, and
(d) reports concordance on a cleaner, guideline-current, near-complete denominator. Absolute
concordance is marginally lower and more defensible; the differential signal — the actual result —
is unchanged within <0.5 pp.

_Artifacts: `baseline_concordance.json`, `after_concordance.json` (raw per-model numbers)._
