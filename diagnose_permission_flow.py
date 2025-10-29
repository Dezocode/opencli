#!/usr/bin/env python3
"""
Diagnostic script to trace permission flow
Run this to verify the flow is working correctly
"""

import sys
import os

# Add repo to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_permission_flow_setup():
    """Test that all the fixes are in place"""
    
    print("=" * 60)
    print("Permission Flow Diagnostic")
    print("=" * 60)
    print()
    
    checks_passed = []
    checks_failed = []
    
    # Check 1: custom_prompt_func in metadata fix
    print("Check 1: Verifying custom_prompt_func metadata fix...")
    try:
        with open('modules/registry.py', 'r') as f:
            content = f.read()
            if 'custom_prompt_func = kwargs.pop' in content and 'metadata[\'custom_prompt_func\']' in content:
                print("  ✅ Fix 1 present: custom_prompt_func extracted to metadata")
                checks_passed.append("custom_prompt_func metadata fix")
            else:
                print("  ❌ Fix 1 missing: custom_prompt_func not moved to metadata")
                checks_failed.append("custom_prompt_func metadata fix")
    except Exception as e:
        print(f"  ❌ Error checking: {e}")
        checks_failed.append("custom_prompt_func metadata fix")
    
    print()
    
    # Check 2: handler_name stored in manager
    print("Check 2: Verifying handler_name storage fix...")
    try:
        with open('modules/permissions/integration.py', 'r') as f:
            content = f.read()
            if '_current_handler_name' in content and 'self._current_handler_name = handler_name' in content:
                print("  ✅ Fix 2 present: handler_name stored in manager")
                checks_passed.append("handler_name storage fix")
            else:
                print("  ❌ Fix 2 missing: handler_name not stored correctly")
                checks_failed.append("handler_name storage fix")
    except Exception as e:
        print(f"  ❌ Error checking: {e}")
        checks_failed.append("handler_name storage fix")
    
    print()
    
    # Check 3: Verify command registration
    print("Check 3: Checking if /help is registered correctly...")
    try:
        with open('modules/commands/command_registry.py', 'r') as f:
            content = f.read()
            lines = content.split('\n')
            found_help = False
            for i, line in enumerate(lines):
                if "'/help'" in line and "show_help" in line:
                    found_help = True
                    # Check next few lines for requires_approval and custom_prompt_func
                    context = '\n'.join(lines[i:i+5])
                    if 'requires_approval=True' in context:
                        print("  ✅ /help has requires_approval=True")
                    else:
                        print("  ❌ /help missing requires_approval=True")
                        checks_failed.append("/help requires_approval")
                    
                    if 'custom_prompt_func=show_help_prompt' in context:
                        print("  ✅ /help has custom_prompt_func")
                    else:
                        print("  ❌ /help missing custom_prompt_func")
                        checks_failed.append("/help custom_prompt_func")
                    break
            
            if found_help:
                checks_passed.append("/help registration")
            else:
                print("  ❌ /help registration not found")
                checks_failed.append("/help registration")
                
    except Exception as e:
        print(f"  ❌ Error checking: {e}")
        checks_failed.append("/help registration")
    
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"✅ Passed: {len(checks_passed)}")
    for check in checks_passed:
        print(f"   - {check}")
    print()
    print(f"❌ Failed: {len(checks_failed)}")
    for check in checks_failed:
        print(f"   - {check}")
    print()
    
    if not checks_failed:
        print("✅ All checks passed! Permission system should work.")
        print()
        print("If prompts still don't appear, the issue is likely:")
        print("  1. Executor not receiving app/session correctly")
        print("  2. UI callback not set in TUI")
        print("  3. Logs not being captured (stderr redirection issue)")
        return True
    else:
        print("❌ Some checks failed. Please review the fixes above.")
        return False


if __name__ == "__main__":
    success = test_permission_flow_setup()
    sys.exit(0 if success else 1)
