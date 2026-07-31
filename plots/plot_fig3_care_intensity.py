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
})
C_HARM = "#C1272D"; C_NS = "#D9B3B2"; C_SAFE = "#6E8CA0"; C_REF = "#9E9E9E"
C_DOT = "#9AA7B0"; C_POOL = "#7A1519"

NICE = {
    "uninsured_only": "uninsured", "medicaid_only": "Medicaid", "underinsured_only": "underinsured",
    "medicare_only": "Medicare", "medicare_advantage_only": "Medicare Advantage",
    "low_income_patient": "low-income", "high_income_patient": "high-income",
    "unhoused_patient": "unhoused", "rural_patient": "rural",
    "small_community_hospital": "community hospital", "immigrant_patient": "immigrant",
    "limited_english_patient": "limited-English", "non_binary_patient": "non-binary",
    "transgender_woman": "transgender woman", "gay_male_patient": "gay male",
    "black_race_only": "Black", "hispanic_race_only": "Hispanic", "asian_race_only": "Asian",
    "native_american_race_only": "Native American", "middle_eastern_race_only": "Middle Eastern",
    "multiracial_race_only": "multiracial",
    "white_male_private": "White male private", "white_female_medicaid": "White female Medicaid",
}
# axis groups (marginalized first); race-only included so coverage matches the 29-variant design
GROUPS = [
    ("SES / housing", ["unhoused_patient", "low_income_patient"], True),
    ("Insurance", ["medicaid_only", "underinsured_only", "uninsured_only",
                   "medicare_only", "medicare_advantage_only"], True),
    ("Race / ethnicity", ["black_race_only", "hispanic_race_only", "asian_race_only",
                          "native_american_race_only", "middle_eastern_race_only",
                          "multiracial_race_only"], True),
    ("Geography", ["small_community_hospital", "rural_patient"], True),
    ("Immigration / language", ["immigrant_patient", "limited_english_patient"], True),
    ("Gender / identity", ["transgender_woman", "gay_male_patient", "non_binary_patient"], True),
    ("Privileged / advantage", ["white_male_private", "white_female_medicaid",
                                "high_income_patient"], False),
]
MARGINAL = [v for name, labs, m in GROUPS if m for v in labs]
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


def fmt_q(q):
    return "q<0.001" if q < 1e-3 else (f"q={q:.2f}" if q >= 0.01 else f"q={q:.3f}")


def panelA(ax, stats, qmap, mkey, harm_neg, title, subtitle):
    rows = [("All marginalized", ("pooled", mkey), True, None)]
    for name, labs, marg in GROUPS:
        if marg:
            rows.append((name, (name, mkey), False, qmap.get((name, mkey))))
    rows.append(("White male private", ("priv", mkey), False, None))
    y = np.arange(len(rows))[::-1]
    # harm-side shading
    if harm_neg:
        ax.axvspan(BXLIM[0], 0, color="#F6ECEC", zorder=0)
    else:
        ax.axvspan(0, BXLIM[1], color="#F6ECEC", zorder=0)
    ax.axvline(0, color="#333", lw=1.0, zorder=2)
    for yi, (lab, key, bold, q) in zip(y, rows):
        est, lo, hi, p = stats[key]
        if bold:
            col = C_POOL
        elif q is None:
            col = C_REF
        else:
            col = C_HARM if q < 0.05 else C_NS
        ax.plot([lo, hi], [yi, yi], color=col, lw=2.0, zorder=3, solid_capstyle="round")
        ax.plot(est, yi, "o", ms=6.5, color=col, zorder=4, markeredgecolor="white", mew=0.7)
        # significance label placed INSIDE the panel on the non-harm side (harm side is shaded)
        if bold:
            txt = "p<0.001" if p < 1e-3 else f"p={p:.3f}"; tc = col
        elif q is None:
            txt = "ns" if p >= 0.05 else ("p<0.001" if p < 1e-3 else f"p={p:.3f}"); tc = "#999"
        else:
            txt = fmt_q(q) if q < 0.05 else "ns"; tc = C_HARM if q < 0.05 else "#999"
        # inset 1.3 from the frame on the non-harm side so labels clear the long y-tick
        # labels (e.g. "White male, private (privileged)") and never touch the axis edge
        tx, tha = (BXLIM[1] - 1.3, "right") if harm_neg else (BXLIM[0] + 1.3, "left")
        ax.text(tx, yi, txt, va="center", ha=tha, fontsize=7.6,
                fontweight="bold" if (bold or (q is not None and q < 0.05)) else "normal", color=tc)
    ax.set_yticks(y); ax.set_yticklabels([r[0] for r in rows], fontsize=8.0)
    for lbl, r in zip(ax.get_yticklabels(), rows):
        if r[2]:
            lbl.set_fontweight("bold")
        if r[0].startswith("White male"):
            lbl.set_color("#777")
    ax.set_xlim(*BXLIM); ax.set_xticks(BXTICKS)
    ax.spines["bottom"].set_bounds(BXLIM[0], BXLIM[1])
    ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.set_xlabel("Net change vs no-demographics (pp)", fontsize=8.2)
    ax.set_title(title, fontsize=14, fontweight="bold", loc="left", pad=10)
    ax.tick_params(length=0); ax.spines[["top", "right", "left"]].set_visible(False)


