# EquityGUIDE — Paper Frame (COMMITTED 2026-07-01)

This is the canonical framing the manuscript is committed to. Every section, figure,
and claim serves the **dissociation thesis** below. When a result doesn't advance the
dissociation, it goes to supplementary or a table — not the main narrative.

Decided via 4-member "Claude council" review (venue/framing, rigor, clinical,
novelty). All four independently converged on this reframe.

---

## Working title
**"Stigma without downgrade: separating warranted socioeconomic responsiveness from
generated stigma in LLM cancer-treatment recommendations."**

(Mechanism-title, not "Auditing demographic bias in…" — the latter is audit #92 and
gets zero novelty credit; a systematic review reports 91.7% of bias audits "find bias.")

## One-sentence thesis
LLMs barely discriminate by **race** on the NSCLC treatment *decision*; they
**stigmatize the socioeconomically disadvantaged** through unprompted *framing* —
adherence-doubt and hallucinated social-determinant problems — that **scales with
disadvantage**, is **~0 for race-only and a white-male control**, and **replicates on
LLM-free deterministic-template notes** across vendors.

## The two stacked reframes (both are ours alone)
1. **Framing bias vs. decision bias** — the bias hides in *narration*, not the
   recommendation. Generic audits that only score the final answer miss it. This is a
   *measurement* point about how to audit clinical LLMs.
2. **Appropriate-SDOH-care vs. stigma decomposition** — the naive "+~90% soft bias" is
   *mostly warranted care* (offering financial counseling, social work); the real bias
   is a smaller, separable stigma layer. We are the first to partition SES-responsiveness
   into appropriate-vs-stigmatizing and show they dissociate. **This is a measurement
   correction other researchers can cite to reanalyze their own audit results** — the
   contribution that earns citations.

## What to LEAD with vs. what is table stakes
- **Lead:** the decomposition; the race≈0 / SES-large **dissociation**; the
  **gradient** (controls ~0 → monotone with disadvantage) — NOT the contested absolute
  stigma rate. The direction is method-robust; the point estimate is disputable.
- **Table stakes (do not lead — hygiene reviewers expect):** multi-vendor replication,
  LLM-as-judge, BH-FDR, dose-response as a stat.

## Deployment-harm hook (opening)
Anchor the harm to live deployments: ambient scribes (Nuance DAX, Abridge) and
Epic + GPT-4o inbox-reply drafts already write into oncology charts at scale. The
concrete harm is not a wrong regimen — it is a deployed system silently inserting
"patient may have difficulty adhering" or fabricated housing instability into the
*permanent record* of the poorest patients, propagating downstream as documented fact.
Frame = documentation-integrity + medico-legal harm, not "biased vibes."

## Position against prior work
- **Omar et al. (ED vignettes):** cite as *converging on SES/housing, not race* — their
  intersectional urgency effects are largely SES-driven too.
- **SES clinical-trial-screening preprint:** reports SES "soft" effects as monolithic
  harm; we show that signal is mostly appropriate care once decomposed.
- **"Artificial Intolerance" (stigma inherited from input language):** we differ —
  the LLM *generates* stigma **unprompted from a bare demographic label**. State this
  contrast explicitly or be called derivative.

## Narrative spine (sections serve the dissociation)
1. Intro: deployment hook → generic audits miss framing bias → we decompose and dissociate.
2. Methods: deterministic GENIE→NCCN ground truth; 30 variants + controls; judge-
   adjudicated stigma (validated); C2 LLM-free template control. (These are the *rigor
   moat* that makes the dissociation trustworthy where opinion/LLM-judge-only audits aren't.)
3. Results in dissociation order (see figures).
4. Mitigation (if elevated): fairness/structured-extraction prompts remove stigma while
   preserving appropriate care; guideline-grounding *amplifies* it (quotable warning).
5. Discussion: framing is the real-world harm surface; audit-methodology implication.

## Figure order (committed — serves the spine)
- **F1 Task competence & decision stability** — models competent (concordance), decision
  barely moves (Δ≈±1pp, TOST-equivalent) → *bias isn't incompetence, and isn't in the decision.*
- **F2 Soft-bias split (money figure)** — stigmatizing vs appropriate net% by variant →
  *most of the "bias" is warranted care; a smaller real stigma layer separates out.*
- **F3 Stigma gradient** — control ~0 → race-only ~0 → SES/housing large, monotone →
  *targets disadvantage specifically, not race.*
- **F4 Robustness (2 panels)** — (a) across vendors; (b) on LLM-free template notes (C2)
  → *not one model, not a note artifact.*
- **F5 (optional/supp) Decision-direction** — signed tier shift + TOST; the real SES
  downgrade (deepseek::underinsured, q=0.012) as the one decision-level effect.
- Supp: judge validation; test-retest noise floor; per-variant flip rates.

## Numbers to carry EXACTLY (corrections locked)
- Judge validation on the 60-item random gold set: judge–human 91.7% (κ=0.57, PABAK
  0.83), regex–human 95.0% (κ=0.77, PABAK 0.90), tree–human 93.3% (κ=0.68, PABAK 0.87).
  Reported stigma rates use the raw regex composite, not judge labels.
- Notes are **synthetic GENIE-derived / deterministic-template** — NEVER call them
  "real notes." Robustness = template control + multi-vendor, NOT real-world prose.
- Arms: **6 vendors, all at n=1,048** — gemini-2.5-flash, deepseek-chat, llama-3.3-70B,
  llama-3.1-8B, gpt-4o, gpt-4o-mini. (GPT-4o was completed from the earlier n=209 partial to
  the full 1,048 as of 2026-07-08 and folded into the panel CSV + 6-vendor figures; the old
  "n=209" disclosure is superseded.) Claude Sonnet audit arm dropped (25-case stub);
  claude-sonnet-4-6 remains the blinded LLM-judge only.
- SES downgrade: **deepseek::underinsured_only** survives grid-wide BH-FDR (q=0.012),
  the ONLY variant that does once the full model×variant family is corrected.

## Open must-fixes this frame depends on (from rigor council member)
- **2nd blinded rater** on the 60-item random gold set → inter-human agreement (closes
  the single-rater status). Highest credibility-per-hour fix.
- Classifier **confusion matrix** vs gold; judge = primary, regex = disclosed upper bound.
- **Natural-embedding A/B** (~100–150 cases) to close the salience-artifact attack (M4).
- Llama **test-retest noise floor** (running).
