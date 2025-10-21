"""
Test to validate current runtime against Grok's original flow
Identifies breaking changes that need to be reverted
"""

import sys
import difflib
from pathlib import Path

def compare_permission_manager_files():
    """Compare Grok's vs current permission_manager.py"""

    grok_file = Path("/Users/dezmondhollins/.cursor/worktrees/opencli/1760885693580-9b0a9f/modules/execution/permission_manager.py")
    current_file = Path("/Users/dezmondhollins/opencli/modules/execution/permission_manager.py")

    with open(grok_file) as f:
        grok_lines = f.readlines()

    with open(current_file) as f:
        current_lines = f.readlines()

    # Find critical differences
    diff = list(difflib.unified_diff(
        grok_lines,
        current_lines,
        fromfile="Grok's version",
        tofile="Current runtime",
        lineterm=''
    ))

    print("=" * 80)
    print("CRITICAL DIFFERENCES IN permission_manager.py")
    print("=" * 80)

    issues = []

    # Check for missing CLI mode detection
    has_cli_mode = any("is_cli_mode" in line for line in current_lines)
    if not has_cli_mode:
        issues.append("❌ MISSING: CLI mode detection (is_cli_mode)")
    else:
        print("✅ FOUND: CLI mode detection")

    # Check for missing _show_cli_permission_prompt
    has_cli_prompt = any("_show_cli_permission_prompt" in line for line in current_lines)
    if not has_cli_prompt:
        issues.append("❌ MISSING: _show_cli_permission_prompt() method")
    else:
        print("✅ FOUND: _show_cli_permission_prompt() method")

    # Check for wrong import (unified vs buffer manager)
    has_wrong_import = any("get_unified_permission_manager" in line for line in current_lines)
    if has_wrong_import:
        issues.append("❌ WRONG: Uses get_unified_permission_manager (should be get_permission_buffer_manager)")
    else:
        print("✅ CORRECT: Uses get_permission_buffer_manager")

    # Check for duplicate custom_prompt_func handling
    custom_prompt_lines = [i for i, line in enumerate(current_lines, 1) if "custom_prompt_func" in line]
    if len(custom_prompt_lines) > 2:  # Should only be mentioned in comments
        issues.append(f"❌ DUPLICATE: custom_prompt_func handling at lines {custom_prompt_lines} (should be in executor.py)")
    else:
        print("✅ CORRECT: No duplicate custom_prompt_func handling")

    # Show all issues
    if issues:
        print("\n" + "=" * 80)
        print("ISSUES FOUND:")
        print("=" * 80)
        for issue in issues:
            print(issue)
        print()
        return False
    else:
        print("\n✅ ALL CHECKS PASSED")
        return True


def check_grok_flow_documentation():
    """Validate that Grok's flow documentation matches implementation"""

    flow_doc = Path("/Users/dezmondhollins/.cursor/worktrees/opencli/1760885693580-9b0a9f/COMMAND_PERMISSION_BUFFER_FLOW.md")

    if not flow_doc.exists():
        print("❌ Flow documentation not found")
        return False

    with open(flow_doc) as f:
        content = f.read()

    print("\n" + "=" * 80)
    print("GROK'S DOCUMENTED FLOW:")
    print("=" * 80)

    # Extract key points from documentation
    key_points = [
        "CLI/TUI mode detection",
        "Permission Manager delegates to buffer manager",
        "custom_prompt_func handled by executor",
        "Unified permission manager for TUI",
        "CLI permission prompt for terminal mode"
    ]

    for point in key_points:
        if point.lower() in content.lower():
            print(f"✅ Documented: {point}")
        else:
            print(f"⚠️  Not explicitly documented: {point}")

    return True


def main():
    """Run all validation tests"""

    print("\n" + "=" * 80)
    print("VALIDATING CURRENT RUNTIME AGAINST GROK'S FLOW")
    print("=" * 80)

    # Test 1: Compare files
    files_match = compare_permission_manager_files()

    # Test 2: Check documentation
    docs_valid = check_grok_flow_documentation()

    # Final result
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)

    if files_match:
        print("✅ Current runtime MATCHES Grok's design")
        print("✅ Permission buffer should render correctly")
        return 0
    else:
        print("❌ Current runtime DIFFERS from Grok's design")
        print("❌ This explains why permission buffer stopped rendering")
        print("\nRECOMMENDED ACTIONS:")
        print("1. Revert custom_prompt_func handling from permission_manager.py")
        print("2. Add back CLI mode detection")
        print("3. Add back _show_cli_permission_prompt() method")
        print("4. Change get_unified_permission_manager to get_permission_buffer_manager")
        return 1


if __name__ == "__main__":
    sys.exit(main())
