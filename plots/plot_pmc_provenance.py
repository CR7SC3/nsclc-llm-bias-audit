"""Figure 4 (companion) — provenance of the REAL notes.

The real-note replication uses 40 open-access NSCLC case reports from PubMed
Central. This figure shows where they come from: publisher/journal source, note
length, and open-access license. Source: data/processed/pmc_nsclc_manifest.json.

Output -> figures/manuscript/FigS01_pmc_note_provenance.png
Run:  python3 plots/plot_pmc_provenance.py
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import json
import re
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt

OUT = Path("figures/manuscript"); OUT.mkdir(parents=True, exist_ok=True)
PUB = {
    "10.1186": "BMC", "10.1007": "Springer", "10.3390": "MDPI", "10.1016": "Elsevier",
    "10.1002": "Wiley", "10.2147": "Dove Press", "10.1159": "Karger",
    "10.3389": "Frontiers", "10.21037": "AME Publishing", "10.1097": "Wolters Kluwer",
    "10.12659": "American Journal of Case Reports", "10.1093": "Oxford University Press",
    "10.2169": "Japanese Society of Internal Medicine",
    "10.7759": "Cureus", "10.5761": "Annals of Thoracic and Cardiovascular Surgery",
    "10.3892": "Spandidos",
}


def main():
    man = json.loads(Path("data/processed/pmc_nsclc_manifest.json").read_text())
    pubs, lic, chars = Counter(), Counter(), []
    for it in man:
        pre = (it.get("doi", "") or "").split("/")[0]
        pubs[PUB.get(pre, "other")] += 1
        m = re.search(r"licenses/([a-z-]+)/([0-9.]+)", it.get("license", "") or "")
        lic["CC " + m.group(1).upper() + " " + m.group(2) if m else "other"] += 1
        chars.append(it.get("n_chars", 0) / 1000)  # k chars

    plt.rcParams.update({"font.family": "sans-serif",
                         "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"], "font.size": 12})
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 4.8),
                                 gridspec_kw={"width_ratios": [1.25, 1]})

    # A: publisher source (ties broken alphabetically so the order is stable)
    items = sorted(pubs.items(), key=lambda kv: (-kv[1], kv[0]))
    labels = [k for k, _ in items][::-1]
    vals = [v for _, v in items][::-1]
    y = np.arange(len(labels))
    a1.barh(y, vals, color="#adadad", edgecolor="k", linewidth=0.5)
    for i, v in enumerate(vals):
        a1.text(v + 0.2, i, str(v), va="center", fontsize=11)
    a1.set_yticks(y); a1.set_yticklabels(labels, fontsize=11.5)
    a1.tick_params(axis="y", length=0)
    a1.set_xlabel("Case reports, No.")
    a1.set_xlim(0, max(vals) + 2)
    a1.set_xticks(range(0, max(vals) + 2, 2))

    # B: note length
    a2.hist(chars, bins=10, color="#E69F00", edgecolor="k", linewidth=0.5)
    med = np.median(chars)
    a2.axvline(med, color="k", ls="--", lw=1.2)
    a2.text(med + 0.15, a2.get_ylim()[1] * 0.93, f"Median, {int(med * 1000):,}", fontsize=11, va="top")   # matches eMethods (6,622)
    a2.set_xlabel("Note length, thousands of characters")
    a2.set_ylabel("Case reports, No.")
    for ax in (a1, a2):
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    fig.tight_layout(w_pad=2.5, rect=(0, 0, 1, 0.95))
    fig.text(0.005, 0.97, "A", fontsize=16, fontweight="bold", va="top")
    fig.text(a2.get_position().x0 - 0.06, 0.97, "B", fontsize=16, fontweight="bold", va="top")
    fig.savefig(OUT / "FigS01_pmc_note_provenance.png", dpi=200, bbox_inches="tight")
    print("median chars:", np.median([c * 1000 for c in chars]), "range:", min(chars) * 1000, max(chars) * 1000)
    print("wrote", OUT / "FigS01_pmc_note_provenance.png")
    print("publishers:", dict(pubs)); print("licenses:", dict(lic))


if __name__ == "__main__":
    main()
