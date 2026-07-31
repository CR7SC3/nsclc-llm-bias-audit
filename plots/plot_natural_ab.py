"""Natural-embedding A/B RESULT — is the stigma gradient a salience artifact?

Salience-artifact control (methods M4). On the SAME 150 cases, demographics are
injected two ways: as a bracketed metadata TAG ('[PATIENT DEMOGRAPHICS: ...]',
the main-pipeline default) vs woven into the note as deterministic natural PROSE
(no LLM; src/generate/natural_embed.py splices the descriptor after the
"NN-year-old" HPI opening). If the disadvantaged >> control gradient survives
natural embedding, the effect is NOT label-following on the salient tag.

Stigma composite reuses finalize_panel (adherence-doubt OR hallucinated SDOH);
error bars = 95% Wilson CI. Two vendor panels (Gemini, DeepSeek).

Output -> figures/manuscript/fig5_natural_ab.png (+ .pdf)
Run:  python3 plots/plot_natural_ab.py
"""
from __future__ import annotations

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import json
import numpy as np
import matplotlib.pyplot as plt

from scripts.nsclc.finalize_panel import STRATA, _is_stigma, _wilson

# Unified typography across all Fig-5 panels (A/B/C/D): one family, one size.
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans"],
    "font.size": 10,
})

OUT = Path("figures/manuscript"); OUT.mkdir(parents=True, exist_ok=True)
# Shared note-type palette across the Fig 9 robustness panels (9a/9b/9c) so each
# note source reads as its own colour; vendor stays encoded by panel + title.
NOTE_COLORS = {
    "synthetic": "#adadad",   # gray baseline — original bracketed-TAG note (shared across panels)
    "template":  "#8E6CAE",   # purple — circularity control (template notes)
    "real":      "#E8833A",   # orange — real PubMed Central notes
    "prose":     "#E69F00",   # orange — robustness condition (non-model palette; was purple -> clashed with GPT-4o)
}

# (vendor label, color, TAG results file, NATURAL results file)
ARMS = {
    "Gemini": ("#4C72B0",
               "results/baseline/v2_genie_bpc_nsclc_results.json",
               "results/baseline/v2_genie_bpc_nsclc_natural150_results.json"),
    "DeepSeek": ("#C44E52",
                 "results/baseline/v2_genie_bpc_nsclc_deepseek-chat_results.json",
                 "results/baseline/v2_genie_bpc_nsclc_natural150_deepseek-chat_results.json"),
}

# disadvantage-ordered; the gradient claim = disadvantaged >> control
ORDER = ["control", "race_only", "uninsured", "underinsured", "low_income",
         "black_unhoused", "unhoused"]
PRETTY = {"control": "control", "race_only": "race-only", "uninsured": "uninsured",
          "underinsured": "underinsured", "low_income": "low income",
          "black_unhoused": "Black + unhoused", "unhoused": "unhoused"}


def _rates(path: str, case_ids: set | None):
    """Per-stratum (k, n) stigma counts. If case_ids given, restrict to them
    (pairs the full TAG arm down to the 150 natural case_ids)."""
    d = json.loads(Path(path).read_text())
    if case_ids is not None:
        d = {c: v for c, v in d.items() if c in case_ids}
    out = {}
    for stratum, vks in STRATA.items():
        k = n = 0
        for cres in d.values():
            for vk in vks:
                r = cres.get(vk)
                if isinstance(r, dict) and r.get("response_text"):
                    n += 1
                    k += _is_stigma(r["response_text"])
        out[stratum] = (k, n)
    return out, set(d.keys())


def main():
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.4), sharey=True)
    x = np.arange(len(ORDER)); w = 0.38

    for ax, (vendor, (color, tag_path, nat_path)) in zip(axes, ARMS.items()):
        nat, nat_ids = _rates(nat_path, None)
        tag, _ = _rates(tag_path, nat_ids)  # pair TAG down to the same 150 cases

        def series(counts):
            r, lo, hi = [], [], []
            for s in ORDER:
                k, n = counts[s]
                p, l, h = _wilson(k, n)
                r.append(100 * p); lo.append(100 * (p - l)); hi.append(100 * (h - p))
            return r, np.clip(lo, 0, None), np.clip(hi, 0, None)

        tag_r, tag_lo, tag_hi = series(tag)
        nat_r, nat_lo, nat_hi = series(nat)

        ax.bar(x - w / 2, tag_r, w, yerr=[tag_lo, tag_hi],
               error_kw=dict(ecolor="0.3", lw=0.9, capsize=2),
               color=NOTE_COLORS["synthetic"], edgecolor="k", linewidth=0.5,
               label="Bracketed TAG")
        ax.bar(x + w / 2, nat_r, w, yerr=[nat_lo, nat_hi],
               error_kw=dict(ecolor="0.3", lw=0.9, capsize=2),
               color=NOTE_COLORS["prose"], edgecolor="k", linewidth=0.5,
               label="Natural PROSE")

        ax.set_xticks(x); ax.set_xticklabels([PRETTY[s] for s in ORDER], rotation=30, ha="right", rotation_mode="anchor")   # standardized 30° tilt
        ax.legend(framealpha=0.95, loc="upper left")   # standardized: framed, inherits unified 10 pt (match panel A)
        ax.set_ylim(0, 100)
        ax.grid(axis="y", alpha=0.25); ax.set_axisbelow(True)   # grey gridlines behind bars (match panels A/B/D)

    axes[0].set_ylabel("Stigmatizing-language rate (%)")
    # titleless panel for combine_figures.py (Fig 5C); banner/suptitle goes to the caption.
    # Fixed geometry so all Fig-5 panels share one height and their x-axes align
    # (two-axis box, same bottom/top as the single-axis panels). No tight bbox.
    PANELS = Path("figures/manuscript_combined/panels"); PANELS.mkdir(parents=True, exist_ok=True)
    fig.set_size_inches(13.2, 5.2)
    axes[0].set_position([0.055, 0.16, 0.43, 0.78])
    axes[1].set_position([0.545, 0.16, 0.43, 0.78])
    fig.savefig(PANELS / "p_natural.png", dpi=200)
    fig.set_size_inches(13, 5.4)
    fig.suptitle("The stigma gradient is not a salience artifact\n"
                 "Bracketed demographic TAG vs. demographics woven into prose, "
                 "same 150 cases (95% Wilson CI)",
                 fontsize=12, fontweight="bold", y=1.02)
    fig.tight_layout(rect=(0, 0, 1, 0.98))
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"fig5_natural_ab.{ext}", dpi=150, bbox_inches="tight")
        print("wrote", OUT / f"fig5_natural_ab.{ext}")

    # echo the numbers
    for vendor, (_, tag_path, nat_path) in ARMS.items():
        nat, nat_ids = _rates(nat_path, None)
        tag, _ = _rates(tag_path, nat_ids)
        print(f"\n{vendor} (paired n={len(nat_ids)}):  {'stratum':14s} {'TAG%':>6s} {'PROSE%':>7s}  Δpp")
        for s in ORDER:
            pt, _, _ = _wilson(*tag[s]); pn, _, _ = _wilson(*nat[s])
            print(f"  {'':13s} {s:14s} {100*pt:5.1f} {100*pn:6.1f}  {100*(pn-pt):+5.1f}")


if __name__ == "__main__":
    main()
