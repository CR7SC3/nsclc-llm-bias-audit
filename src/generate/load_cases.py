"""CancerGUIDE dataset loader and preprocessor.

Loads the microsoft/CancerGUIDE dataset from HuggingFace, strips existing
demographic signals from each patient note, applies all six demographic
variants, and saves the processed cases ready for EvaluationRunner.

Dataset schema (microsoft/CancerGUIDE):
    patient_id   : str   — unique case identifier
    patient_note : str   — synthetic free-text NSCLC clinical note
    label        : str   — NCCN-grounded ground-truth treatment (25 classes)

Two configuration subsets exist:
    synthetic_structured    : 165 cases — more templated note style
    synthetic_unstructured  : 151 cases — more narrative note style

Usage
-----
    python -m src.generate.load_cases
    # or import and call load_cancerguide() directly
"""

from __future__ import annotations

import json
import logging
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from datasets import load_dataset
from src.generate.variant_injector import create_all_variants

logger = logging.getLogger(__name__)

_DATA_RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
_DATA_PROCESSED_DIR = Path(__file__).resolve().parents[2] / "data" / "processed"
_DATA_VARIANTS_DIR = Path(__file__).resolve().parents[2] / "data" / "variants"

for _d in (_DATA_RAW_DIR, _DATA_PROCESSED_DIR, _DATA_VARIANTS_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Demographic signal patterns to strip from notes before variant injection.
# Ordered from most specific to least specific to avoid partial matches.
# ---------------------------------------------------------------------------
_DEMOGRAPHIC_PATTERNS: list[str] = [
    # Race + sex combinations  e.g. "White male", "Black female", "Asian woman"
    r"\b(?:White|Black|African[- ]American|Hispanic|Latino|Latina|Asian|"
    r"Native American|Pacific Islander|Caucasian)\s+(?:male|female|man|woman|"
    r"gentleman|lady)\b",
    # Age + race + sex  e.g. "68-year-old White male"
    r"\b\d{2}[- ]year[- ]old\s+(?:White|Black|African[- ]American|Hispanic|"
    r"Latino|Latina|Asian|Caucasian)\s+(?:male|female|man|woman)\b",
    # Standalone race/ethnicity terms in demographic context
    r"\b(?:White|Black|African[- ]American|Hispanic|Latino|Latina|Asian|"
    r"Native American|Pacific Islander|Caucasian)\b(?=\s+(?:patient|individual|person|"
    r"man|woman|male|female|gentleman|lady))",
    # Insurance mentions
    r"\b(?:Medicaid|Medicare|uninsured|self-pay|private insurance|"
    r"Blue Cross|BCBS|Aetna|UnitedHealth|Cigna|Humana)\b",
    # Employment context phrases
    r"\b(?:employed as|works as|occupation:|job:|unemployed|retired)\s+[^.]{0,60}",
]

_COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in _DEMOGRAPHIC_PATTERNS]


