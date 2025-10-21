
import pytest
import asyncio
import pytest_asyncio
from unittest.mock import patch

from textual.pilot import Pilot
from modules.tui.core import OpenCLITUI
from modules.multiline_input import MultiLineInput
from cli.session import Session
from modules.async_interactive.core import interactive_async

@pytest_asyncio.fixture
async def configured_app() -> OpenCLITUI:
    """
    Provides a fully configured app instance by running the real startup logic.
    It patches set_message_handler to capture the app instance and run_async to prevent blocking.
    """
    session = Session(model='test_model')
    config = {'model': 'test_model', 'baseURL': 'https://api.example.com/v1'}
    
    app_container = {}
    original_set_message_handler = OpenCLITUI.set_message_handler

    # Define a new set_message_handler that calls the original and captures the instance
    def new_set_message_handler(self, handler):
        app_container['app'] = self  # Capture the instance
        original_set_message_handler(self, handler) # Call the original method

    with patch.object(OpenCLITUI, 'set_message_handler', new_set_message_handler):
        with patch.object(OpenCLITUI, 'run_async', return_value=None):
            startup_task = asyncio.create_task(interactive_async(config, session))
            await asyncio.sleep(0.2) # Allow startup to complete

    assert 'app' in app_container, "Failed to capture app instance during startup."
    app_instance = app_container['app']

    yield app_instance
    
    # Cleanup the startup task
    startup_task.cancel()
    try:
        await startup_task
    except asyncio.CancelledError:
        pass

@pytest.mark.parametrize("command", [
    "/help",
    "/status",
    "/clear",
    "/reload",
    "/exit",
])
@pytest.mark.asyncio
async def test_permission_prompt_display(configured_app: OpenCLITUI, command: str):
    """
    Test that running a command requiring approval correctly populates
    the permission_prompt_data on the MultiLineInput widget.
    """
    async with configured_app.run_test() as pilot:
        # The command router is now initialized by the real startup logic

        # Find the input, type the command, and submit
        input_widget = pilot.app.query_one(MultiLineInput)
        input_widget.value = command
        await pilot.press("enter")
        
        # Wait for the permission prompt to be processed and set
        await pilot.pause(0.5)
        
        # Verify that the permission_prompt_data attribute is now populated
        prompt_data = input_widget.permission_prompt_data
        assert prompt_data is not None, f"Permission prompt data was not set for command: {command}"
        
        # Verify that the data has the expected structure
        assert "title" in prompt_data, f"Prompt for {command} is missing a 'title'"
        assert "message" in prompt_data, f"Prompt for {command} is missing a 'message'"
        assert "options" in prompt_data, f"Prompt for {command} is missing 'options'"
        assert len(prompt_data["options"]) > 0, f"Prompt for {command} has no options"
