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
