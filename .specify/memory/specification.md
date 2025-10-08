# Provider Auto-Configuration & 100% Connection Rate Specification

## What We're Building

A robust, fully automated provider switching system for OpenCLI that guarantees 100% valid connection rates across all supported AI providers, with zero manual configuration required.

## Problem Statement

**Current Issue:**
Users experience streaming errors when switching between providers due to:
- Incorrect authentication methods (Google/Gemini using Bearer token instead of query parameter)
- Header leakage between providers (OpenRouter headers sent to Anthropic)
- Malformed API call structures (wrong message formats for different providers)
- Manual configuration burden (users need to know provider-specific details)

**Example Error:**
```
❌ Streaming Error: Error code: 400 - API key not valid. Please pass a valid API key.
Provider: gemini-2.0-flash-exp
Issue: Google API rejected Bearer token auth, requires ?key=API_KEY parameter
```

## Value Proposition

**For Users:**
- Switch providers effortlessly with `/model` command
- Never see authentication errors due to misconfiguration
- No need to understand provider-specific API requirements
- Confidence that any model will work once API key is added

**For Developers:**
- Clean, maintainable provider abstraction
- Easy to add new providers without touching core logic
- Comprehensive test coverage prevents regressions
- Clear debugging information when issues occur

## Functional Requirements

### 1. Auto-Detection & Configuration

**Requirement:** System automatically detects provider from model selection and applies correct configuration.

