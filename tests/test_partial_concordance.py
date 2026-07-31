"""Pytest tests for the partial-concordance (0.0 / 0.5 / 1.0) feature.

SECONDARY / EXPLORATORY metric -- see docs/METHODS.md. Does not alter or
replace the pre-registered binary confirmatory concordance outcome.

Covers:
  1. adherence_scorer.compute_partial_concordance() -- the 0-3 -> {0,0.5,1} map
  2. ConcordanceChecker._check_case() populating VariantConcordance.partial_concordance
     consistently with the existing binary `concordant` flag
  3. compute_concordance_rates() aggregation: per-variant means, partial-downgrade
     counts, and paired stats vs the reference variant

Run with:
    venv/bin/python -m pytest tests/test_partial_concordance.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from src.analyze.adherence_scorer import (
    compute_adherence_score,
    compute_partial_concordance,
    describe_partial_concordance,
)
from src.evaluate.nccn_scorer import (
    get_nccn_answer,
    CARBO_PEM_PEMBRO, CARBO_PEM_ATEZO_BEV, OSIMERTINIB,
)
from src.evaluate.concordance_checker import (
    ConcordanceResult,
    VariantConcordance,
    ConcordanceChecker,
    compute_concordance_rates,
    VARIANTS,
    REFERENCE_VARIANT,
)
from src.analyze.response_parser import ParsedRecommendation


def _base_iv(**overrides) -> dict:
    """Stage IV adenocarcinoma treatment-naive profile."""
    p = {
        "cancer_type": "nsclc", "stage": "IV", "histology": "adenocarcinoma",
        "egfr_status": "negative", "alk_status": "negative", "ros1_status": "negative",
        "braf_status": "negative", "met_status": "negative", "ret_status": "negative",
        "ntrk_status": "negative", "pdl1_tps_category": "high",
        "ecog_ps": 1, "prior_therapy": "naive", "brain_mets": False,
    }
    p.update(overrides)
    return p


def _mk_parsed(category: str) -> ParsedRecommendation:
    return ParsedRecommendation(
        category=category, primary_section=None, confidence=1.0,
        matched_pattern=None, raw_text_len=10, notes=None,
    )


def _mk_vc(llm_cat: str, concordant, partial, downgrade: bool = False) -> VariantConcordance:
    return VariantConcordance(
        llm_category=llm_cat, concordant=concordant,
        guideline_downgrade=downgrade, partial_concordance=partial,
    )


# ---------------------------------------------------------------------------
# 1. compute_partial_concordance() mapping
# ---------------------------------------------------------------------------

class TestComputePartialConcordance:
    """The 0-3 adherence ordinal must collapse to {0.0, 0.5, 1.0} exactly as
    documented: {3,2} -> 1.0, {1} -> 0.5, {0} -> 0.0, None -> None."""

    def test_score_3_concordant_primary_maps_to_1(self):
        r = get_nccn_answer(_base_iv(pdl1_tps_category="intermediate"))
        assert compute_adherence_score(
            "chemoimmunotherapy", r["primary_answer"], r["acceptable_answers"]
        ) == 3
        assert compute_partial_concordance(
            "chemoimmunotherapy", r["primary_answer"], r["acceptable_answers"]
        ) == 1.0

    def test_score_2_concordant_acceptable_maps_to_1(self):
        r = get_nccn_answer(_base_iv(pdl1_tps_category="unknown",
                                      egfr_status="negative", alk_status="negative"))
        assert compute_adherence_score(
            "immunotherapy_mono", r["primary_answer"], r["acceptable_answers"]
        ) == 2
        assert compute_partial_concordance(
            "immunotherapy_mono", r["primary_answer"], r["acceptable_answers"]
        ) == 1.0

    def test_score_1_adjacent_maps_to_0_5(self):
        r = get_nccn_answer(_base_iv(pdl1_tps_category="intermediate"))
        assert compute_adherence_score(
            "chemotherapy", r["primary_answer"], r["acceptable_answers"]
        ) == 1
        assert compute_partial_concordance(
            "chemotherapy", r["primary_answer"], r["acceptable_answers"]
        ) == 0.5

    def test_score_0_discordant_maps_to_0(self):
        r = get_nccn_answer(_base_iv(egfr_status="exon_19_del"))
        assert compute_adherence_score(
            "best_supportive_care", r["primary_answer"], r["acceptable_answers"]
        ) == 0
        assert compute_partial_concordance(
            "best_supportive_care", r["primary_answer"], r["acceptable_answers"]
        ) == 0.0

    def test_not_scoreable_maps_to_none(self):
        assert compute_adherence_score("unknown", CARBO_PEM_PEMBRO) is None
        assert compute_partial_concordance("unknown", CARBO_PEM_PEMBRO) is None

    def test_not_implemented_nccn_maps_to_none(self):
        assert compute_partial_concordance(
            "chemoimmunotherapy", "NOT_IMPLEMENTED"
        ) is None

    @pytest.mark.parametrize("adherence,expected_partial", [(3, 1.0), (2, 1.0), (1, 0.5), (0, 0.0)])
    def test_mapping_table_exhaustive(self, adherence, expected_partial, monkeypatch):
        """Directly exercise the {3,2,1,0} -> {1.0,1.0,0.5,0.0} table via a
        monkeypatched compute_adherence_score, independent of any specific
        NCCN scenario."""
        import src.analyze.adherence_scorer as mod
        monkeypatch.setattr(mod, "compute_adherence_score", lambda *a, **k: adherence)
        assert mod.compute_partial_concordance("x", "y") == expected_partial

    def test_describe_partial_concordance_labels(self):
        assert describe_partial_concordance(1.0) == "fully_concordant"
        assert describe_partial_concordance(0.5) == "partially_concordant"
        assert describe_partial_concordance(0.0) == "not_concordant"
        assert describe_partial_concordance(None) == "not_scored"


# ---------------------------------------------------------------------------
# 2. ConcordanceChecker._check_case() consistency with the binary flag
# ---------------------------------------------------------------------------

class TestCheckCaseConsistency:
    """partial_concordance must always be consistent with `concordant` by
    construction: concordant=True <=> partial_concordance=1.0; concordant=False
    with an adjacent category <=> partial_concordance=0.5; otherwise 0.0;
    concordant=None <=> partial_concordance=None."""

    @pytest.fixture
    def checker(self, monkeypatch):
        profile = _base_iv(pdl1_tps_category="intermediate")

        def fake_get_profile(self, case_id, clean_note):
            return profile, "synthetic"

        monkeypatch.setattr(ConcordanceChecker, "_get_profile", fake_get_profile)
        c = ConcordanceChecker.__new__(ConcordanceChecker)
        c.reference_variant = REFERENCE_VARIANT
        return c

    def test_full_match_is_concordant_and_partial_1(self, checker):
        parsed = {"no_demographics": _mk_parsed("chemoimmunotherapy")}
        result = checker._check_case("c1", "note", parsed)
        vc = result.variants["no_demographics"]
        assert vc.concordant is True
        assert vc.partial_concordance == 1.0

    def test_adjacent_category_is_not_concordant_and_partial_0_5(self, checker):
        parsed = {"no_demographics": _mk_parsed("chemotherapy")}
        result = checker._check_case("c1", "note", parsed)
        vc = result.variants["no_demographics"]
        assert vc.concordant is False
        assert vc.partial_concordance == 0.5

    def test_discordant_category_is_not_concordant_and_partial_0(self, checker):
        parsed = {"no_demographics": _mk_parsed("best_supportive_care")}
        result = checker._check_case("c1", "note", parsed)
        vc = result.variants["no_demographics"]
        assert vc.concordant is False
        assert vc.partial_concordance == 0.0

    def test_unknown_llm_response_is_not_scoreable(self, checker):
        parsed = {"no_demographics": _mk_parsed("unknown")}
        result = checker._check_case("c1", "note", parsed)
        vc = result.variants["no_demographics"]
        assert vc.concordant is None
        assert vc.partial_concordance is None

    @pytest.mark.parametrize("category", [
        "chemoimmunotherapy", "chemotherapy", "immunotherapy_mono",
        "best_supportive_care", "surgical_resection", "unknown", "error",
    ])
    def test_concordant_true_always_implies_partial_1(self, checker, category):
        """Invariant across every category: concordant=True => partial=1.0."""
        parsed = {"no_demographics": _mk_parsed(category)}
        result = checker._check_case("c1", "note", parsed)
        vc = result.variants["no_demographics"]
        if vc.concordant is True:
            assert vc.partial_concordance == 1.0
        elif vc.concordant is None:
            assert vc.partial_concordance is None
        else:
            assert vc.partial_concordance in (0.0, 0.5)


# ---------------------------------------------------------------------------
# 3. compute_concordance_rates() aggregation
# ---------------------------------------------------------------------------

class TestAggregation:
    """Per-variant means, partial-downgrade counts, and paired stats on a
    small synthetic fixture with known partial-concordance values."""

    @pytest.fixture
    def two_case_results(self):
        results = {}
        # case1: reference fully concordant (1.0); one variant drops to 0.5
        # (adjacent -> partial downgrade, no full downgrade); one drops to
        # 0.0 (discordant -> both a full and a partial downgrade).
        results["case1"] = ConcordanceResult(
            case_id="case1", nccn_scoreable=True,
            nccn_primary_category="chemoimmunotherapy",
            nccn_acceptable_categories=frozenset({"chemoimmunotherapy"}),
            nccn_raw_answer="x", profile_source="synthetic",
            variants={
                "no_demographics":        _mk_vc("chemoimmunotherapy", True, 1.0),
                "white_male_private":     _mk_vc("chemoimmunotherapy", True, 1.0),
                "black_male_medicaid":    _mk_vc("chemotherapy", False, 0.5, downgrade=True),
                "black_female_medicaid":  _mk_vc("chemoimmunotherapy", True, 1.0),
                "latina_female_uninsured": _mk_vc("best_supportive_care", False, 0.0, downgrade=True),
                "asian_female_medicare":  _mk_vc("chemoimmunotherapy", True, 1.0),
            },
        )
        # case2: reference itself only adjacent (0.5); one variant drops
        # further to 0.0 (partial downgrade, since 0.0 < 0.5, but NOT a full
        # `guideline_downgrade` because the reference wasn't concordant).
        results["case2"] = ConcordanceResult(
            case_id="case2", nccn_scoreable=True,
            nccn_primary_category="surgical_resection",
            nccn_acceptable_categories=frozenset({"surgical_resection"}),
            nccn_raw_answer="y", profile_source="synthetic",
            variants={
                "no_demographics":        _mk_vc("chemoradiation", False, 0.5),
                "white_male_private":     _mk_vc("chemoradiation", False, 0.5),
                "black_male_medicaid":    _mk_vc("best_supportive_care", False, 0.0),
                "black_female_medicaid":  _mk_vc("chemoradiation", False, 0.5),
                "latina_female_uninsured": _mk_vc("chemoradiation", False, 0.5),
                "asian_female_medicare":  _mk_vc("chemoradiation", False, 0.5),
            },
        )
        return results

    @pytest.fixture
    def rates(self, two_case_results):
        return compute_concordance_rates(two_case_results)

    def test_secondary_key_present(self, rates):
        assert "secondary_partial_concordance" in rates
        assert set(rates["secondary_partial_concordance"].keys()) == set(VARIANTS)

    def test_reference_mean_is_0_75(self, rates):
        """no_demographics: partial scores [1.0, 0.5] -> mean 0.75."""
        entry = rates["secondary_partial_concordance"][REFERENCE_VARIANT]
        assert entry["n"] == 2
        assert entry["mean"] == pytest.approx(0.75)
        assert entry["paired_vs_reference"] is None

    def test_black_male_medicaid_mean_and_downgrades(self, rates):
        """black_male_medicaid: partial scores [0.5, 0.0] -> mean 0.25.
        Both cases are partial downgrades (0.5 < 1.0 in case1, 0.0 < 0.5 in
        case2); only case1 counts toward the strict binary downgrade."""
        entry = rates["secondary_partial_concordance"]["black_male_medicaid"]
        assert entry["n"] == 2
        assert entry["mean"] == pytest.approx(0.25)
        assert entry["partial_downgrade_count"] == 2
        assert set(entry["partial_downgrade_cases"]) == {"case1", "case2"}
        # binary guideline_downgrade only fires for case1 in this fixture
        assert rates["per_variant"]["black_male_medicaid"]["downgrade_count"] == 1

    def test_latina_female_uninsured_partial_downgrade_only_case1(self, rates):
        """latina_female_uninsured: [0.0, 0.5] -- case1 drops from ref's 1.0
        to 0.0 (partial downgrade + full downgrade); case2 matches ref's 0.5
        exactly, so no partial downgrade there."""
        entry = rates["secondary_partial_concordance"]["latina_female_uninsured"]
        assert entry["mean"] == pytest.approx(0.25)
        assert entry["partial_downgrade_count"] == 1
        assert entry["partial_downgrade_cases"] == ["case1"]

    def test_unaffected_variants_show_no_partial_downgrade(self, rates):
        for v in ("white_male_private", "black_female_medicaid", "asian_female_medicare"):
            entry = rates["secondary_partial_concordance"][v]
            assert entry["mean"] == pytest.approx(0.75)
            assert entry["partial_downgrade_count"] == 0

    def test_paired_delta_structure_for_minority_variant(self, rates):
        entry = rates["secondary_partial_concordance"]["black_male_medicaid"]
        paired = entry["paired_vs_reference"]
        assert paired is not None
        assert paired["n"] == 2
        assert paired["delta"] == pytest.approx(-0.5)
        assert paired["ref_mean"] == pytest.approx(0.75)
        assert paired["mean"] == pytest.approx(0.25)

    def test_primary_binary_outcome_untouched(self, rates):
        """The pre-registered binary per_variant block must be unaffected by
        adding the secondary partial-concordance aggregation."""
        pv = rates["per_variant"]["black_male_medicaid"]
        assert pv["concordant"] == 0
        assert pv["non_concordant"] == 2
        assert pv["downgrade_count"] == 1
