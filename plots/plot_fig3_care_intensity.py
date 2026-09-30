#!/usr/bin/env python3
"""Figure 3 (standalone): the care-intensity gradient -- the intermediate bias layer
between the invariant decision (Fig 2) and the framing/stigma signal (Figs 4-5).

The guideline-concordant DECISION does not change (Fig 2), but which options get
foregrounded shifts against marginalized patients: fewer clinical-trial mentions
(advanced treatment) and more palliative/best-supportive-care (de-escalation).

STATS (council-hardened): the inferential claim is a LINEAR MIXED-EFFECTS model with a
random intercept per model -- net_change ~ 1 + (1|model) -- so the six correlated
vendors are NOT treated as independent trials (fixes the earlier pseudo-replicated
binomial). Effects are shown as net change (pp) with 95% CI, per axis group and pooled,
BH-FDR-corrected across the axis-group family. The race-only axis is included (no silent
axis drop). Reference/control = the no_demographics neutral anchor (the 0-line);
white_male_private is a privileged comparison variant, not the reference.

Panel A = mixed-effects forest (per axis group + pooled + privileged comparator).
Panel B = per-label net change, grouped by axis (descriptive; bar = mean of 6 vendors,
dots = per-vendor, k/6 = vendors in the harm direction).
Writes figures/manuscript_combined/Figure3_care_intensity.png
"""
from pathlib import Path
import csv
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests
warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "results/analysis/advanced_care_per_model.csv"
OUT = ROOT / "figures/manuscript_combined"

plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "savefig.facecolor": "white", "axes.spines.top": False, "axes.spines.right": False,
    "mathtext.fontset": "custom", "mathtext.rm": "Helvetica", "mathtext.it": "Helvetica:italic",
})
C_HARM = "#C1272D"; C_NS = "#D9B3B2"; C_SAFE = "#6E8CA0"; C_REF = "#9E9E9E"
C_DOT = "#9AA7B0"; C_POOL = "#7A1519"

# fixed per-model palette (project-wide convention; see plot_publishable_nsclc.py /
# plot_concordance_by_variant.py / plot_restricted_attrition.py -- reused verbatim, not invented)
MODEL_ORDER = ["gemini-2.5-flash", "deepseek-chat", "llama-3.3-70B",
               "llama-3.1-8B", "gpt-4o", "gpt-4o-mini"]
MC = {"gemini-2.5-flash": "#4C72B0", "deepseek-chat": "#C44E52", "llama-3.3-70B": "#55A868",
      "llama-3.1-8B": "#937860", "gpt-4o": "#8172B3", "gpt-4o-mini": "#CCB974"}
ML = {"gemini-2.5-flash": "Gemini-2.5-flash", "deepseek-chat": "DeepSeek-chat",
      "llama-3.3-70B": "Llama-3.3-70B", "llama-3.1-8B": "Llama-3.1-8B",
      "gpt-4o": "GPT-4o", "gpt-4o-mini": "GPT-4o-mini"}

