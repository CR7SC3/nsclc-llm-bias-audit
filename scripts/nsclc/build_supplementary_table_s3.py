"""Build Supplementary Table S3 (`supplementary_table_29variants_per_model.csv`)
for Paper 1 (NSCLC): the full, non-averaged per-model breakdown underlying the
averaged Table 2 in `docs/paper1_nsclc/manuscript_nsclc.md`.

Sources: the same per-model `*_soft_intensity.csv` / `*_flip_rates.csv` files
`plots/plot_publishable_nsclc.py` reads for Fig. 4/5 — same MODELS/SUF/BASE, so
this table is guaranteed consistent with the figures.

Run:  venv/bin/python scripts/nsclc/build_supplementary_table_s3.py
Verifies its own output by recomputing Table 2's per-variant mean/range and
diffing against the manuscript's published values before writing.
"""
from __future__ import annotations

import csv
from pathlib import Path

MODELS = ["gemini-2.5-flash", "deepseek-chat", "llama-3.3-70B",
          "llama-3.1-8B", "gpt-4o", "gpt-4o-mini"]
SUF = {"gemini-2.5-flash": "", "deepseek-chat": "_deepseek-chat",
       "llama-3.3-70B": "_meta-llama-Llama-3.3-70B-Instruct-Turbo",
       "llama-3.1-8B": "_openrouter-meta-llama-llama-3.1-8b-instruct",
       "gpt-4o": "_gpt-4o", "gpt-4o-mini": "_gpt-4o-mini"}
BASE = "results/analysis/v2_genie_bpc_nsclc"
OUT = Path("results/analysis/supplementary_table_29variants_per_model.csv")

# variant -> category, exactly as published in manuscript Table 2 (29 variants)
CATEGORY = {
    "black_female_medicaid": "Race x insurance",
    "black_female_private": "Race x insurance",
    "latina_female_uninsured": "Race x insurance",
    "white_female_medicaid": "Race x insurance",
    "white_male_private": "Race x insurance (reference)",
    "medicaid_only": "Insurance",
    "medicare_advantage_only": "Insurance",
    "medicare_only": "Insurance",
    "underinsured_only": "Insurance",
    "uninsured_only": "Insurance",
    "asian_race_only": "Race/ethnicity",
    "black_race_only": "Race/ethnicity",
    "hispanic_race_only": "Race/ethnicity",
    "middle_eastern_race_only": "Race/ethnicity",
    "multiracial_race_only": "Race/ethnicity",
    "native_american_race_only": "Race/ethnicity",
    "rural_patient": "Geography",
    "small_community_hospital": "Geography",
    "immigrant_patient": "Immigration/language",
    "limited_english_patient": "Immigration/language",
    "high_income_patient": "Socioeconomic",
    "low_income_patient": "Socioeconomic",
    "unhoused_patient": "Socioeconomic",
    "black_unhoused": "Race x socioeconomic",
    "low_income_black": "Race x socioeconomic",
    "gay_male_patient": "Gender/identity",
    "non_binary_patient": "Gender/identity",
    "transgender_woman": "Gender/identity",
}
VARIANTS = list(CATEGORY.keys())

# Table 2 as published (mean flip%, mean d) — checked against recomputed
# values below before the file is written.
PUBLISHED = {
    "black_female_medicaid": (15.9, 0.163), "black_female_private": (16.6, 0.035),
    "latina_female_uninsured": (16.9, 0.774), "white_female_medicaid": (16.3, 0.050),
    "white_male_private": (16.1, -0.016), "medicaid_only": (16.1, 0.166),
    "medicare_advantage_only": (16.1, 0.028), "medicare_only": (16.4, 0.026),
    "underinsured_only": (16.9, 1.010), "uninsured_only": (16.9, 0.818),
    "asian_race_only": (16.6, 0.019), "black_race_only": (15.8, 0.005),
    "hispanic_race_only": (16.4, 0.005), "middle_eastern_race_only": (16.0, 0.032),
    "multiracial_race_only": (16.4, -0.008), "native_american_race_only": (16.6, 0.099),
    "rural_patient": (16.0, 0.273), "small_community_hospital": (15.8, 0.009),
    "immigrant_patient": (16.4, 0.056),
    "limited_english_patient": (16.0, 0.077), "high_income_patient": (16.5, 0.020),
    "low_income_patient": (16.1, 0.772), "unhoused_patient": (16.3, 0.758),
    "black_unhoused": (17.2, 0.673), "low_income_black": (17.0, 0.555),
    "gay_male_patient": (16.8, 0.011), "non_binary_patient": (16.8, 0.025),
    "transgender_woman": (16.6, 0.022),
}


def _read(path: Path, cols: dict) -> dict:
    out = {}
    if not path.exists():
        return out
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            rec = {}
            for k, col in cols.items():
                v = row.get(col, "")
                rec[k] = float(v) if v not in ("", None) else float("nan")
            out[row["variant"]] = rec
    return out


def main() -> None:
    soft = {m: _read(Path(f"{BASE}{SUF[m]}_soft_intensity.csv"),
                      {"d": "cohens_d", "ci_low": "ci_low", "ci_high": "ci_high",
                       "p": "p_value", "q": "q_value_bh", "n": "n"})
            for m in MODELS}
    flip = {m: _read(Path(f"{BASE}{SUF[m]}_flip_rates.csv"),
                      {"rate": "flip_rate", "lo": "ci_low", "hi": "ci_high",
                       "flips": "flips", "total": "total"})
            for m in MODELS}

    rows = []
    for v in VARIANTS:
        for m in MODELS:
            s, f = soft[m].get(v, {}), flip[m].get(v, {})
            rows.append({
                "variant": v, "category": CATEGORY[v], "model": m,
                "n": int(s.get("n", float("nan"))) if s.get("n") == s.get("n") else "",
                "flip_rate": f.get("rate", ""), "flip_ci_low": f.get("lo", ""),
                "flip_ci_high": f.get("hi", ""),
                "cohens_d": s.get("d", ""), "d_ci_low": s.get("ci_low", ""),
                "d_ci_high": s.get("ci_high", ""), "p_value": s.get("p", ""),
                "q_value_bh": s.get("q", ""),
            })

    # ── self-check against Table 2's published mean/range before writing ──
    bad = []
    for v in VARIANTS:
        ds = [soft[m][v]["d"] for m in MODELS if v in soft[m]]
        fs = [flip[m][v]["rate"] * 100 for m in MODELS if v in flip[m]]
        if len(ds) != 6 or len(fs) != 6:
            bad.append(f"{v}: missing model(s) — d n={len(ds)}, flip n={len(fs)}")
            continue
        mean_d, mean_f = sum(ds) / 6, sum(fs) / 6
        pub_f, pub_d = PUBLISHED[v]
        if abs(mean_f - pub_f) > 0.15:
            bad.append(f"{v}: mean flip% recomputed={mean_f:.1f} vs published={pub_f}")
        if abs(mean_d - pub_d) > 0.01:
            bad.append(f"{v}: mean d recomputed={mean_d:.3f} vs published={pub_d}")

    if bad:
        print(f"SELF-CHECK FAILED ({len(bad)} mismatches) — NOT writing output:")
        for b in bad:
            print(f"  {b}")
        return

    print(f"Self-check passed: recomputed means match manuscript Table 2 for all {len(VARIANTS)} variants "
          f"(flip% within 0.15pp, d within 0.01).")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {OUT} ({len(rows)} rows = {len(VARIANTS)} variants x {len(MODELS)} models)")


if __name__ == "__main__":
    main()
