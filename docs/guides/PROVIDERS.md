# Provider Management System

The `/providers` command enables automatic API provider detection and multi-provider support in OpenCLI.

## Features

- **Auto-Detection**: Automatically identifies provider from API key format
- **Multi-Provider Support**: OpenRouter, Anthropic, OpenAI, DeepSeek, Google AI
- **Unified Model List**: All provider models appear in `/model` switcher
- **Recent Models Integration**: Provider models automatically added to recent models list

## Usage

### List Configured Providers

```bash
/providers
/providers list
```

Shows all available providers with their configuration status and model counts.

### Add Provider Key

**Interactive Mode:**
```bash
/providers add
```
Prompts you to paste an API key, then auto-detects the provider.

**Direct Mode:**
```bash
/providers add sk-ant-api03-xyz...
```
Immediately detects provider and registers models.

### Remove Provider

```bash
/providers remove openrouter
/providers remove anthropic
```

## Supported Providers

| Provider | Key Format | Models Endpoint | Notes |
|----------|-----------|-----------------|-------|
| **OpenRouter** | `sk-or-...` | Dynamic from API | Full pricing, popularity ranking |
| **Anthropic** | `sk-ant-...` | Predefined | Claude 3.5 Sonnet, Haiku, Opus |
| **OpenAI** | `sk-proj-...` or `sk-...` | Dynamic from API | GPT-4, GPT-3.5, etc. |
| **DeepSeek** | `sk-...` | Dynamic from API | DeepSeek-V3, DeepSeek-R1 |
| **Google AI** | `AIza...` | Predefined | Gemini 2.0 Flash, 1.5 Pro/Flash |

## Auto-Detection Logic

The system identifies providers by analyzing API key prefixes:

- `sk-or-*` → OpenRouter
- `sk-ant-*` → Anthropic
- `sk-proj-*` → OpenAI
- `AIza*` → Google AI
- `sk-*` → OpenAI or DeepSeek (tries both)

## Integration with /model

After adding a provider:

1. Models are automatically fetched from the provider's API
2. All models appear in `/model` list
3. Free models are highlighted with green "FREE" badges
4. Models are sorted: FREE first, then by popularity (OpenRouter) or alphabetically
5. When you switch to a provider model, it's added to recent models list
6. Recent models show as `r1`, `r2`, etc. for quick switching

## Example Workflow

```bash
# Add your Anthropic API key
/providers add
# Paste: sk-ant-api03-xyz...

# ✓ Detected provider: Anthropic
# ✓ Registered 3 models

# Now see Anthropic models
/model

# Recent models will show Anthropic models after you use them
# Switch quickly with:
/model r1
```

## Benefits

1. **No Hardcoded Lists**: Models fetched fresh from provider APIs
2. **BYOK Support**: Bring your own keys for better rate limits
3. **Multi-Provider**: Use OpenRouter + direct API keys simultaneously
4. **Cost Optimization**: Mix free models (OpenRouter) with BYOK (1M free/month)
5. **Unified UX**: All providers work the same way in `/model` switcher

## Files Modified

- `modules/model_manager.py` - Provider detection and model fetching
- `modules/command_registry.py` - `/providers` command registration
- `modules/async_interactive.py` - `/providers` command handler