NICE = {   # display names match Figure 1 (regen_flip_avg.py / plot_flip_direction_heatmap.py)
    "uninsured_only": "Uninsured", "medicaid_only": "Medicaid", "underinsured_only": "Underinsured",
    "medicare_only": "Medicare", "medicare_advantage_only": "Medicare Advantage",
    "low_income_patient": "Low income", "high_income_patient": "High income",
    "unhoused_patient": "Unhoused", "rural_patient": "Rural",
    "small_community_hospital": "Small community hospital", "immigrant_patient": "Immigrant",
    "limited_english_patient": "Limited English", "non_binary_patient": "Non-binary",
    "transgender_woman": "Transgender woman", "gay_male_patient": "Gay male",
    "black_race_only": "Black", "hispanic_race_only": "Hispanic", "asian_race_only": "Asian",
    "native_american_race_only": "Native American", "middle_eastern_race_only": "Middle Eastern",
    "multiracial_race_only": "Multiracial",
    "low_income_black": "Low income, Black", "black_unhoused": "Black + unhoused",
    "black_female_medicaid": "Black female, Medicaid",
    "latina_female_uninsured": "Hispanic female, uninsured",
    "white_male_private": "White male, private", "white_female_medicaid": "White female, Medicaid",
    "black_female_private": "Black female, private",
}
# Same 9 categories and order as Figure 1. Third field: True = single-axis marginalized
# group entering the mixed-effects family (panel A, 20 labels); None = panel B only
# (multi-axis labels, not in the model); False = comparator.
GROUPS = [
    ("Income / housing", ["unhoused_patient", "low_income_patient"], True),
    ("Insurance", ["medicaid_only", "underinsured_only", "uninsured_only",
                   "medicare_only", "medicare_advantage_only"], True),
    ("Race + disadvantage", ["low_income_black", "black_unhoused", "black_female_medicaid",
                             "latina_female_uninsured"], None),
    ("Race / ethnicity only", ["black_race_only", "hispanic_race_only", "asian_race_only",
                               "native_american_race_only", "middle_eastern_race_only",
                               "multiracial_race_only"], True),
    ("Geography", ["small_community_hospital", "rural_patient"], True),
    ("Immigration / language", ["immigrant_patient", "limited_english_patient"], True),
    ("Gender / sexual identity", ["transgender_woman", "gay_male_patient", "non_binary_patient"], True),
    ("Matched counterexamples", ["black_female_private", "white_female_medicaid"], False),
    ("Privileged comparators", ["white_male_private", "high_income_patient"], False),
]
_K = [v for _, labs, _ in GROUPS for v in labs]
assert len(_K) == 28 and len(set(_K)) == 28
COMPARATORS = {v for _, labs, m in GROUPS if m is False for v in labs}
MARGINAL = [v for name, labs, m in GROUPS if m for v in labs]
assert len(MARGINAL) == 20
PRIV_REF = "white_male_private"
METRICS = [("Advanced treatment", "clinical-trial mention", "ct", True),
           ("De-escalation", "palliative / best-supportive-care", "pall", False)]
BXLIM = (-6.0, 8.0); BXTICKS = [-6, -4, -2, 0, 2, 4, 6, 8]


def load():
    rows = list(csv.DictReader(open(SRC)))
    return pd.DataFrame([{"variant": r["variant"], "model": r["model"],
                          "ct": float(r["ct_net"]), "pall": float(r["pall_net"])} for r in rows])


def mixed(df, labels, metric):
    """net ~ 1 + (1|model): returns (estimate pp, lo, hi, p).
    For a single variant (1 obs per model -> random effect unidentifiable) fall back to a
    one-sample t on the per-model values."""
    sub = df[df.variant.isin(labels)]
    if sub.model.nunique() < 2 or len(sub) < 3:
        return (np.nan,) * 4
    if len(labels) == 1:                      # single-variant comparator: one-sample t
        from scipy.stats import t as tdist
        v = sub[metric].values
        m, se, k = v.mean(), v.std(ddof=1) / np.sqrt(len(v)), len(v)
        tc = tdist.ppf(0.975, k - 1)
        p = tdist.sf(abs(m / se), k - 1) * 2 if se > 0 else 1.0
        return m, m - tc * se, m + tc * se, p
    md = smf.mixedlm(f"{metric} ~ 1", data=sub, groups=sub["model"]).fit()
    ci = md.conf_int().loc["Intercept"]
    return md.params["Intercept"], ci[0], ci[1], md.pvalues["Intercept"]


def group_stats(df):
    """Mixed-effects estimate/CI/p per marginalized axis group + pooled + privileged; BH-FDR q."""
    out = {}
    fam_keys, fam_p = [], []
    for mkey, metric, harm_neg in [("ct", "ct", True), ("pall", "pall", False)]:
        out[("pooled", mkey)] = mixed(df, MARGINAL, metric)
        out[("priv", mkey)] = mixed(df, [PRIV_REF], metric)
        for name, labs, marg in GROUPS:
            if not marg:
                continue
            est, lo, hi, p = mixed(df, labs, metric)
            out[(name, mkey)] = (est, lo, hi, p)
            fam_keys.append((name, mkey)); fam_p.append(p)
    q = multipletests(fam_p, alpha=0.05, method="fdr_bh")[1]
    qmap = {k: qv for k, qv in zip(fam_keys, q)}
    return out, qmap


def fmt_stat(letter, v):
    """AMA style: capital letter, spaced '=', no leading zero (e.g. 'P = .002', 'q = .02')."""
    if v < 1e-3:
        return f"${letter}$ < .001"
    dec = 2 if v >= 0.01 else 3
    s = f"{v:.{dec}f}".lstrip("0")
    return f"${letter}$ = {s}"


