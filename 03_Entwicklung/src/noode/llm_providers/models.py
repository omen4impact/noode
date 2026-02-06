"""LLM Models Configuration.

Users can define their own models or use the built-in defaults.
All models optimized for coding.
"""

from typing import Dict, List

# Built-in model definitions - users can override in config
DEFAULT_MODELS: Dict[str, List[Dict]] = {
    "openai": [
        {
            "id": "gpt-4-turbo-preview",
            "name": "GPT-4 Turbo",
            "description": "Latest GPT-4, excellent for coding",
            "context": 128000,
        },
        {
            "id": "gpt-4",
            "name": "GPT-4",
            "description": "Reliable coding model",
            "context": 8192,
        },
        {
            "id": "gpt-3.5-turbo",
            "name": "GPT-3.5 Turbo",
            "description": "Fast and cost-effective",
            "context": 16385,
        },
    ],
    "anthropic": [
        {
            "id": "claude-3-opus-20240229",
            "name": "Claude 3 Opus",
            "description": "Best for complex coding tasks",
            "context": 200000,
        },
        {
            "id": "claude-3-sonnet-20240229",
            "name": "Claude 3 Sonnet",
            "description": "Balanced performance",
            "context": 200000,
        },
        {
            "id": "claude-3-haiku-20240307",
            "name": "Claude 3 Haiku",
            "description": "Fast responses",
            "context": 200000,
        },
    ],
    "google": [
        {
            "id": "gemini-1.5-pro-latest",
            "name": "Gemini 1.5 Pro",
            "description": "Google's best coding model",
            "context": 1000000,
        },
        {
            "id": "gemini-1.5-flash-latest",
            "name": "Gemini 1.5 Flash",
            "description": "Fast and efficient",
            "context": 1000000,
        },
    ],
    "openrouter": [
        # Users can add ANY model from OpenRouter
        # These are just sensible defaults
        {
            "id": "openai/gpt-4-turbo-preview",
            "name": "OR: GPT-4 Turbo",
            "description": "Via OpenRouter",
            "context": 128000,
        },
        {
            "id": "anthropic/claude-3-opus",
            "name": "OR: Claude 3 Opus",
            "description": "Via OpenRouter",
            "context": 200000,
        },
        {
            "id": "moonshotai/kimi-k2.5",
            "name": "OR: Kimi K2.5",
            "description": "Moonshot AI - excellent for coding",
            "context": 256000,
        },
        {
            "id": "anthropic/claude-3.5-sonnet",
            "name": "OR: Claude 3.5 Sonnet",
            "description": "Via OpenRouter",
            "context": 200000,
        },
        {
            "id": "meta-llama/llama-3.1-405b-instruct",
            "name": "OR: Llama 3.1 405B",
            "description": "Open source giant",
            "context": 128000,
        },
        {
            "id": "google/gemini-1.5-pro",
            "name": "OR: Gemini 1.5 Pro",
            "description": "Via OpenRouter",
            "context": 1000000,
        },
    ],
}


def get_available_models(provider: str) -> List[Dict]:
    """Get list of available models for a provider."""
    return DEFAULT_MODELS.get(provider, [])


def get_default_model(provider: str) -> str:
    """Get default model for a provider."""
    models = get_available_models(provider)
    if models:
        return models[0]["id"]
    
    # Fallback defaults
    defaults = {
        "openai": "gpt-4-turbo-preview",
        "anthropic": "claude-3-opus-20240229",
        "google": "gemini-1.5-pro-latest",
        "openrouter": "openai/gpt-4-turbo-preview",
    }
    return defaults.get(provider, "")


def validate_model(provider: str, model: str) -> bool:
    """Check if a model is valid for a provider."""
    models = get_available_models(provider)
    return any(m["id"] == model for m in models)
