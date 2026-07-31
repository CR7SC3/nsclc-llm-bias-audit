"""OpenRouter model wrapper for EquityGUIDE.

OpenRouter is an OpenAI-compatible aggregator that routes to underlying
inference providers (DeepInfra, Novita, Nebius, ...). For research
reproducibility we PIN a single provider so the whole arm runs on one
serving stack / quantization rather than OpenRouter's default cheapest-route
behaviour (which can switch providers, and therefore quantization, between
requests).

Authentication: set OPEN_ROUTER_KEY in .env
Get a key at: openrouter.ai/keys

Model IDs are passed with an ``openrouter/`` prefix in run_experiment so the
factory routes here and the checkpoint filename stays distinct from the
Together arm. The prefix is stripped before the request is sent, e.g.::

    openrouter/meta-llama/llama-3.3-70b-instruct
        -> sent to OpenRouter as meta-llama/llama-3.3-70b-instruct

Matches the GeminiModel interface exactly so run_experiment_v2.py works
unchanged.

Cost (full 1,048 x 30 run, ~22M in + 18M out, DeepInfra Llama-3.3-70B)
---------------------------------------------------------------------
    ~$8 total (vs ~$36 on Together Turbo)
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

_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
_RESULTS_RAW_DIR = Path(__file__).resolve().parents[2] / "results" / "raw"
_RESULTS_RAW_DIR.mkdir(parents=True, exist_ok=True)

# Pin to one provider for a consistent single serving-stack across the whole
# arm. allow_fallbacks=False guarantees every call is served by DeepInfra
# (no silent provider/quantization switching mid-run).
_PINNED_PROVIDER = "DeepInfra"


class OpenRouterModel:
    """Wrapper around OpenRouter using the OpenAI-compatible API, pinned to one provider.

    Parameters
    ----------
    model_name:
        Run-level model ID, optionally prefixed with ``openrouter/`` (the prefix
        is stripped before the request). E.g.
        ``"openrouter/meta-llama/llama-3.3-70b-instruct"``.
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
    provider:
        Underlying OpenRouter provider to pin to (default ``"DeepInfra"``).
    """

    def __init__(
        self,
        model_name: str = "openrouter/meta-llama/llama-3.3-70b-instruct",
        temperature: float = 0,
        inter_call_sleep: float = 1.0,
        max_retries: int = 3,
        retry_wait: float = 30.0,
        max_tokens: int = 2048,
        provider: str = _PINNED_PROVIDER,
    ) -> None:
        api_key = os.getenv("OPEN_ROUTER_KEY")
        if not api_key:
            raise EnvironmentError("OPEN_ROUTER_KEY not set in .env")

        # timeout bounds each request so a stuck upstream connection fails fast
        # and hits generate_with_retry instead of hanging a worker for ~10 min
        # (the SDK default). max_retries=0: our own retry loop handles backoff.
        self._client = OpenAI(
            api_key=api_key,
            base_url=_OPENROUTER_BASE_URL,
            timeout=90.0,
            max_retries=0,
        )
        # The full prefixed name is kept for logging/checkpoint provenance;
        # the API model id has the ``openrouter/`` prefix stripped.
        self.model_name = model_name
        self._api_model = model_name.split("/", 1)[1] if model_name.startswith("openrouter/") else model_name
        self.temperature = temperature
        self.inter_call_sleep = inter_call_sleep
        self.max_retries = max_retries
        self.retry_wait = retry_wait
        self.max_tokens = max_tokens
        self.provider = provider

        logger.info(
            "OpenRouterModel initialised: model=%s (api=%s) pinned-provider=%s",
            model_name, self._api_model, provider,
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
            extra_body={
                "provider": {
                    # Prefer DeepInfra (FP8) but allow fallback to other
                    # providers — strict single-provider pinning hits OpenRouter's
                    # shared-pool 429 rate limits for this popular model and
                    # stalls the run. Mixed-FP8 serving is a documentable caveat.
                    "order": [self.provider, "Novita", "Nebius", "Lambda"],
                    "allow_fallbacks": True,
                }
            },
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
