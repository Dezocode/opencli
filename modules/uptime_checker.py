"""
Model Uptime Checker for OpenRouter
Fetches availability status to distinguish between model downtime vs config issues
"""

import json
import re
import html as html_lib
import httpx
import time
from typing import Tuple, Optional, Any


async def check_model_uptime(model_id: str) -> Tuple[bool, Optional[float], str]:
    """
    Check current uptime status for a model

    Args:
        model_id: OpenRouter model ID (e.g., "deepseek/deepseek-chat-v3.1:free")

    Returns:
        Tuple of (success: bool, uptime_percent: float or None, message: str)
        - success: Whether we successfully checked uptime
        - uptime_percent: Current uptime percentage (0-100), or None if unknown
        - message: Human-readable status message
    """
    try:
        # Add timestamp to bust any caching
        timestamp = int(time.time())
        url = f"https://openrouter.ai/{model_id}/uptime?t={timestamp}"

        # Cache-busting headers
        headers = {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)

            if response.status_code != 200:
                return False, None, f"Could not fetch uptime data (HTTP {response.status_code})"

            html = response.text

            # Parse uptime from the page
            uptime = _parse_current_uptime(html)

            if uptime is None:
                # Try parsing from graph data
                uptime = _parse_uptime_from_graph(html)

            if uptime is None:
                return False, None, "Could not parse uptime data from page"

            # Generate status message based on uptime
            message = _get_status_message(uptime)

            return True, uptime, message

    except httpx.TimeoutException:
        return False, None, "Timeout fetching uptime data"
    except Exception as e:
        return False, None, f"Error checking uptime: {str(e)}"


def _parse_current_uptime(html: str) -> Optional[float]:
    """
    Parse current uptime percentage from page text

    Looks for patterns like:
    - "Uptime: 95.2%"
    - "Current uptime: 10%"
    - Live uptime indicators
    """
    # Look for percentage values near "uptime" or "live" indicators
    patterns = [
        r'(?:uptime|live)[^\d]*(\d+(?:\.\d+)?)\s*%',
        r'(\d+(?:\.\d+)?)\s*%[^\d]*(?:uptime|live)',
        r'<div[^>]*uptime[^>]*>.*?(\d+(?:\.\d+)?)\s*%',
        r'Uptime stats[^%]*(\d+(?:\.\d+)?)\s*%',
        r'Last\s*24[hH][^%]*(\d+(?:\.\d+)?)\s*%',
        r'last[-_\s]*24[hH][^%]*(\d+(?:\.\d+)?)\s*%',
        r'aria-label="[^"]*(\d+(?:\.\d+)?)\s*%\s*uptime',
        r'data-uptime[^"\']*["\'](\d+(?:\.\d+)?)\s*%',
    ]

    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                continue

    return None


