"""
Pytest proof that permission buffer navigation works
Tests arrow keys, enter, and event flow
"""

import pytest
import asyncio
from textual.app import App, ComposeResult
from textual.widgets import Static
from modules.permissions.widget import PermissionPrompt
from modules.permissions.enums import PermissionResponse


class TestApp(App):
    """Test app for permission prompt"""

    def __init__(self):
        super().__init__()
        self.prompt = None
        self.received_responses = []

    def compose(self) -> ComposeResult:
        """Compose the test UI"""
        self.prompt = PermissionPrompt(
            title="Test Command",
            message="Allow this operation?",
            options=[
                {'text': 'Option 1', 'response': PermissionResponse.ALLOW_ONCE, 'data': {'action': 'opt1'}},
                {'text': 'Option 2', 'response': PermissionResponse.ALLOW_ALWAYS, 'data': {'action': 'opt2'}},
                {'text': 'Option 3', 'response': PermissionResponse.ALLOW_SESSION, 'data': {'action': 'opt3'}},
                {'text': 'Option 4', 'response': PermissionResponse.CANCEL, 'data': {}}
            ]
        )
        self.prompt.is_active = True
        yield self.prompt

    def on_permission_prompt_responded(self, event: PermissionPrompt.Responded) -> None:
        """Capture responses"""
        self.received_responses.append({
            'response': event.response,
            'data': event.data
        })


@pytest.mark.asyncio
async def test_arrow_navigation_proof():
    """
    PROOF: Arrow keys navigate between options
    """

    print("\n" + "="*80)
    print("PROOF: Arrow Key Navigation Works")
    print("="*80 + "\n")

    async with TestApp().run_test() as pilot:
        app = pilot.app
        prompt = app.prompt

        print(f"✓ Permission prompt created with {len(prompt.options)} options")
        print(f"✓ Initial selection: {prompt.selected_option}")

        assert prompt.selected_option == 0, "Should start at option 0"

        # Test DOWN arrow
        print("\nTest 1: Press DOWN arrow")
        print(f"  Before: selected_option = {prompt.selected_option}")

        await pilot.press("down")
        await pilot.pause(0.1)

        print(f"  After:  selected_option = {prompt.selected_option}")

        assert prompt.selected_option == 1, f"DOWN should move to option 1, got {prompt.selected_option}"
        print("  ✅ DOWN arrow works! Moved from 0 → 1")

        # Test DOWN arrow again
        print("\nTest 2: Press DOWN arrow again")
        print(f"  Before: selected_option = {prompt.selected_option}")

        await pilot.press("down")
        await pilot.pause(0.1)

        print(f"  After:  selected_option = {prompt.selected_option}")

        assert prompt.selected_option == 2, f"DOWN should move to option 2, got {prompt.selected_option}"
        print("  ✅ DOWN arrow works! Moved from 1 → 2")

        # Test UP arrow
        print("\nTest 3: Press UP arrow")
        print(f"  Before: selected_option = {prompt.selected_option}")

        await pilot.press("up")
        await pilot.pause(0.1)

        print(f"  After:  selected_option = {prompt.selected_option}")

        assert prompt.selected_option == 1, f"UP should move to option 1, got {prompt.selected_option}"
        print("  ✅ UP arrow works! Moved from 2 → 1")

        # Test boundary - can't go below 0
        print("\nTest 4: Boundary check - can't go below 0")
        prompt.selected_option = 0
        print(f"  Set to: selected_option = {prompt.selected_option}")

        await pilot.press("up")
        await pilot.pause(0.1)

        print(f"  After UP: selected_option = {prompt.selected_option}")

        assert prompt.selected_option == 0, "UP at boundary should stay at 0"
        print("  ✅ Boundary works! Stayed at 0")

        # Test boundary - can't go above max
        print("\nTest 5: Boundary check - can't exceed max")
        max_index = len(prompt.options) - 1
        prompt.selected_option = max_index
        print(f"  Set to: selected_option = {prompt.selected_option} (max)")

        await pilot.press("down")
        await pilot.pause(0.1)

        print(f"  After DOWN: selected_option = {prompt.selected_option}")

        assert prompt.selected_option == max_index, f"DOWN at boundary should stay at {max_index}"
        print(f"  ✅ Boundary works! Stayed at {max_index}")

    print("\n" + "="*80)
    print("✅ PROOF COMPLETE: Arrow navigation works correctly")
    print("="*80)


