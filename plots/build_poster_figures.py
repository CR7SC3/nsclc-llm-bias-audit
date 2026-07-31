"""Pad the six chosen poster panels onto an identical white canvas (no distortion)
so they tile as a clean 2-column x 3-row grid. Each source is scaled to FIT inside
the common box (aspect preserved) and centered; nothing is stretched. Outputs are
numbered in reading order. Run: python3 plots/build_poster_figures.py
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PANELS = ROOT / "figures/manuscript_combined/panels"
OUT = ROOT / "poster_figures"; OUT.mkdir(parents=True, exist_ok=True)

# common canvas: width narrowed 25% (2000 -> 1500) for a tighter poster column;
# figures are contained (aspect preserved), never stretched.
BOX_W, BOX_H = 1500, 1250
PAD = 24  # inner white margin so nothing touches the cell edge

# (source path, output name in reading order)
SOURCES = [
    (PANELS / "p_concordance_stability.png", "1_concordance_decision.png"),
    (PANELS / "p_flip_avg.png",              "2_flip_rate.png"),
    (PANELS / "p_care_intensity_bars.png",   "3_care_intensity.png"),
    (PANELS / "p_gradient.png",              "4_stigma_gradient.png"),
    (OUT / "_raw_bias_by_axis_vertical.png", "5_bias_by_axis.png"),
    (PANELS / "p_template.png",              "6_template_control.png"),
]


def pad_to_box(src: Path, dst: Path):
    im = Image.open(src).convert("RGBA")
    avail_w, avail_h = BOX_W - 2 * PAD, BOX_H - 2 * PAD
    scale = min(avail_w / im.width, avail_h / im.height)
    new = (max(1, round(im.width * scale)), max(1, round(im.height * scale)))
    im = im.resize(new, Image.LANCZOS)
    canvas = Image.new("RGBA", (BOX_W, BOX_H), (255, 255, 255, 255))
    off = ((BOX_W - new[0]) // 2, (BOX_H - new[1]) // 2)
    canvas.paste(im, off, im)
    canvas.convert("RGB").save(dst, "PNG")
    return new


for src, name in SOURCES:
    if not src.exists():
        print(f"MISSING: {src}")
        continue
    dims = pad_to_box(src, OUT / name)
    print(f"{name:28s} <- {src.name:34s} fit {dims[0]}x{dims[1]} on {BOX_W}x{BOX_H}")

print(f"\nAll six written to {OUT} at a uniform {BOX_W}x{BOX_H}px canvas.")
