#!/usr/bin/env python3
"""DRAFT: care-intensity panel as BARS instead of diamonds-among-dots (easier to read).

Each variant row -> a horizontal bar = cross-vendor MEAN net change (extends toward
the harm side, so direction + magnitude are immediate). The 6 per-vendor values stay
overlaid as faint dots (still never pooled), and the k/6 harm-direction count is kept.
Left = advanced treatment (clinical-trial mention, harm = negative);
right = de-escalation (palliative/BSC, harm = positive).

Non-destructive: writes panels/p_care_intensity_bars.png. Run from repo root.
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from plot_care_intensity_permodel import load, ORDER, NICE, REFERENCE

C_DOT = "#9AA7B0"       # per-vendor dots
C_HARM = "#B0322F"      # bar in the harm direction
C_SAFE = "#6E8CA0"      # bar in the non-harm direction
C_REF = "#B9B9B9"       # reference variants
C_HARM_BG = "#F3E4E1"   # faint harm-side shading
PANELS = Path("figures/manuscript_combined/panels")
OUT_PANEL = PANELS / "p_care_intensity_bars.png"


def panel(ax, d, models, idx, title, subtitle, harm_negative, xlim):
    n = len(ORDER)
    ys = {vk: n - 1 - i for i, vk in enumerate(ORDER)}
    ax.axvspan(xlim[0], 0, color=C_HARM_BG, zorder=0) if harm_negative \
        else ax.axvspan(0, xlim[1], color=C_HARM_BG, zorder=0)
    jit = [(-0.20 + 0.40 * k / (len(models) - 1)) for k in range(len(models))]
    ytick, ylab = [], []
    for vk in ORDER:
        y = ys[vk]
        vals = [d[vk][m][idx] for m in models if m in d[vk]]
        if vals:
            mean = sum(vals) / len(vals)
            in_harm = (mean < 0) if harm_negative else (mean > 0)
            colour = C_REF if vk in REFERENCE else (C_HARM if in_harm else C_SAFE)
            ax.barh(y, mean, height=0.62, color=colour, alpha=0.85, zorder=2,
                    edgecolor="white", linewidth=0.5)
            for k, m in enumerate([m for m in models if m in d[vk]]):
                ax.plot(d[vk][m][idx], y + jit[k], "o", ms=3.0, color=C_DOT,
                        alpha=0.85, zorder=3, mew=0)
            harm = sum(1 for v in vals if (v < 0 if harm_negative else v > 0))
            xedge = xlim[0] + 0.015 * (xlim[1] - xlim[0]) if harm_negative else \
                xlim[1] - 0.015 * (xlim[1] - xlim[0])
            ha = "left" if harm_negative else "right"
            col = "#8E1B1B" if (harm >= 3 and vk not in REFERENCE) else "#999"
            ax.text(xedge, y, f"{harm}/{len(vals)}", ha=ha, va="center",
                    fontsize=7.0, color=col, zorder=4)
        ytick.append(y); ylab.append(NICE[vk])
    ax.axvline(0, color="#333", lw=0.9, zorder=4)
    ax.set_yticks(ytick); ax.set_yticklabels(ylab, fontsize=8.2)
    for lbl, vk in zip(ax.get_yticklabels(), ORDER):
        if vk in REFERENCE:
            lbl.set_color("#777"); lbl.set_style("italic")
    ax.set_xlim(*xlim); ax.set_ylim(-0.7, n - 0.3)
    ax.set_xlabel("Net change vs no-demographics (pp)", fontsize=8.8)
    ax.set_title(title, fontsize=16, fontweight="bold", loc="left", pad=10)
    ax.tick_params(length=0)
    ax.spines[["top", "right"]].set_visible(False)


def build(figsize, out_path):
    d, models = load()
    fig, (Ap, Bp) = plt.subplots(1, 2, figsize=figsize, sharey=True)
    xlim = (-4.5, 7.0)
    panel(Ap, d, models, 0, "Advanced treatment",
          "clinical-trial mention   (shaded = offered less)", True, xlim)
    panel(Bp, d, models, 1, "De-escalation",
          "palliative / best-supportive-care   (shaded = offered more)", False, xlim)
    Bp.tick_params(labelleft=False)
    fig.tight_layout(rect=(0, 0, 1, 0.99), w_pad=3.0)
    PANELS.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    from PIL import Image
    w, h = Image.open(out_path).size
    print(f"wrote {out_path.name}  {w}x{h}  aspect={w/h:.3f}")


def main():
    build((11.4, 6.6), OUT_PANEL)                                   # original 1.72
    build((19.1, 6.6), PANELS / "p_care_intensity_bars_wide.png")  # wide ~2.95 for equal-height row


if __name__ == "__main__":
    main()
