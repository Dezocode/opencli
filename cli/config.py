"""
Configuration management for OpenCLI
API keys, provider setup, config loading/saving
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional


def get_api_key(provider="openrouter"):
    """Get API key for specified provider from environment or config"""
    # Check environment variables first
    env_vars = {
        "openrouter": "OPENROUTER_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY", 
        "openai": "OPENAI_API_KEY",
        "google": "GOOGLE_API_KEY"
    }
    
    env_var = env_vars.get(provider.lower())
    if env_var and os.getenv(env_var):
        return os.getenv(env_var)
    
    # Check config file
    try:
        config = load_config()
        return config.get("apiKey", "")
    except:
        return ""


def setup_api_key():
    """Interactive API key setup"""
    print("🔐 API Key Setup")
    print("=" * 50)
    
    providers = {
        "1": ("OpenRouter", "openrouter", "OPENROUTER_API_KEY"),
        "2": ("Anthropic", "anthropic", "ANTHROPIC_API_KEY"),
        "3": ("OpenAI", "openai", "OPENAI_API_KEY"),
        "4": ("Google", "google", "GOOGLE_API_KEY")
    }
    
    print("Select your AI provider:")
    for key, (name, _, _) in providers.items():
        print(f"  {key}. {name}")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice not in providers:
        print("❌ Invalid choice")
        return
    
    provider_name, provider_key, env_var = providers[choice]
    
    print(f"\n📋 Setting up {provider_name}")
    print(f"Environment variable: {env_var}")
    
    api_key = input(f"Enter your {provider_name} API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        return
    
    # Save to config
    try:
        config = load_config()
        config["apiKey"] = api_key
        save_config(config)
        print(f"✅ API key saved to config")
        print(f"💡 You can also set the environment variable: export {env_var}={api_key}")
    except Exception as e:
        print(f"❌ Failed to save config: {e}")


def load_config() -> Dict[str, Any]:
    """Load configuration from config file"""
    config_dir = Path.home() / '.opencli'
    config_file = config_dir / 'config.json'
    
    # Default configuration
    default_config = {
        "model": "grok-beta",
        "baseURL": "https://openrouter.ai/api/v1",
        "apiKey": "",
        "provider": "openrouter",
        "maxTokens": 4096,
        "temperature": 0.7,
        "systemPrompt": "",
        "saveConversations": True,
        "debugMode": False,
        "theme": "dark",
        "autoSave": True,
        "timeout": 60,
        "retries": 3,
        "defaultHeaders": {
            "HTTP-Referer": "https://github.com/your-username/opencli",
            "X-Title": "OpenCLI"
        }
    }
    
    try:
        if config_file.exists():
            with open(config_file, 'r') as f:
                user_config = json.load(f)
            
            # Merge with defaults
            config = default_config.copy()
            config.update(user_config)
            return config
        else:
            # Create default config file
            config_dir.mkdir(parents=True, exist_ok=True)
            save_config(default_config)
            return default_config
            
    except Exception as e:
        print(f"⚠️ Error loading config: {e}")
        print("📄 Using default configuration")
        return default_config


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to config file"""
    config_dir = Path.home() / '.opencli'
    config_file = config_dir / 'config.json'
    
    try:
        config_dir.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        raise Exception(f"Failed to save config: {e}")


def update_config(updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update configuration with new values"""
    config = load_config()
    config.update(updates)
    save_config(config)
    return config


def get_config_value(key: str, default: Any = None) -> Any:
    """Get a specific configuration value"""
    try:
        config = load_config()
        return config.get(key, default)
    except:
        return default


def set_config_value(key: str, value: Any) -> None:
    """Set a specific configuration value"""
    config = load_config()
    config[key] = value
    save_config(config)


def reset_config() -> Dict[str, Any]:
    """Reset configuration to defaults"""
    config_dir = Path.home() / '.opencli'
    config_file = config_dir / 'config.json'
    
    # Remove existing config
    if config_file.exists():
        config_file.unlink()
    
    # Load defaults (will create new file)
    return load_config()


def validate_config(config: Dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate configuration and return (is_valid, errors)"""
    errors = []
    
    # Required fields
    required_fields = ["model", "baseURL", "apiKey"]
    for field in required_fields:
        if not config.get(field):
            errors.append(f"Missing required field: {field}")
    
    # Validate types
    type_checks = {
        "maxTokens": int,
        "temperature": (int, float),
        "timeout": int,
        "retries": int,
        "saveConversations": bool,
        "debugMode": bool,
        "autoSave": bool
    }
    
    for field, expected_type in type_checks.items():
        if field in config and not isinstance(config[field], expected_type):
            errors.append(f"Invalid type for {field}: expected {expected_type.__name__}")
    
    # Validate ranges
    if config.get("temperature", 0) < 0 or config.get("temperature", 0) > 2:
        errors.append("Temperature must be between 0 and 2")
    
    if config.get("maxTokens", 0) < 1:
        errors.append("Max tokens must be positive")
    
    if config.get("timeout", 0) < 1:
        errors.append("Timeout must be positive")
    
    return len(errors) == 0, errors


def print_config() -> None:
    """Print current configuration (hiding sensitive data)"""
    try:
        config = load_config()
        
        print("📋 Current Configuration:")
        print("=" * 40)
        
        # Hide sensitive data
        display_config = config.copy()
        if display_config.get("apiKey"):
            display_config["apiKey"] = "***" + display_config["apiKey"][-4:]
        
        for key, value in display_config.items():
            if isinstance(value, dict):
                print(f"{key}:")
                for subkey, subvalue in value.items():
                    print(f"  {subkey}: {subvalue}")
            else:
                print(f"{key}: {value}")
                
    except Exception as e:
        print(f"❌ Error reading config: {e}")


def migrate_legacy_config() -> None:
    """Migrate configuration from older versions"""
    config_dir = Path.home() / '.opencli'
    legacy_config = config_dir / 'opencli.json'  # Old config name
    new_config = config_dir / 'config.json'     # New config name
    
    if legacy_config.exists() and not new_config.exists():
        try:
            # Copy old config to new location
            import shutil
            shutil.copy2(legacy_config, new_config)
            print("✅ Migrated legacy configuration")
        except Exception as e:
            print(f"⚠️ Could not migrate legacy config: {e}")


# Initialize config migration on import
migrate_legacy_config()