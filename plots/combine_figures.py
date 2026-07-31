#!/usr/bin/env python3
"""Combine individual manuscript plots into the locked 5-figure architecture.

Method-A "paste" composite (native-resolution PIL): each source PNG becomes a
panel; bold A/B/C/D letters are stamped top-left of each panel on a white pad.

Panels are drawn from TITLELESS source plots in `figures/manuscript_combined/panels/`
(regenerated with banner titles/footnotes suppressed — those belong in the caption).
Figure 1's two BioRender schematics have no baked-in titles and are used as-is.

Output: figures/manuscript_combined/
"""
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
MAN = ROOT / "figures" / "manuscript"
PANELS = ROOT / "figures" / "manuscript_combined" / "panels"   # titleless panels
OUT = ROOT / "figures" / "manuscript_combined"
OUT.mkdir(parents=True, exist_ok=True)

ARIAL_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

# Each figure: (out_filename, [source image paths in row-major order], rows, cols)
FIGURES = [
    ("Figure1_study_design.png",
     [OUT / "Fig1A_Experimental_Design_v2.png", MAN / "Fig02_counterfactual_design.png"], 2, 1, False, True),
    # Fig 2 = decision-invariance only (A concordance | B flip-avg, C heatmap full width);
    # the care-intensity panel moved out to its own Figure 3 (plot_fig3_care_intensity.py).
    ("Figure2_decision_stability.png",
     [PANELS / "p_concordance_stability.png", PANELS / "p_flip_avg.png",
      PANELS / "p_flip_heatmap.png"], 2, 1),
    # Figure3_care_intensity.png is built standalone by plot_fig3_care_intensity.py.
    ("Figure4_ses_not_race.png",
     [PANELS / "p_volcano.png", PANELS / "p_intermodel.png",
      PANELS / "p_tier_bias.png"], 3, 1),
    ("Figure5_stigma_anatomy.png",
     [PANELS / "p_soft_split_avg.png", PANELS / "p_stigma_breakdown_avg.png",
      PANELS / "p_gradient.png"], 2, 2, True),
    ("Figure6_robustness_precision_filter.png",
     [PANELS / "p_template.png", PANELS / "p_pmc.png",
      PANELS / "p_natural.png", PANELS / "p_bias_tree.png"], 2, 2, True),
]

TARGET_W = 2600
MARGIN = 70
GUTTER = 55
BAND = 90          # per-panel header strip that holds the panel letter (no overlap)
TRIM_PAD = 24      # white padding kept around content after border auto-trim


def trim_white(im, pad=TRIM_PAD):
    """Crop the surrounding white border (BioRender exports ship generous margins),
    then re-pad uniformly so panel content sits close to its box without touching it."""
    rgb = im.convert("RGB")
    bg = Image.new("RGB", rgb.size, (255, 255, 255))
    diff = ImageChops.difference(rgb, bg)
    bbox = diff.getbbox()
    if bbox is None:
        return im
    cropped = im.crop(bbox)
    out = Image.new("RGB", (cropped.size[0] + 2 * pad, cropped.size[1] + 2 * pad), "white")
    out.paste(cropped, (pad, pad))
    return out


