"""Poster panel: PMC real-note replication, styled to match p_template.png /
poster_figures/6_template_control.png exactly (same figsize, dpi, palette,
hatch convention, legend style).

Control/reference row = no_demographics ONLY (locked convention: no_demographics
is the definitional zero anchor, not white_male_private, in every plot
including this one).

Series: color = note source (gray = synthetic GENIE cohort, orange = real PMC
case reports), hatch = model (solid = Gemini, hatched = DeepSeek).

Output -> figures/manuscript_combined/panels/p_pmc_poster.png
       -> poster_figures/7_pmc_replication.png (via build_poster_figures.py step, or directly here)
Run:  python3 plots/plot_pmc_replication_poster.py
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import json
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

from src.analyze.soft_bias import detect_all
from src.analyze.stats import wilson_ci

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans"],
    "font.size": 10,
})

STIGMA = ("adherence_compliance", "sdoh_generation")

# stratum -> variant keys. control = no_demographics ONLY (locked convention).
STRATA = {
    "control":    ["no_demographics"],
    "race-only":  ["black_race_only", "hispanic_race_only", "asian_race_only",
                   "native_american_race_only", "middle_eastern_race_only",
                   "multiracial_race_only"],
    "uninsured":  ["uninsured_only"],
    "low income": ["low_income_patient"],
    "unhoused":   ["unhoused_patient"],
}

SYN = {"Gemini":   "results/baseline/v2_genie_bpc_nsclc_checkpoint.json",
       "DeepSeek": "results/baseline/v2_genie_bpc_nsclc_deepseek-chat_checkpoint.json"}
PMC = {"Gemini":   "results/baseline/v2_pmc_nsclc_results.json",
       "DeepSeek": "results/baseline/v2_pmc_nsclc_deepseek-chat_results.json"}


def rate_from_case_dict(raw, vkeys):
    """raw: {case_id: {variant_key: {response_text: ...}}}"""
    k = n = 0
    for cid, cd in raw.items():
        for vk in vkeys:
            r = cd.get(vk)
            txt = r.get("response_text", "") if isinstance(r, dict) else ""
            if not txt:
                continue
            n += 1
            if any(detect_all(txt).get(d) for d in STIGMA):
                k += 1
    lo, hi = wilson_ci(k, n) if n else (0, 0)
    return 100 * k / n if n else 0, 100 * lo, 100 * hi, n


def main():
    labels = list(STRATA.keys())
    x = np.arange(len(labels)); w = 0.2

    data = {}
    for model in ("Gemini", "DeepSeek"):
        syn_raw = json.loads(Path(SYN[model]).read_text())
        pmc_raw = json.loads(Path(PMC[model]).read_text())
        data[model] = {}
        for s in labels:
            data[model][s] = {
                "synthetic": rate_from_case_dict(syn_raw, STRATA[s]),
                "real":      rate_from_case_dict(pmc_raw, STRATA[s]),
            }
        for s in labels:
            syn_r = data[model][s]["synthetic"]
            real_r = data[model][s]["real"]
            print(f"{model:9s} {s:12s} synthetic {syn_r[0]:5.1f}% [{syn_r[1]:.1f},{syn_r[2]:.1f}] n={syn_r[3]:5d}   "
                  f"real {real_r[0]:5.1f}% [{real_r[1]:.1f},{real_r[2]:.1f}] n={real_r[3]:3d}")

    fig, ax = plt.subplots(figsize=(9.8, 5.2))
    # Match 6_template_control.png convention: color = note source, hatch = model.
    C_MAIN, C_ALT = "#adadad", "#E69F00"   # grey = synthetic note · orange = real PMC note
    specs = [("Gemini", "synthetic", C_MAIN, "", "Gemini · synthetic", -1.5),
             ("Gemini", "real",      C_ALT,  "", "Gemini · real PMC", -0.5),
             ("DeepSeek", "synthetic", C_MAIN, "////", "DeepSeek · synthetic", 0.5),
             ("DeepSeek", "real",      C_ALT,  "////", "DeepSeek · real PMC", 1.5)]
    for model, nt, color, hatch, label, off in specs:
        rates = [data[model][s][nt][0] for s in labels]
        lo = np.clip([data[model][s][nt][0] - data[model][s][nt][1] for s in labels], 0, None)
        hi = np.clip([data[model][s][nt][2] - data[model][s][nt][0] for s in labels], 0, None)
        ax.bar(x + off * w, rates, w, yerr=[lo, hi],
               error_kw=dict(ecolor="0.3", lw=0.9, capsize=2),
               color=color, hatch=hatch, edgecolor="k", linewidth=0.5, label=label)
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=30, ha="right", rotation_mode="anchor")
    ax.set_ylabel("Stigmatizing-language rate (%)")
    ax.set_ylim(0, 125)
    ax.set_yticks(range(0, 101, 20))
    ax.grid(axis="y", alpha=0.25); ax.set_axisbelow(True)
    ax.legend(ncol=2, framealpha=0.95, loc="upper center",
              columnspacing=1.2, handletextpad=0.5, handlelength=1.6, borderaxespad=0.4)

    PANELS = Path("figures/manuscript_combined/panels"); PANELS.mkdir(parents=True, exist_ok=True)
    fig.set_size_inches(6.6, 5.2)
    ax.set_position([0.10, 0.16, 0.87, 0.78])
    panel_path = PANELS / "p_pmc_poster.png"
    fig.savefig(panel_path, dpi=200)
    print("wrote", panel_path)

    # --- Pad onto the identical 1500x1250 poster canvas (same routine as
    # build_poster_figures.py, no distortion, centered, contained). ---
    BOX_W, BOX_H = 1500, 1250
    PAD = 24
    OUT_DIR = Path("poster_figures"); OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "7_pmc_replication.png"
    im = Image.open(panel_path).convert("RGBA")
    avail_w, avail_h = BOX_W - 2 * PAD, BOX_H - 2 * PAD
    scale = min(avail_w / im.width, avail_h / im.height)
    new = (max(1, round(im.width * scale)), max(1, round(im.height * scale)))
    im = im.resize(new, Image.LANCZOS)
    canvas = Image.new("RGBA", (BOX_W, BOX_H), (255, 255, 255, 255))
    off = ((BOX_W - new[0]) // 2, (BOX_H - new[1]) // 2)
    canvas.paste(im, off, im)
    canvas.convert("RGB").save(out_path, "PNG")
    print(f"wrote {out_path} ({BOX_W}x{BOX_H}, fit {new[0]}x{new[1]})")


if __name__ == "__main__":
    main()
