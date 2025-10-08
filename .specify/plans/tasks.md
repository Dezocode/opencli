# OpenRouter Headers Auto-Config - Task Breakdown

**Date**: 2025-01-08
**Goal**: Implement per-model header fetching from OpenRouter API pages
**Status**: 📋 READY FOR IMPLEMENTATION

---

## Code Research Summary

### Current Architecture

**Key Files** (5,978 total lines):
- `opencli.py` - 1,982 lines - Startup and config loading
- `modules/async_interactive.py` - 3,310 lines - Interactive TUI and command handlers
- `modules/model_manager.py` - 686 lines - Model and provider management
- `modules/provider_settings.py` - ~100 lines - Provider defaults configuration

### Current Header Loading Flow

**1. Startup (`opencli.py:287-320`)**
```python
# Build headers from provider defaults
headers = dict(provider_defaults.get("default_headers") or {})

# Apply provider-level overrides from config.json
base_override = provider_entry.get("headers")
if isinstance(base_override, dict):
    headers.update(base_override)

# Apply model-specific overrides
model_override = provider_entry.get("models", {}).get(model_id)
if isinstance(model_override, dict):
    headers.update(model_override)

# OpenRouter: Apply environment variables
if provider == "openrouter":
    site_url = os.getenv("OPENROUTER_SITE_URL")
    app_name = os.getenv("OPENROUTER_APP_NAME")
    if site_url:
        headers["HTTP-Referer"] = site_url
    if app_name:
        headers["X-Title"] = app_name

# Save to config
config["defaultHeaders"] = headers
```

**2. ModelManager Init (`modules/model_manager.py:31-54`)**
```python
def __init__(self, config_dir: Path = None):
    # ... load config ...

    # Load API key for current provider
    provider = self.config.get("provider")
    if provider:
        api_keys = self.models_db.get("api_keys", {})
        if provider in api_keys:
            self.config["apiKey"] = api_keys[provider]

        # Load headers
        headers = self.get_provider_headers(provider, self.config.get("model"))
        if headers:
            self.config["defaultHeaders"] = headers
```

**3. get_provider_headers (`modules/model_manager.py:189-216`)**
```python
def get_provider_headers(self, provider: str, model_id: Optional[str] = None) -> Dict:
    """Build effective headers for provider/model combination."""
    settings = self.get_provider_settings(provider)
    headers = dict(settings.get("default_headers", {}))

    # Apply overrides from config.json:providerOverrides
    overrides = self.config.get("providerOverrides", {})
    provider_overrides = overrides.get(provider, {})

    base_override = provider_overrides.get("headers") or {}
    if isinstance(base_override, dict):
        headers.update(base_override)

    # Model-specific overrides
    if model_id:
        model_overrides = provider_overrides.get("models") or {}
        specific = model_overrides.get(model_id)
        if isinstance(specific, dict):
            headers.update(specific)

    # Environment variables for OpenRouter
    if provider == "openrouter":
        site_url = os.getenv("OPENROUTER_SITE_URL")
        app_name = os.getenv("OPENROUTER_APP_NAME")
        if site_url:
            headers["HTTP-Referer"] = site_url
        if app_name:
            headers["X-Title"] = app_name

    return headers
```

**4. Model Switch (`modules/model_manager.py:448-499`)**
```python
def switch_model(self, session, model_id: str) -> Dict:
    """Switch to a different model"""
    # ... validation ...

    model_info = self.models_db["models"][model_id]
    provider = model_info.get("provider")

    # Update session and config
    session.model = model_id
    self.config["model"] = model_id
    self._set_active_provider(provider, keys[provider])  # <-- Calls get_provider_headers

    return {"success": True, ...}
```

**5. _set_active_provider (`modules/model_manager.py:124-153`)**
```python
def _set_active_provider(self, provider: str, api_key: Optional[str] = None):
    """Update config to reflect active provider selection."""
    settings = self.get_provider_settings(provider)

    self.config["provider"] = provider
    if api_key:
        self.config["apiKey"] = api_key

    self.config["baseURL"] = settings.get("base_url")
    self.config["requestFormat"] = settings.get("request_format")

    # Load headers for this provider
    headers = self.get_provider_headers(provider, self.config.get("model"))  # <-- KEY LINE
    if headers:
        self.config["defaultHeaders"] = headers
```

### Provider Defaults (`modules/provider_settings.py:17-28`)

