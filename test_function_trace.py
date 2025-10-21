"""
Test with detailed function call tracing
Shows exactly which functions fire and in what order
"""

import pytest
import asyncio
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Static
from modules.multiline_input import MultiLineInput


# Global trace log
function_trace = []


def trace_call(func_name, details=""):
    """Log function calls"""
    entry = f"{func_name}"
    if details:
        entry += f" - {details}"
    function_trace.append(entry)
    print(f"  → {entry}")


class TracedMultiLineInput(MultiLineInput):
    """MultiLineInput with call tracing"""

    def __init__(self, *args, **kwargs):
        trace_call("MultiLineInput.__init__")
        super().__init__(*args, **kwargs)

    def on_key(self, event):
        """Trace key events"""
        trace_call(f"MultiLineInput.on_key", f"key={event.key}, prompt={bool(self.permission_prompt_data)}")
        return super().on_key(event)

    def watch_permission_prompt_data(self, old, new):
        """Trace permission data changes"""
        trace_call("MultiLineInput.watch_permission_prompt_data", f"was_none={old is None}, is_none={new is None}")
        # Watchers are callbacks - just trace, don't call super

    def watch_permission_selected_option(self, old, new):
        """Trace selection changes"""
        trace_call("MultiLineInput.watch_permission_selected_option", f"{old}→{new}")
        # Watchers are callbacks - just trace, don't call super


class TracedTUI(App):
    """TUI with function tracing"""

    def __init__(self):
        trace_call("TracedTUI.__init__")
        super().__init__()
        self.prompt_input = None
        self.responses = []

    def compose(self) -> ComposeResult:
        trace_call("TracedTUI.compose")
        with Container(id="chat-container"):
            yield Static("Chat")

        with Container(id="input-container"):
            self.prompt_input = TracedMultiLineInput(placeholder="Message...", id="prompt-input")
            yield self.prompt_input

    def show_permission_buffer(self, prompt_data):
        """Show permission buffer with tracing"""
        trace_call("TracedTUI.show_permission_buffer", f"title={prompt_data.get('title')}")

        prompt_input = self.query_one("#prompt-input")
        prompt_data['selected'] = 0
        prompt_input.permission_prompt_data = prompt_data
        prompt_input.refresh()

        trace_call("TracedTUI.show_permission_buffer", "permission_prompt_data SET")

    def on_multi_line_input_permission_response(self, event):
        """Capture responses with tracing"""
        trace_call("TracedTUI.on_permission_response", f"option={event.option.get('text')}")
        self.responses.append(event.option)


