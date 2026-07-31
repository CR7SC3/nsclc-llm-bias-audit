"""Ollama (local inference) model wrapper for EquityGUIDE.

Runs an open-weight model entirely on the local machine via Ollama's
OpenAI-compatible endpoint (http://localhost:11434/v1). No data leaves the
host — this is the "on-prem / PHI-safe deployable" arm of the study.

Run-level model IDs are prefixed with ``ollama/`` so the factory routes here
and the checkpoint filename stays distinct, e.g.::

    ollama/med42-8b   -> served by Ollama as  med42-8b

Prereqs
-------
    1. Install Ollama:  brew install ollama   (or https://ollama.com/download)
    2. Start the server: ollama serve   (runs on :11434)
    3. Pull the model:   ollama pull <tag>   (or create from a GGUF Modelfile)

Matches the GeminiModel interface (generate / generate_with_retry) so
run_experiment_v2.py works unchanged.

Notes
-----
    * No API key needed; Ollama's OpenAI-compat endpoint ignores the key.
    * 24 GB RAM comfortably runs 8B (and ~14B q4); 70B will NOT fit locally.
    * Small models follow structured prompts less reliably than API models —
      always pilot on pilot50 and check the parse-failure rate before a full run.
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

# Ollama exposes an OpenAI-compatible API here by default. Override with
# OLLAMA_BASE_URL if the server runs elsewhere.
_OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
_RESULTS_RAW_DIR = Path(__file__).resolve().parents[2] / "results" / "raw"
_RESULTS_RAW_DIR.mkdir(parents=True, exist_ok=True)


class OllamaModel:
    """Wrapper around a locally-served Ollama model via its OpenAI-compatible API.

    Parameters
    ----------
    model_name:
        Run-level model ID, optionally prefixed with ``ollama/`` (stripped before
        the request). E.g. ``"ollama/med42-8b"``.
    temperature:
        Sampling temperature (0 = deterministic).
    inter_call_sleep:
        Seconds to sleep between calls (local: keep small).
    max_retries / retry_wait:
        Retry policy in ``generate_with_retry``.
    max_tokens:
        Maximum completion tokens.
    """

    def __init__(
        self,
        model_name: str = "ollama/med42-8b",
        temperature: float = 0,
        inter_call_sleep: float = 0.0,
        max_retries: int = 3,
        retry_wait: float = 10.0,
        max_tokens: int = 2048,
    ) -> None:
        # Ollama ignores the API key but the OpenAI client requires a non-empty one.
        self._client = OpenAI(
            api_key="ollama",
            base_url=_OLLAMA_BASE_URL,
            timeout=300.0,   # local generation can be slow on CPU/Metal
            max_retries=0,
        )
        self.model_name = model_name
        self._api_model = model_name.split("/", 1)[1] if model_name.startswith("ollama/") else model_name
        self.temperature = temperature
        self.inter_call_sleep = inter_call_sleep
        self.max_retries = max_retries
        self.retry_wait = retry_wait
        self.max_tokens = max_tokens

        logger.info(
            "OllamaModel initialised: model=%s (ollama tag=%s) base=%s",
            model_name, self._api_model, _OLLAMA_BASE_URL,
        )

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def generate(self, prompt: str, case_id: str) -> dict[str, Any]:
        """Send a single prompt and return a result dict matching GeminiModel schema."""
        timestamp = datetime.utcnow().isoformat()
        logger.info("Generating response for case_id=%s", case_id)

        response = self._client.chat.completions.create(
            model=self._api_model,
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
            "prompt_tokens": getattr(usage, "prompt_tokens", None) if usage else None,
            "completion_tokens": getattr(usage, "completion_tokens", None) if usage else None,
            "total_tokens": getattr(usage, "total_tokens", None) if usage else None,
        }

        self._save_result(result, case_id, timestamp)
        if self.inter_call_sleep:
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
