# EquityGUIDE — Full Study Run Plan & Cost Sheet

> **STATUS 2026-07-15:** All runs complete — 6-vendor confirmatory panel at n=1,048 (see
> lineup below). Analysis, figures, and a full manuscript draft
> (`docs/paper1_nsclc/manuscript_nsclc.md`) are done and validated
> (`adjudication/VALIDATION_REPORT.md`). This run-plan is now a historical/cost record;
> remaining work is editorial — see `adjudication/SUBMISSION_READINESS.md`.

Rigorous multi-model demographic-bias audit on GENIE BPC NSCLC (1,048 cases ×
30 demographic variants = 31,440 calls per model), matched conditions:
**temperature 0, single pass, identical prompts, n = 1,048.**

Reference variant for flip/soft-bias calculation: `no_demographics`.

---

## Model lineup

**Confirmatory panel (as of 2026-07-10): 6 vendors, all complete at n=1,048.**

| Arm | Type / lab | Run model ID | Conditions | Status |
|-----|------------|--------------|------------|--------|
| Gemini 2.5 Flash | closed · Google | `gemini-2.5-flash` | temp 0 | ✅ complete (1,048) |
| DeepSeek-chat (V3) | open · DeepSeek | `deepseek-chat` | temp 0 | ✅ complete (1,048) |
| Llama-3.3-70B | open · Meta (API) | `meta-llama/Llama-3.3-70B-Instruct-Turbo` (Together) | temp 0 | ✅ complete (1,048) |
| Llama-3.1-8B | open · Meta (API) | `openrouter/meta-llama/llama-3.1-8b-instruct` | temp 0 | ✅ complete (1,048) |
| GPT-4o | closed · OpenAI | `gpt-4o` | temp 0 | ✅ complete (1,048) |
| GPT-4o-mini | closed · OpenAI | `gpt-4o-mini` | temp 0 | ✅ complete (1,048) |
| ~~Claude Sonnet 4.6 (audit arm)~~ | closed · Anthropic | `claude-sonnet-4-6` | temp 0 | ❌ **DROPPED** (2026-07-09) — only a 25-case stub was run; removed from the audit lineup |
| Med42-8B (optional) | open · medical FT, **local** | `ollama/med42-8b` | temp 0, on-prem | ☐ pilot-gated (not in confirmatory panel) |

> **Claude Sonnet — two distinct roles, do not conflate.** The Sonnet *audit arm* above is
> dropped. **claude-sonnet-4-6 remains the blinded LLM-judge** for stigma-classifier validation
> (a separate role; see PREREGISTRATION §judge and METHODS). Dropping the audit arm does not
> touch the judge.

**Why Sonnet 4.6, not Opus 4.8 (historical note — audit arm now dropped):** Opus 4.7/4.8 reject
the `temperature` param (400), so they could not run the matched temp-0 regime. This rationale
applied when a Sonnet audit arm was planned; it is retained for the record and still governs the
choice of claude-sonnet-4-6 as the temp-0 judge.

**Why Med42-8B for the local arm:** a *medical* fine-tune earns its place by
answering a question the general models can't — *does clinical fine-tuning
reduce or amplify the SES soft-bias?* — AND it doubles as the on-prem /
PHI-safe deployability arm. 70B can't run locally on 24 GB; the local arm is
necessarily a small (8B) model. **Pilot on pilot50 first** — if parse-failure
> ~20%, report Med42 for the soft-bias (text) analysis only, or drop it.

---

## Cost sheet (full 1,048 × 30, measured ~22.2M input + 18.5M output tokens)

Batch API gives 50% off (offline study — no latency need). Build the batch
path before the credited runs.

| Arm | Synchronous (full price) | **Batch (−50%)** |
|-----|--------------------------|------------------|
| GPT-4o | ~$240 | **~$120** |
| GPT-4o-mini (value alt) | ~$14 | ~$7 |
| Claude Sonnet 4.6 | ~$344 | **~$172** |
| Claude Haiku 4.5 (value alt) | ~$115 | ~$57 |
| Llama-3.3-70B finish (809 left, Together) | ~$30 | n/a |
| Med42-8B local | **$0** (compute only) | — |

