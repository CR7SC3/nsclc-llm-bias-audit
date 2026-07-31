"""Anthropic model wrapper for EquityGUIDE.

Matches the GeminiModel interface exactly: generate() and generate_with_retry()
return the same dict schema so run_experiment.py works unchanged.

Authentication: set ANTHROPIC_API_KEY in .env

Supported models
----------------
    claude-sonnet-4-6      — DEFAULT. Production-grade, accepts temperature=0
                             (keeps the study's matched deterministic regime).
    claude-haiku-4-5-20251001 — fast and cheap; also accepts temperature.
    claude-opus-4-8 / -4-7 — most capable, BUT `temperature` is removed on these
                             (returns 400). The wrapper auto-omits temperature for
                             them, so they run under adaptive thinking rather than
                             temp=0 — a *different* generation regime. Use Sonnet 4.6
                             for the matched main comparison; Opus only as a
                             capability-ceiling robustness arm.
"""

from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import anthropic
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_RESULTS_RAW_DIR = Path(__file__).resolve().parents[2] / "results" / "raw"
_RESULTS_RAW_DIR.mkdir(parents=True, exist_ok=True)

# Models that REJECT the `temperature` parameter with a 400 (sampling params
# were removed on Opus 4.7+ and Fable 5). For these we must omit temperature.
# Everything else (Sonnet 4.6, Opus 4.6, Haiku 4.5, older) accepts temperature=0.
_NO_TEMPERATURE_PREFIXES = ("claude-opus-4-8", "claude-opus-4-7", "claude-fable-5", "claude-mythos-5", "claude-sonnet-5")


def _accepts_temperature(model_name: str) -> bool:
    return not any(model_name.startswith(p) for p in _NO_TEMPERATURE_PREFIXES)


class AnthropicModel:
    """Wrapper around Anthropic Messages API.

    Parameters
    ----------
    model_name:
        Anthropic model identifier, e.g. ``"claude-opus-4-8"``.
    temperature:
        Sampling temperature (0 = deterministic).
    inter_call_sleep:
        Seconds to sleep between calls to respect rate limits.
    max_retries:
        Maximum retry attempts in ``generate_with_retry``.
    retry_wait:
        Seconds to wait between retry attempts.
    max_tokens:
        Maximum completion tokens.
    """

    def __init__(
        self,
        model_name: str = "claude-sonnet-4-6",
        temperature: float = 0,
        inter_call_sleep: float = 2.0,
        max_retries: int = 3,
        retry_wait: float = 30.0,
        max_tokens: int = 2048,
    ) -> None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise EnvironmentError("ANTHROPIC_API_KEY not set in .env")

        # timeout bounds each request so a stuck connection fails fast and hits
        # our retry loop instead of hanging a worker (lesson from the OpenRouter
        # hang); max_retries=0 leaves backoff to generate_with_retry.
        self._client = anthropic.Anthropic(api_key=api_key, timeout=120.0, max_retries=0)
        self.model_name = model_name
        self.temperature = temperature
        self._send_temperature = _accepts_temperature(model_name)
        if not self._send_temperature:
            logger.warning(
                "Model %s does not accept temperature; running under adaptive "
                "thinking (NOT temperature=0). Use Sonnet 4.6 for matched temp=0.",
                model_name,
            )
        self.inter_call_sleep = inter_call_sleep
        self.max_retries = max_retries
        self.retry_wait = retry_wait
        self.max_tokens = max_tokens

        logger.info("AnthropicModel initialised: model=%s", model_name)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def generate(self, prompt: str, case_id: str) -> dict[str, Any]:
        """Send a single prompt and return a result dict matching GeminiModel schema."""
        timestamp = datetime.utcnow().isoformat()
        logger.info("Generating response for case_id=%s", case_id)

        kwargs: dict[str, Any] = {
            "model": self.model_name,
            "max_tokens": self.max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if self._send_temperature:
            kwargs["temperature"] = self.temperature
        response = self._client.messages.create(**kwargs)

        response_text = response.content[0].text if response.content else ""
        usage = response.usage

        result: dict[str, Any] = {
            "case_id": case_id,
            "model": self.model_name,
            "prompt": prompt,
            "response_text": response_text,
            "timestamp": timestamp,
            "prompt_tokens": usage.input_tokens if usage else None,
            "completion_tokens": usage.output_tokens if usage else None,
            "total_tokens": (
                (usage.input_tokens + usage.output_tokens)
                if usage else None
            ),
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
