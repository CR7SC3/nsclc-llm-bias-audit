#!/usr/bin/env python3
"""DRAFT rebuilds of Figure 2 with the dissociation panel wired in.

Non-destructive: writes *_DRAFT*.png alongside the existing composite so they
can be judged without overwriting anything.

Variant 1 (v1): reuse the old geometry, reordered
    A concordance | B dissociation (top, shared height)
    C care-intensity (full width, bottom)
  -> thesis panel ends up small; exploratory panel dominates (kept for comparison).

Variant 2 (v2): thesis-prominent, care-intensity -> supplement
    A concordance   (full width, top)
    B dissociation  (full width, bottom)   <- thesis gets full width, sub-labels legible
  -> matches the figure's own title: "decision unchanged" (A) / "framing reshaped" (B).
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
PANELS = ROOT / "figures" / "manuscript_combined" / "panels"
OUT = ROOT / "figures" / "manuscript_combined"

ARIAL_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
TARGET_W = 2600
MARGIN = 70
GUTTER = 55
BAND = 90

P_CONC = PANELS / "p_concordance_stability.png"
P_DISS = PANELS / "p_dissociation.png"
P_CARE = PANELS / "p_care_intensity.png"


def _font():
    return ImageFont.truetype(ARIAL_BOLD, size=max(56, TARGET_W // 34))


def _stamp(draw, font, letter, x, y):
    bb = draw.textbbox((0, 0), letter, font=font)
    draw.text((x, y - bb[1]), letter, fill="black", font=font)


def variant1(out_path):
    A, B, C = [Image.open(s).convert("RGB") for s in (P_CONC, P_DISS, P_CARE)]
    aA, aB, aC = (im.size[0] / im.size[1] for im in (A, B, C))
    inner_w = TARGET_W - 2 * MARGIN
    Ht = (inner_w - GUTTER) / (aA + aB)
    wA, wB, Ht = round(aA * Ht), round(aB * Ht), round(Ht)
    hC = round(inner_w / aC)
    total_h = 2 * MARGIN + (BAND + Ht) + GUTTER + (BAND + hC)
    canvas = Image.new("RGB", (TARGET_W, total_h), "white")
    draw = ImageDraw.Draw(canvas); font = _font()
    y = MARGIN
    _stamp(draw, font, "A", MARGIN, y)
    canvas.paste(A.resize((wA, Ht), Image.LANCZOS), (MARGIN, y + BAND))
    xB = MARGIN + wA + GUTTER
    _stamp(draw, font, "B", xB, y)
    canvas.paste(B.resize((wB, Ht), Image.LANCZOS), (xB, y + BAND))
    y += BAND + Ht + GUTTER
    _stamp(draw, font, "C", MARGIN, y)
    canvas.paste(C.resize((inner_w, hC), Image.LANCZOS), (MARGIN, y + BAND))
    canvas.save(out_path, dpi=(300, 300))
    return canvas.size


def variant2(out_path):
    """Two full-width rows: A concordance on top, B dissociation below."""
    A, B = [Image.open(s).convert("RGB") for s in (P_CONC, P_DISS)]
    aA, aB = (im.size[0] / im.size[1] for im in (A, B))
    inner_w = TARGET_W - 2 * MARGIN
    hA = round(inner_w / aA)
    hB = round(inner_w / aB)
    total_h = 2 * MARGIN + (BAND + hA) + GUTTER + (BAND + hB)
    canvas = Image.new("RGB", (TARGET_W, total_h), "white")
    draw = ImageDraw.Draw(canvas); font = _font()
    y = MARGIN
    _stamp(draw, font, "A", MARGIN, y)
    canvas.paste(A.resize((inner_w, hA), Image.LANCZOS), (MARGIN, y + BAND))
    y += BAND + hA + GUTTER
    _stamp(draw, font, "B", MARGIN, y)
    canvas.paste(B.resize((inner_w, hB), Image.LANCZOS), (MARGIN, y + BAND))
    canvas.save(out_path, dpi=(300, 300))
    return canvas.size


P_HEAT = PANELS / "p_flip_heatmap.png"
P_DISS_WIDE = PANELS / "p_dissociation_wide.png"   # regenerated at heatmap aspect


def variant3(out_path):
    """Four panels, dissociation inserted as C, heatmap kept as D:
        A concordance | B care-intensity   (top row, shared height)
        C dissociation (wide regen)        (full width, ~= heatmap box)
        D tier-shift heatmap               (full width)
    C uses the wide-aspect regeneration so it fills the same full-width box as D
    natively (no stretch)."""
    top_right = getattr(variant3, "_top_right", P_CARE)   # B panel in the top row
    mid_full = getattr(variant3, "_mid_full", P_DISS_WIDE)  # C full-width panel
    A, B, C, D = [Image.open(s).convert("RGB")
                  for s in (P_CONC, top_right, mid_full, P_HEAT)]
    aA, aB, aC, aD = (im.size[0] / im.size[1] for im in (A, B, C, D))
    inner_w = TARGET_W - 2 * MARGIN
    Ht = (inner_w - GUTTER) / (aA + aB)               # row 1: A|B shared height
    wA, wB, Ht = round(aA * Ht), round(aB * Ht), round(Ht)
    hC = round(inner_w / aC)                          # row 2: C full width (native)
    hD = round(inner_w / aD)                          # row 3: D full width
    total_h = (2 * MARGIN + (BAND + Ht) + GUTTER
               + (BAND + hC) + GUTTER + (BAND + hD))
    canvas = Image.new("RGB", (TARGET_W, total_h), "white")
    draw = ImageDraw.Draw(canvas); font = _font()
    y = MARGIN
    _stamp(draw, font, "A", MARGIN, y)
    canvas.paste(A.resize((wA, Ht), Image.LANCZOS), (MARGIN, y + BAND))
    xB = MARGIN + wA + GUTTER
    _stamp(draw, font, "B", xB, y)
    canvas.paste(B.resize((wB, Ht), Image.LANCZOS), (xB, y + BAND))
    y += BAND + Ht + GUTTER
    _stamp(draw, font, "C", MARGIN, y)
    canvas.paste(C.resize((inner_w, hC), Image.LANCZOS), (MARGIN, y + BAND))
    y += BAND + hC + GUTTER
    _stamp(draw, font, "D", MARGIN, y)
    canvas.paste(D.resize((inner_w, hD), Image.LANCZOS), (MARGIN, y + BAND))
    canvas.save(out_path, dpi=(300, 300))
    return canvas.size


P_FLIP_AVG = PANELS / "p_flip_avg.png"
P_CARE_BARS = PANELS / "p_care_intensity_bars.png"
P_CARE_BARS_WIDE = PANELS / "p_care_intensity_bars_wide.png"


def variant4(out_path):
    """Decision-stability reframe (Cohen's-d framing story moves to Figs 3-4),
    THREE equal-height rows all at the A|B row height:
        A concordance / TOST | B flip-rate stable, averaged over 6 LLMs   (top row)
        C tier-shift heatmap                            (full width, scaled to row height)
        D advanced-treatment + de-escalation, bars      (full width, wide regen -> row height)
    """
    D_src = P_CARE_BARS_WIDE if P_CARE_BARS_WIDE.exists() else P_CARE_BARS
    A, B, C, D = [Image.open(s).convert("RGB")
                  for s in (P_CONC, P_FLIP_AVG, P_HEAT, D_src)]
    aA, aB = A.size[0] / A.size[1], B.size[0] / B.size[1]
    inner_w = TARGET_W - 2 * MARGIN
    Ht = round((inner_w - GUTTER) / (aA + aB))        # common row height (A|B shared)
    wA, wB = round(aA * Ht), round(aB * Ht)
    # C and D both fill full width at the SAME row height Ht (C stretched ~8%,
    # D regenerated at ~= full-width aspect so it fills natively).
    total_h = 2 * MARGIN + 3 * (BAND + Ht) + 2 * GUTTER
    canvas = Image.new("RGB", (TARGET_W, total_h), "white")
    draw = ImageDraw.Draw(canvas); font = _font()
    y = MARGIN
    _stamp(draw, font, "A", MARGIN, y)
    canvas.paste(A.resize((wA, Ht), Image.LANCZOS), (MARGIN, y + BAND))
    xB = MARGIN + wA + GUTTER
    _stamp(draw, font, "B", xB, y)
    canvas.paste(B.resize((wB, Ht), Image.LANCZOS), (xB, y + BAND))
    y += BAND + Ht + GUTTER
    _stamp(draw, font, "C", MARGIN, y)
    canvas.paste(C.resize((inner_w, Ht), Image.LANCZOS), (MARGIN, y + BAND))
    y += BAND + Ht + GUTTER
    _stamp(draw, font, "D", MARGIN, y)
    canvas.paste(D.resize((inner_w, Ht), Image.LANCZOS), (MARGIN, y + BAND))
    canvas.save(out_path, dpi=(300, 300))
    return canvas.size


if __name__ == "__main__":
    for s in (P_CONC, P_DISS, P_CARE, P_HEAT):
        if not s.exists():
            raise SystemExit(f"missing panel: {s}")
    s1 = variant1(OUT / "Figure2_decision_stability_DRAFT_v1.png")
    s2 = variant2(OUT / "Figure2_decision_stability_DRAFT_v2.png")
    s3 = variant3(OUT / "Figure2_decision_stability_DRAFT_v3.png")
    print(f"v1 (A|B top, C full bottom)      -> {s1[0]}x{s1[1]}px")
    print(f"v2 (A full, B full; C->suppl.)   -> {s2[0]}x{s2[1]}px")
    print(f"v3 (A|B, C diss, D heatmap)      -> {s3[0]}x{s3[1]}px")
    if P_FLIP_AVG.exists():
        s4 = variant4(OUT / "Figure2_decision_stability_DRAFT_v4.png")
        print(f"v4 (A conc|B flipavg, C heat, D care) -> {s4[0]}x{s4[1]}px")
