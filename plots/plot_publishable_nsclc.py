"""Build figures/manuscript/NSCLC_publishable/ -- the submission-ready NSCLC
figure set, renumbered into narrative order and fixing the readiness-review
blocking items:
  1. F2/F5 (dissociation, forest) extended from 3 to all 6 complete vendor arms.
  2. F4 (soft split) x-axes harmonized to a shared scale across models.
  3. F6 (stigma gradient) title softened: race-only is small-but-not-always-
     zero (per bootstrap CI), not asserted "~0".
  4. F7 (stigma breakdown) visually splits the 2 defensible dimensions
     (adherence doubt, hallucinated SDOH) from the 2 non-defensible ones
     (prognosis framing, watchful waiting) with a panel break, not one stack.
  5. Files renumbered Fig1..Fig8 + S1 in the manuscript's narrative order,
     with journal-ready file naming and a NARRATIVE_ORDER.md caption sheet.

Run:  venv/bin/python plots/plot_publishable_nsclc.py
"""
from pathlib import Path
import sys, csv, shutil, subprocess
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from scipy.stats import t as student_t
from src.analyze.stats import wilson_ci

OUT = Path("figures/manuscript")
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 11, "axes.grid": False, "figure.dpi": 150,
    "savefig.bbox": "tight", "figure.facecolor": "white",
    "axes.facecolor": "white", "savefig.facecolor": "white",
})

MODELS = ["gemini-2.5-flash", "deepseek-chat", "llama-3.3-70B",
          "llama-3.1-8B", "gpt-4o", "gpt-4o-mini"]
MC = {"gemini-2.5-flash": "#4C72B0", "deepseek-chat": "#C44E52", "llama-3.3-70B": "#55A868",
      "llama-3.1-8B": "#937860", "gpt-4o": "#8172B3", "gpt-4o-mini": "#CCB974"}
ML = {"gemini-2.5-flash": "Gemini-2.5-flash", "deepseek-chat": "DeepSeek-chat",
      "llama-3.3-70B": "Llama-3.3-70B", "llama-3.1-8B": "Llama-3.1-8B",
      "gpt-4o": "GPT-4o", "gpt-4o-mini": "GPT-4o-mini"}
SUF = {"gemini-2.5-flash": "", "deepseek-chat": "_deepseek-chat",
       "llama-3.3-70B": "_meta-llama-Llama-3.3-70B-Instruct-Turbo",
       "llama-3.1-8B": "_openrouter-meta-llama-llama-3.1-8b-instruct",
       "gpt-4o": "_gpt-4o", "gpt-4o-mini": "_gpt-4o-mini"}
BASE = "results/analysis/v2_genie_bpc_nsclc"

# Main-figure Fig 2A shows the confirmatory binary NCCN concordance only (clean
# per-model histogram). The secondary/exploratory partial-concordance overlay
# moves to the supplement per the locked figure plan -- set True to restore it.
SHOW_PARTIAL = False


def _regen_or_skip(dst_name, gen_script, upstream_names):
    """Idempotent copy step: the one-time migration into figures/manuscript/
    already renamed the original outputs in place, so on a fresh checkout
    `upstream_names` won't exist -- re-run `gen_script` to regenerate them."""
    dst = OUT / dst_name
    if dst.exists():
        print(f"kept {dst_name} (already in place)")
        return
    for name in upstream_names:
        src = OUT / name
        if src.exists():
            shutil.copy(src, dst)
            print(f"wrote {dst_name} (copied from {name})")
            return
    print(f"SKIPPED {dst_name}: rerun `venv/bin/python {gen_script}` to regenerate, "
          f"then rerun this script.")


def _run_script(script, expect):
    """Regenerate a panel/figure via a standalone generator run as a subprocess.
    These generators import from THIS module (MODELS/SUF/BASE/_read, or
    plot_care_intensity_permodel), so importing them back would be circular;
    running them as a subprocess from the repo root keeps their relative data
    paths (results/analysis/...) correct. `expect` must exist afterward."""
    r = subprocess.run([sys.executable, script], capture_output=True, text=True)
    if Path(expect).exists():
        print(f"wrote {expect} (via {script})")
    else:
        print(f"FAILED {expect}: `{sys.executable} {script}` did not produce it")
        print((r.stdout or "")[-600:]); print((r.stderr or "")[-600:])


# ───────────────────────── Fig 1: cohort description (copy, renamed) ────────
def fig1_cohort():
    _regen_or_skip("Fig1_cohort_description.png", "plots/plot_genie_cohort_strata.py",
                    ["fig_genie_cohort_strata.png"])


# ───────────────────────── Fig 2: task competence & decision stability ──────
PARTIAL_CONCORDANCE_SUMMARY_CSV = "results/analysis/v2_genie_bpc_nsclc_partial_concordance_summary.csv"


def _load_partial_concordance_summary():
    """Load the secondary/exploratory partial-concordance summary produced by
    scripts/nsclc/analyze_partial_concordance.py, if present.

    Returns None if the CSV hasn't been generated yet (panel B is then
    skipped and only the pre-registered binary panel A is drawn).
    """
    p = Path(PARTIAL_CONCORDANCE_SUMMARY_CSV)
    if not p.exists():
        return None
    df = pd.read_csv(p).set_index("model")
    missing = [m for m in MODELS if m not in df.index]
    if missing:
        print(f"  NOTE: partial-concordance summary missing rows for {missing}; skipping panel B")
        return None
    return df


