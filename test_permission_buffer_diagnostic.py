#!/usr/bin/env python3
"""
Diagnostic test to identify why permission buffer doesn't display
"""

import sys
import asyncio
from modules.tui.core import OpenCLITUI
from modules.multiline_input import MultiLineInput
from cli.session import Session


async def test_permission_buffer():
    """Test permission buffer display in isolation"""

    print("\n" + "="*80)
    print("PERMISSION BUFFER DIAGNOSTIC TEST")
    print("="*80 + "\n")

    # Create session
    session = Session(model='test-model')

    # Create minimal config
    config = {
        'model': 'test-model',
        'baseURL': 'https://api.example.com',
        'contextWindow': 128000
    }

    # Create TUI app
    app = OpenCLITUI(config=config, session=session)

    async with app.run_test() as pilot:
        print("✓ TUI app started successfully\n")

        # Test 1: Find the prompt input widget
        print("Test 1: Locating #prompt-input widget...")
        try:
            prompt_input = pilot.app.query_one("#prompt-input", MultiLineInput)
            print(f"  ✓ Widget found: {type(prompt_input)}")
            print(f"  ✓ Widget ID: {prompt_input.id}")
            print(f"  ✓ Widget visible: {prompt_input.visible}")
            print(f"  ✓ Widget mounted: {prompt_input.is_mounted}")
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            return

        print()

        # Test 2: Check reactive property
        print("Test 2: Checking permission_prompt_data reactive property...")
        try:
            from textual.reactive import Reactive
            prop = type(prompt_input).permission_prompt_data
            print(f"  ✓ Property type: {type(prop)}")
            print(f"  ✓ Is reactive: {isinstance(prop, Reactive)}")
            print(f"  ✓ Current value: {prompt_input.permission_prompt_data}")
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            return

        print()

        # Test 3: Manually set permission prompt data
        print("Test 3: Manually setting permission_prompt_data...")
        test_prompt_data = {
            'title': 'TEST: Permission Buffer',
            'message': 'This is a test of the permission buffer display system.',
            'options': [
                {
                    'text': 'Option 1',
                    'response': 'allow_once',
                    'data': {'test': 'option1'}
                },
                {
                    'text': 'Option 2',
                    'response': 'allow_once',
                    'data': {'test': 'option2'}
                },
                {
                    'text': 'Cancel',
                    'response': 'cancel'
                }
            ]
        }

        try:
            prompt_input.permission_prompt_data = test_prompt_data
            print(f"  ✓ Data set successfully")
            print(f"  ✓ Refreshing widget...")
            prompt_input.refresh()
            await pilot.pause(0.5)
            print(f"  ✓ Widget refreshed")

            # Check if it rendered
            rendered = prompt_input.render()
            print(f"  ✓ Rendered content length: {len(str(rendered))}")
            print(f"  ✓ Rendered preview: {str(rendered)[:200]}...")

        except Exception as e:
            print(f"  ✗ ERROR setting data: {e}")
            import traceback
            traceback.print_exc()
            return

        print()

        # Test 4: Use permission buffer manager
        print("Test 4: Testing through permission buffer manager...")
        try:
            from modules.permission_buffer_manager import get_permission_buffer_manager

            buffer_manager = get_permission_buffer_manager()
            print(f"  ✓ Buffer manager type: {type(buffer_manager)}")
            print(f"  ✓ Has request_permission: {hasattr(buffer_manager, 'request_permission')}")

            # Create a test with timeout
            print(f"  → Calling buffer_manager.request_permission() with 2s timeout...")

            try:
                result = await asyncio.wait_for(
                    buffer_manager.request_permission(
                        pilot.app,
                        session,
                        test_prompt_data,
                        timeout=2.0
                    ),
                    timeout=3.0
                )
                print(f"  ✓ Result: {result}")
            except asyncio.TimeoutError:
                print(f"  ⏱ TIMEOUT: request_permission() timed out (expected if no user interaction)")
                print(f"  → This is NORMAL if buffer displayed correctly")

                # Check if buffer actually displayed
                if prompt_input.permission_prompt_data:
                    print(f"  ✓ SUCCESS: Permission buffer data is still set on widget")
                    print(f"  ✓ Buffer should be visible in TUI")
                else:
                    print(f"  ✗ FAILURE: Permission buffer data was cleared")

        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return

        print("\n" + "="*80)
        print("DIAGNOSTIC COMPLETE")
        print("="*80)


if __name__ == "__main__":
    asyncio.run(test_permission_buffer())