@pytest.mark.asyncio
async def test_enter_selection_proof():
    """
    PROOF: Enter key selects current option and posts event
    """

    print("\n" + "="*80)
    print("PROOF: Enter Key Selection Works")
    print("="*80 + "\n")

    async with TestApp().run_test() as pilot:
        app = pilot.app
        prompt = app.prompt

        print(f"✓ Permission prompt created")
        print(f"✓ Event handler registered: on_permission_prompt_responded")

        # Navigate to option 2
        print("\nNavigating to option 2...")
        await pilot.press("down")
        await pilot.pause(0.1)
        await pilot.press("down")
        await pilot.pause(0.1)

        print(f"  Current selection: {prompt.selected_option}")
        assert prompt.selected_option == 2, "Should be at option 2"

        selected_option = prompt.options[2]
        print(f"  Selected option text: '{selected_option['text']}'")
        print(f"  Expected response: {selected_option['response']}")
        print(f"  Expected data: {selected_option['data']}")

        # Clear any previous responses
        app.received_responses = []

        print("\nPressing ENTER to select...")
        await pilot.press("enter")
        await pilot.pause(0.2)

        print(f"\nReceived responses: {len(app.received_responses)}")

        if len(app.received_responses) > 0:
            response = app.received_responses[0]
            print(f"  Response: {response['response']}")
            print(f"  Data: {response['data']}")

            assert response['response'] == selected_option['response'], \
                f"Response mismatch: expected {selected_option['response']}, got {response['response']}"
            assert response['data'] == selected_option['data'], \
                f"Data mismatch: expected {selected_option['data']}, got {response['data']}"

            print("\n✅ ENTER key posted correct response!")
            print(f"   Response: {response['response']}")
            print(f"   Data: {response['data']}")
        else:
            print("\n❌ No response received!")
            pytest.fail("Enter key did not trigger response event")

        # Check that prompt is deactivated
        print(f"\nPrompt active status: {prompt.is_active}")
        assert prompt.is_active == False, "Prompt should be deactivated after selection"
        print("✅ Prompt deactivated after selection")

    print("\n" + "="*80)
    print("✅ PROOF COMPLETE: Enter selection works correctly")
    print("="*80)


@pytest.mark.asyncio
async def test_number_key_selection_proof():
    """
    PROOF: Number keys (1-4) directly select options
    """

    print("\n" + "="*80)
    print("PROOF: Number Key Selection Works")
    print("="*80 + "\n")

    async with TestApp().run_test() as pilot:
        app = pilot.app
        prompt = app.prompt

        print(f"✓ Permission prompt created with {len(prompt.options)} options")

        # Test number key 3
        print("\nTest: Press '3' to select option 3")
        print(f"  Initial selection: {prompt.selected_option}")

        app.received_responses = []

        await pilot.press("3")
        await pilot.pause(0.2)

        print(f"\nReceived responses: {len(app.received_responses)}")

        if len(app.received_responses) > 0:
            response = app.received_responses[0]
            # Number key 3 selects option at index 2 (0-indexed)
            expected_option = prompt.options[2]

            print(f"  Selected option: '{expected_option['text']}'")
            print(f"  Response: {response['response']}")
            print(f"  Data: {response['data']}")

            assert response['response'] == expected_option['response'], \
                "Number key should select correct option"

            print("\n✅ Number key '3' selected option 3 correctly!")
        else:
            print("\n❌ No response received!")
            pytest.fail("Number key did not trigger response event")

    print("\n" + "="*80)
    print("✅ PROOF COMPLETE: Number key selection works")
    print("="*80)


