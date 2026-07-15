"""NCCN NSCLC Decision Tree Flowchart for slide M3.

Produces figures/slide_nccn_flowchart.png
Usage: python plot_nccn_flowchart.py
"""
from __future__ import annotations
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

FIGURES_DIR = Path("figures")
FIGURES_DIR.mkdir(exist_ok=True)

# ── Color palette ─────────────────────────────────────────────────────────────
C = {
    "surgery":        "#27AE60",
    "radiation":      "#E67E22",
    "targeted":       "#2980B9",
    "immunochemo":    "#8E44AD",
    "chemo":          "#C0392B",
    "decision":       "#ECF0F1",
    "decision_edge":  "#7F8C8D",
    "root":           "#2C3E50",
    "text_light":     "white",
    "text_dark":      "#2C3E50",
    "arrow":          "#555555",
}

def box(ax, x, y, w, h, text, fc, ec=None, fontsize=8.2, bold=False,
        text_color=None, radius=0.012):
    ec = ec or fc
    tc = text_color or (C["text_light"] if fc != C["decision"] else C["text_dark"])
    patch = FancyBboxPatch((x - w/2, y - h/2), w, h,
                           boxstyle=f"round,pad={radius}",
                           facecolor=fc, edgecolor=ec, linewidth=1.1, zorder=3)
    ax.add_patch(patch)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize,
            fontweight="bold" if bold else "normal",
            color=tc, zorder=4, wrap=False,
            multialignment="center")
    return patch


def arrow(ax, x1, y1, x2, y2, label="", color=None):
    color = color or C["arrow"]
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color,
                                lw=1.1, mutation_scale=9),
                zorder=2)
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx + 0.008, my, label, fontsize=7, color="#555555",
                va="center", style="italic", zorder=5)


