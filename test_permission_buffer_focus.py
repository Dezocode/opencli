"""
Test permission buffer keyboard focus in TUI context
Simulates actual /help command flow and tests if buffer receives keys
"""

import pytest
import asyncio
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Static
from modules.permissions.widget import PermissionPrompt
from modules.permissions.enums import PermissionResponse
from modules.multiline_input import MultiLineInput


class MockChatDisplay(Static):
    """Mock chat display widget"""
    pass


class MockTUI(App):
    """Simulate actual OpenCLI TUI structure"""

    CSS = """
    Screen {
        layout: vertical;
    }

    #chat-container {
        height: 1fr;
    }

    #input-container {
        height: auto;
    }

    PermissionPrompt {
        width: 100%;
        height: auto;
    }

    MultiLineInput {
        width: 100%;
        height: auto;
    }
    """

    def __init__(self):
        super().__init__()
        self.chat_display = None
        self.input_box = None
        self.permission_prompt = None
        self.responses_received = []

    def compose(self) -> ComposeResult:
        """Compose UI like real TUI"""
        with Container(id="chat-container"):
            self.chat_display = MockChatDisplay("Chat messages...", id="chat-display")
            yield self.chat_display

        with Container(id="input-container"):
            self.input_box = MultiLineInput(placeholder="Type a message...")
            self.input_box.can_focus = True
            yield self.input_box

    def show_permission_buffer(self, prompt_data: dict):
        """Show permission buffer like real TUI does"""
        import sys
        sys.stderr.write("\n[MockTUI.show_permission_buffer] CALLED\n")
        sys.stderr.flush()

        # Create permission prompt if not exists
        if not self.permission_prompt:
            self.permission_prompt = PermissionPrompt(
                title=prompt_data.get('title', 'Permission Required'),
                message=prompt_data.get('message', 'Allow operation?'),
                options=prompt_data.get('options', [])
            )
            # Mount to chat container
            chat_container = self.query_one("#chat-container")
            chat_container.mount(self.permission_prompt)
            sys.stderr.write("[MockTUI] Permission prompt mounted\n")
            sys.stderr.flush()

        # Activate and show
        self.permission_prompt.show()
        sys.stderr.write(f"[MockTUI] Permission prompt shown, is_active={self.permission_prompt.is_active}\n")
        sys.stderr.flush()

        # CRITICAL: Set focus to permission prompt
        sys.stderr.write("[MockTUI] Setting focus to permission prompt...\n")
        sys.stderr.flush()
        self.set_focus(self.permission_prompt)

        # Verify focus
        focused = self.focused
        sys.stderr.write(f"[MockTUI] Focused widget: {type(focused).__name__ if focused else 'None'}\n")
        sys.stderr.flush()

    def on_permission_prompt_responded(self, event: PermissionPrompt.Responded):
        """Capture permission responses"""
        import sys
        sys.stderr.write(f"\n[MockTUI.on_permission_prompt_responded] RECEIVED\n")
        sys.stderr.write(f"  Response: {event.response}\n")
        sys.stderr.write(f"  Data: {event.data}\n")
        sys.stderr.flush()

        self.responses_received.append({
            'response': event.response,
            'data': event.data
        })


