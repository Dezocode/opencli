"""Utility helpers for normalizing tool call messages before API requests."""

from __future__ import annotations

import json
import re
import uuid
from copy import deepcopy
from typing import Any, Dict, Iterable, List, Optional, Tuple


def normalize_tool_call_messages(messages: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return a sanitized copy of messages with well-formed tool call payloads.

    Some providers reject assistant messages that initiate tool calls if the
    payload is missing required keys (e.g. ``type``) or if ``content`` is
    omitted. We defensively fill those fields to prevent malformed requests.
    """
    normalized: List[Dict[str, Any]] = []

    for original in messages:
        msg = deepcopy(original)

        if msg.get("role") == "assistant" and "tool_calls" in msg:
            # Providers expect an explicit string, not ``None``.
            if msg.get("content") is None:
                msg["content"] = ""

            tool_calls = []
            for call in msg.get("tool_calls") or []:
                if not isinstance(call, dict):
                    # Skip unexpected structures but keep processing others.
                    continue

                call_copy = deepcopy(call)
                call_copy.setdefault("type", "function")
                if not call_copy.get("type"):
                    call_copy["type"] = "function"

                call_copy.setdefault("id", f"call_{uuid.uuid4().hex[:8]}")

                function_payload = call_copy.get("function")
                if not isinstance(function_payload, dict):
                    function_payload = {}

                function_payload.setdefault("name", "")
                function_payload.setdefault("arguments", "")
                call_copy["function"] = function_payload

                tool_calls.append(call_copy)

            msg["tool_calls"] = tool_calls

        # Normalize tool result payloads as well
        if "tool_call_id" in msg:
            if msg.get("role") != "tool":
                msg["role"] = "tool"
            if msg.get("content") is None:
                msg["content"] = ""
            if not msg.get("tool_call_id") and msg.get("id"):
                msg["tool_call_id"] = msg["id"]

        normalized.append(msg)

    return normalized


def extract_tool_calls_from_text(text: str) -> Tuple[Optional[List[Dict[str, Any]]], str]:
    """Extract tool calls embedded in text content.

    Some providers may embed tool calls directly in the response text rather than
    using the structured tool_calls format. This function attempts to extract those
    calls and return them in normalized format.

    Args:
        text: The response text that may contain embedded tool calls

    Returns:
        A tuple of (parsed_tool_calls, cleaned_text) where:
        - parsed_tool_calls: List of tool call dicts or None if no calls found
        - cleaned_text: The text with tool call markup removed
    """
    if not text:
        return None, text

    # Pattern to match common tool call formats like:
    # <tool_call>{"name": "function_name", "arguments": {...}}</tool_call>
    # or XML-style: <tool name="function_name"><args>...</args></tool>

    tool_calls = []
    cleaned_text = text

    # Pattern 1: JSON-style tool calls
    json_pattern = r'<tool_call>(.*?)</tool_call>'
    matches = re.finditer(json_pattern, text, re.DOTALL)

    for match in matches:
        try:
            call_data = json.loads(match.group(1).strip())
            tool_call = {
                "id": f"call_{uuid.uuid4().hex[:8]}",
                "type": "function",
                "function": {
                    "name": call_data.get("name", ""),
                    "arguments": json.dumps(call_data.get("arguments", {}))
                }
            }
            tool_calls.append(tool_call)
            # Remove from text
            cleaned_text = cleaned_text.replace(match.group(0), "")
        except (json.JSONDecodeError, KeyError):
            # If parsing fails, leave the text as-is
            continue

    # Pattern 2: XML-style tool calls
    xml_pattern = r'<tool\s+name="([^"]+)">\s*<args>(.*?)</args>\s*</tool>'
    matches = re.finditer(xml_pattern, cleaned_text, re.DOTALL)

    for match in matches:
        try:
            name = match.group(1)
            args_text = match.group(2).strip()

            # Try to parse args as JSON
            try:
                args = json.loads(args_text)
            except json.JSONDecodeError:
                # If not JSON, treat as plain text
                args = {"content": args_text}

            tool_call = {
                "id": f"call_{uuid.uuid4().hex[:8]}",
                "type": "function",
                "function": {
                    "name": name,
                    "arguments": json.dumps(args)
                }
            }
            tool_calls.append(tool_call)
            # Remove from text
            cleaned_text = cleaned_text.replace(match.group(0), "")
        except Exception:
            continue

    # Clean up extra whitespace
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text).strip()

    return (tool_calls if tool_calls else None), cleaned_text
