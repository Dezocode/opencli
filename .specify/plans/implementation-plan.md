# Provider Auto-Configuration Implementation Plan

## Technology Stack

### Core Components (No Changes)
- **Python**: 3.8+ (existing requirement)
- **AsyncIO**: For non-blocking API calls
- **httpx**: HTTP client with async support
- **openai**: AsyncOpenAI client (used for all providers via compatibility)

### Provider Configuration
- **provider_settings.py**: Provider metadata and defaults
- **model_manager.py**: Provider detection and model discovery
- **async_interactive.py**: Client factory and streaming logic

### Storage & Configuration
- **config.json**: Main configuration (provider, model, baseURL)
- **models.json**: Model database and API keys (0o600 permissions)
- **.secrets**: Legacy API key storage (0o600 permissions)

## System Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface (TUI)                  │
│                  /model <model-id>                       │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   ModelManager                           │
│  - detect_provider(api_key) → provider_id               │
│  - get_provider_for_model(model_id) → provider_id       │
│  - switch_model(session, model_id) → result             │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                 ProviderSettings                         │
│  - get_provider_defaults(provider_id) → settings        │
│  - ensure_provider_defaults(existing) → merged          │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              create_async_client(config)                 │
│  - Checks auth_method from provider settings            │
│  - Google: Adds ?key={api_key} to base_url              │
│  - Others: Uses Authorization: Bearer {api_key}         │
│  - Returns AsyncOpenAI client                           │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                 AsyncOpenAI Client                       │
│  - Handles streaming responses                          │
│  - Applies provider-specific headers                    │
│  - Uses provider's base_url + auth                      │
└─────────────────────────────────────────────────────────┘
```

### Data Flow: Provider Switch

```
1. User: /model gemini-2.0-flash-exp
   ↓
2. ModelManager.switch_model()
   ↓
3. get_provider_for_model("gemini-2.0-flash-exp") → "google"
   ↓
4. get_provider_defaults("google") → {
       base_url: "https://generativelanguage.googleapis.com/v1beta/openai/",
       auth_method: "query_param",
       request_format: "openai-chat"
   }
   ↓
5. Update config:
   config["provider"] = "google"
   config["model"] = "gemini-2.0-flash-exp"
   config["baseURL"] = "https://generativelanguage.googleapis.com/v1beta/openai/"
   config["requestFormat"] = "openai-chat"
   ↓
6. get_provider_headers("google", "gemini-2.0-flash-exp") → {}
   config["defaultHeaders"] = {}
   ↓
7. Save config to disk
   ↓
8. create_async_client(config)
   - Sees provider == "google"
   - Appends ?key={api_key} to base_url
   - Uses "placeholder" as api_key to prevent Authorization header
   - Creates AsyncOpenAI client
   ↓
9. Client ready for streaming
```

## Data Models

### Provider Settings Schema

```python
{
    "provider_id": {
        "name": str,              # Display name: "Google AI"
        "base_url": str,          # API endpoint base URL
        "models_endpoint": str,   # URL to fetch model list (optional)
        "key_patterns": [str],    # Patterns to detect API key: ["AIza"]
        "request_format": str,    # "openai-chat" or "anthropic-messages"
        "auth_method": str,       # "bearer" (default) or "query_param"
        "default_headers": dict   # Provider-specific headers
    }
}
```

### Example: Google Provider

```python
{
    "google": {
        "name": "Google AI",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "models_endpoint": None,
        "key_patterns": ["AIza"],
        "request_format": "openai-chat",
        "auth_method": "query_param",
        "default_headers": {}
    }
}
```

### Config.json Schema

```json
{
    "provider": "google",
    "model": "gemini-2.0-flash-exp",
    "apiKey": "AIza...",
    "baseURL": "https://generativelanguage.googleapis.com/v1beta/openai/",
    "requestFormat": "openai-chat",
    "defaultHeaders": {},
    "providerOverrides": {
        "google": {
            "headers": {},
            "models": {
                "gemini-2.0-flash-exp": {}
            }
        }
    }
}
```

## API Design

### Provider Settings API

```python
# Get provider defaults (deep copy to prevent mutations)
def get_provider_defaults(provider_id: str) -> Dict[str, Any]:
    """Return provider settings with all defaults applied."""

# Merge saved settings with current defaults
def ensure_provider_defaults(existing: Dict) -> Dict:
    """Ensure all providers have required fields."""

# Get effective headers for provider/model combo
def get_provider_headers(provider: str, model: str) -> Dict[str, str]:
    """Build headers from defaults + overrides."""
