#!/usr/bin/env python3
"""Omar-et-al-style quantitative bias metrics on the BRCA+PANC PILOT checkpoints.

    *** EXPLORATORY PILOT ANALYSIS (n ~ 50 / cohort) — NOT confirmatory. ***

Produces three Omar-style quantitative bias outputs, computed PER cohort × PER
model (cohorts and models are NEVER pooled). This mirrors the analysis style of
Omar et al. (2025), adapted to the EquityGUIDE FRAMING outcome (soft-bias stigma
composite) instead of a treatment-category label.

Outputs
───────
(A) OMAR-STYLE "TABLE 1": per-variant odds ratio (95% Cornfield CI), Fisher p,
    and BH-q for the pooled BINARY STIGMA COMPOSITE vs the no_demographics
    reference. Composite fires when adherence_compliance OR sdoh_generation
    fires. This is the direct Table-1 analog for the framing outcome.

(B) PER-MODEL VARIABILITY SCORE (Omar metric 4): sum over the 30 variants of
    |stigma_rate(variant) − stigma_rate(no_demographics)|, plus a normalized
    (÷30) version. One scalar per cohort × model — a single bias-magnitude number
    feeding the H4 cross-model convergence story.

(C) GRADED ORDINAL score: mean soft_bias_intensity for the disadvantaged variants
    (unhoused_patient, black_unhoused, low_income_patient) vs the no_demographics
    reference and vs the race-only controls, with paired Cohen's d + 95% CI
    (paired by case). The ordinal analog of Omar's ordinal outcomes.

Statistical caveats
───────────────────
- The Table-1 ORs are per-variant-vs-reference 2×2 Fisher ORs. Responses are
  paired within case (one response per case per variant); a McNemar-style paired
  test is available in the source module, but the Table-1 analog uses the 2×2
  Fisher OR by design. The PRE-REGISTERED CONFIRMATORY version is a
  case-clustered logistic GLM — NOT YET BUILT.
- Zero cells are handled by the Haldane-Anscombe 0.5 correction inside
  _compute_or (imported from scripts/nsclc/analyze_genie_bpc.py); such variants
  are flagged in the output.

Reuses (imported, not reinvented):
  src.analyze.soft_bias.detect_all
  scripts.nsclc.analyze_genie_bpc._compute_or   (Fisher OR + Cornfield CI + Haldane)
  src.analyze.stats.benjamini_hochberg, paired_delta
  src.analyze.continuous_scores.soft_bias_intensity

Runs NO model calls and NO full-cohort runs. Reads existing checkpoints only.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.analyze.soft_bias import detect_all
from src.analyze.stats import benjamini_hochberg, paired_delta
from src.analyze.continuous_scores import soft_bias_intensity
from scripts.nsclc.analyze_genie_bpc import _compute_or  # Fisher OR + Cornfield CI + Haldane

REFERENCE = "no_demographics"
DISADVANTAGED = ["unhoused_patient", "black_unhoused", "low_income_patient"]
RACE_ONLY_CONTROLS = [
    "black_race_only", "hispanic_race_only", "asian_race_only",
    "native_american_race_only", "middle_eastern_race_only", "multiracial_race_only",
]

CHECKPOINTS = {
    ("BRCA", "gemini"):   "v2_genie_bpc_brca_pilot50_checkpoint.json",
    ("BRCA", "deepseek"): "v2_genie_bpc_brca_pilot50_deepseek-chat_checkpoint.json",
    ("PANC", "gemini"):   "v2_genie_bpc_panc_pilot50_checkpoint.json",
    ("PANC", "deepseek"): "v2_genie_bpc_panc_pilot50_checkpoint.json".replace(
        "panc_pilot50", "panc_pilot50_deepseek-chat"),
}
BASELINE_DIR = REPO_ROOT / "results" / "baseline"


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------

def _stigma_composite(result: dict) -> bool | None:
    """Binary stigma composite: adherence_compliance OR sdoh_generation.

    Returns None for an unusable (errored/empty) response.
    """
    if not result or "error" in result:
        return None
    text = result.get("response_text", "")
    if not text:
        return None
    flags = detect_all(text)
    return bool(flags["adherence_compliance"] or flags["sdoh_generation"])


def load_checkpoint(fname: str) -> dict:
    with open(BASELINE_DIR / fname) as fh:
        return json.load(fh)


def variant_order(checkpoint: dict) -> list[str]:
    """All variant labels except the reference, in first-case order."""
    first = next(iter(checkpoint.values()))
    return [v for v in first.keys() if v != REFERENCE]


# ---------------------------------------------------------------------------
# (A) Omar-style Table 1 — per-variant OR on the binary stigma composite
# ---------------------------------------------------------------------------

def table1_ors(checkpoint: dict) -> list[dict]:
    """Per-variant 2×2 Fisher OR (Cornfield CI) vs no_demographics on the composite.

    Counts are per-case: pos = # cases where the variant fired stigma, n = #
    usable cases (both variant and reference scoreable for that case).
    """
    variants = variant_order(checkpoint)
    rows = []
    pvals: dict[str, float] = {}

    for variant in variants:
        pos_var = n_var = pos_ref = n_ref = 0
        for case_id, vmap in checkpoint.items():
            v_stig = _stigma_composite(vmap.get(variant, {}))
            r_stig = _stigma_composite(vmap.get(REFERENCE, {}))
            if v_stig is None or r_stig is None:
                continue  # require both usable on the SAME case
            n_var += 1
            n_ref += 1
            pos_var += int(v_stig)
            pos_ref += int(r_stig)

        zero_cell = 0 in (pos_var, n_var - pos_var, pos_ref, n_ref - pos_ref)
        or_, ci_lo, ci_hi, p = _compute_or(pos_var, n_var, pos_ref, n_ref)
        pvals[variant] = p
        rows.append({
            "variant": variant,
            "pos_var": pos_var, "n_var": n_var,
            "pos_ref": pos_ref, "n_ref": n_ref,
            "or": or_, "ci_lo": ci_lo, "ci_hi": ci_hi, "p": p,
            "zero_cell": zero_cell,
        })

    qvals = benjamini_hochberg(pvals)
    for r in rows:
        r["q"] = qvals[r["variant"]]
    rows.sort(key=lambda r: r["or"], reverse=True)
    return rows


def print_table1(cohort: str, model: str, rows: list[dict]) -> None:
    print(f"\n(A) OMAR-STYLE TABLE 1 — binary stigma composite OR vs {REFERENCE}")
    print(f"    cohort={cohort}  model={model}  [EXPLORATORY PILOT]")
    print(f"    composite = adherence_compliance OR sdoh_generation; 30 variants; "
          f"BH-FDR across the 30 within this cohort×model")
    print(f"    OR is per-variant-vs-reference 2×2 Fisher; case-clustered logistic "
          f"GLM is the (not-yet-built) confirmatory version")
    hdr = f"    {'variant':<28}{'pos/n':>9}{'ref':>7}{'OR':>8}  {'95% CI':>17}{'p':>9}{'q':>9}  flag"
    print(hdr)
    print("    " + "-" * (len(hdr) - 4))
    for r in rows:
        ci = f"[{r['ci_lo']:.2f}, {r['ci_hi']:.2f}]"
        flag = "ZERO-CELL(Haldane)" if r["zero_cell"] else ""
        print(f"    {r['variant']:<28}{r['pos_var']:>3}/{r['n_var']:<5}"
              f"{r['pos_ref']:>3}/{r['n_ref']:<3}{r['or']:>8.2f}  {ci:>17}"
              f"{r['p']:>9.3f}{r['q']:>9.3f}  {flag}")


# ---------------------------------------------------------------------------
# (B) Per-model variability score (Omar metric 4)
# ---------------------------------------------------------------------------

def variability_score(checkpoint: dict) -> dict:
    """Sum over 30 variants of |rate(variant) − rate(reference)| (+ normalized)."""
    variants = variant_order(checkpoint)

    def rate(label: str) -> float:
        pos = n = 0
        for vmap in checkpoint.values():
            s = _stigma_composite(vmap.get(label, {}))
            if s is None:
                continue
            n += 1
            pos += int(s)
        return pos / n if n else 0.0

    ref_rate = rate(REFERENCE)
    total = sum(abs(rate(v) - ref_rate) for v in variants)
    return {"ref_rate": ref_rate, "sum_abs_dev": total,
            "normalized": total / len(variants), "n_variants": len(variants)}


# ---------------------------------------------------------------------------
# (C) Graded ordinal score — soft_bias_intensity, paired vs ref and race-only
# ---------------------------------------------------------------------------

def _intensity_map(checkpoint: dict, label: str) -> dict:
    """{case_id: soft_bias_intensity} for one variant (None if unusable)."""
    out = {}
    for case_id, vmap in checkpoint.items():
        res = vmap.get(label, {})
        if not res or "error" in res:
            out[case_id] = None
            continue
        out[case_id] = soft_bias_intensity(res.get("response_text", ""))
    return out


def _pooled_control_map(checkpoint: dict, labels: list[str]) -> dict:
    """Per-case mean intensity across a set of control variants (None if none usable)."""
    out = {}
    per_label = {lab: _intensity_map(checkpoint, lab) for lab in labels}
    for case_id in checkpoint:
        vals = [per_label[lab][case_id] for lab in labels
                if per_label[lab][case_id] is not None]
        out[case_id] = (sum(vals) / len(vals)) if vals else None
    return out


def graded_ordinal(checkpoint: dict) -> list[dict]:
    """Paired soft_bias_intensity contrasts: disadvantaged & race-only vs reference."""
    ref_map = _intensity_map(checkpoint, REFERENCE)
    race_map = _pooled_control_map(checkpoint, RACE_ONLY_CONTROLS)
    rows = []
    # Disadvantaged variants vs reference
    for label in DISADVANTAGED:
        d = paired_delta(ref_map, _intensity_map(checkpoint, label), test="wilcoxon")
        rows.append({"contrast": f"{label} vs {REFERENCE}", "group": "disadvantaged", **d})
    # Race-only controls (pooled) vs reference
    d = paired_delta(ref_map, race_map, test="wilcoxon")
    rows.append({"contrast": f"race_only(pooled) vs {REFERENCE}", "group": "control", **d})
    # Disadvantaged vs race-only controls (the separation test)
    for label in DISADVANTAGED:
        d = paired_delta(race_map, _intensity_map(checkpoint, label), test="wilcoxon")
        rows.append({"contrast": f"{label} vs race_only(pooled)", "group": "disadv−control", **d})
    return rows


def print_ordinal(cohort: str, model: str, rows: list[dict]) -> None:
    print(f"\n(C) GRADED ORDINAL — mean soft_bias_intensity, paired Cohen's d (95% CI)")
    print(f"    cohort={cohort}  model={model}  [EXPLORATORY PILOT]")
    print(f"    disadvantaged = {', '.join(DISADVANTAGED)}; controls = {len(RACE_ONLY_CONTROLS)} race-only variants")
    hdr = f"    {'contrast':<42}{'n':>4}{'mean':>7}{'ref':>7}{'delta':>7}{'d':>7}  {'95% CI d-delta':>18}"
    print(hdr)
    print("    " + "-" * (len(hdr) - 4))
    for r in rows:
        if r["n"] == 0:
            print(f"    {r['contrast']:<42}{'0':>4}   (no paired cases)")
            continue
        d_val = r["cohens_d"]
        ci_delta = f"[{r['ci_low']:.2f}, {r['ci_high']:.2f}]"
        print(f"    {r['contrast']:<42}{r['n']:>4}{r['mean']:>7.2f}{r['ref_mean']:>7.2f}"
              f"{r['delta']:>7.2f}{d_val:>7.2f}  {ci_delta:>18}")


# ---------------------------------------------------------------------------
# Optional figure — forest plot of Table-1 ORs (one representative model)
# ---------------------------------------------------------------------------

def forest_plot(cohort: str, model: str, rows: list[dict]) -> Path | None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except Exception as exc:  # pragma: no cover
        print(f"    [figure skipped: {exc}]")
        return None

    outdir = REPO_ROOT / "manuscript_brca_panc" / "figures" / "pilot_exploratory"
    outdir.mkdir(parents=True, exist_ok=True)
    ordered = sorted(rows, key=lambda r: r["or"])
    y = np.arange(len(ordered))
    ors = [r["or"] for r in ordered]
    lo = [r["ci_lo"] for r in ordered]
    hi = [r["ci_hi"] for r in ordered]

    fig, ax = plt.subplots(figsize=(7, 9))
    for i, r in enumerate(ordered):
        ax.plot([lo[i], hi[i]], [i, i], color="#555", lw=1)
    ax.scatter(ors, y, color="#c0392b", zorder=3, s=22)
    ax.axvline(1.0, color="#888", ls="--", lw=1)
    ax.set_xscale("log")
    ax.set_yticks(y)
    ax.set_yticklabels([r["variant"] for r in ordered], fontsize=7)
    ax.set_xlabel("Odds ratio (log scale) — stigma composite vs no_demographics")
    ax.set_title(f"[EXPLORATORY PILOT] Stigma-composite ORs\n{cohort} / {model}  (n≈50)", fontsize=10)
    fig.tight_layout()
    out = outdir / f"pilot_omar_table1_forest_{cohort.lower()}_{model}.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 78)
    print("OMAR-STYLE QUANTITATIVE BIAS METRICS — BRCA + PANC PILOT")
    print("*** EXPLORATORY PILOT ANALYSIS (n ~ 50 / cohort) — NOT confirmatory ***")
    print("No model calls; reads existing checkpoints only. Cohorts/models never pooled.")
    print("=" * 78)

    variability_rows = []
    fig_done = False

    for (cohort, model), fname in CHECKPOINTS.items():
        checkpoint = load_checkpoint(fname)
        print("\n" + "#" * 78)
        print(f"# COHORT={cohort}  MODEL={model}  (cases={len(checkpoint)})  file={fname}")
        print("#" * 78)

        # (A) Table 1
        t1 = table1_ors(checkpoint)
        print_table1(cohort, model, t1)

        # (B) variability
        vs = variability_score(checkpoint)
        variability_rows.append((cohort, model, vs))

        # (C) ordinal
        print_ordinal(cohort, model, graded_ordinal(checkpoint))

        # figure once, on the first (representative) model
        if not fig_done:
            out = forest_plot(cohort, model, t1)
            if out:
                print(f"\n    [figure] forest plot saved: {out}")
            fig_done = True

    # (B) summary table across all cohort×model (reported, never pooled)
    print("\n" + "=" * 78)
    print("(B) PER-MODEL VARIABILITY SCORE (Omar metric 4) — single bias-magnitude number")
    print("    sum over 30 variants of |stigma_rate(variant) − stigma_rate(no_demographics)|")
    print(f"    {'cohort':<8}{'model':<12}{'ref_rate':>10}{'sum_abs_dev':>14}{'normalized':>13}")
    print("    " + "-" * 53)
    for cohort, model, vs in variability_rows:
        print(f"    {cohort:<8}{model:<12}{vs['ref_rate']:>10.3f}"
              f"{vs['sum_abs_dev']:>14.3f}{vs['normalized']:>13.4f}")
    print("=" * 78)


if __name__ == "__main__":
    main()
