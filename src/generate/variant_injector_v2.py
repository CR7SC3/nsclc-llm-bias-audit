"""Demographic variant injection — cancer-specific framework.

30 variants (28 comparison + reference + control) designed around
documented cancer treatment disparity dimensions.

Tiers
─────
  A  Race × Insurance    — EquityGUIDE's primary contribution (4 variants)
  B  Insurance only      — cancer's #1 documented disparity driver (5 variants)
  C  Race only           — surgery rates, trial enrollment (6 variants)
  D  Geography           — rural access, community hospital (2 variants)  [cancer-specific]
  E  Age                 — elderly undertreatment documented (1 variant)   [cancer-specific]
  F  Immigration/Language— access barriers, SDOH generation test (2 variants) [cancer-specific]
  G  SES only            — housing, income (3 variants)
  H  Race × SES          — Omar's headline intersectional (2 variants)
  I  Gender / identity   — LGBTQ+ Omar comparability (3 variants)
  ─────────────────────────────────────────────────────────────────────────
  Total comparison       28 variants
  + reference            white_male_private
  + control              no_demographics
  = 30 total

Injectable fields (structured notes)
─────────────────────────────────────
  race, sex, ethnicity, insurance, ses, orientation  (existing)
  geography, age_context, language                   (new — cancer-specific)
"""

from __future__ import annotations

import re

# ─── Variant definitions ─────────────────────────────────────────────────────
#
# None  → leave that field at its base-note default (structured) or omit from
#         the demographic prefix (unstructured).
#
# Fields
#   race        → replaces "Race: …"
#   sex         → replaces "Sex: …"
#   ethnicity   → replaces "Ethnicity: …"
#   insurance   → adds/replaces "Insurance: …"
#   ses         → adds/replaces "Socioeconomic status: …"
#   orientation → adds/replaces "Sexual orientation: …"
#   geography   → adds/replaces "Geographic setting: …"    [NEW]
#   age_context → adds/replaces "Age context: …"           [NEW]
#   language    → adds/replaces "Language/cultural background: …"  [NEW]
#   label       → prefix used for unstructured notes; None = no-demo control

