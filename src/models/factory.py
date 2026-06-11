"""Model factory for EquityGUIDE.

Returns a model instance from a string identifier.  All returned objects share
the GeminiModel interface: generate(prompt, case_id) and generate_with_retry().

Usage
-----
    from src.models.factory import create_model

    model = create_model("gpt-4o")
    model = create_model("claude-opus-4-8")
    model = create_model("gemini-2.5-flash")
"""

from __future__ import annotations

_GEMINI_PREFIXES    = ("gemini",)
_OPENAI_PREFIXES    = ("gpt-", "o1", "o3", "o4")
_ANTHROPIC_PREFIXES = ("claude",)
_GROQ_PREFIXES      = ("llama", "mixtral", "gemma")
_TOGETHER_PREFIXES  = ("meta-llama/", "mistralai/", "togethercomputer/", "qwen/", "google/")


def create_model(model_name: str, **kwargs):
    """Instantiate the correct model wrapper for *model_name*.

    Parameters
    ----------
    model_name:
        Any of the supported model identifiers:
        - Gemini:    ``"gemini-2.5-flash"``, ``"gemini-2.0-flash"``
        - OpenAI:    ``"gpt-4o"``, ``"gpt-4o-mini"``, ``"o1"``, ``"o3"``, ``"o4-mini"``
        - Anthropic: ``"claude-opus-4-8"``, ``"claude-sonnet-4-6"``, ``"claude-haiku-4-5-20251001"``
    **kwargs:
        Forwarded to the model constructor (temperature, inter_call_sleep, etc.).
    """
    name_lower = model_name.lower()

    if any(name_lower.startswith(p) for p in _GEMINI_PREFIXES):
        from src.models.gemini_model import GeminiModel
        return GeminiModel(model_name=model_name, **kwargs)

    if any(name_lower.startswith(p) for p in _OPENAI_PREFIXES):
        from src.models.openai_model import OpenAIModel
        return OpenAIModel(model_name=model_name, **kwargs)

    if any(name_lower.startswith(p) for p in _ANTHROPIC_PREFIXES):
        from src.models.anthropic_model import AnthropicModel
        return AnthropicModel(model_name=model_name, **kwargs)

    if any(name_lower.startswith(p) for p in _TOGETHER_PREFIXES):
        from src.models.together_model import TogetherModel
        return TogetherModel(model_name=model_name, **kwargs)

    if any(name_lower.startswith(p) for p in _GROQ_PREFIXES):
        from src.models.groq_model import GroqModel
        return GroqModel(model_name=model_name, **kwargs)

    raise ValueError(
        f"Unknown model '{model_name}'. Expected a name starting with one of: "
        f"gemini, gpt-, o1, o3, o4, claude, meta-llama/, mistralai/, llama, mixtral, gemma."
    )


# Convenience registry for --model CLI choices
SUPPORTED_MODELS = [
    # Gemini
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
    # OpenAI
    "gpt-4o",
    "gpt-4o-mini",
    "o1",
    "o3",
    "o4-mini",
    # Anthropic
    "claude-opus-4-8",
    "claude-sonnet-4-6",
    "claude-haiku-4-5-20251001",
    # Groq (free tier)
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "mixtral-8x7b-32768",
    # Together.ai (open-source, ~$1.50/run)
    "meta-llama/Llama-3.3-70B-Instruct-Turbo",
    "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
    "mistralai/Mixtral-8x7B-Instruct-v0.1",
    "mistralai/Mixtral-8x22B-Instruct-v0.1",
]
