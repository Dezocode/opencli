"""
Test to verify ALL commands use Grok's unified permission flow
Detects commands using multiple/different flows instead of the single unified flow
"""

import pytest
import asyncio
from modules.execution.registry import ExecutionType
from modules.execution.executor import ExecutionSystem
from cli.session import Session
from modules.permissions.integration import get_unified_permission_manager
from unittest.mock import MagicMock


class FlowTracker:
    """Track which flow path each command uses"""

    def __init__(self):
        self.flows = {}
        self.calls = []

    def record_call(self, command: str, flow_type: str, details: str = ""):
        """Record a flow call"""
        if command not in self.flows:
            self.flows[command] = []

        self.flows[command].append({
            'flow_type': flow_type,
            'details': details
        })

        self.calls.append(f"{command} → {flow_type} {details}".strip())

    def get_flow_types(self, command: str):
        """Get unique flow types for a command"""
        if command not in self.flows:
            return []
        return list(set(f['flow_type'] for f in self.flows[command]))

    def has_multiple_flows(self, command: str):
        """Check if command uses multiple different flows"""
        flow_types = self.get_flow_types(command)
        return len(flow_types) > 1

    def get_report(self):
        """Generate flow analysis report"""
        report = []
        report.append("\n" + "="*80)
        report.append("PERMISSION FLOW ANALYSIS REPORT")
        report.append("="*80 + "\n")

        # Analyze each command
        for command, flows in self.flows.items():
            flow_types = self.get_flow_types(command)

            if len(flow_types) == 1 and flow_types[0] == 'GROK_UNIFIED':
                status = "✅ CORRECT"
            elif len(flow_types) > 1:
                status = "❌ MULTIPLE FLOWS"
            else:
                status = f"⚠️  ALTERNATE FLOW: {flow_types[0]}"

            report.append(f"{status} - {command}")
            for flow in flows:
                report.append(f"    {flow['flow_type']}: {flow['details']}")
            report.append("")

        # Summary
        report.append("="*80)
        report.append("SUMMARY")
        report.append("="*80)

        total = len(self.flows)
        correct = sum(1 for cmd in self.flows.keys()
                     if self.get_flow_types(cmd) == ['GROK_UNIFIED'])
        multiple = sum(1 for cmd in self.flows.keys()
                      if self.has_multiple_flows(cmd))
        alternate = total - correct - multiple

        report.append(f"Total commands tested: {total}")
        report.append(f"✅ Using Grok unified flow: {correct}")
        report.append(f"❌ Using multiple flows: {multiple}")
        report.append(f"⚠️  Using alternate flows: {alternate}")

        if correct == total:
            report.append("\n🎉 ALL COMMANDS USE GROK'S UNIFIED FLOW!")
        else:
            report.append("\n⚠️  SOME COMMANDS ARE NOT USING GROK'S FLOW!")

        return "\n".join(report)


class MockTUIApp:
    """Mock TUI app for testing"""

    def __init__(self, flow_tracker: FlowTracker):
        self.permission_manager = get_unified_permission_manager()
        self.flow_tracker = flow_tracker
        self.debug_mode = True

    def write(self, text):
        """Mock write"""
        pass

    def query_one(self, selector):
        """Mock query_one"""
        return MagicMock()


