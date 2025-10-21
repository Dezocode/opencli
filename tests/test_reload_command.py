
import pytest
from textual.pilot import Pilot
from modules.tui.core import OpenCLITUI
from modules.multiline_input import MultiLineInput
from cli.session import Session

@pytest.fixture
def app() -> OpenCLITUI:
    """Return a new instance of the TUI app for testing."""
    session = Session(model='test_model')
    config = {'model': 'test_model'}
    # The TUI needs a message_handler to be set to process input
    app_instance = OpenCLITUI(session=session, config=config)
    
    async def mock_message_handler(user_input, prompt_input):
        # This is a placeholder to handle the message submission
        pass
        
    app_instance.set_message_handler(mock_message_handler)
    return app_instance

@pytest.mark.asyncio
async def test_reload_command_does_not_crash_app(app: OpenCLITUI):
    """
    Test that running the /reload command does not crash the application.
    """
    async with app.run_test() as pilot:
        # Find the input, type the command, and submit
        input_widget = pilot.app.query_one(MultiLineInput)
        input_widget.value = "/reload"
        await pilot.press("enter")
        
        # Wait for the reload to process
        await pilot.pause(2.0)
        
        # Verify the app is still responsive by checking for the input widget
        try:
            updated_input_widget = pilot.app.query_one(MultiLineInput)
            assert updated_input_widget is not None
            # Check if the widget is still part of the active document
            assert updated_input_widget.is_attached
        except Exception as e:
            pytest.fail(f"App became unresponsive or input widget was removed after /reload. Error: {e}")