def main():
    fig = plt.figure(figsize=(18, 11), facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    # ── Title ─────────────────────────────────────────────────────────────────
    ax.text(0.5, 0.975, "NCCN NSCLC Decision Tree — EquityGUIDE Ground Truth Scorer",
            ha="center", va="top", fontsize=13, fontweight="bold", color=C["root"])
    ax.text(0.5, 0.952, "Primary_answer shown at each leaf  ·  ~78% of dataset cases are scoreable",
            ha="center", va="top", fontsize=9, color="#555555", style="italic")

    # ── Root node ─────────────────────────────────────────────────────────────
    bw, bh = 0.13, 0.045
    box(ax, 0.5, 0.905, 0.17, bh, "NSCLC Clinical Profile\n(stage, ECOG, biomarkers)",
        C["root"], bold=True, fontsize=9)

    # ECOG guard
    box(ax, 0.5, 0.845, 0.16, bh, "ECOG PS ≥ 3?", C["decision"],
        ec=C["decision_edge"], text_color=C["text_dark"])
    arrow(ax, 0.5, 0.905-bh/2, 0.5, 0.845+bh/2)

    # ECOG ≥ 3 → BSC
    box(ax, 0.84, 0.845, 0.12, bh, "BSC / Single-agent\nchemotherapy",
        C["chemo"], fontsize=7.8)
    arrow(ax, 0.5+0.08, 0.845, 0.84-0.06, 0.845, label="Yes")

    # Stage split
    box(ax, 0.5, 0.785, 0.14, bh, "Stage?",
        C["decision"], ec=C["decision_edge"], text_color=C["text_dark"])
    arrow(ax, 0.5, 0.845-bh/2, 0.5, 0.785+bh/2, label="No")

    # ── Stage columns: I=0.10, II=0.265, III=0.44, IV=0.68 ───────────────────
    stage_xs  = [0.09, 0.245, 0.405, 0.70]
    stage_lbs = ["I", "II", "III", "IV"]
    stage_cols = [C["surgery"], C["surgery"], C["surgery"], C["targeted"]]

    for sx, lb, sc in zip(stage_xs, stage_lbs, stage_cols):
        box(ax, sx, 0.725, 0.085, 0.04, f"Stage {lb}", sc,
            fontsize=8.5, bold=True)
        # branching line down from "Stage?" node
        # horizontal line from center then down to column
        arrow(ax, 0.5, 0.785-bh/2, sx, 0.725+0.02)

    # ─────────────────────────────────────────────────────────────────────────
    # STAGE I  (x=0.10)
    # ─────────────────────────────────────────────────────────────────────────
    sx = 0.10
    dh = 0.038

    box(ax, sx, 0.665, 0.11, dh, "Medically\noperable?",
        C["decision"], ec=C["decision_edge"], text_color=C["text_dark"], fontsize=7.8)
    arrow(ax, sx, 0.725-0.02, sx, 0.665+dh/2)

    # Inoperable → SBRT
    box(ax, sx-0.065, 0.610, 0.09, dh, "SBRT / SABR",
        C["radiation"], fontsize=7.8)
    arrow(ax, sx-0.02, 0.665-dh/2+0.005, sx-0.065, 0.610+dh/2, label="No")

    # T1a → lung-sparing
    box(ax, sx+0.005, 0.600, 0.095, dh, "T1a → Lung-\nsparing resection",
        C["surgery"], fontsize=7.5)
    # T1b+ → lobectomy
    box(ax, sx+0.005, 0.550, 0.095, dh, "T1b+ → Lobectomy",
        C["surgery"], fontsize=7.5)
    arrow(ax, sx+0.01, 0.665-dh/2, sx+0.005, 0.600+dh/2, label="Yes")
    arrow(ax, sx+0.005, 0.600-dh/2, sx+0.005, 0.550+dh/2)

    # Post-resection
    box(ax, sx, 0.490, 0.10, dh, "Post-resection\n(R0)?",
        C["decision"], ec=C["decision_edge"], text_color=C["text_dark"], fontsize=7.5)
    arrow(ax, sx+0.005, 0.550-dh/2, sx, 0.490+dh/2)

    box(ax, sx-0.055, 0.438, 0.085, dh, "EGFR+  →\nOsimertinib",
        C["targeted"], fontsize=7.3)
    box(ax, sx+0.058, 0.438, 0.085, dh, "No driver →\nObservation",
        C["surgery"], fontsize=7.3)
    arrow(ax, sx-0.02, 0.490-dh/2, sx-0.055, 0.438+dh/2, label="IB")
    arrow(ax, sx+0.02, 0.490-dh/2, sx+0.058, 0.438+dh/2)

    # ─────────────────────────────────────────────────────────────────────────
    # STAGE II  (x=0.265)
    # ─────────────────────────────────────────────────────────────────────────
    sx = 0.265

    box(ax, sx, 0.665, 0.11, dh, "Medically\noperable?",
        C["decision"], ec=C["decision_edge"], text_color=C["text_dark"], fontsize=7.8)
    arrow(ax, sx, 0.725-0.02, sx, 0.665+dh/2)

    box(ax, sx-0.065, 0.610, 0.085, dh, "SBRT / SABR",
        C["radiation"], fontsize=7.8)
    arrow(ax, sx-0.02, 0.665-dh/2+0.005, sx-0.065, 0.610+dh/2, label="No")

    box(ax, sx+0.005, 0.610, 0.085, dh, "Lobectomy +\nLN dissection",
        C["surgery"], fontsize=7.5)
    arrow(ax, sx+0.01, 0.665-dh/2, sx+0.005, 0.610+dh/2, label="Yes")

    box(ax, sx, 0.550, 0.10, dh, "Post-resection\nadjuvant?",
        C["decision"], ec=C["decision_edge"], text_color=C["text_dark"], fontsize=7.5)
    arrow(ax, sx+0.005, 0.610-dh/2, sx, 0.550+dh/2)

    box(ax, sx-0.055, 0.498, 0.09, dh, "EGFR+ →\nOsimertinib",
        C["targeted"], fontsize=7.3)
    box(ax, sx+0.060, 0.498, 0.09, dh, "No driver →\nCisplatin doublet",
        C["chemo"], fontsize=7.3)
    arrow(ax, sx-0.02, 0.550-dh/2, sx-0.055, 0.498+dh/2)
    arrow(ax, sx+0.02, 0.550-dh/2, sx+0.060, 0.498+dh/2)

    # ─────────────────────────────────────────────────────────────────────────
    # STAGE III  (x=0.405)
    # ─────────────────────────────────────────────────────────────────────────
    sx = 0.405

    box(ax, sx, 0.665, 0.115, dh, "Resectability?",
        C["decision"], ec=C["decision_edge"], text_color=C["text_dark"], fontsize=7.8)
    arrow(ax, sx, 0.725-0.02, sx, 0.665+dh/2)

    box(ax, sx-0.075, 0.610, 0.10, dh, "Resectable IIIA →\nSurgery + adj. chemo",
        C["surgery"], fontsize=7.2)
    box(ax, sx+0.005, 0.590, 0.105, dh, "Marginally resectable →\nPre-op CRT → surgery eval",
        C["radiation"], fontsize=7.0)
    box(ax, sx+0.005, 0.540, 0.105, dh+0.005, "Unresectable →\nConcurrent CRT +\nDurvalumab (PACIFIC)",
        C["immunochemo"], fontsize=7.2)

    arrow(ax, sx-0.025, 0.665-dh/2, sx-0.075, 0.610+dh/2, label="Res.")
    arrow(ax, sx+0.005, 0.665-dh/2, sx+0.005, 0.590+dh/2, label="Marg.")
    arrow(ax, sx+0.005, 0.590-dh/2, sx+0.005, 0.540+dh/2+0.005, label="Unres.")

    # ECOG 2 note
    box(ax, sx+0.005, 0.488, 0.10, dh, "ECOG 2 → Sequential\nCRT (± durvalumab)",
        C["radiation"], fontsize=7.0)
    arrow(ax, sx+0.005, 0.540-dh/2, sx+0.005, 0.488+dh/2, label="ECOG 2")

    # ─────────────────────────────────────────────────────────────────────────
    # STAGE IV  (x=0.70)  — biomarker cascade vertical list
    # ─────────────────────────────────────────────────────────────────────────
    sx = 0.70
    bx_w = 0.28   # wide boxes for stage IV
    lh = 0.043    # row height

    # Header
    box(ax, sx, 0.665, 0.13, dh, "Biomarker panel\n(7 drivers + PD-L1)",
        C["decision"], ec=C["decision_edge"], text_color=C["text_dark"], fontsize=7.8)
    arrow(ax, sx, 0.725-0.02, sx, 0.665+dh/2)

    # Each row: left = condition, right = drug
    rows = [
        # (condition, drug, drug_color)
        ("EGFR exon 19 del / L858R",        "Osimertinib",                         C["targeted"]),
        ("EGFR exon 20 insertion",           "Amivantamab + carbo/pem",             C["targeted"]),
        ("ALK rearrangement",                "Alectinib / brigatinib / lorlatinib", C["targeted"]),
        ("ROS1 rearrangement",               "Entrectinib / crizotinib",            C["targeted"]),
        ("BRAF V600E",                       "Dabrafenib + trametinib",             C["targeted"]),
        ("MET exon 14 skipping",             "Capmatinib / tepotinib",              C["targeted"]),
        ("RET fusion",                       "Selpercatinib / pralsetinib",         C["targeted"]),
        ("NTRK fusion",                      "Larotrectinib / entrectinib",         C["targeted"]),
        ("Driver-negative · PD-L1 ≥50%",    "Pembrolizumab\nmono",                 C["immunochemo"]),
        ("Driver-neg · PD-L1 <50%\n(non-squamous)", "Carbo+pem+pembro\n(KEYNOTE-189)", C["immunochemo"]),
        ("Driver-neg · PD-L1 <50%\n(squamous)",     "Carbo+pac+pembro\n(KEYNOTE-407)", C["immunochemo"]),
    ]

    y_start = 0.615
    cond_x   = 0.590
    drug_x   = 0.855
    cond_w   = 0.155
    drug_w   = 0.145
    row_h    = 0.046

    # Draw vertical spine
    ax.plot([sx, sx], [0.665-dh/2, y_start - len(rows)*row_h - 0.002],
            color=C["arrow"], lw=1.0, zorder=1)

    for i, (cond, drug, dc) in enumerate(rows):
        yc = y_start - i * row_h
        ax.plot([sx, cond_x + cond_w/2 + 0.002], [yc, yc],
                color=C["arrow"], lw=0.8, zorder=1)
        box(ax, cond_x, yc, cond_w, row_h-0.006, cond,
            C["decision"], ec=C["decision_edge"], text_color=C["text_dark"],
            fontsize=7.0)
        arrow(ax, cond_x + cond_w/2, yc, drug_x - drug_w/2, yc)
        box(ax, drug_x, yc, drug_w, row_h-0.006, drug, dc, fontsize=7.2)

    # ── Dividing line between Stage I–III and Stage IV ────────────────────────
    ax.axvline(0.525, ymin=0.33, ymax=0.80,
               color="#CCCCCC", lw=1.0, ls="--", zorder=0)
    ax.text(0.530, 0.92, "Stage IV biomarker cascade →",
            fontsize=8, color="#888888", style="italic", va="center")

    # ── Legend ────────────────────────────────────────────────────────────────
    legend_items = [
        (C["surgery"],       "Surgery / observation"),
        (C["radiation"],     "Radiation / CRT"),
        (C["targeted"],      "Targeted therapy (TKI / kinase inhibitor)"),
        (C["immunochemo"],   "Immunotherapy / chemoimmunotherapy"),
        (C["chemo"],         "Chemotherapy"),
        (C["decision"],      "Decision node"),
    ]
    lx, ly = 0.02, 0.10
    for color, label in legend_items:
        ec = C["decision_edge"] if color == C["decision"] else color
        patch = mpatches.FancyBboxPatch((lx, ly-0.009), 0.025, 0.018,
                                        boxstyle="round,pad=0.002",
                                        facecolor=color, edgecolor=ec, linewidth=0.8)
        ax.add_patch(patch)
        tc = C["text_dark"] if color == C["decision"] else "white"
        ax.text(lx + 0.032, ly, label, fontsize=8, va="center", color=C["text_dark"])
        ly -= 0.026

    ax.text(0.02, ly + 0.008, "Note: ~78% of dataset cases are scoreable by this tree.\n"
            "Stage IV with unknown biomarkers → excluded from concordance analysis.",
            fontsize=7.5, color="#777777", style="italic", va="top")

    out = FIGURES_DIR / "slide_nccn_flowchart.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
