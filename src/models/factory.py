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
_DEEPSEEK_PREFIXES  = ("deepseek",)
_OPENROUTER_PREFIXES = ("openrouter/",)
_OLLAMA_PREFIXES     = ("ollama/",)

# Exact model IDs that must route to Groq even though their prefix (qwen/,
# openai/, meta-llama/) would otherwise match OpenAI or Together. These are the
# free-tier open-weight models served on Groq's LPU hardware. Checked before
# prefix routing so the same family name resolves to the free Groq endpoint.
_GROQ_MODELS = frozenset({
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "qwen/qwen3-32b",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "meta-llama/llama-4-scout-17b-16e-instruct",
})


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

    # Exact-match Groq IDs first — disambiguates slash-prefixed names (qwen/,
    # openai/, meta-llama/) that would otherwise route to Together or OpenAI.
    if model_name in _GROQ_MODELS:
        from src.models.groq_model import GroqModel
        return GroqModel(model_name=model_name, **kwargs)

    # OpenRouter (prefixed ``openrouter/...``) — checked before Together's
    # ``meta-llama/`` prefix so the pinned-provider OpenRouter route wins.
    if any(name_lower.startswith(p) for p in _OPENROUTER_PREFIXES):
        from src.models.openrouter_model import OpenRouterModel
        return OpenRouterModel(model_name=model_name, **kwargs)

    # Ollama (prefixed ``ollama/...``) — local inference, on-prem arm.
    if any(name_lower.startswith(p) for p in _OLLAMA_PREFIXES):
        from src.models.ollama_model import OllamaModel
        return OllamaModel(model_name=model_name, **kwargs)

    if any(name_lower.startswith(p) for p in _GEMINI_PREFIXES):
        from src.models.gemini_model import GeminiModel
        return GeminiModel(model_name=model_name, **kwargs)

    if any(name_lower.startswith(p) for p in _OPENAI_PREFIXES):
        from src.models.openai_model import OpenAIModel
        return OpenAIModel(model_name=model_name, **kwargs)

    if any(name_lower.startswith(p) for p in _ANTHROPIC_PREFIXES):
        from src.models.anthropic_model import AnthropicModel
        return AnthropicModel(model_name=model_name, **kwargs)

    if any(name_lower.startswith(p) for p in _DEEPSEEK_PREFIXES):
        from src.models.deepseek_model import DeepSeekModel
        return DeepSeekModel(model_name=model_name, **kwargs)

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
    "claude-sonnet-5",
    "claude-sonnet-4-6",
    "claude-haiku-4-5-20251001",
    # Groq (free tier, open-weight) — verified live 2026-06
    "llama-3.3-70b-versatile",                    # Llama 3.3 70B
    "meta-llama/llama-4-scout-17b-16e-instruct",  # Llama 4 Scout 17B
    "qwen/qwen3-32b",                             # Qwen3 32B (emits <think> blocks)
    "openai/gpt-oss-120b",                        # GPT-OSS 120B
    "openai/gpt-oss-20b",                         # GPT-OSS 20B
    "llama-3.1-8b-instant",                       # Llama 3.1 8B
    # Together.ai (open-source, ~$1.50/run)
    "meta-llama/Llama-3.3-70B-Instruct-Turbo",
    "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
    "mistralai/Mixtral-8x7B-Instruct-v0.1",
    "mistralai/Mixtral-8x22B-Instruct-v0.1",
    "Qwen/Qwen3-235B-A22B-Instruct-2507-tput",    # Qwen3 235B MoE (non-thinking Instruct)
    # DeepSeek (~$5/full run)
    "deepseek-chat",      # DeepSeek V3
    "deepseek-reasoner",  # DeepSeek R1
    # OpenRouter (pinned to one provider; ~$8/full run) — prefixed to stay
    # distinct from the Together meta-llama/ route and checkpoint.
    "openrouter/meta-llama/llama-3.3-70b-instruct",
    "openrouter/meta-llama/llama-3.1-8b-instruct",   # Llama 3.1 8B (cheapest 8B arm)
    # Ollama (local, on-prem arm) — prefixed; served from localhost:11434.
    "ollama/med42-8b",
    "ollama/meditron",   # medical pilot (official Ollama lib; base 7B, weak instr)
]