**Behavior:**
- User selects model: `gemini-2.0-flash-exp`
- System detects provider: `google`
- System applies Google-specific config:
  - Base URL: `https://generativelanguage.googleapis.com/v1beta/openai/`
  - Auth method: Query parameter `?key=API_KEY`
  - Request format: `openai-chat`
  - Headers: None (Google doesn't need custom headers)

**Acceptance Criteria:**
- ✅ Provider detected from model ID prefix
- ✅ Provider detected from models database
- ✅ Fallback to configured provider if detection fails
- ✅ Config applied before client creation

### 2. Provider-Specific Authentication

**Requirement:** Each provider uses its correct authentication method.

**Authentication Matrix:**

| Provider | Method | Implementation |
|----------|--------|---------------|
| OpenRouter | Bearer token | `Authorization: Bearer {key}` header |
| Anthropic | Bearer token + version | `Authorization: Bearer {key}` + `anthropic-version: 2023-06-01` |
| OpenAI | Bearer token | `Authorization: Bearer {key}` header |
| DeepSeek | Bearer token | `Authorization: Bearer {key}` header |
| Google | Query parameter | `?key={api_key}` in URL, no Authorization header |

**Acceptance Criteria:**
- ✅ Each provider authenticates successfully with valid API key
- ✅ Google uses query param, not Bearer token
- ✅ Anthropic includes version header
- ✅ OpenRouter includes referer headers
- ✅ No provider receives wrong auth format

### 3. Header Isolation

**Requirement:** Provider-specific headers never leak to other providers.

**Current Issue:**
```python
# Bad: Headers persist across provider switches
config["defaultHeaders"] = {"HTTP-Referer": "..."}  # OpenRouter
# Switch to Anthropic -> Anthropic receives OpenRouter headers ❌
```

**Solution:**
```python
# Good: Headers rebuilt for each provider
headers = get_provider_headers(provider, model)
config["defaultHeaders"] = headers  # Only this provider's headers
```

**Acceptance Criteria:**
- ✅ Headers cleared when switching providers
- ✅ Only provider-specific headers included
- ✅ Model-specific header overrides work
- ✅ User custom headers preserved per provider

### 4. Message Format Translation

**Requirement:** API calls use provider's expected message structure.

**Format Support:**
- `openai-chat`: OpenRouter, OpenAI, DeepSeek, Google (via OpenAI-compatible endpoint)
- `anthropic-messages`: Anthropic (native format)

**Acceptance Criteria:**
- ✅ Format auto-selected based on provider
- ✅ Messages converted to provider format
- ✅ Tool calls mapped correctly
- ✅ Streaming responses parsed correctly

### 5. Configuration Migration

**Requirement:** Legacy configurations auto-upgrade to new format.

**Migration Scenarios:**
1. Old Google config with direct generativelanguage endpoint → Migrate to OpenAI-compatible endpoint
2. Missing auth_method field → Add based on provider type
3. Old single API key format → Migrate to multi-provider format
4. Missing provider field → Infer from baseURL or model

**Acceptance Criteria:**
- ✅ Legacy configs detected on startup
- ✅ Auto-migration applied without user action
- ✅ Migration logged in debug mode
- ✅ Original config backed up before migration

### 6. Error Handling & Recovery

**Requirement:** Informative errors with clear resolution steps.

**Error Types & Messages:**

```
❌ API Key Invalid
   Provider: google
   Issue: API key format incorrect or expired
   Fix: Check API key at https://makersuite.google.com/app/apikey

❌ Authentication Failed
   Provider: anthropic
   Issue: Using wrong auth method
   Fix: [System auto-corrects and retries]

❌ Provider Not Configured
   Provider: google
   Issue: No API key found
   Fix: Add API key with: /providers add google YOUR_KEY
```

**Acceptance Criteria:**
- ✅ Errors include provider name
- ✅ Errors explain root cause
- ✅ Errors suggest fix steps
- ✅ Auto-retry with corrected config when possible
- ✅ User can continue chatting after errors

## User Experience

### Happy Path: Switching Providers

```
User: /model gemini-2.0-flash-exp
Bot: ✓ Switched to gemini-2.0-flash-exp (Google AI)

User: Hi
Bot: [Streams response successfully using Google API]

User: /model anthropic/claude-3-5-sonnet
Bot: ✓ Switched to claude-3-5-sonnet (Anthropic)

User: Hi
Bot: [Streams response successfully using Anthropic API]
```

### Error Path: Invalid API Key

```
User: /model gemini-2.0-flash-exp
Bot: ✓ Switched to gemini-2.0-flash-exp (Google AI)

User: Hi
Bot: ❌ Streaming Error: API key not valid
     Provider: google
     Fix: Check your API key at https://makersuite.google.com/app/apikey

     ⚠️ You can continue chatting.
```

### Debug Mode Experience

```
User: /debug on
Bot: ✓ Debug mode enabled

User: /model gemini-2.0-flash-exp
Bot: [DEBUG] Detected provider: google from model ID
     [DEBUG] Applying Google config:
       - Base URL: https://generativelanguage.googleapis.com/v1beta/openai/
       - Auth: query_param
       - Format: openai-chat
     [DEBUG] Creating client with query param auth
     ✓ Switched to gemini-2.0-flash-exp (Google AI)
```

## Success Criteria

### Functional Success
1. All 5 supported providers (OpenRouter, Anthropic, OpenAI, DeepSeek, Google) connect successfully
2. Switching between any two providers works without errors
3. Each provider uses its correct authentication method
4. Headers are properly isolated between providers
5. Message formats are correctly translated

### Quality Success
1. 100% connection rate with valid API keys
2. Zero header leakage between providers
3. All provider-specific quirks handled transparently
4. Debug logging provides complete troubleshooting info
5. Error messages guide users to resolution

### User Success
1. Users never need to manually configure provider settings
2. Provider switching "just works" on first try
3. Errors are rare and clearly explained when they occur
4. Users can switch providers as easily as switching models
5. No special knowledge required to use any provider

## Out of Scope

- Custom provider support (v1 focuses on the 5 core providers)
- Provider-specific feature parity (some providers may have unique capabilities)
- Automatic API key acquisition (users must provide their own keys)
- Cross-provider conversation migration (conversation history stays with session)
- Provider performance optimization (beyond basic request efficiency)

## Technical Constraints

- Must work with existing OpenCLI architecture
- Must maintain backward compatibility with existing configs
- Must use AsyncOpenAI client for all providers (via compatibility layer)
- Must not require external dependencies beyond current stack
- Must preserve file operation permissions and security

## Dependencies

- Existing provider_settings.py with PROVIDER_DEFAULTS
- model_manager.py for provider detection
- async_interactive.py for client creation
- Config files: config.json, models.json, .secrets

## Risks & Mitigation

**Risk:** Breaking existing configurations
**Mitigation:** Auto-migration with backup, extensive testing

**Risk:** Provider API changes
**Mitigation:** Version checking, graceful fallbacks

**Risk:** New provider quirks discovered
**Mitigation:** Debug logging, easy config updates

**Risk:** Security issues with query param auth
**Mitigation:** URL encoding, no logging of sensitive data