def panelA(ax, df, models, stats, qmap, mkey, harm_neg, title, subtitle):
    """Mixed-effects forest plot: one horizontal row per axis-group category, each
    showing (1) the pooled mixed-effects estimate as a dot + 95% CI line (primary
    encoding) and (2) six small semi-transparent per-model mean dots jittered
    vertically within the row (secondary encoding, same jitter pattern as panelB's
    `jit` list), so a reader sees both the formal pooled effect and which model(s)
    drive the spread without connecting unordered categories with lines."""
    rows = [("All marginalized", ("pooled", mkey), True, None, MARGINAL)]
    for name, labs, marg in GROUPS:
        if marg:
            rows.append((name, (name, mkey), False, qmap.get((name, mkey)), labs))
    rows.append(("White male, private", ("priv", mkey), False, None, [PRIV_REF]))
    y = np.arange(len(rows))[::-1]

    # harm-side shading (vertical bands -- original forest-plot convention)
    if harm_neg:
        ax.axvspan(BXLIM[0], 0, color="#F6ECEC", zorder=0)
    else:
        ax.axvspan(0, BXLIM[1], color="#F6ECEC", zorder=0)
    ax.axvline(0, color="#333", lw=1.0, zorder=2)

    # vertical jitter offsets for the six per-model dots within a row (same construction
    # as panelB's `jit`, adapted from a horizontal bar-row jitter to a forest-row jitter)
    jit = [(-0.20 + 0.40 * k / (len(models) - 1)) for k in range(len(models))]

    for ri, (yi, (lab, key, bold, q, labs)) in enumerate(zip(y, rows)):
        est, lo, hi, p = stats[key]
        if bold:
            col = C_POOL
        elif q is None:
            col = C_REF
        else:
            col = C_HARM if q < 0.05 else C_NS

        # secondary encoding: each model's own mean over the variants in this row,
        # jittered vertically so all six are visible without overlapping (labelled
        # only once, on the first row, so the shared legend gets one entry per model)
        for k, m in enumerate(models):
            sub = df[(df.model == m) & (df.variant.isin(labs))]
            if len(sub):
                mval = sub[mkey].mean()
                ax.plot(mval, yi + jit[k], "o", ms=5.5, color=MC.get(m, "#999"),
                         alpha=0.55, zorder=3, mew=0,
                         label=(ML.get(m, m) if ri == 0 else None))

        # primary encoding: pooled mixed-effects estimate + 95% CI
        ax.plot([lo, hi], [yi, yi], color=col, lw=2.0, zorder=4, solid_capstyle="round")
        ax.plot(est, yi, "o", ms=8.5, color=col, zorder=5, markeredgecolor="white", mew=0.7,
                 label=("Pooled (mixed-effects)" if bold else None))

        # significance label placed INSIDE the panel on the non-harm side (harm side shaded)
        if bold:
            txt = fmt_stat("P", p); tc = col
        elif q is None:
            txt = fmt_stat("P", p); tc = "#999"
        else:
            txt = fmt_stat("q", q); tc = C_HARM if q < 0.05 else "#999"
        tx, tha = (BXLIM[1] - 1.3, "right") if harm_neg else (BXLIM[0] + 1.3, "left")
        ax.text(tx, yi, txt, va="center", ha=tha, fontsize=11,
                 fontweight="bold" if (bold or (q is not None and q < 0.05)) else "normal",
                 color=tc, zorder=6)

    ax.set_yticks(y); ax.set_yticklabels([r[0] for r in rows], fontsize=12)
    ax.tick_params(axis="x", labelsize=11)
    for lbl, r in zip(ax.get_yticklabels(), rows):
        if r[2]:
            lbl.set_fontweight("bold")
        if r[0].startswith("White male"):
            lbl.set_color("#777")
    ax.set_xlim(*BXLIM); ax.set_xticks(BXTICKS)
    ax.spines["bottom"].set_bounds(BXLIM[0], BXLIM[1])
    ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.set_xlabel("Net change vs reference (pp)", fontsize=12)
    ax.set_title(title, fontsize=15, fontweight="bold", loc="left", pad=10)
    ax.tick_params(length=0); ax.spines[["top", "right", "left"]].set_visible(False)


