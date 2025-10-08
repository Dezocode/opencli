# OpenRouter Headers Auto-Config Implementation Plan

**Date**: 2025-01-08
**Goal**: Parse headers from per-model API pages for 100% reliable auto-configuration
**Status**: 🔧 PLANNING

---

## Overview

Implement a system that automatically fetches and parses OpenRouter model API pages to extract the correct `HTTP-Referer` and `X-Title` headers for each model.

---

## Architecture

### 1. Header Fetcher Module (`modules/openrouter_headers.py`)

New module to handle all OpenRouter header operations:

```python
class OpenRouterHeaderManager:
    """
    Manages OpenRouter headers by fetching from model API pages
    """

    def __init__(self, cache_dir: Path = None):
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
            cached_headers = self.cache[model_id]
            if self._is_cache_valid(cached_headers):
                return cached_headers["headers"]

        # Fetch from API page
        headers = self._fetch_headers_from_api_page(model_id)

        # Cache the result
        self._cache_headers(model_id, headers)

        return headers

    def _fetch_headers_from_api_page(self, model_id: str) -> Dict[str, str]:
        """
        Fetch and parse headers from model's API page
        """
        url = f"https://openrouter.ai/{model_id}/api"

        try:
            # Fetch the page
            response = httpx.get(url, timeout=10.0, follow_redirects=True)
            response.raise_for_status()

            # Parse headers from HTML/JSON
            headers = self._parse_headers(response.text)

            return headers

        except Exception as e:
            # Fall back to defaults
            return self._get_default_headers()

    def _parse_headers(self, html_content: str) -> Dict[str, str]:
        """
        Parse HTTP-Referer and X-Title from API page HTML

        Strategy:
        1. Look for code examples showing headers
        2. Parse from meta tags or JSON blocks
        3. Extract from cURL examples
        4. Fall back to defaults if not found
        """
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        headers = {}

        # Strategy 1: Look for code blocks with header examples
        code_blocks = soup.find_all('code')
        for block in code_blocks:
            text = block.get_text()
            if 'HTTP-Referer' in text or 'X-Title' in text:
                # Parse header values
                headers.update(self._extract_headers_from_code(text))

        # Strategy 2: Look for JSON configuration
        scripts = soup.find_all('script', type='application/json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if 'headers' in data:
                    headers.update(data['headers'])
            except:
                pass

        # Strategy 3: Check for meta tags
        referer_meta = soup.find('meta', {'name': 'http-referer'})
        if referer_meta:
            headers['HTTP-Referer'] = referer_meta.get('content')

        title_meta = soup.find('meta', {'name': 'x-title'})
        if title_meta:
            headers['X-Title'] = title_meta.get('content')

        # Fall back to defaults if nothing found
        if not headers:
            headers = self._get_default_headers()

        return headers

    def _extract_headers_from_code(self, code_text: str) -> Dict[str, str]:
        """
        Extract headers from code example text
        """
        headers = {}

        # Match patterns like:
        # "HTTP-Referer": "https://example.com"
        # 'X-Title': 'My App'
        # HTTP-Referer: https://example.com

        import re

        referer_match = re.search(
            r'["\']?HTTP-Referer["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            code_text
        )
        if referer_match:
            headers['HTTP-Referer'] = referer_match.group(1)

        title_match = re.search(
            r'["\']?X-Title["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            code_text
        )
        if title_match:
            headers['X-Title'] = title_match.group(1)

        return headers

    def _get_default_headers(self) -> Dict[str, str]:
        """
        Default headers for OpenCLI
        """
        return {
            "HTTP-Referer": "https://github.com/Dezocode/opencli",
            "X-Title": "OpenCLI"
        }

    def _is_cache_valid(self, cached_entry: dict) -> bool:
        """
        Check if cached headers are still valid (24 hour TTL)
        """
        from datetime import datetime, timedelta

        cached_time = datetime.fromisoformat(cached_entry["timestamp"])
        return datetime.now() - cached_time < timedelta(hours=24)

    def _cache_headers(self, model_id: str, headers: Dict[str, str]):
        """
        Save headers to cache
        """
        from datetime import datetime

        self.cache[model_id] = {
            "headers": headers,
            "timestamp": datetime.now().isoformat()
        }

        self._save_cache()

    def _load_cache(self) -> dict:
        """
        Load cached headers from disk
        """
        if self.cache_file.exists():
            try:
                with open(self.cache_file) as f:
                    return json.load(f)
            except:
                pass
        return {}

    def _save_cache(self):
        """
        Save cache to disk
        """
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
```

---

## Integration Points

### 1. ModelManager Integration

**File**: `modules/model_manager.py`

Add method to use OpenRouterHeaderManager:

