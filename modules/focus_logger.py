"""
Focus logging utility for debugging focus issues
Creates a fresh log file on each opencli startup
"""

import os
import datetime
from pathlib import Path

FOCUS_LOG = "/tmp/opencli_focus.log"


def clear_focus_log():
    """Clear focus log file - call on opencli startup"""
    try:
        with open(FOCUS_LOG, 'w') as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            f.write(f"{'='*80}\n")
            f.write(f"OPENCLI FOCUS LOG - Started at {timestamp}\n")
            f.write(f"{'='*80}\n\n")
        return True
    except Exception as e:
        print(f"⚠️ Failed to clear focus log: {e}")
        return False


def log_focus_attempt(source_file: str, source_function: str, method: str,
                      widget_type: str = "unknown", success: bool = None,
                      error: str = None, extra_info: str = None):
    """
    Log a focus attempt with timestamp and details

    Args:
        source_file: File making the focus call (e.g., "widget.py")
        source_function: Function name (e.g., "on_blur", "watch_permission_prompt_data")
        method: Focus method used (e.g., "app.set_focus", "widget.focus", "call_after_refresh")
        widget_type: Type of widget (e.g., "MultiLineInput", "prompt_input")
        success: True if successful, False if failed, None if unknown
        error: Error message if failed
        extra_info: Additional context (e.g., "permission_prompt_data=True")
    """
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        # Determine status emoji
        if success is True:
            status = "✅"
        elif success is False:
            status = "❌"
        else:
            status = "🔄"

        log_entry = f"[{timestamp}] {status} {source_file}::{source_function}()\n"
        log_entry += f"    Method:  {method}\n"
        log_entry += f"    Widget:  {widget_type}\n"

        if extra_info:
            log_entry += f"    Context: {extra_info}\n"

        if error:
            log_entry += f"    Error:   {error}\n"

        log_entry += "\n"

        with open(FOCUS_LOG, 'a') as f:
            f.write(log_entry)
    except Exception as e:
        # Don't let logging errors break the app
        pass


def log_focus_event(source_file: str, source_function: str, event_type: str,
                    widget_type: str = "unknown", extra_info: str = None):
    """
    Log a focus-related event (gained, lost, etc)

    Args:
        source_file: File where event occurred
        source_function: Function handling the event
        event_type: Type of event (e.g., "GAINED_FOCUS", "LOST_FOCUS", "FOCUS_LOCK")
        widget_type: Type of widget
        extra_info: Additional context
    """
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        # Event emoji mapping
        emoji_map = {
            "GAINED_FOCUS": "🎯",
            "LOST_FOCUS": "💨",
            "FOCUS_LOCK": "🔒",
            "FOCUS_UNLOCK": "🔓",
            "PERMISSION_ACTIVE": "⚡",
            "PERMISSION_CLEARED": "✨"
        }
        emoji = emoji_map.get(event_type, "📌")

        log_entry = f"[{timestamp}] {emoji} EVENT: {event_type}\n"
        log_entry += f"    Source:  {source_file}::{source_function}()\n"
        log_entry += f"    Widget:  {widget_type}\n"

        if extra_info:
            log_entry += f"    Context: {extra_info}\n"

        log_entry += "\n"

        with open(FOCUS_LOG, 'a') as f:
            f.write(log_entry)
    except Exception as e:
        # Don't let logging errors break the app
        pass


def log_focus_state(source_file: str, widget_type: str, has_focus: bool,
                    can_focus: bool, is_mounted: bool = None, extra_info: str = None):
    """
    Log current focus state snapshot

    Args:
        source_file: File logging the state
        widget_type: Type of widget
        has_focus: Whether widget currently has focus
        can_focus: Whether widget can receive focus
        is_mounted: Whether widget is mounted
        extra_info: Additional state info
    """
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        log_entry = f"[{timestamp}] 📊 FOCUS STATE: {widget_type}\n"
        log_entry += f"    Source:     {source_file}\n"
        log_entry += f"    has_focus:  {has_focus}\n"
        log_entry += f"    can_focus:  {can_focus}\n"

        if is_mounted is not None:
            log_entry += f"    is_mounted: {is_mounted}\n"

        if extra_info:
            log_entry += f"    Context:    {extra_info}\n"

        log_entry += "\n"

        with open(FOCUS_LOG, 'a') as f:
            f.write(log_entry)
    except Exception as e:
        # Don't let logging errors break the app
        pass


def get_focus_log_path():
    """Return the path to the focus log file"""
    return FOCUS_LOG
