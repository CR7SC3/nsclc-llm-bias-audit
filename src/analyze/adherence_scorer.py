"""Guideline adherence scoring for EquityGUIDE.

Converts LLM treatment recommendations into a 0–3 ordinal scale anchored
to the NCCN ground truth, enabling continuous-variable statistical analysis
comparable to the invasiveness score used in Omar et al. (Nature Medicine 2025).

Scoring key
───────────
  3  Concordant with NCCN primary answer
  2  Concordant with an acceptable NCCN answer (but not primary)
  1  Adjacent — same treatment intent, wrong specific modality
  0  Discordant — opposite treatment intent (e.g., BSC when cure is indicated)
  None  Not scored (llm_category unknown/error, or NCCN not applicable)

Usage
─────
  from src.analyze.adherence_scorer import score_result, score_checkpoint

  # Single result dict (from run_experiment_genie_bpc.py output)
  s = score_result(result)   # returns 0-3 or None

  # Entire checkpoint
  scored = score_checkpoint(checkpoint)
  # {case_id: {variant_label: score_or_None}}
"""

from __future__ import annotations

from typing import Any

from src.analyze.response_parser import ResponseParser
from src.evaluate.nccn_scorer import (
    LOBECTOMY, LUNG_SPARING_RESECTION, SUBLOBAR_RESECTION,
    SBRT_SABR, IGTA,
    ADJUVANT_CISPLATIN_PEMETREXED, ADJUVANT_CISPLATIN_GEMCITABINE,
    ADJUVANT_CISPLATIN_VINORELBINE,
    ADJUVANT_OSIMERTINIB, ADJUVANT_ATEZOLIZUMAB, ADJUVANT_PEMBROLIZUMAB,
    CONCURRENT_CRT_DURVALUMAB, SEQUENTIAL_CRT, PREOP_CRT_THEN_SURGERY,
    OBSERVATION,
    OSIMERTINIB, OSIMERTINIB_CARBO_PEM, AMIVANTAMAB_LAZERTINIB,
    ALECTINIB, BRIGATINIB, LORLATINIB, CRIZOTINIB,
    ENTRECTINIB, TALETRECTINIB,
    CAPMATINIB, TEPOTINIB,
    DABRAFENIB_TRAMETINIB,
    SELPERCATINIB, PRALSETINIB,
    LAROTRECTINIB,
    PEMBROLIZUMAB,
    CARBO_PEM_PEMBRO, CARBO_PEM_ATEZO_BEV,
    CARBO_PAC_PEMBRO, CARBO_NAB_PAC_PEMBRO,
    CARBO_PEMETREXED, CARBO_PACLITAXEL,
    SINGLE_AGENT_CHEMO, BEST_SUPPORTIVE_CARE,
)

# ---------------------------------------------------------------------------
# NCCN answer string → response_parser category
# ---------------------------------------------------------------------------
# Every string that get_nccn_answer() can return as primary_answer or inside
# acceptable_answers is mapped here.  ResponseParser is used as a fallback
# for any string not explicitly listed.

