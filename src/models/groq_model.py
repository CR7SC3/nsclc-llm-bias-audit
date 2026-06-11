"""Groq model wrapper for EquityGUIDE.

Groq runs open-source models on custom LPU hardware — extremely fast inference,
generous free tier.  API is OpenAI-compatible.

Matches the GeminiModel interface exactly so run_experiment.py works unchanged.

Authentication: set GROQ_API_KEY in .env
Get a free key at: console.groq.com

Supported models
----------------
    llama-3.3-70b-versatile   — Llama 3.3 70B (recommended)
    llama-3.1-70b-versatile   — Llama 3.1 70B
    mixtral-8x7b-32768        — Mixtral 8x7B (32k context)

Free tier rate limits (as of 2025)
-----------------------------------
    llama-3.3-70b-versatile : 30 RPM, 6000 TPM, 14400 RPD
    With ~1700 tokens/call, expect ~3-4 calls/min → ~250 min for 990 calls.
    Set inter_call_sleep=20.0 to stay safely under token limits.
"""

from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_RESULTS_RAW_DIR = Path(__file__).resolve().parents[2] / "results" / "raw"
_RESULTS_RAW_DIR.mkdir(parents=True, exist_ok=True)


class GroqModel:
    """Wrapper around Groq's chat completions API.

    Parameters
    ----------
    model_name:
        Groq model identifier, e.g. ``"llama-3.3-70b-versatile"``.
    temperature:
        Sampling temperature (0 = deterministic).
    inter_call_sleep:
        Seconds to sleep between calls.  Set to ≥20s on the free tier to
        respect the ~6000 tokens-per-minute limit for large models.
    max_retries:
        Maximum retry attempts in ``generate_with_retry``.
    retry_wait:
        Seconds to wait after a rate-limit error before retrying.
    max_tokens:
        Maximum completion tokens per call.
    """

    def __init__(
        self,
        model_name: str = "llama-3.3-70b-versatile",
        temperature: float = 0,
        inter_call_sleep: float = 20.0,
        max_retries: int = 5,
        retry_wait: float = 60.0,
        max_tokens: int = 2048,
    ) -> None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError("GROQ_API_KEY not set in .env")

        self._client = Groq(api_key=api_key)
        self.model_name = model_name
        self.temperature = temperature
        self.inter_call_sleep = inter_call_sleep
        self.max_retries = max_retries
        self.retry_wait = retry_wait
        self.max_tokens = max_tokens

        logger.info("GroqModel initialised: model=%s", model_name)

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
