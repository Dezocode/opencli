
import pytest
import asyncio
from textual.pilot import Pilot
from modules.tui.core import OpenCLITUI
from modules.multiline_input import MultiLineInput
from cli.session import Session

@pytest.fixture
def app() -> OpenCLITUI:
    """Return a new instance of the TUI app for testing."""
    session = Session(model='test_model')
    config = {'model': 'test_model'}
    app_instance = OpenCLITUI(session=session, config=config)
    
    async def mock_message_handler(user_input, prompt_input):
        # Simulate work and then finish
        await asyncio.sleep(0.1)
        pass
        
    app_instance.set_message_handler(mock_message_handler)
    return app_instance

@pytest.mark.asyncio
async def test_for_task_leak_on_message_submit(app: OpenCLITUI):
    """
    Test that submitting messages does not leave orphaned asyncio tasks.
    """
    async with app.run_test() as pilot:
        await pilot.pause()
        initial_tasks = set(asyncio.all_tasks())

        # Send the first message
        input_widget = pilot.app.query_one(MultiLineInput)
        input_widget.value = "first message"
        await pilot.press("enter")
        await pilot.pause(0.5) # Allow time for the task to be created and finish

        tasks_after_first = set(asyncio.all_tasks())
        new_tasks_after_first = tasks_after_first - initial_tasks
        # Assert that any new tasks created are temporary and have finished.
        # We check if they are 'done()'. A task that is done is not a leak.
        for task in new_tasks_after_first:
            assert task.done(), f"A new task created after the first message was left running: {task.get_name()}"

        # Send a second message to be sure
        input_widget.value = "second message"
        await pilot.press("enter")
        await pilot.pause(0.5)

        tasks_after_second = set(asyncio.all_tasks())
        new_tasks_after_second = tasks_after_second - tasks_after_first
        for task in new_tasks_after_second:
            assert task.done(), f"A new task created after the second message was left running: {task.get_name()}"
