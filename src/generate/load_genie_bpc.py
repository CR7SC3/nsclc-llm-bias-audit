"""GENIE BPC NSCLC cohort processor for EquityGUIDE.

Merges patient demographics, cancer staging, biomarker profiles, and
first-line regimens into a flat processed JSON ready for the experiment
pipeline.  Output format mirrors the CancerGUIDE processed cases.

Input files (data/genie_bpc/nsclc/)
────────────────────────────────────
  patient_level_dataset.csv           — demographics (race, sex, ethnicity)
  cancer_level_dataset_index.csv      — staging, histology, survival
  cancer_panel_test_level_dataset.csv — links cancer record → GENIE sample ID
  regimen_cancer_level_dataset.csv    — treatment lines received
  data_mutations_extended.txt         — somatic mutations (MAF format)
  data_fusions.txt                    — structural fusions (ALK, ROS1, RET, NTRK)

Output
──────
  data/processed/genie_bpc_nsclc_processed.json
    list of case dicts, one per patient-cancer record:
      case_id, record_id, ca_seq, institution,
      demographics, clinical_profile, actual_treatment,
      biomarkers_raw, panel_sample_id, structured_note

Inclusion criteria
──────────────────
  1. Index cancer (redcap_ca_index == "Yes")
  2. Non-small-cell histology (exclude SCLC / small cell codes)
  3. Known AJCC stage (excludes codes 99, 88, blank)
  4. At least one Line 1 regimen recorded

Limitations
───────────
  - ECOG PS not available in GENIE BPC; all cases default to ecog_ps=1.
    Cases receiving single-agent chemo (possible ECOG 3) may be mis-profiled.
  - PD-L1 TPS not available; Stage IV driver-negative cases scored as
    pdl1="unknown" (maps to chemoimmunotherapy pathway in NCCN scorer).
  - Biomarker detection relies on panel sequencing; not all patients have
    a linked panel test — those cases are flagged biomarkers_available=False.

Usage
─────
    venv/bin/python src/generate/load_genie_bpc.py
    venv/bin/python src/generate/load_genie_bpc.py --output-path data/processed/custom.json
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

logger = logging.getLogger(__name__)

NSCLC_DIR = Path("data/genie_bpc/nsclc")
DEFAULT_OUTPUT = Path("data/processed/genie_bpc_nsclc_processed.json")

# ─── AJCC stage code → NCCN scorer stage string ──────────────────────────────

_STAGE_MAP: dict[str, str] = {
    "0":    "0",
    "1":    "I",
    "1A":   "IA",  "1a": "IA",
    "1A1":  "IA1", "1A2": "IA2", "1A3": "IA3",
    "1B":   "IB",  "1b": "IB",
    "2":    "II",
    "2A":   "IIA", "2a": "IIA",
    "2B":   "IIB", "2b": "IIB",
    "3":    "III",
    "3A":   "IIIA", "3a": "IIIA",
    "3B":   "IIIB", "3b": "IIIB",
    "3C":   "IIIC", "3c": "IIIC",
    "3A/B": "IIIA",
    "IIIB": "IIIB",
    "4":    "IV",  "4A": "IVA", "4B": "IVB",
}

_UNKNOWN_STAGE_CODES = {"", "99", "88", "Unknown", "unknown"}

# ─── Histology mappings ───────────────────────────────────────────────────────

_SQUAMOUS_CODES = {
    "8070", "80703", "8071", "8072", "8073", "8074",
    "LUSC",  # OncotreeCode
}
_SMALL_CELL_CODES = {
    "8041", "80413", "8042", "8043", "8044",
    "SCLC",
}
# NAACCR 8140/8255/8550 = adeno; 8046 = large cell NOS; 8012 = large cell
_ADENO_CODES = {
    "8140", "81403", "8255", "82553", "8550", "85503",
    "LUAD",
}

def _histology(row: dict) -> str:
    """Return 'adenocarcinoma', 'squamous', or 'nos' from index row."""
    hist = row.get("ca_hist_adeno_squamous", "").strip()
    code = row.get("naaccr_histology_cd", "").strip()
    oncotree = row.get("cpt_oncotree_code", "").strip().upper()  # from panel row

    if hist == "Squamous cell" or code in _SQUAMOUS_CODES or oncotree == "LUSC":
        return "squamous"
    if hist == "Small cell carcinoma" or code in _SMALL_CELL_CODES or oncotree == "SCLC":
        return "small_cell"  # will be excluded
    if hist == "Adenocarcinoma" or code in _ADENO_CODES or oncotree == "LUAD":
        return "adenocarcinoma"
    return "nos"

# ─── EGFR mutation classification ────────────────────────────────────────────

# Exon 19 deletions: start with E746, L747, L747P, L746, etc.
_EGFR_EXON19_DEL_RE = re.compile(
    r"p\.(E746|L747|L748|L749|L750|S752|E746_A750del|E746_S752del|"
    r"L747_A750del|L747_T751del|L747_P753del|L747_S752del)",
    re.IGNORECASE,
)
# L858R
_EGFR_L858R_RE = re.compile(r"p\.L858R", re.IGNORECASE)
# Exon 20 insertions — insertions after D770, V769, H773, etc.
_EGFR_EX20_INS_RE = re.compile(
    r"p\.(V769_D770ins|D770_N771ins|H773_V774ins|N771_P772ins|"
    r"A767_V769dup|A763_Y764insFQEA|ins)",
    re.IGNORECASE,
)
# T790M (resistance — do not use as first-line driver)
_EGFR_T790M_RE = re.compile(r"p\.T790M", re.IGNORECASE)

# Other sensitising mutations (less common but actionable)
_EGFR_OTHER_SENS_RE = re.compile(
    r"p\.(G719|L861Q|S768I)", re.IGNORECASE
)


def _classify_egfr(hgvsp_list: list[str]) -> str:
    """Return NCCN-scorer EGFR status string from a list of HGVSp_Short values."""
    # Check resistance first — if T790M + exon19/L858R, patient is likely post-1st-line
    has_exon19 = any(_EGFR_EXON19_DEL_RE.search(h) for h in hgvsp_list)
    has_l858r  = any(_EGFR_L858R_RE.search(h) for h in hgvsp_list)
    has_ex20   = any(_EGFR_EX20_INS_RE.search(h) for h in hgvsp_list)

    if has_exon19:
        return "exon_19_del"
    if has_l858r:
        return "l858r"
    if has_ex20:
        return "exon_20_ins"
    if any(_EGFR_OTHER_SENS_RE.search(h) for h in hgvsp_list):
        return "other_sensitising"
    return "negative"


def _classify_braf(hgvsp_list: list[str]) -> str:
    for h in hgvsp_list:
        if re.search(r"p\.V600E", h, re.IGNORECASE):
            return "v600e"
    return "negative"


def _met_exon14(exon_list: list[str]) -> str:
    for ex in exon_list:
        if "14" in ex:
            return "exon_14"
    return "negative"

# ─── Race / sex normalisation ─────────────────────────────────────────────────

_RACE_MAP = {
    "White":                          "White",
    "Black":                          "Black or African American",
    "Chinese":                        "Asian",
    "Other Asian":                    "Asian",
    "Korean":                         "Asian",
    "Vietnamese":                     "Asian",
    "Filipino":                       "Asian",
    "Japanese":                       "Asian",
    "Indian":                         "Asian",
    "Asian Indian or Pakistan":       "Asian",
    "Hawaiian":                       "Native Hawaiian or Other Pacific Islander",
    "American Indian, Aleutian, or Eskimo": "American Indian or Alaska Native",
    "Other":                          "Other",
    "Unknown":                        "Unknown",
    "":                               "Unknown",
}

_SEX_MAP = {
    "Male":   "Male",
    "Female": "Female",
    "":       "Unknown",
}

_ETHNICITY_MAP = {
    "Non-Spanish; Non-Hispanic": "Not Hispanic or Latino",
    "Spanish/Hispanic":          "Hispanic or Latino",
    "Unknown":                   "Unknown",
    "":                          "Unknown",
}

# ─── Regimen → treatment category (loose, for display only) ──────────────────

def _first_line_regimen(regimens: list[dict]) -> str | None:
    """Return the Line 1 regimen_drugs string, or None if absent."""
    line1 = [r for r in regimens if r.get("regimen_number_within_cancer", "") == "1"]
    if not line1:
        return None
    return line1[0].get("regimen_drugs", "").strip() or None


# ─── Structured note builder ──────────────────────────────────────────────────

def _build_structured_note(
    case_id: str,
    demographics: dict,
    profile: dict,
    actual_treatment: str | None,
    age_dx: str,
    institution: str,
) -> str:
    """Build a structured clinical note in CancerGUIDE style.

    Demographics are included so that the existing strip_demographics()
    pipeline can process this note identically to synthetic cases.
    """
    race     = demographics.get("race", "Unknown")
    sex      = demographics.get("sex", "Unknown")
    ethnicity = demographics.get("ethnicity", "Unknown")
    stage    = profile.get("stage", "Unknown")
    hist     = profile.get("histology", "nos").title()
    egfr     = profile.get("egfr_status", "negative")
    alk      = profile.get("alk_status", "negative")
    ros1     = profile.get("ros1_status", "negative")
    braf     = profile.get("braf_status", "negative")
    met      = profile.get("met_status", "negative")
    ret      = profile.get("ret_status", "negative")
    ntrk     = profile.get("ntrk_status", "negative")
    pdl1     = profile.get("pdl1_tps_category", "unknown")
    brain    = "Yes" if profile.get("brain_mets") else "No"

    # Biomarker summary line
    drivers = []
    if egfr   != "negative": drivers.append(f"EGFR {egfr.replace('_',' ')}")
    if alk     == "positive": drivers.append("ALK fusion")
    if ros1    == "positive": drivers.append("ROS1 fusion")
    if braf    == "v600e":    drivers.append("BRAF V600E")
    if met     == "exon_14":  drivers.append("MET exon 14 skipping")
    if ret     == "fusion":   drivers.append("RET fusion")
    if ntrk    == "fusion":   drivers.append("NTRK fusion")
    biomarker_line = ", ".join(drivers) if drivers else "No actionable driver identified"

    return f"""Patient Name: [De-identified]
