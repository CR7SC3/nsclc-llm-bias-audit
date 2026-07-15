"""Figure 4 (companion) — provenance of the REAL notes.

The real-note replication uses 40 open-access NSCLC case reports from PubMed
Central. This figure shows where they come from: publisher/journal source, note
length, and open-access license. Source: data/processed/pmc_nsclc_manifest.json.

Output -> figures/manuscript/fig4_pmc_provenance.png
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
    "10.3389": "Frontiers", "10.21037": "AME", "10.1097": "Wolters Kluwer",
    "10.12659": "Am J Case Rep", "10.1093": "Oxford", "10.2169": "Jpn Soc Int Med",
    "10.7759": "Cureus", "10.5761": "other", "10.3892": "Spandidos",
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

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5.2),
                                 gridspec_kw={"width_ratios": [1.15, 1]})

    # Panel A: publisher / journal source
    items = pubs.most_common()
    labels = [k for k, _ in items][::-1]
    vals = [v for _, v in items][::-1]
    y = np.arange(len(labels))
    a1.barh(y, vals, color="#3B7DA8", edgecolor="k", linewidth=0.4)
    for i, v in enumerate(vals):
        a1.text(v + 0.15, i, str(v), va="center", fontsize=10)
    a1.set_yticks(y); a1.set_yticklabels(labels)
    a1.set_xlabel("Number of case reports")
    a1.set_title("Journal / publisher source", fontweight="bold")
    a1.set_xlim(0, max(vals) + 1.5)

    # Panel B: note-length distribution
    a2.hist(chars, bins=10, color="#6FA36F", edgecolor="k", linewidth=0.5)
    med = np.median(chars)
    a2.axvline(med, color="k", ls="--", lw=1.2)
    a2.text(med, a2.get_ylim()[1] * 0.9, f" median {med:.1f}k chars", fontsize=10)
    a2.set_xlabel("Note length (thousands of characters)")
    a2.set_ylabel("Case reports")
    a2.set_title("Real clinical narratives, substantial length", fontweight="bold")

    lic_str = ",  ".join(f"{k}: {v}" for k, v in lic.most_common())
    fig.suptitle("Where the real notes come from: 40 open-access PubMed Central NSCLC "
                 "case reports\n" + lic_str, fontsize=12, fontweight="bold", y=1.02)
    fig.tight_layout(rect=(0, 0, 1, 0.99))
    fig.savefig(OUT / "fig4_pmc_provenance.png", dpi=150, bbox_inches="tight")
    print("wrote", OUT / "fig4_pmc_provenance.png")
    print("publishers:", dict(pubs)); print("licenses:", dict(lic))


if __name__ == "__main__":
    main()
