# EquityGUIDE — Pre-Registration / Analysis Plan

**Status:** locked before GPT-4o and Claude arms are run (Gemini, DeepSeek complete;
Llama in progress). Purpose: fix the confirmatory analysis so the remaining model
arms cannot be reverse-engineered into the hypotheses. Exploratory analyses are
permitted but will be labelled as such.

Author: Alvaro Cuervo · Date locked: 2026-06-29

> **Deviations from pre-registration (addendum, 2026-07-10 — does not alter locked hypotheses):**
> The locked plan named a 5-model audit panel including a `claude-sonnet-4-6` audit arm. As
> executed, the confirmatory panel is **6 vendors, all at n=1,048** — gemini-2.5-flash,
> deepseek-chat, llama-3.3-70B, **llama-3.1-8B**, gpt-4o, **gpt-4o-mini**. The **claude-sonnet-4-6
> audit arm was dropped** (only a 25-case stub was run; 2026-07-09 decision). This is a lineup
> change, not a hypothesis change. **claude-sonnet-4-6 remains the blinded LLM-judge** for
> stigma-classifier validation (§ judge below), unaffected. GPT-4o, listed as pending at lock
> time, was completed to the full 1,048 (2026-07-08). All deviations are disclosed here rather
> than edited into the locked text above.

**Target venue:** medRxiv preprint (primary, near-term citable artifact) → journal
submission to **JMIR AI** (primary) or **BMC Medical Informatics & Decision Making**
(backup); PLOS Digital Health / PLOS ONE as fallbacks. Optional health-AI workshop
(ML4H / trustworthy-ML). Top medical venues are out of scope given synthetic notes,
single-annotator validation, and moderate inter-rater κ — all disclosed.

---

## 1. Study question

Do LLMs alter (a) their guideline-concordant treatment recommendation, or (b) the
rhetorical/clinical *framing* of their response, when a demographics-neutral NSCLC
note is annotated with a demographic label — holding all clinical facts constant?

## 2. Design

- **Cases:** 1,048 GENIE BPC NSCLC profiles. Demographics-neutral base notes; 30
  label-only demographic variants injected at runtime (`variant_injector_v2`).
- **Reference variant:** `white_male_private`. Neutral anchor: `no_demographics`.
- **Models (audit panel):** gemini-2.5-flash, deepseek-chat,
  meta-llama/Llama-3.3-70B-Instruct-Turbo, gpt-4o, claude-sonnet-4-6.
- **Sampling:** single pass, temperature 0.0 (matched across models).
- **Ground truth:** deterministic GENIE→NCCN mapping
  (`genie_nsclc_notes_groundtruth.csv`); not re-annotated per case.

## 3. Primary outcomes (confirmatory)

1. **Concordance (decision stability):** does the recommendation match the NCCN
   acceptable-answer set? Outcome = adherence score per (case × variant × model).
2. **Stigmatizing soft-bias:** automated rubric count of stigmatizing elements
   (adherence-doubt, hallucinated SDOH, unprompted de-escalation). This is the
   defensible bias signal — distinct from appropriate SES-responsive framing
   (e.g., cost discussion for an uninsured patient), which is NOT counted as bias.

## 4. Confirmatory hypotheses

- **H1 (recommendation stability):** for race-only and `white_male_private`
  control variants, concordance is statistically equivalent to `no_demographics`
  (TOST equivalence, margin pre-set below).
- **H2 (stigma gradient):** stigmatizing soft-bias is elevated for the most
  disadvantaged variants (esp. `unhoused_patient`, `black_unhoused`,
  `low_income_patient`) vs. reference, and scales with disadvantage.
- **H3 (control holds):** stigmatizing soft-bias for race-only variants and
  `white_male_private` is ≈ 0 (not distinguishable from `no_demographics`).
- **H4 (cross-model convergence):** the H2 direction replicates across ≥3 of the
  5 models (sign agreement), reported per-model — never pooled across vendors.

## 5. Statistical plan

- **Effect sizes + CIs:** report Cohen's *d* with 95% CIs for every variant-vs-
  reference contrast. Do **not** report point estimates without CIs.
- **Multiplicity:** Benjamini–Hochberg FDR across the full
  (29 variants × outcome) grid, **per model**. Report q-values as primary,
  unadjusted p as secondary.
- **Equivalence (H1/H3):** two one-sided tests (TOST), equivalence margin
  d = ±0.10 (pre-registered; ~quarter of the smallest effect of interest).
- **Clinical anchoring:** benchmark the SES treatment-downgrade effect
  (observed d ≈ −0.03..−0.07 in DeepSeek) against NCCN intra-rater / acceptable-
  answer-set width, and state explicitly whether it is clinically meaningful.
- **Disaggregation:** all results reported per model; convergence (sign agreement)
  is the headline robustness claim, not a blended average.

## 6. Circularity control (confirmatory robustness)

Base notes in the main cohort are Gemini-generated, and Gemini is in the audit
panel. Two pre-specified checks:

- **C1 — self-favoring (already observed, retained):** Gemini scores its own notes
  *lower* than DeepSeek does (NCCN concordance 2.32 vs 2.58 on identical notes),
  i.e., no self-upgrading. Reported as evidence against the dominant circularity
  mechanism.
- **C2 — generator-invariance (deterministic templates):** re-run the pipeline on
  notes rendered deterministically from the same GENIE structured fields
  (`genie_bpc_nsclc_templates100`, no LLM in the loop). **Pre-registered
  prediction:** H2/H3 replicate (stigma elevated for unhoused, ≈0 for controls).
  If the signal survives notes whose every fact is code-traceable, it cannot be a
  generator artifact. Run on ≥2 panel models (deepseek-chat + one other).

