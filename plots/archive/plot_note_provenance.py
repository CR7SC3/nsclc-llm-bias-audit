"""Annotated synthetic-note slide: shows a real GENIE-derived note with each
span color-coded by provenance (real GENIE structured field / LLM narrative
scaffold / LLM-generated specific detail not in GENIE). Case GENIE-MSK-P-0012061.

Run:  venv/bin/python plots/plot_note_provenance.py
Out:  figures/manuscript/FigS_note_provenance.png (+ .pdf)
"""
from __future__ import annotations
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch

OUT = Path("figures/manuscript"); OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "figure.dpi": 150, "savefig.bbox": "tight", "figure.facecolor": "white"})

# tier -> (text color, highlight color)
TIER = {
    "REAL":  ("#1E6B3A", "#DCEEE2"),   # green  – real GENIE BPC structured field
    "SCAF":  ("#274C86", "#E1E9F6"),   # blue   – LLM narrative scaffold
    "FAB":   ("#9A5B00", "#F6E8CE"),   # amber  – LLM-generated detail, not in GENIE
    "H":     ("#111111", None),        # section header
}

# note as (text, tier) segments, "\n" starts a new block; headers are ("...","H")
SEG = [
 ("HPI", "H"), ("\n",""),
 ("82-year-old", "REAL"), (" individual with a history of ", "SCAF"),
 ("former tobacco use", "REAL"),
 (", presenting for an initial oncology consultation for newly diagnosed ", "SCAF"),
 ("metastatic non-small cell lung cancer", "REAL"), (". ", "SCAF"),
 ("Two-month history of a persistent non-productive cough and progressive dyspnea on exertion", "FAB"),
 ("; fully ambulatory, ", "SCAF"), ("ECOG performance status 1", "REAL"), (".", "SCAF"),
 ("\n\n",""),
 ("Diagnostic Workup", "H"), ("\n",""),
 ("CT of the chest revealed a ", "SCAF"),
 ("4.5 cm spiculated right-upper-lobe mass with contralateral pulmonary nodules and a moderate right pleural effusion", "FAB"),
 (". CT-guided core-needle biopsy confirmed ", "SCAF"),
 ("adenocarcinoma", "REAL"), ("; ", "SCAF"),
 ("pleural cytology positive", "FAB"), (". ", "SCAF"),
 ("AJCC Stage IV", "REAL"), (" ", "SCAF"), ("(cT3 N0 M1a)", "FAB"),
 ("; ", "SCAF"), ("brain MRI negative for metastases", "REAL"), (".", "SCAF"),
 ("\n\n",""),
 ("Molecular Studies", "H"), ("\n",""),
 ("Next-generation sequencing identified a ", "SCAF"),
 ("MET exon 14 skipping mutation and a KRAS G12C mutation", "REAL"),
 (". Negative for ", "SCAF"),
 ("EGFR, ALK, ROS1, BRAF, RET, NTRK, ERBB2", "REAL"), (". ", "SCAF"),
 ("Tumor mutational burden intermediate", "REAL"), ("; ", "SCAF"),
 ("PD-L1 not tested", "REAL"), (".", "SCAF"),
]

def flow_tokens():
    toks = []
    for text, tier in SEG:
        if text.startswith("\n"):
            for _ in text: toks.append(("\n", tier))
            continue
        parts = text.split(" ")
        for k, w in enumerate(parts):
            if w == "" and k < len(parts):   # preserve spacing between segments
                continue
            toks.append((w, tier))
    return toks

def main():
    fig = plt.figure(figsize=(13.2, 7.0), facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

    ax.text(0.035, 0.965, "Anatomy of a synthetic note",
            fontsize=17, fontweight="bold", color="#1B2444")
    ax.text(0.035, 0.925,
            "One demographics-neutral GENIE BPC case (GENIE-MSK-P-0012061), color-coded by where each fact came from",
            fontsize=10.5, color="#555")

    # legend
    lx = 0.035
    for tier, label in [("REAL", "Real GENIE BPC structured field"),
                        ("SCAF", "LLM narrative scaffold (Gemini-2.5-flash)"),
                        ("FAB", "LLM-generated detail — not in GENIE (disclosed)")]:
        tc, hl = TIER[tier]
        ax.add_patch(Rectangle((lx, 0.862), 0.022, 0.026, facecolor=hl, edgecolor=tc, lw=0.8))
        ax.text(lx + 0.03, 0.875, label, fontsize=9.2, va="center", color=tc, fontweight="bold")
        lx += 0.30

    # note card
    ax.add_patch(FancyBboxPatch((0.03, 0.10), 0.94, 0.70, boxstyle="round,pad=0.008",
                 facecolor="#FBFCFE", edgecolor="#D3DAE4", lw=1.1))

    CW = 0.0092      # char width in axis-x
    SP = CW * 0.9    # space width
    x0, x1 = 0.055, 0.945
    y = 0.755; LH = 0.040
    x = x0
    for w, tier in flow_tokens():
        if w == "\n":
            y -= LH * 0.55; x = x0; continue
        tc, hl = TIER[tier]
        is_h = (tier == "H")
        fs = 11.5 if not is_h else 11.5
        wlen = len(w) * CW + (0.004 if is_h else 0)
        if x + wlen > x1:            # wrap
            y -= LH; x = x0
        if hl:
            ax.add_patch(Rectangle((x - SP*0.4, y - 0.016), wlen + SP*0.3, 0.030,
                         facecolor=hl, edgecolor="none", zorder=1))
        ax.text(x, y, w, fontsize=fs, color=tc, va="center", zorder=2,
                fontweight="bold" if is_h else "normal")
        x += wlen + SP
        if is_h:
            y -= LH * 0.15   # small gap handled by following \n

    ax.text(0.055, 0.055,
            "Real patient = MSK, 82-year-old former smoker.  The real demographics (Asian male) are REMOVED to make the neutral base note; "
            "the 30 demographic variants are injected on top.  Structured fields (green) are GENIE ground truth; the prose that carries them (blue) "
            "and specific clinical details like tumor size or symptom timeline (amber) are model-generated.",
            fontsize=8.4, color="#666", va="top", wrap=True)

    fig.savefig(OUT / "FigS_note_provenance.png", dpi=300)
    fig.savefig(OUT / "FigS_note_provenance.pdf")
    print("wrote", OUT / "FigS_note_provenance.png")

if __name__ == "__main__":
    main()
