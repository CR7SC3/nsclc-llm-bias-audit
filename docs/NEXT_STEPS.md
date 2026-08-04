# EquityGUIDE: Next Steps (follow-up to the NSCLC project)

**Prepared:** 2026-07-08 · **Updated:** 2026-07-15 (manuscript draft now in-repo &
fully validated by a 4-seat deep-dive; A2 GPT-4o fold-in done; A3 Claude Sonnet arm dropped;
NSCLC two-rater gold sheets built). · **Scope:** what to do next
given the state of Paper 1 (NSCLC) and the in-progress Paper 2 (BRCA + PANC) follow-up.
Grounded in a read of the repo as of the update date, not the planning docs alone: several
planning docs are now stale (see §0).

---

## 0. What actually changed since the docs were written (read this first)

Three facts on disk contradict what the older planning markdown still says. They reshape
the priority order:

1. **The GPT-4o NSCLC arm is complete AND folded in.** `REVIEWER_ASSESSMENT.md`
   (2026-07-02) treats GPT-4o as a submission blocker at n=209/1,048. It is now at
   **n=1,048** (`v2_genie_bpc_nsclc_gpt-4o_results.json`) and **already incorporated** into
   the corrected analysis and figures: it is in `correct_analysis.py`'s `MODELS`, in
   `finalize_panel.py`'s `ARMS`, and present at full n=1,048 in
   `results/analysis/panel_stigma_rates.csv`. gpt-4o is also **visually confirmed plotted**
   in the 6-vendor headline figure `Fig4_dissociation_6vendor.png` (2026-07-09 inspection):
   it appears as its own GPT-4o series in the legend and as points across all strata in both
   the treatment-selection and response-framing panels. **Gating item #2 in that assessment
   is fully resolved: nothing left to do here** (was formerly A2; see below).

2. **The BRCA/PANC pilots are run and analyzable**, and the pilot signal trends
   **against the pre-registered primary hypothesis of Paper 2** (details in §2). This is
   the single most consequential thing in the repo right now.

3. **Claude Sonnet has been DROPPED from the model lineup.** The
   `..._claude-sonnet-5_results.json` file was only a 25-case stub, never a real arm; per
   the 2026-07-09 decision it is dropped rather than completed, so the confirmatory NSCLC
   panel is the **6 vendors at n=1,048** (gemini-2.5-flash, deepseek-chat, llama-3.3-70B,
   llama-3.1-8B, gpt-4o, gpt-4o-mini), matching `finalize_panel.py` ARMS,
   `results/analysis/panel_stigma_rates.csv`, and the `Fig4/Fig5_*_6vendor` figures. Note
   this is a lineup decision only: **claude-sonnet-4-6 remains
   the blinded LLM-judge** for stigma-classifier validation (a different role; see §3), and
   is unaffected.

> **2026-07-15 note:** The single source of truth for what blocks submission is now
> **`adjudication/SUBMISSION_READINESS.md`** (produced by the validation deep-dive). The
> A1–A6 list below is retained for history; A2/A3/A6 are done, and A1/A4/A5 map onto the
> readiness checklist's BLOCKING items.

The remaining NSCLC gating items are now narrower still:

4. **The manuscript prose draft NOW EXISTS and is validated.** A complete ~59KB draft
   (`docs/paper1_nsclc/manuscript_nsclc.md`: Abstract/Intro/Methods/Results/Discussion/
   Limitations/Declarations/14 refs) was written into the repo 2026-07-15 (it had previously
   lived only as a Claude Science artifact, which is why earlier NEXT_STEPS said "no draft
   exists"). A four-seat validation deep-dive (stats / figures / red-team / codebase; see
   `adjudication/VALIDATION_REPORT.md` + `SUBMISSION_READINESS.md`) confirmed **every
   quantitative claim reproduces exactly** from `results/`: flip means 6/6, Table 2 Cohen's d
   8/8, cohort counts, and the concordance table. The science is sound; what remains is
   editorial/disclosure (see A1 + the readiness checklist), not analysis.

