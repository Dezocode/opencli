#!/usr/bin/env python3
"""
Test to verify custom prompt data is passed to permission buffer
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
async def test_custom_prompt_data_flow():
    """Test that custom prompt data reaches the permission buffer"""

    print("\n[TEST] ========== TESTING CUSTOM PROMPT DATA FLOW ==========")

    # Track custom prompt function calls
    custom_prompt_called = []

    from modules.commands import basic_commands
    original_show_help_prompt = basic_commands.show_help_prompt

    def traced_show_help_prompt(app, session, registration, context):
        print(f"[TRACE] show_help_prompt called")
        result = original_show_help_prompt(app, session, registration, context)
        custom_prompt_called.append(result)
        print(f"[TRACE] show_help_prompt returned: {result}")
        return result

    basic_commands.show_help_prompt = traced_show_help_prompt

    try:
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

        assert 'app' in app_container
        app_instance = app_container['app']

        async with app_instance.run_test() as pilot:
            input_widget = pilot.app.query_one("#prompt-input", MultiLineInput)

            # Type /help and wait for suggestions
            input_widget.value = "/help"
            await pilot.pause(0.5)

            # Press enter
            await pilot.press("enter")

            # Wait for permission buffer
            await pilot.pause(1.0)

            # Check results
            print("\n[TEST] ===== RESULTS =====")
            print(f"[TEST] custom_prompt_called: {len(custom_prompt_called)} times")

            if custom_prompt_called:
                prompt_data = custom_prompt_called[0]
                print(f"[TEST] Prompt data keys: {prompt_data.keys() if prompt_data else 'None'}")
                if prompt_data:
                    print(f"[TEST] Title: {prompt_data.get('title')}")
                    print(f"[TEST] Message: {prompt_data.get('message', '')[:50]}...")
                    print(f"[TEST] Options count: {len(prompt_data.get('options', []))}")
                    if 'options' in prompt_data:
                        for i, opt in enumerate(prompt_data['options']):
                            print(f"[TEST]   Option {i+1}: {opt.get('text')}")

            # Check if permission_prompt_data was set on input widget
            print(f"\n[TEST] input_widget.permission_prompt_data: {input_widget.permission_prompt_data is not None}")
            if input_widget.permission_prompt_data:
                print(f"[TEST] Buffer data title: {input_widget.permission_prompt_data.get('title')}")

            # Verify custom prompt was called
            assert len(custom_prompt_called) > 0, "Custom prompt function was never called!"

            # Verify prompt data has expected structure
            prompt_data = custom_prompt_called[0]
            assert prompt_data is not None, "Custom prompt returned None!"
            assert 'title' in prompt_data, "Prompt data missing 'title'!"
            assert 'message' in prompt_data, "Prompt data missing 'message'!"
            assert 'options' in prompt_data, "Prompt data missing 'options'!"
            assert len(prompt_data['options']) > 0, "Prompt data has no options!"

            print("\n[TEST] ✅ Custom prompt data flow verified!")

        # Cleanup
        startup_task.cancel()
        try:
            await startup_task
        except asyncio.CancelledError:
            pass

    finally:
        # Restore original
        basic_commands.show_help_prompt = original_show_help_prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