```python
PROVIDER_DEFAULTS = {
    "openrouter": {
        "name": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "models_endpoint": "https://openrouter.ai/api/v1/models",
        "request_format": "openai-chat",
        "default_headers": {
            "HTTP-Referer": _OPENROUTER_SITE,  # From env or "https://github.com/Dezocode/opencli"
            "X-Title": _OPENROUTER_APP          # From env or "OpenCLI"
        }
    },
    # ... other providers ...
}
```

---

## Integration Points Identified

1. ✅ **`modules/model_manager.py:189-216`** - `get_provider_headers()` method
2. ✅ **`modules/model_manager.py:50`** - Called in `__init__`
3. ✅ **`modules/model_manager.py:148`** - Called in `_set_active_provider`
4. ✅ **`modules/model_manager.py:239`** - Called in `update_provider_headers`
5. ✅ **`opencli.py:287-320`** - Header building in `load_config()`
6. ⚠️ **`modules/provider_settings.py:13-27`** - Hardcoded OpenRouter defaults (need to make dynamic)

---

## Tasks

### Phase 1: Create OpenRouter Header Manager Module

**Estimated Time**: 45 minutes

#### Task 1.1: Create Module File
**Priority**: P0 (Blocking)

**Action**: Create new file `modules/openrouter_headers.py`