5. **The two-rater gold-set validation is scaffolded but not yet labeled**: the second
   blinded rater closes the single-rater κ=0.57 (60-item random set) risk (see A1). Both the NSCLC random and
   classifier-flagged (APPROPRIATE-vs-STIGMA) two-rater sheets exist under `adjudication/`
   (`gold_random_rater{1,2}.csv`, `gold_flagged_rater{1,2}.csv`), built 2026-07-09; they need
   two independent raters to label them, then `score_random_gold_v2.py --gold-tag {random,flagged}`.

---

## 1. Priority A: Finish and ship Paper 1 (NSCLC). It is the follow-up's blocker.

Paper 2's own timeline (`PAPER2_FRAME.md`) is explicit: *"Paper 1 submitted → immediately
pre-register Paper 2 … Paper 2 full runs: after Paper 1 under review."* Paper 1 is the
critical path. The science is done; what remains is execution:

- **A1. Second blinded rater on the gold set (highest credibility-per-hour fix).**
  Both `PAPER_FRAME.md` and the reviewer assessment call single-rater validation the one
  top risk for a paper whose contribution rests on a stigma classifier's validity.
  **The two-rater sheets now exist (built 2026-07-09):** `adjudication/gold_random_rater{1,2}.csv`
  (60-item uniform sample, STIGMA/APPROPRIATE/NEUTRAL: prevalence + recall) and
  `adjudication/gold_flagged_rater{1,2}.csv` (60 classifier-flagged items,
  APPROPRIATE-vs-STIGMA: the contested-boundary reliability number). Both raters label
  the same blinded ids independently; `score_random_gold_v2.py --gold-tag {random,flagged}`
  then computes rater-vs-rater κ + consensus-vs-judge/classifier. What remains is the
  human/logistics step: recruit the second rater (a lab-mate/mentor; a clinician is
  stronger but not required) and label. **Do this first; it gates the credibility of
  everything else and it has the longest lead time.** Report the κ you get (cite Viera &
  Garrett / Hallgren), and the stigma rate as a contested range, not a point estimate.
- **A2. ~~Fold the completed GPT-4o arm into the corrected analysis.~~ DONE (2026-07-09
  verify).** GPT-4o is in `correct_analysis.py`'s `MODELS` and `finalize_panel.py`'s
  `ARMS`, present at full n=1,048 in `results/analysis/panel_stigma_rates.csv`, and in the
  regenerated 6-vendor figures `Fig4_dissociation_6vendor.png` /
  `Fig5_forest_ses_vs_race_6vendor.png` (dated 2026-07-08). gpt-4o visually confirmed as its
  own plotted series in `Fig4_dissociation_6vendor.png` (2026-07-09). No action remaining.
- **A3. ~~Decide the Claude Sonnet arm.~~ DONE: DROPPED (2026-07-09).** The 25-case
  `..._claude-sonnet-5_results.json` stub is dropped from the model lineup, not completed.
  Confirmatory NSCLC panel = 6 vendors at n=1,048 (gemini-2.5-flash, deepseek-chat,
  llama-3.3-70B, llama-3.1-8B, gpt-4o, gpt-4o-mini). Ensure any lineup table in
  `STUDY_RUN_PLAN.md` / `METHODS.md` / `PREREGISTRATION.md` lists these six and does not
  imply a Sonnet audit arm. **Unchanged:** claude-sonnet-4-6 stays the blinded LLM-judge for classifier
  validation: that is a separate role, not an audited model.
- **A4. Switch primary CIs to a case-clustered method** (bootstrap or cluster-robust
  variance). The reviewer's independent bootstrap already showed the pooled-response
  Wilson intervals understate uncertainty on this repeated-measures design. Low effort,
  closes a real statistical objection.
- **A5. Move the note-provenance / circularity framing to the top of the README** and
  point to Fig 9a (template) + Fig 9b (PMC). The evidence already rebuts the objection;
  the exposition just buries it.
- **A6. ~~Write the actual manuscript.~~ DONE: draft exists & validated (2026-07-15).**
  `docs/paper1_nsclc/manuscript_nsclc.md` is a complete ~59KB draft (Abstract, Intro,
  Methods, Results incl. Tables 1–2 and Figs 2–9, Discussion, Limitations, Declarations,
  14 refs). A four-seat deep-dive (`adjudication/VALIDATION_REPORT.md`) confirmed every
  quantitative claim reproduces exactly from `results/`. What remains is **revision, not
  authoring**: see `adjudication/SUBMISSION_READINESS.md` for the itemized blockers
  (2 missing supplementary artifacts, reference placeholders, inline κ hedging, git-add).

