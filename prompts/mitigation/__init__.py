"""The mitigation prompts, gathered in one place.

These are the five prompts the v3 intervention study runs against the baseline
to see which ones remove the bias without breaking the clinical recommendation.
The full text of each lives in ``prompts/evaluation/prompt_templates.py`` (that
file is the single source of truth). This module just names the five and gives a
plain description of what each one tries to do, so the mitigation set can be read
on its own.

  fairness
      Tells the model to ignore race, sex, insurance, and socioeconomic status
      and to decide only on staging, histology, molecular markers, performance
      status, and comorbidities.

  guideline_grounded
      Asks the model to name the NCCN category, walk the pathway step by step,
      and state the preferred category-1 treatment. The idea is that a fixed
      pathway leaves less room for demographic drift.

  structured_extraction
      Two steps. First the model pulls the clinical facts with no demographics.
      Then it recommends a treatment using only those facts, without looking back
      at the original note.

  counterfactual_check
      The model drafts an answer, then asks itself whether the answer or its
      wording would change if the patient's demographics were different, then
      revises so the recommendation rests on clinical facts alone.

  stigma_targeted
      The model may not add adherence doubts, social-determinant caveats, social
      work or financial-counseling referrals, or prognosis hedging unless the note
      itself documents them. This aims straight at the stigma layer, which is the
      part of the soft bias that is not warranted care.

Note on what mitigation did here: on the DeepSeek 151-case re-score all four
naive arms overcorrected. They cut the stigma wording but also weakened warranted
care. Read these as a proof of concept for the discussion, not a clean fix.
"""

from __future__ import annotations

from ..evaluation.prompt_templates import PROMPTS, build_prompt

# The strategy keys that count as mitigation (as opposed to baseline, rating,
# and self_consistency, which are reference and measurement prompts).
MITIGATION_STRATEGIES: list[str] = [
    "fairness",
    "guideline_grounded",
    "structured_extraction",
    "counterfactual_check",
    "stigma_targeted",
]

# Convenience view: only the mitigation prompts, keyed by strategy name.
MITIGATION_PROMPTS: dict[str, str] = {
    name: PROMPTS[name] for name in MITIGATION_STRATEGIES
}

__all__ = ["MITIGATION_STRATEGIES", "MITIGATION_PROMPTS", "build_prompt"]