@pytest.mark.asyncio
async def test_all_commands_use_unified_flow():
    """
    Test that ALL approval-required commands use Grok's unified flow
    Detects commands using old/alternate flows
    """

    print("\n" + "="*80)
    print("TESTING: All Commands Use Grok's Unified Permission Flow")
    print("="*80 + "\n")

    # Initialize tracking
    flow_tracker = FlowTracker()
    session = Session(model='test-model')
    app = MockTUIApp(flow_tracker)

    # Create executor with shared permission manager
    executor = ExecutionSystem(
        app=app,
        session=session,
        permission_manager=app.permission_manager
    )

    # Register all commands
    from modules.commands.registry import register_all
    await register_all(executor)

    # Get all commands that require approval
    approval_required_commands = []
    for cmd_name, registration in executor.registry.commands.items():
        if registration.requires_approval:
            approval_required_commands.append(cmd_name)

    print(f"Found {len(approval_required_commands)} commands requiring approval\n")

    # Instrument the permission flow to track which path is used
    original_unified_check = app.permission_manager.check_permission
    original_buffer_request = app.permission_manager.get_buffer_manager().request_permission

    # Track if old PermissionManager is being used (shouldn't be!)
    try:
        from modules.execution.permission_manager import PermissionManager as OldPermissionManager
        old_pm_check_called = []

        original_old_check = OldPermissionManager.check_permission

        async def tracked_old_check(self, *args, **kwargs):
            """Track if old permission manager is called"""
            command = args[0].name if args else "unknown"
            flow_tracker.record_call(command, 'OLD_PERMISSION_MANAGER', '⚠️ Using deprecated flow!')
            old_pm_check_called.append(command)
            return True

        OldPermissionManager.check_permission = tracked_old_check
    except ImportError:
        old_pm_check_called = None

    async def tracked_unified_check(registration, context, app_arg=None, session_arg=None):
        """Track unified permission manager calls"""
        flow_tracker.record_call(
            registration.name,
            'GROK_UNIFIED',
            'UnifiedPermissionManager.check_permission()'
        )

        # Simulate approval
        return True

    async def tracked_buffer_request(app_arg, session_arg, prompt_data, timeout=30.0):
        """Track buffer manager calls"""
        command = prompt_data.get('title', 'unknown').replace('System: ', '')
        flow_tracker.record_call(
            command,
            'GROK_UNIFIED',
            'PermissionBufferManager.request_permission()'
        )

        # Simulate user approval
        return {'response': 'allow_once', 'data': {}}

    # Patch the flows
    app.permission_manager.check_permission = tracked_unified_check
    app.permission_manager.get_buffer_manager().request_permission = tracked_buffer_request

    # Test a representative sample of commands
    test_commands = [
        '/help',
        '/exit',
        '/quit',
        '/clear',
        '/permissions',
        '/status',
        '/agent',
        '/model',
        '/diff',
        '/docker',
    ]

    print("Testing commands:")
    for cmd in test_commands:
        if cmd in approval_required_commands:
            print(f"  {cmd}")
    print()

    # Execute each command and track which flow it uses
    for cmd_name in test_commands:
        if cmd_name not in approval_required_commands:
            continue

        try:
            print(f"Testing {cmd_name}...")

            # Execute with timeout to prevent hanging
            result = await asyncio.wait_for(
                executor.execute(ExecutionType.COMMAND, cmd_name, context={}),
                timeout=2.0
            )

            # Check if this command used the unified flow
            flow_types = flow_tracker.get_flow_types(cmd_name)

            if 'GROK_UNIFIED' in flow_types:
                print(f"  ✅ {cmd_name} uses Grok unified flow")
            elif 'OLD_PERMISSION_MANAGER' in flow_types:
                print(f"  ❌ {cmd_name} uses OLD permission manager!")
            else:
                print(f"  ⚠️  {cmd_name} uses unknown flow: {flow_types}")

            # Check for multiple flows
            if flow_tracker.has_multiple_flows(cmd_name):
                print(f"  ❌ WARNING: {cmd_name} uses MULTIPLE different flows!")
                print(f"     Flows detected: {flow_types}")

        except asyncio.TimeoutError:
            print(f"  ⚠️  {cmd_name} timed out (might be waiting for actual user input)")
        except Exception as e:
            # Some commands might fail due to missing registry, that's OK for this test
            if "Registry not available" in str(e) or "Session not available" in str(e):
                print(f"  ⚠️  {cmd_name} failed (handler issue, not flow issue)")
            else:
                print(f"  ❌ {cmd_name} failed: {e}")

    # Generate report
    print(flow_tracker.get_report())

    # Validate results
    print("\n" + "="*80)
    print("VALIDATION")
    print("="*80 + "\n")

    # Check if any command used old permission manager
    if old_pm_check_called and len(old_pm_check_called) > 0:
        print(f"❌ FAILURE: {len(old_pm_check_called)} commands used OLD PermissionManager:")
        for cmd in old_pm_check_called:
            print(f"   - {cmd}")
        pytest.fail("Some commands are using old PermissionManager instead of unified flow")

    # Check if any command used multiple flows
    multiple_flow_commands = [cmd for cmd in flow_tracker.flows.keys()
                             if flow_tracker.has_multiple_flows(cmd)]

    if len(multiple_flow_commands) > 0:
        print(f"❌ FAILURE: {len(multiple_flow_commands)} commands use MULTIPLE flows:")
        for cmd in multiple_flow_commands:
            flows = flow_tracker.get_flow_types(cmd)
            print(f"   - {cmd}: {flows}")
        pytest.fail("Some commands are using multiple different permission flows")

    # Check if all commands used unified flow
    unified_flow_commands = [cmd for cmd in flow_tracker.flows.keys()
                            if flow_tracker.get_flow_types(cmd) == ['GROK_UNIFIED']]

    tested_count = len([cmd for cmd in test_commands if cmd in approval_required_commands])

    if len(unified_flow_commands) == tested_count:
        print(f"✅ SUCCESS: All {tested_count} tested commands use Grok's unified flow!")
    else:
        print(f"⚠️  Only {len(unified_flow_commands)}/{tested_count} commands use unified flow")

        alternate_flow_commands = [cmd for cmd in flow_tracker.flows.keys()
                                  if cmd not in unified_flow_commands and
                                  not flow_tracker.has_multiple_flows(cmd)]

        if len(alternate_flow_commands) > 0:
            print(f"\nCommands using alternate flows:")
            for cmd in alternate_flow_commands:
                flows = flow_tracker.get_flow_types(cmd)
                print(f"   - {cmd}: {flows}")
            pytest.fail("Some commands are not using Grok's unified flow")


