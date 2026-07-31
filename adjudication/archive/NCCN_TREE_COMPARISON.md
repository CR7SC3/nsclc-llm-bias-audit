# NCCN NSCLC Decision Tree — Your Scorer vs. Ground-Truth Guidelines

> **RESOLVED 2026-07-10:** All gaps identified below have since been implemented — the scorer is
> now pinned to **v6.2026** with atypical-EGFR, ensartinib, repotrectinib, binimetinib/encorafenib
> added, and ERBB2/NRG1 correctly handled as subsequent-line. See `NCCN_RESCORE_BEFORE_AFTER.md`
> for the implementation and rescore. This document is retained as the dated pre-implementation
> comparison (describes the original `v1.2025` state).

**Compared:** `src/evaluate/nccn_scorer.py` (implemented tree AT TIME OF COMPARISON, pinned `NSCLC v1.2025`)
**Against:** `nscl.pdf` = **NCCN Clinical Practice Guidelines, NSCLC Version 6.2026** (06/12/26)
**Scope of comparison:** Stage IV / advanced first-line, treatment-naive — the biomarker-directed
first-line nodes the EquityGUIDE study actually scores. (Stage I–III surgical/CRT logic was
spot-checked and aligns; the biomarker pathways are where the divergences are.)
**Date:** 2026-07-09

---

## Headline

Your tree is **structurally sound and correct on the common driver nodes**, but it is built against an
**older guideline version** than the ground-truth PDF. The PDF is **v6.2026**; your scorer is pinned to
**v1.2025** (and the human reference doc says "~v5.2026"). Between those versions NCCN **added preferred
agents and two whole biomarker pathways**, so the gaps are all in the same direction: the ground truth
has *more* options than your tree encodes.

**14 first-line nodes checked:** 6 FULL match · 4 PARTIAL (missing a newly-preferred agent) ·
1 WRONG (atypical EGFR) · 2 MISSING (ERBB2/HER2, NRG1) · 1 silent gap (KRAS G12C).

---

## Discrepancies that matter (ranked)

### 1. Atypical EGFR (S768I / L861Q / G719X) — **WRONG pathway** 🔴
Your `_is_egfr_sensitising()` folds `other_sensitising` into the classic **exon19del/L858R** node,
so an atypical-EGFR case is scored as acceptable = {osimertinib, osi+chemo (FLAURA2),
amivantamab+lazertinib (MARIPOSA)}. But NCCN gives atypical EGFR a **separate page (NSCL-24)**:
first-line preferred = **afatinib OR osimertinib**; FLAURA2 and MARIPOSA are **not** indicated there.
Your tree both **omits afatinib** (a preferred option) and **credits two regimens that don't apply**.
This is the one place the tree gives an affirmatively incorrect acceptable-set, not just an incomplete one.

### 2. Two biomarker pathways absent entirely — **MISSING** 🔴
- **ERBB2 / HER2 mutation (NSCL-36):** preferred = fam-trastuzumab deruxtecan, **zongertinib**,
  **sevabertinib**. No node in your scorer — a HER2 case falls through to the PD-L1/chemo-IO branch.
- **NRG1 fusion (NSCL-37):** zenocutuzumab-zbco. No node (rare, but it's in the ground truth).

### 3. Newly-preferred agents missing from existing nodes — **PARTIAL** 🟠
Each of these nodes is otherwise correct but is missing a v6.2026 preferred first-line agent, which
means a model answer citing the new drug would be **falsely scored discordant**:
- **ALK (NSCL-27):** missing **ensartinib** (cat1 preferred).
- **ROS1 (NSCL-30):** missing **repotrectinib** (preferred).
- **NTRK (NSCL-33):** missing **repotrectinib** (preferred).
- **BRAF V600E (NSCL-32):** missing **binimetinib/encorafenib** (co-preferred). Your node also returns
  a single non-ambiguous answer where NCCN now has **two** preferred combinations.

### 4. KRAS G12C — **silent gap** 🟡
There is no KRAS node. A KRAS G12C case is scored by the PD-L1/histology branch. That happens to be
*right* (sotorasib/adagrasib are subsequent-line only, so first-line is PD-L1-directed), but it's correct
by accident rather than by design — the case is unhandled. v6.2026 added KRAS G12C to required
biomarker testing, so this is worth an explicit node even if first-line therapy is unchanged.

---

## Nodes that FULLY match ground truth ✅
EGFR exon19del/L858R (NSCL-21) · EGFR exon20ins (NSCL-25) · MET exon14 (NSCL-34) ·
RET fusion (NSCL-35) · PD-L1 ≥50% driver-negative (NSCL-28/38) · PD-L1 <50% non-squamous chemo-IO
(NSCL-30/39, KEYNOTE-189). For these, your primary answer and acceptable set correctly capture the
NCCN preferred first-line regimen(s).

---

## Recommended fixes (in priority order)
1. **Split the atypical-EGFR node** out of `_is_egfr_sensitising`: give S768I/L861Q/G719X its own
   acceptable set = {afatinib, osimertinib (+ dacomitinib/erlotinib/gefitinib as other-recommended)};
   remove FLAURA2 / MARIPOSA from it. *(correctness bug — do first)*
2. **Add ensartinib** to ALK; **add repotrectinib** to ROS1 and NTRK; **add binimetinib/encorafenib**
   to BRAF (and mark BRAF ambiguous). *(under-crediting bug — inflates false discordance)*
3. **Add ERBB2/HER2 and NRG1 nodes.** *(coverage gap)*
4. **Add an explicit KRAS G12C node** (first-line = PD-L1-directed; note TKIs are subsequent-line).
5. **Re-pin `NCCN_GUIDELINE_VERSION` to the version you actually validate against** (the PDF is
   v6.2026; the code says v1.2025 and the reference doc says ~v5.2026 — all three should agree).

## Caveat on scope
The study scores **first-line, treatment-naive** answers, so subsequent-line/progression logic in the
PDF (T790M testing, resistance-mutation switching, local therapy for oligoprogression) was **not**
scored against your tree — those pages exist in the ground truth but are out of your stated scope.
Stage I–III surgical/adjuvant/chemo-RT logic aligned on spot-check and was not exhaustively tabulated.

See `nccn_tree_comparison.csv` for the full node-by-node table with page references.