## 6b. Stigma-classifier validation (confirmatory measurement validity)

The primary stigma outcome is produced by a regex classifier
(`src/analyze/soft_bias.py`). To validate it as an instrument without recruiting
human raters:

- **Composite (pre-registered):** "stigma present" = `adherence_compliance` OR
  `sdoh_generation` (adherence-doubt OR hallucinated SDOH). `treatment_hedging`
  and `watchful_waiting` are **excluded** — hedging fires on ~70% of responses in
  *all* strata (including white-male/race-only controls), i.e. it indexes ordinary
  clinical caution, not bias. The two-dim composite gives control 0% / race-only
  3% / disadvantaged 67% on a 180-item stratified sample.
- **LLM-judge:** Claude Sonnet 4.6, blinded (sees only the response text, not the
  variant or the classifier verdict), labels each item STIGMA / APPROPRIATE /
  NEUTRAL against a fixed rubric (`run_judge.py`). Stratified sample of 180 real
  responses (60 disadvantaged / 60 race-only / 60 control), drawn from the
  completed Gemini + DeepSeek arms (`build_judge_packet.py`).
- **Human anchor:** the analyst hand-labels a blinded 40-item gold subset; the
  judge is licensed only if judge-vs-gold agreement is high.
- **Reported:** judge-vs-classifier agreement + Cohen's κ on "stigma present", and
  judge-vs-gold agreement. **Pre-registered prediction:** judge confirms the
  classifier (κ substantial) and reproduces the disadvantaged≫control gradient.
- **Caveat (disclosed):** an LLM judging LLM output carries mild circularity; the
  judge is a non-panel model only for stigma *labeling* (not generation), anchored
  to a human gold set.

## 7. Exploratory (labelled non-confirmatory)

- **Real-note cross-validation (PMC open-access NSCLC case reports — primary):**
  fetch ~30-50 real, human-written NSCLC case reports from the PubMed Central OA subset,
  extract the case-presentation narrative, neutralize/strip demographics, inject the same
  30 demographic variants, and re-run the stigma detector. Confirms the disadvantaged>control
  gradient replicates on genuine, on-domain clinical prose — the feasible substitute for
  "validate on real notes" (GENIE BPC releases no source notes; §8). The demographic
  contrast is WITHIN-case (variant vs. reference on the same note), so case-report
  selection bias affects clinical-mix generalizability only, not the demographic effect;
  disclosed as such. MTSamples = optional domain-general supplement; MIMIC-IV = stronger
  but credentialing-gated follow-up. (Council pick, 2026-06-30.)
- Held-out non-panel LLM generator (e.g., Qwen-72B) as a second invariance check.
- V3 mitigation arm (fairness / structured-extraction / guideline-grounded
  prompting). Reported as exploratory directions, not solutions.
- Per-variant qualitative audit of recommendation flips (true disagreement vs
  parser noise).

## 8. Known limitations (disclosed)

- Notes are synthetic vignettes derived from a curated registry; this is a bias-
  *measurement* study, not a clinical-validity study. Template notes (C2) read
  less naturally than real clinical notes by construction — a generalizability,
  not a correctness, limitation.
- **GENIE BPC releases no source free-text notes** — PRISSMM curation abstracts
  structured variables out of the EHR, and the original documents are withheld for
  PHI. We therefore synthesized notes from the structured fields; there was no
  real-note alternative for this cohort. Real-prose generalizability is addressed by
  the MTSamples cross-validation (§7), not by GENIE notes.
- **Demographic injection is an explicit prepended tag**, not naturally embedded
  prose; this risks measuring label-following rather than presentation-mediated bias.
  Partially mitigated by the natural-embedding A/B subset (if run) and the MTSamples
  real-note check; disclosed as a measurement-design limitation.
- **Single annotator** for stigma-classifier validation; inter-rater reliability
  beyond the human–LLM-judge comparison is unestablished. A second blinded human rater
  (Krippendorff's α) is the planned upgrade / future work.
- NCCN labels are rule-derived; an optional single oncologist review of the
  *mapping rule* (O(1), not per-case) would strengthen but is not required for the
  confirmatory analysis.
- The stigma classifier is validated by an LLM judge anchored to a 40-item human
  gold set (§6b), not by a full human-rater study; this is a deliberate scope
  choice for the preprint/workshop tier, disclosed as such.

## 9. Run commands (reference)

```
# circularity control arm
python generate_template_notes.py --n 100
python run_experiment_v2.py --subset genie_bpc_nsclc_templates100 --model deepseek-chat --temperature 0.0 --max-workers 8
python analyze_results_v2.py --subset genie_bpc_nsclc_templates100 --model deepseek-chat --concordance --save

# stigma-classifier validation (Sonnet judge; ~$0.40 of Anthropic credit)
python build_judge_packet.py --per-group 30 --gold 40
#   -> hand-label adjudication/gold_template.csv (STIGMA/APPROPRIATE/NEUTRAL)
python run_judge.py                # batch judge + agreement/kappa vs classifier and gold

# credited panel arms via Batch API (~50% cost) when credits land
python run_experiment_v2_batch.py --subset genie_bpc_nsclc --model gpt-4o --submit-only
python run_experiment_v2_batch.py --subset genie_bpc_nsclc --model gpt-4o --collect
```
