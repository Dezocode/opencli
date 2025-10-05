"""
Model Manager for OpenCLI
Auto-discovers models from API keys, no hardcoded model lists
"""

import json
import httpx
from pathlib import Path
from typing import Dict, List, Optional


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

    def _load_models(self) -> Dict:
        """Load models database"""
        if self.models_file.exists():
            with open(self.models_file) as f:
                return json.load(f)
        return {
            "api_keys": {},
            "models": {},
            "usage_history": [],  # Track recently used models
            "providers": {
                "openrouter": {
                    "name": "OpenRouter",
                    "base_url": "https://openrouter.ai/api/v1",
                    "models_endpoint": "https://openrouter.ai/api/v1/models",
                    "key_patterns": ["sk-or-", "OPENROUTER"]
                },
                "anthropic": {
                    "name": "Anthropic",
                    "base_url": "https://api.anthropic.com/v1",
                    "models_endpoint": None,  # Uses predefined model list
                    "key_patterns": ["sk-ant-"]
                },
                "openai": {
                    "name": "OpenAI",
                    "base_url": "https://api.openai.com/v1",
                    "models_endpoint": "https://api.openai.com/v1/models",
                    "key_patterns": ["sk-proj-", "sk-"]
                },
                "deepseek": {
                    "name": "DeepSeek",
                    "base_url": "https://api.deepseek.com/v1",
                    "models_endpoint": "https://api.deepseek.com/v1/models",
                    "key_patterns": ["sk-"]
                },
                "google": {
                    "name": "Google AI",
                    "base_url": "https://generativelanguage.googleapis.com/v1beta",
                    "models_endpoint": None,
                    "key_patterns": ["AIza"]
                }
            }
        }

    def _load_config(self) -> Dict:
        """Load main config"""
        if self.config_file.exists():
            with open(self.config_file) as f:
                return json.load(f)
        return {}

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
            self.config["apiKey"] = api_key
            provider_info = self.models_db["providers"].get(provider, {})
            self.config["baseURL"] = provider_info.get("base_url")
            self._save_config()

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
        provider_info = self.models_db["providers"].get(provider, {})
        self.config["baseURL"] = provider_info.get("base_url")
        self.config["apiKey"] = keys[provider]
        self._save_config()

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
            endpoint = provider_info.get("models_endpoint")
            if not endpoint:
                return {"success": False, "error": "No models endpoint configured"}

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    endpoint,
                    headers={"Authorization": f"Bearer {api_key}"},
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