def _parse_uptime_from_graph(html: str) -> Optional[float]:
    """
    Parse uptime from graph data or metadata

    Looks for:
    - Chart/graph data points
    - Meta tags with uptime info
    - JSON data embedded in page
    """
    # Look for the most recent data point in graph
    # Pattern for data points like: data: [100, 100, 95, 10, 20]
    data_pattern = r'data:\s*\[([\d\s,\.]+)\]'
    match = re.search(data_pattern, html)

    if match:
        try:
            data_str = match.group(1)
            # Get the last value (most recent)
            values = [float(x.strip()) for x in data_str.split(',') if x.strip()]
            if values:
                return values[-1]
        except (ValueError, IndexError):
            pass

    # New chart format: JSON-like data stored in attributes (e.g., data-chart="{...}")
    json_like_pattern = r'data-(?:chart|state|config)="([^"]+)"'
    for attr_match in re.finditer(json_like_pattern, html):
        encoded = attr_match.group(1)
        try:
            decoded = html_lib.unescape(encoded)
            chart_data = json.loads(decoded)
            value = _extract_uptime_from_json(chart_data)
            if value is not None:
                return value
        except Exception:
            continue

    # __NEXT_DATA__ script JSON
    next_match = re.search(r'<script[^>]+id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
    if next_match:
        try:
            payload = html_lib.unescape(next_match.group(1).strip())
            data = json.loads(payload)
            value = _extract_uptime_from_json(data)
            if value is not None:
                return value
        except Exception:
            pass

    # window.__NUXT__ assignment
    nuxt_match = re.search(r'window\.__NUXT__\s*=\s*(\{.*?\});', html, re.DOTALL)
    if nuxt_match:
        try:
            payload = html_lib.unescape(nuxt_match.group(1).strip())
            data = json.loads(payload.rstrip(';'))
            value = _extract_uptime_from_json(data)
            if value is not None:
                return value
        except Exception:
            pass

    # Generic fallback: look for "y": 0.95 values (take last)
    y_values = re.findall(r'"y"\s*:\s*(0?\.\d+|\d+(?:\.\d+)?)', html)
    if y_values:
        try:
            value = float(y_values[-1])
            if value <= 1.0:
                value *= 100.0
            return value
        except ValueError:
            pass

    # Look for JSON or meta data containing uptime percentage
    json_patterns = [
        r'"uptimePercent"\s*:\s*(0?\.\d+|\d+(?:\.\d+)?)',
        r'"uptimePercentage"\s*:\s*(0?\.\d+|\d+(?:\.\d+)?)',
        r'"currentUptime"\s*:\s*(0?\.\d+|\d+(?:\.\d+)?)',
        r'"uptime"\s*:\s*(0?\.\d+|\d+(?:\.\d+)?)',
        r'"last24h"\s*:\s*(0?\.\d+|\d+(?:\.\d+)?)',
        r'"last_24h"\s*:\s*(0?\.\d+|\d+(?:\.\d+)?)',
        r'"uptimeLast24Hours"\s*:\s*(0?\.\d+|\d+(?:\.\d+)?)',
    ]

    for pattern in json_patterns:
        for json_match in re.finditer(pattern, html):
            try:
                value = float(json_match.group(1))
                if value <= 1.0:
                    value *= 100.0
                return value
            except ValueError:
                continue

    # Next.js data payload
    # Look for live badge or indicator
    if re.search(r'<[^>]*(?:class|id)=["\'][^"\']*live[^"\']*["\'][^>]*>', html, re.IGNORECASE):
        live_context = re.search(r'live.*?(\d+(?:\.\d+)?)\s*%', html, re.IGNORECASE | re.DOTALL)
        if live_context:
            try:
                return float(live_context.group(1))
            except ValueError:
                pass

    return None


def _extract_uptime_from_json(data: Any) -> Optional[float]:
    """
    Recursively search JSON data for uptime-related fields.
    """
    key_candidates = [
        "uptime", "uptimePercent", "uptimePercentage",
        "currentUptime", "last24h", "last_24h", "uptimeLast24Hours"
    ]

    def normalize(value: Any) -> Optional[float]:
        if isinstance(value, (int, float)):
            return value * 100.0 if 0.0 <= value <= 1.0 else float(value)
        if isinstance(value, str):
            try:
                parsed = float(value.strip().rstrip('%'))
                if parsed <= 1.0:
                    parsed *= 100.0
                return parsed
            except ValueError:
                return None
        return None

    if isinstance(data, dict):
        for key, value in data.items():
            key_lower = key.lower()
            if any(candidate.lower() in key_lower for candidate in key_candidates):
                normalized = normalize(value)
                if normalized is not None:
                    return normalized
            nested = _extract_uptime_from_json(value)
            if nested is not None:
                return nested
    elif isinstance(data, list):
        for item in data:
            nested = _extract_uptime_from_json(item)
            if nested is not None:
                return nested

    return None


def _get_status_message(uptime: float) -> str:
    """
    Generate human-readable status message based on uptime percentage

    Args:
        uptime: Uptime percentage (0-100)

    Returns:
        Status message string
    """
    if uptime >= 95:
        return f"Model is healthy ({uptime:.1f}% uptime)"
    elif uptime >= 75:
        return f"Model is experiencing minor issues ({uptime:.1f}% uptime)"
    elif uptime >= 50:
        return f"Model is degraded ({uptime:.1f}% uptime)"
    elif uptime >= 25:
        return f"Model is experiencing major issues ({uptime:.1f}% uptime)"
    else:
        return f"Model is mostly unavailable ({uptime:.1f}% uptime)"


def is_model_healthy(uptime: Optional[float]) -> bool:
    """
    Determine if model is healthy enough to attempt requests

    Args:
        uptime: Uptime percentage (0-100), or None if unknown

    Returns:
        True if model is likely healthy, False if clearly down
    """
    if uptime is None:
        # Unknown - assume healthy (don't block on uncertainty)
        return True

    # Consider healthy if uptime is above 50%
    return uptime >= 50.0


def get_user_recommendation(uptime: Optional[float], model_id: str) -> str:
    """
    Get recommendation for user based on uptime status

    Args:
        uptime: Current uptime percentage
        model_id: Model identifier

    Returns:
        Recommendation message
    """
    if uptime is None:
        return "Unable to verify model status. Try the request - if it fails, the model may be down."

    if uptime >= 75:
        return "Model appears healthy. The error is likely due to configuration or settings."

    elif uptime >= 50:
        return f"Model is degraded ({uptime:.1f}% uptime). The error may be temporary. You can:\n  • Wait a few minutes and retry\n  • Try a different model\n  • Check configuration if errors persist"

    else:
        return f"Model is experiencing significant downtime ({uptime:.1f}% uptime).\n\nRecommendation:\n  • Try a different model (e.g., /model to switch)\n  • Check https://openrouter.ai/{model_id}/uptime for status updates\n  • Retry in a few minutes"
