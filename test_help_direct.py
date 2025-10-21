#!/usr/bin/env python3
"""Direct test of /help command execution to debug permission flow"""

import sys
import asyncio
sys.path.insert(0, '/Users/dezmondhollins/.opencli')

from cli.session import Session
from modules.execution.executor import get_executor, ExecutionType
from modules.execution.registry import ExecutionRegistration
from modules.multiline_input import MultiLineInput
from textual.app import App

class FakeTUI(App):
    """Minimal fake TUI for testing"""
    def __init__(self):
        super().__init__()
        self.output = []
        self._prompt_widget = None

    def compose(self):
        """Compose the app"""
        from textual.widgets import Static
        self._prompt_widget = MultiLineInput()
        self._prompt_widget.id = "prompt-input"
        yield self._prompt_widget
        yield Static("Test", id="chat")

    def write(self, text):
        """Capture writes"""
        self.output.append(text)
        sys.stderr.write(f"[FakeTUI.write] {text}\n")
        sys.stderr.flush()

    def query_one(self, selector, widget_type=None):
        """Return the prompt widget"""
        if selector == "#prompt-input" or selector == MultiLineInput:
            sys.stderr.write(f"[FakeTUI.query_one] Returning prompt widget: {self._prompt_widget}\n")
            sys.stderr.flush()
            return self._prompt_widget
        raise Exception(f"Widget not found: {selector}")

    def set_focus(self, widget):
        """Fake focus"""
        sys.stderr.write(f"[FakeTUI.set_focus] Setting focus to: {widget}\n")
        sys.stderr.flush()

async def test_help_execution():
    """Test /help command execution"""
    print("=" * 80)
    print("DIRECT /HELP EXECUTION TEST")
    print("=" * 80)

    # Create session and fake app
    session = Session(model='test_model')
    app = FakeTUI()

    print("\n[1] Creating executor...")
    executor = get_executor(app, session)
    print(f"   executor.app = {executor.app}")
    print(f"   executor.session = {executor.session}")

    # Register /help command manually
    print("\n[2] Manually registering /help command...")
    from modules.commands.basic_commands import show_help, show_help_prompt
    from modules.execution.registry import ExecutionCategory, RiskLevel

    registration = ExecutionRegistration(
        type=ExecutionType.COMMAND,
        name="/help",
        handler=show_help,
        category=ExecutionCategory.SYSTEM,
        risk_level=RiskLevel.LOW,
        description="Show command help",
        requires_approval=True,
        enabled=True,
        metadata={'custom_prompt_func': show_help_prompt}
    )

    executor.registry.commands["/help"] = registration
    print(f"   ✓ Registered /help")
    print(f"   requires_approval: {registration.requires_approval}")
    print(f"   custom_prompt_func: {registration.metadata.get('custom_prompt_func')}")

    # Execute /help
    print("\n[3] Executing /help command...")
    try:
        result = await executor.execute(
            ExecutionType.COMMAND,
            "/help",
            None,
            app=app,
            session=session
        )
        print(f"   ✓ Command executed successfully")
        print(f"   Result: {result}")
    except PermissionError as e:
        print(f"   ❌ Permission denied: {e}")
        print(f"   This means check_permission() returned False!")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

    # Check if widget was set
    print("\n[4] Checking widget state...")
    if hasattr(app, '_prompt_widget') and app._prompt_widget:
        print(f"   Widget: {app._prompt_widget}")
        print(f"   permission_prompt_data: {app._prompt_widget.permission_prompt_data}")
    else:
        print(f"   ❌ No prompt widget found!")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    asyncio.run(test_help_execution())
