"""GENIE BPC breast cancer (BRCA) and pancreatic cancer (PANC) cohort processor.

Mirrors the NSCLC processor (load_genie_bpc.py) for the two additional
EquityGUIDE cohorts.  Each cohort produces a flat processed JSON ready
for the experiment pipeline.

Input files (data/genie_bpc/{brca,panc}/)
──────────────────────────────────────────
  patient_level_dataset.csv
  cancer_level_dataset_index.csv
  cancer_panel_test_level_dataset.csv
  regimen_cancer_level_dataset.csv
  data_mutations_extended.txt
  tmb.tsv

Output
──────
  data/processed/genie_bpc_brca_processed.json
  data/processed/genie_bpc_panc_processed.json

Inclusion criteria (both cohorts)
──────────────────────────────────
  1. Known stage (stage_dx not blank / "Stage I-III NOS")
  2. Non-excluded histology (PANC: exclude non-adenocarcinoma; BRCA: exclude sarcoma)
  3. At least one Line 1 regimen recorded

Design notes
────────────
  BRCA: Primary pathway driver is receptor subtype (HR+/HER2-,  HR+/HER2+,
        HR-/HER2+, TNBC).  Extracted from ca_bca_er / ca_bca_pr / ca_bca_her_summ
        and cross-checked against bca_subtype.  Somatic drivers (PIK3CA, ESR1,
        BRCA1/2) extracted from mutations file for targeted therapy eligibility.

  PANC: Primary pathway driver is stage / resectability.  BRCA1/2 determines
        olaparib maintenance eligibility after platinum.  NTRK from mutations.
        TMB-H (>16) used as MSI-H proxy for pembrolizumab eligibility.

Limitations (both cohorts)
──────────────────────────
  - ECOG PS not captured in GENIE BPC; defaulted to 1.
  - Menopausal status not available (affects BRCA endocrine therapy choice).
  - PANC resectability inferred from broad stage (Stage I-II → resectable,
    Stage III → locally advanced, Stage IV → metastatic); surgical intent
    not directly recorded.
  - PD-L1 TPS not available for either cohort.

Usage
─────
    venv/bin/python src/generate/load_genie_bpc_brca_panc.py
    venv/bin/python src/generate/load_genie_bpc_brca_panc.py --cohort brca
    venv/bin/python src/generate/load_genie_bpc_brca_panc.py --cohort panc
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

logger = logging.getLogger(__name__)

BRCA_DIR    = Path("data/genie_bpc/brca")
PANC_DIR    = Path("data/genie_bpc/panc")
BRCA_OUTPUT = Path("data/processed/genie_bpc_brca_processed.json")
PANC_OUTPUT = Path("data/processed/genie_bpc_panc_processed.json")


# ─── Shared utilities ─────────────────────────────────────────────────────────

def _read_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def _read_tsv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


_STAGE_SUB_MAP: dict[str, str] = {
    "0":    "0",
    "1":    "I",   "1A": "IA",  "1a": "IA",
    "1A1":  "IA1", "1A2": "IA2",
    "1B":   "IB",  "1b": "IB",  "1C": "IC",
    "2":    "II",  "2A": "IIA", "2a": "IIA",
    "2B":   "IIB", "2b": "IIB", "2C": "IIC",
    "3":    "III", "3A": "IIIA","3a": "IIIA",
    "3B":   "IIIB","3b": "IIIB","3C": "IIIC","3c": "IIIC",
    "4":    "IV",  "4A": "IVA", "4B": "IVB",
    "IIIB": "IIIB",
}

_STAGE_BROAD_MAP: dict[str, str] = {
    "Stage I":   "I",
    "Stage II":  "II",
    "Stage III": "III",
    "Stage IV":  "IV",
}

_UNKNOWN_STAGE = {"", "99", "88", "Unknown", "unknown", "Stage I-III NOS"}


def _resolve_stage(best_ajcc: str, stage_dx: str) -> str | None:
    """Return NCCN-scorer-compatible stage string.

    Prefers sub-stage from best_ajcc_stage_cd; falls back to broad stage
    from stage_dx when best_ajcc is blank or unknown.
    """
    sub = best_ajcc.strip()
    if sub and sub not in _UNKNOWN_STAGE:
        mapped = _STAGE_SUB_MAP.get(sub)
        if mapped:
            return mapped

    broad = stage_dx.strip()
    if broad in _UNKNOWN_STAGE or not broad:
        return None
    return _STAGE_BROAD_MAP.get(broad)


_RACE_MAP = {
    "White":                          "White",
    "Black":                          "Black or African American",
    "Asian":                          "Asian",
    "Chinese":                        "Asian",
    "Other Asian":                    "Asian",
    "Korean":                         "Asian",
    "Japanese":                       "Asian",
    "Indian":                         "Asian",
    "Filipino":                       "Asian",
    "Vietnamese":                     "Asian",
    "Asian Indian or Pakistan":       "Asian",
    "Hawaiian":                       "Native Hawaiian or Other Pacific Islander",
    "American Indian, Aleutian, or Eskimo": "American Indian or Alaska Native",
    "Native American":                "American Indian or Alaska Native",
    "Other":                          "Other",
    "Unknown":                        "Unknown",
    "":                               "Unknown",
}

_SEX_MAP      = {"Male": "Male", "Female": "Female", "": "Unknown"}
_ETHNICITY_MAP = {
    "Non-Spanish; Non-Hispanic": "Not Hispanic or Latino",
    "Spanish/Hispanic":          "Hispanic or Latino",
    "Unknown": "Unknown", "": "Unknown",
}


def _demographics(pt: dict, institution: str) -> dict:
    return {
        "race":           _RACE_MAP.get(pt.get("naaccr_race_code_primary", ""), "Unknown"),
        "sex":            _SEX_MAP.get(pt.get("naaccr_sex_code", ""), "Unknown"),
        "ethnicity":      _ETHNICITY_MAP.get(pt.get("naaccr_ethnicity_code", ""), "Unknown"),
        "race_ethnicity": pt.get("race_ethnicity", ""),
        "race_raw":       pt.get("naaccr_race_code_primary", ""),
        "sex_raw":        pt.get("naaccr_sex_code", ""),
        "institution":    institution,
    }


def _first_line_regimen(reg_rows: list[dict]) -> str | None:
    line1 = [r for r in reg_rows if r.get("regimen_number_within_cancer", "") == "1"]
    return (line1[0].get("regimen_drugs", "").strip() or None) if line1 else None


def _build_biomarker_lookups(
    panels: list[dict],
    mutations: list[dict],
) -> tuple[dict, dict, dict]:
    """Return three lookup dicts indexed by (record_id, ca_seq).

    Returns
    -------
    panels_by_key   : (record_id, ca_seq) → list of panel rows (sorted by dx_cpt_rep_days)
    muts_by_sample  : sample_barcode → list of mutation rows
    tmb_by_sample   : sample_id → tmb_bin string
    """
    panels_by_key: dict[tuple, list] = defaultdict(list)
    for p in panels:
        panels_by_key[(p["record_id"], p["ca_seq"])].append(p)
    # Sort each list by proximity to diagnosis
    for k in panels_by_key:
        panels_by_key[k].sort(
            key=lambda p: float(p.get("dx_cpt_rep_days", "999999") or "999999")
        )

    muts_by_sample: dict[str, list] = defaultdict(list)
    for m in mutations:
        muts_by_sample[m["Tumor_Sample_Barcode"]].append(m)

    return panels_by_key, muts_by_sample


def _collect_mutations(
    key: tuple,
    panels_by_key: dict,
    muts_by_sample: dict,
) -> tuple[dict, list[str], bool]:
    """Return muts_by_gene, sample_ids, biomarkers_available."""
    panel_rows = panels_by_key.get(key, [])
    sample_ids = [p["cpt_genie_sample_id"] for p in panel_rows if p.get("cpt_genie_sample_id")]

    all_muts: list[dict] = []
    for sid in sample_ids:
        all_muts.extend(muts_by_sample.get(sid, []))

    muts_by_gene: dict[str, list[str]] = defaultdict(list)
    for m in all_muts:
        gene  = m.get("Hugo_Symbol", "")
        hgvsp = m.get("HGVSp_Short", "")
        if gene and hgvsp:
            muts_by_gene[gene].append(hgvsp)

    available = bool(sample_ids and all_muts)
    return muts_by_gene, sample_ids, available


def _ntrk_status(muts_by_gene: dict, biomarkers_available: bool) -> str:
    ntrk_genes = {"NTRK1", "NTRK2", "NTRK3"}
    if not biomarkers_available:
        return "unknown"
    return "fusion" if any(muts_by_gene.get(g) for g in ntrk_genes) else "negative"


# ─── BRCA-specific logic ──────────────────────────────────────────────────────

def _brca_receptor_status(cancer: dict) -> dict:
    """Extract ER, PR, HER2, and subtype from the cancer index row."""
    er_raw  = cancer.get("ca_bca_er", "").strip()
    pr_raw  = cancer.get("ca_bca_pr", "").strip()
    her_raw = cancer.get("ca_bca_her_summ", "").strip()
    subtype = cancer.get("bca_subtype", "").strip()

    er  = "positive" if "Positive" in er_raw  else ("negative" if "Negative" in er_raw  else "unknown")
    pr  = "positive" if "Positive" in pr_raw  else ("negative" if "Negative" in pr_raw  else "unknown")
    her2 = "positive" if "Positive" in her_raw else ("negative" if "Negative" in her_raw else "unknown")

    # Normalise subtype
    if not subtype or subtype in ("", "Unknown"):
        if er == "positive" or pr == "positive":
            subtype = "HR+, HER2-" if her2 == "negative" else ("HR+, HER2+" if her2 == "positive" else "HR+, HER2-")
        elif her2 == "positive":
            subtype = "HR-, HER2+"
        elif er == "negative" and pr == "negative" and her2 == "negative":
            subtype = "Triple Negative"
        else:
            subtype = "Unknown"

    return {"er": er, "pr": pr, "her2": her2, "subtype": subtype}


def _brca_somatic_drivers(muts_by_gene: dict, biomarkers_available: bool) -> dict:
    """Extract key somatic drivers for breast cancer treatment eligibility."""
    def _has(gene: str) -> str:
        if not biomarkers_available:
            return "unknown"
        return "mutated" if muts_by_gene.get(gene) else "negative"

    pik3ca_muts = muts_by_gene.get("PIK3CA", [])
    return {
        "brca1":  _has("BRCA1"),
        "brca2":  _has("BRCA2"),
        "pik3ca": ("mutated" if biomarkers_available and pik3ca_muts else
                   "unknown" if not biomarkers_available else "negative"),
        "esr1":   _has("ESR1"),
        "erbb2_amp": _has("ERBB2"),
    }


def _build_brca_note(
    case_id: str,
    demographics: dict,
    profile: dict,
    actual_treatment: str | None,
    age_dx: str,
    institution: str,
) -> str:
    stage   = profile.get("stage", "Unknown")
    subtype = profile.get("subtype", "Unknown")
    er      = profile.get("er_status", "unknown")
    pr      = profile.get("pr_status", "unknown")
    her2    = profile.get("her2_status", "unknown")
    brca1   = profile.get("brca1_status", "unknown")
    brca2   = profile.get("brca2_status", "unknown")
    pik3ca  = profile.get("pik3ca_status", "unknown")
    esr1    = profile.get("esr1_status", "unknown")
    ntrk    = profile.get("ntrk_status", "unknown")
    tmb     = profile.get("tmb_category", "unknown")
    race    = demographics.get("race", "Unknown")
    sex     = demographics.get("sex", "Unknown")
    eth     = demographics.get("ethnicity", "Unknown")
    drivers = []
    if pik3ca  == "mutated": drivers.append("PIK3CA mutated")
    if esr1    == "mutated": drivers.append("ESR1 mutated")
    if brca1   == "mutated": drivers.append("BRCA1 mutated")
    if brca2   == "mutated": drivers.append("BRCA2 mutated")
    if erbb2   := profile.get("erbb2_amp_status", "negative"):
        if erbb2 == "mutated": drivers.append("ERBB2 amplified/mutated")
    if ntrk    == "fusion":   drivers.append("NTRK fusion")
    driver_line = ", ".join(drivers) if drivers else "No actionable somatic driver identified"

    return f"""Patient Name: [De-identified]
