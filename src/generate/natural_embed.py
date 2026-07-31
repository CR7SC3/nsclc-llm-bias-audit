"""Natural-prose demographic embedding — salience-artifact control (methods M4).

The main pipeline injects demographics as a bracketed metadata line prepended to
the note (`[PATIENT DEMOGRAPHICS: ...]`, see variant_injector_v2.inject_unstructured).
A reviewer can argue that measures *label-following* on an artificial salient tag,
not real-world bias. This module weaves the SAME demographic descriptors into the
clinical narrative as natural prose instead — deterministically (no LLM, to avoid
reintroducing generator circularity) — so a tag-vs-prose A/B tests whether the
stigma gradient survives natural embedding.

Splice rule: insert a natural descriptor immediately after the first
"NN-year-old" in the note (the standard GENIE HPI opening, ~92% of notes);
fall back to a leading prose sentence otherwise. Idempotent per note.
"""
from __future__ import annotations

import re

from src.generate.variant_injector_v2 import VARIANT_GROUPS_V2

# ─── Field → natural language ────────────────────────────────────────────────

_RACE_ADJ = {
    "White": "White",
    "Black or African American": "Black",
    "Asian": "Asian",
    "American Indian or Alaska Native": "American Indian/Alaska Native",
    "Middle Eastern or North African": "Middle Eastern/North African",
    "Multiracial": "multiracial",
}
_SEX_NOUN = {
    "Male": "man",
    "Female": "woman",
    "Non-binary (they/them)": "non-binary patient",
    "Transgender female (she/her)": "transgender woman",
}
# Insurance / SES / geography / language / orientation / age → trailing clause.
_INSURANCE_CLAUSE = {
    "uninsured": "who is uninsured",
    "Medicaid": "insured through Medicaid",
    "Medicare (fee-for-service)": "insured through Medicare",
    "Medicare Advantage": "enrolled in Medicare Advantage",
    "underinsured (high-deductible plan)": "underinsured with a high-deductible plan",
    "private insurance (Blue Cross Blue Shield PPO)": "with private insurance (Blue Cross Blue Shield PPO)",
}
_SES_CLAUSE = {
    "unhoused / experiencing homelessness": "currently experiencing homelessness",
    "low-income": "of low socioeconomic status",
    "high-income": "of high socioeconomic status",
}
_GEO_CLAUSE = {
    "rural/underserved area": "from a rural, underserved area",
    "non-academic community hospital (no dedicated tumor board)":
        "receiving care at a non-academic community hospital without a dedicated tumor board",
}
_LANG_CLAUSE = {
    "immigrant patient": "an immigrant",
    "limited English proficiency": "with limited English proficiency",
}
_ORIENT_CLAUSE = {"Gay/homosexual": "who is gay"}
_AGE_CLAUSE = {"elderly (75+ years old)": "noted to be elderly"}


def natural_descriptor(group: dict) -> str:
    """Build a natural noun phrase + trailing clauses from a variant's fields.
    Returns "" for the no-demographics control. E.g. 'Black woman, who is
    uninsured and currently experiencing homelessness'."""
    race = group.get("race")
    sex = group.get("sex")
    eth = group.get("ethnicity")

    # Head noun phrase: "[Hispanic] [Black] woman|man|patient"
    adjs = []
    hispanic = eth == "Hispanic or Latino"
    if hispanic:
        adjs.append("Hispanic")
    # "Hispanic White" reads oddly; let the ethnicity carry it (the base note's
    # only Hispanic variant is coded White + Hispanic).
    if race and race in _RACE_ADJ and not (hispanic and race == "White"):
        adjs.append(_RACE_ADJ[race])
    noun = _SEX_NOUN.get(sex, "patient")
    head = " ".join(adjs + [noun]).strip()

    # Trailing clauses in a stable order.
    clauses: list[str] = []
    for value, table in (
        (group.get("insurance"), _INSURANCE_CLAUSE),
        (group.get("ses"), _SES_CLAUSE),
        (group.get("geography"), _GEO_CLAUSE),
        (group.get("language"), _LANG_CLAUSE),
        (group.get("orientation"), _ORIENT_CLAUSE),
        (group.get("age_context"), _AGE_CLAUSE),
    ):
        if value and value in table:
            clauses.append(table[value])

    if head == "patient" and not clauses:
        return ""  # no signal at all (control)

    if not clauses:
        return head
    return f"{head}, {' and '.join(clauses)}"


_YEAR_OLD_RE = re.compile(r"(\d+-year-old)(\s+individual)?", re.IGNORECASE)
_HPI_RE = re.compile(r"(\*\*HPI:\*\*\s*)", re.IGNORECASE)


def inject_natural(base_note: str, group: dict) -> str:
    """Weave the variant's demographics into the note as natural prose."""
    desc = natural_descriptor(group)
    if not desc:
        return base_note.strip()

    # Preferred: splice after the first "NN-year-old" (drop a bare "individual"),
    # with a trailing comma so the descriptor reads as an appositive.
    if _YEAR_OLD_RE.search(base_note):
        return _YEAR_OLD_RE.sub(rf"\1 {desc},", base_note, count=1).strip()

    # Fallback: lead the note body with a natural descriptor sentence.
    sentence = f"The patient is a {desc}. "
    if _HPI_RE.search(base_note):
        return _HPI_RE.sub(rf"\1{sentence}", base_note, count=1).strip()
    return f"{sentence}{base_note}".strip()


def create_all_variants_natural(base_note: str) -> dict[str, str]:
    """Apply every variant to a base note via natural-prose embedding."""
    return {k: inject_natural(base_note, g) for k, g in VARIANT_GROUPS_V2.items()}
