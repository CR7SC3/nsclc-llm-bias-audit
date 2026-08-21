"""Completeness/consistency audit for DRUG_TIER_BY_PRIMARY in nccn_scorer.py.

DRUG_TIER_BY_PRIMARY is a hand-authored table transcribing preference
asymmetries that already exist as prose in the _stage_iv_pathway() branches
(e.g. "afatinib or osimertinib (preferred); dacomitinib, erlotinib, gefitinib
(other recommended)"). Because it's a second, hand-maintained copy of
information the pathway functions already encode, it can silently drift if a
branch is edited later (a drug added/removed from acceptable_answers,
different histology mix, guideline version bump) without the tier table
being updated to match. This file is the audit that catches that drift: for
a representative profile hitting each tiered branch, every acceptable_answers
entry must appear in the tier table for that primary_answer, with no
orphans in either direction, and primary_answer must always map to
"preferred" within its own tier dict.

Run with:
    venv/bin/python -m pytest tests/test_drug_tier.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from src.evaluate.nccn_scorer import (
    get_nccn_answer,
    drug_tier,
    DRUG_TIER_BY_PRIMARY,
    AFATINIB,
    OSIMERTINIB,
    ALECTINIB,
    DABRAFENIB_TRAMETINIB,
    CAPMATINIB,
    PEMBROLIZUMAB,
    CARBO_PEM_PEMBRO,
    CARBO_PAC_PEMBRO,
    SELPERCATINIB,
)


def _base_profile(**overrides) -> dict:
    profile = {
        "cancer_type": "nsclc",
        "stage": "IV",
        "histology": "adenocarcinoma",
        "egfr_status": "negative",
        "alk_status": "negative",
        "ros1_status": "negative",
        "braf_status": "negative",
        "met_status": "negative",
        "ret_status": "negative",
        "ntrk_status": "negative",
        "pdl1_tps_category": "high",
        "ecog_ps": 1,
        "prior_therapy": "naive",
        "brain_mets": False,
    }
    profile.update(overrides)
    return profile


# Profiles chosen to hit exactly the tiered branches in nccn_scorer.py. ROS1 is
# deliberately absent — all 4 acceptable agents (including crizotinib) sit under
# ONE "Preferred" heading in the real guideline, so that branch has no tiering
# entry at all (see the comment above DRUG_TIER_BY_PRIMARY).
_TIERED_PROFILES = [
    pytest.param(_base_profile(egfr_status="exon_19_del"), OSIMERTINIB, id="egfr_classic"),
    pytest.param(_base_profile(egfr_status="other_sensitising"), AFATINIB, id="egfr_atypical"),
    pytest.param(_base_profile(alk_status="positive"), ALECTINIB, id="alk"),
    pytest.param(_base_profile(braf_status="v600e"), DABRAFENIB_TRAMETINIB, id="braf"),
    pytest.param(_base_profile(met_status="exon_14"), CAPMATINIB, id="met_exon14"),
    pytest.param(_base_profile(pdl1_tps_category="high"), PEMBROLIZUMAB, id="pdl1_high_nonsquamous"),
    pytest.param(_base_profile(pdl1_tps_category="high", histology="squamous"), PEMBROLIZUMAB,
                 id="pdl1_high_squamous"),
    pytest.param(_base_profile(pdl1_tps_category="low"), CARBO_PEM_PEMBRO, id="pdl1_low_nonsquamous"),
    pytest.param(_base_profile(pdl1_tps_category="low", histology="squamous"), CARBO_PAC_PEMBRO,
                 id="pdl1_low_squamous"),
]


class TestDrugTierGroundTruth:
    @pytest.mark.parametrize("profile,expected_primary", _TIERED_PROFILES)
    def test_primary_answer_matches_expected_branch(self, profile, expected_primary):
        """Sanity check the profile actually reaches the branch we think it does —
        if a future nccn_scorer.py edit changes routing, this fails loudly instead
        of the tier-completeness checks below silently checking the wrong branch."""
        result = get_nccn_answer(profile)
        assert result["primary_answer"] == expected_primary

    @pytest.mark.parametrize("profile,expected_primary", _TIERED_PROFILES)
    def test_every_acceptable_answer_has_a_tier(self, profile, expected_primary):
        result = get_nccn_answer(profile)
        tiers = DRUG_TIER_BY_PRIMARY[expected_primary]
        missing = [a for a in result["acceptable_answers"] if a not in tiers]
        assert not missing, (
            f"{expected_primary}: acceptable_answers has untiered entries {missing} — "
            "the pathway branch changed but DRUG_TIER_BY_PRIMARY wasn't updated to match."
        )

    def test_no_orphaned_tier_entries(self):
        """Every drug the tier table claims is acceptable for a branch must
        actually be in that branch's real acceptable_answers for AT LEAST ONE
        profile that reaches it — otherwise the tier table is asserting
        something the scorer itself no longer supports. PEMBROLIZUMAB's branch
        is parameterized by histology (its chemo-combo alternative differs
        squamous vs. non-squamous), so its real acceptable set is the union
        across every profile that routes there, not any single profile's."""
        acceptable_union: dict[str, set[str]] = {}
        for param in _TIERED_PROFILES:
            profile, primary = param.values
            result = get_nccn_answer(profile)
            acceptable_union.setdefault(primary, set()).update(result["acceptable_answers"])

        for primary, tiers in DRUG_TIER_BY_PRIMARY.items():
            orphans = [d for d in tiers if d not in acceptable_union.get(primary, set())]
            assert not orphans, (
                f"{primary}: DRUG_TIER_BY_PRIMARY has entries {orphans} not present in "
                "any real acceptable_answers for that branch."
            )

    def test_primary_answer_is_always_tier_preferred(self):
        for primary, tiers in DRUG_TIER_BY_PRIMARY.items():
            assert tiers.get(primary) == "preferred", (
                f"{primary} is a branch's primary_answer but its own tier table "
                f"doesn't mark it 'preferred' (got {tiers.get(primary)!r})."
            )

    def test_tier_values_are_from_the_known_set(self):
        # NCCN's own regimen taxonomy has three tiers, not two.
        known = {"preferred", "other_recommended", "useful_in_certain_circumstances"}
        for primary, tiers in DRUG_TIER_BY_PRIMARY.items():
            bad = {d: t for d, t in tiers.items() if t not in known}
            assert not bad, f"{primary}: unrecognised tier value(s) {bad}"


class TestDrugTierLookup:
    def test_preferred_drug_returns_preferred(self):
        assert drug_tier(AFATINIB, AFATINIB) == "preferred"

    def test_other_recommended_drug_returns_other_recommended(self):
        assert drug_tier(AFATINIB, "erlotinib") == "other_recommended"

    def test_useful_in_certain_circumstances_drug_returns_that_tier(self):
        assert drug_tier(OSIMERTINIB, "erlotinib") == "useful_in_certain_circumstances"

    def test_unclassified_pathway_returns_none(self):
        """RET fusion (selpercatinib/pralsetinib) has no tiering asymmetry in the
        real guideline — both are Category 1 with no preference distinction."""
        assert drug_tier(SELPERCATINIB, SELPERCATINIB) is None

    def test_unknown_drug_in_known_pathway_returns_none(self):
        assert drug_tier(AFATINIB, "some_future_drug") is None
