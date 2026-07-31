"""Figure 1 — NSCLC study-design schematic (BioRender-style, matched to the
reference triage-study layout: pale lavender boxes, periwinkle block arrows,
left-aligned titles + bullets, small vector icons).

Run:  venv/bin/python plots/plot_fig1_setup.py
Out:  figures/manuscript/Fig1_study_design.png (+ .pdf)
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, Ellipse, Rectangle, Circle

OUT = Path("figures/manuscript")
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "figure.dpi": 150, "savefig.bbox": "tight",
    "figure.facecolor": "white", "savefig.facecolor": "white",
})

FIGW, FIGH = 7.4, 12.0
AR = FIGW / FIGH

# palette matched to the reference figure
BOXFC   = "#E9EBF7"   # pale lavender box
BOXEC   = "#8189C4"   # periwinkle border
TITLE   = "#1B2444"   # dark navy title
TXT     = "#2C3345"   # body text
ARROW   = "#AEB8E4"   # light periwinkle block arrow
ARROWEC = "#8f9bd6"

# icon palette (BioRender-ish flat)
IC_BLUE = "#5C8AA8"; IC_DBLUE = "#3E6B85"; IC_TEAL = "#4E9C93"
IC_SKIN = "#C79B78"; IC_CLIP = "#F1F4F9"; IC_LINE = "#9AA7B4"
IC_RED = "#E0574A"; IC_PURP = "#7E64C4"; IC_ORANGE = "#E5883C"; IC_SCREEN = "#3F4A5E"

MC = {"gemini-2.5-flash": "#4C72B0", "deepseek-chat": "#D0605E",
      "llama-3.3-70B": "#5BAE7C", "llama-3.1-8B": "#A08869",
      "gpt-4o": "#8E7CC3", "gpt-4o-mini": "#D4BE6A"}


# ── primitives ───────────────────────────────────────────────────────────
def rrect(ax, x, y, w, h, fc, ec, lw=1.3, z=3, pad=0.010):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                 boxstyle=f"round,pad={pad},rounding_size={pad}",
                 facecolor=fc, edgecolor=ec, linewidth=lw, zorder=z))


def block_arrow(ax, x1, y1, x2, y2, shaft=0.11, head_w=0.28, head_len=0.17):
    """Block arrow drawn in physical (inch) space so it never shears."""
    ax1, ay1, ax2, ay2 = x1 * FIGW, y1 * FIGH, x2 * FIGW, y2 * FIGH
    d = np.array([ax2 - ax1, ay2 - ay1]); L = np.hypot(*d)
    u = d / L; n = np.array([-u[1], u[0]])
    tip = np.array([ax2, ay2]); base = np.array([ax1, ay1])
    hb = tip - u * head_len
    pts = [base + n * shaft / 2, hb + n * shaft / 2, hb + n * head_w / 2,
           tip, hb - n * head_w / 2, hb - n * shaft / 2, base - n * shaft / 2]
    pts = [(px / FIGW, py / FIGH) for px, py in pts]
    ax.add_patch(Polygon(pts, closed=True, facecolor=ARROW, edgecolor=ARROWEC,
                 linewidth=0.8, zorder=2, joinstyle="miter"))


def box(ax, x, y, w, h, title, bullets, sub=None, icon=None, title_fs=9.6,
        bul_fs=8.0, iconpad=0.10):
    rrect(ax, x, y, w, h, BOXFC, BOXEC)
    lx = x - w / 2 + 0.022
    ty = y + h / 2 - 0.024
    ax.text(lx, ty, title, ha="left", va="top", fontsize=title_fs,
            fontweight="bold", color=TITLE, zorder=5)
    by = ty - 0.030
    for b in bullets:
        ax.text(lx + 0.006, by, "•", ha="left", va="top", fontsize=bul_fs,
                color=TXT, zorder=5)
        ax.text(lx + 0.028, by, b, ha="left", va="top", fontsize=bul_fs,
                color=TXT, zorder=5, linespacing=1.3)
        by -= 0.021 * (1 + b.count("\n"))
    if sub:
        ax.text(lx, by - 0.004, sub, ha="left", va="top", fontsize=7.2,
                color="#5A6376", style="italic", zorder=5)
    if icon:
        icon(ax, x + w / 2 - iconpad, y, 0.032)


# ── icons (cx, cy center; s = half-size in data-x) ───────────────────────
def _circle(ax, x, y, r, **kw):
    # r is x-radius; scale y by AR so it renders round on the full-bleed axis
    ax.add_patch(Ellipse((x, y), 2 * r, 2 * r * AR, **kw))


def ic_hospital(ax, cx, cy, s):
    w, h = s * 1.0, s * 1.5 / AR * AR   # body
    bx, by, bw, bh = cx - w, cy - s * 0.9, 2 * w, s * 1.9
    ax.add_patch(Rectangle((bx, by), bw, bh, facecolor=IC_BLUE, edgecolor=IC_DBLUE,
                 lw=1.0, zorder=5))
    # windows
    for i in range(3):
        for j in range(3):
            ax.add_patch(Rectangle((bx + bw * (0.17 + 0.28 * i), by + bh * (0.15 + 0.26 * j)),
                         bw * 0.15, bh * 0.14, facecolor="white", edgecolor="none", zorder=6))
    # cross plaque on top
    ax.add_patch(Rectangle((cx - s * 0.5, cy + s * 1.0), s * 1.0, s * 0.7 / AR,
                 facecolor="white", edgecolor=IC_DBLUE, lw=0.9, zorder=6))
    ax.plot([cx, cx], [cy + s * 1.05, cy + s * 1.55], color=IC_RED, lw=1.6, zorder=7,
            solid_capstyle="butt")
    ax.plot([cx - s * 0.28, cx + s * 0.28], [cy + s * 1.3, cy + s * 1.3],
            color=IC_RED, lw=1.6, zorder=7, solid_capstyle="butt")


def ic_clinician(ax, cx, cy, s):
    # clipboard (right)
    clx = cx + s * 0.35
    ax.add_patch(FancyBboxPatch((clx - s * 0.55, cy - s * 1.0), s * 1.1, s * 2.0,
                 boxstyle="round,pad=0.004", facecolor=IC_CLIP, edgecolor=IC_LINE,
                 lw=1.0, zorder=6))
    for k, yy in enumerate((0.55, 0.15, -0.25, -0.6)):
        ax.plot([clx - s * 0.35, clx + s * 0.3], [cy + s * yy, cy + s * yy],
                color=IC_LINE, lw=0.9, zorder=7)
    ax.plot([clx - s * 0.42, clx - s * 0.34, clx - s * 0.18],
            [cy + s * 0.55, cy + s * 0.45, cy + s * 0.68], color=IC_TEAL, lw=1.2, zorder=7)
    # clinician (left): head + teal scrubs torso
    hx = cx - s * 0.7
    _circle(ax, hx, cy + s * 0.7, s * 0.42, facecolor=IC_SKIN, edgecolor="none", zorder=6)
    ax.add_patch(Polygon([(hx - s * 0.7, cy - s * 1.05), (hx - s * 0.55, cy + s * 0.15),
                          (hx + s * 0.55, cy + s * 0.15), (hx + s * 0.7, cy - s * 1.05)],
                 closed=True, facecolor=IC_TEAL, edgecolor="none", zorder=5))


def ic_checklist(ax, cx, cy, s):
    for k, yy in enumerate((0.85, 0.0, -0.85)):
        y = cy + s * yy
        if k == 0:
            ax.text(cx - s * 1.05, y, "×", ha="center", va="center", fontsize=8,
                    color=IC_DBLUE, zorder=6)
        else:
            _circle(ax, cx - s * 1.05, y, s * 0.22, facecolor="none",
                    edgecolor=IC_DBLUE, lw=1.0, zorder=6)
        block_arrow(ax, (cx - s * 0.7), (y), (cx - s * 0.05), (y),
                    shaft=0.02, head_w=0.06, head_len=0.05)
        ax.add_patch(FancyBboxPatch((cx + s * 0.1, y - s * 0.32), s * 0.7, s * 0.64 / AR * AR,
                     boxstyle="round,pad=0.002", facecolor=IC_PURP, edgecolor="none", zorder=6))
        ax.plot([cx + s * 0.22, cx + s * 0.4, cx + s * 0.72],
                [y, y - s * 0.2, y + s * 0.25], color="white", lw=1.2, zorder=7,
                solid_capstyle="round", solid_joinstyle="round")


def ic_monitor(ax, cx, cy, s):
    ax.add_patch(FancyBboxPatch((cx - s * 1.1, cy - s * 0.4), s * 2.2, s * 1.7,
                 boxstyle="round,pad=0.004", facecolor=IC_SCREEN, edgecolor="none", zorder=5))
    ax.add_patch(Rectangle((cx - s * 0.95, cy - s * 0.25), s * 1.9, s * 1.4,
                 facecolor="#DDE4F2", edgecolor="none", zorder=6))
    rng = np.linspace(-0.75, 0.75, 8)
    ys = 0.2 + 0.6 * rng + np.array([0.1, -0.1, 0.15, 0.0, 0.2, 0.1, 0.3, 0.25])
    for xx, yy in zip(rng, ys):
        ax.add_patch(Circle((cx + s * xx, cy + s * yy * 0.9), s * 0.09,
                     facecolor=IC_ORANGE, edgecolor="none", zorder=7))
    ax.plot([cx - s * 0.9, cx + s * 0.9], [cy - s * 0.05, cy + s * 0.9],
            color=IC_DBLUE, lw=1.0, zorder=7)
    ax.plot([cx - s * 0.35, cx + s * 0.35], [cy - s * 0.4, cy - s * 0.4],
            color=IC_SCREEN, lw=2.4, zorder=5)   # stand


def main():
    fig = plt.figure(figsize=(FIGW, FIGH), facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

    xL, xR, cx = 0.275, 0.725, 0.5
    WIDE, HALF = 0.90, 0.42

    # 1a. data source (top-left)
    box(ax, xL, 0.930, HALF, 0.115,
        "GENIE BPC NSCLC cases",
        ["1,048 real de-identified cases",
         "structured genomic + clinical fields",
         "AACR Project GENIE v2.0-public"],
        icon=ic_hospital, iconpad=0.052)
    # 1b. measurement scale (top-right)
    box(ax, xR, 0.930, HALF, 0.115,
        "NCCN guideline ground truth",
        ["deterministic decision-tree scorer",
         "standard-of-care category per case",
         "surgery / chemo / immuno / targeted / RT"])

    block_arrow(ax, xL, 0.870, 0.46, 0.833)
    block_arrow(ax, xR, 0.870, 0.54, 0.833)

    # 2. note generation
    box(ax, cx, 0.788, WIDE, 0.092,
        "Demographics-neutral clinical notes",
        ["generated from structured fields (Gemini-2.5-flash)",
         "clinical facts held constant across all variants"],
        icon=ic_clinician, iconpad=0.075)

    block_arrow(ax, cx, 0.740, cx, 0.703)

    # 3. factorial variants
    box(ax, cx, 0.652, WIDE, 0.100,
        "Factorial demographic variants (30 per case)",
        ["race × insurance × SES × gender/identity × intersectional",
         "29 demographic framings  +  1 no-demographics reference",
         "yields 31,440 prompts per model  (1,048 × 30)"],
        icon=ic_checklist, iconpad=0.075)

    block_arrow(ax, cx, 0.600, cx, 0.563)

    # 4. models
    box(ax, cx, 0.512, WIDE, 0.092,
        "Six LLMs queried  (temperature 0)",
        ["Gemini-2.5-flash · DeepSeek-chat · Llama-3.3-70B",
         "Llama-3.1-8B · GPT-4o · GPT-4o-mini",
         "fresh query per prompt  ·  ≈ 188,640 responses"])

    block_arrow(ax, cx, 0.464, cx, 0.427)

    # 5. output extraction
    box(ax, cx, 0.383, WIDE, 0.078,
        "Output extraction  (per response)",
        ["treatment recommendation + rationale text",
         "NCCN concordance  ·  soft-framing intensity score"])

    block_arrow(ax, cx, 0.342, xL, 0.305)
    block_arrow(ax, cx, 0.342, xR, 0.305)

    # 6a. decision bias
    box(ax, xL, 0.250, HALF, 0.098,
        "Decision bias",
        ["treatment flip rate vs reference",
         "NCCN concordance\n(TOST equivalence)"], title_fs=9.6, bul_fs=7.8)
    # 6b. framing bias
    box(ax, xR, 0.250, HALF, 0.098,
        "Framing bias  (soft / stigma)",
        ["stigmatizing vs appropriate split",
         "LLM judge + bias decision tree\n(validated vs human gold)"], title_fs=9.6, bul_fs=7.8)

    block_arrow(ax, xL, 0.201, 0.46, 0.163)
    block_arrow(ax, xR, 0.201, 0.54, 0.163)

    # 7. statistics
    box(ax, cx, 0.118, WIDE, 0.098,
        "Statistical analysis",
        ["case-clustered bootstrap (B=10,000) 95% CIs",
         "grid-wide Benjamini-Hochberg FDR (174 model×variant tests)",
         "TOST equivalence  ·  paired sign tests"],
        icon=ic_monitor, iconpad=0.075)

    fig.savefig(OUT / "Fig1_study_design.png", dpi=300)
    fig.savefig(OUT / "Fig1_study_design.pdf")
    print("wrote", OUT / "Fig1_study_design.png")


if __name__ == "__main__":
    main()
