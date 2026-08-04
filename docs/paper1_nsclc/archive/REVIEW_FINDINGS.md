# EquityGUIDE — Adversarial Review Findings & Remediation Record

Compiled from a 4-agent adversarial review panel (hostile peer reviewer,
biostatistician, thoracic oncologist, novelty skeptic), each grounded in the
actual code/data. This is the manuscript-correction checklist. Status legend:

- ✅ FIXED (code/analysis change made, runs on existing data)
- 🔧 CODE-READY (fix implemented in code; needs a re-analysis/re-derivation pass)
- 🔁 NEEDS RE-RUN (requires new model calls — credits)
- 🗂 NEEDS DATA (requires re-extracting from raw GENIE or new corpus)
- 👥 NEEDS HUMAN (requires clinician / two-rater adjudication)

---

## THE HEADLINE CORRECTION (this changes the paper)

**Two claims I (and the prior narrative) overstated, now corrected on real data
(`correct_analysis.py`, grid-wide BH across 58 directional tests):**

**(1) "Decision-stable" was too strong, but "large decision bias" would be too — it's
a SMALL, SES-keyed downgrade.** After proper grid-wide BH, only 2/58 directional
tests survive — both DeepSeek SES variants, modest effect:

| Variant (DeepSeek) | down / up | sign-p | grid-BH q | tier-rank d |
|---|---|---|---|---|
| underinsured_only | 94 / 48 | 0.0001 | **0.008** | −0.065 |
| latina_female_uninsured | 91 / 52 | 0.0014 | **0.041** | −0.032 |

The biostatistician's uncorrected hits (uninsured p=.014, medicaid .017, elderly
.007) mostly do NOT survive correction. **TOST equivalence:** DeepSeek 27/29 variants
equivalent (within d=±0.10); **Gemini only 14/29 — for 15 variants you cannot even
establish equivalence**, so the Gemini "no decision bias" is a genuine
failure-to-reject, not a demonstrated null. → Report: *small but significant SES
downgrade in DeepSeek; inconclusive/underpowered for Gemini; NOT "decision-stable."*

**(2) The "huge soft bias (d>1)" is MOSTLY appropriate SDOH care, not bias.** Split
into stigmatizing-regardless vs appropriate-given-context (sign test, BH within
group):

| Variant | APPROPRIATE net% (cost/financial — NCCN-endorsed) | STIGMATIZING net% (adherence-doubt, hallucinated SDOH, de-escalation — the real bias) |
|---|---|---|
| uninsured_only (DS) | **+84.5%** | +3.7% |
| underinsured_only (DS) | **+86.0%** | +9.8% |
| low_income (DS) | **+73.0%** | +7.9% |
| **unhoused (DS)** | +74.5% | **+78.9%** ← cleanest real bias |
| black_race_only (DS) | −1.8% ns | +0.6% ns |
| white_male_private (DS) | −1.9% ns | −0.6% ns |

➡️ The +90% "soft bias" headline was largely **appropriate** (cost discussion for an
explicitly-uninsured patient). The defensible BIAS signal is the smaller
**stigmatizing** component — and it is **huge and clean for unhoused patients**
(+71–79%: hallucinated barriers, adherence doubt, watchful-waiting), scales with
disadvantage, and is **~0 for race-only and white-male** (the control holds).

**New, defensible thesis:** *LLMs apply (mostly appropriate) SES-responsive framing,
but layer genuinely stigmatizing assumptions onto the most disadvantaged (esp.
unhoused) patients, plus a small treatment-downgrade signal for low-SES patients —
while leaving the recommendation largely intact for race alone.*

---

## FATAL findings

### F1. "Real GENIE clinical notes" is a misrepresentation — notes are LLM-generated 🗂
`src/generate/note_generator.py` uses **gemini-2.5-flash** to write the free-text
notes from GENIE *structured* fields. So (a) the notes are **synthetic**, and (b)
the note author (gemini-2.5-flash) is also a **headline audited model** → partial
circularity. The repo code is honest ("LLM-generated"); the manuscript framing must
match.
- **Action ✅:** never call these "real notes" — use **"synthetic GENIE-derived
  notes."** (Repo comments already correct.)