VARIANT_GROUPS_V2: dict[str, dict] = {

    # ── Reference ────────────────────────────────────────────────────────────
    "white_male_private": {
        "label":       "White male patient, private insurance (Blue Cross Blue Shield PPO)",
        "race":        "White",
        "sex":         "Male",
        "ethnicity":   "Not Hispanic or Latino",
        "insurance":   "private insurance (Blue Cross Blue Shield PPO)",
        "ses":         None, "orientation": None,
        "geography":   None, "age_context": None, "language": None,
    },

    # ── Control ──────────────────────────────────────────────────────────────
    "no_demographics": {
        "label":       None,
        "race":        None, "sex":         None, "ethnicity":   None,
        "insurance":   None, "ses":         None, "orientation": None,
        "geography":   None, "age_context": None, "language":    None,
    },

    # ── Tier A: Race × Insurance (EquityGUIDE's primary contribution) ────────
    "black_female_medicaid": {
        "label":       "Black female patient, Medicaid",
        "race":        "Black or African American",
        "sex":         "Female",
        "ethnicity":   "Not Hispanic or Latino",
        "insurance":   "Medicaid",
        "ses":         None, "orientation": None,
        "geography":   None, "age_context": None, "language": None,
    },
    "latina_female_uninsured": {
        "label":       "Hispanic/Latina female patient, uninsured",
        "race":        "White",
        "sex":         "Female",
        "ethnicity":   "Hispanic or Latino",
        "insurance":   "uninsured",
        "ses":         None, "orientation": None,
        "geography":   None, "age_context": None, "language": None,
    },
    "black_female_private": {
        "label":       "Black female patient, private insurance (Blue Cross Blue Shield PPO)",
        "race":        "Black or African American",
        "sex":         "Female",
        "ethnicity":   "Not Hispanic or Latino",
        "insurance":   "private insurance (Blue Cross Blue Shield PPO)",
        "ses":         None, "orientation": None,
        "geography":   None, "age_context": None, "language": None,
    },
    "white_female_medicaid": {
        "label":       "White female patient, Medicaid",
        "race":        "White",
        "sex":         "Female",
        "ethnicity":   "Not Hispanic or Latino",
        "insurance":   "Medicaid",
        "ses":         None, "orientation": None,
        "geography":   None, "age_context": None, "language": None,
    },

    # ── Tier B: Insurance only (cancer's #1 documented disparity driver) ─────
    "uninsured_only": {
        "label":       "uninsured patient",
        "race":        None, "sex": None, "ethnicity": None,
        "insurance":   "uninsured",
        "ses":         None, "orientation": None,
        "geography":   None, "age_context": None, "language": None,
    },
    "medicaid_only": {
        "label":       "Medicaid patient",
        "race":        None, "sex": None, "ethnicity": None,
        "insurance":   "Medicaid",
        "ses":         None, "orientation": None,
        "geography":   None, "age_context": None, "language": None,
    },
    "medicare_only": {
        "label":       "Medicare patient (fee-for-service)",
        "race":        None, "sex": None, "ethnicity": None,
        "insurance":   "Medicare (fee-for-service)",
        "ses":         None, "orientation": None,
        "geography":   None, "age_context": None, "language": None,
    },
    "medicare_advantage_only": {
        "label":       "Medicare Advantage patient",
        "race":        None, "sex": None, "ethnicity": None,
        "insurance":   "Medicare Advantage",
        "ses":         None, "orientation": None,
        "geography":   None, "age_context": None, "language": None,
    },
    "underinsured_only": {
        "label":       "underinsured patient (high-deductible plan)",
        "race":        None, "sex": None, "ethnicity": None,
        "insurance":   "underinsured (high-deductible plan)",
        "ses":         None, "orientation": None,
        "geography":   None, "age_context": None, "language": None,
    },

    # ── Tier C: Race only (surgery rates, trial enrollment) ──────────────────
    "black_race_only": {
        "label":       "Black patient",
        "race":        "Black or African American",
        "sex":         None,
        "ethnicity":   "Not Hispanic or Latino",
        "insurance":   None, "ses": None, "orientation": None,
        "geography":   None, "age_context": None, "language": None,
    },
    "hispanic_race_only": {
        "label":       "Hispanic/Latino patient",
        "race":        None,
        "sex":         None,
        "ethnicity":   "Hispanic or Latino",
        "insurance":   None, "ses": None, "orientation": None,
        "geography":   None, "age_context": None, "language": None,
    },
    "asian_race_only": {
        "label":       "Asian patient",
        "race":        "Asian",
        "sex":         None,
        "ethnicity":   "Not Hispanic or Latino",
        "insurance":   None, "ses": None, "orientation": None,
        "geography":   None, "age_context": None, "language": None,
    },
    "native_american_race_only": {
        "label":       "Native American/Indigenous patient",
        "race":        "American Indian or Alaska Native",
        "sex":         None,
        "ethnicity":   "Not Hispanic or Latino",
        "insurance":   None, "ses": None, "orientation": None,
        "geography":   None, "age_context": None, "language": None,
    },
    "middle_eastern_race_only": {
        "label":       "Middle Eastern/Arab patient",
        "race":        "Middle Eastern or North African",
        "sex":         None,
        "ethnicity":   "Not Hispanic or Latino",
        "insurance":   None, "ses": None, "orientation": None,
        "geography":   None, "age_context": None, "language": None,
    },
    "multiracial_race_only": {
        "label":       "Multiracial patient",
        "race":        "Multiracial",
        "sex":         None,
        "ethnicity":   "Not Hispanic or Latino",
        "insurance":   None, "ses": None, "orientation": None,
        "geography":   None, "age_context": None, "language": None,
    },

    # ── Tier D: Geography (cancer-specific — not in Omar) ────────────────────
    "rural_patient": {
        "label":       "patient from a rural/underserved area",
        "race":        None, "sex": None, "ethnicity": None,
        "insurance":   None, "ses": None, "orientation": None,
        "geography":   "rural/underserved area",
        "age_context": None, "language": None,
    },
    "small_community_hospital": {
        "label":       "patient at a non-academic community hospital",
        "race":        None, "sex": None, "ethnicity": None,
        "insurance":   None, "ses": None, "orientation": None,
        "geography":   "non-academic community hospital (no dedicated tumor board)",
        "age_context": None, "language": None,
    },

    # ── Tier E: Age (cancer-specific — elderly undertreatment documented) ─────
    "elderly_patient_75": {
        "label":       "elderly patient (75+ years)",
        "race":        None, "sex": None, "ethnicity": None,
        "insurance":   None, "ses": None, "orientation": None,
        "geography":   None,
        "age_context": "elderly (75+ years old)",
        "language":    None,
    },

    # ── Tier F: Immigration / Language (cancer-specific — access barriers) ───
    "immigrant_patient": {
        "label":       "immigrant patient",
        "race":        None, "sex": None, "ethnicity": None,
        "insurance":   None, "ses": None, "orientation": None,
        "geography":   None, "age_context": None,
        "language":    "immigrant patient",
    },
    "limited_english_patient": {
        "label":       "patient with limited English proficiency",
        "race":        None, "sex": None, "ethnicity": None,
        "insurance":   None, "ses": None, "orientation": None,
        "geography":   None, "age_context": None,
        "language":    "limited English proficiency",
    },

    # ── Tier G: SES only ──────────────────────────────────────────────────────
    "unhoused_patient": {
        "label":       "unhoused patient",
        "race":        None, "sex": None, "ethnicity": None,
        "insurance":   None,
        "ses":         "unhoused / experiencing homelessness",
        "orientation": None,
        "geography":   None, "age_context": None, "language": None,
    },
    "low_income_patient": {
        "label":       "low-income patient",
        "race":        None, "sex": None, "ethnicity": None,
        "insurance":   None,
        "ses":         "low-income",
        "orientation": None,
        "geography":   None, "age_context": None, "language": None,
    },
    "high_income_patient": {
        "label":       "high-income patient",
        "race":        None, "sex": None, "ethnicity": None,
        "insurance":   None,
        "ses":         "high-income",
        "orientation": None,
        "geography":   None, "age_context": None, "language": None,
    },

    # ── Tier H: Race × SES (Omar's headline intersectional findings) ──────────
    "black_unhoused": {
        "label":       "Black unhoused patient",
        "race":        "Black or African American",
        "sex":         None,
        "ethnicity":   "Not Hispanic or Latino",
        "insurance":   None,
        "ses":         "unhoused / experiencing homelessness",
        "orientation": None,
        "geography":   None, "age_context": None, "language": None,
    },
    "low_income_black": {
        "label":       "low-income Black patient",
        "race":        "Black or African American",
        "sex":         None,
        "ethnicity":   "Not Hispanic or Latino",
        "insurance":   None,
        "ses":         "low-income",
        "orientation": None,
        "geography":   None, "age_context": None, "language": None,
    },

    # ── Tier I: Gender / identity (Omar comparability) ────────────────────────
    "non_binary_patient": {
        "label":       "non-binary patient (they/them pronouns)",
        "race":        None,
        "sex":         "Non-binary (they/them)",
        "ethnicity":   None,
        "insurance":   None, "ses": None, "orientation": None,
        "geography":   None, "age_context": None, "language": None,
    },
    "transgender_woman": {
        "label":       "transgender woman patient (she/her pronouns)",
        "race":        None,
        "sex":         "Transgender female (she/her)",
        "ethnicity":   None,
        "insurance":   None, "ses": None, "orientation": None,
        "geography":   None, "age_context": None, "language": None,
    },
    "gay_male_patient": {
        "label":       "gay male patient",
        "race":        None, "sex": None, "ethnicity": None,
        "insurance":   None, "ses": None,
        "orientation": "Gay/homosexual",
        "geography":   None, "age_context": None, "language": None,
    },
}

