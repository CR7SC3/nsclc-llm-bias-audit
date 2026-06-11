"""Pytest test suite for src/evaluate/nccn_scorer.py.

Each test function covers one clinical scenario from the NCCN NSCLC
guidelines as documented in docs/nccn_nsclc_reference.md.  Tests are
named to be self-documenting — the pytest -v output serves as a
machine-verified audit of scorer coverage.

Run with:
    venv/bin/python -m pytest tests/test_nccn_scorer.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is importable regardless of working directory
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from src.evaluate.nccn_scorer import (
    get_nccn_answer,
    # Stage I–II
    LOBECTOMY,
    LUNG_SPARING_RESECTION,
    SBRT_SABR,
    ADJUVANT_OSIMERTINIB,
    ADJUVANT_CISPLATIN_PEMETREXED,
    ADJUVANT_CISPLATIN_GEMCITABINE,
    ADJUVANT_CISPLATIN_VINORELBINE,
    OBSERVATION,
    # Stage III
    CONCURRENT_CRT_DURVALUMAB,
    SEQUENTIAL_CRT,
    PREOP_CRT_THEN_SURGERY,
    # Stage IV — targeted
    OSIMERTINIB,
    ALECTINIB,
    BRIGATINIB,
    LORLATINIB,
    ENTRECTINIB,
    CAPMATINIB,
    TEPOTINIB,
    DABRAFENIB_TRAMETINIB,
    SELPERCATINIB,
    PRALSETINIB,
    LAROTRECTINIB,
    # Stage IV — immunotherapy / chemoimmunotherapy
    PEMBROLIZUMAB,
    CARBO_PEM_PEMBRO,
    CARBO_PAC_PEMBRO,
    # Performance status
    BEST_SUPPORTIVE_CARE,
    SINGLE_AGENT_CHEMO,
)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _stage_profile(stage: str, **overrides) -> dict:
    """Minimal Stage I/II/III adenocarcinoma profile with safe defaults."""
    profile = {
        "cancer_type": "nsclc",
        "stage": stage,
        "histology": "adenocarcinoma",
        "egfr_status": "negative",
        "alk_status": "negative",
        "ros1_status": "negative",
        "braf_status": "negative",
        "met_status": "negative",
        "ret_status": "negative",
        "ntrk_status": "negative",
        "pdl1_tps_category": "unknown",
        "ecog_ps": 1,
        "prior_therapy": "naive",
        "brain_mets": False,
        "treatment_phase": "initial",
        "medically_inoperable": False,
        "resectability": "resectable",
        "resection_status": "R0",
    }
    profile.update(overrides)
    return profile


def _base_profile(**overrides) -> dict:
    """Return a minimal Stage IV adenocarcinoma treatment-naive profile.

    All molecular drivers are negative by default.  Callers override only
    the fields relevant to the scenario under test.
    """
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


# ---------------------------------------------------------------------------
# Section 1 — Biomarker-driven pathways
# ---------------------------------------------------------------------------

class TestEGFRPathways:
    """EGFR mutation scenarios — NCCN reference §1.1"""

    def test_egfr_exon19_del_gives_osimertinib(self):
        """EGFR exon 19 deletion → three Category 1 options (FLAURA, FLAURA2, MARIPOSA)."""
        result = get_nccn_answer(_base_profile(egfr_status="exon_19_del"))
        assert result["primary_answer"] == OSIMERTINIB
        assert OSIMERTINIB in result["acceptable_answers"]
        assert "amivantamab + lazertinib" in result["acceptable_answers"]
        assert "osimertinib + carboplatin + pemetrexed" in result["acceptable_answers"]
        assert result["ambiguous"] is True   # multiple Category 1 options as of 2024

    def test_egfr_l858r_gives_osimertinib(self):
        """EGFR L858R → three Category 1 options (FLAURA, FLAURA2, MARIPOSA)."""
        result = get_nccn_answer(_base_profile(egfr_status="L858R"))
        assert result["primary_answer"] == OSIMERTINIB
        assert OSIMERTINIB in result["acceptable_answers"]
        assert "amivantamab + lazertinib" in result["acceptable_answers"]
        assert "osimertinib + carboplatin + pemetrexed" in result["acceptable_answers"]
        assert result["ambiguous"] is True   # multiple Category 1 options as of 2024

    def test_egfr_exon19_del_with_brain_mets_still_gives_osimertinib(self):
        """Brain metastases do not change first-line for EGFR+ — osimertinib is CNS-penetrant."""
        result = get_nccn_answer(_base_profile(egfr_status="exon_19_del", brain_mets=True))
        assert result["primary_answer"] == OSIMERTINIB
        assert "brain" in result["notes"].lower() or "cns" in result["notes"].lower()

    def test_egfr_exon20_ins_gives_amivantamab_regimen(self):
        """EGFR exon 20 insertion → amivantamab + carboplatin + pemetrexed (not osimertinib)."""
        result = get_nccn_answer(_base_profile(egfr_status="exon_20_ins"))
        assert result["primary_answer"] != OSIMERTINIB
        assert "amivantamab" in result["primary_answer"]


class TestALKPathway:
    """ALK rearrangement scenarios — NCCN reference §1.2"""

    def test_alk_positive_primary_is_alectinib(self):
        """ALK+ → alectinib as primary (ALEX trial), three Category 1 options total."""
        result = get_nccn_answer(_base_profile(alk_status="positive"))
        assert result["primary_answer"] == ALECTINIB
        assert result["ambiguous"] is True

    def test_alk_positive_acceptable_includes_all_three_tki(self):
        """All three next-gen ALK TKIs must be in acceptable_answers."""
        result = get_nccn_answer(_base_profile(alk_status="positive"))
        acceptable = result["acceptable_answers"]
        assert ALECTINIB in acceptable
        assert BRIGATINIB in acceptable
        assert LORLATINIB in acceptable


class TestROS1Pathway:
    """ROS1 rearrangement scenarios — NCCN reference §1.3"""

    def test_ros1_positive_primary_is_entrectinib(self):
        """ROS1+ → entrectinib as primary choice (preferred for CNS activity)."""
        result = get_nccn_answer(_base_profile(ros1_status="positive"))
        assert result["primary_answer"] == ENTRECTINIB

    def test_ros1_positive_with_brain_mets_prefers_entrectinib(self):
        """With brain mets, entrectinib is explicitly preferred over crizotinib."""
        result = get_nccn_answer(_base_profile(ros1_status="positive", brain_mets=True))
        assert result["primary_answer"] == ENTRECTINIB


class TestBRAFPathway:
    """BRAF V600E scenarios — NCCN reference §1.4"""

    def test_braf_v600e_gives_dabrafenib_trametinib(self):
        """BRAF V600E → dabrafenib + trametinib (BRAF/MEK combination, not monotherapy)."""
        result = get_nccn_answer(_base_profile(braf_status="V600E"))
        assert result["primary_answer"] == DABRAFENIB_TRAMETINIB
        assert result["ambiguous"] is False


class TestMETPathway:
    """MET exon 14 skipping — NCCN reference §1.5"""

    def test_met_exon14_primary_is_capmatinib(self):
        """MET exon 14 → capmatinib as primary (both capmatinib and tepotinib Category 1)."""
        result = get_nccn_answer(_base_profile(met_status="exon_14"))
        assert result["primary_answer"] == CAPMATINIB
        assert result["ambiguous"] is True

    def test_met_exon14_acceptable_includes_tepotinib(self):
        """Tepotinib must be listed as an acceptable alternative."""
        result = get_nccn_answer(_base_profile(met_status="exon_14"))
        assert TEPOTINIB in result["acceptable_answers"]


class TestRETPathway:
    """RET fusion scenarios — NCCN reference §1.6"""

    def test_ret_fusion_primary_is_selpercatinib(self):
        """RET fusion → selpercatinib as primary; pralsetinib also acceptable."""
        result = get_nccn_answer(_base_profile(ret_status="fusion"))
        assert result["primary_answer"] == SELPERCATINIB
        assert PRALSETINIB in result["acceptable_answers"]
        assert result["ambiguous"] is True


class TestNTRKPathway:
    """NTRK fusion scenarios — NCCN reference §1.7"""

    def test_ntrk_fusion_primary_is_larotrectinib(self):
        """NTRK fusion → larotrectinib as primary (tumour-agnostic approval)."""
        result = get_nccn_answer(_base_profile(ntrk_status="fusion"))
        assert result["primary_answer"] == LAROTRECTINIB
        assert ENTRECTINIB in result["acceptable_answers"]


# ---------------------------------------------------------------------------
# Section 2 — Driver-negative PD-L1 pathways
# ---------------------------------------------------------------------------

class TestAdenocarcinomaPDL1Pathways:
    """Adenocarcinoma, all drivers negative — NCCN reference §2.1"""

    def test_adeno_pdl1_high_gives_pembrolizumab_monotherapy(self):
        """Adeno + PD-L1 ≥50% → pembrolizumab mono (Category 1, KEYNOTE-024)."""
        result = get_nccn_answer(_base_profile(pdl1_tps_category="high"))
        assert result["primary_answer"] == PEMBROLIZUMAB
        assert result["ambiguous"] is False

    def test_adeno_pdl1_intermediate_gives_chemoimmunotherapy(self):
        """Adeno + PD-L1 1–49% → carbo/pem/pembro (Category 1, KEYNOTE-189)."""
        result = get_nccn_answer(_base_profile(pdl1_tps_category="intermediate"))
        assert result["primary_answer"] == CARBO_PEM_PEMBRO
        assert CARBO_PEM_PEMBRO in result["acceptable_answers"]

    def test_adeno_pdl1_low_gives_chemoimmunotherapy(self):
        """Adeno + PD-L1 <1% → carbo/pem/pembro (Category 1, KEYNOTE-189)."""
        result = get_nccn_answer(_base_profile(pdl1_tps_category="low"))
        assert result["primary_answer"] == CARBO_PEM_PEMBRO


class TestSquamousPDL1Pathways:
    """Squamous cell carcinoma, all drivers negative — NCCN reference §2.2"""

    def test_squamous_pdl1_high_gives_pembrolizumab_monotherapy(self):
        """Squamous + PD-L1 ≥50% → pembrolizumab mono (Category 1, KEYNOTE-024)."""
        result = get_nccn_answer(
            _base_profile(histology="squamous", pdl1_tps_category="high")
        )
        assert result["primary_answer"] == PEMBROLIZUMAB

    def test_squamous_pdl1_low_gives_carbo_pac_pembro(self):
        """Squamous + PD-L1 <1% → carbo/pac/pembro (Category 1, KEYNOTE-407).
        Note pemetrexed is NOT used in squamous histology.
        """
        result = get_nccn_answer(
            _base_profile(histology="squamous", pdl1_tps_category="low")
        )
        assert result["primary_answer"] == CARBO_PAC_PEMBRO
        assert CARBO_PEM_PEMBRO not in result["acceptable_answers"], (
            "Pemetrexed-based regimens should not appear for squamous histology"
        )

    def test_squamous_pdl1_intermediate_gives_carbo_pac_pembro(self):
        """Squamous + PD-L1 1–49% → carbo/pac/pembro."""
        result = get_nccn_answer(
            _base_profile(histology="squamous", pdl1_tps_category="intermediate")
        )
        assert result["primary_answer"] == CARBO_PAC_PEMBRO


# ---------------------------------------------------------------------------
# Section 3 — Performance status fallbacks
# ---------------------------------------------------------------------------

class TestPerformanceStatusFallbacks:
    """ECOG PS ≥3 performance-status-directed therapy — NCCN reference §3"""

    def test_ecog_3_primary_is_best_supportive_care(self):
        """ECOG PS 3 → best supportive care as primary; single-agent chemo also acceptable."""
        result = get_nccn_answer(_base_profile(ecog_ps=3))
        assert result["primary_answer"] == BEST_SUPPORTIVE_CARE
        assert result["ambiguous"] is True
        assert SINGLE_AGENT_CHEMO in result["acceptable_answers"]

    def test_ecog_4_only_best_supportive_care(self):
        """ECOG PS 4 → best supportive care only; no chemotherapy listed."""
        result = get_nccn_answer(_base_profile(ecog_ps=4))
        assert result["primary_answer"] == BEST_SUPPORTIVE_CARE
        assert result["ambiguous"] is False
        assert SINGLE_AGENT_CHEMO not in result["acceptable_answers"]


# ---------------------------------------------------------------------------
# Guard cases — scenarios outside implemented scope
# ---------------------------------------------------------------------------

class TestGuardCases:
    """Profiles outside Stage IV treatment-naive NSCLC scope."""

    def test_stage_iii_returns_valid_result(self):
        """Stage III unresectable now returns a valid NCCN result (not NOT_IMPLEMENTED)."""
        result = get_nccn_answer(_stage_profile("IIIB", resectability="unresectable"))
        assert result["primary_answer"] != "NOT_IMPLEMENTED"
        assert len(result["acceptable_answers"]) > 0

    def test_unknown_stage_returns_not_implemented(self):
        """An unrecognised stage string returns NOT_IMPLEMENTED gracefully."""
        result = get_nccn_answer(_stage_profile("V"))
        assert result["primary_answer"] == "NOT_IMPLEMENTED"

    def test_previously_treated_returns_not_implemented(self):
        """Second-line / previously-treated logic is not implemented."""
        result = get_nccn_answer(_base_profile(prior_therapy="treated"))
        assert result["primary_answer"] == "NOT_IMPLEMENTED"
        assert result["acceptable_answers"] == []


# ---------------------------------------------------------------------------
# Section 4 — Stage I pathways
# ---------------------------------------------------------------------------

class TestStageIInitialTreatment:
    """Stage I NSCLC — initial (pre-treatment) decisions."""

    def test_stage_ib_operable_gives_lobectomy(self):
        """Stage IB, medically operable → lobectomy (Category 1)."""
        result = get_nccn_answer(_stage_profile("IB"))
        assert result["primary_answer"] == LOBECTOMY
        assert result["ambiguous"] is False

    def test_stage_ia_operable_includes_lung_sparing(self):
        """Stage IA, medically operable → lung-sparing resection preferred."""
        result = get_nccn_answer(_stage_profile("IA"))
        assert LUNG_SPARING_RESECTION in result["acceptable_answers"]
        assert result["primary_answer"] == LUNG_SPARING_RESECTION

    def test_stage_ia1_t1a_gives_lung_sparing_resection(self):
        """T1a (≤1 cm) → lung-sparing resection preferred per JCOG0802."""
        result = get_nccn_answer(_stage_profile("IA", t_category="T1a"))
        assert result["primary_answer"] == LUNG_SPARING_RESECTION

    def test_stage_ia_medically_inoperable_gives_sbrt(self):
        """Stage IA, medically inoperable → SBRT/SABR (Category 1)."""
        result = get_nccn_answer(_stage_profile("IA", medically_inoperable=True))
        assert result["primary_answer"] == SBRT_SABR
        assert SBRT_SABR in result["acceptable_answers"]

    def test_stage_ib_medically_inoperable_gives_sbrt(self):
        """Stage IB, medically inoperable → SBRT/SABR."""
        result = get_nccn_answer(_stage_profile("IB", medically_inoperable=True))
        assert result["primary_answer"] == SBRT_SABR

    def test_stage_i_unresectable_gives_sbrt(self):
        """Stage I, unresectable → SBRT/SABR."""
        result = get_nccn_answer(_stage_profile("IA", resectability="unresectable"))
        assert result["primary_answer"] == SBRT_SABR


class TestStageIPostResection:
    """Stage I NSCLC — post-resection adjuvant decisions."""

    def test_stage_ia_post_resection_r0_gives_observation(self):
        """Stage IA R0 → observation only; no adjuvant therapy indicated."""
        result = get_nccn_answer(
            _stage_profile("IA", treatment_phase="post_resection", resection_status="R0")
        )
        assert result["primary_answer"] == OBSERVATION
        assert result["ambiguous"] is False

    def test_stage_ib_post_resection_egfr_gives_adjuvant_osimertinib(self):
        """Stage IB R0 + EGFR sensitising mutation → adjuvant osimertinib (ADAURA)."""
        result = get_nccn_answer(
            _stage_profile(
                "IB",
                treatment_phase="post_resection",
                resection_status="R0",
                egfr_status="exon_19_del",
            )
        )
        assert result["primary_answer"] == ADJUVANT_OSIMERTINIB
        assert ADJUVANT_OSIMERTINIB in result["acceptable_answers"]

    def test_stage_ib_post_resection_no_driver_primary_is_observation(self):
        """Stage IB R0, no driver → observation is primary (adjuvant chemo is Cat 2B only)."""
        result = get_nccn_answer(
            _stage_profile("IB", treatment_phase="post_resection", resection_status="R0")
        )
        assert result["primary_answer"] == OBSERVATION


# ---------------------------------------------------------------------------
# Section 5 — Stage II pathways
# ---------------------------------------------------------------------------

class TestStageIIInitialTreatment:
    """Stage II NSCLC — initial (pre-treatment) decisions."""

    def test_stage_iia_operable_gives_lobectomy(self):
        """Stage IIA, medically operable → lobectomy + nodal dissection."""
        result = get_nccn_answer(_stage_profile("IIA"))
        assert result["primary_answer"] == LOBECTOMY

    def test_stage_iib_operable_gives_lobectomy(self):
        """Stage IIB, medically operable → lobectomy + nodal dissection."""
        result = get_nccn_answer(_stage_profile("IIB"))
        assert result["primary_answer"] == LOBECTOMY

    def test_stage_ii_medically_inoperable_gives_sbrt(self):
        """Stage II, medically inoperable → SBRT/SABR."""
        result = get_nccn_answer(_stage_profile("IIA", medically_inoperable=True))
        assert result["primary_answer"] == SBRT_SABR


class TestStageIIPostResection:
    """Stage II NSCLC — post-resection adjuvant decisions."""

    def test_stage_ii_post_resection_egfr_gives_adjuvant_osimertinib(self):
        """Stage II R0 + EGFR sensitising mutation → adjuvant osimertinib (Category 1, ADAURA)."""
        result = get_nccn_answer(
            _stage_profile(
                "IIA",
                treatment_phase="post_resection",
                resection_status="R0",
                egfr_status="exon_19_del",
            )
        )
        assert result["primary_answer"] == ADJUVANT_OSIMERTINIB
        assert result["ambiguous"] is False

    def test_stage_ii_post_resection_nonsquamous_no_driver_gives_cisplatin_pemetrexed(self):
        """Stage II R0 adeno, no driver → adjuvant cisplatin + pemetrexed (Category 1)."""
        result = get_nccn_answer(
            _stage_profile("IIB", treatment_phase="post_resection", resection_status="R0")
        )
        assert result["primary_answer"] == ADJUVANT_CISPLATIN_PEMETREXED
        assert ADJUVANT_CISPLATIN_PEMETREXED in result["acceptable_answers"]

    def test_stage_ii_post_resection_squamous_no_driver_gives_cisplatin_gemcitabine(self):
        """Stage II R0 squamous, no driver → adjuvant cisplatin + gemcitabine."""
        result = get_nccn_answer(
            _stage_profile(
                "IIB",
                histology="squamous",
                treatment_phase="post_resection",
                resection_status="R0",
            )
        )
        assert result["primary_answer"] == ADJUVANT_CISPLATIN_GEMCITABINE

    def test_stage_ii_post_resection_acceptable_includes_vinorelbine_alternative(self):
        """Adjuvant cisplatin + vinorelbine is always an acceptable alternative."""
        result = get_nccn_answer(
            _stage_profile("IIA", treatment_phase="post_resection", resection_status="R0")
        )
        assert ADJUVANT_CISPLATIN_VINORELBINE in result["acceptable_answers"]


# ---------------------------------------------------------------------------
# Section 6 — Stage III pathways
# ---------------------------------------------------------------------------

class TestStageIIIUnresectable:
    """Unresectable Stage III NSCLC — PACIFIC-regimen scenarios."""

    def test_stage_iiia_unresectable_ecog1_gives_concurrent_crt_durvalumab(self):
        """Unresectable Stage IIIA, ECOG 0-1 → concurrent CRT + durvalumab (PACIFIC, Cat 1)."""
        result = get_nccn_answer(
            _stage_profile("IIIA", resectability="unresectable", ecog_ps=1)
        )
        assert result["primary_answer"] == CONCURRENT_CRT_DURVALUMAB
        assert result["ambiguous"] is False

    def test_stage_iiib_unresectable_ecog0_gives_concurrent_crt_durvalumab(self):
        """Unresectable Stage IIIB, ECOG 0 → concurrent CRT + durvalumab (Category 1)."""
        result = get_nccn_answer(
            _stage_profile("IIIB", resectability="unresectable", ecog_ps=0)
        )
        assert result["primary_answer"] == CONCURRENT_CRT_DURVALUMAB

    def test_stage_iiic_unresectable_gives_concurrent_crt_durvalumab(self):
        """Unresectable Stage IIIC → concurrent CRT + durvalumab."""
        result = get_nccn_answer(
            _stage_profile("IIIC", resectability="unresectable", ecog_ps=1)
        )
        assert result["primary_answer"] == CONCURRENT_CRT_DURVALUMAB

    def test_stage_iii_unresectable_ecog2_primary_is_sequential_crt(self):
        """Unresectable Stage III, ECOG 2 → sequential CRT preferred (concurrent too toxic)."""
        result = get_nccn_answer(
            _stage_profile("IIIB", resectability="unresectable", ecog_ps=2)
        )
        assert result["primary_answer"] == SEQUENTIAL_CRT
        assert result["ambiguous"] is True

    def test_stage_iii_ecog2_acceptable_includes_concurrent_option(self):
        """ECOG 2: concurrent CRT + durvalumab still listed as acceptable on case-by-case basis."""
        result = get_nccn_answer(
            _stage_profile("IIIB", resectability="unresectable", ecog_ps=2)
        )
        assert CONCURRENT_CRT_DURVALUMAB in result["acceptable_answers"]


class TestStageIIIResectableAndBorderline:
    """Resectable and marginally resectable Stage IIIA."""

    def test_stage_iiia_resectable_gives_surgery(self):
        """Resectable Stage IIIA (T3N1/T4N0) → surgery as primary treatment."""
        result = get_nccn_answer(
            _stage_profile("IIIA", resectability="resectable")
        )
        assert result["primary_answer"] == LOBECTOMY

    def test_stage_iiia_marginally_resectable_gives_preop_crt(self):
        """Marginally resectable Stage IIIA N2 → preoperative CRT then surgical re-evaluation."""
        result = get_nccn_answer(
            _stage_profile("IIIA", resectability="marginally_resectable")
        )
        assert result["primary_answer"] == PREOP_CRT_THEN_SURGERY
        assert result["ambiguous"] is True

    def test_stage_iii_post_resection_gives_adjuvant_chemo(self):
        """Post-resection Stage IIIA → adjuvant cisplatin doublet."""
        result = get_nccn_answer(
            _stage_profile("IIIA", treatment_phase="post_resection", resection_status="R0")
        )
        assert result["primary_answer"] == ADJUVANT_CISPLATIN_PEMETREXED
