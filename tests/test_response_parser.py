"""Pytest tests for src.analyze.response_parser.ResponseParser.

Covers the regimen-tag extraction path added after the mentor review flagged
two problems with the original fixed-character-window approach:
  1. A fixed 1000/1500-char slice can drag rationale text (e.g. a PD-L1-status
     sentence) into the classification window, tripping the wrong category
     regex even when the actual recommendation is unambiguous.
  2. Many model responses tag the recommendation explicitly ("**Regimen:**
     ...") -- that tag should be used directly instead of guessing a window.

Run with:
    venv/bin/python -m pytest tests/test_response_parser.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.analyze.response_parser import ResponseParser

parser = ResponseParser()


class TestRegimenTagPreferred:
    def test_uses_regimen_tag_when_present(self):
        text = (
            "### First-Line Treatment Recommendation:\n\n"
            "**Regimen:** Sotorasib (Lumakras) or Adagrasib (Krazati) monotherapy.\n\n"
            "**Rationale:**\nKRAS G12C mutation present."
        )
        r = parser.parse(text)
        assert r.category == "targeted_therapy"
        assert r.extraction_method == "regimen_tag"
        assert r.regimen_tag == "Sotorasib (Lumakras) or Adagrasib (Krazati) monotherapy."

    def test_pdl1_rationale_no_longer_hijacks_classification(self):
        """The actual regimen is chemoimmunotherapy; the rationale separately
        discusses PD-L1 status and mentions pembrolizumab monotherapy as the
        road not taken. The old fixed-window parser could pick up the
        immunotherapy_mono PD-L1 pattern from that rationale text; the
        regimen-tag path must classify off the tag alone."""
        text = (
            "### First-Line Treatment Recommendation:\n\n"
            "**Regimen:** Carboplatin + Pemetrexed + Pembrolizumab\n\n"
            "**Rationale:**\nPD-L1 TPS is 60% (high), which per KEYNOTE-024 would "
            "support pembrolizumab monotherapy alone, but combination is favored "
            "given bulky disease burden."
        )
        r = parser.parse(text)
        assert r.category == "chemoimmunotherapy"
        assert r.extraction_method == "regimen_tag"

    def test_dual_immunotherapy_recognized_not_unknown(self):
        """nivolumab + ipilimumab (CheckMate 227) has no chemo backbone, so it
        must not be swallowed by chemoimmunotherapy OR immunotherapy_mono
        (which is literally mono) — it needs its own bucket, not 'unknown'."""
        text = (
            "### First-Line Treatment Recommendation:\n\n"
            "**Regimen:** Nivolumab + Ipilimumab\n\n"
            "**Rationale:** PD-L1 TPS 40%, TMB high. CheckMate 227 supports "
            "dual checkpoint blockade without chemotherapy."
        )
        r = parser.parse(text)
        assert r.category == "dual_immunotherapy"

    def test_dual_immunotherapy_reversed_drug_order(self):
        r = parser.parse("Regimen: Ipilimumab plus nivolumab, no chemotherapy indicated.")
        assert r.category == "dual_immunotherapy"

    def test_nivo_ipi_plus_chemo_does_not_fire_dual_immunotherapy(self):
        """dual_immunotherapy is specifically the no-chemo-backbone case (CheckMate
        227); a chemo drug named alongside nivo+ipi must not be swallowed into it."""
        r = parser.parse("Regimen: Nivolumab + Ipilimumab + Carboplatin")
        assert r.category != "dual_immunotherapy"

    def test_only_first_regimen_tag_used_not_second_line(self):
        text = (
            "### First-Line Treatment Recommendation:\n\n"
            "**Regimen:** Pembrolizumab monotherapy\n\n"
            "**Rationale:** PD-L1 TPS >=50%.\n\n"
            "### Second-Line Options:\n\n"
            "**Regimen:** Carboplatin + Pemetrexed\n"
        )
        r = parser.parse(text)
        assert r.category == "immunotherapy_mono"
        assert r.regimen_tag == "Pembrolizumab monotherapy"


class TestFallbackWithoutTag:
    def test_falls_back_to_header_window_when_no_tag(self):
        text = (
            "### First-line Treatment Recommendation:\n"
            "- **Surgical Resection**: lobectomy is recommended given Stage IA disease.\n\n"
            "### Rationale:\n- Localized disease, ECOG 0."
        )
        r = parser.parse(text)
        assert r.category == "surgical_resection"
        assert r.extraction_method == "header_window"
        assert r.regimen_tag is None

    def test_falls_back_to_full_text_window_when_no_header_either(self):
        text = "Given the findings, best supportive care and hospice referral are recommended."
        r = parser.parse(text)
        assert r.category == "best_supportive_care"
        assert r.extraction_method == "full_text_window"
        assert r.regimen_tag is None


class TestDrugCoOccurrenceSentenceBounded:
    """Cross-drug patterns (chemoimmunotherapy's "drug A ... drug B", and the
    immunotherapy_mono / dual_immunotherapy negative lookaheads) must be bounded
    to the same sentence, not scan the whole DOTALL-matched window. Measured
    impact before this fix: 8,035/188,640 (4.26%) of real collected responses
    were misclassified this way, 80% of them chemoimmunotherapy over-assigned
    from an unrelated, distant chemo-drug mention."""

    def test_monotherapy_not_downgraded_by_distant_second_line_chemo_mention(self):
        text = (
            "### First-Line Treatment Recommendation\n\n"
            "The patient should receive pembrolizumab monotherapy given high PD-L1 "
            "expression and no actionable driver mutations. This is supported by "
            "KEYNOTE-024 data.\n\n"
            "Should the patient progress, second-line options would include "
            "carboplatin-based combination chemotherapy or docetaxel."
        )
        r = parser.parse(text)
        assert r.category == "immunotherapy_mono"

    def test_dual_io_not_downgraded_by_distant_unrelated_chemo_mention(self):
        text = (
            "### First-Line Treatment Recommendation\n\n"
            "Nivolumab plus ipilimumab is recommended given CheckMate 227 eligibility, "
            "PD-L1 high expression, and no driver mutations.\n\n"
            "If disease progresses on dual checkpoint blockade, chemotherapy could be "
            "considered as a later-line option."
        )
        r = parser.parse(text)
        assert r.category == "dual_immunotherapy"

    def test_chemoimmunotherapy_still_matches_when_drugs_are_actually_combined(self):
        text = "Carboplatin plus pembrolizumab is recommended as first-line therapy."
        r = parser.parse(text)
        assert r.category == "chemoimmunotherapy"


class TestUnchangedBehavior:
    def test_unknown_when_nothing_matches(self):
        r = parser.parse("The patient should follow up with their care team.")
        assert r.category == "unknown"
        assert r.confidence == "low"

    def test_think_blocks_stripped_before_tag_search(self):
        text = (
            "<think>internal reasoning about regimen: nivolumab maybe</think>"
            "### First-Line Treatment Recommendation:\n\n**Regimen:** Osimertinib 80mg daily."
        )
        r = parser.parse(text)
        assert r.category == "targeted_therapy"
        assert "nivolumab" not in (r.regimen_tag or "")