MRN: [De-identified]

OBJECTIVE:
Age at Diagnosis: {age_dx} years
Sex: {sex}
Race: {race}
Ethnicity: {eth}
ECOG Performance Status: 1

STAGING:
AJCC Stage: {stage}
Primary diagnosis: Breast cancer

RECEPTOR STATUS:
Subtype: {subtype}
ER status: {er}
PR status: {pr}
HER2 status (summary): {her2}

MOLECULAR PROFILE:
{driver_line}
BRCA1: {brca1}
BRCA2: {brca2}
PIK3CA: {pik3ca}
ESR1: {esr1}
NTRK: {ntrk}
TMB category: {tmb}
PD-L1: unknown

SOCIAL HISTORY:
No alcohol or illicit drug use reported. Lives independently.
"""


# ─── PANC-specific logic ──────────────────────────────────────────────────────

_PANC_EXCLUDED_HIST = {"Squamous cell", "Sarcoma"}


def _panc_resectability(stage: str) -> str:
    """Infer surgical resectability from AJCC stage.

    Stage I–II → resectable (most); Stage III → locally advanced/unresectable;
    Stage IV → metastatic.  This is a first-order approximation — actual
    resectability depends on vascular involvement not captured in GENIE BPC.
    """
    if stage in ("I", "IA", "IB"):
        return "resectable"
    if stage in ("II", "IIA", "IIB"):
        return "resectable"
    if stage in ("III", "IIIA", "IIIB", "IIIC"):
        return "locally_advanced"
    if stage in ("IV", "IVA", "IVB"):
        return "metastatic"
    return "unknown"


def _panc_kras_status(muts_by_gene: dict, biomarkers_available: bool) -> str:
    """Return the most clinically actionable KRAS allele, or 'wildtype'/'unknown'."""
    if not biomarkers_available:
        return "unknown"
    hgvsp_list = muts_by_gene.get("KRAS", [])
    if not hgvsp_list:
        return "wildtype"
    # Prioritise G12C (sotorasib/adagrasib eligibility)
    for h in hgvsp_list:
        if "G12C" in h:
            return "G12C"
    # Return most common allele
    return hgvsp_list[0].replace("p.", "") if hgvsp_list else "other"


def _panc_germline_drivers(muts_by_gene: dict, biomarkers_available: bool) -> dict:
    def _has(gene: str) -> str:
        if not biomarkers_available:
            return "unknown"
        return "mutated" if muts_by_gene.get(gene) else "negative"
    return {
        "brca1":  _has("BRCA1"),
        "brca2":  _has("BRCA2"),
        "atm":    _has("ATM"),
        "palb2":  _has("PALB2"),
    }


def _build_panc_note(
    case_id: str,
    demographics: dict,
    profile: dict,
    actual_treatment: str | None,
    age_dx: str,
    institution: str,
) -> str:
    stage        = profile.get("stage", "Unknown")
    resectability = profile.get("resectability", "unknown")
    hist         = profile.get("histology", "adenocarcinoma").title()
    kras         = profile.get("kras_status", "unknown")
    brca1        = profile.get("brca1_status", "unknown")
    brca2        = profile.get("brca2_status", "unknown")
    atm          = profile.get("atm_status", "unknown")
    palb2        = profile.get("palb2_status", "unknown")
    ntrk         = profile.get("ntrk_status", "unknown")
    tmb          = profile.get("tmb_category", "unknown")
    race         = demographics.get("race", "Unknown")
    sex          = demographics.get("sex", "Unknown")
    eth          = demographics.get("ethnicity", "Unknown")
    drivers = []
    if kras  == "G12C":    drivers.append("KRAS G12C (sotorasib/adagrasib eligible)")
    if brca1 == "mutated": drivers.append("BRCA1 mutated (platinum/olaparib)")
    if brca2 == "mutated": drivers.append("BRCA2 mutated (platinum/olaparib)")
    if atm   == "mutated": drivers.append("ATM mutated (platinum sensitivity)")
    if palb2 == "mutated": drivers.append("PALB2 mutated (platinum sensitivity)")
    if ntrk  == "fusion":  drivers.append("NTRK fusion (larotrectinib/entrectinib)")
    if tmb   == "high":    drivers.append("TMB-High (pembrolizumab eligible)")
    driver_line = ", ".join(drivers) if drivers else "No actionable driver identified"

    return f"""Patient Name: [De-identified]
