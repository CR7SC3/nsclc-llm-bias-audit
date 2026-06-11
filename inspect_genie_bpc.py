"""GENIE BPC schema inspector.

Run this immediately after placing cohort files under data/genie_bpc/.
Reports: row counts, column names, key biomarker coverage, treatment
regimen patterns, and patient demographics for each cohort.

Expected directory layout
─────────────────────────
  data/genie_bpc/
    nsclc/
      patient_level_dataset.csv
      cancer_level_dataset_index.csv
      cancer_panel_test_level_dataset.csv
      regimen_cancer_level_dataset.csv
    brca/
      patient_level_dataset.csv
      cancer_level_dataset_index.csv
      cancer_panel_test_level_dataset.csv
      regimen_cancer_level_dataset.csv
    panc/
      patient_level_dataset.csv
      cancer_level_dataset_index.csv
      cancer_panel_test_level_dataset.csv
      regimen_cancer_level_dataset.csv

Usage
─────
    venv/bin/python inspect_genie_bpc.py
    venv/bin/python inspect_genie_bpc.py --cohort nsclc   # single cohort
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

DATA_ROOT = Path("data/genie_bpc")
COHORTS   = ["nsclc", "brca", "panc"]

# Biomarker columns we specifically look for — names vary by cohort/version
BIOMARKER_ALIASES = {
    # NSCLC drivers
    "EGFR":    ["mut_EGFR", "egfr_mutation", "EGFR"],
    "ALK":     ["ALK_fusion", "alk_fusion", "ALK"],
    "KRAS":    ["mut_KRAS", "KRAS"],
    "ROS1":    ["ROS1_fusion", "ros1_fusion", "ROS1"],
    "BRAF":    ["mut_BRAF", "BRAF"],
    "MET":     ["MET_amp", "MET_exon14", "MET"],
    "RET":     ["RET_fusion", "RET"],
    "NTRK":    ["NTRK1_fusion", "NTRK2_fusion", "NTRK3_fusion", "NTRK"],
    # Breast cancer
    "BRCA1":   ["mut_BRCA1", "BRCA1"],
    "BRCA2":   ["mut_BRCA2", "BRCA2"],
    "PIK3CA":  ["mut_PIK3CA", "PIK3CA"],
    "ESR1":    ["mut_ESR1", "ESR1"],
    "ERBB2":   ["ERBB2_amp", "HER2_amp", "ERBB2"],
    # Pancreatic
    "SMAD4":   ["mut_SMAD4", "SMAD4"],
    "CDKN2A":  ["mut_CDKN2A", "CDKN2A"],
    "TP53":    ["mut_TP53", "TP53"],
    "PALB2":   ["mut_PALB2", "PALB2"],
    "MSI":     ["msi_status", "MSI_status", "MSI"],
    "TMB":     ["tmb_score", "TMB_score", "TMB"],
}


# ── Helpers ──────────────────────────────────────────────────────────────────

def _read_csv(path: Path) -> tuple[list[str], list[dict]]:
    if not path.exists():
        return [], []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        cols = reader.fieldnames or []
    return list(cols), rows


def _find_cols(cols: list[str], aliases: list[str]) -> list[str]:
    cols_lower = {c.lower(): c for c in cols}
    found = []
    for alias in aliases:
        orig = cols_lower.get(alias.lower())
        if orig:
            found.append(orig)
    return found


def _value_counts(rows: list[dict], col: str, top_n: int = 8) -> dict:
    ctr = Counter(r.get(col, "") for r in rows)
    return dict(ctr.most_common(top_n))


def _non_null_rate(rows: list[dict], col: str) -> float:
    if not rows:
        return 0.0
    filled = sum(1 for r in rows if r.get(col, "").strip() not in ("", "NA", "N/A", "Unknown"))
    return filled / len(rows)


# ── Per-cohort inspection ─────────────────────────────────────────────────────

def inspect_cohort(cohort: str) -> dict:
    base = DATA_ROOT / cohort
    result = {"cohort": cohort, "files": {}, "missing_files": []}

    files = {
        "patient":   base / "patient_level_dataset.csv",
        "index":     base / "cancer_level_dataset_index.csv",
        "panel":     base / "cancer_panel_test_level_dataset.csv",
        "regimen":   base / "regimen_cancer_level_dataset.csv",
    }

    for key, path in files.items():
        if not path.exists():
            result["missing_files"].append(path.name)
            continue
        cols, rows = _read_csv(path)
        result["files"][key] = {
            "path":    str(path),
            "rows":    len(rows),
            "columns": cols,
        }

    if result["missing_files"]:
        return result

    # ── Patient summary ───────────────────────────────────────────────────────
    _, pt_rows = _read_csv(files["patient"])
    result["n_patients"] = len(pt_rows)

    sex_cols  = _find_cols(result["files"]["patient"]["columns"],
                            ["sex", "naaccr_sex_code"])
    race_cols = _find_cols(result["files"]["patient"]["columns"],
                            ["naaccr_race_code_primary", "race", "ethnicity"])
    inst_cols = _find_cols(result["files"]["patient"]["columns"],
                            ["institution", "center"])

    if sex_cols:
        result["sex_distribution"] = _value_counts(pt_rows, sex_cols[0])
    if race_cols:
        result["race_distribution"] = _value_counts(pt_rows, race_cols[0])
    if inst_cols:
        result["institution_distribution"] = _value_counts(pt_rows, inst_cols[0])

    # ── Cancer index summary ──────────────────────────────────────────────────
    idx_cols, idx_rows = _read_csv(files["index"])
    result["n_cancer_records"] = len(idx_rows)

    stage_cols = _find_cols(idx_cols, ["stage_dx", "ajcc_tnm_stage_grp", "tumor_stage",
                                        "cancer_stage_at_dx", "stage"])
    hist_cols  = _find_cols(idx_cols, ["histology", "oncotree_code", "cancer_histology"])

    if stage_cols:
        result["stage_distribution"] = _value_counts(idx_rows, stage_cols[0])
    if hist_cols:
        result["histology_distribution"] = _value_counts(idx_rows, hist_cols[0])

    # ── Panel / biomarker coverage ────────────────────────────────────────────
    panel_cols, panel_rows = _read_csv(files["panel"])
    result["n_panel_records"] = len(panel_rows)

    biomarker_coverage = {}
    for gene, aliases in BIOMARKER_ALIASES.items():
        found = _find_cols(panel_cols, aliases)
        if found:
            rate = _non_null_rate(panel_rows, found[0])
            vc   = _value_counts(panel_rows, found[0], top_n=5)
            biomarker_coverage[gene] = {
                "column": found[0],
                "non_null_rate": round(rate, 3),
                "value_counts": vc,
            }
    result["biomarker_coverage"] = biomarker_coverage

    # Report all panel columns not matched to known biomarkers
    matched_cols = {v["column"] for v in biomarker_coverage.values()}
    result["unmatched_panel_columns"] = [c for c in panel_cols if c not in matched_cols]

    # ── Regimen summary ───────────────────────────────────────────────────────
    reg_cols, reg_rows = _read_csv(files["regimen"])
    result["n_regimen_records"] = len(reg_rows)

    drug_cols  = _find_cols(reg_cols, ["regimen_drugs", "drugs_admin", "drug_name",
                                        "drugs", "regimen"])
    line_cols  = _find_cols(reg_cols, ["line_therapy", "regimen_number", "line_of_therapy"])
    reason_cols = _find_cols(reg_cols, ["regimen_stop_reason", "stop_reason", "reason_stop"])

    if drug_cols:
        result["top_regimens"] = _value_counts(reg_rows, drug_cols[0], top_n=15)
    if line_cols:
        result["line_distribution"] = _value_counts(reg_rows, line_cols[0])
    if reason_cols:
        result["stop_reason_distribution"] = _value_counts(reg_rows, reason_cols[0])

    result["all_regimen_columns"] = reg_cols

    return result


# ── Printer ───────────────────────────────────────────────────────────────────

def print_report(r: dict) -> None:
    cohort = r["cohort"].upper()
    sep = "=" * 70

    print(f"\n{sep}")
    print(f"  GENIE BPC — {cohort}")
    print(sep)

    if r["missing_files"]:
        print(f"  ⚠  Missing files: {r['missing_files']}")
        print(f"     Place files under data/genie_bpc/{r['cohort']}/\n")
        return

    print(f"\nPatients:         {r.get('n_patients', '?'):>6}")
    print(f"Cancer records:   {r.get('n_cancer_records', '?'):>6}")
    print(f"Panel records:    {r.get('n_panel_records', '?'):>6}")
    print(f"Regimen records:  {r.get('n_regimen_records', '?'):>6}")

    # File column counts
    print("\nFile column counts:")
    for key, finfo in r.get("files", {}).items():
        print(f"  {key:<10}: {len(finfo['columns']):>3} columns  ({finfo['rows']} rows)")

    # Demographics
    if "sex_distribution" in r:
        print("\nSex distribution:")
        for k, v in r["sex_distribution"].items():
            print(f"  {str(k):<20}: {v}")

    if "race_distribution" in r:
        print("\nRace distribution (top 8):")
        for k, v in r["race_distribution"].items():
            print(f"  {str(k):<30}: {v}")

    if "institution_distribution" in r:
        print("\nInstitution:")
        for k, v in r["institution_distribution"].items():
            print(f"  {str(k):<20}: {v}")

    # Stage / histology
    if "stage_distribution" in r:
        print("\nStage at diagnosis:")
        for k, v in r["stage_distribution"].items():
            print(f"  {str(k):<20}: {v}")

    if "histology_distribution" in r:
        print("\nHistology / OncotreeCode (top 8):")
        for k, v in r["histology_distribution"].items():
            print(f"  {str(k):<30}: {v}")

    # Biomarkers
    if r.get("biomarker_coverage"):
        print("\nBiomarker columns found in panel file:")
        print(f"  {'Gene':<10} {'Column':<35} {'Non-null%':>9}  Top values")
        print("  " + "-" * 80)
        for gene, info in r["biomarker_coverage"].items():
            pct = f"{info['non_null_rate']*100:.0f}%"
            vals = "  |  ".join(f"{k}:{v}" for k, v in list(info["value_counts"].items())[:3])
            print(f"  {gene:<10} {info['column']:<35} {pct:>9}  {vals}")
    else:
        print("\n  No known biomarker columns matched in panel file.")
        print(f"  Panel columns: {r.get('unmatched_panel_columns', [])[:20]}")

    # Top regimens
    if "top_regimens" in r:
        print("\nTop 15 regimens (actual treatment received):")
        for drug, count in r["top_regimens"].items():
            print(f"  {str(drug):<55}: {count}")

    if "line_distribution" in r:
        print("\nLine of therapy distribution:")
        for k, v in r["line_distribution"].items():
            print(f"  Line {str(k):<6}: {v}")

    # All panel columns (for building the profile extractor)
    print("\nAll panel file columns:")
    for col in r.get("files", {}).get("panel", {}).get("columns", []):
        print(f"  {col}")

    print()


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cohort", choices=COHORTS + ["all"], default="all")
    parser.add_argument("--json",   action="store_true",
                        help="Dump full report as JSON instead of human-readable")
    args = parser.parse_args()

    cohorts_to_run = COHORTS if args.cohort == "all" else [args.cohort]

    all_reports = []
    for cohort in cohorts_to_run:
        report = inspect_cohort(cohort)
        all_reports.append(report)
        if not args.json:
            print_report(report)

    if args.json:
        print(json.dumps(all_reports, indent=2))
    else:
        # Summary table
        print("=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"{'Cohort':<8} {'Patients':>9} {'Panel':>8} {'Regimens':>10} {'Biomarkers found'}")
        print("-" * 60)
        for r in all_reports:
            if r["missing_files"]:
                print(f"{r['cohort'].upper():<8}  {'— files missing —'}")
                continue
            bm = ", ".join(r.get("biomarker_coverage", {}).keys())
            print(f"{r['cohort'].upper():<8} {r.get('n_patients',0):>9} "
                  f"{r.get('n_panel_records',0):>8} {r.get('n_regimen_records',0):>10}  {bm}")
        print()

        print("Next steps:")
        any_missing = any(r["missing_files"] for r in all_reports)
        if any_missing:
            print("  1. Download missing cohorts from Synapse and place in data/genie_bpc/<cohort>/")
            print("  2. Re-run this script")
        else:
            print("  1. Run: venv/bin/python src/generate/load_genie_bpc.py")
            print("     (builds processed JSON cases ready for the experiment pipeline)")


if __name__ == "__main__":
    main()