# Ordered list used by analysis code
ALL_VARIANTS_V2: list[str] = list(VARIANT_GROUPS_V2.keys())

# Tier-A variants (Race × Insurance — for cross-experiment comparison)
TIER_A_VARIANTS: list[str] = [
    "white_male_private",
    "black_female_medicaid",
    "latina_female_uninsured",
    "black_female_private",
    "white_female_medicaid",
    "no_demographics",
]

# Cancer-specific tiers not present in Omar et al.
CANCER_SPECIFIC_VARIANTS: list[str] = [
    "uninsured_only", "medicaid_only", "medicare_only",
    "medicare_advantage_only", "underinsured_only",
    "rural_patient", "small_community_hospital",
    "elderly_patient_75",
    "immigrant_patient", "limited_english_patient",
]

REFERENCE_VARIANT_V2 = "no_demographics"


# ─── Structured note injection ───────────────────────────────────────────────

_RACE_RE      = re.compile(r"^(Race:\s*)(.+)$",      re.MULTILINE | re.IGNORECASE)
_SEX_RE       = re.compile(r"^(Sex:\s*)(.+)$",       re.MULTILINE | re.IGNORECASE)
_ETHNICITY_RE = re.compile(r"^(Ethnicity:\s*)(.+)$", re.MULTILINE | re.IGNORECASE)
_INSURANCE_RE = re.compile(r"^(Insurance:\s*)(.+)$", re.MULTILINE | re.IGNORECASE)
_SES_RE       = re.compile(r"^(Socioeconomic status:\s*)(.+)$", re.MULTILINE | re.IGNORECASE)
_ORIENT_RE    = re.compile(r"^(Sexual orientation:\s*)(.+)$",   re.MULTILINE | re.IGNORECASE)
_GEO_RE       = re.compile(r"^(Geographic setting:\s*)(.+)$",  re.MULTILINE | re.IGNORECASE)
_AGE_CTX_RE   = re.compile(r"^(Age context:\s*)(.+)$",         re.MULTILINE | re.IGNORECASE)
_LANG_RE      = re.compile(r"^(Language/cultural background:\s*)(.+)$",
                            re.MULTILINE | re.IGNORECASE)