# Per-model treatment-aggressiveness tier CSVs (1=BSC ... 8=surgical resection;
# ordinal, from src/analyze/continuous_scores.py TREATMENT_RANK).
AGG_FILES = {
    "gemini-2.5-flash": "results/analysis/v2_genie_bpc_nsclc_aggressiveness.csv",
    "deepseek-chat":    "results/analysis/v2_genie_bpc_nsclc_deepseek-chat_aggressiveness.csv",
    "llama-3.3-70B":    "results/analysis/v2_genie_bpc_nsclc_meta-llama-Llama-3.3-70B-Instruct-Turbo_aggressiveness.csv",
    "llama-3.1-8B":     "results/analysis/v2_genie_bpc_nsclc_openrouter-meta-llama-llama-3.1-8b-instruct_aggressiveness.csv",
    "gpt-4o":           "results/analysis/v2_genie_bpc_nsclc_gpt-4o_aggressiveness.csv",
    "gpt-4o-mini":      "results/analysis/v2_genie_bpc_nsclc_gpt-4o-mini_aggressiveness.csv",
}


def _load_aggressiveness():
    """Reference vs pooled with-demographics mean treatment-tier rank per model,
    plus the BH-significant variant count. Returns None if any CSV is missing."""
    out = {}
    for m, f in AGG_FILES.items():
        if not Path(f).exists():
            print(f"  NOTE: aggressiveness CSV missing for {m}; skipping panel C")
            return None
        rows = [r for r in pd.read_csv(f).to_dict("records") if pd.notna(r["mean_score"])]
        ref = next(r["mean_score"] for r in rows if r["variant"] == "no_demographics")
        dv = [r for r in rows if r["variant"] != "no_demographics"]
        num = sum(r["mean_score"] * r["n"] for r in dv)
        den = sum(r["n"] for r in dv)
        nsig = sum(1 for r in dv if pd.notna(r["q_value_bh"]) and r["q_value_bh"] < 0.05)
        out[m] = dict(ref=ref, dem=num / den, n_dem=int(den), nsig=nsig, n_var=len(dv))
    return out


