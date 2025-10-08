"""
Model Manager for OpenCLI
Auto-discovers models from API keys, no hardcoded model lists
"""

import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Dict, List, Optional

import httpx

try:
    from .provider_settings import (
        ensure_provider_defaults,
        get_provider_defaults,
        PROVIDER_DEFAULTS,
    )
except ImportError:
    from provider_settings import (
        ensure_provider_defaults,
        get_provider_defaults,
        PROVIDER_DEFAULTS,
    )


class ModelManager:
    """Manage models dynamically based on configured API keys"""

    def __init__(self, config_dir: Path = None):
        self.config_dir = config_dir or Path.home() / ".opencli"
        self.models_file = self.config_dir / "models.json"
        self.config_file = self.config_dir / "config.json"
        self.secrets_file = self.config_dir / ".secrets"

        # Load configurations
        self.models_db = self._load_models()
        self.config = self._load_config()
        self.config.setdefault("providerOverrides", {})

        # Load API key for the current provider
        provider = self.config.get("provider")
        if provider:
            # Get API key from models.json for this provider
            api_keys = self.models_db.get("api_keys", {})
            if provider in api_keys and api_keys[provider]:
                self.config["apiKey"] = api_keys[provider]

            headers = self.get_provider_headers(provider, self.config.get("model"))
            if headers:
                self.config["defaultHeaders"] = headers
            elif "defaultHeaders" in self.config:
                del self.config["defaultHeaders"]

    def _load_models(self) -> Dict:
        """Load models database"""
        if self.models_file.exists():
            with open(self.models_file) as f:
                data = json.load(f)
        else:
            data = {
                "api_keys": {},
                "models": {},
                "usage_history": [],  # Track recently used models
                "providers": deepcopy(PROVIDER_DEFAULTS),
            }

        data["providers"] = ensure_provider_defaults(data.get("providers", {}))
        return data

    def _load_config(self) -> Dict:
        """Load main config"""
        config = {}

        if self.config_file.exists():
            with open(self.config_file) as f:
                try:
                    config = json.load(f)
                except json.JSONDecodeError:
                    config = {}

        provider = config.get("provider")
        if not provider:
            model_id = config.get("model")
            provider = self.get_provider_for_model(model_id) if model_id else None

        if not provider:
            base_url = config.get("baseURL")
            for provider_id, settings in self.models_db.get("providers", {}).items():
                if base_url and settings.get("base_url") == base_url:
                    provider = provider_id
                    break

        if not provider:
            provider = "openrouter"

        config["provider"] = provider
        config.setdefault("providerOverrides", {})

        provider_settings = self.get_provider_settings(provider)
        if provider_settings.get("request_format") and "requestFormat" not in config:
            config["requestFormat"] = provider_settings["request_format"]

        return config

    def _save_models(self):
        """Save models database"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.models_file, 'w') as f:
            json.dump(self.models_db, f, indent=2)
        # Set restrictive permissions (0o600) since it contains API keys
        import os
        os.chmod(self.models_file, 0o600)

    def _save_config(self):
        """Save main config"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
        # Set restrictive permissions since config contains API keys
        import os
        os.chmod(self.config_file, 0o600)

    def _set_active_provider(self, provider: str, api_key: Optional[str] = None):
        """
        Update config to reflect active provider selection.

        Args:
            provider: Provider identifier (e.g., 'openrouter')
            api_key: Optional API key to persist alongside the provider switch
        """
        settings = self.get_provider_settings(provider)
        if not settings:
            return

        self.config["provider"] = provider
        if api_key:
            self.config["apiKey"] = api_key

        base_url = settings.get("base_url")
        if base_url:
            self.config["baseURL"] = base_url

        request_format = settings.get("request_format")
        if request_format:
            self.config["requestFormat"] = request_format

        headers = self.get_provider_headers(provider, self.config.get("model"))
        if headers:
            self.config["defaultHeaders"] = headers
        elif "defaultHeaders" in self.config:
            del self.config["defaultHeaders"]

        self._save_config()

    def get_provider_settings(self, provider: str) -> Dict:
        """Return provider metadata with defaults applied."""
        providers = self.models_db.get("providers", {})
        if provider in providers:
            return deepcopy(providers[provider])
        return get_provider_defaults(provider)

    def get_provider_for_model(self, model_id: str) -> Optional[str]:
        """
        Identify the provider associated with a given model.

        Args:
            model_id: Model identifier (e.g., 'anthropic/claude-3-5-sonnet')

        Returns:
            Provider ID or None if not determined
        """
        if not model_id:
            return None

        models = self.models_db.get("models", {})
        if model_id in models:
            provider = models[model_id].get("provider")
            if provider:
                return provider

        if "/" in model_id:
            prefix = model_id.split("/", 1)[0]
            if prefix in self.models_db.get("providers", {}):
                return prefix

        return self.config.get("provider")

    def get_provider_headers(self, provider: str, model_id: Optional[str] = None) -> Dict:
        """
        Build effective headers for provider/model combination.

        For OpenRouter models, fetches per-model headers from API pages.
        For other providers, uses default headers + overrides.
        """
        # OpenRouter: Fetch per-model headers from API pages
        if provider == "openrouter" and model_id:
            try:
                # Import here to avoid circular dependency
                try:
                    from .openrouter_headers import OpenRouterHeaderManager
                except ImportError:
                    from openrouter_headers import OpenRouterHeaderManager

                header_mgr = OpenRouterHeaderManager()
                headers = header_mgr.get_headers_for_model(model_id)

                # Apply any user overrides on top of fetched headers
                overrides = self.config.get("providerOverrides", {})
                provider_overrides = overrides.get(provider, {})

                # Provider-level overrides
                base_override = provider_overrides.get("headers") or {}
                if isinstance(base_override, dict):
                    headers.update(base_override)

                # Model-specific overrides
                model_overrides = provider_overrides.get("models") or {}
                specific = model_overrides.get(model_id)
                if isinstance(specific, dict):
                    headers.update(specific)

                return headers

            except Exception as e:
                # Fall back to default behavior on any error
                pass

        # Default behavior for non-OpenRouter providers or fallback
        settings = self.get_provider_settings(provider)
        headers = deepcopy(settings.get("default_headers") or {})

        # Apply overrides from config.json:providerOverrides
        overrides = self.config.get("providerOverrides", {})
        provider_overrides = overrides.get(provider, {}) if isinstance(overrides, dict) else {}

        base_override = provider_overrides.get("headers") or {}
        if isinstance(base_override, dict):
            headers.update(base_override)

        # Model-specific overrides
        if model_id:
            model_overrides = provider_overrides.get("models") or {}
            if isinstance(model_overrides, dict):
                specific = model_overrides.get(model_id)
                if isinstance(specific, dict):
                    headers.update(specific)

        # Environment variable overrides for OpenRouter (fallback only)
        if provider == "openrouter":
            site_url = os.getenv("OPENROUTER_SITE_URL")
            app_name = os.getenv("OPENROUTER_APP_NAME")
            if site_url:
                headers["HTTP-Referer"] = site_url
            if app_name:
                headers["X-Title"] = app_name

        return headers

    def update_provider_headers(self, provider: str, new_headers: Dict[str, str], model_id: Optional[str] = None):
        """Persist custom headers for a provider (optionally scoped to a model)."""
        overrides = self.config.setdefault("providerOverrides", {})
        provider_overrides = overrides.setdefault(provider, {})

        # Normalize header keys to strings
        cleaned_headers = {str(k): v for k, v in (new_headers or {}).items() if v}

        if model_id:
            models_map = provider_overrides.setdefault("models", {})
            if cleaned_headers:
                models_map[model_id] = cleaned_headers
            elif model_id in models_map:
                del models_map[model_id]
        else:
            if cleaned_headers:
                provider_overrides["headers"] = cleaned_headers
            elif "headers" in provider_overrides:
                del provider_overrides["headers"]

        # Update effective headers in config
        headers = self.get_provider_headers(provider, self.config.get("model"))
        if headers:
            self.config["defaultHeaders"] = headers
        elif "defaultHeaders" in self.config:
            del self.config["defaultHeaders"]

        self._save_config()

    def get_configured_keys(self) -> Dict[str, str]:
        """Get all configured API keys"""
        keys = {}

        # Check models.json (primary storage)
        for provider, key in self.models_db.get("api_keys", {}).items():
            if key:
                keys[provider] = key

        # Check main config for legacy openrouter key
        if "apiKey" in self.config and "openrouter" not in keys:
            keys["openrouter"] = self.config["apiKey"]

        # Check .secrets file for all providers
        if self.secrets_file.exists():
            try:
                with open(self.secrets_file) as f:
                    secrets = json.load(f)

                    # Legacy OpenRouter format
                    if "apiKey" in secrets and "openrouter" not in keys:
                        keys["openrouter"] = secrets["apiKey"]

                    # New multi-provider format
                    if "providers" in secrets:
                        for provider, key in secrets["providers"].items():
                            if key and provider not in keys:
                                keys[provider] = key
            except:
                pass

        return keys

    async def fetch_models_from_openrouter(self, api_key: str) -> Dict:
        """
        Fetch available models from OpenRouter API

        Args:
            api_key: OpenRouter API key

        Returns:
            Result dict with models list
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://openrouter.ai/api/v1/models",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "HTTP-Referer": "https://github.com/Dezocode/opencli",
                        "X-Title": "OpenCLI"
                    },
                    timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()
                    models = []

                    for model in data.get("data", []):
                        models.append({
                            "id": model.get("id"),
                            "name": model.get("name", model.get("id")),
                            "context": model.get("context_length", 0),
                            "pricing": model.get("pricing", {}),
                            "architecture": model.get("architecture", {})
                        })

                    return {
                        "success": True,
                        "models": models,
                        "count": len(models)
                    }
                else:
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code}"
                    }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def register_models(self, provider: str, models: List[Dict]):
        """
        Register models from API response

        Args:
            provider: Provider ID (e.g., 'openrouter')
            models: List of model dicts from API (already sorted by popularity)
        """
        for idx, model in enumerate(models):
            model_id = model["id"]
            self.models_db["models"][model_id] = {
                "provider": provider,
                "name": model.get("name", model_id),
                "context": model.get("context", 0),
                "pricing": model.get("pricing"),
                "architecture": model.get("architecture"),
                "privacy": model.get("privacy"),
                "tags": model.get("tags"),
                "popularity_rank": idx  # Preserve OpenRouter's ranking
            }

        self._save_models()

    def add_api_key(self, provider: str, api_key: str):
        """
        Add API key for provider

        Args:
            provider: Provider ID
            api_key: API key string
        """
        # Save to models.json (primary storage)
        self.models_db["api_keys"][provider] = api_key
        self._save_models()

        # Also save to .secrets for compatibility
        self._save_to_secrets(provider, api_key)

        # Update main config for active provider
        if provider == "openrouter":
            self._set_active_provider(provider, api_key)

    def _save_to_secrets(self, provider: str, api_key: str):
        """Save API key to .secrets file for compatibility"""
        secrets = {}

        # Load existing secrets
        if self.secrets_file.exists():
            try:
                with open(self.secrets_file) as f:
                    secrets = json.load(f)
            except:
                secrets = {}

        # Add provider key
        if provider == "openrouter":
            # Legacy format for OpenRouter
            secrets["apiKey"] = api_key

        # Store all provider keys
        if "providers" not in secrets:
            secrets["providers"] = {}
        secrets["providers"][provider] = api_key

        # Save with restrictive permissions
        with open(self.secrets_file, 'w') as f:
            json.dump(secrets, f, indent=2)

        import os
        os.chmod(self.secrets_file, 0o600)

    def list_available_models(self) -> List[Dict]:
        """
        List only models for which we have API keys

        Returns:
            List of available model dicts
        """
        configured_keys = self.get_configured_keys()
        available = []

        for model_id, model_info in self.models_db.get("models", {}).items():
            provider = model_info.get("provider")
            if provider in configured_keys:
                # We have a key for this provider
                available.append({
                    "id": model_id,
                    "name": model_info.get("name", model_id),
                    "provider": provider,
                    "context": model_info.get("context", 0),
                    "pricing": model_info.get("pricing", {})
                })

        # Sort: FREE models first, then by OpenRouter popularity rank
        def sort_key(m):
            pricing = m.get("pricing", {})
            is_free = (
                pricing.get("prompt") == "0" or
                pricing.get("completion") == "0" or
                ":free" in m["id"]
            )
            # Get popularity rank from models_db
            model_info = self.models_db.get("models", {}).get(m["id"], {})
            popularity_rank = model_info.get("popularity_rank", 999999)

            # Sort: free first (0), then paid (1), then by popularity
            return (not is_free, popularity_rank)

        return sorted(available, key=sort_key)

    def get_current_model(self, session) -> str:
        """Get current model from session or config"""
        if hasattr(session, 'model') and session.model:
            return session.model
        return self.config.get("model", "")

    def switch_model(self, session, model_id: str) -> Dict:
        """
        Switch to a different model

        Args:
            session: Session object
            model_id: Model identifier

        Returns:
            Result dict
        """
        if model_id not in self.models_db.get("models", {}):
            return {
                "success": False,
                "error": f"Model not found: {model_id}"
            }

        model_info = self.models_db["models"][model_id]
        provider = model_info.get("provider")

        # Check if we have API key
        keys = self.get_configured_keys()
        if provider not in keys:
            return {
                "success": False,
                "error": f"No API key for provider: {provider}"
            }

        # Update session
        session.model = model_id

        # Update config
        self.config["model"] = model_id
        self._set_active_provider(provider, keys[provider])

        # Track usage history (keep last 10)
        usage_history = self.models_db.get("usage_history", [])
        # Remove if already in history
        usage_history = [m for m in usage_history if m != model_id]
        # Add to front
        usage_history.insert(0, model_id)
        # Keep only last 10
        self.models_db["usage_history"] = usage_history[:10]
        self._save_models()

        return {
            "success": True,
            "model": model_info.get("name", model_id),
            "provider": provider,
            "pricing": model_info.get("pricing", {}),
            "context": model_info.get("context", 0)
        }

    def get_recent_models(self) -> List[Dict]:
        """Get recently used models with full info"""
        usage_history = self.models_db.get("usage_history", [])
        recent = []

        for model_id in usage_history:
            if model_id in self.models_db.get("models", {}):
                model_info = self.models_db["models"][model_id]
                recent.append({
                    "id": model_id,
                    "name": model_info.get("name", model_id),
                    "provider": model_info.get("provider"),
                    "context": model_info.get("context", 0),
                    "pricing": model_info.get("pricing", {})
                })

        return recent

    def get_providers(self) -> List[Dict]:
        """List configured providers"""
        keys = self.get_configured_keys()
        providers = []

        for provider_id, provider_info in self.models_db.get("providers", {}).items():
            has_key = provider_id in keys
            model_count = sum(
                1 for m in self.models_db.get("models", {}).values()
                if m.get("provider") == provider_id
            )

            providers.append({
                "id": provider_id,
                "name": provider_info.get("name", provider_id),
                "has_key": has_key,
                "model_count": model_count
            })

        return providers

    def detect_provider(self, api_key: str) -> Optional[str]:
        """
        Auto-detect provider from API key format

        Args:
            api_key: API key string to analyze

        Returns:
            Provider ID or None if not detected
        """
        # Check for local providers first (case-insensitive)
        api_key_lower = api_key.lower()
        if api_key_lower in ["ollama", "local"]:
            return "ollama"

        for provider_id, provider_info in self.models_db.get("providers", {}).items():
            patterns = provider_info.get("key_patterns", [])
            for pattern in patterns:
                if api_key.startswith(pattern):
                    return provider_id

        # Fallback detection by key structure
        if api_key.startswith("sk-or-"):
            return "openrouter"
        elif api_key.startswith("sk-ant-"):
            return "anthropic"
        elif api_key.startswith("sk-proj-"):
            return "openai"
        elif api_key.startswith("AIza"):
            return "google"

        return None

    async def fetch_models_from_provider(self, provider: str, api_key: str) -> Dict:
        """
        Fetch models from any supported provider

        Args:
            provider: Provider ID
            api_key: API key for the provider

        Returns:
            Result dict with models list
        """
        provider_info = self.models_db.get("providers", {}).get(provider)
        if not provider_info:
            return {"success": False, "error": f"Unknown provider: {provider}"}

        # OpenRouter uses existing method
        if provider == "openrouter":
            return await self.fetch_models_from_openrouter(api_key)

        # OpenAI compatible providers
        if provider in ["openai", "deepseek"]:
            return await self._fetch_openai_compatible(provider, provider_info, api_key)

        # Anthropic - predefined models
        if provider == "anthropic":
            return self._get_anthropic_models()

        # Google AI - predefined models
        if provider == "google":
            return self._get_google_models()

        return {"success": False, "error": f"Provider not yet supported: {provider}"}

    async def _fetch_openai_compatible(self, provider: str, provider_info: Dict, api_key: str) -> Dict:
        """Fetch models from OpenAI-compatible API"""
        try:
            # Handle Ollama separately - different API format
            if provider == "ollama":
                return await self._fetch_ollama_models(provider_info)

            endpoint = provider_info.get("models_endpoint")
            if not endpoint:
                return {"success": False, "error": "No models endpoint configured"}

            # Check if API key is required
            requires_key = provider_info.get("requires_key", True)
            headers = {}
            if requires_key and api_key:
                headers["Authorization"] = f"Bearer {api_key}"

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    endpoint,
                    headers=headers,
                    timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()
                    models = []

                    for model in data.get("data", []):
                        models.append({
                            "id": model.get("id"),
                            "name": model.get("id"),  # Most don't have friendly names
                            "context": model.get("context_length", 8192),
                            "pricing": {},  # Usually not in API response
                            "architecture": {}
                        })

                    return {"success": True, "models": models, "count": len(models)}
                else:
                    return {"success": False, "error": f"API error: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _fetch_ollama_models(self, provider_info: Dict) -> Dict:
        """Fetch models from Ollama server using /api/tags endpoint"""
        try:
            endpoint = provider_info.get("models_endpoint")
            if not endpoint:
                return {"success": False, "error": "No models endpoint configured"}

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    endpoint,
                    timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()
                    models = []

                    # Ollama returns {"models": [{"name": "llama2", "modified_at": "...", "size": ...}]}
                    for model in data.get("models", []):
                        model_name = model.get("name", "")
                        # Parse size (bytes) to GB for display
                        size_bytes = model.get("size", 0)
                        size_gb = round(size_bytes / (1024**3), 2) if size_bytes else 0

                        models.append({
                            "id": model_name,
                            "name": model_name,
                            "context": 4096,  # Default, Ollama doesn't expose this
                            "pricing": {"prompt": "0", "completion": "0"},  # Local = free
                            "architecture": {
                                "size_gb": size_gb,
                                "modified_at": model.get("modified_at", "")
                            }
                        })

                    return {"success": True, "models": models, "count": len(models)}
                elif response.status_code == 404:
                    return {"success": False, "error": "Ollama server not found. Is Ollama running? (ollama serve)"}
                else:
                    return {"success": False, "error": f"Ollama API error: {response.status_code}"}
        except httpx.ConnectError:
            return {"success": False, "error": "Cannot connect to Ollama. Is the server running? (ollama serve)"}
        except Exception as e:
            return {"success": False, "error": f"Ollama error: {str(e)}"}

    def _get_anthropic_models(self) -> Dict:
        """Get predefined Anthropic models"""
        models = [
            {
                "id": "claude-3-5-sonnet-20241022",
                "name": "Claude 3.5 Sonnet",
                "context": 200000,
                "pricing": {"prompt": "0.000003", "completion": "0.000015"},
                "architecture": {}
            },
            {
                "id": "claude-3-5-haiku-20241022",
                "name": "Claude 3.5 Haiku",
                "context": 200000,
                "pricing": {"prompt": "0.000001", "completion": "0.000005"},
                "architecture": {}
            },
            {
                "id": "claude-3-opus-20240229",
                "name": "Claude 3 Opus",
                "context": 200000,
                "pricing": {"prompt": "0.000015", "completion": "0.000075"},
                "architecture": {}
            }
        ]
        return {"success": True, "models": models, "count": len(models)}

    def _get_google_models(self) -> Dict:
        """Get predefined Google AI models"""
        models = [
            {
                "id": "gemini-2.0-flash-exp",
                "name": "Gemini 2.0 Flash",
                "context": 1000000,
                "pricing": {"prompt": "0", "completion": "0"},
                "architecture": {}
            },
            {
                "id": "gemini-1.5-pro",
                "name": "Gemini 1.5 Pro",
                "context": 2000000,
                "pricing": {"prompt": "0.00000125", "completion": "0.000005"},
                "architecture": {}
            },
            {
                "id": "gemini-1.5-flash",
                "name": "Gemini 1.5 Flash",
                "context": 1000000,
                "pricing": {"prompt": "0", "completion": "0"},
                "architecture": {}
            }
        ]
        return {"success": True, "models": models, "count": len(models)}
