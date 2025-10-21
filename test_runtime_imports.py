#!/usr/bin/env python3
"""
Test which modules are actually being imported at runtime
"""

import sys
sys.path.insert(0, '/Users/dezmondhollins/.opencli')

print("="*80)
print("RUNTIME IMPORT TEST")
print("="*80)

# Test 1: Check execution module
print("\n1. Checking execution.permission_manager...")
try:
    from cli.modules.execution import permission_manager as pm
    print(f"  ✓ Module file: {pm.__file__}")

    # Check if it has our debug statements
    import inspect
    source = inspect.getsource(pm.PermissionManager.check_permission)
    if 'PermissionManager.check_permission] ===== ENTERED =====' in source:
        print(f"  ✓ Has our debug logging")
    else:
        print(f"  ✗ MISSING our debug logging!")
        print(f"  First 500 chars of check_permission:")
        print(source[:500])

except Exception as e:
    print(f"  ✗ ERROR: {e}")

# Test 2: Check permission_buffer_manager
print("\n2. Checking permission_buffer_manager...")
try:
    from cli.modules.permission_buffer_manager import get_permission_buffer_manager
    manager = get_permission_buffer_manager()
    print(f"  ✓ Manager type: {type(manager)}")
    print(f"  ✓ Manager from module: {manager.__class__.__module__}")

except Exception as e:
    print(f"  ✗ ERROR: {e}")

# Test 3: Check TUI imports
print("\n3. Checking TUI modules...")
try:
    from cli.modules.tui.core import OpenCLITUI
    print(f"  ✓ TUI module: {OpenCLITUI.__module__}")

    # Check permission system setup
    import inspect
    source = inspect.getsource(OpenCLITUI._setup_permission_system)
    if 'get_unified_permission_manager' in source:
        print(f"  ✓ Uses get_unified_permission_manager()")
    elif 'get_permission_buffer_manager' in source:
        print(f"  ⚠ Uses get_permission_buffer_manager() (old way)")
    else:
        print(f"  ✗ Unknown permission system!")

except Exception as e:
    print(f"  ✗ ERROR: {e}")

# Test 4: Check multiline_input
print("\n4. Checking multiline_input...")
try:
    from cli.modules.multiline_input import MultiLineInput
    print(f"  ✓ MultiLineInput from: {MultiLineInput.__module__}")

    # Check if it has permission_prompt_data
    if hasattr(MultiLineInput, 'permission_prompt_data'):
        print(f"  ✓ Has permission_prompt_data reactive property")
    else:
        print(f"  ✗ MISSING permission_prompt_data!")

except Exception as e:
    print(f"  ✗ ERROR: {e}")

print("\n" + "="*80)
