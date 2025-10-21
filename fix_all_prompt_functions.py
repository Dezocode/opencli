#!/usr/bin/env python3
"""
Fix all custom prompt functions to be synchronous and return data only.
This fixes the deadlock where async prompt functions block the UI.
"""

import re
from pathlib import Path

def fix_prompt_function(content: str) -> tuple[str, int]:
    """
    Fix all custom prompt functions in the given content.

    Changes:
    1. async def xxx_prompt(...) → def xxx_prompt(...)
    2. Removes await buffer_manager.request_permission() calls
    3. Changes to return prompt_data

    Returns:
        (fixed_content, num_fixes)
    """

    fixes = 0

    # Pattern 1: Remove 'async' from prompt function definitions
    pattern1 = r'^(async\s+)(def\s+\w+_prompt\s*\()'
    content, count1 = re.subn(pattern1, r'\2', content, flags=re.MULTILINE)
    fixes += count1

    # Pattern 2: Replace buffer_manager.request_permission() with return prompt_data
    # Find all instances of:
    #     buffer_manager = get_permission_buffer_manager()
    #     return await buffer_manager.request_permission(app, session, prompt_data, timeout=30.0)
    # Replace with:
    #     return prompt_data

    pattern2 = r'\s+buffer_manager\s*=\s*get_permission_buffer_manager\(\)\s*\n\s+return\s+await\s+buffer_manager\.request_permission\([^)]+\)'
    content, count2 = re.subn(pattern2, '\n    return prompt_data', content)
    fixes += count2

    return content, fixes

def fix_file(file_path: Path) -> tuple[bool, int]:
    """Fix a single file. Returns (changed, num_fixes)"""

    try:
        content = file_path.read_text()
        fixed_content, num_fixes = fix_prompt_function(content)

        if num_fixes > 0:
            file_path.write_text(fixed_content)
            return True, num_fixes
        else:
            return False, 0
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False, 0

def main():
    """Fix all command files"""

    # Find all command files
    commands_dir = Path('/Users/dezmondhollins/opencli/modules/commands')
    command_files = list(commands_dir.glob('*_commands.py'))

    print("=" * 80)
    print("FIXING ALL CUSTOM PROMPT FUNCTIONS")
    print("=" * 80)
    print(f"\nFound {len(command_files)} command files\n")

    total_fixes = 0
    files_changed = 0

    for file_path in sorted(command_files):
        changed, num_fixes = fix_file(file_path)
        if changed:
            files_changed += 1
            total_fixes += num_fixes
            print(f"✓ {file_path.name}: {num_fixes} fixes applied")
        else:
            print(f"  {file_path.name}: no changes needed")

    print(f"\n{'=' * 80}")
    print(f"SUMMARY:")
    print(f"  Files changed: {files_changed}")
    print(f"  Total fixes: {total_fixes}")
    print(f"{'=' * 80}\n")

    # Now sync to runtime
    if total_fixes > 0:
        print("Syncing to runtime...")
        import shutil
        runtime_dir = Path('/Users/dezmondhollins/.opencli/modules/commands')
        runtime_dir.mkdir(parents=True, exist_ok=True)

        for file_path in command_files:
            dest = runtime_dir / file_path.name
            shutil.copy2(file_path, dest)
            print(f"  ✓ Synced {file_path.name}")

        print("\n✅ All files synced to runtime!")

if __name__ == '__main__':
    main()