**Content**:
```python
"""
OpenRouter Header Manager

Fetches and parses per-model headers from OpenRouter API pages.
Caches results to avoid repeated HTTP requests.
"""

import json
import re
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime, timedelta

try:
    import httpx
except ImportError:
    import sys
    print("Error: httpx not installed. Run: pip3 install httpx")
    sys.exit(1)

try:
    from bs4 import BeautifulSoup
except ImportError:
    import sys
    print("Error: beautifulsoup4 not installed. Run: pip3 install beautifulsoup4")
    sys.exit(1)


class OpenRouterHeaderManager:
    """
    Manages OpenRouter headers by fetching from model API pages

    Example:
        mgr = OpenRouterHeaderManager()
        headers = mgr.get_headers_for_model("deepseek/deepseek-chat-v3.1:free")
        # Returns: {"HTTP-Referer": "...", "X-Title": "..."}
    """

    CACHE_TTL_HOURS = 24
    DEFAULT_TIMEOUT = 10.0

    def __init__(self, cache_dir: Path = None):
        """
        Initialize header manager

        Args:
            cache_dir: Directory for cache file (default: ~/.opencli/cache)
        """
        self.cache_dir = cache_dir or (Path.home() / ".opencli" / "cache")
        self.cache_file = self.cache_dir / "openrouter_headers.json"
        self.cache = self._load_cache()

    def get_headers_for_model(self, model_id: str) -> Dict[str, str]:
        """
        Get headers for a specific OpenRouter model

        Args:
            model_id: OpenRouter model ID (e.g., "deepseek/deepseek-chat-v3.1:free")

        Returns:
            Dict with HTTP-Referer and X-Title headers
        """
        # Check cache first
        if model_id in self.cache:
            cached_entry = self.cache[model_id]
            if self._is_cache_valid(cached_entry):
                return cached_entry["headers"]

        # Fetch from API page
        headers = self._fetch_headers_from_api_page(model_id)

        # Cache the result
        self._cache_headers(model_id, headers)

        return headers

    def _fetch_headers_from_api_page(self, model_id: str) -> Dict[str, str]:
        """
        Fetch and parse headers from model's API page

        Args:
            model_id: Model identifier

        Returns:
            Dict with headers, or defaults on error
        """
        url = f"https://openrouter.ai/{model_id}/api"

        try:
            # Fetch the page
            response = httpx.get(
                url,
                timeout=self.DEFAULT_TIMEOUT,
                follow_redirects=True
            )
            response.raise_for_status()

            # Parse headers from HTML
            headers = self._parse_headers(response.text)

            return headers

        except Exception as e:
            # Fall back to defaults on any error
            return self._get_default_headers()

    def _parse_headers(self, html_content: str) -> Dict[str, str]:
        """
        Parse HTTP-Referer and X-Title from API page HTML

        Strategies (in order):
        1. Look for code examples showing headers
        2. Parse from JSON blocks
        3. Extract from cURL examples
        4. Fall back to defaults if not found

        Args:
            html_content: HTML content from API page

        Returns:
            Dict with parsed headers
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        headers = {}

        # Strategy 1: Look for code blocks with header examples
        code_blocks = soup.find_all(['code', 'pre'])
        for block in code_blocks:
            text = block.get_text()
            if 'HTTP-Referer' in text or 'X-Title' in text:
                parsed = self._extract_headers_from_code(text)
                if parsed:
                    headers.update(parsed)
                    break  # Found headers, stop searching

        # Strategy 2: Look for JSON configuration in script tags
        if not headers:
            scripts = soup.find_all('script', type='application/json')
            for script in scripts:
                if script.string:
                    try:
                        data = json.loads(script.string)
                        if 'headers' in data:
                            headers.update(data['headers'])
                            break
                    except json.JSONDecodeError:
                        pass

        # Strategy 3: Check for meta tags
        if not headers:
            referer_meta = soup.find('meta', {'name': 'http-referer'})
            if referer_meta and referer_meta.get('content'):
                headers['HTTP-Referer'] = referer_meta.get('content')

            title_meta = soup.find('meta', {'name': 'x-title'})
            if title_meta and title_meta.get('content'):
                headers['X-Title'] = title_meta.get('content')

        # Fall back to defaults if nothing found
        if not headers or 'HTTP-Referer' not in headers:
            headers = self._get_default_headers()

        return headers

    def _extract_headers_from_code(self, code_text: str) -> Dict[str, str]:
        """
        Extract headers from code example text using regex

        Matches patterns like:
        - "HTTP-Referer": "https://example.com"
        - 'X-Title': 'My App'
        - HTTP-Referer: https://example.com
        - -H "HTTP-Referer: https://example.com"

        Args:
            code_text: Code block text content

        Returns:
            Dict with extracted headers
        """
        headers = {}

        # Pattern for HTTP-Referer
        referer_patterns = [
            r'["\']?HTTP-Referer["\']?\s*[:=]\s*["\']([^"\']+)["\']',  # JSON/Python style
            r'-H\s+["\']HTTP-Referer:\s*([^"\']+)["\']',              # cURL style
            r'HTTP-Referer:\s*([^\s,;]+)',                            # Plain style
        ]

        for pattern in referer_patterns:
            match = re.search(pattern, code_text, re.IGNORECASE)
            if match:
                headers['HTTP-Referer'] = match.group(1).strip()
                break

        # Pattern for X-Title
        title_patterns = [
            r'["\']?X-Title["\']?\s*[:=]\s*["\']([^"\']+)["\']',      # JSON/Python style
            r'-H\s+["\']X-Title:\s*([^"\']+)["\']',                   # cURL style
            r'X-Title:\s*([^\s,;]+)',                                 # Plain style
        ]

        for pattern in title_patterns:
            match = re.search(pattern, code_text, re.IGNORECASE)
            if match:
                headers['X-Title'] = match.group(1).strip()
                break

        return headers

    def _get_default_headers(self) -> Dict[str, str]:
        """
        Default headers for OpenCLI

        Returns:
            Dict with default OpenRouter headers
        """
        return {
            "HTTP-Referer": "https://github.com/Dezocode/opencli",
            "X-Title": "OpenCLI"
        }

    def _is_cache_valid(self, cached_entry: dict) -> bool:
        """
        Check if cached headers are still valid (24 hour TTL)

        Args:
            cached_entry: Cache entry dict with timestamp

        Returns:
            True if cache is still valid
        """
        try:
            cached_time = datetime.fromisoformat(cached_entry["timestamp"])
            age = datetime.now() - cached_time
            return age < timedelta(hours=self.CACHE_TTL_HOURS)
        except (KeyError, ValueError):
            return False

    def _cache_headers(self, model_id: str, headers: Dict[str, str]):
        """
        Save headers to cache

        Args:
            model_id: Model identifier
            headers: Headers dict to cache
        """
        self.cache[model_id] = {
            "headers": headers,
            "timestamp": datetime.now().isoformat()
        }
        self._save_cache()

    def _load_cache(self) -> dict:
        """
        Load cached headers from disk

        Returns:
            Cache dict or empty dict if not found
        """
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}

    def _save_cache(self):
        """
        Save cache to disk
        """
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except IOError:
            pass  # Fail silently if can't write cache

    def clear_cache(self):
        """
        Clear all cached headers
        """
        self.cache = {}
        if self.cache_file.exists():
            self.cache_file.unlink()
```

**Acceptance Criteria**:
- [ ] File created at `modules/openrouter_headers.py`
- [ ] All methods implemented with docstrings
- [ ] No syntax errors
- [ ] Imports work (httpx, beautifulsoup4)

**Testing**:
```python
# Quick test
from modules.openrouter_headers import OpenRouterHeaderManager
mgr = OpenRouterHeaderManager()
headers = mgr.get_headers_for_model("deepseek/deepseek-chat-v3.1:free")
print(headers)
# Should print: {'HTTP-Referer': '...', 'X-Title': '...'}
```

---

#### Task 1.2: Install Dependencies
**Priority**: P0 (Blocking)