def panelB(ax, df, models, mkey, harm_neg):
    seq = []
    for name, labs, marg in GROUPS:
        seq.append(("hdr", name))
        for v in labs:
            seq.append(("lab", v))
    n = len(seq); ys = {i: n - 1 - i for i in range(n)}
    jit = [(-0.20 + 0.40 * k / (len(models) - 1)) for k in range(len(models))]
    xcount = BXLIM[0] + 0.03 * (BXLIM[1] - BXLIM[0]) if harm_neg else \
        BXLIM[1] - 0.03 * (BXLIM[1] - BXLIM[0])
    hac = "left" if harm_neg else "right"
    beyond = 0; ytick, ylab = [], []
    for i, (kind, payload) in enumerate(seq):
        yv = ys[i]
        if kind == "hdr":
            ax.axhline(yv - 0.45, color="#ececec", lw=0.8, zorder=0)
            # inset the axis-group header a little so it does not touch the left axis
            ax.text(BXLIM[0] + 0.35, yv + 0.12, payload, va="center", ha="left", fontsize=7.4,
                    fontweight="bold", color="#555", style="italic")
            ytick.append(yv); ylab.append(""); continue
        vk = payload
        sub = df[df.variant == vk]
        vals = sub.set_index("model")[mkey].to_dict()
        mean = np.mean(list(vals.values()))
        is_ref = vk in ("white_male_private", "white_female_medicaid", "high_income_patient")
        in_harm = (mean < 0) if harm_neg else (mean > 0)
        colour = C_REF if is_ref else (C_HARM if in_harm else C_SAFE)
        ax.barh(yv, mean, height=0.6, color=colour, alpha=0.85, zorder=2, edgecolor="white", linewidth=0.5)
        for k, m in enumerate(models):
            if m in vals:
                beyond += (vals[m] < BXLIM[0] or vals[m] > BXLIM[1])
                ax.plot(vals[m], yv + jit[k], "o", ms=2.6, color=C_DOT, alpha=0.8, zorder=3, mew=0)
        harm = sum(1 for v in vals.values() if (v < 0 if harm_neg else v > 0))
        col = "#8E1B1B" if (harm >= 5 and not is_ref) else "#999"
        ax.text(xcount, yv, f"{harm}/{len(vals)}", ha=hac, va="center", fontsize=6.4, color=col, zorder=4)
        ytick.append(yv); ylab.append("   " + NICE.get(vk, vk))
    ax.axvline(0, color="#333", lw=0.9, zorder=4)
    ax.set_yticks(ytick); ax.set_yticklabels(ylab, fontsize=7.4)
    ax.set_xlim(*BXLIM); ax.set_xticks(BXTICKS); ax.set_ylim(-0.7, n - 0.3)
    ax.set_xlabel("Net change vs no-demographics (pp)", fontsize=8.0)
    ax.tick_params(length=0); ax.spines[["top", "right"]].set_visible(False)


def main():
    df = load()
    models = sorted(df.model.unique())
    stats, qmap = group_stats(df)
    fig = plt.figure(figsize=(13.4, 11.0))
    gs = GridSpec(2, 2, height_ratios=[1.35, 3.0], hspace=0.30, wspace=0.30,
                  left=0.17, right=0.90, top=0.93, bottom=0.055)
    for col, (title, sub, mkey, harm_neg) in enumerate(METRICS):
        panelA(fig.add_subplot(gs[0, col]), stats, qmap, mkey, harm_neg, title, sub)
        panelB(fig.add_subplot(gs[1, col]), df, models, mkey, harm_neg)
    fig.text(0.045, 0.945, "A", fontsize=20, fontweight="bold")
    fig.text(0.045, 0.60, "B", fontsize=20, fontweight="bold")
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