- **Action 🗂/🔁:** for a strong claim, (i) regenerate notes with a generator
  **disjoint** from every audited model, and/or (ii) validate on a real
  de-identified corpus (e.g., MIMIC-style). Until then, drop Gemini's *self-authored*
  arm from primary comparison or caveat it explicitly.

### F2. The "decision-stable" null — see HEADLINE CORRECTION above ✅
Directional tests implemented in `correct_analysis.py` (sign test + signed tier-rank
Cohen's d with grid-wide BH). The null is replaced by a directional result.

### F3. Soft-bias confounds bias with appropriate SDOH care; reference is rigged ✅/👥
`no_demographics` is *stripped* of SES context, so "uninsured" vs "no financial
context" guarantees a cost-language delta — and discussing copay assistance for an
uninsured patient is **NCCN-endorsed care, not bias.**
- **Action ✅:** detectors split (`correct_analysis.py`) into
  **stigmatizing-regardless** (`adherence_compliance`, `prognosis_framing`,
  `sdoh_generation`, `watchful_waiting` — the defensible bias signal) vs
  **appropriate-given-context** (`financial_barrier`, `social_work`,
  `specialist_referral`, `clinical_trial`). Report the stigmatizing group + the
  **race-only ≈ 0 contrast** as the bias finding.
- **Action 👥:** blinded clinician rating of a sample for "warranted vs gratuitous"
  SDOH framing to validate the regex split.

---

## MAJOR findings

### M1. NCCN scorer is too permissive → the concordance null is partly tautological 🔧/🗂
ECOG hardcoded to 1 (poor-PS branches are dead code); PD-L1 ignored for ~64%;
Stage IV accepts chemo-IO + IO-mono + "test first" simultaneously (498/594 ambiguous).
- **🗂 ECOG — RESOLVED as not-fixable (2026-06-29):** the `ecog_ps='1'` constant is
  **not a careless default — it is the only value the public data permits.** An
  exhaustive search of all 11 raw GENIE BPC NSCLC v2.0 public CSVs
  (`cancer_level_dataset_index/non_index`, `med_onc_note_level_dataset`,
  `imaging_level_dataset`, `patient_level_dataset`, etc.) found **zero ECOG / KPS /
  performance-status columns** (only `image_inst_perf`, imaging-institution metadata).
  Real per-case PS lives in the **restricted PRISSMM phenomic layer**, which is not in
  the public release. Re-extraction is therefore **blocked by the data, not the code.**
  → Gap closed-by-impossibility. **Adopt the permanent caveat below; demote the
  decision-concordance arm to secondary/supporting.** Obtaining real ECOG requires a
  separate Sage Bionetworks restricted-access application (months; a future paper).

  **MANUSCRIPT CAVEAT (paste into Methods + Limitations verbatim):**
  > ECOG performance status is not available in the public GENIE BPC NSCLC v2.0
  > release and is fixed at 1 for all 1,048 cases. The poor-performance-status
  > treatment pathway (de-escalation to single-agent therapy or best supportive
  > care) is therefore untested, and performance-status–mediated decision bias —
  > the most plausible route by which demographics (age, housing, frailty
  > assumptions) would alter a treatment *decision* in NSCLC — cannot be excluded.
  > We treat this as the leading residual confound, report the decision-concordance
  > result as secondary/supporting rather than as a demonstrated null, and frame the
  > study primarily as an audit of treatment *framing* rather than treatment
  > *selection*.
- **🔧 PD-L1:** real values exist (`pdl1_final`: 377 high/intermediate/low). Scorer
  can use them to tighten the Stage IV acceptable set. Implement + re-derive
  concordance.
- **🔧 Report concordance on UNIQUE-answer cases only** (exclude the ≥3-tier ambiguous
  Stage-IV set) as a sensitivity analysis.

### M2. NCCN scorer clinical gaps ✅/🔧
- ✅ **Atypical EGFR** (`other_sensitising`, 19 cases) now scored as TKI-sensitising
  (`_is_egfr_sensitising` fixed; `exon_20_ins` correctly excluded).
- 🔧 **STK11/KEAP1** (91/27 mutated): add IO-resistance flag (does not change
  first-line primary answer but should be noted).
- 🔧 **KRAS G12C** (120): correctly falls through to first-line chemo-IO (G12C
  inhibitors are subsequent-line) — verified not a first-line error; add as a note.
- 🔧 **Stage III default to "unresectable"** removes the surgical fork for 251 cases;
  flag resectable-IIIA explicitly or report Stage III separately.

### M3. Statistics hygiene ✅
- ✅ **Directional / signed tests** added (F2).
- ✅ **TOST equivalence** (`correct_analysis.py`, margin d=±0.10): "no decision bias"
  is only claimable where the tier-shift d CI ⊂ (−0.10, +0.10); otherwise it is a
  failure-to-reject. MDEs: flip ±~3pp, tier-rank d≈0.09.
- ✅ **Grid-wide BH-FDR** across the variant×model family (not the smallest
  per-metric family).
- ✅ **Soft-bias significance** added (paired sign test + n_nonzero) — the old soft
  table had no test.
- 🔧 **Omnibus chi-square** (`chi_square_flip_homogeneity`) exists in `stats.py` but
  was never called — wire it into the analyzer or stop claiming an omnibus result.
- 🔧 **BH-correct the 6 McNemar isolation pairs.**

### M4. Ecological validity — the bracketed `[PATIENT DEMOGRAPHICS:…]` header 🔁
A conspicuous prepended banner is a salience artifact that likely inflates the
framing signal vs. demographics embedded naturally in the HPI.
- **Action 🔁:** add an arm that embeds demographics naturally into the note prose
  and re-measure; report whether the soft-bias effect survives.

### M5. Circular detector / rank calibration ✅/🔁
`TREATMENT_RANK`, adjacency map, and soft-bias regexes were calibrated on the pilot
cohort then applied to inference.
- ✅ **Rank-permutation sensitivity** on the direction tests (add to
  `correct_analysis.py`).
- 🔁 Re-derive detectors/ranks on a held-out split.

### M6. Cross-model generalization is premature 🔁
"Similar across closed and open" currently rests on Gemini (the note author) +
DeepSeek + partial Llama (n=719). Complete Llama and add GPT-4o + Claude Sonnet 4.6
(matched temp 0) before any closed-vs-open claim.

---

## MINOR findings ✅
- ✅ Report `n_nonzero` alongside Cohen's d for soft-intensity (ties inflate d).
- ✅ Parser verified **non-differential** (unknown rate 2.1–3.6% across variants) —
  does not manufacture the null. (One worry formally cleared.)
- 🔧 Parser ordering brittleness (`surgical_resection` negative-lookahead) — audit
  against the human sample.

---

## NEEDS HUMAN / NEEDS RUN (cannot be done in code on existing data)

| Item | Why | Type |
|---|---|---|
| **Test–retest** (re-run reference k≥3 at temp 0) | substantiate/replace the "instability floor"; estimate noise vs signal | ✅ DONE 2026-06-29: self-flip Gemini 3.4%, DeepSeek 9.4% (`results/baseline/retest_*.json`) |
| **Natural-embedding arm** | M4 ecological validity | 🔁 full re-run |
| **Disjoint note generator / real corpus** | F1 circularity | 🗂 + 🔁 |
| **Real per-case ECOG** | M1 | ❌ NOT in public GENIE BPC v2.0 (see M1); needs restricted PRISSMM access → caveat adopted, decision arm demoted to secondary |
| **Clinician adjudication of soft-bias & parser** | F3, MINOR | 👥 |
| **Complete Llama + add GPT-4o + Sonnet 4.6** | M6 | 🔁 credits |

---

## The defensible core (what survives the panel)
1. The **SES-keyed framing effect is statistically robust** (d≈0.95–1.43, q≈1e-148).
2. The **race-only ≈ 0 vs SES contrast** — clean, same detector, no signal on race.
3. The **NEW directional finding** — net treatment downgrades for low-SES/elderly.
4. The **genomics-conditioned angle** (framing bias persisting even with actionable
   molecular drivers) — the one question Omar/Zack/the trial-screening preprint don't
   test; the paper's best novelty anchor.