@pytest.mark.asyncio
async def test_function_trace():
    """
    TEST: Show all function calls during navigation
    """

    global function_trace
    function_trace = []

    print("\n" + "="*80)
    print("FUNCTION CALL TRACE TEST")
    print("="*80 + "\n")

    print("🔍 Starting TUI...")
    async with TracedTUI().run_test() as pilot:
        app = pilot.app

        print("\n🔍 Showing permission buffer...")
        prompt_data = {
            'title': 'System: /help',
            'message': 'Test',
            'selected': 0,
            'options': [
                {'text': 'Allow once', 'response': 'allow_once', 'data': {'act': '1'}},
                {'text': 'Allow always', 'response': 'allow_always', 'data': {'act': '2'}},
                {'text': 'Cancel', 'response': 'cancel', 'data': {}}
            ]
        }

        app.show_permission_buffer(prompt_data)
        await pilot.pause(0.2)

        print("\n🔍 Pressing DOWN arrow...")
        await pilot.press("down")
        await pilot.pause(0.1)

        print("\n🔍 Pressing DOWN arrow again...")
        await pilot.press("down")
        await pilot.pause(0.1)

        print("\n🔍 Pressing UP arrow...")
        await pilot.press("up")
        await pilot.pause(0.1)

        print("\n🔍 Pressing ENTER to select...")
        await pilot.press("enter")
        await pilot.pause(0.2)

    print("\n" + "="*80)
    print("COMPLETE FUNCTION TRACE")
    print("="*80 + "\n")

    for i, call in enumerate(function_trace, 1):
        print(f"{i:3d}. {call}")

    print("\n" + "="*80)
    print("ANALYSIS")
    print("="*80 + "\n")

    # Check key sequence
    key_calls = [c for c in function_trace if 'on_key' in c]
    print(f"Total key events: {len(key_calls)}")
    for kc in key_calls:
        print(f"  {kc}")

    # Check selection changes
    selection_calls = [c for c in function_trace if 'watch_permission_selected_option' in c]
    print(f"\nSelection changes: {len(selection_calls)}")
    for sc in selection_calls:
        print(f"  {sc}")

    # Check permission data changes
    data_calls = [c for c in function_trace if 'watch_permission_prompt_data' in c]
    print(f"\nPermission data changes: {len(data_calls)}")
    for dc in data_calls:
        print(f"  {dc}")

    # Check response
    response_calls = [c for c in function_trace if 'on_permission_response' in c]
    print(f"\nResponse events: {len(response_calls)}")
    for rc in response_calls:
        print(f"  {rc}")

    print("\n" + "="*80)
    print("EXPECTED SEQUENCE")
    print("="*80 + "\n")

    expected = [
        "1. show_permission_buffer called",
        "2. watch_permission_prompt_data fired (None→data)",
        "3. on_key fired for DOWN",
        "4. watch_permission_selected_option fired (0→1)",
        "5. on_key fired for DOWN",
        "6. watch_permission_selected_option fired (1→2)",
        "7. on_key fired for UP",
        "8. watch_permission_selected_option fired (2→1)",
        "9. on_key fired for ENTER",
        "10. on_permission_response fired",
    ]

    for exp in expected:
        print(f"  {exp}")

    print("\n" + "="*80)
    print("VERIFICATION")
    print("="*80 + "\n")

    # Verify each expected call happened
    checks = {
        "Permission buffer shown": any('show_permission_buffer' in c for c in function_trace),
        "Permission data watched": any('watch_permission_prompt_data' in c for c in function_trace),
        "Keys captured": len(key_calls) >= 4,
        "Selection changed": len(selection_calls) >= 3,
        "Response posted": len(response_calls) >= 1,
    }

    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")

    if all(checks.values()):
        print("\n✅ ALL CHECKS PASSED - Code is working correctly!")
    else:
        print("\n❌ SOME CHECKS FAILED - See above for details")
        pytest.fail("Function trace validation failed")


@pytest.mark.asyncio
async def test_code_path_validation():
    """
    TEST: Validate exact code paths taken
    """

    global function_trace
    function_trace = []

    print("\n" + "="*80)
    print("CODE PATH VALIDATION")
    print("="*80 + "\n")

    async with TracedTUI().run_test() as pilot:
        app = pilot.app

        # Setup
        prompt_data = {
            'title': 'Test',
            'message': 'Test',
            'selected': 0,
            'options': [
                {'text': 'Opt1', 'response': 'r1', 'data': {}},
                {'text': 'Opt2', 'response': 'r2', 'data': {}}
            ]
        }

        print("Action: Show buffer")
        app.show_permission_buffer(prompt_data)
        await pilot.pause(0.1)

        # Validate buffer shown
        assert app.prompt_input.permission_prompt_data is not None, "Buffer data not set!"
        print("  ✓ Buffer data SET")

        print("\nAction: Press DOWN")
        initial = app.prompt_input.permission_selected_option
        await pilot.press("down")
        await pilot.pause(0.1)

        final = app.prompt_input.permission_selected_option
        print(f"  ✓ Selection: {initial} → {final}")

        assert final == initial + 1, f"Selection should increase by 1: {initial} → {final}"

        print("\nAction: Press ENTER")
        app.responses = []
        await pilot.press("enter")
        await pilot.pause(0.2)

        assert len(app.responses) > 0, "No response captured!"
        print(f"  ✓ Response captured: {app.responses[0].get('text')}")

    print("\n" + "="*80)
    print("CODE PATHS TAKEN:")
    print("="*80)

    # Group by function
    from collections import defaultdict
    by_function = defaultdict(list)

    for call in function_trace:
        func_name = call.split(" - ")[0]
        by_function[func_name].append(call)

    for func, calls in sorted(by_function.items()):
        print(f"\n{func}:")
        for call in calls:
            details = call.split(" - ", 1)[1] if " - " in call else ""
            print(f"  → {details if details else '(called)'}")

    print("\n✅ CODE PATH VALIDATION COMPLETE")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
