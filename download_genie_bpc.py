"""Download GENIE BPC files from Synapse directly into data/genie_bpc/.

Usage
─────
    venv/bin/python download_genie_bpc.py

You will be prompted for your Synapse username and password (or PAT).
Files are downloaded into data/genie_bpc/{nsclc,brca,panc}/ with their
original filenames. Already-downloaded files are skipped automatically.
"""
from __future__ import annotations

import getpass
import sys
from pathlib import Path

import synapseclient

# ── SynID manifest ────────────────────────────────────────────────────────────
# Each entry: (cohort_dir, synapse_id, filename)
FILES = [
    # ── NSCLC 2.0 ─────────────────────────────────────────────────────────────
    ("nsclc", "syn30358090", "cancer_level_dataset_index.csv"),
    ("nsclc", "syn30358091", "cancer_level_dataset_non_index.csv"),
    ("nsclc", "syn30358092", "cancer_panel_test_level_dataset.csv"),
    ("nsclc", "syn30358093", "imaging_level_dataset.csv"),
    ("nsclc", "syn30358094", "med_onc_note_level_dataset.csv"),
    ("nsclc", "syn30358095", "pathology_report_level_dataset.csv"),
    ("nsclc", "syn30358096", "patient_level_dataset.csv"),
    ("nsclc", "syn30358097", "regimen_cancer_level_dataset.csv"),
    ("nsclc", "syn30358099", "data_CNA.txt"),
    ("nsclc", "syn30358100", "data_clinical_patient.txt"),
    ("nsclc", "syn30358101", "data_clinical_sample.txt"),
    ("nsclc", "syn30358105", "data_fusions.txt"),
    ("nsclc", "syn30358120", "data_mutations_extended.txt"),
    ("nsclc", "syn74835209", "tmb.tsv"),
    ("nsclc", "syn30557304", "GENIE_BPC_NSCLC_v2.0-public_Analytic_Data_Guide.pdf"),
    ("nsclc", "syn30557312", "BPC_NSCLC_v2.0-public_variable_synopsis.xlsx"),

    # ── BrCa 1.0 ──────────────────────────────────────────────────────────────
    ("brca", "syn71825316", "cancer_level_dataset_index.csv"),
    ("brca", "syn71825308", "cancer_level_dataset_non_index.csv"),
    ("brca", "syn71825309", "cancer_panel_test_level_dataset.csv"),
    ("brca", "syn71825313", "imaging_level_dataset.csv"),
    ("brca", "syn71825312", "med_onc_note_level_dataset.csv"),
    ("brca", "syn71825311", "pathology_report_level_dataset.csv"),
    ("brca", "syn71825315", "patient_level_dataset.csv"),
    ("brca", "syn71825310", "regimen_cancer_level_dataset.csv"),
    ("brca", "syn71825238", "data_CNA.txt"),
    ("brca", "syn71825255", "data_clinical_patient.txt"),
    ("brca", "syn71825242", "data_clinical_sample.txt"),
    ("brca", "syn71825252", "data_sv.txt"),
    ("brca", "syn71825237", "data_mutations_extended.txt"),
    ("brca", "syn71825225", "genomic_information.txt"),
    ("brca", "syn71825314", "tm_level_dataset.csv"),
    ("brca", "syn71825241", "data_timeline_labtest.txt"),
    ("brca", "syn74835278", "tmb.tsv"),
    ("brca", "syn71825209", "GENIE_BPC_BrCa_v1.0-public_Analytic_Data_Guide.pdf"),
    ("brca", "syn71825211", "GENIE_BPC_BrCa_v1.0-public_Variable_Synopsis.xlsx"),

    # ── PANC 1.0 ──────────────────────────────────────────────────────────────
    ("panc", "syn72666500", "cancer_level_dataset_index.csv"),
    ("panc", "syn72666507", "cancer_level_dataset_non_index.csv"),
    ("panc", "syn72666499", "cancer_panel_test_level_dataset.csv"),
    ("panc", "syn72666505", "imaging_level_dataset.csv"),
    ("panc", "syn72666508", "med_onc_note_level_dataset.csv"),
    ("panc", "syn72666504", "pathology_report_level_dataset.csv"),
    ("panc", "syn72666502", "patient_level_dataset.csv"),
    ("panc", "syn72666503", "regimen_cancer_level_dataset.csv"),
    ("panc", "syn72666457", "data_CNA.txt"),
    ("panc", "syn72666446", "data_clinical_patient.txt"),
    ("panc", "syn72666468", "data_clinical_sample.txt"),
    ("panc", "syn72666432", "data_sv.txt"),
    ("panc", "syn72666431", "data_mutations_extended.txt"),
    ("panc", "syn72666434", "genomic_information.txt"),
    ("panc", "syn72666506", "tm_level_dataset.csv"),
    ("panc", "syn72666450", "data_timeline_labtest.txt"),
    ("panc", "syn72666501", "ca_radtx_dataset.csv"),
    ("panc", "syn74833868", "tmb.tsv"),
    ("panc", "syn72666511", "GENIE_BPC_PANC_v1.0-public_Analytic_Data_Guide.pdf"),
    ("panc", "syn72666512", "GENIE_BPC_PANC_v1.0-public_Variable_Synopsis.xlsx"),
]

DATA_ROOT = Path("data/genie_bpc")


def main() -> None:
    print("EquityGUIDE — GENIE BPC Synapse downloader")
    print(f"Downloading {len(FILES)} files → {DATA_ROOT}/\n")

    # ── Authenticate ──────────────────────────────────────────────────────────
    syn = synapseclient.Synapse()
    print("Synapse login — enter your Personal Access Token (PAT).")
    print("Generate one at: www.synapse.org → your profile → Access Tokens")
    print("(PAT needs View, Download, and Modify scopes)\n")
    pat = getpass.getpass("Personal Access Token: ").strip()
    try:
        # synapseclient v4+ removed password auth; PATs must be passed as authToken.
        syn.login(authToken=pat, silent=True)
        print("Logged in.\n")
    except Exception as exc:
        print(f"Login failed: {exc}")
        sys.exit(1)

    # ── Create directories ────────────────────────────────────────────────────
    for cohort in ("nsclc", "brca", "panc"):
        (DATA_ROOT / cohort).mkdir(parents=True, exist_ok=True)

    # ── Download ──────────────────────────────────────────────────────────────
    ok = skipped = failed = 0
    for cohort, syn_id, filename in FILES:
        dest = DATA_ROOT / cohort / filename
        if dest.exists():
            print(f"  skip  {cohort}/{filename}")
            skipped += 1
            continue
        try:
            print(f"  ↓     {cohort}/{filename}  ({syn_id})", end="", flush=True)
            entity = syn.get(syn_id, downloadLocation=str(DATA_ROOT / cohort))
            # Synapse saves with original filename; rename if needed
            downloaded = Path(entity.path)
            if downloaded.name != filename:
                downloaded.rename(dest)
            print(f"  ✓  ({dest.stat().st_size // 1024} KB)")
            ok += 1
        except Exception as exc:
            print(f"\n  ✗  {cohort}/{filename}: {exc}")
            failed += 1

    print(f"\nDone: {ok} downloaded, {skipped} skipped, {failed} failed")
    if failed == 0:
        print("\nNext step: venv/bin/python inspect_genie_bpc.py")


if __name__ == "__main__":
    main()
