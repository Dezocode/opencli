#!/usr/bin/env python3
"""
Test risk assessment system
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.permissions import RiskAssessmentManager, RiskLevel

def test_risk_assessment():
    """Test risk assessment functionality"""
    print("Testing Risk Assessment System\n")
    print("=" * 60)
    
    # Create manager
    manager = RiskAssessmentManager()
    
    # Test 1: Tool risk classification
    print("\n1. Tool Risk Classification:")
    print("-" * 60)
    tools = ['Read', 'Write', 'Edit', 'Bash', 'GitHub']
    for tool in tools:
        risk = manager.get_tool_risk(tool)
        print(f"  {tool:15} → {risk.value}")
    
    # Test 2: Path safety assessment
    print("\n2. Path Safety Assessment:")
    print("-" * 60)
    test_paths = [
        ("./local_file.txt", "/home/user/project"),
        ("../parent/file.txt", "/home/user/project"),
        ("/etc/hosts", "/home/user/project"),
        ("/home/user/.ssh/id_rsa", "/home/user/project"),
        ("/tmp/temp.txt", "/home/user/project"),
    ]
    
    for path, cwd in test_paths:
        risk, reason = manager.assess_path_risk(path, cwd)
        print(f"  Path: {path:30} → {risk.value:10} ({reason})")
    
    # Test 3: Operation risk assessment
    print("\n3. Operation Risk Assessment:")
    print("-" * 60)
    test_ops = [
        ("Read", {"file_path": "./local.txt"}, "/home/user/project"),
        ("Write", {"file_path": "/etc/hosts"}, "/home/user/project"),
        ("Edit", {"file_path": "../parent/file.txt"}, "/home/user/project"),
        ("Bash", {"command": "ls -la"}, "/home/user/project"),
    ]
    
    for tool, args, cwd in test_ops:
        risk, reason = manager.assess_operation_risk(tool, args, cwd)
        print(f"  {tool} {args.get('file_path', args.get('command', ''))[:20]:22} → {risk.value:10} ({reason})")
    
    # Test 4: Should prompt logic
    print("\n4. Should Prompt Decision:")
    print("-" * 60)
    for tool, args, cwd in test_ops:
        should_prompt, reason, risk = manager.should_prompt(tool, args, cwd)
        prompt_str = "YES" if should_prompt else "NO"
        print(f"  {tool} → Prompt: {prompt_str:3} | Risk: {risk.value:10} | {reason}")
    
    # Test 5: Allowed tools management
    print("\n5. Allowed Tools Management:")
    print("-" * 60)
    print(f"  Initially allowed: {manager.get_allowed_tools()}")
    manager.add_allowed_tool("Bash")
    print(f"  After adding Bash: {manager.get_allowed_tools()}")
    
    # Test with allowed tool
    should_prompt, reason, risk = manager.should_prompt("Bash", {"command": "ls"}, "/home/user")
    print(f"  Bash with safe path → Prompt: {'YES' if should_prompt else 'NO'} ({reason})")
    
    should_prompt, reason, risk = manager.should_prompt("Bash", {"command": "rm -rf /"}, "/home/user")
    print(f"  Bash (dangerous) → Prompt: {'YES' if should_prompt else 'NO'} ({reason})")
    
    manager.remove_allowed_tool("Bash")
    print(f"  After removing Bash: {manager.get_allowed_tools()}")
    
    # Test 6: Operation preview formatting
    print("\n6. Operation Preview Formatting:")
    print("-" * 60)
    preview = manager.format_operation_preview(
        "Edit",
        {"file_path": "/etc/hosts", "old_string": "127.0.0.1", "new_string": "0.0.0.0"},
        "/home/user/project"
    )
    print(preview)
    
    print("\n" + "=" * 60)
    print("✅ All tests completed successfully!")


if __name__ == "__main__":
    try:
        test_risk_assessment()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
