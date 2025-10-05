"""Utility helpers for normalizing tool call messages before API requests."""

from __future__ import annotations

import uuid
from copy import deepcopy
from typing import Any, Dict, Iterable, List


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