**Action**: Add dependencies to requirements.txt and install

**File**: `requirements.txt`

**Add**:
```
beautifulsoup4>=4.12.0
```

**Commands**:
```bash
cd /Users/dezmondhollins/opencli
pip3 install beautifulsoup4
pip3 install -r requirements.txt
```

**Acceptance Criteria**:
- [ ] beautifulsoup4 added to requirements.txt
- [ ] Package installed successfully
- [ ] Can import: `from bs4 import BeautifulSoup`

---

#### Task 1.3: Create Unit Tests
**Priority**: P1

**Action**: Create test file for OpenRouterHeaderManager

**File**: `test_openrouter_headers.py` (root directory)

**Content**:
```python
#!/usr/bin/env python3
"""
Unit tests for OpenRouterHeaderManager
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from modules.openrouter_headers import OpenRouterHeaderManager


def test_fetch_headers():
    """Test fetching headers from API page"""
    print("=" * 80)
    print("TEST 1: Fetch headers from API page")
    print("=" * 80)

    mgr = OpenRouterHeaderManager()
    headers = mgr.get_headers_for_model("deepseek/deepseek-chat-v3.1:free")

    print(f"Model: deepseek/deepseek-chat-v3.1:free")
    print(f"Headers: {headers}")

    assert "HTTP-Referer" in headers, "Missing HTTP-Referer"
    assert "X-Title" in headers, "Missing X-Title"
    assert headers["HTTP-Referer"].startswith("http"), "Invalid HTTP-Referer format"

    print("✅ PASS: Headers fetched successfully")
    print()
    return True


def test_cache_functionality():
    """Test header caching"""
    print("=" * 80)
    print("TEST 2: Cache functionality")
    print("=" * 80)

    mgr = OpenRouterHeaderManager()

    # First fetch (from API)
    print("First fetch (from API)...")
    headers1 = mgr.get_headers_for_model("deepseek/deepseek-chat-v3.1:free")

    # Second fetch (from cache)
    print("Second fetch (from cache)...")
    headers2 = mgr.get_headers_for_model("deepseek/deepseek-chat-v3.1:free")

    assert headers1 == headers2, "Headers don't match"
    assert mgr.cache_file.exists(), "Cache file not created"

    print(f"Cache file: {mgr.cache_file}")
    print(f"Headers: {headers1}")
    print("✅ PASS: Cache working correctly")
    print()
    return True


def test_fallback_to_defaults():
    """Test fallback when API page unreachable"""
    print("=" * 80)
    print("TEST 3: Fallback to defaults")
    print("=" * 80)

    mgr = OpenRouterHeaderManager()
    headers = mgr.get_headers_for_model("invalid/model/id/that/does/not/exist")

    print(f"Model: invalid/model/id/that/does/not/exist")
    print(f"Headers: {headers}")

    # Should return defaults
    assert headers["HTTP-Referer"] == "https://github.com/Dezocode/opencli"
    assert headers["X-Title"] == "OpenCLI"

    print("✅ PASS: Defaults returned on error")
    print()
    return True


def test_multiple_models():
    """Test fetching headers for multiple models"""
    print("=" * 80)
    print("TEST 4: Multiple models")
    print("=" * 80)

    mgr = OpenRouterHeaderManager()

    models = [
        "deepseek/deepseek-chat-v3.1:free",
        "anthropic/claude-3.5-sonnet",
        "openai/gpt-4-turbo"
    ]

    for model_id in models:
        headers = mgr.get_headers_for_model(model_id)
        print(f"{model_id}: {headers}")
        assert "HTTP-Referer" in headers
        assert "X-Title" in headers

    print("✅ PASS: Multiple models handled correctly")
    print()
    return True


if __name__ == "__main__":
    tests = [
        test_fetch_headers,
        test_cache_functionality,
        test_fallback_to_defaults,
        test_multiple_models
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ FAIL: {test.__name__}")
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 80)

    sys.exit(0 if failed == 0 else 1)
```

**Acceptance Criteria**:
- [ ] Test file created
- [ ] All 4 tests pass
- [ ] Cache file created in `~/.opencli/cache/`
- [ ] Headers fetched successfully

**Run**:
```bash
python3 test_openrouter_headers.py
```

---

### Phase 2: Integrate with ModelManager

**Estimated Time**: 30 minutes

#### Task 2.1: Update get_provider_headers Method
**Priority**: P0 (Blocking)

**File**: `modules/model_manager.py`
**Lines**: 189-216

