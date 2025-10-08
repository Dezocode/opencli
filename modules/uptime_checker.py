"""
Model Uptime Checker for OpenRouter
Fetches availability status to distinguish between model downtime vs config issues
"""

import re
import httpx
import time
from typing import Tuple, Optional


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
            "Expires": "0"
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

    # Look for live badge or indicator
    if re.search(r'<[^>]*(?:class|id)=["\'][^"\']*live[^"\']*["\'][^>]*>', html, re.IGNORECASE):
        # If there's a LIVE badge, try to extract nearby percentage
        live_context = re.search(r'live.*?(\d+(?:\.\d+)?)\s*%', html, re.IGNORECASE | re.DOTALL)
        if live_context:
            try:
                return float(live_context.group(1))
            except ValueError:
                pass

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
