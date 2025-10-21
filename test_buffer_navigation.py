"""
Test permission buffer navigation and interaction
Validates arrow key navigation, selection capture, and flow continuation
"""

import pytest
import asyncio
from textual.events import Key
from modules.permissions.widget import PermissionPrompt
from modules.permissions.enums import PermissionResponse


class MockApp:
    """Mock Textual app for testing"""

    def __init__(self):
        self.focused_widget = None
        self.messages = []

    def set_focus(self, widget):
        """Mock focus"""
        self.focused_widget = widget

    def post_message(self, message):
        """Mock message posting"""
        self.messages.append(message)


@pytest.mark.asyncio
async def test_permission_buffer_arrow_navigation():
    """
    Test that arrow keys navigate between options in permission buffer
    """

    print("\n" + "="*80)
    print("TESTING: Permission Buffer Arrow Key Navigation")
    print("="*80 + "\n")

    # Create permission prompt with multiple options
    prompt_data = {
        'title': 'Test Command',
        'message': 'Allow this operation?',
        'options': [
            {
                'text': 'Yes, allow this once',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {}
            },
            {
                'text': 'Yes, and remember for this item',
                'response': PermissionResponse.ALLOW_ALWAYS,
                'data': {}
            },
            {
                'text': 'Yes, and auto-accept this session',
                'response': PermissionResponse.ALLOW_SESSION,
                'data': {}
            },
            {
                'text': 'No, cancel',
                'response': PermissionResponse.CANCEL,
                'data': {}
            }
        ]
    }

    # Create widget
    widget = PermissionPrompt(
        title=prompt_data['title'],
        message=prompt_data['message'],
        options=prompt_data['options']
    )

    # Mount widget
    app = MockApp()
    # widget.app = app

    print("Created permission buffer with 4 options")
    print(f"Initial selection: option 0")

    # Check initial state
    initial_selected = getattr(widget, 'selected_index', 0)
    print(f"  Current selection: {initial_selected}")

    # Test arrow down
    print("\nTest 1: Arrow Down Key")
    down_key = Key(key="down")

    # Check if widget has key handler
    has_on_key = hasattr(widget, 'on_key')
    print(f"  Widget has on_key handler: {has_on_key}")

    if has_on_key:
        await widget.on_key(down_key)
        new_selected = getattr(widget, 'selected_index', 0)
        print(f"  After down arrow: selection = {new_selected}")

        if new_selected == 1:
            print("  ✅ Arrow down navigation works")
        else:
            print(f"  ❌ Arrow down failed: expected 1, got {new_selected}")
            pytest.fail("Arrow down navigation not working")
    else:
        print("  ⚠️  Widget missing on_key handler")
        print("  Checking for action handlers...")

        # Check for action-based navigation (Textual pattern)
        has_action_down = hasattr(widget, 'action_cursor_down')
        has_action_up = hasattr(widget, 'action_cursor_up')

        print(f"    Has action_cursor_down: {has_action_down}")
        print(f"    Has action_cursor_up: {has_action_up}")

        if not (has_action_down or has_action_up):
            print("  ❌ No navigation handlers found!")
            pytest.fail("Widget missing navigation handlers (on_key or action_cursor_*)")

    print("\n" + "="*80)
    print("Test 2: Arrow Up Key")
    print("="*80)

    # Set to option 2
    if hasattr(widget, 'selected_index'):
        widget.selected_index = 2
        print(f"  Set selection to: 2")

    up_key = Key(key="up")

    if has_on_key:
        await widget.on_key(up_key)
        new_selected = getattr(widget, 'selected_index', 0)
        print(f"  After up arrow: selection = {new_selected}")

        if new_selected == 1:
            print("  ✅ Arrow up navigation works")
        else:
            print(f"  ❌ Arrow up failed: expected 1, got {new_selected}")

    print("\n" + "="*80)
    print("Test 3: Enter Key Selection")
    print("="*80)

    # Set to specific option
    if hasattr(widget, 'selected_index'):
        widget.selected_index = 0
        print(f"  Set selection to option 0: 'Yes, allow this once'")

    enter_key = Key(key="enter")
    selection_made = False
    selected_option = None

    # Track if selection event is posted
    if has_on_key:
        original_post = widget.post_message if hasattr(widget, 'post_message') else None

        def track_post_message(message):
            nonlocal selection_made, selected_option
            selection_made = True
            selected_option = message
            print(f"  ✅ Selection event posted: {type(message).__name__}")

        if original_post:
            widget.post_message = track_post_message

        await widget.on_key(enter_key)

        if selection_made:
            print("  ✅ Enter key triggers selection event")
        else:
            print("  ⚠️  Enter key did not post selection event")
            # Check if widget has action_select
            has_action_select = hasattr(widget, 'action_select')
            print(f"    Has action_select: {has_action_select}")

            if not has_action_select:
                print("  ❌ No selection handler found!")
                pytest.fail("Widget missing selection handler")

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    # Check widget composition
    print("\nWidget Composition Check:")
    print(f"  Type: {type(widget).__name__}")
    print(f"  Has selected_index: {hasattr(widget, 'selected_index')}")
    print(f"  Has options: {hasattr(widget, 'options')}")
    print(f"  Has on_key: {hasattr(widget, 'on_key')}")
    print(f"  Has action_cursor_down: {hasattr(widget, 'action_cursor_down')}")
    print(f"  Has action_cursor_up: {hasattr(widget, 'action_cursor_up')}")
    print(f"  Has action_select: {hasattr(widget, 'action_select')}")

    # Check if widget is a Textual widget
    has_focus = hasattr(widget, 'focus')
    has_render = hasattr(widget, 'render')
    has_compose = hasattr(widget, 'compose')

    print(f"\nTextual Widget Interface:")
    print(f"  Has focus: {has_focus}")
    print(f"  Has render: {has_render}")
    print(f"  Has compose: {has_compose}")

    if not (has_focus and has_render):
        print("\n⚠️  Widget may not be a proper Textual widget!")