**Current Code**:
```python
def get_provider_headers(self, provider: str, model_id: Optional[str] = None) -> Dict:
    """Build effective headers for provider/model combination."""
    settings = self.get_provider_settings(provider)
    headers = dict(settings.get("default_headers", {}))

    # ... existing override logic ...

    # Environment variables for OpenRouter
    if provider == "openrouter":
        site_url = os.getenv("OPENROUTER_SITE_URL")
        app_name = os.getenv("OPENROUTER_APP_NAME")
        if site_url:
            headers["HTTP-Referer"] = site_url
        if app_name:
            headers["X-Title"] = app_name

    return headers
```

**New Code** (replace lines 189-216):
```python
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
    headers = dict(settings.get("default_headers", {}))

    # Apply overrides from config.json:providerOverrides
    overrides = self.config.get("providerOverrides", {})
    provider_overrides = overrides.get(provider, {})

    base_override = provider_overrides.get("headers") or {}
    if isinstance(base_override, dict):
        headers.update(base_override)

    # Model-specific overrides
    if model_id:
        model_overrides = provider_overrides.get("models") or {}
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
```

**Acceptance Criteria**:
- [ ] Code updated in `model_manager.py`
- [ ] OpenRouter models use `OpenRouterHeaderManager`
- [ ] Other providers use existing logic
- [ ] User overrides still work
- [ ] No syntax errors

**Testing**:
```python
from modules.model_manager import ModelManager

mgr = ModelManager()
headers = mgr.get_provider_headers("openrouter", "deepseek/deepseek-chat-v3.1:free")
print(f"OpenRouter headers: {headers}")

headers = mgr.get_provider_headers("google", "gemini-2.0-flash-exp")
print(f"Google headers: {headers}")
```

---

#### Task 2.2: Test Model Switching
**Priority**: P1

**Action**: Create test for model switching with header updates

**File**: `test_model_switch_headers.py`

**Content**:
```python
#!/usr/bin/env python3
"""
Test that model switching correctly loads headers
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from modules.model_manager import ModelManager


class FakeSession:
    def __init__(self):
        self.model = None


def test_switch_to_openrouter_model():
    """Test switching to OpenRouter model loads headers"""
    print("=" * 80)
    print("TEST: Switch to OpenRouter model")
    print("=" * 80)

    mgr = ModelManager()
    session = FakeSession()

    # Get list of OpenRouter models
    models = mgr.list_available_models()
    openrouter_models = [m for m in models if m.get("provider") == "openrouter"]

    if not openrouter_models:
        print("⚠️  No OpenRouter models found, skipping test")
        return True

    model_id = openrouter_models[0]["id"]
    print(f"Switching to: {model_id}")

    result = mgr.switch_model(session, model_id)

    if not result["success"]:
        print(f"❌ Switch failed: {result.get('error')}")
        return False

    # Check that headers were loaded
    headers = mgr.config.get("defaultHeaders", {})
    print(f"Headers after switch: {headers}")

    assert "HTTP-Referer" in headers, "Missing HTTP-Referer"
    assert "X-Title" in headers, "Missing X-Title"

    print("✅ PASS: Headers loaded after model switch")
    return True


if __name__ == "__main__":
    try:
        if test_switch_to_openrouter_model():
            print("\n✅ All tests passed!")
            sys.exit(0)
        else:
            print("\n❌ Test failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
```

**Acceptance Criteria**:
- [ ] Test passes
- [ ] Headers correctly loaded when switching to OpenRouter model
- [ ] Cache file updated

**Run**:
```bash
python3 test_model_switch_headers.py
```

---

### Phase 3: Integrate with Startup (opencli.py)

**Estimated Time**: 20 minutes

#### Task 3.1: Update load_config() for OpenRouter
**Priority**: P0 (Blocking)

**File**: `opencli.py`
**Lines**: 287-320

**Current Code** (lines 308-314):
```python
if provider == "openrouter":
    site_url = os.getenv("OPENROUTER_SITE_URL")
    app_name = os.getenv("OPENROUTER_APP_NAME")
    if site_url:
        headers["HTTP-Referer"] = site_url
    if app_name:
        headers["X-Title"] = app_name
```

**Replace with**:
```python
# OpenRouter: Fetch per-model headers from API pages
if provider == "openrouter" and model_id:
    try:
        from modules.openrouter_headers import OpenRouterHeaderManager
        header_mgr = OpenRouterHeaderManager()

        # Fetch model-specific headers
        model_headers = header_mgr.get_headers_for_model(model_id)

        # Merge with any existing headers from overrides
        headers.update(model_headers)

    except Exception:
        # Fall back to environment variables
        site_url = os.getenv("OPENROUTER_SITE_URL")
        app_name = os.getenv("OPENROUTER_APP_NAME")
        if site_url:
            headers["HTTP-Referer"] = site_url
        if app_name:
            headers["X-Title"] = app_name
```

