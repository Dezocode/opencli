# OpenRouter Headers Auto-Config Specification

**Date**: 2025-01-08
**Goal**: Ensure OpenRouter headers (HTTP-Referer, X-Title) auto-configure 100% reliably
**Status**: 🔍 INVESTIGATION

---

## Problem Statement

OpenRouter models require specific headers (`HTTP-Referer` and `X-Title`) for proper operation and privacy compliance. Currently, the header auto-configuration doesn't work 100% of the time, leading to:

- Policy errors from OpenRouter API
- Manual header configuration required
- Inconsistent behavior between sessions
- Headers not applying in all code paths

---

## Current Behavior Analysis

### Header Sources (Priority Order)

Based on code analysis, headers are loaded from:

1. **Provider defaults** (`modules/provider_settings.py:13-14`):
   ```python
   _OPENROUTER_SITE = os.getenv("OPENROUTER_SITE_URL") or "https://github.com/Dezocode/opencli"
   _OPENROUTER_APP = os.getenv("OPENROUTER_APP_NAME") or "OpenCLI"
   ```

2. **Provider overrides** (`config.json:providerOverrides.openrouter.headers`):
   ```json
   {
     "providerOverrides": {
       "openrouter": {
         "headers": {
           "HTTP-Referer": "https://github.com/Dezocode/opencli",
           "X-Title": "OpenCLI"
         }
       }
     }
   }
   ```

3. **Environment variables**:
   - `OPENROUTER_SITE_URL` → `HTTP-Referer`
   - `OPENROUTER_APP_NAME` → `X-Title`

4. **Runtime config** (`config.json:defaultHeaders`):
   ```json
   {
     "defaultHeaders": {
       "HTTP-Referer": "https://github.com/Dezocode/opencli",
       "X-Title": "OpenCLI"
     }
   }
   ```

### Code Paths That Handle Headers

#### 1. Startup: `opencli.py:load_config()` (lines 287-314)
```python
# Build effective headers (provider defaults -> overrides -> environment)
provider_overrides = config.get("providerOverrides") or {}
provider_entry = provider_overrides.get(provider, {})

# Start with ONLY the current provider's default headers
headers = dict(provider_defaults.get("default_headers") or {})

# Apply base override
base_override = provider_entry.get("headers")
if isinstance(base_override, dict):
    headers.update(base_override)

# Apply model-specific override
model_override = provider_entry.get("models", {}).get(model_id)
if isinstance(model_override, dict):
    headers.update(model_override)

# OpenRouter environment variable override
if provider == "openrouter":
    site_url = os.getenv("OPENROUTER_SITE_URL")
    app_name = os.getenv("OPENROUTER_APP_NAME")
    if site_url:
        headers["HTTP-Referer"] = site_url
    if app_name:
        headers["X-Title"] = app_name

# Persist merged headers
if headers:
    config["defaultHeaders"] = headers
```

#### 2. ModelManager: `modules/model_manager.py:get_provider_headers()` (lines 195-215)
```python
def get_provider_headers(self, provider: str, model_id: Optional[str] = None) -> Dict[str, str]:
    provider_defaults = get_provider_defaults(provider)
    headers = dict(provider_defaults.get("default_headers") or {})

    # Apply provider-level overrides
    provider_overrides = self.config.get("providerOverrides", {})
    provider_entry = provider_overrides.get(provider, {})

    base_override = provider_entry.get("headers")
    if isinstance(base_override, dict):
        headers.update(base_override)

    # Apply model-specific overrides
    if model_id:
        model_override = provider_entry.get("models", {}).get(model_id)
        if isinstance(model_override, dict):
            headers.update(model_override)

    # Environment variable overrides for OpenRouter
    if provider == "openrouter":
        site_url = os.getenv("OPENROUTER_SITE_URL")
        app_name = os.getenv("OPENROUTER_APP_NAME")
        if site_url:
            headers["HTTP-Referer"] = site_url
        if app_name:
            headers["X-Title"] = app_name

    return headers
```

#### 3. Policy Error Handler: `opencli.py:handle_openrouter_policy_error()` (lines 1537-1585)
```python
# Suggested headers from environment overrides
proposed = {}
env_referer = os.getenv("OPENROUTER_SITE_URL")
env_title = os.getenv("OPENROUTER_APP_NAME")
if env_referer:
    proposed["HTTP-Referer"] = env_referer
if env_title:
    proposed["X-Title"] = env_title
if not proposed:
    proposed = {
        "HTTP-Referer": "https://github.com/Dezocode/opencli",
        "X-Title": "OpenCLI"
    }
```

#### 4. Async Interactive: `modules/async_interactive.py:handle_policy_error()` (lines 2405-2465)
Similar pattern to #3.

