"""Concordance-stability heatmap: NCCN adherence change per (model x demographic variant).

Reimagines the Fig 2A concordance bars as a 6-model x 29-variant heatmap. Each cell is the
mean-adherence delta (0-3 NCCN adherence ordinal) of a variant versus that model's
no-demographics reference; BH-significant cells (q<0.05, per model) are starred. A near-
uniform near-zero field is the point: the treatment decision is stable under demographic
relabeling. Reads the six {BASE}{SUF}_adherence.csv files (delta, q_value_bh columns).

Writes standalone figures/manuscript/Fig_concordance_heatmap.png (+pdf) and a titleless
panel figures/manuscript_combined/panels/p_concordance_heatmap.png.
"""
from pathlib import Path
import sys
import csv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

from plots.plot_publishable_nsclc import MODELS, ML, SUF, BASE

MAN = Path("figures/manuscript"); MAN.mkdir(parents=True, exist_ok=True)
PANELS = Path("figures/manuscript_combined/panels"); PANELS.mkdir(parents=True, exist_ok=True)

# grouped variant order (controls/race -> insurance/SES -> housing/geography -> identity)
ORDER = [
    "white_male_private", "black_race_only", "hispanic_race_only", "asian_race_only",
    "native_american_race_only", "middle_eastern_race_only", "multiracial_race_only",
    "uninsured_only", "underinsured_only", "medicaid_only", "medicare_only",
    "medicare_advantage_only", "low_income_patient", "high_income_patient",
    "black_female_medicaid", "latina_female_uninsured", "black_female_private",
    "white_female_medicaid", "low_income_black", "black_unhoused", "unhoused_patient",
    "rural_patient", "small_community_hospital", "immigrant_patient",
    "limited_english_patient", "elderly_patient_75", "non_binary_patient",
    "transgender_woman", "gay_male_patient",
]
NICE = {v: v.replace("_only", "").replace("_patient", "").replace("_", " ") for v in ORDER}


def read_model(suffix):
    """{variant: (delta, q)} for a model."""
    p = Path(f"{BASE}{suffix}_adherence.csv")
    out = {}
    if not p.exists():
        return out
    for r in csv.DictReader(open(p)):
        try:
            q = float(r["q_value_bh"]) if r["q_value_bh"] not in ("", None) else np.nan
        except (ValueError, TypeError):
            q = np.nan
        try:
            out[r["variant"]] = (float(r["delta"]), q)
        except (ValueError, TypeError):
            pass
    return out


def main():
    data = {m: read_model(SUF[m]) for m in MODELS}
    variants = [v for v in ORDER if all(v in data[m] for m in MODELS)]
    mat = np.array([[data[m][v][0] for v in variants] for m in MODELS])   # (models, variants)
    qmat = np.array([[data[m][v][1] for v in variants] for m in MODELS])
    nsig = int(np.nansum(qmat < 0.05))

    vmax = max(0.15, float(np.abs(mat).max()))
    norm = TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)

    fig, ax = plt.subplots(figsize=(11.2, 3.6))
    im = ax.imshow(mat, cmap="RdBu_r", norm=norm, aspect="auto")
    ax.set_xticks(range(len(variants)))
    ax.set_xticklabels([NICE[v] for v in variants], rotation=45, ha="right", fontsize=7.4)
    ax.set_yticks(range(len(MODELS)))
    ax.set_yticklabels([ML[m] for m in MODELS], fontsize=8.6)
    # star BH-significant cells
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            if np.isfinite(qmat[i, j]) and qmat[i, j] < 0.05:
                ax.text(j, i, "*", ha="center", va="center", fontsize=11,
                        color="black", fontweight="bold")
    ax.set_xticks(np.arange(-.5, len(variants), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(MODELS), 1), minor=True)
    ax.grid(which="minor", color="white", lw=1.2)
    ax.tick_params(which="both", length=0)
    cb = fig.colorbar(im, ax=ax, shrink=0.85, pad=0.012)
    cb.set_label("Δ mean NCCN adherence vs no-demographics\n(0–3 ordinal; + = more concordant)",
                 fontsize=7.8)
    ax.set_title(f"Adherence is stable under demographic relabeling  "
                 f"({nsig}/{mat.size} model×variant cells BH-significant)",
                 fontsize=10.5, fontweight="bold", loc="left", pad=8)
    fig.tight_layout()
    fig.savefig(MAN / "Fig_concordance_heatmap.png", dpi=200, bbox_inches="tight")
    fig.savefig(MAN / "Fig_concordance_heatmap.pdf", bbox_inches="tight")

    # panel version: short descriptive title (parity with panels B/C); the finding
    # ("1/174 BH-significant") moves to the caption.
    ax.set_title("Guideline concordance", fontsize=11, fontweight="bold", loc="left", pad=8)
    fig.savefig(PANELS / "p_concordance_heatmap.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {MAN/'Fig_concordance_heatmap.png'}  ({nsig}/{mat.size} cells BH-sig)")


if __name__ == "__main__":
    main()