@pytest.mark.asyncio
async def test_permission_buffer_receives_focus():
    """
    TEST: Permission buffer receives focus when shown
    """

    print("\n" + "="*80)
    print("TEST: Permission Buffer Focus in TUI Context")
    print("="*80 + "\n")

    async with MockTUI().run_test() as pilot:
        app = pilot.app

        # Initial state - input box should have focus
        print("Initial state:")
        print(f"  Focused widget: {type(app.focused).__name__ if app.focused else 'None'}")

        assert app.focused == app.input_box, "Input box should have initial focus"
        print("  ✓ Input box has focus\n")

        # Simulate /help command triggering permission buffer
        print("Simulating /help command...")
        prompt_data = {
            'title': 'System: /help',
            'message': 'Show available commands with descriptions',
            'options': [
                {
                    'text': 'Yes, allow this once',
                    'response': PermissionResponse.ALLOW_ONCE,
                    'data': {'action': 'view_all'}
                },
                {
                    'text': 'No, cancel',
                    'response': PermissionResponse.CANCEL,
                    'data': {}
                }
            ]
        }

        app.show_permission_buffer(prompt_data)
        await pilot.pause(0.2)

        # Check if permission prompt received focus
        print("\nAfter showing permission buffer:")
        print(f"  Focused widget: {type(app.focused).__name__ if app.focused else 'None'}")
        print(f"  Permission prompt exists: {app.permission_prompt is not None}")
        print(f"  Permission prompt is_active: {app.permission_prompt.is_active if app.permission_prompt else 'N/A'}")
        print(f"  Permission prompt can_focus: {app.permission_prompt.can_focus if app.permission_prompt else 'N/A'}")

        if app.focused != app.permission_prompt:
            print(f"\n  ❌ FOCUS ISSUE: Expected PermissionPrompt, got {type(app.focused).__name__}")
            print(f"     This is why keyboard input is not working!")

            # Try to manually set focus
            print("\n  Attempting to manually set focus...")
            app.set_focus(app.permission_prompt)
            await pilot.pause(0.1)

            print(f"  After manual focus: {type(app.focused).__name__ if app.focused else 'None'}")

            if app.focused != app.permission_prompt:
                pytest.fail("Permission prompt cannot receive focus - keyboard navigation will not work!")
            else:
                print("  ✓ Manual focus worked")
        else:
            print("  ✓ Permission prompt has focus")


@pytest.mark.asyncio
async def test_permission_buffer_keyboard_input():
    """
    TEST: Permission buffer responds to keyboard input
    """

    print("\n" + "="*80)
    print("TEST: Permission Buffer Keyboard Input")
    print("="*80 + "\n")

    async with MockTUI().run_test() as pilot:
        app = pilot.app

        # Show permission buffer
        prompt_data = {
            'title': 'System: /help',
            'message': 'Show available commands',
            'options': [
                {'text': 'Allow once', 'response': PermissionResponse.ALLOW_ONCE, 'data': {'action': '1'}},
                {'text': 'Allow always', 'response': PermissionResponse.ALLOW_ALWAYS, 'data': {'action': '2'}},
                {'text': 'Cancel', 'response': PermissionResponse.CANCEL, 'data': {}}
            ]
        }

        app.show_permission_buffer(prompt_data)
        await pilot.pause(0.2)

        # Ensure focus
        if app.focused != app.permission_prompt:
            print("⚠️  Permission prompt doesn't have focus, forcing focus...")
            app.set_focus(app.permission_prompt)
            await pilot.pause(0.1)

        print("Testing keyboard input:")
        print(f"  Initial selection: {app.permission_prompt.selected_option}")

        # Test DOWN arrow
        print("\n  Pressing DOWN arrow...")
        await pilot.press("down")
        await pilot.pause(0.1)

        print(f"  Selection after DOWN: {app.permission_prompt.selected_option}")

        if app.permission_prompt.selected_option == 1:
            print("  ✅ DOWN arrow worked!")
        else:
            print(f"  ❌ DOWN arrow failed: expected 1, got {app.permission_prompt.selected_option}")
            print("     Keys are NOT reaching the permission prompt widget!")
            pytest.fail("Keyboard input not reaching permission buffer")

        # Test UP arrow
        print("\n  Pressing UP arrow...")
        await pilot.press("up")
        await pilot.pause(0.1)

        print(f"  Selection after UP: {app.permission_prompt.selected_option}")

        if app.permission_prompt.selected_option == 0:
            print("  ✅ UP arrow worked!")
        else:
            print(f"  ❌ UP arrow failed")

        # Test ENTER to select
        print("\n  Pressing ENTER to select option 0...")
        app.responses_received = []

        await pilot.press("enter")
        await pilot.pause(0.2)

        print(f"\n  Responses received: {len(app.responses_received)}")

        if len(app.responses_received) > 0:
            response = app.responses_received[0]
            print(f"  Response: {response['response']}")
            print(f"  Data: {response['data']}")
            print("  ✅ ENTER key worked! Selection captured!")
        else:
            print("  ❌ ENTER key failed - no response received")
            print("     The selection is not being posted as an event!")
            pytest.fail("Enter key selection not working")