---

## Identified Issues

### Issue 1: Header Loss During Provider Switches
**Problem**: When switching between providers, headers may not be properly loaded for the new provider.

**Evidence**: Current config shows `apiKey` in saved config (line 16), which should be excluded. This suggests config saving may be overwriting runtime state.

### Issue 2: Multiple Header Loading Paths
**Problem**: 4 different code locations load headers independently, each potentially with different logic or bugs.

**Risk**: Inconsistency between what `load_config()` does vs what `ModelManager` does vs what policy error handlers do.

### Issue 3: Environment Variable Checking
**Problem**: Environment variables are checked in 4 separate locations but not centralized.

**Risk**: If env vars change during runtime, some code paths get new values, others get cached values.

### Issue 4: providerOverrides vs defaultHeaders Confusion
**Problem**: Both `config.json:providerOverrides` and `config.json:defaultHeaders` store headers.

**Current behavior**:
- `providerOverrides` = persistent storage per provider
- `defaultHeaders` = runtime merged headers
- But `defaultHeaders` is being saved to config.json (not just runtime)

**Risk**: Stale `defaultHeaders` from previous provider persists in config file.

### Issue 5: ModelManager Constructor Timing
**Problem**: `ModelManager.__init__()` calls `get_provider_headers()` which reads env vars, but constructor is called many times per session.

**Risk**: Different ModelManager instances may see different env var values if vars change.

---

## Success Criteria

For headers to auto-configure 100% reliably:

1. ✅ **On startup**: OpenRouter headers loaded from environment or defaults
2. ✅ **On provider switch TO OpenRouter**: Headers loaded correctly
3. ✅ **On provider switch FROM OpenRouter**: Headers removed (don't leak to other providers)
4. ✅ **On model switch within OpenRouter**: Headers persist
5. ✅ **On policy error**: Headers auto-applied and API call retried
6. ✅ **On session restart**: Headers reload from correct source
7. ✅ **Environment variable changes**: Reflected immediately in next API call
8. ✅ **No manual intervention**: User never needs to run `/providers headers` manually

---

## User Requirements (CRITICAL)

**Per-model header parsing**: Headers should be automatically fetched and parsed from each OpenRouter model's API page.

**Example**: For model `deepseek/deepseek-chat-v3.1:free`, fetch from:
```
https://openrouter.ai/deepseek/deepseek-chat-v3.1:free/api
```

Parse the page to extract the correct `HTTP-Referer` and `X-Title` values specific to that model.

### OpenRouter Header Requirements

Per OpenRouter documentation (https://openrouter.ai/docs/app-attribution):

**HTTP-Referer**:
- Purpose: Identifies app's URL for attribution
- Value: Full domain URL (e.g., "https://github.com/Dezocode/opencli")
- Required for: Appearing in OpenRouter rankings
- Localhost: Must include X-Title if using localhost URL

**X-Title**:
- Purpose: Sets app's display name in rankings
- Value: App name (e.g., "OpenCLI")
- Required for: Localhost development, optional otherwise
- Best practice: Keep concise and descriptive

**Current defaults**:
```python
HTTP-Referer: "https://github.com/Dezocode/opencli"
X-Title: "OpenCLI"
```

## Root Cause Hypothesis

**Primary hypothesis**: Headers are NOT being parsed from per-model API pages. Instead, they use hardcoded defaults.

**Required solution**:
1. Fetch model API page: `https://openrouter.ai/{model_id}/api`
2. Parse HTML/JSON to extract recommended headers for that model
3. Cache headers per model to avoid repeated fetches
4. Apply model-specific headers to API requests
5. Fall back to defaults if parsing fails

---

## Investigation Plan

### Phase 1: Trace Header Flow
1. ✅ Document all code paths that load headers
2. ⏳ Identify which path is failing
3. ⏳ Determine when headers are lost

### Phase 2: Create Test Cases
1. Test startup with OpenRouter model
2. Test switch from Google → OpenRouter
3. Test switch from OpenRouter → Google
4. Test policy error triggering header fix
5. Test environment variable changes
6. Test session restart

### Phase 3: Design Solution
Based on findings, design centralized header management that:
- Loads headers once per API call from authoritative source
- Never caches headers across provider switches
- Automatically retries on policy errors
- Works in all code paths (startup, interactive, error handlers)

---

## Next Steps

1. Create test script to reproduce header failures
2. Add strategic logging to trace header values through complete flow
3. Identify exact point where headers are lost or misapplied
4. Implement centralized header loading solution
5. Verify 100% success rate across all test cases

---

**Document Version**: 1.0
**Investigation Status**: In Progress
**Priority**: High (affects OpenRouter usability)
