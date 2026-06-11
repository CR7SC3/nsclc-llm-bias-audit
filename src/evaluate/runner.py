"""Evaluation runner for the EquityGUIDE experiment pipeline.

Orchestrates the full experiment: for each case, for each prompting strategy,
for each demographic variant, calls the model and persists the result.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Optional

from tqdm import tqdm

from src.models.gemini_model import GeminiModel
from prompts.evaluation.prompt_templates import build_prompt

logger = logging.getLogger(__name__)

_RESULTS_DIR = Path(__file__).resolve().parents[2] / "results"
_RESULTS_DIR.mkdir(parents=True, exist_ok=True)


class EvaluationRunner:
    """Orchestrates model inference across cases, variants, and strategies.

    Parameters
    ----------
    model:
        An initialised ``GeminiModel`` (or compatible model wrapper).
    strategy:
        Default prompting strategy key.  Can be overridden per call.
    output_dir:
        Root directory for persisting aggregated results.  Individual raw
        API results are also saved by the model itself to ``results/raw/``.
    """

    ALL_STRATEGIES: list[str] = [
        "baseline",
        "fairness",
        "guideline_grounded",
        "structured_extraction",
        "self_consistency",
    ]

    def __init__(
        self,
        model: Optional[GeminiModel] = None,
        strategy: str = "baseline",
        output_dir: Optional[Path] = None,
    ) -> None:
        self.model = model if model is not None else GeminiModel()
        self.strategy = strategy
        self.output_dir = output_dir or _RESULTS_DIR

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def run_case(
        self,
        case_id: str,
        clinical_note: str,
        strategy: Optional[str] = None,
        variant_label: str = "no_demographics",
    ) -> dict[str, Any]:
        """Run a single case through the model and return the result.

        Parameters
        ----------
        case_id:
            Unique case identifier (used for logging and file naming).
        clinical_note:
            The full clinical note text to pass to the model.
        strategy:
            Prompting strategy key.  Defaults to ``self.strategy``.
        variant_label:
            Demographic variant label (e.g., ``"white_male_private"``).
            Appended to ``case_id`` in the saved result.

        Returns
        -------
        dict
            The full model result dictionary augmented with ``variant_label``
            and ``strategy``.
        """
        effective_strategy = strategy or self.strategy
        full_case_id = f"{case_id}__{variant_label}__{effective_strategy}"

        prompt = build_prompt(effective_strategy, clinical_note)
        logger.info("Running case_id=%s strategy=%s variant=%s", case_id, effective_strategy, variant_label)

        result = self.model.generate_with_retry(prompt, full_case_id)
        result["variant_label"] = variant_label
        result["strategy"] = effective_strategy
        result["base_case_id"] = case_id
        return result

    def run_all_variants(
        self,
        case_id: str,
        variants: dict[str, str],
        strategy: Optional[str] = None,
    ) -> dict[str, Any]:
        """Run all demographic variants for a single case under one strategy.

        Parameters
        ----------
        case_id:
            Unique base case identifier.
        variants:
            Dictionary mapping variant label to the full clinical note text
            for that variant (as returned by ``create_all_variants``).
        strategy:
            Prompting strategy.  Defaults to ``self.strategy``.

        Returns
        -------
        dict
            Keys are variant labels; values are the corresponding result dicts.
        """
        effective_strategy = strategy or self.strategy
        variant_results: dict[str, Any] = {}

        for variant_label, clinical_note in variants.items():
            result = self.run_case(
                case_id=case_id,
                clinical_note=clinical_note,
                strategy=effective_strategy,
                variant_label=variant_label,
            )
            variant_results[variant_label] = result

        # Persist the aggregated variant set for easy downstream analysis
        self._save_variant_set(case_id, effective_strategy, variant_results)
        return variant_results

    def run_full_experiment(
        self,
        cases: dict[str, dict[str, str]],
        strategies: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """Run the complete experiment: all cases × all strategies × all variants.

        Parameters
        ----------
        cases:
            Dictionary mapping ``case_id`` → ``{variant_label: note_text}``.
            Produce this with ``create_all_variants`` applied to each case.
        strategies:
            List of strategy keys to run.  Defaults to ``ALL_STRATEGIES``.

        Returns
        -------
        dict
            Nested structure: ``{case_id: {strategy: {variant_label: result}}}``.
        """
        strategies = strategies or self.ALL_STRATEGIES
        all_results: dict[str, Any] = {}

        total_runs = len(cases) * len(strategies)
        with tqdm(total=total_runs, desc="Experiment progress", unit="case×strategy") as pbar:
            for case_id, variants in cases.items():
                all_results[case_id] = {}
                for strat in strategies:
                    pbar.set_description(f"Case {case_id} | Strategy {strat}")
                    variant_results = self.run_all_variants(
                        case_id=case_id,
                        variants=variants,
                        strategy=strat,
                    )
                    all_results[case_id][strat] = variant_results
                    pbar.update(1)

        # Persist the full experiment output
        self._save_full_experiment(all_results)
        return all_results

    # ------------------------------------------------------------------
    # Private persistence helpers
    # ------------------------------------------------------------------

    def _save_variant_set(
        self,
        case_id: str,
        strategy: str,
        variant_results: dict[str, Any],
    ) -> None:
        """Save aggregated variant results for one case + strategy."""
        subdir = self.output_dir / "variants"
        subdir.mkdir(parents=True, exist_ok=True)
        filename = subdir / f"{case_id}__{strategy}__variants.json"
        with open(filename, "w", encoding="utf-8") as fh:
            json.dump(variant_results, fh, indent=2, ensure_ascii=False)
        logger.debug("Saved variant set to %s", filename)

    def _save_full_experiment(self, all_results: dict[str, Any]) -> None:
        """Save the complete experiment result tree."""
        filename = self.output_dir / "full_experiment_results.json"
        with open(filename, "w", encoding="utf-8") as fh:
            json.dump(all_results, fh, indent=2, ensure_ascii=False)
        logger.info("Full experiment results saved to %s", filename)