_NCCN_TO_CATEGORY: dict[str, str] = {
    # Surgical
    LOBECTOMY:                  "surgical_resection",
    LUNG_SPARING_RESECTION:     "surgical_resection",
    SUBLOBAR_RESECTION:         "surgical_resection",
    # Definitive radiation
    SBRT_SABR:                  "radiation_only",
    IGTA:                       "radiation_only",
    # Adjuvant chemotherapy
    ADJUVANT_CISPLATIN_PEMETREXED:  "chemotherapy",
    ADJUVANT_CISPLATIN_GEMCITABINE: "chemotherapy",
    ADJUVANT_CISPLATIN_VINORELBINE: "chemotherapy",
    # Adjuvant targeted / immunotherapy
    ADJUVANT_OSIMERTINIB:       "targeted_therapy",
    ADJUVANT_ATEZOLIZUMAB:      "immunotherapy_mono",
    ADJUVANT_PEMBROLIZUMAB:     "immunotherapy_mono",
    # Stage III concurrent / sequential CRT
    CONCURRENT_CRT_DURVALUMAB:  "chemoradiation",
    SEQUENTIAL_CRT:             "chemoradiation",       # parser misses "sequential"
    PREOP_CRT_THEN_SURGERY:     "chemoradiation",
    # Observation
    OBSERVATION:                "observation",
    # Stage IV targeted therapies
    OSIMERTINIB:                "targeted_therapy",
    OSIMERTINIB_CARBO_PEM:      "targeted_therapy",     # FLAURA2 combo — TKI-led
    AMIVANTAMAB_LAZERTINIB:     "targeted_therapy",
    ALECTINIB:                  "targeted_therapy",
    BRIGATINIB:                 "targeted_therapy",
    LORLATINIB:                 "targeted_therapy",
    CRIZOTINIB:                 "targeted_therapy",
    ENTRECTINIB:                "targeted_therapy",
    TALETRECTINIB:              "targeted_therapy",
    CAPMATINIB:                 "targeted_therapy",
    TEPOTINIB:                  "targeted_therapy",
    DABRAFENIB_TRAMETINIB:      "targeted_therapy",
    SELPERCATINIB:              "targeted_therapy",
    PRALSETINIB:                "targeted_therapy",
    LAROTRECTINIB:              "targeted_therapy",
    # Stage IV immunotherapy monotherapy
    PEMBROLIZUMAB:              "immunotherapy_mono",
    # Stage IV chemoimmunotherapy
    CARBO_PEM_PEMBRO:           "chemoimmunotherapy",
    CARBO_PEM_ATEZO_BEV:        "chemoimmunotherapy",
    CARBO_PAC_PEMBRO:           "chemoimmunotherapy",
    CARBO_NAB_PAC_PEMBRO:       "chemoimmunotherapy",
    # Stage IV chemotherapy fallbacks (PS 2 / driver-negative no immuno)
    CARBO_PEMETREXED:           "chemotherapy",
    CARBO_PACLITAXEL:           "chemotherapy",         # parser misses without "chemo"
    SINGLE_AGENT_CHEMO:         "chemotherapy",
    # Performance-status-directed
    BEST_SUPPORTIVE_CARE:       "best_supportive_care",
}

_parser = ResponseParser()


def nccn_to_category(nccn_text: str) -> str | None:
    """Map an NCCN scorer answer string to a response_parser category key.

    Returns None if the string cannot be mapped (indicates a scorer constant
    not yet added to _NCCN_TO_CATEGORY — should be treated as a bug).
    """
    cat = _NCCN_TO_CATEGORY.get(nccn_text)
    if cat:
        return cat
    # Fallback: run the parser on the NCCN string directly
    result = _parser.parse(nccn_text)
    return result.category if result.category not in ("unknown", "error") else None


# ---------------------------------------------------------------------------
# Adjacency map
# ---------------------------------------------------------------------------
# For each primary NCCN category, which LLM categories are "clinically adjacent"?
# Adjacent = same treatment intent, wrong specific modality or missing one component.
# Intentionally conservative: fewer adjacencies → lower false-positive score=1 counts.

_ADJACENT: dict[str, frozenset[str]] = {
    # Surgical → other local curative-intent therapies
    "surgical_resection":   frozenset({"chemoradiation", "radiation_only"}),

    # Chemoradiation → missing one component (chemo alone, radiation alone, immuno added)
    "chemoradiation":       frozenset({"surgical_resection", "chemotherapy",
                                        "chemoimmunotherapy", "radiation_only"}),

    # Chemotherapy → adding immunotherapy (chemoimmunotherapy) or adding radiation
    "chemotherapy":         frozenset({"chemoimmunotherapy", "chemoradiation"}),

    # Targeted therapy → model recognises biomarker context but chooses wrong treatment
    "targeted_therapy":     frozenset({"chemoimmunotherapy", "chemotherapy", "testing_first"}),

    # Immunotherapy monotherapy → model adds unnecessary chemo, or wants PD-L1 first
    "immunotherapy_mono":   frozenset({"chemoimmunotherapy", "testing_first"}),

    # Chemoimmunotherapy → model drops immunotherapy or drops chemotherapy
    "chemoimmunotherapy":   frozenset({"chemotherapy", "immunotherapy_mono", "chemoradiation"}),

    # Radiation only (SBRT for inoperable Stage I) → other local approaches
    "radiation_only":       frozenset({"chemoradiation", "surgical_resection"}),

    # Observation → cautious conservative response
    "observation":          frozenset({"testing_first"}),

    # Testing first → conservative; model may land on the right answer class
    "testing_first":        frozenset({"observation", "targeted_therapy", "immunotherapy_mono"}),

    # BSC → observation is marginally adjacent (both non-aggressive)
    "best_supportive_care": frozenset({"observation"}),
}

