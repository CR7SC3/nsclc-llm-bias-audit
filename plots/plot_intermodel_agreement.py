"""Inter-model agreement (supplement) — do the six vendors respond to the same
demographic labels the same way?

Robustness argument that the framing signal is a shared cross-vendor construct, not
one model's quirk. For each model we take its vector of label-induced framing effects
(Cohen's d vs no-demographics) across the 29 demographic variants, then compute the
Spearman rank correlation between every pair of models.

Why per-VARIANT deltas and Spearman (not per-case Pearson): correlating raw per-case
stigma across models can be inflated purely by shared case difficulty (both models
reacting to the objectively sickest notes). Correlating the induced effect ACROSS
demographic variants removes the shared case baseline — the axis is the demographic
label, not the note — so a high correlation means shared demographic RESPONSE, which
is the construct we care about. Spearman (rank) is robust to the models' very
different effect magnitudes.

Reads the six *_soft_intensity.csv files (same source as the forest / volcano).
Output -> figures/manuscript/FigS_intermodel_agreement.png
Run:  python3 plots/plot_intermodel_agreement.py
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import csv
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
from scipy.cluster.hierarchy import linkage, leaves_list
from scipy.spatial.distance import squareform

from plots.plot_publishable_nsclc import MODELS, ML, SUF, BASE

OUT = Path("figures/manuscript"); OUT.mkdir(parents=True, exist_ok=True)


def read_d(suffix):
    """{variant: cohens_d} for a model (excluding the reference)."""
    p = Path(f"{BASE}{suffix}_soft_intensity.csv")
    out = {}
    if not p.exists():
        return out
    with open(p, newline="") as fh:
        for r in csv.DictReader(fh):
            if r["variant"] == "no_demographics":
                continue
            try:
                out[r["variant"]] = float(r["cohens_d"])
            except (ValueError, TypeError):
                pass
    return out


def main():
    dvecs = {m: read_d(SUF[m]) for m in MODELS}
    variants = sorted(set.intersection(*[set(dvecs[m]) for m in MODELS]))
    mat = np.array([[dvecs[m][v] for v in variants] for m in MODELS])  # (n_models, n_variants)

    n = len(MODELS)
    corr = np.eye(n)
    for i in range(n):
        for j in range(i + 1, n):
            rho = spearmanr(mat[i], mat[j]).statistic
            corr[i, j] = corr[j, i] = rho

    # hierarchical leaf order (correlation distance) so similar models sit together
    dist = 1 - corr
    np.fill_diagonal(dist, 0.0)
    order = leaves_list(linkage(squareform(dist, checks=False), method="average")) if n > 2 else list(range(n))
    C = corr[np.ix_(order, order)]
    labels = [ML[MODELS[k]] for k in order]

    fig, ax = plt.subplots(figsize=(7.4, 6.2))
    im = ax.imshow(C, cmap="RdBu_r", vmin=-1, vmax=1, aspect="equal")
    ax.set_xticks(range(n)); ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=9)
    ax.set_yticks(range(n)); ax.set_yticklabels(labels, fontsize=9)
    for i in range(n):
        for j in range(n):
            ax.text(j, i, f"{C[i, j]:.2f}", ha="center", va="center", fontsize=9,
                    color="white" if abs(C[i, j]) > 0.6 else "0.15")
    med = np.median(C[np.triu_indices(n, 1)])
    ax.set_title("Vendors share one demographic-response profile\n"
                 f"(Spearman ρ of per-variant induced framing effect; off-diagonal median ρ={med:.2f})",
                 fontsize=11.5, fontweight="bold")
    cb = fig.colorbar(im, ax=ax, shrink=0.82)
    cb.set_label("Spearman ρ across 29 demographic variants")
    fig.tight_layout()
    fig.savefig(OUT / "FigS_intermodel_agreement.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("wrote", OUT / "FigS_intermodel_agreement.png",
          f"(off-diagonal median rho={med:.2f})")


if __name__ == "__main__":
    main()
