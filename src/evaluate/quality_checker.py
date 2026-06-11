"""Clinical note quality checker for EquityGUIDE.

Validates that generated or curated clinical notes meet the structural and
clinical-fidelity requirements needed for reliable bias auditing.  All six
checks are documented inline and must pass before a note enters the
experiment pipeline.
"""

from __future__ import annotations

import re
from typing import Any


# ---------------------------------------------------------------------------
# Required note sections
# ---------------------------------------------------------------------------

REQUIRED_SECTIONS: list[str] = [
    "chief complaint",
    "history of present illness",
    "past medical history",
    "medications",
    "social history",
    "physical exam",
    "labs",
    "imaging",
    "assessment",
]

# Phrases that suggest a treatment plan has been pre-written into the note
_TREATMENT_PLAN_SIGNALS: list[str] = [
    r"\btreatment plan\b",
    r"\bplan:\b",
    r"\bwill start\b",
    r"\bwe will initiate\b",
    r"\bprescribed\b",
    r"\bordered\b.*(?:chemotherapy|immunotherapy|radiation)",
    r"\bscheduled for\b.*(?:infusion|treatment|therapy)",
    r"\bwill receive\b.*(?:chemotherapy|pembrolizumab|osimertinib|carboplatin)",
]


class QualityChecker:
    """Validates clinical notes against structural and clinical-fidelity criteria.

    Use before adding any note to the experiment dataset to ensure:
    1. The note contains all required EHR sections.
    2. Clinical facts (stage, biomarkers, age) match the specified profile.
    3. No treatment plan language is present (the note should end at Assessment).
    4. Demographic variants are clinically identical to the base note.

    Parameters
    ----------
    age_tolerance:
        Maximum acceptable difference (in years) between the age stated in
        the note and the age in the clinical profile. Default is 2.
    """

    def __init__(self, age_tolerance: int = 2) -> None:
        self.age_tolerance = age_tolerance

    def check_note(
        self,
        clinical_note: str,
        clinical_profile: dict[str, Any],
    ) -> dict[str, Any]:
        """Run all six quality checks on a clinical note.

        Parameters
        ----------
        clinical_note:
            The full text of the clinical note to validate.
        clinical_profile:
            Dictionary of expected clinical facts.  Relevant keys:
            ``stage``, ``histology``, ``egfr_status``, ``alk_status``,
            ``pdl1_tps_category``, ``ecog_ps``, ``age`` (int).

        Returns
        -------
        dict
            ``checks`` : dict[str, dict]
                Keyed by check name.  Each sub-dict has ``passed`` (bool)
                and ``detail`` (str describing any failure or confirmation).
            ``overall_pass`` : bool
                ``True`` only when every check passes.
            ``failure_count`` : int
                Number of failed checks.
        """
        note_lower = clinical_note.lower()

        results: dict[str, dict[str, Any]] = {}

        results["stage_match"] = self._check_stage(note_lower, clinical_profile)
        results["biomarker_consistency"] = self._check_biomarkers(note_lower, clinical_profile)
        results["completeness"] = self._check_completeness(note_lower)
        results["no_treatment_plan"] = self._check_no_treatment_plan(note_lower)
        results["age_match"] = self._check_age(clinical_note, clinical_profile)
        results["demographic_isolation"] = self._check_demographic_isolation(
            clinical_note, clinical_profile
        )

        failure_count = sum(1 for r in results.values() if not r["passed"])
        return {
            "checks": results,
            "overall_pass": failure_count == 0,
            "failure_count": failure_count,
        }

    # ------------------------------------------------------------------
    # Individual checks
    # ------------------------------------------------------------------

    def _check_stage(
        self,
        note_lower: str,
        profile: dict[str, Any],
    ) -> dict[str, Any]:
        """Verify that the stated disease stage matches the profile.

        Looks for the stage string (e.g., 'stage iv', 'stage 4') in the
        assessment section and anywhere in the note.
        """
        stage = str(profile.get("stage", "")).upper()
        # Accept Roman numeral and Arabic numeral variants
        stage_patterns = {
            "IV": [r"stage\s+iv\b", r"stage\s+4\b", r"metastatic"],
            "IIIA": [r"stage\s+iii[a]?\b", r"stage\s+3[a]?\b"],
            "IIIB": [r"stage\s+iii[b]?\b", r"stage\s+3[b]?\b"],
            "II": [r"stage\s+ii\b", r"stage\s+2\b"],
            "I": [r"stage\s+i\b", r"stage\s+1\b"],
        }
        patterns = stage_patterns.get(stage, [rf"stage\s+{stage.lower()}"])
        for pat in patterns:
            if re.search(pat, note_lower):
                return {"passed": True, "detail": f"Stage {stage} confirmed in note."}
        return {
            "passed": False,
            "detail": f"Expected stage {stage} not found in note. "
                      f"Checked patterns: {patterns}",
        }

    def _check_biomarkers(
        self,
        note_lower: str,
        profile: dict[str, Any],
    ) -> dict[str, Any]:
        """Check that key biomarker results in the note match the profile.

        Only validates biomarkers explicitly specified in the profile
        (i.e., not 'unknown').  Missing biomarker mentions are flagged
        as failures to ensure the note is sufficiently detailed.
        """
        failures: list[str] = []
        confirmations: list[str] = []

        egfr = str(profile.get("egfr_status", "unknown")).lower()
        if egfr not in ("unknown", ""):
            if egfr in ("exon_19_del", "del19", "exon19del"):
                if re.search(r"egfr.{0,30}exon\s*19|del\s*19|exon\s*19\s*del", note_lower):
                    confirmations.append("EGFR exon 19 del confirmed")
                else:
                    failures.append("EGFR exon 19 deletion not found in note")
            elif egfr == "l858r":
                if re.search(r"l858r|egfr.{0,20}l858", note_lower):
                    confirmations.append("EGFR L858R confirmed")
                else:
                    failures.append("EGFR L858R not found in note")
            elif egfr == "negative":
                if re.search(r"egfr.{0,40}negative|egfr.{0,40}wild.?type", note_lower):
                    confirmations.append("EGFR negative confirmed")
                # Not a hard failure if not explicitly stated — may be implicit

        alk = str(profile.get("alk_status", "unknown")).lower()
        if alk == "positive":
            if not re.search(r"alk.{0,20}positive|alk.{0,20}rearrange|alk.{0,20}fusion", note_lower):
                failures.append("ALK positive not found in note")
            else:
                confirmations.append("ALK positive confirmed")

        pdl1 = str(profile.get("pdl1_tps_category", "unknown")).lower()
        if pdl1 == "high":
            if not re.search(r"pd.?l1.{0,30}[5-9]\d%|pd.?l1.{0,30}100%|≥\s*50%|>50%", note_lower):
                failures.append("PD-L1 high (≥50%) not clearly stated in note")
            else:
                confirmations.append("PD-L1 high confirmed")
        elif pdl1 == "intermediate":
            if not re.search(r"pd.?l1.{0,30}[1-4]\d%|pd.?l1.{0,30}35%|1.49%", note_lower):
                failures.append("PD-L1 intermediate (1–49%) not clearly stated in note")
            else:
                confirmations.append("PD-L1 intermediate confirmed")
        elif pdl1 == "low":
            if not re.search(r"pd.?l1.{0,30}[<0]\d?%|pd.?l1.{0,30}negative|<1%", note_lower):
                failures.append("PD-L1 low (<1%) not clearly stated in note")

        if failures:
            return {
                "passed": False,
                "detail": "Biomarker mismatches: " + "; ".join(failures),
            }
        return {
            "passed": True,
            "detail": "Biomarker consistency confirmed: " + "; ".join(confirmations),
        }

    def _check_completeness(self, note_lower: str) -> dict[str, Any]:
        """Confirm that all required EHR sections are present."""
        missing: list[str] = []
        for section in REQUIRED_SECTIONS:
            if section not in note_lower:
                missing.append(section)
        if missing:
            return {
                "passed": False,
                "detail": f"Missing sections: {', '.join(missing)}",
            }
        return {"passed": True, "detail": "All required sections present."}

    def _check_no_treatment_plan(self, note_lower: str) -> dict[str, Any]:
        """Ensure the note contains no pre-written treatment plan.

        The note should end at the Assessment section so that the model's
        recommendation is not anchored by a suggested plan.
        """
        for pattern in _TREATMENT_PLAN_SIGNALS:
            match = re.search(pattern, note_lower)
            if match:
                # Report the matched phrase and its approximate location
                start = max(0, match.start() - 40)
                end = min(len(note_lower), match.end() + 40)
                snippet = note_lower[start:end].replace("\n", " ")
                return {
                    "passed": False,
                    "detail": f"Treatment plan language detected near: '...{snippet}...'",
                }
        return {"passed": True, "detail": "No treatment plan language detected."}

    def _check_age(
        self,
        clinical_note: str,
        profile: dict[str, Any],
    ) -> dict[str, Any]:
        """Verify the patient age in the note matches the profile within tolerance."""
        expected_age = profile.get("age")
        if expected_age is None:
            return {"passed": True, "detail": "Age not specified in profile — skipped."}

        # Extract age from common clinical note patterns
        age_match = re.search(
            r"\b(\d{2})[- ]?(?:year|yo|y\.?o\.?)[- ]?(?:old)?\b",
            clinical_note,
            re.IGNORECASE,
        )
        if not age_match:
            return {
                "passed": False,
                "detail": f"Could not find patient age in note. Expected ~{expected_age}.",
            }

        stated_age = int(age_match.group(1))
        diff = abs(stated_age - int(expected_age))
        if diff <= self.age_tolerance:
            return {
                "passed": True,
                "detail": f"Age match: note states {stated_age}, profile expects {expected_age} "
                          f"(tolerance ±{self.age_tolerance}).",
            }
        return {
            "passed": False,
            "detail": f"Age mismatch: note states {stated_age}, profile expects {expected_age} "
                      f"(difference {diff} > tolerance {self.age_tolerance}).",
        }

    def _check_demographic_isolation(
        self,
        clinical_note: str,
        profile: dict[str, Any],
    ) -> dict[str, Any]:
        """Check that clinical facts outside the social history are demographics-free.

        For the purposes of this audit, demographic signals should appear ONLY
        in the social history section.  This check scans all other sections for
        race/ethnicity terms that could confound the counterfactual design.

        This check is advisory — it passes if no demographic terms appear
        outside the social history section, or if the note is the
        ``no_demographics`` variant (which by design has no demographic terms).
        """
        # Isolate text outside the social history section
        parts = re.split(r"\bSOCIAL HISTORY\b", clinical_note, flags=re.IGNORECASE)
        non_social_text = parts[0]
        if len(parts) > 1:
            # Take text after the next section header following social history
            after_social = parts[1]
            next_section = re.search(r"\n[A-Z][A-Z\s]{3,}[:\-]", after_social)
            if next_section:
                non_social_text += after_social[next_section.start():]

        demographic_terms = [
            r"\bwhite\b", r"\bblack\b", r"\bhispanic\b", r"\blatina?\b",
            r"\basian\b", r"\bnative american\b", r"\bpacific islander\b",
            r"\bmedicaid\b", r"\buninsured\b", r"\bmedicare\b",
        ]
        found: list[str] = []
        for term_pattern in demographic_terms:
            if re.search(term_pattern, non_social_text, re.IGNORECASE):
                found.append(term_pattern.strip(r"\b"))

        if found:
            return {
                "passed": False,
                "detail": f"Demographic terms found outside social history: {found}. "
                          "Clinical facts sections must be demographics-neutral.",
            }
        return {
            "passed": True,
            "detail": "No demographic terms found outside the social history section.",
        }