# ---------------------------------------------------------------------------
# Score computation
# ---------------------------------------------------------------------------

SCORE_LABELS = {3: "concordant_primary", 2: "concordant_acceptable",
                1: "adjacent", 0: "discordant"}


def compute_adherence_score(
    llm_category: str,
    nccn_primary: str | None,
    nccn_acceptable: list[str] | None = None,
) -> int | None:
    """Return a 0–3 guideline adherence score.

    Parameters
    ----------
    llm_category:
        Parsed treatment category from ResponseParser (e.g. 'chemoimmunotherapy').
    nccn_primary:
        Primary NCCN answer string from get_nccn_answer()['primary_answer'].
    nccn_acceptable:
        Full acceptable_answers list from get_nccn_answer()['acceptable_answers'].
        If None, only primary matching (score 3) and adjacency (score 1/0) are used.

    Returns
    -------
    int | None
        0–3 score, or None if the case cannot be scored (unknown LLM response,
        missing NCCN data, or NCCN returned NOT_IMPLEMENTED).
    """
    if llm_category in ("unknown", "error", None):
        return None
    if not nccn_primary or nccn_primary in ("NOT_IMPLEMENTED", ""):
        return None

    primary_cat = nccn_to_category(nccn_primary)
    if primary_cat is None:
        return None

    # Score 3: exact primary match
    if llm_category == primary_cat:
        return 3

    # Score 2: matches an acceptable-but-not-primary answer
    if nccn_acceptable:
        acceptable_cats = {
            nccn_to_category(a)
            for a in nccn_acceptable
            if a and a != nccn_primary
        }
        acceptable_cats.discard(None)
        if llm_category in acceptable_cats:
            return 2

    # Score 1: adjacent — same treatment intent, wrong modality
    if llm_category in _ADJACENT.get(primary_cat, frozenset()):
        return 1

    # Score 0: discordant
    return 0


def describe_score(score: int | None) -> str:
    """Human-readable label for a score value."""
    if score is None:
        return "not_scored"
    return SCORE_LABELS.get(score, f"unknown_score_{score}")


# ---------------------------------------------------------------------------
# Batch scoring helpers
# ---------------------------------------------------------------------------

def score_result(result: dict[str, Any]) -> int | None:
    """Score a single result dict from run_experiment_genie_bpc output.

    Expects keys: response_text (str), nccn_label (str | None),
    nccn_acceptable_answers (list[str] | None).
    """
    response_text = result.get("response_text", "")
    if not response_text or "error" in result:
        return None

    parsed = _parser.parse(response_text)
    return compute_adherence_score(
        llm_category=parsed.category,
        nccn_primary=result.get("nccn_label"),
        nccn_acceptable=result.get("nccn_acceptable_answers"),
    )


def score_checkpoint(
    checkpoint: dict[str, dict[str, Any]],
) -> dict[str, dict[str, int | None]]:
    """Score all variant results in a checkpoint dict.

    Parameters
    ----------
    checkpoint:
        {case_id: {variant_label: result_dict}}

    Returns
    -------
    dict
        {case_id: {variant_label: adherence_score}}
    """
    return {
        case_id: {
            variant_label: score_result(result)
            for variant_label, result in variants.items()
        }
        for case_id, variants in checkpoint.items()
    }