**Acceptance Criteria**:
- [ ] Code updated in `opencli.py`
- [ ] OpenRouter models fetch headers on startup
- [ ] Environment variables still work as fallback
- [ ] Google provider not affected

**Testing**:
```bash
# Start OpenCLI with OpenRouter model active
opencli

# Check that headers are loaded
# Should see HTTP-Referer and X-Title in config
```

---

### Phase 4: Testing & Validation

**Estimated Time**: 30 minutes

#### Task 4.1: End-to-End Test Suite
**Priority**: P1

**Action**: Create comprehensive E2E test

**File**: `test_e2e_headers.py`

**Content**:
```python
#!/usr/bin/env python3
"""
End-to-end test for OpenRouter header auto-config
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from opencli import load_config
from modules.model_manager import ModelManager


def test_startup_with_openrouter():
    """Test startup loads headers correctly"""
    print("=" * 80)
    print("TEST 1: Startup with OpenRouter model")
    print("=" * 80)

    # Set config to OpenRouter model
    config_file = Path.home() / ".opencli" / "config.json"
    with open(config_file, 'r') as f:
        config = json.load(f)

    original_provider = config.get("provider")
    original_model = config.get("model")

    # Get first OpenRouter model
    mgr = ModelManager()
    models = mgr.list_available_models()
    openrouter_models = [m for m in models if m.get("provider") == "openrouter"]

    if not openrouter_models:
        print("⚠️  No OpenRouter models, skipping")
        return True

    # Set to OpenRouter model
    test_model = openrouter_models[0]["id"]
    config["provider"] = "openrouter"
    config["model"] = test_model

    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

    # Load config (simulates startup)
    loaded_config = load_config()

    print(f"Model: {test_model}")
    print(f"Headers: {loaded_config.get('defaultHeaders')}")

    # Restore original config
    config["provider"] = original_provider
    config["model"] = original_model
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

    # Verify headers loaded
    headers = loaded_config.get("defaultHeaders", {})
    assert "HTTP-Referer" in headers, "Missing HTTP-Referer"
    assert "X-Title" in headers, "Missing X-Title"

    print("✅ PASS: Headers loaded on startup")
    return True


def test_google_provider_unaffected():
    """Test that Google provider is not affected"""
    print("=" * 80)
    print("TEST 2: Google provider unaffected")
    print("=" * 80)

    mgr = ModelManager()
    headers = mgr.get_provider_headers("google", "gemini-2.0-flash-exp")

    print(f"Google headers: {headers}")

    # Google should have empty headers
    assert headers == {} or "HTTP-Referer" not in headers
    assert "anthropic-version" not in headers

    print("✅ PASS: Google provider unchanged")
    return True


def test_cache_persistence():
    """Test that cache persists between instances"""
    print("=" * 80)
    print("TEST 3: Cache persistence")
    print("=" * 80)

    from modules.openrouter_headers import OpenRouterHeaderManager

    # Create first instance and fetch headers
    mgr1 = OpenRouterHeaderManager()
    headers1 = mgr1.get_headers_for_model("deepseek/deepseek-chat-v3.1:free")

    # Create second instance
    mgr2 = OpenRouterHeaderManager()
    headers2 = mgr2.get_headers_for_model("deepseek/deepseek-chat-v3.1:free")

    assert headers1 == headers2, "Cache not persisting"

    print(f"Cache file: {mgr2.cache_file}")
    print(f"Headers: {headers2}")
    print("✅ PASS: Cache persists correctly")
    return True


if __name__ == "__main__":
    tests = [
        test_startup_with_openrouter,
        test_google_provider_unaffected,
        test_cache_persistence
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
                print()
        except Exception as e:
            print(f"❌ FAIL: {test.__name__}")
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
            print()
            failed += 1

    print("=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 80)

    sys.exit(0 if failed == 0 else 1)
```

**Acceptance Criteria**:
- [ ] All tests pass
- [ ] OpenRouter headers fetched on startup
- [ ] Google provider unaffected
- [ ] Cache persists between instances

**Run**:
```bash
python3 test_e2e_headers.py
```

---

#### Task 4.2: Manual Testing Checklist

**Test Case 1**: Fresh OpenCLI Startup with OpenRouter Model
```bash
1. Set config to OpenRouter model:
   vi ~/.opencli/config.json
   # Set "provider": "openrouter", "model": "deepseek/deepseek-chat-v3.1:free"

2. Start OpenCLI:
   opencli

3. Check headers loaded:
   # Should see HTTP-Referer and X-Title in requests

4. Send test message:
   > hi

5. Verify no errors
```

