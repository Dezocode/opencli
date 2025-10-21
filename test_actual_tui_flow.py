"""
Test EXACT TUI flow as it happens in live OpenCLI
Simulates showing permission buffer through MultiLineInput.permission_prompt_data
"""

import pytest
import asyncio
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Static
from modules.multiline_input import MultiLineInput


class ActualTUISimulation(App):
    """Simulate EXACT TUI structure"""

    def __init__(self):
        super().__init__()
        self.prompt_input = None
        self.responses_received = []

    def compose(self) -> ComposeResult:
        """Compose exactly like real TUI"""
        with Container(id="chat-container"):
            yield Static("Chat messages...")

        with Container(id="input-container"):
            self.prompt_input = MultiLineInput(placeholder="Type a message...", id="prompt-input")
            yield self.prompt_input

    def show_permission_prompt_real_way(self, prompt_data: dict):
        """Show permission prompt THE REAL WAY - through MultiLineInput"""
        import sys
        sys.stderr.write("\n[TEST] Showing permission prompt via MultiLineInput.permission_prompt_data\n")
        sys.stderr.flush()

        # This is EXACTLY how the real TUI does it (permission_handlers.py:401-407)
        try:
            prompt_input = self.query_one("#prompt-input")
            prompt_data['selected'] = 0
            prompt_input.permission_prompt_data = prompt_data
            prompt_input.refresh()

            sys.stderr.write(f"[TEST] Set permission_prompt_data: {prompt_data.get('title')}\n")
            sys.stderr.write(f"[TEST] Has options: {len(prompt_data.get('options', []))}\n")
            sys.stderr.flush()

        except Exception as e:
            sys.stderr.write(f"[TEST] ERROR: {e}\n")
            sys.stderr.flush()

    def on_multi_line_input_permission_response(self, event: MultiLineInput.PermissionResponse):
        """Capture permission responses"""
        import sys
        sys.stderr.write(f"\n[TEST] PERMISSION RESPONSE RECEIVED!\n")
        sys.stderr.write(f"  Option: {event.option}\n")
        sys.stderr.flush()

        self.responses_received.append(event.option)


@pytest.mark.asyncio
async def test_actual_tui_permission_flow():
    """
    TEST: Exact flow as it happens in live TUI
    """

    print("\n" + "="*80)
    print("TEST: Actual TUI Permission Flow")
    print("="*80 + "\n")

    async with ActualTUISimulation().run_test() as pilot:
        app = pilot.app

        print("Step 1: Initial state")
        print(f"  Focused widget: {type(app.focused).__name__}")
        print(f"  MultiLineInput.permission_prompt_data: {app.prompt_input.permission_prompt_data}")
        print()

        # Simulate /help command showing permission buffer
        print("Step 2: Simulate /help command...")
        prompt_data = {
            'title': 'System: /help',
            'message': 'Show available commands with descriptions',
            'selected': 0,  # This is set by the TUI
            'options': [
                {
                    'text': 'Yes, allow this once',
                    'response': 'allow_once',
                    'data': {'action': 'view_all'}
                },
                {
                    'text': 'No, cancel',
                    'response': 'cancel',
                    'data': {}
                }
            ]
        }

        app.show_permission_prompt_real_way(prompt_data)
        await pilot.pause(0.2)

        print(f"  permission_prompt_data set: {app.prompt_input.permission_prompt_data is not None}")
        print(f"  permission_selected_option: {app.prompt_input.permission_selected_option}")
        print(f"  Focused widget: {type(app.focused).__name__}")
        print(f"  MultiLineInput has focus: {app.prompt_input.has_focus}")
        print()

        # Try arrow key navigation
        print("Step 3: Press DOWN arrow key...")
        print(f"  Before: selected_option = {app.prompt_input.permission_selected_option}")

        await pilot.press("down")
        await pilot.pause(0.2)

        print(f"  After:  selected_option = {app.prompt_input.permission_selected_option}")

        if app.prompt_input.permission_selected_option == 1:
            print("  ✅ DOWN arrow worked!")
        else:
            print(f"  ❌ DOWN arrow did NOT work!")
            print(f"     Expected: 1, Got: {app.prompt_input.permission_selected_option}")
            pytest.fail("Arrow key navigation not working in actual TUI flow")

        print()

        # Try UP arrow
        print("Step 4: Press UP arrow key...")
        print(f"  Before: selected_option = {app.prompt_input.permission_selected_option}")

        await pilot.press("up")
        await pilot.pause(0.2)

        print(f"  After:  selected_option = {app.prompt_input.permission_selected_option}")

        if app.prompt_input.permission_selected_option == 0:
            print("  ✅ UP arrow worked!")
        else:
            print(f"  ❌ UP arrow did NOT work!")

        print()

        # Try ENTER to select
        print("Step 5: Press ENTER to select...")
        app.responses_received = []

        await pilot.press("enter")
        await pilot.pause(0.3)

        print(f"  Responses received: {len(app.responses_received)}")

        if len(app.responses_received) > 0:
            response = app.responses_received[0]
            print(f"  Response: {response}")
            print("  ✅ ENTER worked! Response captured!")
        else:
            print("  ❌ ENTER did NOT work - no response received!")
            pytest.fail("Enter key not working in actual TUI flow")


@pytest.mark.asyncio
async def test_debug_key_events():
    """
    TEST: Debug why keys might not be reaching on_key
    """

    print("\n" + "="*80)
    print("DEBUG: Key Event Routing")
    print("="*80 + "\n")

    async with ActualTUISimulation().run_test() as pilot:
        app = pilot.app

        # Show permission prompt
        prompt_data = {
            'title': 'Test',
            'message': 'Test',
            'selected': 0,
            'options': [
                {'text': 'Option 1', 'response': 'allow'},
                {'text': 'Option 2', 'response': 'deny'}
            ]
        }

        app.show_permission_prompt_real_way(prompt_data)
        await pilot.pause(0.2)

        print("State check:")
        print(f"  permission_prompt_data is None: {app.prompt_input.permission_prompt_data is None}")
        print(f"  permission_prompt_data exists: {app.prompt_input.permission_prompt_data is not None}")
        print(f"  Options count: {len(app.prompt_input.permission_prompt_data.get('options', []))}")
        print(f"  Focused: {app.focused == app.prompt_input}")
        print(f"  Can focus: {app.prompt_input.can_focus}")
        print(f"  Has focus: {app.prompt_input.has_focus}")
        print()

        # The debug log in on_key should print this
        print("Pressing DOWN arrow (watch stderr for debug log)...")
        await pilot.press("down")
        await pilot.pause(0.1)

        print(f"Selection after DOWN: {app.prompt_input.permission_selected_option}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