---

## 2. Priority B: Resolve the Paper 2 hypothesis crisis BEFORE the full runs

**This is the most important strategic decision in the project.** The pilot data
(n≈50/cohort, gemini-flash + deepseek) already trends **against** Paper 2's pre-registered
primary hypothesis.

The locked H1 (`PREREGISTRATION_PAPER2.md` §4) predicts the SES-stigma gradient is
**larger in PANC (grim prognosis) than in BRCA (favorable)**. The exploratory pilot shows
the opposite direction in **both** models:

| Model | BRCA gradient | PANC gradient | Δ (PANC−BRCA) | vs. H1 |
|-------|--------------:|--------------:|--------------:|--------|
| gemini-2.5-flash | +61.9 pp | +52.7 pp | **−9.2 pp** | against |
| deepseek-chat | +63.9 pp | +54.0 pp | **−9.9 pp** | against |

The controls behave exactly as designed (race-only ≈2%, `white_*_private` ≈0–4%,
`no_demographics` ≈0–4%), so the instrument is working: the *cross-cancer ordering* is
just not what was predicted. The within-cancer prognosis probe (§7) is likewise mixed and
underpowered (PANC metastatic-vs-resectable DiD is +0.9 pp / −6.6 pp across the two models;
BRCA TNBC arm is n≈7). Pilots are noisy and not age-adjusted, so this is not a confirmatory
refutation, but it is a strong signal that **the full run is likely to reject H1.**

Three viable paths (a decision for the study team, not something to run on autopilot):

1. **Pre-register the null / reversal as the finding, then run.** The prereg already names
   an "informative null on prognosis-modulation" as publishable-but-weaker. The pilot
   suggests something more interesting than a null: a **possible reversal** (favorable-
   prognosis BRCA elicits *more* SES stigma than grim PANC). If that holds at full n and
   survives the age adjustment, "prognosis does **not** drive the gradient: cancer-type
   *lay-stigma* or cohort composition does" is a genuine, non-incremental result. This is
   the strongest option **if** the frame is rewritten *before* the confirmatory runs to
   avoid HARKing.
2. **Reframe the axis away from prognosis** to something the pilot supports, e.g. the
   remarkable **cross-cancer stability** of the SES gradient (~52–64 pp in every
   cohort×model, race-only ≈0 everywhere), which would make Paper 2 a *generalization*
   paper ("the NSCLC dissociation is a property of the model, not the cancer") rather than
   a *modulation* paper. Lower novelty ceiling, but well-supported and low-risk.
3. **Confront the age confound head-on as the story.** BRCA is capped at age ≤56 by GENIE
   eligibility (median 44, 79% premenopausal); PANC runs 24–87 (median 65). Any BRCA/PANC
   difference is confounded with a ~20-year age gap. The prereg's §5b mandates an
   age-adjusted model **and** a PANC≤56 matched re-run. If the −9 pp Δ *flips* under age
   matching, the headline becomes "apparent prognosis effects in cross-cancer LLM audits
   are age-composition artifacts", a methods contribution in the same spirit as Paper 1's
   measurement-correction framing.

**Recommendation:** do **not** launch the four full-cohort runs (4 models × 2 cohorts ×
~1,000 cases × 30 variants) until this is settled. Instead: (B1) run the age-adjusted
interaction and the PANC≤56 matched analysis *on the pilots* as a cheap directional check;
(B2) hold a short council/reframe pass to pick path 1/2/3 and amend the prereg *before*
unblinding full data; (B3) then run. Running first and reframing after is the one move that
would compromise the pre-registration integrity the project has otherwise protected well.

### B1 result (2026-07-08): age-matching does NOT rescue H1 on the pilots

Ran `scripts/brca_panc/age_adjusted_pilot_check.py` (both pre-registered §5b controls on
the pilots). **The against-H1 direction does not flip:**