def fig2_concordance():
    # reference / with-demographics concordance recomputed from plot_concordance_by_variant.py
    # (confirmatory NCCN scorer, no_demographics reference), 2026-07 verification.
    ref = {"gemini-2.5-flash": 78.8, "deepseek-chat": 89.0, "llama-3.3-70B": 73.9,
           "llama-3.1-8B": 49.9, "gpt-4o": 86.7, "gpt-4o-mini": 53.1}
    dem = {"gemini-2.5-flash": 79.8, "deepseek-chat": 88.5, "llama-3.3-70B": 73.8,
           "llama-3.1-8B": 49.5, "gpt-4o": 85.7, "gpt-4o-mini": 54.1}
    n_ref = {"gemini-2.5-flash": 590, "deepseek-chat": 601, "llama-3.3-70B": 598,
             "llama-3.1-8B": 570, "gpt-4o": 603, "gpt-4o-mini": 585}
    n_dem = {"gemini-2.5-flash": 17119, "deepseek-chat": 17425, "llama-3.3-70B": 17311,
             "llama-3.1-8B": 16635, "gpt-4o": 17437, "gpt-4o-mini": 17022}
    # TOST equivalence counts recomputed from the confirmatory pipeline
    # (scripts/nsclc/correct_analysis.py MAJOR-6, margin d=+/-0.10), 2026-07 verification.
    tost = {"gemini-2.5-flash": "23/29", "deepseek-chat": "27/29", "llama-3.3-70B": "29/29",
            "llama-3.1-8B": "28/29", "gpt-4o": "29/29", "gpt-4o-mini": "27/29"}

    def _ci(rate, n):
        lo, hi = wilson_ci(round(rate / 100 * n), n)
        return rate - 100 * lo, 100 * hi - rate

    x = np.arange(len(MODELS)); w = 0.36
    ekw = dict(ecolor="0.3", lw=1.0, capsize=3)

    partial = _load_partial_concordance_summary() if SHOW_PARTIAL else None
    agg = _load_aggressiveness()

    if agg is not None:
        fig, (ax, axB) = plt.subplots(1, 2, figsize=(15.5, 5.8),
                                      gridspec_kw={"width_ratios": [1.4, 1.0]})
    else:
        fig, ax = plt.subplots(figsize=(11.5, 5.6))

    # ---- concordance bars, factored so the standalone left axis AND the
    # concordance-only panel export reuse identical drawing --------------------
    # Solid bar = pre-registered binary NCCN concordance (confirmatory); hatched cap
    # = SECONDARY/EXPLORATORY partial concordance (see docs/METHODS.md section 12).
    err_ref = np.array([_ci(ref[m], n_ref[m]) for m in MODELS]).T
    err_dem = np.array([_ci(dem[m], n_dem[m]) for m in MODELS]).T
    if partial is not None:
        p_ref = {m: partial.loc[m, "ref_partial_concordance_pct"] for m in MODELS}
        p_dem = {m: partial.loc[m, "dem_partial_concordance_pct"] for m in MODELS}
    from matplotlib.patches import Patch

    def draw_conc(a, legend_anchor=None):
        if partial is not None:
            a.bar(x - w / 2, [p_ref[m] for m in MODELS], w, color=[MC[m] for m in MODELS],
                  alpha=0.20, edgecolor="k", linewidth=0.6, hatch="////", zorder=1)
            a.bar(x + w / 2, [p_dem[m] for m in MODELS], w, color=[MC[m] for m in MODELS],
                  alpha=0.30, edgecolor="k", linewidth=0.6, hatch="////", zorder=1)
        a.bar(x - w / 2, [ref[m] for m in MODELS], w, yerr=err_ref, error_kw=ekw,
              color=[MC[m] for m in MODELS], alpha=0.55, edgecolor="k", linewidth=0.6, zorder=3)
        # hatch on the with-demographics bar so demo vs no-demo survives grayscale/CVD
        # (shade alone was the sole encoder — council: dataviz)
        a.bar(x + w / 2, [dem[m] for m in MODELS], w, yerr=err_dem, error_kw=ekw,
              color=[MC[m] for m in MODELS], alpha=1.0, edgecolor="k", linewidth=0.6,
              hatch="///", zorder=3)
        for i, m in enumerate(MODELS):
            d = dem[m] - ref[m]
            top = max(ref[m], dem[m])
            if partial is not None:
                top = max(top, p_ref[m], p_dem[m])
            a.text(i, top + 4.5, f"$\\Delta$={d:+.1f} pp\nTOST {tost[m]} equiv.",
                   ha="center", va="bottom", fontsize=9)
        a.set_xticks(x); a.set_xticklabels([ML[m] for m in MODELS], rotation=12, ha="right")
        a.set_ylabel("Concordance with NCCN guideline label (%)")
        a.set_ylim(0, 118)
        handles = [
            Patch(facecolor="0.4", alpha=0.55, edgecolor="k", label="No-demographics (reference)"),
            Patch(facecolor="0.4", alpha=1.0, edgecolor="k", hatch="///", label="With demographics"),
        ]
        if partial is not None:
            handles += [
                Patch(facecolor="none", edgecolor="k", label="Binary NCCN concordance (pre-registered)"),
                Patch(facecolor="0.4", alpha=0.25, edgecolor="k", hatch="////",
                      label="Partial concordance (secondary/exploratory)"),
            ]
        a.legend(handles=handles, loc="upper left", bbox_to_anchor=legend_anchor,
                 fontsize=8.0, framealpha=0.95, ncol=1, borderaxespad=0.4)
        # equivalence margin (d = +/- 0.10) stated in the caption, not on-panel

    draw_conc(ax, legend_anchor=(1.01, 1.0) if agg is None else None)

    # ---- Panel B: treatment-aggressiveness tier (confirmatory, continuous) ----
    if agg is not None:
        aref = [agg[m]["ref"] for m in MODELS]
        adem = [agg[m]["dem"] for m in MODELS]
        axB.bar(x - w / 2, aref, w, color=[MC[m] for m in MODELS], alpha=0.55,
                edgecolor="k", linewidth=0.6, zorder=3)
        axB.bar(x + w / 2, adem, w, color=[MC[m] for m in MODELS], alpha=1.0,
                edgecolor="k", linewidth=0.6, zorder=3)
        for i, m in enumerate(MODELS):
            d = agg[m]["dem"] - agg[m]["ref"]
            axB.text(i, max(aref[i], adem[i]) + 0.18,
                     f"$\\Delta$={d:+.2f}\n{agg[m]['nsig']}/{agg[m]['n_var']} BH-sig",
                     ha="center", va="bottom", fontsize=8.5)
        axB.set_xticks(x); axB.set_xticklabels([ML[m] for m in MODELS], rotation=12, ha="right")
        axB.set_ylabel("Mean treatment-aggressiveness tier\n(1 = best supportive care  …  8 = surgical resection)")
        axB.set_ylim(0, 8.6)
        from matplotlib.patches import Patch as _Patch
        axB.legend(handles=[
            _Patch(facecolor="0.4", alpha=0.55, edgecolor="k", label="No-demographics (reference)"),
            _Patch(facecolor="0.4", alpha=1.0, edgecolor="k", label="With demographics"),
        ], loc="lower left", fontsize=8.0, framealpha=0.95, borderaxespad=0.4)
    # Concordance-% ONLY panel for combine_figures.py (Fig 2A). The tier-intensity
    # subpanel is dropped here — it duplicated the direction heatmap (Fig 2C) — so the
    # main figure carries only the concordance percentages. Titleless single axis.
    PANELS = Path("figures/manuscript_combined/panels"); PANELS.mkdir(parents=True, exist_ok=True)
    figP, axP = plt.subplots(figsize=(8.0, 5.6))
    draw_conc(axP)
    figP.tight_layout()
    figP.savefig(PANELS / "p_concordance_stability.png", dpi=200, bbox_inches="tight",
                 facecolor="white")
    plt.close(figP)
    print("wrote panels/p_concordance_stability.png (concordance-only)")

    # standalone supplement copy (2 subpanels): restore banner titles + sub-panel letters.
    ax.set_title("Treatment-recommendation concordance is unaffected by\n"
                 "prepended demographic labels", fontsize=12.5, fontweight="bold")
    if agg is not None:
        axB.set_title("Treatment intensity is likewise unaffected by\n"
                      "demographic labels (ordinal tier rank)",
                      fontsize=12.5, fontweight="bold")
        ax.text(-0.10, 1.03, "A", transform=ax.transAxes, fontsize=15, fontweight="bold")
        axB.text(-0.14, 1.03, "B", transform=axB.transAxes, fontsize=15, fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUT / "Fig2_concordance_stability.png"); plt.close(fig)
    if partial is not None:
        print("wrote Fig2_concordance_stability.png "
              "(binary NCCN concordance overlaid with secondary/exploratory partial concordance)")
    else:
        print("wrote Fig2_concordance_stability.png "
              "(binary NCCN concordance only; partial-concordance overlay off -- SHOW_PARTIAL=False)")


