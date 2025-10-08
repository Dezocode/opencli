"""
Provider configuration defaults for OpenCLI.

Centralizes per-provider settings including base URLs, required headers,
and the request format used when building API payloads.
"""

import os
from copy import deepcopy
from typing import Dict, Any

# Allow users to override OpenRouter header metadata via environment variables.
_OPENROUTER_SITE = os.getenv("OPENROUTER_SITE_URL") or "https://github.com/Dezocode/opencli"
_OPENROUTER_APP = os.getenv("OPENROUTER_APP_NAME") or "OpenCLI"

# NOTE: Keep names aligned with ModelManager.DEFAULT_PROVIDERS
PROVIDER_DEFAULTS: Dict[str, Dict[str, Any]] = {
    "openrouter": {
        "name": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "models_endpoint": "https://openrouter.ai/api/v1/models",
        "key_patterns": ["sk-or-", "OPENROUTER"],
        "request_format": "openai-chat",
        "default_headers": {
            "HTTP-Referer": _OPENROUTER_SITE,
            "X-Title": _OPENROUTER_APP
        }
    },
    "anthropic": {
        "name": "Anthropic",
        "base_url": "https://api.anthropic.com/v1",
        "models_endpoint": None,
        "key_patterns": ["sk-ant-"],
        "request_format": "anthropic-messages",
        "default_headers": {
            "anthropic-version": "2023-06-01"
        }
    },
    "openai": {
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "models_endpoint": "https://api.openai.com/v1/models",
        "key_patterns": ["sk-proj-", "sk-"],
        "request_format": "openai-chat",
        "default_headers": {}
    },
    "deepseek": {
        "name": "DeepSeek",
        "base_url": "https://api.deepseek.com/v1",
        "models_endpoint": "https://api.deepseek.com/v1/models",
        "key_patterns": ["sk-"],
        "request_format": "openai-chat",
        "default_headers": {}
    },
    "google": {
        "name": "Google AI",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "models_endpoint": None,
        "key_patterns": ["AIza"],
        "request_format": "openai-chat",
        "default_headers": {}
    }
}


def ensure_provider_defaults(existing: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Merge persisted provider metadata with current defaults.

    Ensures new fields (e.g., request_format, default_headers) are present
    without overwriting user-specific overrides.
    """
    merged: Dict[str, Dict[str, Any]] = {}

    # Start with known providers so new installs get full defaults
    for provider_id, defaults in PROVIDER_DEFAULTS.items():
        current = deepcopy(defaults)
        stored = existing.get(provider_id, {})
        for key, value in stored.items():
            current[key] = value
        merged[provider_id] = current

    # Preserve any unknown/custom providers the user may have added
    for provider_id, info in existing.items():
        if provider_id not in merged:
            merged[provider_id] = deepcopy(info)

    return merged


def get_provider_defaults(provider_id: str) -> Dict[str, Any]:
    """Return a deep copy of the default settings for the provider."""
    defaults = PROVIDER_DEFAULTS.get(provider_id, {})
    return deepcopy(defaults)
