# Random-60 gold-set validation (representative) — INTERIM

**Status:** INTERIM, single-rater. Computed 2026-07-15. Supersedes the archived
35-item (enriched) and 40-item single-rater sets as the *representative* result.
**Headline inter-rater kappa is NOT reportable yet** — awaits a second independent
rater on `gold_random_rater2.csv`. Do not update the manuscript kappa until then.

## Design

60 items drawn **uniformly at random** (seed 17) from the full NSCLC response pool
(gemini-2.5-flash + deepseek-chat baseline checkpoints; no stratum enrichment), so
the STIGMA base rate is a genuine prevalence estimate (contrast the enriched
targeted set). Three-label rubric STIGMA / APPROPRIATE / NEUTRAL, binarized to
STIGMA-vs-not. Rater 1 = A. Cuervo (`gold_random_rater1_alvaro.csv`, 60/60 labeled).
Judge = Sonnet-4.6 (`random_judge_labels.json`, `scripts` scratch runner, same
rubric as `run_judge.py`). Classifier = regex flags (`_classifier_stigma` in
`random_judge_items.jsonl`).

## Results (n=60)

| Comparison | % agreement | Cohen's kappa | PABAK | STIGMA counts (a vs b, both) |
|---|---|---|---|---|
| Human (Alvaro) vs Judge | 91.7% | 0.569 | 0.833 | 6 vs 7, both 4 |
| Human (Alvaro) vs Regex | 95.0% | 0.773 | 0.900 | 6 vs 9, both 6 |
| Judge vs Regex | 90.0% | 0.568 | 0.800 | 7 vs 9, both 5 |

Judge label distribution: 40 NEUTRAL / 13 APPROPRIATE / 7 STIGMA.
Human prevalence: 6/60 = 10%. Classifier prevalence: 9/60 = 15%.

## Interpretation (honest)

- **Raw agreement is uniformly high (90-95%); PABAK uniformly ~0.80-0.83.** These
  are the stable, reportable quantities.
- **The three kappas (0.57-0.77) are statistically indistinguishable at this n.**
  With only 4-9 items in the STIGMA cell (~10% prevalence), each single
  disagreement moves kappa ~0.08-0.10, so the sample cannot rank the instruments.
  Report kappa **with** PABAK and disclose the base-rate fragility.
- **Over-counting replicates but is mild on a representative sample:** classifier
  flags 9 vs human 6 (3 excess); judge 7 vs human 6. The strong 12/17 contested-case
  over-counting evidence lives in the archived targeted set, which remains available.
- **Do not over-read "judge < regex" here** (0.569 vs 0.773) — it is within noise
  and reverses the enriched-set ordering; n=60 is underpowered to establish it.

## Next step

Second independent rater labels `gold_random_rater2.csv` (no conferring), then
`python scripts/nsclc/score_random_gold_v2.py` for the reportable inter-rater kappa
(bar >= 0.60). Judge labels for that comparison already exist in
`random_judge_labels.json`.