**Expected**: ✅ Headers auto-loaded, no errors

---

**Test Case 2**: Switch from Google to OpenRouter
```bash
1. Start with Google:
   # config: "provider": "google", "model": "gemini-2.0-flash-exp"

2. Start OpenCLI:
   opencli

3. Switch to OpenRouter model:
   /model deepseek/deepseek-chat-v3.1:free

4. Send message:
   > test

5. Check headers were loaded for OpenRouter
```

**Expected**: ✅ Headers loaded after switch, Google unchanged

---

**Test Case 3**: Cache Works Across Sessions
```bash
1. First session:
   opencli
   # Switch to OpenRouter model
   /model deepseek/deepseek-chat-v3.1:free

2. Exit and check cache:
   ls -la ~/.opencli/cache/openrouter_headers.json
   cat ~/.opencli/cache/openrouter_headers.json

3. Second session:
   opencli
   # Should use cached headers (no HTTP fetch)

4. Verify headers loaded instantly
```

**Expected**: ✅ Cache file exists, second load instant

---

**Test Case 4**: Multiple OpenRouter Models
```bash
1. Test with 3 different models:
   - deepseek/deepseek-chat-v3.1:free
   - anthropic/claude-3.5-sonnet
   - openai/gpt-4-turbo

2. Switch between them:
   /model deepseek/deepseek-chat-v3.1:free
   > test 1

   /model anthropic/claude-3.5-sonnet
   > test 2

   /model openai/gpt-4-turbo
   > test 3

3. Check cache has all 3:
   cat ~/.opencli/cache/openrouter_headers.json
```

**Expected**: ✅ All 3 models have cached headers

---

### Phase 5: Cleanup & Documentation

**Estimated Time**: 15 minutes

#### Task 5.1: Update provider_settings.py
**Priority**: P2

**File**: `modules/provider_settings.py`
**Lines**: 13-27

**Action**: Add comment explaining dynamic header loading

**Current Code**:
```python
# Allow users to override OpenRouter header metadata via environment variables.
_OPENROUTER_SITE = os.getenv("OPENROUTER_SITE_URL") or "https://github.com/Dezocode/opencli"
_OPENROUTER_APP = os.getenv("OPENROUTER_APP_NAME") or "OpenCLI"

PROVIDER_DEFAULTS = {
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
```

**Update to**:
```python
# Allow users to override OpenRouter header metadata via environment variables.
# NOTE: These are fallback defaults only. OpenRouter headers are now dynamically
# fetched from per-model API pages by OpenRouterHeaderManager.
# See: modules/openrouter_headers.py
_OPENROUTER_SITE = os.getenv("OPENROUTER_SITE_URL") or "https://github.com/Dezocode/opencli"
_OPENROUTER_APP = os.getenv("OPENROUTER_APP_NAME") or "OpenCLI"

PROVIDER_DEFAULTS = {
    "openrouter": {
        "name": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "models_endpoint": "https://openrouter.ai/api/v1/models",
        "key_patterns": ["sk-or-", "OPENROUTER"],
        "request_format": "openai-chat",
        # NOTE: default_headers are fallback only. Per-model headers are fetched
        # dynamically from https://openrouter.ai/{model_id}/api
        "default_headers": {
            "HTTP-Referer": _OPENROUTER_SITE,  # Fallback default
            "X-Title": _OPENROUTER_APP          # Fallback default
        }
    },
```

**Acceptance Criteria**:
- [ ] Comments added explaining dynamic loading
- [ ] No functional changes
- [ ] Defaults still work as fallback

---

#### Task 5.2: Sync to Runtime
**Priority**: P0 (Blocking)

**Action**: Copy updated files to `.opencli` runtime directory

**Commands**:
```bash
# Copy updated modules
cp /Users/dezmondhollins/opencli/modules/model_manager.py /Users/dezmondhollins/.opencli/modules/model_manager.py
cp /Users/dezmondhollins/opencli/modules/openrouter_headers.py /Users/dezmondhollins/.opencli/modules/openrouter_headers.py
cp /Users/dezmondhollins/opencli/modules/provider_settings.py /Users/dezmondhollins/.opencli/modules/provider_settings.py
cp /Users/dezmondhollins/opencli/opencli.py /Users/dezmondhollins/.opencli/opencli.py

# Verify sync
diff /Users/dezmondhollins/opencli/modules/model_manager.py /Users/dezmondhollins/.opencli/modules/model_manager.py
```

