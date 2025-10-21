
import pytest
from unittest.mock import AsyncMock, patch
from textual.pilot import Pilot
from modules.tui.core import OpenCLITUI
from modules.multiline_input import MultiLineInput
from cli.session import Session

@pytest.fixture
def app() -> OpenCLITUI:
    """Return a new instance of the TUI app for testing."""
    session = Session(model='test_model')
    config = {'model': 'test_model', 'provider': 'openrouter'}
    app_instance = OpenCLITUI(session=session, config=config)
    return app_instance

@pytest.mark.asyncio
async def test_double_submission_after_reload(app: OpenCLITUI):
    """
    Test that after a /reload command, a subsequent message is only sent once.
    """
    async with app.run_test() as pilot:
        # 1. Set a mock message handler to intercept submissions
        #    This is crucial because the real one is lost during reload.
        submission_handler = AsyncMock()
        app.set_message_handler(submission_handler)

        # 2. Run the /reload command
        input_widget = pilot.app.query_one(MultiLineInput)
        input_widget.value = "/reload"
        await pilot.press("enter")
        await pilot.pause(1.0) # Wait for reload

        # After reload, the original message_handler is gone.
        # We must re-set it on the potentially new app instance.
        # Note: In a real hot-reload, the app object itself might be new.
        # Here we are just reloading the modules within the same app instance.
        app.set_message_handler(submission_handler)

        # 3. Send a regular message
        input_widget = pilot.app.query_one(MultiLineInput)
        input_widget.value = "hi"
        await pilot.press("enter")
        await pilot.pause(0.5)

        # 4. Assert that the message handler was called exactly once
        assert submission_handler.call_count == 1, f"Expected message handler to be called once, but it was called {submission_handler.call_count} times."
        
        # 5. Optional: Check the content of the call
        submission_handler.assert_called_once_with("hi", input_widget)
