"""
Model Manager for OpenCLI
Handles model switching and API key management
Does NOT call any LLM APIs - pure local configuration management
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


class ModelManager:
    """Manage models and API keys locally without API calls"""

    def __init__(self, config_dir: Path = None):
        self.config_dir = config_dir or Path.home() / ".opencli"
        self.models_file = self.config_dir / "models.json"
        self.config_file = self.config_dir / "config.json"

        # Load models configuration
        self.models = self._load_models()
        self.config = self._load_config()

    def _load_models(self) -> Dict:
        """Load models configuration"""
        if self.models_file.exists():
            with open(self.models_file) as f:
                return json.load(f)
        else:
            # Default models configuration
            return {
                "providers": {
                    "openrouter": {
                        "name": "OpenRouter",
                        "base_url": "https://openrouter.ai/api/v1",
                        "requires_key": True
                    },
                    "openai": {
                        "name": "OpenAI",
                        "base_url": "https://api.openai.com/v1",
                        "requires_key": True
                    },
                    "anthropic": {
                        "name": "Anthropic",
                        "base_url": "https://api.anthropic.com/v1",
                        "requires_key": True
                    }
                },
                "models": {
                    "openrouter/x-ai/grok-4-fast:free": {
                        "provider": "openrouter",
                        "name": "Grok 4 Fast (Free)",
                        "context": 128000,
                        "default": True
                    },
                    "openrouter/anthropic/claude-sonnet-4": {
                        "provider": "openrouter",
                        "name": "Claude Sonnet 4",
                        "context": 200000
                    },
                    "openrouter/google/gemini-2.0-flash-thinking-exp:free": {
                        "provider": "openrouter",
                        "name": "Gemini 2.0 Flash Thinking (Free)",
                        "context": 32000
                    },
                    "gpt-4o": {
                        "provider": "openai",
                        "name": "GPT-4o",
                        "context": 128000
                    },
                    "claude-3-5-sonnet-20241022": {
                        "provider": "anthropic",
                        "name": "Claude 3.5 Sonnet",
                        "context": 200000
                    }
                },
                "api_keys": {}
            }

    def _load_config(self) -> Dict:
        """Load main config"""
        if self.config_file.exists():
            with open(self.config_file) as f:
                return json.load(f)
        return {}

    def _save_models(self):
        """Save models configuration"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.models_file, 'w') as f:
            json.dump(self.models, f, indent=2)

    def _save_config(self):
        """Save main config"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def list_models(self) -> List[Dict]:
        """
        List all available models

        Returns:
            List of model dicts with metadata
        """
        models_list = []
        for model_id, model_info in self.models.get("models", {}).items():
            provider_id = model_info.get("provider")
            provider = self.models["providers"].get(provider_id, {})

            has_key = bool(self.get_api_key(provider_id))

            models_list.append({
                "id": model_id,
                "name": model_info.get("name", model_id),
                "provider": provider.get("name", provider_id),
                "provider_id": provider_id,
                "context": model_info.get("context", 0),
                "has_key": has_key,
                "is_default": model_info.get("default", False)
            })

        return sorted(models_list, key=lambda x: (not x["is_default"], x["name"]))

    def get_current_model(self, session) -> str:
        """Get current model from session or config"""
        return session.model if hasattr(session, 'model') and session.model else self.config.get("model", "openrouter/x-ai/grok-4-fast:free")

    def switch_model(self, session, model_id: str) -> Dict:
        """
        Switch to a different model

        Args:
            session: Session object
            model_id: Model identifier

        Returns:
            Result dict with success status
        """
        if model_id not in self.models.get("models", {}):
            return {
                "success": False,
                "error": f"Unknown model: {model_id}"
            }

        model_info = self.models["models"][model_id]
        provider_id = model_info.get("provider")
        provider = self.models["providers"].get(provider_id, {})

        # Check if API key is required and available
        if provider.get("requires_key"):
            if not self.get_api_key(provider_id):
                return {
                    "success": False,
                    "error": f"No API key set for {provider.get('name', provider_id)}",
                    "needs_key": True,
                    "provider_id": provider_id
                }

        # Update session
        session.model = model_id

        # Update config for persistence
        self.config["model"] = model_id
        self.config["baseURL"] = provider.get("base_url")
        self._save_config()

        return {
            "success": True,
            "model": model_info.get("name", model_id),
            "provider": provider.get("name", provider_id)
        }

    def get_api_key(self, provider_id: str) -> Optional[str]:
        """Get API key for provider"""
        # Check models.json first
        key = self.models.get("api_keys", {}).get(provider_id)
        if key:
            return key

        # Check main config as fallback
        if provider_id == "openrouter":
            return self.config.get("apiKey")

        return None

    def set_api_key(self, provider_id: str, api_key: str):
        """
        Set API key for provider

        Args:
            provider_id: Provider identifier
            api_key: API key string
        """
        if "api_keys" not in self.models:
            self.models["api_keys"] = {}

        self.models["api_keys"][provider_id] = api_key
        self._save_models()

        # Also update main config if it's the current provider
        current_model = self.config.get("model", "")
        if current_model:
            model_info = self.models.get("models", {}).get(current_model, {})
            if model_info.get("provider") == provider_id:
                self.config["apiKey"] = api_key
                self._save_config()

    def get_providers(self) -> List[Dict]:
        """List all providers"""
        providers = []
        for provider_id, provider_info in self.models.get("providers", {}).items():
            has_key = bool(self.get_api_key(provider_id))
            providers.append({
                "id": provider_id,
                "name": provider_info.get("name", provider_id),
                "base_url": provider_info.get("base_url"),
                "requires_key": provider_info.get("requires_key", False),
                "has_key": has_key
            })
        return providers
