"""F1 (alt) — NCCN concordance split BY demographic label, per model, with
significance stars (exact McNemar vs the no-demographics reference, BH-FDR across
variants within each model).

Reuses the corrected-panel scorer + ground truth so numbers match correct_analysis.py.
Output -> figures/manuscript/FigS07_concordance_by_variant.png

Run:  python3 plots/plot_concordance_by_variant.py
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import binomtest

from src.analyze.response_parser import ResponseParser
from src.evaluate.nccn_scorer import get_nccn_answer
from src.evaluate.concordance_checker import nccn_answer_to_category
from src.analyze.stats import benjamini_hochberg, wilson_ci

CASES_PATH = "data/processed/genie_bpc_nsclc_with_notes.json"
REFERENCE = "no_demographics"
OUT = Path("figures/manuscript"); OUT.mkdir(parents=True, exist_ok=True)

MODELS = {
    "Gemini-2.5-flash": "results/baseline/v2_genie_bpc_nsclc_results.json",
    "DeepSeek-chat":    "results/baseline/v2_genie_bpc_nsclc_deepseek-chat_results.json",
    "Llama-3.3-70B":    "results/baseline/v2_genie_bpc_nsclc_meta-llama-Llama-3.3-70B-Instruct-Turbo_results.json",
    "Llama-3.1-8B":     "results/baseline/v2_genie_bpc_nsclc_openrouter-meta-llama-llama-3.1-8b-instruct_results.json",
    "GPT-4o":           "results/baseline/v2_genie_bpc_nsclc_gpt-4o_results.json",
    "GPT-4o-mini":      "results/baseline/v2_genie_bpc_nsclc_gpt-4o-mini_results.json",
}
MC = {"Gemini-2.5-flash": "#4C72B0", "DeepSeek-chat": "#C44E52", "Llama-3.3-70B": "#55A868",
      "Llama-3.1-8B": "#937860", "GPT-4o": "#8172B3", "GPT-4o-mini": "#CCB974"}

# fixed variant order (grouped): controls -> race-only -> SES/insurance -> housing/other
ORDER = [
    "white_male_private", "black_race_only", "hispanic_race_only", "asian_race_only",
    "native_american_race_only", "middle_eastern_race_only", "multiracial_race_only",
    "uninsured_only", "underinsured_only", "medicaid_only", "medicare_only",
    "medicare_advantage_only", "low_income_patient", "high_income_patient",
    "black_female_medicaid", "latina_female_uninsured", "black_female_private",
    "white_female_medicaid", "low_income_black", "black_unhoused", "unhoused_patient",
    "rural_patient", "small_community_hospital", "immigrant_patient",
    "limited_english_patient", "non_binary_patient",
    "transgender_woman", "gay_male_patient",
]
NICE = {
    "white_male_private": "White male, private",
    "black_race_only": "Black", "hispanic_race_only": "Hispanic",
    "asian_race_only": "Asian", "native_american_race_only": "Native American",
    "middle_eastern_race_only": "Middle Eastern", "multiracial_race_only": "Multiracial",
    "uninsured_only": "Uninsured", "underinsured_only": "Underinsured",
    "medicaid_only": "Medicaid", "medicare_only": "Medicare",
    "medicare_advantage_only": "Medicare Advantage", "low_income_patient": "Low income",
    "high_income_patient": "High income",
    "black_female_medicaid": "Black female, Medicaid",
    "latina_female_uninsured": "Hispanic female, uninsured",
    "black_female_private": "Black female, private",
    "white_female_medicaid": "White female, Medicaid",
    "low_income_black": "Low income, Black", "black_unhoused": "Black + unhoused",
    "unhoused_patient": "Unhoused", "rural_patient": "Rural",
    "small_community_hospital": "Small community hospital",
    "immigrant_patient": "Immigrant", "limited_english_patient": "Limited English",
    "non_binary_patient": "Non-binary", "transgender_woman": "Transgender woman",
    "gay_male_patient": "Gay male",
}


def build_ground_truth():
    cases = json.loads(Path(CASES_PATH).read_text())
    cases = cases if isinstance(cases, list) else list(cases.values())
    uniq, cat_map = set(), {}
    for c in cases:
        cid = c["case_id"]
        try:
            nccn = get_nccn_answer(c.get("clinical_profile", c))
            acc = nccn.get("acceptable_answers") or [nccn.get("primary_answer")]
            cats = set(filter(None, (nccn_answer_to_category(a) for a in acc)))
            if len(cats) == 1:
                uniq.add(cid); cat_map[cid] = next(iter(cats))
        except Exception:
            pass
    return uniq, cat_map


LAST_REF = [None]


def concordance_by_variant(raw, uniq, cat_map, parser):
    """Return {variant: (rate%, n, p_vs_ref)} and reference rate%."""
    # per-case correctness: cid -> {variant: bool}
    ref_correct, ref_n = 0, 0
    correct = {v: 0 for v in ORDER}
    total = {v: 0 for v in ORDER}
    b = {v: 0 for v in ORDER}  # ref-correct, var-wrong
    cc = {v: 0 for v in ORDER}  # var-correct, ref-wrong
    for cid in uniq:
        if cid not in raw:
            continue
        exp = cat_map[cid]
        rt = raw[cid].get(REFERENCE, {}).get("response_text", "")
        rcat = parser.parse(rt).category if rt else "unknown"
        r_ok = (rcat == exp) if rcat != "unknown" else None
        if r_ok is not None:
            ref_n += 1; ref_correct += int(r_ok)
        for v in ORDER:
            vv = raw[cid].get(v, {})
            cat = parser.parse(vv.get("response_text", "")).category
            if cat == "unknown":
                continue
            v_ok = (cat == exp)
            total[v] += 1; correct[v] += int(v_ok)
            if r_ok is not None and v_ok != r_ok:  # discordant pair
                if r_ok and not v_ok:
                    b[v] += 1
                elif v_ok and not r_ok:
                    cc[v] += 1
    ref_rate = 100 * ref_correct / ref_n if ref_n else 0
    LAST_REF[0] = (ref_correct, ref_n)   # for the reference CI band (signature unchanged)
    out = {}
    for v in ORDER:
        rate = 100 * correct[v] / total[v] if total[v] else 0
        lo, hi = wilson_ci(correct[v], total[v]) if total[v] else (0, 0)
        nb, ncv = b[v], cc[v]
        p = binomtest(nb, nb + ncv, 0.5).pvalue if (nb + ncv) else 1.0
        out[v] = (rate, total[v], p, 100 * lo, 100 * hi)
    return out, ref_rate


def main():
    uniq, cat_map = build_ground_truth()
    parser = ResponseParser()
    results, ref_rates, ref_cis = {}, {}, {}
    for name, path in MODELS.items():
        if not Path(path).exists():
            print("skip", name); continue
        raw = json.loads(Path(path).read_text())
        results[name], ref_rates[name] = concordance_by_variant(raw, uniq, cat_map, parser)
        ref_cis[name] = wilson_ci(*LAST_REF[0])
        # BH across variants within model
        q = benjamini_hochberg({v: results[name][v][2] for v in ORDER})
        results[name] = {v: (*results[name][v], q[v]) for v in ORDER}
        nsig = sum(1 for v in ORDER if q[v] is not None and q[v] < 0.05)
        print(f"{name}: ref={ref_rates[name]:.1f}%  significant variants (q<0.05): {nsig}")

    names = list(results.keys())
    # rows grouped into Figure 1's 9 categories (same order/colours as eFigure 4)
    from plots.plot_concordance_by_variant_avg import GROUPS
    rows, ycol, spans = [], [], []
    for gname, keys, col in GROUPS:
        spans.append((gname, len(rows), len(rows) + len(keys), col))
        rows += keys; ycol += [col] * len(keys)
    assert sorted(rows) == sorted(ORDER)
    plt.rcParams.update({"font.family": "sans-serif",
                         "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"]})
    fig, axes = plt.subplots(2, 3, figsize=(10.0, 13.0), sharey=True)
    y = np.arange(len(rows))
    for ax, name in zip(axes.flat, names):
        ref = ref_rates[name]; rlo, rhi = ref_cis[name]
        ax.axvspan(100 * rlo, 100 * rhi, color="0.88", zorder=0)
        ax.axvline(ref, color="k", ls="--", lw=1.0, zorder=1)
        for i, v in enumerate(rows):
            rate, _, pr, lo, hi, qq = results[name][v]
            ax.errorbar(rate, i, xerr=[[rate - lo], [hi - rate]], fmt="o", ms=5.5,
                        color=ycol[i], ecolor=ycol[i], elinewidth=1.1, capsize=2,
                        markeredgecolor="white", markeredgewidth=0.5, zorder=3)
            if qq is not None and qq < 0.05:
                ax.plot(hi + 1.2, i, marker="*", ms=11, color="k", zorder=4)
            elif pr < 0.05:
                ax.plot(hi + 1.0, i, marker="o", ms=3.8, color="k", zorder=4)
        for _, s0, _, _ in spans:
            if s0:
                ax.axhline(s0 - 0.5, color="#cccccc", lw=0.7, zorder=0)
        ax.set_xlim(ref - 14, min(ref + 14, 100.5))
        ax.set_title(f"{name}\nreference {ref:.1f}%", fontsize=12, fontweight="bold")
        ax.tick_params(axis="x", labelsize=10.5); ax.tick_params(axis="y", length=0)
        ax.xaxis.grid(True, ls=":", alpha=0.5); ax.set_axisbelow(True)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    for ax in axes[1]:
        ax.set_xlabel("NCCN guideline concordance (%)", fontsize=11.5)
    for ax in axes[:, 0]:
        ax.set_yticks(y); ax.set_yticklabels([NICE[v] for v in rows], fontsize=10.5)
        for t, col in zip(ax.get_yticklabels(), ycol):
            t.set_color(col)
    axes[0, 0].set_ylim(len(rows) - 0.4, -0.6)
    fig.tight_layout(h_pad=2.0)
    fig.savefig(OUT / "FigS07_concordance_by_variant.png", dpi=200, bbox_inches="tight")
    print("wrote", OUT / "FigS07_concordance_by_variant.png")
    for name in names:
        hits = [(v, round(results[name][v][0], 1), round(results[name][v][2], 4), results[name][v][5])
                for v in ORDER if results[name][v][2] < 0.05]
        print(f"  {name}: ref {ref_rates[name]:.1f}%  P<.05: {len(hits)}  "
              + "; ".join(f"{v} {r}% P={p} q={q if q is None else round(q,3)}" for v, r, p, q in hits))

if __name__ == "__main__":
    main()
