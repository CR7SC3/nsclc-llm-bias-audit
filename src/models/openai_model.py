"""OpenAI model wrapper for EquityGUIDE.

Matches the GeminiModel interface exactly: generate() and generate_with_retry()
return the same dict schema so run_experiment.py works unchanged.

Authentication: set OPENAI_API_KEY in .env

Supported models
----------------
    gpt-4o             — flagship, best for cross-model comparison
    gpt-4o-mini        — cheaper, lower quality
    o1                 — reasoning model (temperature fixed at 1, no system prompt)
    o3                 — reasoning model (temperature fixed at 1)
    o4-mini            — reasoning model, efficient
"""

from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_RESULTS_RAW_DIR = Path(__file__).resolve().parents[2] / "results" / "raw"
_RESULTS_RAW_DIR.mkdir(parents=True, exist_ok=True)

# Reasoning models have fixed temperature=1 and don't accept the parameter
_REASONING_MODELS = {"o1", "o1-mini", "o1-preview", "o3", "o3-mini", "o4-mini"}


class OpenAIModel:
    """Wrapper around OpenAI Chat Completions API.

    Parameters
    ----------
    model_name:
        OpenAI model identifier, e.g. ``"gpt-4o"`` or ``"o1"``.
    temperature:
        Sampling temperature (0 = deterministic). Ignored for reasoning models.
    inter_call_sleep:
        Seconds to sleep between calls to respect rate limits.
    max_retries:
        Maximum retry attempts in ``generate_with_retry``.
    retry_wait:
        Seconds to wait between retry attempts.
    max_tokens:
        Maximum completion tokens. Reasoning models use max_completion_tokens.
    """

    def __init__(
        self,
        model_name: str = "gpt-4o",
        temperature: float = 0,
        inter_call_sleep: float = 1.0,
        max_retries: int = 3,
        retry_wait: float = 30.0,
        max_tokens: int = 2048,
    ) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError("OPENAI_API_KEY not set in .env")

        self._client = OpenAI(api_key=api_key)
        self.model_name = model_name
        self.temperature = temperature
        self.inter_call_sleep = inter_call_sleep
        self.max_retries = max_retries
        self.retry_wait = retry_wait
        self.max_tokens = max_tokens
        self._is_reasoning = any(model_name.startswith(r) for r in _REASONING_MODELS)

        logger.info("OpenAIModel initialised: model=%s", model_name)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def generate(self, prompt: str, case_id: str) -> dict[str, Any]:
        """Send a single prompt and return a result dict matching GeminiModel schema."""
        timestamp = datetime.utcnow().isoformat()
        logger.info("Generating response for case_id=%s", case_id)

        kwargs: dict[str, Any] = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
        }

        if self._is_reasoning:
            kwargs["max_completion_tokens"] = self.max_tokens
            # Reasoning models do not accept temperature or system role
        else:
            kwargs["temperature"] = self.temperature
            kwargs["max_tokens"] = self.max_tokens

        response = self._client.chat.completions.create(**kwargs)

        response_text = response.choices[0].message.content or ""
        usage = response.usage

        result: dict[str, Any] = {
            "case_id": case_id,
            "model": self.model_name,
            "prompt": prompt,
            "response_text": response_text,
            "timestamp": timestamp,
            "prompt_tokens": usage.prompt_tokens if usage else None,
            "completion_tokens": usage.completion_tokens if usage else None,
            "total_tokens": usage.total_tokens if usage else None,
        }

        self._save_result(result, case_id, timestamp)
        time.sleep(self.inter_call_sleep)
        return result

    def generate_with_retry(self, prompt: str, case_id: str) -> dict[str, Any]:
        """Call ``generate`` with up to ``max_retries`` retry attempts."""
        last_exc: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info("Attempt %d/%d for case_id=%s", attempt, self.max_retries, case_id)
                return self.generate(prompt, case_id)
            except Exception as exc:
                last_exc = exc
                logger.warning(
                    "Attempt %d failed for case_id=%s: %s. Waiting %ds.",
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
        safe_ts = timestamp.replace(":", "-").replace(".", "-")
        filename = _RESULTS_RAW_DIR / f"{case_id}_{safe_ts}.json"
        try:
            with open(filename, "w", encoding="utf-8") as fh:
                json.dump(result, fh, indent=2, ensure_ascii=False)
        except OSError as exc:
            logger.error("Failed to save result for case_id=%s: %s", case_id, exc)
