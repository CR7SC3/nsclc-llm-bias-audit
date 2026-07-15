"""F1 (alt) — NCCN concordance split BY demographic label, per model, with
significance stars (exact McNemar vs the no-demographics reference, BH-FDR across
variants within each model).

Reuses the corrected-panel scorer + ground truth so numbers match correct_analysis.py.
Output -> figures/manuscript/fig1_concordance_by_variant.png

Run:  python3 plots/plot_concordance_by_variant.py
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import json
import numpy as np
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
    "limited_english_patient", "elderly_patient_75", "non_binary_patient",
    "transgender_woman", "gay_male_patient",
]
NICE = {v: v.replace("_", " ") for v in ORDER}


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
    results, ref_rates = {}, {}
    for name, path in MODELS.items():
        if not Path(path).exists():
            print("skip", name); continue
        raw = json.loads(Path(path).read_text())
        results[name], ref_rates[name] = concordance_by_variant(raw, uniq, cat_map, parser)
        # BH across variants within model
        q = benjamini_hochberg({v: results[name][v][2] for v in ORDER})
        results[name] = {v: (*results[name][v], q[v]) for v in ORDER}
        nsig = sum(1 for v in ORDER if q[v] is not None and q[v] < 0.05)
        print(f"{name}: ref={ref_rates[name]:.1f}%  significant variants (q<0.05): {nsig}")

    names = list(results.keys())
    fig, axes = plt.subplots(1, len(names), figsize=(5.2 * len(names), 8.5), sharey=True)
    if len(names) == 1:
        axes = [axes]
    y = np.arange(len(ORDER))
    for ax, name in zip(axes, names):
        rates = [results[name][v][0] for v in ORDER]
        praw = [results[name][v][2] for v in ORDER]
        lo = [rates[i] - results[name][v][3] for i, v in enumerate(ORDER)]
        hi = [results[name][v][4] - rates[i] for i, v in enumerate(ORDER)]
        qs = [results[name][v][5] for v in ORDER]
        ref = ref_rates[name]
        colors = [MC[name] if r >= ref else "#BBBBBB" for r in rates]
        ax.barh(y, rates, xerr=[lo, hi], error_kw=dict(ecolor="0.3", lw=0.9, capsize=2),
                color=colors, edgecolor="k", linewidth=0.4)
        ax.axvline(ref, color="k", ls="--", lw=1.2)
        ax.text(ref, len(ORDER) - 0.2, f" ref {ref:.0f}%", fontsize=9, va="top", color="k")
        for i, (v, qq, pr) in enumerate(zip(ORDER, qs, praw)):
            sx = results[name][v][4] + 2  # just past the upper CI bound
            if qq is not None and qq < 0.05:      # survives BH-FDR
                ax.text(sx, i, "★", va="center", fontsize=13, color="#B8860B")
            elif pr < 0.05:                         # raw-significant only
                ax.text(sx, i, "☆", va="center", fontsize=13, color="#B8860B")
        ax.set_title(name, color=MC[name], fontweight="bold")
        ax.set_xlabel("Concordance with NCCN label (%)")
        ax.set_xlim(0, 100)
    axes[0].set_yticks(y); axes[0].set_yticklabels([NICE[v] for v in ORDER], fontsize=9)
    axes[0].invert_yaxis()
    fig.suptitle("NCCN concordance by demographic label",
                 fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout(rect=(0, 0, 1, 0.99))
    fig.savefig(OUT / "fig1_concordance_by_variant.png", dpi=150, bbox_inches="tight")
    print("wrote", OUT / "fig1_concordance_by_variant.png")


if __name__ == "__main__":
    main()