@pytest.mark.asyncio
async def test_focus_chain_issue():
    """
    TEST: Identify if focus chain is the problem
    """

    print("\n" + "="*80)
    print("TEST: Focus Chain Analysis")
    print("="*80 + "\n")

    async with MockTUI().run_test() as pilot:
        app = pilot.app

        # Get all focusable widgets
        print("Analyzing focusable widgets in TUI:")

        focusable = []
        for widget in app.query("*"):
            if getattr(widget, 'can_focus', False):
                focusable.append(widget)
                print(f"  - {type(widget).__name__} (can_focus={widget.can_focus})")

        print(f"\nTotal focusable widgets: {len(focusable)}")

        # Show permission buffer
        prompt_data = {
            'title': 'Test',
            'message': 'Test',
            'options': [
                {'text': 'Option 1', 'response': 'allow'},
                {'text': 'Option 2', 'response': 'deny'}
            ]
        }

        app.show_permission_buffer(prompt_data)
        await pilot.pause(0.2)

        # Check if permission prompt is in focus chain
        print("\nAfter showing permission buffer:")

        focusable_after = []
        for widget in app.query("*"):
            if getattr(widget, 'can_focus', False):
                focusable_after.append(widget)
                is_focused = (widget == app.focused)
                focus_marker = " ← FOCUSED" if is_focused else ""
                print(f"  - {type(widget).__name__} (can_focus={widget.can_focus}){focus_marker}")

        print(f"\nTotal focusable widgets: {len(focusable_after)}")

        # Check if permission prompt is focusable
        if app.permission_prompt in focusable_after:
            print("\n✅ Permission prompt IS in focus chain")
        else:
            print("\n❌ Permission prompt NOT in focus chain!")
            print("   This is why it's not receiving keyboard input!")

        # Try to focus it
        print("\nAttempting to focus permission prompt...")
        app.set_focus(app.permission_prompt)
        await pilot.pause(0.1)

        if app.focused == app.permission_prompt:
            print("✅ Successfully focused permission prompt")

            # Try a key press
            print("\nTesting key press after manual focus...")
            initial = app.permission_prompt.selected_option
            await pilot.press("down")
            await pilot.pause(0.1)
            final = app.permission_prompt.selected_option

            if final != initial:
                print(f"✅ Key press worked! {initial} → {final}")
            else:
                print(f"❌ Key press did NOT work")
        else:
            print(f"❌ Failed to focus permission prompt")
            print(f"   Focused widget: {type(app.focused).__name__}")
            pytest.fail("Cannot focus permission prompt - focus chain issue!")


@pytest.mark.asyncio
async def test_multiline_input_stealing_focus():
    """
    TEST: Check if MultiLineInput is stealing focus back
    """

    print("\n" + "="*80)
    print("TEST: MultiLineInput Focus Stealing")
    print("="*80 + "\n")

    async with MockTUI().run_test() as pilot:
        app = pilot.app

        # Show permission buffer
        prompt_data = {
            'title': 'Test',
            'message': 'Test',
            'options': [{'text': 'Option', 'response': 'allow'}]
        }

        print("Initial focus:")
        print(f"  {type(app.focused).__name__}")

        app.show_permission_buffer(prompt_data)
        await pilot.pause(0.1)

        print("\nFocus after showing buffer:")
        print(f"  {type(app.focused).__name__}")

        # Wait a bit and check if focus changed
        await pilot.pause(0.5)

        print("\nFocus after 500ms delay:")
        print(f"  {type(app.focused).__name__}")

        if app.focused != app.permission_prompt:
            print(f"\n❌ FOCUS WAS STOLEN!")
            print(f"   Permission prompt had focus but now: {type(app.focused).__name__}")
            print(f"   This is likely MultiLineInput reclaiming focus")

            # Check if it's the input box
            if app.focused == app.input_box:
                print(f"   ✓ Confirmed: MultiLineInput stole focus back!")
                pytest.fail("MultiLineInput is stealing focus from permission buffer")
        else:
            print("\n✅ Focus maintained on permission prompt")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