def strip_demographics(note: str) -> str:
    """Remove demographic signals from a clinical note.

    Applies a series of regex substitutions to scrub race, sex, insurance,
    and employment references.  The goal is a demographically neutral base
    note that can then receive any of the six variant social histories via
    ``create_all_variants``.

    Parameters
    ----------
    note:
        Raw clinical note text that may contain demographic information.

    Returns
    -------
    str
        The note with demographic terms replaced by neutral placeholders
        or removed entirely.
    """
    cleaned = note
    for pattern in _COMPILED_PATTERNS:
        cleaned = pattern.sub("", cleaned)
    # Collapse any double spaces or blank lines created by removal
    cleaned = re.sub(r"  +", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def load_cancerguide(
    subset: str = "synthetic_structured",
    save_raw: bool = True,
    save_processed: bool = True,
    save_variants: bool = True,
) -> list[dict[str, Any]]:
    """Load, clean, and variant-expand the CancerGUIDE dataset.

    Parameters
    ----------
    subset:
        Which configuration subset to load.  One of
        ``"synthetic_structured"`` (165 cases) or
        ``"synthetic_unstructured"`` (151 cases).
    save_raw:
        If True, save the raw HuggingFace records to ``data/raw/``.
    save_processed:
        If True, save the stripped (demographics-removed) notes to
        ``data/processed/``.
    save_variants:
        If True, save the six demographic variant notes to
        ``data/variants/``.

    Returns
    -------
    list[dict]
        One dict per case with keys:
        ``case_id``, ``label``, ``raw_note``, ``clean_note``, ``variants``.
    """
    logger.info("Loading microsoft/CancerGUIDE subset=%s from HuggingFace...", subset)
    ds = load_dataset("microsoft/CancerGUIDE", subset, split="train")
    logger.info("Loaded %d cases.", len(ds))

    raw_records: list[dict] = []
    processed_cases: list[dict[str, Any]] = []

    for row in ds:
        case_id = f"cancerguide_{subset[:4]}_{row['patient_id']}"
        raw_note: str = row["patient_note"]
        label: str = row["label"]

        # Persist raw record
        raw_records.append({
            "case_id": case_id,
            "patient_id": row["patient_id"],
            "subset": subset,
            "patient_note": raw_note,
            "label": label,
        })

        # Strip demographics to create neutral base note
        clean_note = strip_demographics(raw_note)

        # Create all six demographic variants
        variants = create_all_variants(clean_note)

        processed_cases.append({
            "case_id": case_id,
            "label": label,
            "raw_note": raw_note,
            "clean_note": clean_note,
            "variants": variants,
        })

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    if save_raw:
        raw_path = _DATA_RAW_DIR / f"cancerguide_{subset}_raw.json"
        with open(raw_path, "w", encoding="utf-8") as fh:
            json.dump(raw_records, fh, indent=2, ensure_ascii=False)
        logger.info("Raw records saved to %s", raw_path)

    if save_processed:
        processed_path = _DATA_PROCESSED_DIR / f"cancerguide_{subset}_processed.json"
        # Save without the full variant texts to keep file size manageable
        slim = [
            {k: v for k, v in case.items() if k != "variants"}
            for case in processed_cases
        ]
        with open(processed_path, "w", encoding="utf-8") as fh:
            json.dump(slim, fh, indent=2, ensure_ascii=False)
        logger.info("Processed cases saved to %s", processed_path)

    if save_variants:
        variants_path = _DATA_VARIANTS_DIR / f"cancerguide_{subset}_variants.json"
        # Store only variant notes (not raw/clean) to keep the file focused
        variant_index = {
            case["case_id"]: case["variants"]
            for case in processed_cases
        }
        with open(variants_path, "w", encoding="utf-8") as fh:
            json.dump(variant_index, fh, indent=2, ensure_ascii=False)
        logger.info("Variant notes saved to %s", variants_path)

    return processed_cases


def load_both_subsets(
    save_raw: bool = True,
    save_processed: bool = True,
    save_variants: bool = True,
) -> dict[str, list[dict[str, Any]]]:
    """Load both CancerGUIDE subsets and return them together.

    Parameters
    ----------
    save_raw, save_processed, save_variants:
        Passed through to ``load_cancerguide`` for each subset.

    Returns
    -------
    dict
        Keys: ``"synthetic_structured"``, ``"synthetic_unstructured"``.
        Values: list of processed case dicts from ``load_cancerguide``.
    """
    structured = load_cancerguide(
        "synthetic_structured", save_raw, save_processed, save_variants
    )
    unstructured = load_cancerguide(
        "synthetic_unstructured", save_raw, save_processed, save_variants
    )
    logger.info(
        "Loaded %d structured + %d unstructured = %d total cases.",
        len(structured), len(unstructured), len(structured) + len(unstructured),
    )
    return {
        "synthetic_structured": structured,
        "synthetic_unstructured": unstructured,
    }


def cases_to_runner_format(
    processed_cases: list[dict[str, Any]],
) -> dict[str, dict[str, str]]:
    """Convert processed cases to the format expected by EvaluationRunner.

    Parameters
    ----------
    processed_cases:
        Output of ``load_cancerguide``.

    Returns
    -------
    dict
        ``{case_id: {variant_label: note_text}}`` — pass directly to
        ``EvaluationRunner.run_full_experiment(cases)``.
    """
    return {
        case["case_id"]: case["variants"]
        for case in processed_cases
    }


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    print("Loading CancerGUIDE from HuggingFace...")
    cases = load_both_subsets()
    total = sum(len(v) for v in cases.values())
    print(f"\nDone. {total} cases loaded and saved to data/")
    print(f"  data/raw/        — original HuggingFace records")
    print(f"  data/processed/  — demographic-stripped notes + labels")
    print(f"  data/variants/   — 6-variant note sets ready for EvaluationRunner")
    print(f"\nNext step: pass to EvaluationRunner.run_full_experiment()")
