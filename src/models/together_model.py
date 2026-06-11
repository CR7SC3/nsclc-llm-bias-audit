"""Together.ai model wrapper for EquityGUIDE.

Together.ai hosts open-source models with an OpenAI-compatible API.
New accounts receive $25 free credits — enough for multiple full runs.

Authentication: set TOGETHER_API_KEY in .env
Get a free key at: api.together.ai

Matches the GeminiModel interface exactly so run_experiment.py works unchanged.

Supported models (Together.ai model IDs)
-----------------------------------------
    meta-llama/Llama-3.3-70B-Instruct-Turbo   — Llama 3.3 70B (recommended)
    meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo
    mistralai/Mixtral-8x7B-Instruct-v0.1
    mistralai/Mixtral-8x22B-Instruct-v0.1

Cost estimates (2025 pricing)
-------------------------------
    Llama 3.3 70B: ~$0.88/1M tokens in+out → ~$1.50 for 990 calls
    Mixtral 8x7B:  ~$0.60/1M tokens        → ~$1.00 for 990 calls
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

_TOGETHER_BASE_URL = "https://api.together.xyz/v1"
_RESULTS_RAW_DIR = Path(__file__).resolve().parents[2] / "results" / "raw"
_RESULTS_RAW_DIR.mkdir(parents=True, exist_ok=True)


class TogetherModel:
    """Wrapper around Together.ai using the OpenAI-compatible API.

    Parameters
    ----------
    model_name:
        Together.ai model ID, e.g. ``"meta-llama/Llama-3.3-70B-Instruct-Turbo"``.
    temperature:
        Sampling temperature (0 = deterministic).
    inter_call_sleep:
        Seconds to sleep between calls.
    max_retries:
        Maximum retry attempts in ``generate_with_retry``.
    retry_wait:
        Seconds to wait between retry attempts.
    max_tokens:
        Maximum completion tokens.
    """

    def __init__(
        self,
        model_name: str = "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        temperature: float = 0,
        inter_call_sleep: float = 1.0,
        max_retries: int = 3,
        retry_wait: float = 30.0,
        max_tokens: int = 2048,
    ) -> None:
        api_key = os.getenv("TOGETHER_API_KEY")
        if not api_key:
            raise EnvironmentError("TOGETHER_API_KEY not set in .env")

        self._client = OpenAI(api_key=api_key, base_url=_TOGETHER_BASE_URL)
        self.model_name = model_name
        self.temperature = temperature
        self.inter_call_sleep = inter_call_sleep
        self.max_retries = max_retries
        self.retry_wait = retry_wait
        self.max_tokens = max_tokens

        logger.info("TogetherModel initialised: model=%s", model_name)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def generate(self, prompt: str, case_id: str) -> dict[str, Any]:
        """Send a single prompt and return a result dict matching GeminiModel schema."""
        timestamp = datetime.utcnow().isoformat()
        logger.info("Generating response for case_id=%s", case_id)

        response = self._client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

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