```

### Model Manager API

```python
# Detect provider from API key format
def detect_provider(api_key: str) -> Optional[str]:
    """Auto-detect provider from key pattern."""

# Get provider for a given model
def get_provider_for_model(model_id: str) -> Optional[str]:
    """Identify provider from model ID."""

# Switch to a different model
def switch_model(session, model_id: str) -> Dict:
    """Switch model and update provider config."""

# Internal: Set active provider
def _set_active_provider(provider: str, api_key: str):
    """Update config for provider switch."""
```

### Client Factory API

```python
def create_async_client(current_config: Dict) -> AsyncOpenAI:
    """
    Create AsyncOpenAI client with provider-specific auth.

    - Reads provider from config
    - Applies Google's query param auth if needed
    - Sets up headers from config
    - Returns configured client
    """
```

## Implementation Details

### 1. Google Query Parameter Authentication

**Problem:** Google's OpenAI-compatible endpoint requires `?key=API_KEY`, not `Authorization: Bearer`

**Solution:**
```python
def create_async_client(current_config):
    headers = current_config.get("defaultHeaders") or None
    base_url = current_config["baseURL"]
    api_key = current_config["apiKey"]

    provider = current_config.get("provider", "")
    if provider == "google":
        # Append API key as query parameter
        if "?" in base_url:
            base_url = f"{base_url}&key={api_key}"
        else:
            base_url = f"{base_url}?key={api_key}"
        # Use placeholder to prevent Authorization header
        api_key = "placeholder"

    return AsyncOpenAI(
        base_url=base_url,
        api_key=api_key,
        default_headers=headers
    )
```

**Why This Works:**
- AsyncOpenAI always adds `Authorization: Bearer {api_key}` if api_key is provided
- By using "placeholder", we prevent the Authorization header
- The real API key goes in the URL query parameter
- Google's endpoint accepts the query param and ignores missing Authorization header

### 2. Header Isolation

**Problem:** Headers from one provider leak to another

**Current Implementation (Already Fixed):**
```python
def _set_active_provider(self, provider: str, api_key: str):
    # ... set provider, baseURL, requestFormat ...

    # Get fresh headers for this provider
    headers = self.get_provider_headers(provider, self.config.get("model"))
    if headers:
        self.config["defaultHeaders"] = headers
    elif "defaultHeaders" in self.config:
        # Important: Delete old headers if new provider has none
        del self.config["defaultHeaders"]

    self._save_config()
```

**Why This Works:**
- Headers are rebuilt from scratch for each provider
- Old headers are explicitly deleted if new provider has none
- get_provider_headers() pulls from provider defaults + user overrides
- No residual headers from previous provider

### 3. Provider Detection

**Detection Priority:**
1. From model ID in models database
2. From model ID prefix (e.g., "anthropic/" → "anthropic")
3. From current config["provider"]
4. From baseURL matching provider's base_url
5. Default to "openrouter"

**Implementation:**
```python
def get_provider_for_model(self, model_id: str) -> Optional[str]:
    if not model_id:
        return None

    # 1. Check models database
    models = self.models_db.get("models", {})
    if model_id in models:
        provider = models[model_id].get("provider")
        if provider:
            return provider

    # 2. Check prefix (anthropic/claude-3-5-sonnet → anthropic)
    if "/" in model_id:
        prefix = model_id.split("/", 1)[0]
        if prefix in self.models_db.get("providers", {}):
            return prefix

    # 3. Fall back to current provider
    return self.config.get("provider")
```

### 4. Configuration Migration

**Legacy Google Config:**
```json
{
    "provider": "google",
    "baseURL": "https://generativelanguage.googleapis.com/v1beta",
    "apiKey": "AIza..."
}
```

**Migrated Config:**
```json
{
    "provider": "google",
    "baseURL": "https://generativelanguage.googleapis.com/v1beta/openai/",
    "apiKey": "AIza...",
    "requestFormat": "openai-chat"
}
```

**Migration Logic (Already Implemented in Recent Commits):**
- Check if baseURL is old generativelanguage endpoint without /openai/
- Update to OpenAI-compatible endpoint
- Add request_format if missing
- Log migration in debug mode

## File Structure

```
opencli/
├── modules/
│   ├── provider_settings.py       # Provider defaults (MODIFIED)
│   ├── model_manager.py            # Provider detection (EXISTING)
│   ├── async_interactive.py        # Client factory (MODIFIED)
│   └── uptime_checker.py           # Health checks (NO CHANGES)
├── .specify/
│   ├── memory/
│   │   ├── constitution.md         # Project principles (CREATED)
│   │   └── specification.md        # Requirements (CREATED)
│   └── plans/
│       └── implementation-plan.md  # This file (CREATED)
└── config files/
    ├── config.json                 # Main config (RUNTIME UPDATES)
    ├── models.json                 # Model DB (RUNTIME UPDATES)
    └── .secrets                    # API keys (USER PROVIDED)
