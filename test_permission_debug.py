#!/usr/bin/env python3
"""
Debug test for permission buffer display
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
async def test_permission_prompt_debug():
    """Debug test - check if permission_prompt_data gets set"""
    print("\n[TEST] Starting permission prompt debug test")

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
    print(f"[TEST] Got app instance: {app_instance}")

    async with app_instance.run_test() as pilot:
        print("[TEST] Entering run_test context")

        # Get input widget
        input_widget = pilot.app.query_one("#prompt-input", MultiLineInput)
        print(f"[TEST] Got input widget: {input_widget}")
        print(f"[TEST] Initial permission_prompt_data: {input_widget.permission_prompt_data}")

        # Type /help command
        input_widget.value = "/help"
        print(f"[TEST] Set input value to /help")

        # Press enter
        print(f"[TEST] Pressing enter...")
        await pilot.press("enter")
        print(f"[TEST] Enter pressed")

        # Check permission_prompt_data immediately
        print(f"[TEST] Immediately after enter: permission_prompt_data = {input_widget.permission_prompt_data}")

        # Wait a bit
        await pilot.pause(0.1)
        print(f"[TEST] After 0.1s pause: permission_prompt_data = {input_widget.permission_prompt_data}")

        await pilot.pause(0.2)
        print(f"[TEST] After 0.3s total pause: permission_prompt_data = {input_widget.permission_prompt_data}")

        await pilot.pause(0.5)
        print(f"[TEST] After 0.8s total pause: permission_prompt_data = {input_widget.permission_prompt_data}")

        await pilot.pause(1.0)
        print(f"[TEST] After 1.8s total pause: permission_prompt_data = {input_widget.permission_prompt_data}")

        # Final check
        prompt_data = input_widget.permission_prompt_data
        print(f"[TEST] Final permission_prompt_data: {prompt_data}")

        if prompt_data is None:
            print("[TEST] ❌ FAILED: permission_prompt_data is still None")
            assert False, "Permission prompt data was never set"
        else:
            print(f"[TEST] ✅ SUCCESS: Got permission_prompt_data with title: {prompt_data.get('title')}")
            assert 'title' in prompt_data
            assert 'message' in prompt_data
            assert 'options' in prompt_data

    # Cleanup
    startup_task.cancel()
    try:
        await startup_task
    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    asyncio.run(test_permission_prompt_debug())
