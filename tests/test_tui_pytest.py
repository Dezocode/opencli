
import pytest
from textual.pilot import Pilot
from modules.tui.core import OpenCLITUI
from modules.multiline_input import MultiLineInput

@pytest.fixture
async def pilot() -> Pilot:
    """A textual pilot fixture."""
    app = OpenCLITUI()
    async with app.run_test() as pilot:
        yield pilot

async def test_message_submission(pilot: Pilot):
    """
    Test that typing a message and pressing enter submits it.
    """
    # Get the input widget
    input_widget = pilot.app.query_one(MultiLineInput)
    
    # Simulate typing a message
    input_widget.value = "hello world"
    
    # Simulate pressing enter
    await pilot.press("enter")
    
    # The app should handle the message. We can add assertions here
    # to check if the message was processed correctly. For now, this
    # test verifies that the input and submission process works without crashing.
    
    # For example, we could check if the input is cleared after submission
    assert input_widget.value == ""