def composite(sources, rows, cols, out_path, justify=False, trim=False):
    if justify:
        return composite_justified(sources, rows, cols, out_path)
    imgs = [Image.open(s).convert("RGB") for s in sources]
    if trim:
        imgs = [trim_white(im) for im in imgs]
    inner_w = TARGET_W - 2 * MARGIN - (cols - 1) * GUTTER
    cell_w = inner_w // cols
    resized = []
    for im in imgs:
        w, h = im.size
        resized.append(im.resize((cell_w, round(h * cell_w / w)), Image.LANCZOS))
    while len(resized) < rows * cols:
        resized.append(None)
    # cell height = letter band + image; row height = tallest cell in the row
    row_h = []
    for r in range(rows):
        band = [resized[r * cols + c] for c in range(cols) if resized[r * cols + c]]
        row_h.append(BAND + max((im.size[1] for im in band), default=0))
    total_h = 2 * MARGIN + sum(row_h) + (rows - 1) * GUTTER
    canvas = Image.new("RGB", (TARGET_W, total_h), "white")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(ARIAL_BOLD, size=max(56, TARGET_W // 34))

    idx = 0
    y = MARGIN
    for r in range(rows):
        x = MARGIN
        for c in range(cols):
            im = resized[r * cols + c]
            if im is not None:
                letter = chr(ord("A") + idx)
                bb = draw.textbbox((0, 0), letter, font=font)
                draw.text((x, y - bb[1]), letter, fill="black", font=font)  # in the band
                canvas.paste(im, (x, y + BAND))                              # image below band
            x += cell_w + GUTTER
            idx += 1
        y += row_h[r] + GUTTER
    canvas.save(out_path, dpi=(300, 300))
    return canvas.size


def composite_justified(sources, rows, cols, out_path):
    """Row-justified layout: within each row, panels share one height and their widths
    vary to fill the row exactly (natural aspect preserved). Eliminates the vertical
    white space that a fixed equal-width grid leaves under a row's shorter panel."""
    imgs = [Image.open(s).convert("RGB") for s in sources]
    while len(imgs) < rows * cols:
        imgs.append(None)
    inner_w = TARGET_W - 2 * MARGIN - (cols - 1) * GUTTER
    # per-row layout: solve for the common height H that fills inner_w
    layout = []          # list of rows; each row is a list of (img, w, h)
    for r in range(rows):
        row_imgs = [imgs[r * cols + c] for c in range(cols) if imgs[r * cols + c] is not None]
        aspects = [im.size[0] / im.size[1] for im in row_imgs]
        gutters = (len(row_imgs) - 1) * GUTTER
        H = (inner_w - gutters) / sum(aspects)
        layout.append([(im, round(a * H), round(H)) for im, a in zip(row_imgs, aspects)])
    row_h = [BAND + (row[0][2] if row else 0) for row in layout]
    total_h = 2 * MARGIN + sum(row_h) + (rows - 1) * GUTTER
    canvas = Image.new("RGB", (TARGET_W, total_h), "white")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(ARIAL_BOLD, size=max(56, TARGET_W // 34))

    idx = 0
    y = MARGIN
    for r in range(rows):
        x = MARGIN
        for im, w, h in layout[r]:
            letter = chr(ord("A") + idx)
            bb = draw.textbbox((0, 0), letter, font=font)
            draw.text((x, y - bb[1]), letter, fill="black", font=font)
            canvas.paste(im.resize((w, h), Image.LANCZOS), (x, y + BAND))
            x += w + GUTTER
            idx += 1
        y += row_h[r] + GUTTER
    canvas.save(out_path, dpi=(300, 300))
    return canvas.size


def composite_fig2_Lshape(sources, out_path):
    """Bespoke Figure 2 layout: A (concordance) over B (dissociation) in a left column,
    C (care intensity) as a tall panel filling a right column. Left/right column widths
    are solved so both columns share the same total height — wide-and-short, no dead
    space under B. sources = [A, B, C] in that order."""
    A, B, C = [Image.open(s).convert("RGB") for s in sources]
    inner_w = TARGET_W - 2 * MARGIN - GUTTER          # two columns, one gutter between
    aA, aB, aC = (im.size[0] / im.size[1] for im in (A, B, C))
    kL = 1 / aA + 1 / aB                              # left column height per unit width
    # left_h(left_w) == right_h(inner_w - left_w); solve for left_w:
    left_w = round((inner_w / aC - BAND - GUTTER) / (kL + 1 / aC))
    right_w = inner_w - left_w
    hA, hB, hC = round(left_w / aA), round(left_w / aB), round(right_w / aC)
    left_h = 2 * BAND + GUTTER + hA + hB
    right_h = BAND + hC
    total_h = 2 * MARGIN + max(left_h, right_h)
    canvas = Image.new("RGB", (TARGET_W, total_h), "white")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(ARIAL_BOLD, size=max(56, TARGET_W // 34))

    def stamp(letter, x, y):
        bb = draw.textbbox((0, 0), letter, font=font)
        draw.text((x, y - bb[1]), letter, fill="black", font=font)

    # left column: A over B
    x = MARGIN
    stamp("A", x, MARGIN)
    canvas.paste(A.resize((left_w, hA), Image.LANCZOS), (x, MARGIN + BAND))
    yB = MARGIN + BAND + hA + GUTTER
    stamp("B", x, yB)
    canvas.paste(B.resize((left_w, hB), Image.LANCZOS), (x, yB + BAND))
    # right column: C
    xr = MARGIN + left_w + GUTTER
    stamp("C", xr, MARGIN)
    canvas.paste(C.resize((right_w, hC), Image.LANCZOS), (xr, MARGIN + BAND))

    canvas.save(out_path, dpi=(300, 300))
    return canvas.size


def composite_fig2_stack(sources, out_path):
    """Figure 2 layout (3 panels, 2 rows):
        A  concordance %  |  B  care-intensity (top row, justified to a shared height)
        C  treatment-direction heatmap         (full width, bottom, landscape)
    sources = [A, B, C]."""
    A, B, C = [Image.open(s).convert("RGB") for s in sources]
    aA, aB, aC = (im.size[0] / im.size[1] for im in (A, B, C))
    inner_w = TARGET_W - 2 * MARGIN
    Ht = (inner_w - GUTTER) / (aA + aB)               # row 1: A|B share a common height
    wA, wB, Ht = round(aA * Ht), round(aB * Ht), round(Ht)
    hC = round(inner_w / aC)                          # row 2: C full width
    total_h = 2 * MARGIN + (BAND + Ht) + GUTTER + (BAND + hC)
    canvas = Image.new("RGB", (TARGET_W, total_h), "white")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(ARIAL_BOLD, size=max(56, TARGET_W // 34))

    def stamp(letter, x, y):
        bb = draw.textbbox((0, 0), letter, font=font)
        draw.text((x, y - bb[1]), letter, fill="black", font=font)

    # row 1: A | B justified to a shared height
    y = MARGIN
    stamp("A", MARGIN, y)
    canvas.paste(A.resize((wA, Ht), Image.LANCZOS), (MARGIN, y + BAND))
    xB = MARGIN + wA + GUTTER
    stamp("B", xB, y)
    canvas.paste(B.resize((wB, Ht), Image.LANCZOS), (xB, y + BAND))
    # row 2: C full width
    y += BAND + Ht + GUTTER
    stamp("C", MARGIN, y)
    canvas.paste(C.resize((inner_w, hC), Image.LANCZOS), (MARGIN, y + BAND))

    canvas.save(out_path, dpi=(300, 300))
    return canvas.size


def composite_fig2(sources, out_path):
    """Figure 2 = decision invariance, two rows:
        A concordance / TOST | B flip-rate stable, averaged over 6 LLMs   (top row)
        C tier-shift heatmap                                 (full width, native aspect)
    The care-intensity panel moved out to Figure 3.
    sources = [A concordance, B flip_avg, C heatmap]."""
    A, B, C = [Image.open(s).convert("RGB") for s in sources]
    aA, aB, aC = (im.size[0] / im.size[1] for im in (A, B, C))
    inner_w = TARGET_W - 2 * MARGIN
    Ht = round((inner_w - GUTTER) / (aA + aB))        # top row A|B shared height
    wA, wB = round(aA * Ht), round(aB * Ht)
    hC = round(inner_w / aC)                           # heatmap full width, native aspect
    total_h = 2 * MARGIN + (BAND + Ht) + GUTTER + (BAND + hC)
    canvas = Image.new("RGB", (TARGET_W, total_h), "white")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(ARIAL_BOLD, size=max(56, TARGET_W // 34))

    def stamp(letter, x, y):
        bb = draw.textbbox((0, 0), letter, font=font)
        draw.text((x, y - bb[1]), letter, fill="black", font=font)

    y = MARGIN
    stamp("A", MARGIN, y)
    canvas.paste(A.resize((wA, Ht), Image.LANCZOS), (MARGIN, y + BAND))
    xB = MARGIN + wA + GUTTER
    stamp("B", xB, y)
    canvas.paste(B.resize((wB, Ht), Image.LANCZOS), (xB, y + BAND))
    y += BAND + Ht + GUTTER
    stamp("C", MARGIN, y)
    canvas.paste(C.resize((inner_w, hC), Image.LANCZOS), (MARGIN, y + BAND))
    canvas.save(out_path, dpi=(300, 300))
    return canvas.size


def composite_fig3_T1B2(sources, out_path):
    """Figure 3 layout: A (volcano) spans the full width on top; B (intermodel) and
    C (tier bias) share the bottom row, justified to a common height that fills the
    width. sources = [top, bottom_left, bottom_right]."""
    top, bl, br = [Image.open(s).convert("RGB") for s in sources]
    inner_w = TARGET_W - 2 * MARGIN
    aT, aBL, aBR = (im.size[0] / im.size[1] for im in (top, bl, br))
    hT = round(inner_w / aT)                                   # top: full width
    Hb = (inner_w - GUTTER) / (aBL + aBR)                      # bottom: shared height
    wBL, wBR, hB = round(aBL * Hb), round(aBR * Hb), round(Hb)
    total_h = 2 * MARGIN + BAND + hT + GUTTER + BAND + hB
    canvas = Image.new("RGB", (TARGET_W, total_h), "white")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(ARIAL_BOLD, size=max(56, TARGET_W // 34))

    def stamp(letter, x, y):
        bb = draw.textbbox((0, 0), letter, font=font)
        draw.text((x, y - bb[1]), letter, fill="black", font=font)

    # top row: A full width
    stamp("A", MARGIN, MARGIN)
    canvas.paste(top.resize((inner_w, hT), Image.LANCZOS), (MARGIN, MARGIN + BAND))
    # bottom row: B | C
    yb = MARGIN + BAND + hT + GUTTER
    stamp("B", MARGIN, yb)
    canvas.paste(bl.resize((wBL, hB), Image.LANCZOS), (MARGIN, yb + BAND))
    xr = MARGIN + wBL + GUTTER
    stamp("C", xr, yb)
    canvas.paste(br.resize((wBR, hB), Image.LANCZOS), (xr, yb + BAND))

    canvas.save(out_path, dpi=(300, 300))
    return canvas.size


def composite_fig5_uniform(sources, out_path):
    """Figure 5 layout: 2x2 of A|B / C|D where every panel is pasted at the SAME
    height, so all four plot boxes are equal-height and their x-axes sit on a common
    line within each row. Source panels ship with fixed geometry (identical figure
    height + identical axes rectangle), so equal-height scaling aligns the axes.

    Rows pair one single-axis panel with one two-axis panel (A+B, C+D) — identical
    total native width — so both rows fill the canvas to the same right edge with no
    ragged margin. sources = [A, B, C, D]."""
    A, B, C, D = [Image.open(s).convert("RGB") for s in sources]
    inner_w = TARGET_W - 2 * MARGIN
    sw, dw, nh = A.size[0], B.size[0], A.size[1]      # single width, double width, common height
    scale = (inner_w - GUTTER) / (sw + dw)            # single + gutter + double == inner_w
    Ws, Wd, H = round(sw * scale), round(dw * scale), round(nh * scale)
    total_h = 2 * MARGIN + 2 * (BAND + H) + GUTTER
    canvas = Image.new("RGB", (TARGET_W, total_h), "white")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(ARIAL_BOLD, size=max(56, TARGET_W // 34))

    def stamp(letter, x, y):
        bb = draw.textbbox((0, 0), letter, font=font)
        draw.text((x, y - bb[1]), letter, fill="black", font=font)

    rows = [[("A", A, Ws), ("B", B, Wd)], [("C", C, Wd), ("D", D, Ws)]]
    y = MARGIN
    for row in rows:
        x = MARGIN
        for letter, im, w in row:
            stamp(letter, x, y)
            canvas.paste(im.resize((w, H), Image.LANCZOS), (x, y + BAND))
            x += w + GUTTER
        y += BAND + H + GUTTER
    canvas.save(out_path, dpi=(300, 300))
    return canvas.size


if __name__ == "__main__":
    for entry in FIGURES:
        name, srcs, rows, cols = entry[0], entry[1], entry[2], entry[3]
        justify = entry[4] if len(entry) > 4 else False
        trim = entry[5] if len(entry) > 5 else False
        missing = [str(s) for s in srcs if not Path(s).exists()]
        if missing:
            print(f"SKIP {name}: missing {missing}")
            continue
        if name == "Figure2_decision_stability.png":
            size = composite_fig2(srcs, OUT / name)
        elif name == "Figure4_ses_not_race.png":
            size = composite_fig3_T1B2(srcs, OUT / name)
        elif name == "Figure6_robustness_precision_filter.png":
            size = composite_fig5_uniform(srcs, OUT / name)
        else:
            size = composite(srcs, rows, cols, OUT / name, justify=justify, trim=trim)
        print(f"{name:44s} {rows}x{cols}  {len(srcs)} panels  -> {size[0]}x{size[1]}px")
    print(f"\nWrote combined figures to {OUT}")