```python
def get_provider_headers(self, provider: str, model_id: Optional[str] = None) -> Dict[str, str]:
    """Get headers for provider, with per-model fetching for OpenRouter"""

    if provider == "openrouter" and model_id:
        # Use OpenRouterHeaderManager for per-model headers
        try:
            from .openrouter_headers import OpenRouterHeaderManager
            header_mgr = OpenRouterHeaderManager()
            return header_mgr.get_headers_for_model(model_id)
        except Exception as e:
            # Fall back to default behavior
            pass

    # Existing logic for other providers or fallback
    provider_defaults = get_provider_defaults(provider)
    headers = dict(provider_defaults.get("default_headers") or {})

    # ... rest of existing logic ...
```

### 2. load_config Integration

**File**: `opencli.py`

Update header loading in `load_config()`:

```python
def load_config():
    # ... existing config loading ...

    # Build effective headers
    if provider == "openrouter" and model_id:
        # Fetch per-model headers
        try:
            from modules.openrouter_headers import OpenRouterHeaderManager
            header_mgr = OpenRouterHeaderManager()
            headers = header_mgr.get_headers_for_model(model_id)
        except Exception:
            # Fall back to existing logic
            headers = dict(provider_defaults.get("default_headers") or {})
    else:
        # Existing logic for non-OpenRouter providers
        headers = dict(provider_defaults.get("default_headers") or {})

    # ... rest of header merging logic ...
```

### 3. Model Switch Integration

**File**: `modules/async_interactive.py`

When switching to OpenRouter model, fetch fresh headers:

```python
# After model switch
if result["success"] and provider == "openrouter":
    # Fetch model-specific headers
    try:
        from .openrouter_headers import OpenRouterHeaderManager
        header_mgr = OpenRouterHeaderManager()
        model_headers = header_mgr.get_headers_for_model(model_id)
        config["defaultHeaders"] = model_headers
        client = create_async_client(config)
    except Exception:
        pass  # Fall back to existing headers
```

---

## Dependencies

Add to `requirements.txt`:
```
beautifulsoup4>=4.12.0  # For HTML parsing
httpx>=0.27.0          # Already used in project
```

---

## Testing Strategy

### Test 1: Header Fetch and Parse
```python
def test_fetch_deepseek_headers():
    mgr = OpenRouterHeaderManager()
    headers = mgr.get_headers_for_model("deepseek/deepseek-chat-v3.1:free")

    assert "HTTP-Referer" in headers
    assert "X-Title" in headers
    assert headers["HTTP-Referer"].startswith("http")
```

### Test 2: Cache Functionality
```python
def test_header_caching():
    mgr = OpenRouterHeaderManager()

    # First fetch (from API)
    headers1 = mgr.get_headers_for_model("deepseek/deepseek-chat-v3.1:free")

    # Second fetch (from cache)
    headers2 = mgr.get_headers_for_model("deepseek/deepseek-chat-v3.1:free")

    assert headers1 == headers2
    assert mgr.cache_file.exists()
```

### Test 3: Fallback to Defaults
```python
def test_fallback_on_error():
    mgr = OpenRouterHeaderManager()
    headers = mgr.get_headers_for_model("invalid/model/id")

    # Should return defaults
    assert headers["HTTP-Referer"] == "https://github.com/Dezocode/opencli"
    assert headers["X-Title"] == "OpenCLI"
```

### Test 4: End-to-End Integration
```python
def test_model_switch_loads_headers():
    # Switch to OpenRouter model
    config = load_config()

    # Should have fetched model-specific headers
    assert "defaultHeaders" in config
    assert "HTTP-Referer" in config["defaultHeaders"]
```

---

## Rollout Plan

### Phase 1: Build Core Module
1. Create `modules/openrouter_headers.py`
2. Implement `OpenRouterHeaderManager` class
3. Add unit tests for header fetching and parsing
4. Test with multiple OpenRouter models

### Phase 2: Integrate with ModelManager
1. Update `ModelManager.get_provider_headers()`
2. Test header loading during model switches
3. Verify cache functionality

### Phase 3: Integrate with load_config
1. Update `opencli.py:load_config()`
2. Test headers on startup with OpenRouter model
3. Verify no impact on other providers

### Phase 4: Testing & Validation
1. Test with 5+ different OpenRouter models
2. Test cache invalidation after 24 hours
3. Test fallback when API page unreachable
4. Test no regression for Google/Anthropic providers

### Phase 5: Cleanup
1. Remove hardcoded OpenRouter headers from `provider_settings.py`
2. Update documentation
3. Add user-facing messages about header auto-config

---

## Success Criteria

- ✅ Headers automatically fetched from model API pages
- ✅ Headers cached to avoid repeated fetches
- ✅ Headers update when switching models
- ✅ Graceful fallback to defaults on errors
- ✅ No impact on non-OpenRouter providers
- ✅ 24-hour cache TTL to keep headers fresh
- ✅ User never needs to manually configure OpenRouter headers

---

**Document Version**: 1.0
**Status**: Ready for Implementation
**Estimated Time**: 2-3 hours