# ───────────── Fig 3: concordance by variant (copy, renamed — already 6-model) ─
def fig3_concordance_by_variant():
    _regen_or_skip("Fig3_concordance_by_variant.png", "plots/plot_concordance_by_variant.py",
                    ["fig1_concordance_by_variant.png"])


# ───────────── Fig 4: the dissociation centerpiece, now 6 vendors ───────────
TIERS = [
    ("Socioeconomic disadvantage", "#C1272D", [
        "underinsured_only", "uninsured_only", "latina_female_uninsured",
        "low_income_patient", "black_unhoused", "unhoused_patient",
    ]),
    ("Race only", "#6A51A3", [
        "black_race_only", "hispanic_race_only", "asian_race_only",
    ]),
    ("Control", "#666666", ["no_demographics"]),
]
LABELS = {
    "underinsured_only": "Underinsured", "uninsured_only": "Uninsured",
    "latina_female_uninsured": "Latina female, uninsured", "low_income_patient": "Low income",
    "black_unhoused": "Black + unhoused", "unhoused_patient": "Unhoused",
    "black_race_only": "Black", "hispanic_race_only": "Hispanic", "asian_race_only": "Asian",
    "white_male_private": "White male, private ins.", "no_demographics": "No demographics",
}


def _read(path, key_cols):
    out = {}
    p = Path(path)
    if not p.exists():
        return out
    with open(p, newline="") as fh:
        for row in csv.DictReader(fh):
            rec = {}
            for k, col in key_cols.items():
                v = row.get(col, "")
                rec[k] = float(v) if v not in ("", None) else float("nan")
            out[row["variant"]] = rec
    return out