```

## Testing Strategy

### Unit Tests

```python
# test_provider_settings.py
def test_google_has_query_param_auth():
    settings = get_provider_defaults("google")
    assert settings["auth_method"] == "query_param"

def test_header_isolation():
    # Verify headers cleared when switching providers

# test_model_manager.py
def test_provider_detection_from_model_id():
    assert get_provider_for_model("gemini-2.0-flash-exp") == "google"

def test_api_key_detection():
    assert detect_provider("AIza...") == "google"
    assert detect_provider("sk-ant-...") == "anthropic"

# test_client_factory.py
def test_google_client_has_query_param():
    config = {
        "provider": "google",
        "baseURL": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "apiKey": "AIzaTestKey123"
    }
    client = create_async_client(config)
    assert "?key=AIzaTestKey123" in client.base_url
    assert client.api_key == "placeholder"
```

### Integration Tests

```python
# test_provider_switching.py
async def test_switch_from_openrouter_to_google():
    # Start with OpenRouter
    session.model = "openrouter/anthropic/claude-3-5-sonnet"

    # Switch to Google
    result = manager.switch_model(session, "gemini-2.0-flash-exp")

    # Verify switch successful
    assert result["success"] == True
    assert config["provider"] == "google"
    assert "HTTP-Referer" not in config.get("defaultHeaders", {})

async def test_api_call_after_switch():
    # Switch to Google
    manager.switch_model(session, "gemini-2.0-flash-exp")

    # Make API call
    response = await client.chat.completions.create(
        model="gemini-2.0-flash-exp",
        messages=[{"role": "user", "content": "Hi"}],
        stream=True
    )

    # Verify response streams without error
    async for chunk in response:
        assert chunk is not None
```

### Manual Testing Checklist

- [ ] OpenRouter → Google switch works
- [ ] Google → Anthropic switch works
- [ ] Anthropic → OpenAI switch works
- [ ] OpenAI → DeepSeek switch works
- [ ] DeepSeek → OpenRouter switch works
- [ ] Each provider streams responses correctly
- [ ] Headers are isolated per provider
- [ ] Invalid API keys show helpful errors
- [ ] Debug mode shows provider switches
- [ ] Legacy configs auto-migrate

## Deployment Plan

### Phase 1: Core Fixes (COMPLETED)
- [x] Add auth_method to Google provider settings
- [x] Update create_async_client for query param auth
- [x] Verify header isolation in _set_active_provider

### Phase 2: Testing & Validation (CURRENT)
- [ ] Test Google provider with valid API key
- [ ] Test switching between all 5 providers
- [ ] Verify no header leakage
- [ ] Check debug logging

### Phase 3: Documentation
- [ ] Update SPEC_DRIVEN.md with provider switching details
- [ ] Document auth methods for each provider
- [ ] Add troubleshooting guide for common errors
- [ ] Create provider configuration examples

### Phase 4: Monitoring
- [ ] Add provider switch metrics
- [ ] Log provider-specific errors
- [ ] Track connection success rates
- [ ] Monitor header configurations

## Performance Targets

- Provider switch: < 50ms
- Config load: < 100ms
- Client creation: < 20ms
- Header resolution: < 5ms

## Security Considerations

### API Key Protection
- Never log API keys (even in debug mode)
- Use 0o600 permissions on .secrets and models.json
- URL-encode keys in query parameters
- Clear sensitive data from memory after use

### Header Security
- Validate header values before setting
- Prevent injection attacks via custom headers
- Isolate headers per provider
- No cross-origin header leakage

### Network Security
- Use HTTPS for all provider endpoints
- Validate SSL certificates
- Timeout requests after 30s
- Retry with exponential backoff

## Rollback Plan

If issues occur:
1. Revert provider_settings.py to remove auth_method
2. Revert async_interactive.py client factory changes
3. Users can manually configure Google with old endpoint
4. Document manual workaround in README

## Success Metrics

- 100% connection rate with valid API keys
- 0 header leakage incidents
- < 1% error rate from provider switching
- All 5 providers pass integration tests
- User can switch providers without manual config
