# Should you update the tree from v6.2026 and rescore? — Impact Analysis

> **IMPLEMENTED 2026-07-10:** This was the pre-decision memo (mentions the then-current
> code=v1.2025 / ref-doc=~v5.2026 / PDF=v6.2026 mismatch). All recommendations here have since
> been implemented and the version reconciled to **v6.2026**; see `NCCN_RESCORE_BEFORE_AFTER.md`
> for the executed before/after rescore. Retained as the dated decision record.

**Date:** 2026-07-09 · **Basis:** full NSCLC checkpoint (1,048 cases × 30 variants = 31,440 responses)

## The scoring architecture decides the answer
Concordance is scored at the **category** level (`concordance_checker._NCCN_TO_CATEGORY`): a
response is concordant if its parsed category matches any `acceptable_answers` entry. **Every
targeted agent — alectinib, and the would-be-added ensartinib / repotrectinib /
binimetinib+encorafenib / afatinib — collapses to the single category `targeted_therapy`**,
which the affected nodes already return.

**Consequence: editing the tree alone moves almost nothing.** Adding ensartinib to the ALK
acceptable set doesn't change concordance, because an ALK case that returns `alectinib` already
resolves to `targeted_therapy`, and a model answer of "ensartinib" would too — *if the parser
recognized it.*

## The real lever is the response parser, not the tree
`ResponseParser` has **no keyword** for ensartinib, repotrectinib, binimetinib, encorafenib,
afatinib, dacomitinib, zongertinib, sevabertinib, sotorasib, adagrasib, trastuzumab-deruxtecan,
or zenocutuzumab. Measured on the real responses:

- **1,490 / 31,440 responses (4.7%) parse to `unknown`** → counted non-concordant by default.
- **1,440 of those (4.58% of all responses) mention a drug the parser can't see.** Breakdown of
  those unknown-and-un-keyworded mentions: sotorasib 908, adagrasib 738, trastuzumab-deruxtecan
  453, afatinib 359, dacomitinib 184.

This 4.7% is the **upper bound** on how much any rescore could move — and the realistic figure is
much smaller, because most of those would stay non-concordant even after fixes:
- **sotorasib / adagrasib (KRAS G12C):** subsequent-line only; for first-line KRAS the acceptable
  set is PD-L1-directed IO, so these stay non-concordant whether or not the parser sees them. **No rescue.**
- **afatinib / dacomitinib (atypical EGFR):** rescued only if BOTH the atypical-EGFR node is fixed
  to accept afatinib AND the parser learns the keyword. **Rescue requires both edits.**
- **trastuzumab-deruxtecan (HER2):** rescued only if an ERBB2/HER2 node is added AND the parser
  learns the keyword. **Rescue requires both edits.**

## It will NOT change your headline bias findings
The concordance metric is a **secondary "task-competence" sanity check** (PAPER_FRAME F1), not the
paper's headline. The headline is *differential* framing/flip rates across demographic variants,
which all share the **same clinical profile per base case**. The parser/tree gaps are
**demographic-blind** — they mis-score `white_male_private` and `black_female_medicaid` identically
for the same case — so they shift the **absolute** concordance level but largely **cancel** in the
variant-vs-reference comparison. Rescoring is very unlikely to change any bias conclusion.

## Recommendation: yes, update — as a defensibility/robustness fix, in this order
1. **Fix the atypical-EGFR node** (the one correctness bug: it currently credits FLAURA2 + MARIPOSA
   for S768I/L861Q/G719X, which NSCL-24 does not indicate; and omits afatinib). Do this regardless.
2. **Add parser keywords** for the 12 drugs above — this is the ONLY change that measurably moves
   concordance (rescues legitimate targeted/HER2 answers now forced to `unknown`).
3. **Add missing preferred agents** (ensartinib→ALK, repotrectinib→ROS1/NTRK,
   binimetinib+encorafenib→BRAF) and **missing pathways** (ERBB2/HER2, NRG1) and an explicit
   **KRAS G12C** node — for guideline coverage/defensibility.
4. **Re-pin `NCCN_GUIDELINE_VERSION`** to the version you validate against (code=v1.2025,
   ref-doc=~v5.2026, PDF=v6.2026 — reconcile).
5. **Rescore and report before/after** concordance as a robustness check. Expect a small absolute
   uptick (bounded ≤4.7%, realistically 1–2 pp once KRAS cases are excluded) and **no change to the
   differential bias results.**

**Do NOT** ship a tree-only edit and call it a rescore — without the parser keywords it changes
nothing, and without the version re-pin the mismatch remains a reviewer target.