@pytest.mark.asyncio
async def test_escape_cancel_proof():
    """
    PROOF: Escape key cancels the prompt
    """

    print("\n" + "="*80)
    print("PROOF: Escape Key Cancellation Works")
    print("="*80 + "\n")

    async with TestApp().run_test() as pilot:
        app = pilot.app
        prompt = app.prompt

        print(f"✓ Permission prompt created")

        # Navigate to some option
        await pilot.press("down")
        await pilot.pause(0.1)

        print(f"  Current selection: {prompt.selected_option}")

        app.received_responses = []

        print("\nPressing ESCAPE to cancel...")
        await pilot.press("escape")
        await pilot.pause(0.2)

        print(f"\nReceived responses: {len(app.received_responses)}")

        if len(app.received_responses) > 0:
            response = app.received_responses[0]
            print(f"  Response: {response['response']}")

            assert response['response'] == PermissionResponse.CANCEL, \
                f"ESC should send CANCEL, got {response['response']}"

            print("\n✅ ESCAPE posted CANCEL response!")
        else:
            print("\n❌ No response received!")
            pytest.fail("Escape key did not trigger response event")

        # Check that prompt is deactivated
        print(f"\nPrompt active status: {prompt.is_active}")
        assert prompt.is_active == False, "Prompt should be deactivated after cancel"
        print("✅ Prompt deactivated after cancel")

    print("\n" + "="*80)
    print("✅ PROOF COMPLETE: Escape cancellation works")
    print("="*80)


@pytest.mark.asyncio
async def test_full_navigation_flow_proof():
    """
    PROOF: Complete navigation flow from start to selection
    """

    print("\n" + "="*80)
    print("PROOF: Complete Navigation Flow")
    print("="*80 + "\n")

    async with TestApp().run_test() as pilot:
        app = pilot.app
        prompt = app.prompt

        print("Simulating real user interaction:")
        print("  1. Start at option 0")
        print("  2. Press DOWN to option 1")
        print("  3. Press DOWN to option 2")
        print("  4. Press UP back to option 1")
        print("  5. Press ENTER to select")
        print()

        # Initial state
        assert prompt.selected_option == 0
        print(f"✓ Start: option {prompt.selected_option}")

        # DOWN to 1
        await pilot.press("down")
        await pilot.pause(0.1)
        assert prompt.selected_option == 1
        print(f"✓ After DOWN: option {prompt.selected_option}")

        # DOWN to 2
        await pilot.press("down")
        await pilot.pause(0.1)
        assert prompt.selected_option == 2
        print(f"✓ After DOWN: option {prompt.selected_option}")

        # UP to 1
        await pilot.press("up")
        await pilot.pause(0.1)
        assert prompt.selected_option == 1
        print(f"✓ After UP: option {prompt.selected_option}")

        # ENTER to select
        app.received_responses = []
        await pilot.press("enter")
        await pilot.pause(0.2)

        assert len(app.received_responses) == 1
        response = app.received_responses[0]
        expected = prompt.options[1]

        assert response['response'] == expected['response']
        assert response['data'] == expected['data']

        print(f"✓ After ENTER: received response")
        print(f"    Response: {response['response']}")
        print(f"    Data: {response['data']}")
        print(f"    Prompt deactivated: {not prompt.is_active}")

    print("\n" + "="*80)
    print("✅ PROOF COMPLETE: Full navigation flow works perfectly!")
    print("="*80)
    print("\nSUMMARY:")
    print("  ✅ Arrow keys navigate options")
    print("  ✅ Enter selects current option")
    print("  ✅ Events are posted correctly")
    print("  ✅ Prompt deactivates after selection")
    print("  ✅ Response data is captured")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