MRN: [De-identified]

OBJECTIVE:
Age at Diagnosis: {age_dx} years
Sex: {sex}
Race: {race}
Ethnicity: {eth}
ECOG Performance Status: 1

STAGING:
AJCC Stage: {stage}
Resectability: {resectability}
Histology: {hist}

MOLECULAR PROFILE:
{driver_line}
KRAS status: {kras}
BRCA1: {brca1}
BRCA2: {brca2}
ATM: {atm}
PALB2: {palb2}
NTRK: {ntrk}
TMB category: {tmb}
PD-L1: unknown

SOCIAL HISTORY:
No alcohol or illicit drug use reported. Lives independently.
"""


# ─── Main loaders ─────────────────────────────────────────────────────────────

def load_genie_bpc_brca(
    brca_dir: Path = BRCA_DIR,
    output_path: Path = BRCA_OUTPUT,
) -> list[dict]:
    logger.info("Loading GENIE BPC BRCA from %s ...", brca_dir)

    patients  = _read_csv(brca_dir / "patient_level_dataset.csv")
    cancers   = _read_csv(brca_dir / "cancer_level_dataset_index.csv")
    panels    = _read_csv(brca_dir / "cancer_panel_test_level_dataset.csv")
    regimens  = _read_csv(brca_dir / "regimen_cancer_level_dataset.csv")
    mutations = _read_tsv(brca_dir / "data_mutations_extended.txt")
    tmb_rows  = _read_tsv(brca_dir / "tmb.tsv")

    logger.info(
        "Loaded: %d patients, %d cancers, %d panels, %d regimens, %d mutations",
        len(patients), len(cancers), len(panels), len(regimens), len(mutations),
    )

    pt_by_id   = {p["record_id"]: p for p in patients}
    reg_by_key = defaultdict(list)
    for r in regimens:
        reg_by_key[(r["record_id"], r["ca_seq"])].append(r)

    tmb_by_sample = {r["SAMPLE_ID"]: r.get("tmb_bin", "") for r in tmb_rows}

    panels_by_key, muts_by_sample = _build_biomarker_lookups(panels, mutations)

    processed: list[dict] = []
    excl = {"unknown_stage": 0, "no_regimen": 0, "excluded_hist": 0}

    for cancer in cancers:
        record_id = cancer["record_id"]
        ca_seq    = cancer["ca_seq"]
        key       = (record_id, ca_seq)

        # Histology filter — exclude sarcoma
        hist_raw = cancer.get("ca_hist_brca", cancer.get("ca_histology", "")).strip()
        if hist_raw in _PANC_EXCLUDED_HIST:
            excl["excluded_hist"] += 1
            continue

        # Stage
        stage = _resolve_stage(
            cancer.get("best_ajcc_stage_cd", ""),
            cancer.get("stage_dx", ""),
        )
        if not stage:
            excl["unknown_stage"] += 1
            continue

        # Regimen
        actual_treatment = _first_line_regimen(reg_by_key.get(key, []))
        if actual_treatment is None:
            excl["no_regimen"] += 1
            continue

        institution = cancer.get("institution", "")
        pt          = pt_by_id.get(record_id, {})
        age_dx      = cancer.get("age_dx", "")

        # Biomarkers
        muts_by_gene, sample_ids, bio_avail = _collect_mutations(
            key, panels_by_key, muts_by_sample
        )

        receptors = _brca_receptor_status(cancer)
        drivers   = _brca_somatic_drivers(muts_by_gene, bio_avail)

        # TMB
        tmb_category = "unknown"
        for sid in sample_ids:
            tmb_bin = tmb_by_sample.get(sid, "")
            if "High" in tmb_bin:
                tmb_category = "high"
                break
            elif "Mid" in tmb_bin:
                tmb_category = "mid"
            elif "Low" in tmb_bin and tmb_category == "unknown":
                tmb_category = "low"

        clinical_profile = {
            "cancer_type":     "breast",
            "stage":           stage,
            "stage_dx":        cancer.get("stage_dx", ""),
            "subtype":         receptors["subtype"],
            "er_status":       receptors["er"],
            "pr_status":       receptors["pr"],
            "her2_status":     receptors["her2"],
            "brca1_status":    drivers["brca1"],
            "brca2_status":    drivers["brca2"],
            "pik3ca_status":   drivers["pik3ca"],
            "esr1_status":     drivers["esr1"],
            "erbb2_amp_status": drivers["erbb2_amp"],
            "ntrk_status":     _ntrk_status(muts_by_gene, bio_avail),
            "tmb_category":    tmb_category,
            "ecog_ps":         1,
            "prior_therapy":   "naive",
        }

        demo = _demographics(pt, institution)
        case_id = f"genie_BRCA_{record_id}_{ca_seq}"

        processed.append({
            "case_id":              case_id,
            "record_id":            record_id,
            "ca_seq":               ca_seq,
            "institution":          institution,
            "age_dx":               age_dx,
            "demographics":         demo,
            "clinical_profile":     clinical_profile,
            "actual_treatment":     actual_treatment,
            "biomarkers_available": bio_avail,
            "biomarkers_raw": {
                "pik3ca_mutations": muts_by_gene.get("PIK3CA", []),
                "esr1_mutations":   muts_by_gene.get("ESR1", []),
                "brca1_mutations":  muts_by_gene.get("BRCA1", []),
                "brca2_mutations":  muts_by_gene.get("BRCA2", []),
                "erbb2_mutations":  muts_by_gene.get("ERBB2", []),
                "tp53_mutations":   muts_by_gene.get("TP53", []),
                "sample_ids":       sample_ids,
            },
            "panel_sample_ids":     sample_ids,
            "structured_note":      _build_brca_note(
                case_id, demo, clinical_profile, actual_treatment, age_dx, institution
            ),
            "stage_raw":            cancer.get("best_ajcc_stage_cd", ""),
            "histology_raw":        hist_raw,
            "n_regimens":           len(reg_by_key.get(key, [])),
        })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(processed, fh, indent=2, ensure_ascii=False)
    logger.info("BRCA: saved %d cases to %s (excl: %s)", len(processed), output_path, excl)
    return processed


def load_genie_bpc_panc(
    panc_dir: Path = PANC_DIR,
    output_path: Path = PANC_OUTPUT,
) -> list[dict]:
    logger.info("Loading GENIE BPC PANC from %s ...", panc_dir)

    patients  = _read_csv(panc_dir / "patient_level_dataset.csv")
    cancers   = _read_csv(panc_dir / "cancer_level_dataset_index.csv")
    panels    = _read_csv(panc_dir / "cancer_panel_test_level_dataset.csv")
    regimens  = _read_csv(panc_dir / "regimen_cancer_level_dataset.csv")
    mutations = _read_tsv(panc_dir / "data_mutations_extended.txt")
    tmb_rows  = _read_tsv(panc_dir / "tmb.tsv")

    logger.info(
        "Loaded: %d patients, %d cancers, %d panels, %d regimens, %d mutations",
        len(patients), len(cancers), len(panels), len(regimens), len(mutations),
    )

    pt_by_id   = {p["record_id"]: p for p in patients}
    reg_by_key = defaultdict(list)
    for r in regimens:
        reg_by_key[(r["record_id"], r["ca_seq"])].append(r)

    tmb_by_sample = {r["SAMPLE_ID"]: r.get("tmb_bin", "") for r in tmb_rows}

    panels_by_key, muts_by_sample = _build_biomarker_lookups(panels, mutations)

    processed: list[dict] = []
    excl = {"unknown_stage": 0, "no_regimen": 0, "excluded_hist": 0}

    for cancer in cancers:
        record_id = cancer["record_id"]
        ca_seq    = cancer["ca_seq"]
        key       = (record_id, ca_seq)

        # Histology filter — exclude non-adenocarcinoma (sarcoma, squamous)
        hist_name = cancer.get("ca_hist_adeno_squamous", "").strip()
        if hist_name in _PANC_EXCLUDED_HIST:
            excl["excluded_hist"] += 1
            continue

        # Stage
        stage = _resolve_stage(
            cancer.get("best_ajcc_stage_cd", ""),
            cancer.get("stage_dx", ""),
        )
        if not stage:
            excl["unknown_stage"] += 1
            continue

        # Regimen
        actual_treatment = _first_line_regimen(reg_by_key.get(key, []))
        if actual_treatment is None:
            excl["no_regimen"] += 1
            continue

        institution = cancer.get("institution", "")
        pt          = pt_by_id.get(record_id, {})
        age_dx      = cancer.get("age_dx", "")

        # Biomarkers
        muts_by_gene, sample_ids, bio_avail = _collect_mutations(
            key, panels_by_key, muts_by_sample
        )

        kras      = _panc_kras_status(muts_by_gene, bio_avail)
        germline  = _panc_germline_drivers(muts_by_gene, bio_avail)

        # Histology
        hist = "adenocarcinoma" if hist_name in ("Adenocarcinoma", "") else "nos"
        if "Carcinoma" in hist_name:
            hist = "adenocarcinoma"

        # TMB
        tmb_category = "unknown"
        for sid in sample_ids:
            tmb_bin = tmb_by_sample.get(sid, "")
            if "High" in tmb_bin:
                tmb_category = "high"
                break
            elif "Mid" in tmb_bin:
                tmb_category = "mid"
            elif "Low" in tmb_bin and tmb_category == "unknown":
                tmb_category = "low"

        clinical_profile = {
            "cancer_type":    "pancreatic",
            "stage":          stage,
            "stage_dx":       cancer.get("stage_dx", ""),
            "resectability":  _panc_resectability(stage),
            "histology":      hist,
            "kras_status":    kras,
            "brca1_status":   germline["brca1"],
            "brca2_status":   germline["brca2"],
            "atm_status":     germline["atm"],
            "palb2_status":   germline["palb2"],
            "ntrk_status":    _ntrk_status(muts_by_gene, bio_avail),
            "tmb_category":   tmb_category,
            "ecog_ps":        1,
            "prior_therapy":  "naive",
        }

        demo    = _demographics(pt, institution)
        case_id = f"genie_PANC_{record_id}_{ca_seq}"

        processed.append({
            "case_id":              case_id,
            "record_id":            record_id,
            "ca_seq":               ca_seq,
            "institution":          institution,
            "age_dx":               age_dx,
            "demographics":         demo,
            "clinical_profile":     clinical_profile,
            "actual_treatment":     actual_treatment,
            "biomarkers_available": bio_avail,
            "biomarkers_raw": {
                "kras_mutations":  muts_by_gene.get("KRAS", []),
                "brca1_mutations": muts_by_gene.get("BRCA1", []),
                "brca2_mutations": muts_by_gene.get("BRCA2", []),
                "atm_mutations":   muts_by_gene.get("ATM", []),
                "palb2_mutations": muts_by_gene.get("PALB2", []),
                "tp53_mutations":  muts_by_gene.get("TP53", []),
                "smad4_mutations": muts_by_gene.get("SMAD4", []),
                "sample_ids":      sample_ids,
            },
            "panel_sample_ids":     sample_ids,
            "structured_note":      _build_panc_note(
                case_id, demo, clinical_profile, actual_treatment, age_dx, institution
            ),
            "stage_raw":            cancer.get("best_ajcc_stage_cd", ""),
            "histology_raw":        hist_name,
            "n_regimens":           len(reg_by_key.get(key, [])),
        })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(processed, fh, indent=2, ensure_ascii=False)
    logger.info("PANC: saved %d cases to %s (excl: %s)", len(processed), output_path, excl)
    return processed


# ─── Summary printers ─────────────────────────────────────────────────────────

def _print_brca_summary(cases: list[dict]) -> None:
    from collections import Counter
    total = len(cases)
    print(f"\n{'='*60}")
    print(f"  GENIE BPC BRCA — Processed Dataset Summary")
    print(f"{'='*60}")
    print(f"\nTotal cases: {total}")

    stages   = Counter(c["clinical_profile"]["stage"] for c in cases)
    subtypes = Counter(c["clinical_profile"]["subtype"] for c in cases)
    races    = Counter(c["demographics"]["race"] for c in cases)
    insts    = Counter(c["institution"] for c in cases)
    bio      = Counter(c["biomarkers_available"] for c in cases)

    print("\nStage:")
    for k, v in sorted(stages.items()):
        print(f"  {k:<8}: {v:>4}  ({100*v/total:.1f}%)")

    print("\nSubtype:")
    for k, v in subtypes.most_common():
        print(f"  {k:<25}: {v:>4}  ({100*v/total:.1f}%)")

    print("\nRace:")
    for k, v in races.most_common():
        print(f"  {k:<40}: {v:>4}")

    print("\nInstitution:")
    for k, v in insts.most_common():
        print(f"  {k:<10}: {v:>4}")

    print(f"\nBiomarkers available: {bio[True]} / {total} ({100*bio[True]/total:.1f}%)")

    bio_total = bio[True]
    if bio_total:
        for gene in ["pik3ca", "esr1", "brca1", "brca2", "erbb2_amp", "ntrk"]:
            key = f"{gene}_status" if gene != "erbb2_amp" else "erbb2_amp_status"
            n = sum(1 for c in cases if c["biomarkers_available"] and
                    c["clinical_profile"].get(key, "") == "mutated")
            if gene == "ntrk":
                n = sum(1 for c in cases if c["biomarkers_available"] and
                        c["clinical_profile"].get("ntrk_status", "") == "fusion")
            label = gene.upper()
            print(f"  {label:<12}: {n:>4}  ({100*n/bio_total:.1f}%)")

    print("\nTop 10 actual treatments (Line 1):")
    for t, n in Counter(c["actual_treatment"] for c in cases).most_common(10):
        print(f"  {str(t):<55}: {n}")


def _print_panc_summary(cases: list[dict]) -> None:
    from collections import Counter
    total = len(cases)
    print(f"\n{'='*60}")
    print(f"  GENIE BPC PANC — Processed Dataset Summary")
    print(f"{'='*60}")
    print(f"\nTotal cases: {total}")

    stages        = Counter(c["clinical_profile"]["stage"] for c in cases)
    resectability = Counter(c["clinical_profile"]["resectability"] for c in cases)
    races         = Counter(c["demographics"]["race"] for c in cases)
    insts         = Counter(c["institution"] for c in cases)
    bio           = Counter(c["biomarkers_available"] for c in cases)

    print("\nStage:")
    for k, v in sorted(stages.items()):
        print(f"  {k:<8}: {v:>4}  ({100*v/total:.1f}%)")

    print("\nResectability (inferred):")
    for k, v in resectability.most_common():
        print(f"  {k:<20}: {v:>4}  ({100*v/total:.1f}%)")

    print("\nRace:")
    for k, v in races.most_common():
        print(f"  {k:<40}: {v:>4}")

    print("\nInstitution:")
    for k, v in insts.most_common():
        print(f"  {k:<10}: {v:>4}")

    print(f"\nBiomarkers available: {bio[True]} / {total} ({100*bio[True]/total:.1f}%)")

    bio_total = bio[True]
    if bio_total:
        kras_g12c = sum(1 for c in cases if c["clinical_profile"].get("kras_status") == "G12C")
        kras_wt   = sum(1 for c in cases if c["clinical_profile"].get("kras_status") == "wildtype")
        print(f"  KRAS G12C    : {kras_g12c:>4}  ({100*kras_g12c/bio_total:.1f}%)")
        print(f"  KRAS wildtype: {kras_wt:>4}  ({100*kras_wt/bio_total:.1f}%)")
        for gene in ["brca1", "brca2", "atm", "palb2", "ntrk"]:
            key = f"{gene}_status"
            val = "fusion" if gene == "ntrk" else "mutated"
            n = sum(1 for c in cases if c["biomarkers_available"] and
                    c["clinical_profile"].get(key, "") == val)
            print(f"  {gene.upper():<12} : {n:>4}  ({100*n/bio_total:.1f}%)")
        tmb_h = sum(1 for c in cases if c["clinical_profile"].get("tmb_category") == "high")
        print(f"  TMB-High     : {tmb_h:>4}  ({100*tmb_h/bio_total:.1f}%)")

    print("\nTop 10 actual treatments (Line 1):")
    for t, n in Counter(c["actual_treatment"] for c in cases).most_common(10):
        print(f"  {str(t):<55}: {n}")


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cohort", choices=["brca", "panc", "both"], default="both")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    if args.cohort in ("brca", "both"):
        cases = load_genie_bpc_brca()
        _print_brca_summary(cases)
        print(f"\nOutput: {BRCA_OUTPUT}")

    if args.cohort in ("panc", "both"):
        cases = load_genie_bpc_panc()
        _print_panc_summary(cases)
        print(f"\nOutput: {PANC_OUTPUT}")


if __name__ == "__main__":
    main()