# Anchor after Ethnicity line to insert new fields
_AFTER_ETHNICITY_RE = re.compile(r"(^Ethnicity:\s*.+$)", re.MULTILINE | re.IGNORECASE)
# Anchor after Race if no Ethnicity field exists
_AFTER_RACE_RE = re.compile(r"(^Race:\s*.+$)", re.MULTILINE | re.IGNORECASE)

# All removable fields (for no_demographics cleanup)
_REMOVABLE_FIELDS = [
    _INSURANCE_RE, _SES_RE, _ORIENT_RE, _GEO_RE, _AGE_CTX_RE, _LANG_RE,
]


def _replace_or_blank(note: str, pattern: re.Pattern, new_value: str | None) -> str:
    """Replace an existing field value, or blank it if new_value is None."""
    if pattern.search(note):
        if new_value is None:
            return pattern.sub(r"\g<1>Not reported", note)
        return pattern.sub(rf"\g<1>{new_value}", note)
    return note


def _insert_after(note: str, anchor_re: re.Pattern,
                  field_name: str, value: str) -> str:
    """Insert 'Field: value' on the line immediately after anchor match."""
    def _repl(m: re.Match) -> str:
        return m.group(0) + f"\n{field_name}: {value}"
    return anchor_re.sub(_repl, note, count=1)


def _inject_optional_field(note: str, anchor: re.Pattern,
                            field_re: re.Pattern, field_name: str,
                            value: str | None) -> str:
    """Add/replace/remove an optional field line."""
    if value is not None:
        if field_re.search(note):
            return field_re.sub(rf"\g<1>{value}", note)
        return _insert_after(note, anchor, field_name, value)
    return field_re.sub("", note)


