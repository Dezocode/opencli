#!/usr/bin/env python3
"""
Test script to verify all relative import fixes are working correctly.

This test verifies that:
1. All 16 target files can be imported without errors
2. Key dependencies resolve correctly
3. No relative imports remain in fixed files
"""

import sys
from pathlib import Path

# Add the repo root to path
repo_root = Path(__file__).parent
sys.path.insert(0, str(repo_root))

def test_command_module_imports():
    """Test that all command modules can be imported"""
    print("Testing command module imports...")
    
    command_modules = [
        'agent_commands', 'basic_commands', 'command_registry', 'command_router',
        'dev_commands', 'diff_commands', 'local_commands', 'model_commands',
        'provider_commands', 'registry', 'spec_commands', 'system_commands',
        'tool_registry'
    ]
    
    for module_name in command_modules:
        try:
            exec(f"from modules.commands import {module_name}")
            print(f"  ✅ {module_name}")
        except Exception as e:
            print(f"  ❌ {module_name}: {e}")
            return False
    
    return True

def test_other_module_imports():
    """Test that other fixed modules can be imported"""
    print("\nTesting other module imports...")
    
    tests = [
        ("async_interactive.core", "from modules.async_interactive import core"),
        ("tools.core_tools", "from modules.tools import core_tools"),
        ("tui.command_handlers", "from modules.tui import command_handlers"),
    ]
    
    for name, import_stmt in tests:
        try:
            exec(import_stmt)
            print(f"  ✅ {name}")
        except Exception as e:
            print(f"  ❌ {name}: {e}")
            return False
    
    return True

def test_key_dependencies():
    """Test that key dependencies resolve correctly"""
    print("\nTesting key dependencies...")
    
    try:
        from modules.permissions import PermissionResponse, get_permission_buffer_manager
        print(f"  ✅ permissions.PermissionResponse")
        print(f"  ✅ permissions.get_permission_buffer_manager")
    except Exception as e:
        print(f"  ❌ permissions: {e}")
        return False
    
    try:
        from modules.agent_manager import AgentManager
        print(f"  ✅ agent_manager.AgentManager")
    except Exception as e:
        print(f"  ❌ agent_manager: {e}")
        return False
    
    try:
        from modules.execution.registry import ExecutionType, ExecutionCategory, RiskLevel
        print(f"  ✅ execution.registry (ExecutionType, etc.)")
    except Exception as e:
        print(f"  ❌ execution.registry: {e}")
        return False
    
    try:
        from modules.sdk.enforcement import enforce_handler
        print(f"  ✅ sdk.enforcement.enforce_handler")
    except Exception as e:
        print(f"  ❌ sdk.enforcement: {e}")
        return False
    
    return True

def test_no_relative_imports():
    """Verify no relative imports remain in target files"""
    print("\nChecking for relative imports in target files...")
    
    target_files = [
        "modules/commands/agent_commands.py",
        "modules/commands/basic_commands.py",
        "modules/commands/command_registry.py",
        "modules/commands/command_router.py",
        "modules/commands/dev_commands.py",
        "modules/commands/diff_commands.py",
        "modules/commands/local_commands.py",
        "modules/commands/model_commands.py",
        "modules/commands/provider_commands.py",
        "modules/commands/registry.py",
        "modules/commands/spec_commands.py",
        "modules/commands/system_commands.py",
        "modules/commands/tool_registry.py",
        "modules/async_interactive/core.py",
        "modules/tools/core_tools.py",
        "modules/tui/command_handlers.py",
    ]
    
    import re
    all_clean = True
    
    for file_path in target_files:
        full_path = repo_root / file_path
        try:
            with open(full_path, 'r') as f:
                content = f.read()
                relative_imports = re.findall(r'^\s*from\s+\.\.', content, re.MULTILINE)
                if relative_imports:
                    print(f"  ❌ {file_path}: Found {len(relative_imports)} relative imports")
                    all_clean = False
                else:
                    print(f"  ✅ {file_path}: No relative imports")
        except Exception as e:
            print(f"  ⚠️  {file_path}: Error reading file: {e}")
            all_clean = False
    
    return all_clean

def main():
    """Run all tests"""
    print("=" * 70)
    print("OPENCLI IMPORT FIX VERIFICATION")
    print("=" * 70)
    
    results = []
    
    results.append(("Command Module Imports", test_command_module_imports()))
    results.append(("Other Module Imports", test_other_module_imports()))
    results.append(("Key Dependencies", test_key_dependencies()))
    results.append(("No Relative Imports", test_no_relative_imports()))
    
    print("\n" + "=" * 70)
    print("TEST RESULTS")
    print("=" * 70)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("=" * 70)
    
    if all_passed:
        print("✅ ALL TESTS PASSED")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