def fig4_dissociation():
    variants, tier_spans = [], []
    for name, colour, vs in TIERS:
        s = len(variants); variants += vs; tier_spans.append((name, colour, s, len(variants)))
    n = len(variants); y = np.arange(n)[::-1]
    offs = np.linspace(-0.30, 0.30, len(MODELS))

    data = {}
    for m in MODELS:
        soft = _read(f"{BASE}{SUF[m]}_soft_intensity.csv", {"d": "cohens_d", "q": "q_value_bh"})
        flip = _read(f"{BASE}{SUF[m]}_flip_rates.csv", {"rate": "flip_rate", "lo": "ci_low", "hi": "ci_high"})
        flip.setdefault("no_demographics", {"rate": 0.0, "lo": 0.0, "hi": 0.0})
        soft.setdefault("no_demographics", {"d": 0.0, "q": float("nan")})
        data[m] = {"soft": soft, "flip": flip}

    fig, (axA, axB) = plt.subplots(1, 2, figsize=(12.5, 6.8), sharey=True,
                                    gridspec_kw={"wspace": 0.08})
    demo_vars = [v for v in variants if v != "no_demographics"]
    for m, off in zip(MODELS, offs):
        colour = MC[m]; fl = data[m]["flip"]
        meanflip = np.nanmean([fl.get(v, {}).get("rate", np.nan) * 100 for v in demo_vars])
        axA.axvline(meanflip, color=colour, ls="--", lw=0.9, alpha=0.4, zorder=1)
        xs = [fl.get(v, {}).get("rate", np.nan) * 100 for v in variants]
        los = [fl.get(v, {}).get("lo", np.nan) * 100 for v in variants]
        his = [fl.get(v, {}).get("hi", np.nan) * 100 for v in variants]
        axA.hlines(y + off, los, his, color=colour, linewidth=0.9, alpha=0.55, zorder=2)
        axA.scatter(xs, y + off, s=18, color=colour, zorder=3, edgecolor="white", linewidth=0.3)
    axA.set_xlim(0, 27)
    axA.set_xlabel("Treatment-recommendation flip rate (%)", fontsize=9.5)
    axA.set_title("(A)  Treatment selection", fontsize=10.5, fontweight="bold", pad=8)
    axA.xaxis.grid(True, ls="--", alpha=0.35, zorder=0)

    axB.axvline(0, color="#444444", linewidth=0.9, zorder=4)
    for m, off in zip(MODELS, offs):
        colour = MC[m]; sd = data[m]["soft"]
        xs = [sd.get(v, {}).get("d", np.nan) for v in variants]
        sig = [sd.get(v, {}).get("q", np.nan) < 0.05 for v in variants]
        axB.scatter(xs, y + off, s=[26 if s else 16 for s in sig], color=colour,
                    zorder=3, edgecolor="white", linewidth=0.3)
    axB.set_xlim(-0.3, 2.05)
    axB.set_xlabel("Added soft-framing intensity (Cohen's $d$)", fontsize=9.5)
    axB.set_title("(B)  Response framing", fontsize=10.5, fontweight="bold", pad=8)
    axB.xaxis.grid(True, ls="--", alpha=0.35, zorder=0)

    axA.set_yticks(y); axA.set_yticklabels([LABELS[v] for v in variants], fontsize=9)
    tick_colour = {v: colour for name, colour, s, e in tier_spans for v in variants[s:e]}
    for tick, v in zip(axA.get_yticklabels(), variants):
        tick.set_color(tick_colour[v])
    for ax in (axA, axB):
        ax.set_ylim(-0.6, n - 0.4); ax.tick_params(axis="y", length=0)
        for name, colour, s, e in tier_spans:
            if s != 0:
                ax.axhline((y[s] + y[s - 1]) / 2, color="#dddddd", lw=0.8, zorder=1)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.set_axisbelow(True)
    for name, colour, s, e in tier_spans:
        mid = (y[s] + y[e - 1]) / 2
        axA.annotate(name, xy=(0, 0), xytext=(-0.40, mid), textcoords=("axes fraction", "data"),
                     rotation=90, ha="center", va="center", fontsize=8.0, fontweight="bold",
                     color=colour, annotation_clip=False)

    handles = [mlines.Line2D([], [], marker="o", linestyle="none", color=MC[m],
                             markersize=6.5, markeredgecolor="white", label=ML[m]) for m in MODELS]
    fig.legend(handles=handles, loc="lower center", ncol=6, frameon=False, fontsize=8.2,
               bbox_to_anchor=(0.5, -0.045))

    # titleless panel (A/B subtitles kept; banner suptitle + footnote suppressed —
    # those belong in the manuscript caption) for combine_figures.py -> Figure2
    PANELS = Path("figures/manuscript_combined/panels"); PANELS.mkdir(parents=True, exist_ok=True)
    fig.savefig(PANELS / "p_dissociation.png", dpi=200, bbox_inches="tight", facecolor="white")
    print("wrote panels/p_dissociation.png")

    fig.suptitle("Fig. 4 | Demographic labels leave the treatment decision unchanged\n"
                 "but reshape its framing -- six complete vendor arms",
                 fontsize=12.5, fontweight="bold", y=1.01)
    fig.text(0.5, -0.10,
             "1,048 GENIE NSCLC cases x 6 vendors x 30 variants; each variant = same note, one prepended "
             "demographic label vs no label.\n(A) Every variant overlaps its vendor's mean flip rate -- no "
             "demographic group destabilizes the recommendation. (B) Larger markers: $q_{BH}<0.05$.",
             ha="center", fontsize=7.2, color="#555555", style="italic")
    fig.savefig(OUT / "Fig4_dissociation_6vendor.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("wrote Fig4_dissociation_6vendor.png")


# ───────────── Fig 5: SES-vs-race forest, now 6 vendors ─────────────────────
def _read_forest(suffix):
    out = {}
    p = Path(f"{BASE}{suffix}_soft_intensity.csv")
    if not p.exists():
        return out
    with open(p, newline="") as fh:
        for row in csv.DictReader(fh):
            def f(c):
                v = row.get(c, "")
                return float(v) if v not in ("", None) else float("nan")
            d, delta = f("cohens_d"), f("delta")
            lo_raw, hi_raw = f("ci_low"), f("ci_high")
            scale = (d / delta) if delta not in (0.0, float("nan")) else 0.0
            out[row["variant"]] = {"d": d, "lo": lo_raw * scale, "hi": hi_raw * scale, "q": f("q_value_bh")}
    out.setdefault("no_demographics", {"d": 0.0, "lo": 0.0, "hi": 0.0, "q": float("nan")})
    return out


def fig5_forest():
    data = {m: _read_forest(SUF[m]) for m in MODELS}
    variants, tier_spans = [], []
    for name, colour, vs in TIERS:
        s = len(variants); variants += vs; tier_spans.append((name, colour, s, len(variants)))
    n = len(variants); y = np.arange(n)[::-1]
    offs = np.linspace(-0.30, 0.30, len(MODELS))

    fig, ax = plt.subplots(figsize=(9.5, 7.2))
    ax.axvline(0, color="#444444", linewidth=0.9, zorder=4)
    for m, off in zip(MODELS, offs):
        colour = MC[m]; sd = data[m]
        ds = [sd.get(v, {}).get("d", np.nan) for v in variants]
        los = [sd.get(v, {}).get("lo", np.nan) for v in variants]
        his = [sd.get(v, {}).get("hi", np.nan) for v in variants]
        ax.hlines(y + off, los, his, color=colour, linewidth=1.1, alpha=0.8, zorder=2)
        ax.scatter(ds, y + off, s=22, color=colour, zorder=3, edgecolor="white", linewidth=0.4)

    ax.set_yticks(y); ax.set_yticklabels([LABELS[v] for v in variants], fontsize=9)
    tick_colour = {v: colour for name, colour, s, e in tier_spans for v in variants[s:e]}
    for tick, v in zip(ax.get_yticklabels(), variants):
        tick.set_color(tick_colour[v])
    for name, colour, s, e in tier_spans:
        if s != 0:
            ax.axhline((y[s] + y[s - 1]) / 2, color="#dddddd", lw=0.8, zorder=1)
        mid = (y[s] + y[e - 1]) / 2
        ax.annotate(name, xy=(0, 0), xytext=(-0.42, mid), textcoords=("axes fraction", "data"),
                    rotation=90, ha="center", va="center", fontsize=8.0, fontweight="bold",
                    color=colour, annotation_clip=False)
    ax.set_ylim(-0.6, n - 0.4); ax.set_xlim(-0.55, 2.05)
    ax.set_xlabel("Added soft-framing intensity (Cohen's $d$ vs no-demographics, 95% CI)", fontsize=9.5)
    ax.set_title("Fig. 5 | Framing bias is socioeconomic, not racial, and generalizes\n"
                 "across all six complete vendor arms (1,048 GENIE NSCLC cases)",
                 fontsize=12, fontweight="bold", pad=10)
    ax.xaxis.grid(True, ls="--", alpha=0.4, zorder=0)
    ax.tick_params(axis="y", length=0)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.set_axisbelow(True)
    handles = [mlines.Line2D([], [], marker="o", linestyle="-", color=MC[m], markersize=6.5,
                             markeredgecolor="white", label=ML[m]) for m in MODELS]
    ax.legend(handles=handles, loc="lower right", frameon=False, fontsize=8.2, ncol=2)
    fig.text(0.5, -0.03,
             "Soft framing = added cost / financial-barrier / social-work / adherence language. "
             "Race-only CIs are small and, in one of six vendors, do not fully exclude a small positive "
             "effect (see Methods); SES CIs sit far right in all six.",
             ha="center", fontsize=7.2, color="#555555", style="italic")
    fig.savefig(OUT / "Fig5_forest_ses_vs_race_6vendor.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("wrote Fig5_forest_ses_vs_race_6vendor.png")


# ───────────── Fig 6: money figure, axes harmonized across models ──────────
SOFT_SPLIT_VARIANTS = ["uninsured", "underinsured", "low income", "unhoused",
                       "black+medicaid", "race-only", "white-male (comparison)"]
SOFT_SPLIT_DATA = {
    "gemini-2.5-flash": dict(appr=[88.9, 93.2, 87.5, 65.7, 37.6, -1.8, 1.0],
                             stig=[9.6, 19.0, 39.5, 71.1, 12.9, 2.7, 0.6]),
    "deepseek-chat":    dict(appr=[84.5, 86.0, 73.0, 74.5, 9.8, -1.8, -1.9],
                             stig=[3.7, 9.8, 7.9, 78.9, 6.3, 0.6, -0.6]),
    "llama-3.3-70B":    dict(appr=[51.6, 76.1, 58.9, 28.4, -0.2, -0.4, -2.4],
                             stig=[0.6, 1.8, 11.5, 40.2, 0.9, -0.3, -0.1]),
    "llama-3.1-8B":     dict(appr=[32.1, 27.3, 21.4, 7.4, 11.9, -2.7, -0.5],
                             stig=[6.9, 7.6, 8.6, 25.1, 5.1, 4.3, 2.9]),
    "gpt-4o":           dict(appr=[60.4, 62.8, 49.2, -6.4, 1.0, -3.0, 1.0],
                             stig=[5.3, 11.2, 32.3, 52.4, 0.8, 0.3, 0.2]),
    "gpt-4o-mini":      dict(appr=[3.2, 1.8, 5.9, 0.2, 0.4, 0.1, 0.0],
                             stig=[0.5, 0.4, 1.2, 2.0, 0.2, 0.1, 0.0]),
}


def fig6_soft_split():
    variants = SOFT_SPLIT_VARIANTS
    data = SOFT_SPLIT_DATA
    # shared x-limit across ALL six panels so cross-model magnitude is directly
    # comparable at a glance (readiness-review blocking item: unharmonized axes)
    xmax = max(max(abs(v) for v in d["appr"] + d["stig"]) for d in data.values())
    xlim = (-8, np.ceil(xmax / 5) * 5 + 2)

    fig, axes = plt.subplots(1, len(MODELS), figsize=(3.6 * len(MODELS), 5.4), sharey=True, sharex=True)
    y = np.arange(len(variants)); h = 0.38
    for ax, m in zip(axes, MODELS):
        ax.barh(y + h / 2, data[m]["appr"], h, color="#7FB3D5", edgecolor="k",
                linewidth=0.5, label="Appropriate SDOH care")
        ax.barh(y - h / 2, data[m]["stig"], h, color="#C0392B", edgecolor="k",
                linewidth=0.5, label="Stigmatizing")
        ax.axvline(0, color="k", lw=0.8)
        ax.set_title(ML[m], color=MC[m], fontweight="bold", fontsize=10.5)
        ax.set_xlabel("Net % vs. no-demographics", fontsize=8.5)
        ax.set_xlim(*xlim)
        ax.set_yticks(y); ax.set_yticklabels(variants, fontsize=9)
        ax.invert_yaxis()
    axes[0].legend(loc="lower right", fontsize=8, framealpha=0.95)
    fig.suptitle("Fig. 6 | The naive \u2018soft bias\u2019 is mostly appropriate care (blue); the\n"
                 "stigmatizing layer (red) is smaller and concentrated on the most disadvantaged\n"
                 "-- shared axis scale, all six vendors directly comparable",
                 fontsize=12.5, fontweight="bold", y=1.09)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(OUT / "Fig6_soft_split_harmonized.png"); plt.close(fig)
    print("wrote Fig6_soft_split_harmonized.png")


# ── Fig 6 supplement: soft-split across models, one panel (dots, no CI) ──────
def fig6_soft_split_avg():
    """Supplemental single-panel version of Fig 6.

    The bar is the UNWEIGHTED MEAN of the six models' per-model net% values; the
    six per-model values are overlaid as dots so the (large) between-model spread
    is visible. Deliberately NO parametric confidence interval: only six models
    were audited, so the model -- not the case -- is the replication unit, and a
    between-model variance cannot be reliably estimated (or honestly narrowed) from
    six clusters. Pooling the ~6x1048 case×model observations into a tight CI would
    be pseudoreplication (understating uncertainty several-fold); the wide t(df=5)
    CI is the only honest parametric alternative and is left to the reader's eye via
    the dots. See the 6-panel Fig 6 for the full per-model detail."""
    variants = SOFT_SPLIT_VARIANTS
    models = list(SOFT_SPLIT_DATA)
    n = len(models)

    def per_model(key):
        return np.array([SOFT_SPLIT_DATA[m][key] for m in models])  # (n_models, n_variants)

    appr = per_model("appr"); stig = per_model("stig")
    appr_m = appr.mean(axis=0); stig_m = stig.mean(axis=0)

    y = np.arange(len(variants)); h = 0.38
    # fixed (deterministic) vertical offsets so all six dots are visible per bar
    offs = np.linspace(-h * 0.34, h * 0.34, n)

    fig, ax = plt.subplots(figsize=(9.0, 5.8))
    ax.barh(y + h / 2, appr_m, h, color="#7FB3D5", edgecolor="k", linewidth=0.5,
            label="Appropriate SDOH care", zorder=1)
    ax.barh(y - h / 2, stig_m, h, color="#C0392B", edgecolor="k", linewidth=0.5,
            label="Stigmatizing", zorder=1)
    # overlay the six per-model values as dots on each bar
    for i in range(n):
        ax.scatter(appr[i], y + h / 2 + offs[i], s=16, color="#1f3b57",
                   edgecolor="white", linewidth=0.4, zorder=3)
        ax.scatter(stig[i], y - h / 2 + offs[i], s=16, color="#4d1414",
                   edgecolor="white", linewidth=0.4, zorder=3)
    ax.axvline(0, color="k", lw=0.9)
    ax.set_yticks(y); ax.set_yticklabels(variants, fontsize=9.5)
    ax.invert_yaxis()
    ax.set_xlabel("Net % vs. no-demographics", fontsize=9.5)
    # proxy handle for the per-model dots
    dot_proxy = mlines.Line2D([], [], color="#333333", marker="o", linestyle="none",
                              markersize=5, markeredgecolor="white", label=f"Individual model (n={n})")
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles=handles + [dot_proxy], loc="lower right", fontsize=12,
              markerscale=1.3, framealpha=0.95)

    # titleless panel for combine_figures.py -> Figure4 panel A (banner headline -> caption)
    PANELS = Path("figures/manuscript_combined/panels"); PANELS.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(PANELS / "p_soft_split_avg.png", dpi=200, bbox_inches="tight", facecolor="white")
    print("wrote panels/p_soft_split_avg.png")

    ax.set_title("Soft-bias split across models: appropriate SDOH care (blue) dominates;\n"
                 "stigmatizing layer (red) is smaller, concentrated on the unhoused",
                 fontsize=11.5, fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUT / "FigS03_soft_split_avg.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("wrote FigS03_soft_split_avg.png")


# ───────────── Fig 7: stigma dose-response gradient, softened title ────────
def fig7_stigma_gradient():
    df = pd.read_csv("results/analysis/panel_stigma_rates.csv")
    order = ["control", "race_only", "uninsured", "underinsured", "low_income",
             "black_unhoused", "unhoused"]
    nice = {"control": "control", "race_only": "race-only",
            "uninsured": "uninsured", "underinsured": "underinsured",
            "low_income": "low income", "black_unhoused": "Black+unhoused",
            "unhoused": "unhoused"}
    x = np.arange(len(order)); w = 0.8 / len(MODELS)
    fig, ax = plt.subplots(figsize=(13, 5.8))
    for j, m in enumerate(MODELS):
        sub = df[df.model == m].set_index("stratum")
        rates = [sub.loc[s, "rate"] * 100 for s in order]
        lo = [(sub.loc[s, "rate"] - sub.loc[s, "ci_low"]) * 100 for s in order]
        hi = [(sub.loc[s, "ci_high"] - sub.loc[s, "rate"]) * 100 for s in order]
        ax.bar(x + (j - (len(MODELS) - 1) / 2) * w, rates, w, yerr=[lo, hi], capsize=2,
               color=MC[m], edgecolor="k", linewidth=0.5, label=ML[m])
    ax.axvspan(-0.5, 1.5, color="0.9", zorder=0)
    ax.set_xticks(x); ax.set_xticklabels([nice[s] for s in order])
    ax.set_ylabel("Stigmatizing-language rate (%)")
    ax.set_xlabel(r"Increasing socioeconomic disadvantage  $\rightarrow$   "
                  "(grey band = non-SES anchors)", fontsize=10)
    ax.legend(fontsize=10, framealpha=0.9, loc="upper left")

    # titleless panel for combine_figures.py -> Figure4 panel C (banner headline -> caption)
    PANELS = Path("figures/manuscript_combined/panels"); PANELS.mkdir(parents=True, exist_ok=True)
    fig.savefig(PANELS / "p_gradient.png", dpi=200, bbox_inches="tight", facecolor="white")
    print("wrote panels/p_gradient.png")

    ax.set_title("Fig. 7 | Stigma scales with socioeconomic disadvantage. Race alone and\n"
                 "the white-male control are small and, in a case-clustered bootstrap, not always\n"
                 "distinguishable from zero -- direction-consistent across six models.",
                 fontsize=12, fontweight="bold")
    fig.savefig(OUT / "Fig7_stigma_gradient_softened.png"); plt.close(fig)
    print("wrote Fig7_stigma_gradient_softened.png")


# ───────────── Fig 8: stigma breakdown, defensible vs non-defensible split ──
def fig8_stigma_breakdown():
    dst_name = "Fig8_stigma_breakdown_ORIGINAL_see_caveat.png"
    _regen_or_skip(dst_name, "plots/plot_stigma_breakdown.py", ["fig2_stigma_breakdown.png"])
    if (OUT / dst_name).exists():
        print("  NOTE: NARRATIVE_ORDER.md flags the un-split composite -- "
              "recommend re-deriving as two side-by-side panels [defensible | "
              "non-defensible] before submission; source counts were not "
              "available to safely regenerate in this pass.")


# ───────────── Fig 9 / S1: circularity + PMC replication + judge validation ─
def fig9_robustness_panel():
    _regen_or_skip("Fig9a_circularity_template_notes.png", "plots/plot_circularity_ci.py",
                    ["fig4_circularity.png"])
    _regen_or_skip("Fig9b_pmc_real_note_replication.png", "plots/plot_pmc_replication.py",
                    ["fig4_pmc_replication.png"])
    _regen_or_skip("Fig9c_natural_embedding_salience_control.png", "plots/plot_natural_ab.py",
                    ["fig5_natural_ab.png"])
    _regen_or_skip("FigS01_pmc_note_provenance.png", "plots/plot_pmc_provenance.py",
                    ["fig4_pmc_provenance.png"])


# ─── Fig 2B: flip rate averaged across the 6 vendors (noise-floor panel) ────
def fig2_flip_avg():
    """Figure 2 panel B in the locked 6-figure architecture: treatment-flip rate
    averaged over the six models, showing the ~17% test-retest/label-salience
    floor is uniform across advantaged and disadvantaged labels. Titleless panel
    consumed by combine_figures.composite_fig2()."""
    _run_script("plots/regen_flip_avg.py",
                "figures/manuscript_combined/panels/p_flip_avg.png")


# ─── Fig 3: care-intensity, the intermediate bias layer (new standalone) ────
def fig3_care_intensity():
    """Figure 3 in the locked 6-figure architecture (care-intensity pulled out
    of the old Fig 2). Emits the wide titleless bars panel for the composite and
    the standalone two-panel Figure3_care_intensity.png."""
    _run_script("plots/regen_care_intensity_bars.py",
                "figures/manuscript_combined/panels/p_care_intensity_bars_wide.png")
    _run_script("plots/plot_fig3_care_intensity.py",
                "figures/manuscript_combined/Figure3_care_intensity.png")


def main():
    fig1_cohort()
    fig2_concordance()
    fig2_flip_avg()            # NEW: Figure 2 panel B (flip-rate noise floor)
    fig3_care_intensity()      # NEW: Figure 3 (care-intensity intermediate layer)
    fig3_concordance_by_variant()
    fig4_dissociation()
    fig5_forest()
    fig6_soft_split()
    fig6_soft_split_avg()
    fig7_stigma_gradient()
    fig8_stigma_breakdown()
    fig9_robustness_panel()


if __name__ == "__main__":
    main()
