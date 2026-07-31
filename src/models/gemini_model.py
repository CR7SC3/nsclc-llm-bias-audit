"""Gemini model wrapper using google-genai SDK routed through Vertex AI.

Routes through Vertex AI so calls bill to your Google Cloud project
and draw from the $300 free trial credit.

Authentication: Application Default Credentials (ADC).
Run once: gcloud auth application-default login
          gcloud auth application-default set-quota-project equityguide

Required .env variables:
    GOOGLE_CLOUD_PROJECT   — your Google Cloud project ID (e.g. equityguide)
    GOOGLE_CLOUD_LOCATION  — region (e.g. us-central1)
"""

from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

_RESULTS_RAW_DIR = Path(__file__).resolve().parents[2] / "results" / "raw"
_RESULTS_RAW_DIR.mkdir(parents=True, exist_ok=True)


class GeminiModel:
    """Wrapper around Gemini via Vertex AI for reproducible, auditable inference.

    Every call is persisted to results/raw/ as a timestamped JSON file.

    Parameters
    ----------
    model_name:
        Gemini model identifier, e.g. ``"gemini-2.0-flash"``.
    temperature:
        Sampling temperature. Use 0 for deterministic output.
    inter_call_sleep:
        Seconds to sleep between calls to respect rate limits.
    max_retries:
        Maximum retry attempts in ``generate_with_retry``.
    retry_wait:
        Seconds to wait between retry attempts.
    """

    def __init__(
        self,
        model_name: str = "gemini-2.5-flash",
        temperature: float = 1.0,
        inter_call_sleep: float = 2.0,
        max_retries: int = 3,
        retry_wait: float = 60.0,
    ) -> None:
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

        if not project:
            raise EnvironmentError(
                "GOOGLE_CLOUD_PROJECT is not set. Add it to your .env file."
            )

        # vertexai=True routes through Vertex AI using ADC credentials,
        # billing your Cloud project instead of AI Studio prepay credits.
        # http_options.timeout (ms) bounds each request so an occasionally-stuck
        # Vertex call fails fast and hits generate_with_retry instead of hanging
        # the whole run indefinitely.
        self._client = genai.Client(
            vertexai=True,
            project=project,
            location=location,
            http_options=types.HttpOptions(timeout=120_000),
        )

        self.model_name = model_name
        self.temperature = temperature
        self.inter_call_sleep = inter_call_sleep
        self.max_retries = max_retries
        self.retry_wait = retry_wait

        # Disable extended thinking — oncology prompts trigger Gemini 2.5 Flash's
        # full reasoning mode (~23s/call). thinking_budget=0 forces direct
        # generation (~2-3s/call) which is appropriate for structured prompts.
        # NOTE: was 600 — that truncated 100% of responses mid-rationale, biasing
        # soft-bias metrics low and making Gemini non-comparable to the other
        # models (2048). Raised to 2048 to match openai/deepseek/anthropic wrappers.
        self._gen_config = types.GenerateContentConfig(
            temperature=temperature,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            max_output_tokens=2048,
        )

        logger.info(
            "GeminiModel initialised (Vertex AI): model=%s project=%s location=%s",
            model_name, project, location,
        )

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def generate(self, prompt: str, case_id: str) -> dict[str, Any]:
        """Send a single prompt to Gemini and persist the result.

        Parameters
        ----------
        prompt:
            The complete formatted prompt string.
        case_id:
            Unique case identifier for logging and file naming.

        Returns
        -------
        dict
            Keys: ``case_id``, ``model``, ``prompt``, ``response_text``,
            ``timestamp``, ``prompt_tokens``, ``completion_tokens``,
            ``total_tokens``.
        """
        timestamp = datetime.utcnow().isoformat()
        logger.info("Generating response for case_id=%s", case_id)

        response = self._client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=self._gen_config,
        )

        prompt_tokens = getattr(response.usage_metadata, "prompt_token_count", None)
        completion_tokens = getattr(response.usage_metadata, "candidates_token_count", None)
        total_tokens = (
            (prompt_tokens or 0) + (completion_tokens or 0)
            if (prompt_tokens is not None and completion_tokens is not None)
            else None
        )

        result: dict[str, Any] = {
            "case_id": case_id,
            "model": self.model_name,
            "prompt": prompt,
            "response_text": response.text,
            "timestamp": timestamp,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
        }

        self._save_result(result, case_id, timestamp)
        time.sleep(self.inter_call_sleep)
        return result

    def generate_with_retry(self, prompt: str, case_id: str) -> dict[str, Any]:
        """Call ``generate`` with up to ``max_retries`` retry attempts.

        Parameters
        ----------
        prompt:
            The complete formatted prompt string.
        case_id:
            Unique case identifier.
        """
        last_exc: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info("Attempt %d/%d for case_id=%s", attempt, self.max_retries, case_id)
                return self.generate(prompt, case_id)
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                logger.warning(
                    "Attempt %d failed for case_id=%s: %s. Waiting %ds before retry.",
                    attempt, case_id, exc, self.retry_wait,
                )
                if attempt < self.max_retries:
                    time.sleep(self.retry_wait)

        raise RuntimeError(
            f"All {self.max_retries} attempts failed for case_id={case_id}. "
            f"Last error: {last_exc}"
        ) from last_exc

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _save_result(self, result: dict[str, Any], case_id: str, timestamp: str) -> None:
        """Persist a single inference result to results/raw/ as JSON."""
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = _RESULTS_RAW_DIR / f"{case_id}_{safe_timestamp}.json"
        try:
            with open(filename, "w", encoding="utf-8") as fh:
                json.dump(result, fh, indent=2, ensure_ascii=False)
            logger.debug("Saved result to %s", filename)
        except OSError as exc:
            logger.error("Failed to save result for case_id=%s: %s", case_id, exc)