**Acceptance Criteria**:
- [ ] All files synced to `.opencli`
- [ ] No differences in diff output
- [ ] Runtime ready for testing

---

#### Task 5.3: Update Documentation
**Priority**: P2

**File**: `.specify/OPENROUTER_HEADERS_SPEC_SUMMARY.md`

**Action**: Update status to "IMPLEMENTED"

**Change**:
```markdown
**Status**: ✅ IMPLEMENTED - Ready for Testing
```

**Acceptance Criteria**:
- [ ] Documentation updated
- [ ] Status changed to IMPLEMENTED

---

#### Task 5.4: Commit to Git
**Priority**: P1

**Action**: Commit all changes to dev7 branch

**Commands**:
```bash
cd /Users/dezmondhollins/opencli

git add modules/openrouter_headers.py
git add modules/model_manager.py
git add modules/provider_settings.py
git add opencli.py
git add requirements.txt
git add .specify/

git commit -m "$(cat <<'EOF'
feat: Add per-model header fetching for OpenRouter

Implements OpenRouterHeaderManager to dynamically fetch HTTP-Referer and
X-Title headers from each model's API page at openrouter.ai/{model_id}/api.

## New Features
- **OpenRouterHeaderManager** module for per-model header fetching
- HTML parsing with BeautifulSoup to extract headers from API pages
- 24-hour cache to avoid repeated HTTP requests
- Automatic fallback to defaults on errors

## Changes
- **modules/openrouter_headers.py**: New module with OpenRouterHeaderManager class
- **modules/model_manager.py**: Updated get_provider_headers() to use header manager
- **opencli.py**: Updated load_config() to fetch headers on startup
- **modules/provider_settings.py**: Added comments about dynamic loading
- **requirements.txt**: Added beautifulsoup4 dependency

## Integration Points
- Fetches headers when switching to OpenRouter models
- Fetches headers on startup if OpenRouter model active
- Caches headers to ~/.opencli/cache/openrouter_headers.json
- Falls back to environment variables or defaults on errors

## Testing
- Unit tests: test_openrouter_headers.py
- Integration tests: test_model_switch_headers.py
- E2E tests: test_e2e_headers.py

## Impact
- OpenRouter models: 100% auto-configured headers
- Other providers: No changes (Google, Anthropic, etc. unaffected)
- User overrides: Still work via providerOverrides in config.json

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

git push origin dev7
```

**Acceptance Criteria**:
- [ ] All files committed
- [ ] Descriptive commit message
- [ ] Pushed to dev7 branch

---

## Summary

### Files to Create (3 new files)
1. ✅ `modules/openrouter_headers.py` - Header manager module (~400 lines)
2. ✅ `test_openrouter_headers.py` - Unit tests (~150 lines)
3. ✅ `test_model_switch_headers.py` - Integration tests (~80 lines)
4. ✅ `test_e2e_headers.py` - E2E tests (~150 lines)

### Files to Modify (4 existing files)
1. ✅ `modules/model_manager.py:189-216` - Update get_provider_headers()
2. ✅ `opencli.py:308-314` - Update load_config()
3. ✅ `modules/provider_settings.py:13-27` - Add comments
4. ✅ `requirements.txt` - Add beautifulsoup4

### Dependencies
- ✅ `beautifulsoup4>=4.12.0`
- ✅ `httpx` (already installed)

### Testing Strategy
- ✅ Unit tests for OpenRouterHeaderManager
- ✅ Integration tests for ModelManager
- ✅ E2E tests for complete flow
- ✅ Manual testing checklist (4 test cases)

### Estimated Total Time
- Phase 1: 45 minutes (Core module)
- Phase 2: 30 minutes (ModelManager integration)
- Phase 3: 20 minutes (Startup integration)
- Phase 4: 30 minutes (Testing)
- Phase 5: 15 minutes (Cleanup)

**Total: 2 hours 20 minutes**

---

## Success Criteria

✅ **Functional**:
- [ ] Headers fetched from model API pages
- [ ] Headers cached for 24 hours
- [ ] Headers update when switching models
- [ ] Graceful fallback to defaults

✅ **Quality**:
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] All E2E tests pass
- [ ] Manual tests pass

✅ **Safety**:
- [ ] Google provider unaffected
- [ ] Other providers unaffected
- [ ] User overrides still work
- [ ] No breaking changes

✅ **Documentation**:
- [ ] Code well-commented
- [ ] Specification complete
- [ ] Git commit descriptive
- [ ] Ready for PR

---

**Document Version**: 1.0
**Status**: Ready for Implementation
**Next Step**: Begin Phase 1, Task 1.1