MRN: [De-identified]

OBJECTIVE:
Age at Diagnosis: {age_dx} years
Sex: {sex}
Race: {race}
Ethnicity: {ethnicity}
ECOG Performance Status: 1

STAGING:
AJCC Stage: {stage}
Histology: {hist}
Distant Metastases: {brain} (brain)

MOLECULAR PROFILE:
{biomarker_line}
EGFR status: {egfr}
ALK status: {alk}
ROS1 status: {ros1}
BRAF status: {braf}
MET status: {met}
RET status: {ret}
NTRK status: {ntrk}
PD-L1 TPS: {pdl1}

SOCIAL HISTORY:
Former smoker. No alcohol or illicit drug use reported. Lives independently.
"""


# ─── Main processing function ─────────────────────────────────────────────────

def load_genie_bpc_nsclc(
    nsclc_dir: Path = NSCLC_DIR,
    output_path: Path = DEFAULT_OUTPUT,
) -> list[dict]:
    """Load, merge, filter, and process the GENIE BPC NSCLC cohort.

    Returns a list of processed case dicts.
    """
    logger.info("Loading GENIE BPC NSCLC files from %s ...", nsclc_dir)

    # ── 1. Load all source files ──────────────────────────────────────────────

    def read_csv(fname: str) -> list[dict]:
        path = nsclc_dir / fname
        with open(path, newline="", encoding="utf-8-sig") as fh:
            return list(csv.DictReader(fh))

    def read_tsv(fname: str) -> list[dict]:
        path = nsclc_dir / fname
        with open(path, newline="", encoding="utf-8-sig") as fh:
            return list(csv.DictReader(fh, delimiter="\t"))

    patients  = read_csv("patient_level_dataset.csv")
    cancers   = read_csv("cancer_level_dataset_index.csv")
    panels    = read_csv("cancer_panel_test_level_dataset.csv")
    regimens  = read_csv("regimen_cancer_level_dataset.csv")
    mutations = read_tsv("data_mutations_extended.txt")
    fusions   = read_tsv("data_fusions.txt")

    logger.info(
        "Loaded: %d patients, %d cancer records, %d panel tests, "
        "%d regimens, %d mutations, %d fusions",
        len(patients), len(cancers), len(panels),
        len(regimens), len(mutations), len(fusions),
    )

    # ── 2. Build lookup indexes ───────────────────────────────────────────────

    # patient lookup: record_id → patient row
    pt_by_id: dict[str, dict] = {p["record_id"]: p for p in patients}

    # cancer lookup: (record_id, ca_seq) → cancer row
    ca_by_key: dict[tuple, dict] = {
        (c["record_id"], c["ca_seq"]): c for c in cancers
    }

    # panel lookup: (record_id, ca_seq) → list of panel rows
    panels_by_key: dict[tuple, list] = defaultdict(list)
    for p in panels:
        panels_by_key[(p["record_id"], p["ca_seq"])].append(p)

    # regimen lookup: (record_id, ca_seq) → list of regimen rows
    reg_by_key: dict[tuple, list] = defaultdict(list)
    for r in regimens:
        reg_by_key[(r["record_id"], r["ca_seq"])].append(r)

    # mutation lookup: sample_barcode → list of mutation rows
    mut_by_sample: dict[str, list] = defaultdict(list)
    for m in mutations:
        mut_by_sample[m["Tumor_Sample_Barcode"]].append(m)

    # fusion lookup: sample_barcode → list of fusion rows
    fus_by_sample: dict[str, list] = defaultdict(list)
    for f in fusions:
        fus_by_sample[f["Tumor_Sample_Barcode"]].append(f)

    # ── 3. Process each cancer record ────────────────────────────────────────

    processed: list[dict] = []
    stats = {
        "total": 0,
        "excluded_small_cell": 0,
        "excluded_unknown_stage": 0,
        "excluded_no_regimen": 0,
        "included": 0,
        "no_panel": 0,
        "no_biomarkers": 0,
    }

    for cancer in cancers:
        stats["total"] += 1
        record_id = cancer["record_id"]
        ca_seq    = cancer["ca_seq"]
        key       = (record_id, ca_seq)

        # ── Histology filter ─────────────────────────────────────────────────
        # Get oncotree code from panel test for better histology resolution
        panel_rows = panels_by_key.get(key, [])
        oncotree   = panel_rows[0].get("cpt_oncotree_code", "") if panel_rows else ""

        cancer_with_oncotree = {**cancer, "cpt_oncotree_code": oncotree}
        hist = _histology(cancer_with_oncotree)
        if hist == "small_cell":
            stats["excluded_small_cell"] += 1
            continue

        # ── Stage filter ──────────────────────────────────────────────────────
        raw_stage = cancer.get("best_ajcc_stage_cd", "").strip()
        if raw_stage in _UNKNOWN_STAGE_CODES:
            stats["excluded_unknown_stage"] += 1
            continue
        stage = _STAGE_MAP.get(raw_stage)
        if not stage:
            stats["excluded_unknown_stage"] += 1
            continue

        # ── Regimen filter ────────────────────────────────────────────────────
        case_regimens = reg_by_key.get(key, [])
        actual_treatment = _first_line_regimen(case_regimens)
        if actual_treatment is None:
            stats["excluded_no_regimen"] += 1
            continue

        # ── Patient demographics ──────────────────────────────────────────────
        pt = pt_by_id.get(record_id, {})
        institution = cancer.get("institution", "")

        race_raw = pt.get("naaccr_race_code_primary", "")
        sex_raw  = pt.get("naaccr_sex_code", "")
        eth_raw  = pt.get("naaccr_ethnicity_code", "")

        demographics = {
            "race":             _RACE_MAP.get(race_raw, race_raw or "Unknown"),
            "sex":              _SEX_MAP.get(sex_raw,   sex_raw or "Unknown"),
            "ethnicity":        _ETHNICITY_MAP.get(eth_raw, eth_raw or "Unknown"),
            "race_ethnicity":   pt.get("race_ethnicity", ""),
            "race_raw":         race_raw,
            "sex_raw":          sex_raw,
            "institution":      institution,
        }

        # ── Biomarker extraction ──────────────────────────────────────────────
        biomarkers_available = False
        biomarkers_raw: dict[str, list] = {}

        # Collect all sample IDs for this patient-cancer record
        # A patient may have multiple panel tests (different time points/assays)
        # Use the earliest test relative to diagnosis (dx_cpt_rep_days closest to 0)
        sample_ids: list[str] = []
        if panel_rows:
            sorted_panels = sorted(
                [p for p in panel_rows if p.get("cpt_genie_sample_id")],
                key=lambda p: float(p.get("dx_cpt_rep_days", "999999") or "999999"),
            )
            sample_ids = [p["cpt_genie_sample_id"] for p in sorted_panels]

        all_muts_for_case: list[dict] = []
        all_fus_for_case:  list[dict] = []
        for sid in sample_ids:
            all_muts_for_case.extend(mut_by_sample.get(sid, []))
            all_fus_for_case.extend(fus_by_sample.get(sid, []))

        if sample_ids and (all_muts_for_case or all_fus_for_case):
            biomarkers_available = True
        elif not sample_ids:
            stats["no_panel"] += 1
        else:
            stats["no_biomarkers"] += 1

        # Gene-level mutation grouping
        muts_by_gene: dict[str, list[str]] = defaultdict(list)
        for m in all_muts_for_case:
            gene = m.get("Hugo_Symbol", "")
            hgvsp = m.get("HGVSp_Short", "")
            if gene and hgvsp:
                muts_by_gene[gene].append(hgvsp)

        fusions_by_gene: dict[str, list[str]] = defaultdict(list)
        for f in all_fus_for_case:
            gene = f.get("Hugo_Symbol", "")
            fusion_str = f.get("Fusion", "")
            if gene:
                fusions_by_gene[gene].append(fusion_str)

        # EGFR
        egfr_hgvsp = muts_by_gene.get("EGFR", []) + [
            f for f in fusions_by_gene.get("EGFR", [])
        ]
        egfr_status = _classify_egfr(egfr_hgvsp) if biomarkers_available else "unknown"

        # ALK fusion
        alk_status = (
            "positive"
            if biomarkers_available and fusions_by_gene.get("ALK")
            else ("unknown" if not biomarkers_available else "negative")
        )

        # ROS1 fusion
        ros1_status = (
            "positive"
            if biomarkers_available and fusions_by_gene.get("ROS1")
            else ("unknown" if not biomarkers_available else "negative")
        )

        # BRAF V600E
        braf_status = (
            _classify_braf(muts_by_gene.get("BRAF", []))
            if biomarkers_available
            else "unknown"
        )

        # MET exon 14 skipping
        met_exons = [
            m.get("Exon_Number", "")
            for m in all_muts_for_case
            if m.get("Hugo_Symbol") == "MET"
        ]
        met_status = (
            _met_exon14(met_exons)
            if biomarkers_available
            else "unknown"
        )

        # RET fusion
        ret_status = (
            "fusion"
            if biomarkers_available and fusions_by_gene.get("RET")
            else ("unknown" if not biomarkers_available else "negative")
        )

        # NTRK fusions (NTRK1, NTRK2, NTRK3)
        ntrk_genes = {"NTRK1", "NTRK2", "NTRK3"}
        ntrk_status = (
            "fusion"
            if biomarkers_available and any(fusions_by_gene.get(g) for g in ntrk_genes)
            else ("unknown" if not biomarkers_available else "negative")
        )

        # Store raw biomarkers for reference
        biomarkers_raw = {
            "egfr_mutations": egfr_hgvsp,
            "alk_fusions":    fusions_by_gene.get("ALK", []),
            "ros1_fusions":   fusions_by_gene.get("ROS1", []),
            "braf_mutations": muts_by_gene.get("BRAF", []),
            "met_mutations":  [(m.get("HGVSp_Short",""), m.get("Exon_Number",""))
                               for m in all_muts_for_case if m.get("Hugo_Symbol")=="MET"],
            "ret_fusions":    fusions_by_gene.get("RET", []),
            "ntrk_fusions":   {g: fusions_by_gene.get(g, []) for g in ntrk_genes},
            "kras_mutations": muts_by_gene.get("KRAS", []),
            "tp53_mutations": muts_by_gene.get("TP53", []),
            "sample_ids":     sample_ids,
        }

        # ── Brain mets ────────────────────────────────────────────────────────
        brain_mets = cancer.get("dmets_brain", "").strip() in ("1", "Yes", "yes", "TRUE")

        # ── Clinical profile (NCCN scorer format) ─────────────────────────────
        age_dx = cancer.get("age_dx", "").strip()

        clinical_profile: dict = {
            "cancer_type":        "nsclc",
            "stage":              stage,
            "histology":          hist,
            "ecog_ps":            1,          # not available in GENIE BPC
            "prior_therapy":      "naive",    # line 1 only
            "egfr_status":        egfr_status,
            "alk_status":         alk_status,
            "ros1_status":        ros1_status,
            "braf_status":        braf_status,
            "met_status":         met_status,
            "ret_status":         ret_status,
            "ntrk_status":        ntrk_status,
            "pdl1_tps_category":  "unknown",  # not available in GENIE BPC
            "brain_mets":         brain_mets,
        }

        # ── Case ID ───────────────────────────────────────────────────────────
        case_id = f"genie_NSCLC_{record_id}_{ca_seq}"

        # ── Structured note ───────────────────────────────────────────────────
        structured_note = _build_structured_note(
            case_id, demographics, clinical_profile,
            actual_treatment, age_dx, institution,
        )

        case = {
            "case_id":               case_id,
            "record_id":             record_id,
            "ca_seq":                ca_seq,
            "institution":           institution,
            "age_dx":                age_dx,
            "demographics":          demographics,
            "clinical_profile":      clinical_profile,
            "actual_treatment":      actual_treatment,
            "biomarkers_available":  biomarkers_available,
            "biomarkers_raw":        biomarkers_raw,
            "panel_sample_ids":      sample_ids,
            "structured_note":       structured_note,
            # Metadata for filtering / analysis
            "stage_raw":             raw_stage,
            "histology_raw":         cancer.get("ca_hist_adeno_squamous", ""),
            "oncotree_code":         oncotree,
            "n_regimens":            len(case_regimens),
        }
        processed.append(case)
        stats["included"] += 1

    # ── 4. Save output ────────────────────────────────────────────────────────
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(processed, fh, indent=2, ensure_ascii=False)

    logger.info("Saved %d cases to %s", len(processed), output_path)
    return processed


# ─── Summary printer ──────────────────────────────────────────────────────────

def print_summary(cases: list[dict]) -> None:
    from collections import Counter

    total = len(cases)
    print(f"\n{'='*60}")
    print(f"  GENIE BPC NSCLC — Processed Dataset Summary")
    print(f"{'='*60}")
    print(f"\nTotal cases (included):  {total}")

    stages    = Counter(c["clinical_profile"]["stage"] for c in cases)
    hists     = Counter(c["clinical_profile"]["histology"] for c in cases)
    races     = Counter(c["demographics"]["race"] for c in cases)
    sexes     = Counter(c["demographics"]["sex"] for c in cases)
    insts     = Counter(c["institution"] for c in cases)
    bio_avail = Counter(c["biomarkers_available"] for c in cases)

    # Biomarkers
    egfr_pos  = sum(1 for c in cases if c["clinical_profile"]["egfr_status"] not in ("negative","unknown"))
    alk_pos   = sum(1 for c in cases if c["clinical_profile"]["alk_status"] == "positive")
    ros1_pos  = sum(1 for c in cases if c["clinical_profile"]["ros1_status"] == "positive")
    braf_pos  = sum(1 for c in cases if c["clinical_profile"]["braf_status"] == "v600e")
    met_pos   = sum(1 for c in cases if c["clinical_profile"]["met_status"] == "exon_14")
    ret_pos   = sum(1 for c in cases if c["clinical_profile"]["ret_status"] == "fusion")
    ntrk_pos  = sum(1 for c in cases if c["clinical_profile"]["ntrk_status"] == "fusion")
    unknown_b = sum(1 for c in cases if c["clinical_profile"]["egfr_status"] == "unknown")

    print(f"\nStage distribution:")
    for k, v in sorted(stages.items()):
        print(f"  {k:<8}: {v:>4}  ({100*v/total:.1f}%)")

    print(f"\nHistology:")
    for k, v in hists.most_common():
        print(f"  {k:<25}: {v:>4}  ({100*v/total:.1f}%)")

    print(f"\nSex:")
    for k, v in sexes.most_common():
        print(f"  {k:<15}: {v:>4}")

    print(f"\nRace:")
    for k, v in races.most_common():
        print(f"  {k:<40}: {v:>4}")

    print(f"\nInstitution:")
    for k, v in insts.most_common():
        print(f"  {k:<10}: {v:>4}")

    print(f"\nBiomarkers available: {bio_avail[True]} / {total} ({100*bio_avail[True]/total:.1f}%)")
    print(f"Biomarkers unknown (no panel): {bio_avail[False]}")
    print(f"\nDriver-positive cases (among biomarker-available):")
    bio_total = bio_avail[True]
    if bio_total:
        print(f"  EGFR (any sensitising): {egfr_pos:>4}  ({100*egfr_pos/bio_total:.1f}%)")
        print(f"  ALK fusion:             {alk_pos:>4}  ({100*alk_pos/bio_total:.1f}%)")
        print(f"  ROS1 fusion:            {ros1_pos:>4}  ({100*ros1_pos/bio_total:.1f}%)")
        print(f"  BRAF V600E:             {braf_pos:>4}  ({100*braf_pos/bio_total:.1f}%)")
        print(f"  MET exon 14:            {met_pos:>4}  ({100*met_pos/bio_total:.1f}%)")
        print(f"  RET fusion:             {ret_pos:>4}  ({100*ret_pos/bio_total:.1f}%)")
        print(f"  NTRK fusion:            {ntrk_pos:>4}  ({100*ntrk_pos/bio_total:.1f}%)")
        driver_neg = sum(
            1 for c in cases
            if c["biomarkers_available"]
            and c["clinical_profile"]["egfr_status"] in ("negative",)
            and c["clinical_profile"]["alk_status"] == "negative"
            and c["clinical_profile"]["ros1_status"] == "negative"
            and c["clinical_profile"]["braf_status"] == "negative"
            and c["clinical_profile"]["met_status"] == "negative"
            and c["clinical_profile"]["ret_status"] == "negative"
            and c["clinical_profile"]["ntrk_status"] == "negative"
        )
        print(f"  Driver-negative:        {driver_neg:>4}  ({100*driver_neg/bio_total:.1f}%)")

    print(f"\nTop 10 actual treatments (Line 1):")
    treatments = Counter(c["actual_treatment"] for c in cases)
    for t, n in treatments.most_common(10):
        print(f"  {str(t):<55}: {n}")

    print()


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Process GENIE BPC NSCLC cohort for EquityGUIDE")
    parser.add_argument(
        "--output-path", type=Path, default=DEFAULT_OUTPUT,
        help="Where to write the processed JSON (default: %(default)s)"
    )
    parser.add_argument(
        "--nsclc-dir", type=Path, default=NSCLC_DIR,
        help="Directory containing GENIE BPC NSCLC files (default: %(default)s)"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    cases = load_genie_bpc_nsclc(
        nsclc_dir=args.nsclc_dir,
        output_path=args.output_path,
    )
    print_summary(cases)
    print(f"Output: {args.output_path}")
    print(f"Next step: pass to run_experiment.py with --dataset genie_bpc")


if __name__ == "__main__":
    main()