def panelB(ax, df, models, mkey, harm_neg, title):
    seq = []
    for name, labs, marg in GROUPS:
        seq.append(("hdr", name))
        for v in labs:
            seq.append(("lab", v))
    n = len(seq); ys = {i: n - 1 - i for i in range(n)}
    jit = [(-0.20 + 0.40 * k / (len(models) - 1)) for k in range(len(models))]
    # k/6 counts sit just outside the right edge of the axes, clear of the model dots
    ctrans = ax.get_yaxis_transform()
    beyond = 0; ytick, ylab = [], []
    for i, (kind, payload) in enumerate(seq):
        yv = ys[i]
        if kind == "hdr":
            if i > 0:
                ax.axhline(yv + 0.55, color="#dddddd", lw=0.8, zorder=0)
            ax.text(BXLIM[0] + 0.2, yv - 0.05, payload, va="center", ha="left", fontsize=10.5,
                    fontweight="bold", color="#555", style="italic")
            ytick.append(yv); ylab.append(""); continue
        vk = payload
        sub = df[df.variant == vk]
        vals = sub.set_index("model")[mkey].to_dict()
        mean = np.mean(list(vals.values()))
        is_ref = vk in COMPARATORS
        in_harm = (mean < 0) if harm_neg else (mean > 0)
        colour = C_REF if is_ref else (C_HARM if in_harm else C_SAFE)
        ax.barh(yv, mean, height=0.6, color=colour, alpha=0.85, zorder=2, edgecolor="white", linewidth=0.5)
        for k, m in enumerate(models):
            if m in vals:
                beyond += (vals[m] < BXLIM[0] or vals[m] > BXLIM[1])
                ax.plot(vals[m], yv + jit[k], "o", ms=3.8, color=MC.get(m, C_DOT), alpha=0.8,
                        zorder=3, mew=0)
        harm = sum(1 for v in vals.values() if (v < 0 if harm_neg else v > 0))
        col = "#8E1B1B" if (harm >= 5 and not is_ref) else "#999"
        ax.text(1.015, yv, f"{harm}/{len(vals)}", transform=ctrans, ha="left", va="center",
                fontsize=10, color=col, fontweight="bold" if col != "#999" else "normal",
                zorder=4, clip_on=False)
        ytick.append(yv); ylab.append(NICE.get(vk, vk))
    ax.axvline(0, color="#333", lw=0.9, zorder=4)
    ax.set_yticks(ytick); ax.set_yticklabels(ylab, fontsize=11)
    ax.tick_params(axis="x", labelsize=11)
    ax.set_xlim(*BXLIM); ax.set_xticks(BXTICKS); ax.set_ylim(-0.7, n - 0.3)
    ax.set_xlabel("Net change vs reference (pp)", fontsize=12)
    ax.set_title(f"{title}, by label", fontsize=13, fontweight="bold", loc="left", pad=8)
    ax.tick_params(length=0); ax.spines[["top", "right"]].set_visible(False)


def main():
    df = load()
    present = set(df.model.unique())
    models = [m for m in MODEL_ORDER if m in present] + \
        sorted(present - set(MODEL_ORDER))  # any unrecognized model still gets plotted
    stats, qmap = group_stats(df)
    fig = plt.figure(figsize=(14.0, 17.0))
    gs = GridSpec(2, 2, height_ratios=[1.35, 3.4], hspace=0.14, wspace=0.62,
                  left=0.12, right=0.95, top=0.93, bottom=0.04)
    axesA = []
    for col, (title, sub, mkey, harm_neg) in enumerate(METRICS):
        axA = fig.add_subplot(gs[0, col])
        panelA(axA, df, models, stats, qmap, mkey, harm_neg, title, sub)
        axB = fig.add_subplot(gs[1, col])
        panelB(axB, df, models, mkey, harm_neg, title)
        axesA.append(axA)
    handles, labels = axesA[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=len(handles), frameon=False,
               fontsize=12, bbox_to_anchor=(0.5, 0.985), handlelength=1.8, columnspacing=1.3)
    fig.text(0.015, axesA[0].get_position().y1 + 0.012, "A", fontsize=24, fontweight="bold")
    fig.text(0.015, axB.get_position().y1 + 0.012, "B", fontsize=24, fontweight="bold")
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / "Figure3_care_intensity.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    from PIL import Image
    w, h = Image.open(out).size
    print(f"wrote {out}  {w}x{h}")
    for title, sub, mkey, harm_neg in METRICS:
        est, lo, hi, p = stats[("pooled", mkey)]
        print(f"  {title:20s} pooled mixed-effects {est:+.2f}pp [{lo:.2f},{hi:.2f}] p={p:.4f}")


if __name__ == "__main__":
    main()
