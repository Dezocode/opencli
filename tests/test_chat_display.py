
import pytest
from textual.pilot import Pilot
from modules.tui.core import OpenCLITUI
from modules.streaming_display import StreamingDisplay
from cli.session import Session

@pytest.fixture
def app() -> OpenCLITUI:
    """Return a new instance of the TUI app for testing."""
    # Mock session and config
    session = Session(model='test_model')
    config = {'model': 'test_model'}
    return OpenCLITUI(session=session, config=config)

@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_chat_box_loads_and_displays_banner(app: OpenCLITUI):
    """
    Test that the StreamingDisplay widget is present and that the
    welcome banner is written to it on startup.
    """
    async with app.run_test() as pilot:
        # The app composes and mounts, which should trigger the banner write.
        # We give it a brief moment for async operations to complete.
        await pilot.pause()

        # Query for the StreamingDisplay widget
        widgets = pilot.app.query(StreamingDisplay)
        
        # Assert that the widget exists
        assert len(widgets) == 1, "Expected to find one StreamingDisplay widget."
        chat_box = widgets[0]
        assert chat_box.id == "stream-display"

        # Access the internal lines and check the content
        # The banner is written to the `_lines` attribute.
        content = ""
        if chat_box.content_lines:
            # Concatenate the plain text from each line
            content = "".join(line.plain if hasattr(line, 'plain') else str(line) for line in chat_box.content_lines)
        
        # Assert that the welcome banner text is present
        assert "Session:" in content, f"Welcome banner not found in chat box content. Content was: '{content}'"

        # Assert that the widget has a non-zero size
        assert chat_box.size.width > 0, "Chat box width is zero."
        assert chat_box.size.height > 0, "Chat box height is zero."