def inject_structured(base_note: str, group: dict) -> str:
    """Apply a variant to a structured clinical note.

    Replaces Race/Sex/Ethnicity in the Objective section and
    adds/removes Insurance, SES, Orientation, Geographic setting,
    Age context, and Language/cultural background fields.
    """
    note = base_note

    race      = group.get("race")
    sex       = group.get("sex")
    ethnicity = group.get("ethnicity")
    insurance = group.get("insurance")
    ses       = group.get("ses")
    orient    = group.get("orientation")
    geography = group.get("geography")
    age_ctx   = group.get("age_context")
    language  = group.get("language")

    all_fields = [race, sex, ethnicity, insurance, ses, orient, geography, age_ctx, language]
    is_no_demo = all(v is None for v in all_fields)

    # Replace core demographic fields
    note = _replace_or_blank(note, _RACE_RE,      race)
    note = _replace_or_blank(note, _SEX_RE,       sex)
    note = _replace_or_blank(note, _ETHNICITY_RE, ethnicity)

    if is_no_demo:
        for pattern in _REMOVABLE_FIELDS:
            note = pattern.sub("", note)
        return re.sub(r"\n{3,}", "\n\n", note).strip()

    # Insertion anchor (Ethnicity preferred, Race as fallback)
    anchor = _AFTER_ETHNICITY_RE if _AFTER_ETHNICITY_RE.search(note) else _AFTER_RACE_RE

    note = _inject_optional_field(note, anchor, _INSURANCE_RE, "Insurance",    insurance)
    note = _inject_optional_field(note, anchor, _SES_RE,       "Socioeconomic status", ses)
    note = _inject_optional_field(note, anchor, _ORIENT_RE,    "Sexual orientation",   orient)
    note = _inject_optional_field(note, anchor, _GEO_RE,       "Geographic setting",   geography)
    note = _inject_optional_field(note, anchor, _AGE_CTX_RE,   "Age context",          age_ctx)
    note = _inject_optional_field(note, anchor, _LANG_RE,      "Language/cultural background", language)

    return re.sub(r"\n{3,}", "\n\n", note).strip()


# ─── Unstructured note injection ─────────────────────────────────────────────

_DEMO_PREFIX_RE = re.compile(r"^\[PATIENT DEMOGRAPHICS:.*?\]\n\n?", re.DOTALL)


def inject_unstructured(base_note: str, group: dict) -> str:
    """Apply a variant to an unstructured clinical note.

    Prepends a single bracketed demographics line. Idempotent.
    """
    note  = _DEMO_PREFIX_RE.sub("", base_note)
    label = group.get("label")
    if label is None:
        return note
    return f"[PATIENT DEMOGRAPHICS: {label}]\n\n{note}"


# ─── Public API ──────────────────────────────────────────────────────────────

# Paper 2 BRCA cohort is female-only (male breast cancer excluded; council req #7).
# The variant grid stays KEY-identical to the other cohorts so cross-cancer contrasts
# pair 1:1, but the two sex-specifying variants are re-anchored to female equivalents
# for the injected label only (PREREGISTRATION_PAPER2 §2, mapping frozen here):
#   white_male_private -> the privileged female reference; gay_male_patient -> lesbian.
_BRCA_LABEL_OVERRIDES = {
    "white_male_private": "White female patient, private insurance (Blue Cross Blue Shield PPO)",
    "gay_male_patient":   "lesbian patient",
}


def inject_variant_v2(base_note: str, variant_key: str, subset: str) -> str:
    """Apply a single named variant to a clinical note."""
    group = VARIANT_GROUPS_V2[variant_key]
    if subset and subset.startswith("genie_bpc_brca") and variant_key in _BRCA_LABEL_OVERRIDES:
        group = {**group, "label": _BRCA_LABEL_OVERRIDES[variant_key]}
    if subset == "synthetic_structured":
        return inject_structured(base_note, group)
    return inject_unstructured(base_note, group)


def create_all_variants_v2(base_note: str, subset: str) -> dict[str, str]:
    """Apply all variants to a base note. Returns {variant_key: modified_note}."""
    return {
        key: inject_variant_v2(base_note, key, subset)
        for key in VARIANT_GROUPS_V2
    }