**Lab-credit ask:**
- Premium (frontier closed arms): **~$320** = GPT-4o batch (~$120) + Sonnet 4.6
  batch (~$172) + Llama finish (~$30).
- Value (mini/haiku tiers): **~$95** = 4o-mini batch (~$7) + Haiku batch (~$57)
  + Llama finish (~$30).

Recommend the premium tier for the headline table (frontier models are more
defensible given the "more-capable = more-sensitive" pilot finding); the value
tier is a fallback if credit is tight.

---

## Commands (each arm is one command once credits land)

```bash
# Llama — finish to 1,048 (Together, resumes from 239; drops credit-walled cases)
caffeinate -i ./venv/bin/python scripts/nsclc/run_experiment_v2.py \
    --subset genie_bpc_nsclc --model "meta-llama/Llama-3.3-70B-Instruct-Turbo" --max-workers 8

# GPT-4o
caffeinate -i ./venv/bin/python scripts/nsclc/run_experiment_v2.py \
    --subset genie_bpc_nsclc --model gpt-4o --max-workers 8

# Claude Sonnet 4.6
caffeinate -i ./venv/bin/python scripts/nsclc/run_experiment_v2.py \
    --subset genie_bpc_nsclc --model claude-sonnet-4-6 --max-workers 8

# Med42-8B (local) — pilot first, then full
ollama serve &                      # start local server
./venv/bin/python scripts/nsclc/run_experiment_v2.py \
    --subset genie_bpc_nsclc_pilot50 --model ollama/med42-8b --max-workers 1   # PILOT
./venv/bin/python scripts/nsclc/run_experiment_v2.py \
    --subset genie_bpc_nsclc --model ollama/med42-8b --max-workers 1            # FULL
```

Each writes its own checkpoint (`v2_genie_bpc_nsclc_<model>_checkpoint.json`)
and resumes automatically; analyze with
`analyze_results_v2.py --subset genie_bpc_nsclc_<model> --save`.

---

## Operational notes (lessons from the runs so far)

- **Keep the machine awake.** `caffeinate -i` does NOT stop a lid-close sleep —
  a sleep kills sockets and freezes the run until manually restarted. Keep the
  lid open, or use clamshell mode (power + external display) for unattended runs.
- **Provider reliability:** Together's direct API is reliable; OpenRouter's
  shared free-credit pool rate-limits/hangs under sustained 31k-call load — use
  a direct provider key (BYOK) or Together for Llama.
- **Wrappers all have a request timeout + own retry loop** so a stuck upstream
  fails fast instead of hanging a worker.
- **Batch path: TODO** — build & test `messages.batches` (Claude) and OpenAI
  batch when credits land, to realize the 50% discount above.

---

## Analysis plan (lock before running — avoids p-hacking)

Per model, all vs the `no_demographics` reference:
1. **Flip rate** + Wilson CIs (expect a flat ~12–19% deterministic-instability
   floor with no demographic signal).
2. **McNemar isolation tests** (race-vs-insurance, Medicaid-vs-private, etc.).
3. **Flip direction** (downgrade/upgrade among flips).
4. **Continuous treatment-tier rank** + NCCN concordance, BH-FDR corrected
   (expect the hard-decision null).
5. **Soft-bias disadvantage-framing** (cost / financial-deflection / social-work
   / adherence) + continuous framing-intensity score, BH-FDR, with effect sizes
   and CIs (the primary positive finding: large SES-keyed effect, race-only ≈ 0).

Cross-model: matched table of the above; closed-vs-open soft-bias magnitude
gradient. Strengthening: sign-tests/CIs on soft-bias deltas; small human audit
of flips (true disagreement vs parser noise).
