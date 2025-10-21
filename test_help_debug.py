#!/usr/bin/env python3
"""Debug test for /help command permission buffer"""

import asyncio
import sys
from modules.execution.executor import ExecutionSystem
from modules.execution.registry import ExecutionType
from unittest.mock import Mock

async def test_help_command():
    """Test /help command permission flow"""

    # Create mock app and session
    app = Mock()
    session = Mock()
    session.session_id = "test-123"

    # Mock prompt widget
    prompt_widget = Mock()
    prompt_widget.permission_prompt_data = None
    app.query_one = Mock(return_value=prompt_widget)

    # Create execution system
    executor = ExecutionSystem(app, session)

    # Register SDK commands
    print("Registering SDK commands...")
    from modules.commands.registry import register_all
    await register_all(executor)

    print(f"Total commands registered: {len(executor.registry.commands)}")

    # Check if /help is registered
    help_reg = executor.registry.get(ExecutionType.COMMAND, '/help')
    if help_reg:
        print(f"✓ /help is registered")
        print(f"  requires_approval: {help_reg.requires_approval}")
        print(f"  has custom_prompt_func: {help_reg.metadata.get('custom_prompt_func') is not None}")
    else:
        print("❌ /help is NOT registered!")
        return

    # Try to execute /help
    print("\nExecuting /help command...")
    try:
        result = await executor.execute(
            ExecutionType.COMMAND,
            '/help',
            app=app,
            session=session
        )
        print(f"✓ /help executed successfully!")
        print(f"Result: {result}")
    except Exception as e:
        print(f"❌ /help execution failed!")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_help_command())
