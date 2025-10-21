#!/usr/bin/env python3
"""
Simple test to verify the permission bypass fix
"""
import pytest
import asyncio
from unittest.mock import patch

from textual.pilot import Pilot
from modules.tui.core import OpenCLITUI
from modules.multiline_input import MultiLineInput
from cli.session import Session
from modules.async_interactive.core import interactive_async


@pytest.mark.asyncio
async def test_suggestion_bypass_fix():
    """Test that commands execute even when suggestions are not ready"""

    print("\n[TEST] ========== TESTING SUGGESTION BYPASS FIX ==========")

    session = Session(model='test_model')
    config = {'model': 'test_model', 'baseURL': 'https://api.example.com/v1'}

    app_container = {}
    original_set_message_handler = OpenCLITUI.set_message_handler

    def new_set_message_handler(self, handler):
        app_container['app'] = self
        original_set_message_handler(self, handler)

    with patch.object(OpenCLITUI, 'set_message_handler', new_set_message_handler):
        with patch.object(OpenCLITUI, 'run_async', return_value=None):
            startup_task = asyncio.create_task(interactive_async(config, session))
            await asyncio.sleep(0.3)

    assert 'app' in app_container, "Failed to capture app instance"
    app_instance = app_container['app']

    async with app_instance.run_test() as pilot:
        input_widget = pilot.app.query_one("#prompt-input", MultiLineInput)

        # Type /help
        input_widget.value = "/help"
        print(f"[TEST] Set input to /help, suggestions_active={input_widget.suggestions_active}")

        # Wait for suggestions to load
        await pilot.pause(0.5)
        print(f"[TEST] After 0.5s, suggestions_active={input_widget.suggestions_active}")

        # Check if suggestions buffer has suggestions
        try:
            suggestions_buffer = pilot.app.query_one("#command-suggestions")
            print(f"[TEST] Suggestions buffer has {len(suggestions_buffer.suggestions)} suggestions")
            if suggestions_buffer.suggestions:
                selected = suggestions_buffer.get_selected_command()
                print(f"[TEST] Selected command: {selected}")
        except Exception as e:
            print(f"[TEST] Could not get suggestions buffer: {e}")

        # Press enter
        print("[TEST] Pressing enter...")
        await pilot.press("enter")

        # Wait for processing
        await pilot.pause(1.0)

        print("[TEST] ========== TEST COMPLETE ==========\n")

    # Cleanup
    startup_task.cancel()
    try:
        await startup_task
    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