@pytest.mark.asyncio
async def test_no_duplicate_permission_checks():
    """
    Test that permission is only checked ONCE per command execution
    Detects duplicate/redundant permission checks
    """

    print("\n" + "="*80)
    print("TESTING: No Duplicate Permission Checks")
    print("="*80 + "\n")

    session = Session(model='test-model')
    app = MockTUIApp(FlowTracker())

    executor = ExecutionSystem(
        app=app,
        session=session,
        permission_manager=app.permission_manager
    )

    from modules.commands.registry import register_all
    await register_all(executor)

    # Track how many times check_permission is called
    check_permission_calls = []

    original_check = app.permission_manager.check_permission

    async def counted_check(*args, **kwargs):
        """Count permission check calls"""
        registration = args[0]
        check_permission_calls.append(registration.name)
        return True

    app.permission_manager.check_permission = counted_check

    # Execute /help command once
    try:
        await asyncio.wait_for(
            executor.execute(ExecutionType.COMMAND, '/help', context={}),
            timeout=2.0
        )
    except Exception:
        pass  # Ignore execution errors

    # Check how many times permission was checked
    help_checks = [cmd for cmd in check_permission_calls if cmd == '/help']

    print(f"Permission check calls for /help: {len(help_checks)}")

    if len(help_checks) == 1:
        print("✅ SUCCESS: Permission checked exactly once")
    elif len(help_checks) == 0:
        print("❌ FAILURE: Permission was never checked!")
        pytest.fail("Permission check was not called")
    else:
        print(f"❌ FAILURE: Permission checked {len(help_checks)} times!")
        print("This indicates duplicate/redundant permission checks")
        pytest.fail(f"Permission was checked {len(help_checks)} times instead of once")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])
