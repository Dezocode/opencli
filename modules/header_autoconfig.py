"""
Header Auto-Configuration for OpenRouter Models
Fetches and parses header requirements from model API example pages
"""

import re
import httpx
from typing import Dict, Optional, Tuple


async def fetch_model_header_config(model_id: str) -> Tuple[bool, Dict[str, str], str]:
    """
    Fetch required headers from model's API example page

    Args:
        model_id: OpenRouter model ID (e.g., "deepseek/deepseek-chat-v3.1:free")

    Returns:
        Tuple of (success: bool, headers: dict, error_message: str)
    """
    try:
        url = f"https://openrouter.ai/{model_id}/api"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)

            if response.status_code != 200:
                return False, {}, f"Failed to fetch model page: HTTP {response.status_code}"

            html = response.text

            # Extract headers from Python example code
            headers = _parse_headers_from_html(html)

            if not headers:
                # Try parsing from other code examples (TypeScript, curl, etc.)
                headers = _parse_headers_fallback(html)

            if not headers:
                return False, {}, "No header configuration found in API examples"

            return True, headers, ""

    except httpx.TimeoutException:
        return False, {}, "Timeout fetching model API page"
    except Exception as e:
        return False, {}, f"Error fetching headers: {str(e)}"


def _parse_headers_from_html(html: str) -> Dict[str, str]:
    """
    Parse headers from Python example in HTML

    Looks for patterns like:
      extra_headers={
        "HTTP-Referer": "<YOUR_SITE_URL>",
        "X-Title": "<YOUR_SITE_NAME>",
      }
    """
    headers = {}

    # Pattern for extra_headers block
    extra_headers_pattern = r'extra_headers=\{([^}]+)\}'
    match = re.search(extra_headers_pattern, html, re.DOTALL)

    if match:
        headers_block = match.group(1)

        # Extract HTTP-Referer
        referer_pattern = r'"HTTP-Referer":\s*"([^"]+)"'
        referer_match = re.search(referer_pattern, headers_block)
        if referer_match:
            value = referer_match.group(1)
            # Skip placeholder values
            if not value.startswith('<') and not value.startswith('YOUR_'):
                headers["HTTP-Referer"] = value
            else:
                # Use default for OpenCLI
                headers["HTTP-Referer"] = "https://github.com/Dezocode/opencli"

        # Extract X-Title
        title_pattern = r'"X-Title":\s*"([^"]+)"'
        title_match = re.search(title_pattern, headers_block)
        if title_match:
            value = title_match.group(1)
            # Skip placeholder values
            if not value.startswith('<') and not value.startswith('YOUR_'):
                headers["X-Title"] = value
            else:
                # Use default for OpenCLI
                headers["X-Title"] = "OpenCLI"

    # If we found the structure but values were placeholders, use defaults
    if match and not headers:
        headers = {
            "HTTP-Referer": "https://github.com/Dezocode/opencli",
            "X-Title": "OpenCLI"
        }

    return headers


def _parse_headers_fallback(html: str) -> Dict[str, str]:
    """
    Fallback parsing for other code example formats (curl, TypeScript, etc.)
    """
    headers = {}

    # Pattern for curl -H headers
    curl_referer = re.search(r'-H\s+["\']HTTP-Referer:\s*([^"\']+)["\']', html)
    curl_title = re.search(r'-H\s+["\']X-Title:\s*([^"\']+)["\']', html)

    if curl_referer:
        value = curl_referer.group(1).strip()
        if not value.startswith('<') and not value.startswith('YOUR_'):
            headers["HTTP-Referer"] = value
        else:
            headers["HTTP-Referer"] = "https://github.com/Dezocode/opencli"

    if curl_title:
        value = curl_title.group(1).strip()
        if not value.startswith('<') and not value.startswith('YOUR_'):
            headers["X-Title"] = value
        else:
            headers["X-Title"] = "OpenCLI"

    # TypeScript/JS pattern
    if not headers:
        ts_pattern = r'headers:\s*\{([^}]+)\}'
        ts_match = re.search(ts_pattern, html, re.DOTALL)

        if ts_match:
            headers_block = ts_match.group(1)

            referer = re.search(r'["\']HTTP-Referer["\']\s*:\s*["\']([^"\']+)["\']', headers_block)
            title = re.search(r'["\']X-Title["\']\s*:\s*["\']([^"\']+)["\']', headers_block)

            if referer:
                value = referer.group(1)
                headers["HTTP-Referer"] = value if not value.startswith('<') else "https://github.com/Dezocode/opencli"

            if title:
                value = title.group(1)
                headers["X-Title"] = value if not value.startswith('<') else "OpenCLI"

    return headers


def get_default_headers() -> Dict[str, str]:
    """
    Get default OpenCLI headers for OpenRouter

    Returns:
        Dict with HTTP-Referer and X-Title
    """
    return {
        "HTTP-Referer": "https://github.com/Dezocode/opencli",
        "X-Title": "OpenCLI"
    }


async def auto_configure_headers(model_id: str, current_headers: Dict[str, str]) -> Tuple[bool, Dict[str, str], str]:
    """
    Auto-configure headers for a model by fetching from API page

    Args:
        model_id: OpenRouter model ID
        current_headers: Current header configuration

    Returns:
        Tuple of (success: bool, new_headers: dict, message: str)
    """
    success, fetched_headers, error = await fetch_model_header_config(model_id)

    if not success:
        # Return defaults if fetch failed
        defaults = get_default_headers()
        return True, defaults, "Using default OpenCLI headers"

    # Merge fetched headers with current (fetched takes precedence)
    new_headers = {**current_headers, **fetched_headers}

    return True, new_headers, f"Auto-configured headers from model API page"
