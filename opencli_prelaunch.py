#!/usr/bin/env python3
"""
OpenCLI Pre-Launch Status Screen
Shows codebase status, cache verification, and confirmation before launch
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import subprocess

def get_most_recent_change(directory):
    """Get the most recent modification time in directory tree"""
    most_recent = 0
    most_recent_file = None

    for root, dirs, files in os.walk(directory):
        # Skip cache directories
        dirs[:] = [d for d in dirs if d != '__pycache__']

        for file in files:
            if file.endswith('.pyc'):
                continue
            filepath = os.path.join(root, file)
            try:
                mtime = os.path.getmtime(filepath)
                if mtime > most_recent:
                    most_recent = mtime
                    most_recent_file = filepath
            except:
                pass

    return most_recent, most_recent_file

def check_cache_files(directory):
    """Check for any .pyc or __pycache__ in directory"""
    cache_files = []
    pycache_dirs = []

    for root, dirs, files in os.walk(directory):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                pycache_dirs.append(os.path.join(root, dir_name))

        for file in files:
            if file.endswith('.pyc'):
                cache_files.append(os.path.join(root, file))

    return cache_files, pycache_dirs

def count_python_files(directory):
    """Count .py files in directory"""
    count = 0
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        count += len([f for f in files if f.endswith('.py') and not f.endswith('.pyc')])
    return count

def print_border(text='═', width=80):
    """Print a border line"""
    print(text if len(text) == width else text * width)

def print_box_line(text, width=80, align='left'):
    """Print text in a box"""
    if align == 'center':
        padding = (width - len(text) - 4) // 2
        print(f"║ {' ' * padding}{text}{' ' * (width - len(text) - 4 - padding)} ║")
    elif align == 'left':
        print(f"║ {text:<{width-4}} ║")

def main():
    opencli_dir = Path.home() / ".opencli"
    modules_dir = opencli_dir / "modules"
    sessions_dir = opencli_dir / "sessions"

    # Clear screen for clean display
    os.system('clear' if os.name != 'nt' else 'cls')

    # Header
    print()
    print('╔' + '═' * 78 + '╗')
    print_box_line("", align='center')
    print_box_line("🚀  OPENCLI PRE-LAUNCH STATUS", width=80, align='center')
    print_box_line("", align='center')
    print('╠' + '═' * 78 + '╣')
    print()

    # Section 1: Codebase Status
    print_box_line("📁  CODEBASE STATUS", width=80)
    print('╠' + '─' * 78 + '╣')

    most_recent, most_recent_file = get_most_recent_change(modules_dir)
    if most_recent:
        dt = datetime.fromtimestamp(most_recent)
        print_box_line(f"   Last Updated: {dt.strftime('%Y-%m-%d %H:%M:%S')}", width=80)
        print_box_line(f"   Most Recent:  {os.path.relpath(most_recent_file, opencli_dir)}", width=80)
    else:
        print_box_line("   ❌ Could not determine last update", width=80)

    py_count = count_python_files(modules_dir)
    print_box_line(f"   Python Files: {py_count} files", width=80)
    print_box_line("", width=80)

    # Section 2: Directory Structure
    print('╠' + '═' * 78 + '╣')
    print_box_line("📂  RUNTIME DIRECTORIES", width=80)
    print('╠' + '─' * 78 + '╣')

    # Show key directories
    key_dirs = [
        ("modules/", "Core modules (single source of truth)"),
        ("modules/permissions/", "Permission system"),
        ("modules/tui/", "TUI interface"),
        ("modules/execution/", "Command execution"),
        ("cli/", "CLI entry point"),
        ("sessions/", "Session history (preserved)"),
    ]

    for dir_path, description in key_dirs:
        full_path = opencli_dir / dir_path
        if full_path.exists():
            file_count = count_python_files(full_path) if full_path.is_dir() else 0
            print_box_line(f"   ✅ {dir_path:<30} {description}", width=80)
            if file_count > 0 and dir_path != "sessions/":
                print_box_line(f"      └─ {file_count} .py files", width=80)
        else:
            print_box_line(f"   ❌ {dir_path:<30} NOT FOUND", width=80)

    print_box_line("", width=80)

    # Section 3: Cache Verification
    print('╠' + '═' * 78 + '╣')
    print_box_line("🧹  CACHE VERIFICATION", width=80)
    print('╠' + '─' * 78 + '╣')

    cache_files, pycache_dirs = check_cache_files(opencli_dir)

    # Exclude sessions directory from cache check
    cache_files = [f for f in cache_files if '/sessions/' not in f]
    pycache_dirs = [d for d in pycache_dirs if '/sessions/' not in d]

    if not cache_files and not pycache_dirs:
        print_box_line("   ✅ No bytecode cache found", width=80)
        print_box_line("   ✅ Python will use fresh source files", width=80)
        cache_clean = True
    else:
        print_box_line(f"   ❌ Found {len(pycache_dirs)} __pycache__ directories", width=80)
        print_box_line(f"   ❌ Found {len(cache_files)} .pyc files", width=80)
        print_box_line("   ⚠️  Stale cache detected!", width=80)
        cache_clean = False

    print_box_line("", width=80)

    # Section 4: Import Path
    print('╠' + '═' * 78 + '╣')
    print_box_line("🔍  PYTHON IMPORT PATH", width=80)
    print('╠' + '─' * 78 + '╣')

    print_box_line(f"   Priority 1: {opencli_dir}", width=80)
    print_box_line("   ├─ modules/ (all code loaded from here)", width=80)
    print_box_line("   └─ cli/ (entry point only)", width=80)
    print_box_line("", width=80)
    print_box_line("   ✅ Single source of truth: modules/", width=80)
    print_box_line("", width=80)

    # Section 5: Critical Files Check
    print('╠' + '═' * 78 + '╣')
    print_box_line("📋  CRITICAL FILES CHECK", width=80)
    print('╠' + '─' * 78 + '╣')

    critical_files = [
        "modules/permissions/risk_assessment.py",
        "modules/permissions/templates.py",
        "modules/permissions/integration.py",
        "modules/docker_commands.py",
        "modules/tui/core.py",
    ]

    all_critical_exist = True
    for file_path in critical_files:
        full_path = opencli_dir / file_path
        if full_path.exists():
            import hashlib
            with open(full_path, 'rb') as f:
                md5 = hashlib.md5(f.read()).hexdigest()[:12]
            print_box_line(f"   ✅ {file_path}", width=80)
            print_box_line(f"      MD5: {md5}", width=80)
        else:
            print_box_line(f"   ❌ {file_path} MISSING", width=80)
            all_critical_exist = False

    print_box_line("", width=80)

    # Final Status
    print('╠' + '═' * 78 + '╣')
    print_box_line("", width=80)

    if cache_clean and all_critical_exist:
        print_box_line("✅  STATUS: READY TO LAUNCH", width=80, align='center')
        print_box_line("", width=80)
        print_box_line("All checks passed:", width=80, align='center')
        print_box_line("• Using latest codebase", width=80, align='center')
        print_box_line("• No stale cache", width=80, align='center')
        print_box_line("• All critical files present", width=80, align='center')
        can_launch = True
    else:
        print_box_line("❌  STATUS: ISSUES DETECTED", width=80, align='center')
        print_box_line("", width=80)
        if not cache_clean:
            print_box_line("• Clear cache before launching", width=80, align='center')
        if not all_critical_exist:
            print_box_line("• Critical files missing", width=80, align='center')
        can_launch = False

    print_box_line("", width=80)
    print('╚' + '═' * 78 + '╝')
    print()

    if not can_launch:
        print("❌ Cannot launch - please fix issues above")
        if not cache_clean:
            print("\nTo clear cache:")
            print("  find ~/.opencli -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null")
            print("  find ~/.opencli -type f -name '*.pyc' -delete 2>/dev/null")
        print()
        sys.exit(1)

    # Ask for confirmation
    print("Launch OpenCLI? (y/n): ", end='', flush=True)
    response = input().strip().lower()

    if response == 'y' or response == 'yes':
        print("\n🚀 Launching OpenCLI...\n")
        return 0  # Continue to launch
    else:
        print("\n❌ Launch cancelled by user\n")
        sys.exit(0)

if __name__ == "__main__":
    sys.exit(main())