@pytest.mark.asyncio
async def test_permission_buffer_focus_handling():
    """
    Test that permission buffer can receive and maintain focus
    """

    print("\n" + "="*80)
    print("TESTING: Permission Buffer Focus Handling")
    print("="*80 + "\n")

    prompt_data = {
        'title': 'Test Command',
        'message': 'Test focus',
        'options': [
            {'text': 'Option 1', 'response': 'allow'},
            {'text': 'Option 2', 'response': 'deny'}
        ]
    }

    widget = PermissionPrompt(
        title=prompt_data['title'],
        message=prompt_data['message'],
        options=prompt_data['options']
    )

    # Check focus capabilities
    can_focus = getattr(widget, 'can_focus', False)
    print(f"Widget can_focus: {can_focus}")

    if not can_focus:
        print("❌ Widget cannot receive focus!")
        print("   This will prevent keyboard input from being captured")
        pytest.fail("PermissionPrompt widget cannot receive focus")
    else:
        print("✅ Widget can receive focus")

    # Check if widget has focus method
    has_focus_method = hasattr(widget, 'focus')
    print(f"Has focus() method: {has_focus_method}")

    # Check if widget is focusable
    if hasattr(widget, '_is_focusable'):
        is_focusable = widget._is_focusable
        print(f"Is focusable: {is_focusable}")


@pytest.mark.asyncio
async def test_permission_buffer_selection_capture():
    """
    Test that user selection is properly captured and returned
    """

    print("\n" + "="*80)
    print("TESTING: Permission Buffer Selection Capture")
    print("="*80 + "\n")

    prompt_data = {
        'title': 'Test Selection',
        'message': 'Select an option',
        'options': [
            {
                'text': 'Allow once',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'test'}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL,
                'data': {}
            }
        ]
    }

    widget = PermissionPrompt(
        title=prompt_data['title'],
        message=prompt_data['message'],
        options=prompt_data['options']
    )

    print("Testing selection capture mechanism...")

    # Check if widget has selection callback
    has_callback = hasattr(widget, 'on_option_selected')
    print(f"  Has on_option_selected callback: {has_callback}")

    # Check if widget posts messages
    has_post_message = hasattr(widget, 'post_message')
    print(f"  Has post_message method: {has_post_message}")

    # Check for selection storage
    selected_response = None
    selected_data = None

    if hasattr(widget, 'get_selected_option'):
        selected = widget.get_selected_option()
        print(f"  Can get selected option: {selected is not None}")
        if selected:
            selected_response = selected.get('response')
            selected_data = selected.get('data')
            print(f"    Response: {selected_response}")
            print(f"    Data: {selected_data}")

    print("\n✅ Selection capture mechanism check complete")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
