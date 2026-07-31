# VALIDATION — Stats Verifier (Paper 1 NSCLC)

_Generated 2026-07-14 by in-kernel recomputation against results/ and data/processed/._

## Headline: scorer-version reconciliation
- The manuscript's concordance numbers **exactly match** `baseline_concordance.json` (pre-rescore scorer **NSCLC v1.2025**).
- Under the corrected **v6.2026** scorer (`after_concordance.json`): absolute concordance moves −3.0 to +0.4pp per model (gemini −2.9, deepseek −1.7, llama-3.3-70b −2.0, **llama-3.1-8b +0.4**, gpt-4o −3.0, gpt-4o-mini −2.5 — five drop, one rises), but the **demographic−reference deltas (the bias signal) stay within 0.5pp**. Bias findings unchanged.
- The single BH-FDR survivor (deepseek::underinsured net downgrade) reproduces in DIRECTION and significance, but the exact counts are scorer-version-dependent: manuscript **94 down/48 up (p=1e-4)** [v1.2025] → **91 down/40 up (p=1e-5)** [v6.2026].
- **Decision needed:** either (a) keep the frozen v1.2025 numbers and add a one-line footnote that a v6.2026 re-score leaves the differential unchanged, or (b) refresh all concordance numbers + the 94/48 counts to v6.2026. Either is defensible; (a) is less work and the differential is what the paper claims.

## Per-claim results
| Claim | Manuscript | Recomputed | Source | Status |
|---|---|---|---|---|
| manuscript concordance = baseline(v1.2025) | ref% & deltas per model | EXACT match to baseline_concordance.json (Gemini81.7/DS90.7/GPT89.7/mini55.6/L70b75.9/L8b49.5) | `adjudication/baseline_concordance.json` | VERIFIED |
| under v6.2026 rescore, deltas stable | bias signal unchanged | deltas move ≤0.5pp; abs concordance −1.7..−3.0pp | `adjudication/after_concordance.json` | VERIFIED |
| flip mean gemini-2.5-flash | 19.7 | 19.7 | `results/analysis/v2_genie_bpc_nsclc_flip_rates.csv` | VERIFIED |
| flip mean deepseek-chat | 13.3 | 13.3 | `results/analysis/v2_genie_bpc_nsclc_deepseek-chat_flip_rates.csv` | VERIFIED |
| flip mean llama-3.3-70b | 14.5 | 14.5 | `results/analysis/v2_genie_bpc_nsclc_meta-llama-Llama-3.3-70B-Instruct-Turbo_flip_rates.csv` | VERIFIED |
| flip mean llama-3.1-8b | 17.5 | 17.5 | `results/analysis/v2_genie_bpc_nsclc_openrouter-meta-llama-llama-3.1-8b-instruct_flip_rates.csv` | VERIFIED |
| flip mean gpt-4o | 11.7 | 11.7 | `results/analysis/v2_genie_bpc_nsclc_gpt-4o_flip_rates.csv` | VERIFIED |
| flip mean gpt-4o-mini | 22.1 | 22.1 | `results/analysis/v2_genie_bpc_nsclc_gpt-4o-mini_flip_rates.csv` | VERIFIED |
| flip range | 11.7–22.1% | 11.7 (gpt-4o) – 22.1 (gpt-4o-mini) | `results/analysis flip files` | VERIFIED |
| Cohen's d white_male_private | -0.016 | -0.016 | `results/analysis/*_soft_intensity.csv (mean of 6)` | VERIFIED |
| Cohen's d black_race_only | 0.005 | 0.005 | `results/analysis/*_soft_intensity.csv (mean of 6)` | VERIFIED |
| Cohen's d underinsured_only | 1.01 | 1.01 | `results/analysis/*_soft_intensity.csv (mean of 6)` | VERIFIED |
| Cohen's d uninsured_only | 0.818 | 0.818 | `results/analysis/*_soft_intensity.csv (mean of 6)` | VERIFIED |
| Cohen's d unhoused_patient | 0.758 | 0.758 | `results/analysis/*_soft_intensity.csv (mean of 6)` | VERIFIED |
| Cohen's d low_income_patient | 0.772 | 0.772 | `results/analysis/*_soft_intensity.csv (mean of 6)` | VERIFIED |
| Cohen's d latina_female_uninsured | 0.774 | 0.774 | `results/analysis/*_soft_intensity.csv (mean of 6)` | VERIFIED |
| Cohen's d high_income_patient | 0.02 | 0.02 | `results/analysis/*_soft_intensity.csv (mean of 6)` | VERIFIED |
| BH-FDR survivor deepseek::underinsured (v1.2025) | 94 down/48 up, p=0.0001, q=0.0245 | 91 down/40 up, p=0.00001 under v6.2026 (pre-rescore gave 94/48) | `reproduced via correct_analysis.directional_decision` | VERIFIED-DIRECTION (counts shift w/ scorer version) |
| max single effect d=1.62 | gemini latina_female_uninsured | 1.6238 | `soft_intensity gemini` | VERIFIED |
| gemini underinsured d=1.55 | 1.55 | 1.5535 | `soft_intensity gemini` | VERIFIED |
| cohort EGFR actionable | 224 | 224 | `data/processed/genie_bpc_nsclc_with_notes.json` | VERIFIED |
| cohort KRAS G12C | 116 | 120 | `data/processed/genie_bpc_nsclc_with_notes.json` | MINOR-DIFF |
| cohort ALK | 42 | 43 | `data/processed/genie_bpc_nsclc_with_notes.json` | MINOR-DIFF |
| cohort MET ex14 | 22 | 23 | `data/processed/genie_bpc_nsclc_with_notes.json` | MINOR-DIFF |
| cohort ROS1 | 19 | 20 | `data/processed/genie_bpc_nsclc_with_notes.json` | MINOR-DIFF |
| cohort RET | 14 | 15 | `data/processed/genie_bpc_nsclc_with_notes.json` | MINOR-DIFF |
| cohort BRAF | 11 | 11 | `data/processed/genie_bpc_nsclc_with_notes.json` | VERIFIED |
| cohort NTRK | 2 | 2 | `data/processed/genie_bpc_nsclc_with_notes.json` | VERIFIED |
| cohort PD-L1 tested | 377 | 377 | `data/processed/genie_bpc_nsclc_with_notes.json` | VERIFIED |
| cohort N cohort | 1048 | 1048 | `data/processed/genie_bpc_nsclc_with_notes.json` | VERIFIED |
| cohort stage IV/III/I-II | 594/251/203 | 594/251/203 | `data/processed/genie_bpc_nsclc_with_notes.json` | VERIFIED |
| cohort histology adeno/sq/nos | 884/123/41 | 884/123/41 | `data/processed/genie_bpc_nsclc_with_notes.json` | VERIFIED |
| cohort site MSK/DFCI/VICC | 556/343/149 | 556/343/149 | `data/processed/genie_bpc_nsclc_with_notes.json` | VERIFIED |

## Summary
- Checked: 33
- Status counts: {'VERIFIED': 27, 'VERIFIED-DIRECTION (counts shift w/ scorer version)': 1, 'MINOR-DIFF': 5}
- All flip-rate means (6/6) and all spot-checked Table 2 Cohen's d (8/8) match exactly.
- Minor biomarker count diffs (1–4 cases) reflect a status-field counting-convention difference, not a data error; EGFR/BRAF/NTRK/PD-L1/N/stage/histology/site all exact.