| Model | Raw Δ (PANC−BRCA) | PANC≤56 matched Δ | Age-adjusted GLM interaction |
|-------|------------------:|------------------:|------------------------------|
| gemini-2.5-flash | −9.2 pp | −1.9 pp (PANC≤56 60.0 vs BRCA 61.9) | coef +3.69, CI [−2.8, +10.2], p=0.26 |
| deepseek-chat | −9.9 pp | −10.6 pp (PANC≤56 53.3 vs BRCA 63.9) | coef −19.97, CI [±22k], p=0.99 |

Reading: matching PANC to the BRCA age window narrows gemini's gap toward zero (−9.2 →
−1.9 pp) but **does not reverse it to PANC>BRCA**, and deepseek stays firmly against H1
(−10.6 pp). **The age confound is not the explanation for the against-H1 direction.** Two
strong caveats: (i) the matched PANC subcohort is only **n=10** cases (of 50): the ceiling
falls at age 56 so almost all PANC pilot cases are excluded, so the matched read is
directional at best; (ii) the age-adjusted GLM is **quasi-separated** at pilot n (reference
stigma ≈0–4%), so its interaction estimate is uninterpretable (deepseek's CI spans
±22,000). Both problems are pilot-size artifacts and resolve at full n. Figure:
`manuscript_brca_panc/figures/pilot_exploratory/fig_pilot_age_matched_gradient.png`.

**Consequence for the decision above:** path 3 ("it's the age confound") is now the
*least* supported of the three reframes: the pilot says age doesn't carry the effect.
Paths 1 (pre-register the null/reversal) and 2 (cross-cancer *stability* of the SES
gradient) are better supported and should lead the B2 reframe discussion. Confirm on the
full cohorts (proper n for both the matched analysis and the GLM) before locking.

---

## 3. Priority C: Paper 2 measurement-validity gate (parallel to A1, same lead time)

Council requirement #4 is non-negotiable and shares the long human lead time with A1:

- The two-rater gold packet is **built** (`build_judge_packet_v2.py` was run;
  `adjudication_brca_panc/gold_{brca,panc}_rater{1,2}.csv`, 50 items/cohort, correctly
  stratified). **But the label columns are empty and rater 2 is not recruited.**
- **Action:** recruit the second rater once (they can label the NSCLC 40-item set for A1
  *and* the BRCA+PANC sheets in one sitting), then run `score_gold_v2.py`. The κ≥0.60 gate
  is per-cohort; the script surfaces PASS/FAIL but does **not** decide the response to a
  fail; pre-decide now: retrain, add a third adjudicator, or report the cohort as
  unvalidated.
- **Model-pair flag (from `STATUS.md`):** the gold pool currently sources only from
  gemini + deepseek (the two pilots that existed). If the intended anchor is the full
  4-model panel, that needs Llama/GPT-4o pilots on BRCA/PANC first and a packet rebuild.
  Decide before raters spend effort on a pool you'll discard.

---

## 4. Suggested sequence

```
Now ──┬─ A1  recruit 2nd rater  ─────────────┐  (longest lead; start today)
      ├─ C   have them label NSCLC + BRCA/PANC gold sheets in one pass
      │      (NSCLC sheets already built: gold_{random,flagged}_rater{1,2}.csv)
      │
      ├─ A2  ✔ DONE: GPT-4o folded into grid + 6-vendor figs
      ├─ A3  ✔ DONE: Claude Sonnet arm dropped (5-vendor panel)
      ├─ A4  case-clustered CIs                                 } can run in
      ├─ A5  README circularity reframe                         } parallel
      │
      ├─ B1  age-adjusted + PANC≤56 check ON THE PILOTS
      └─ B2  reframe/prereg-amend decision (paths 1/2/3)
            │
      A6  write Paper 1 manuscript  ──►  submit Paper 1 (medRxiv → JMIR AI)
            │
      B3  launch Paper 2 full runs (only after B2)  ──►  Paper 2 detector validation
            │                                              (needs C complete)
            └─►  Paper 2 analysis + manuscript
```

**One-line version:** *Ship NSCLC first: with GPT-4o already folded in and Sonnet dropped,
what's left is the 2nd rater on the (now-built) gold sheets plus the manuscript write-up. And
before spending compute on the BRCA/PANC full runs, resolve that the pilot data is pointing
against Paper 2's prognosis hypothesis: reframe the prereg around the null/reversal or the
age confound, then run.*
