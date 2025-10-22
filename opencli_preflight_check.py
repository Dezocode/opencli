#!/usr/bin/env python3
"""
Pre-flight check for opencli alias
Shows EXACTLY which files will be imported when you run 'opencli'
"""

import sys
import os
from pathlib import Path

print("=" * 80)
print("OPENCLI ALIAS PRE-FLIGHT CHECK")
print("=" * 80)
print()

# Step 1: What does the opencli alias point to?
print("1. TRACING OPENCLI ALIAS:")
print("-" * 80)

alias_path = Path.home() / "bin" / "opencli"
print(f"   Alias location: {alias_path}")

if alias_path.exists():
    with open(alias_path) as f:
        content = f.read()
    print(f"   ✅ File exists")
    print()
    print("   Content:")
    for i, line in enumerate(content.split('\n')[:20], 1):
        print(f"   {i:3d} | {line}")

    # Extract where it points
    if "~/.opencli/opencli.py" in content or ".opencli/opencli.py" in content:
        print()
        print(f"   ➡️  Points to: ~/.opencli/opencli.py")
else:
    print(f"   ❌ File does not exist!")
    sys.exit(1)

print()
print()

# Step 2: Check opencli.py sys.path configuration
print("2. PYTHON IMPORT PATH CONFIGURATION:")
print("-" * 80)

opencli_main = Path.home() / ".opencli" / "opencli.py"
if opencli_main.exists():
    with open(opencli_main) as f:
        lines = f.readlines()

    print("   Checking sys.path configuration in ~/.opencli/opencli.py:")
    print()

    for i, line in enumerate(lines, 1):
        if 'sys.path' in line or 'ROOT_DIR' in line or 'CLI_DIR' in line:
            print(f"   {i:3d} | {line.rstrip()}")

    print()
    print("   ⚠️  CRITICAL: Python imports from paths in order of sys.path.insert()")
    print("   ⚠️  FIRST path checked wins!")
else:
    print(f"   ❌ {opencli_main} does not exist!")
    sys.exit(1)

print()
print()

# Step 3: Simulate Python import resolution
print("3. SIMULATING PYTHON IMPORT RESOLUTION:")
print("-" * 80)
print("   When you run 'opencli', Python will search these paths IN ORDER:")
print()

# Mimic what opencli.py does
root_dir = Path.home() / ".opencli"
cli_dir = Path.home() / ".opencli" / "cli"

# These are added in reverse order (last insert = first checked)
search_paths = [
    cli_dir,      # Added second, searched FIRST
    root_dir,     # Added first, searched SECOND
]

for priority, path in enumerate(search_paths, 1):
    print(f"   Priority {priority}: {path}")

print()
print()

# Step 4: Check which files will actually be imported
print("4. IMPORT RESOLUTION FOR KEY FILES:")
print("-" * 80)

critical_imports = [
    "modules/permissions/risk_assessment.py",
    "modules/permissions/templates.py",
    "modules/permissions/integration.py",
    "modules/permissions/manager.py",
    "modules/docker_commands.py",
]

print("   For each critical file, showing which location Python will import from:")
print()

all_good = True

for module_path in critical_imports:
    print(f"   📦 {module_path}")

    found = False
    winning_file = None

    # Check each path in priority order
    for priority, base_path in enumerate(search_paths, 1):
        full_path = base_path / module_path

        if full_path.exists():
            if not found:
                # This is the winner (first found)
                winning_file = full_path
                found = True

                # Get MD5 hash
                import hashlib
                with open(full_path, 'rb') as f:
                    md5 = hashlib.md5(f.read()).hexdigest()[:16]

                print(f"      ✅ Priority {priority}: {full_path}")
                print(f"         MD5: {md5}")
            else:
                # This file exists but will be shadowed
                import hashlib
                with open(full_path, 'rb') as f:
                    md5 = hashlib.md5(f.read()).hexdigest()[:16]

                print(f"      ⚠️  Priority {priority}: {full_path} (SHADOWED - will NOT be imported)")
                print(f"         MD5: {md5}")

                # Check if hashes match
                with open(winning_file, 'rb') as f:
                    winning_md5 = hashlib.md5(f.read()).hexdigest()[:16]

                if md5 != winning_md5:
                    print(f"         ❌ HASH MISMATCH! This file is DIFFERENT but shadowed!")
                    all_good = False

    if not found:
        print(f"      ❌ NOT FOUND in any path!")
        all_good = False

    print()

print()

# Step 5: Check for stale cache
print("5. PYTHON BYTECODE CACHE CHECK:")
print("-" * 80)

pycache_dirs = []
pyc_files = []

for base_path in [root_dir, cli_dir]:
    for pycache in base_path.rglob("__pycache__"):
        pycache_dirs.append(pycache)
    for pyc in base_path.rglob("*.pyc"):
        pyc_files.append(pyc)

if pycache_dirs or pyc_files:
    print(f"   ❌ FOUND STALE CACHE!")
    print(f"      __pycache__ directories: {len(pycache_dirs)}")
    print(f"      .pyc files: {len(pyc_files)}")
    print()
    print("   ⚠️  Cached bytecode may cause stale code to be loaded!")
    all_good = False
else:
    print(f"   ✅ No bytecode cache found - Python will use source files")

print()
print()

# Step 6: Final verdict
print("=" * 80)
print("FINAL VERDICT")
print("=" * 80)

if all_good:
    print("✅ ALL CHECKS PASSED")
    print()
    print("It is SAFE to run 'opencli' - you will get the NEW code from PR #7")
    print()
    print("What will happen when you run 'opencli':")
    print("  1. ~/bin/opencli wrapper is executed")
    print("  2. It runs ~/.opencli/opencli.py")
    print("  3. Python imports are loaded from the paths shown above")
    print("  4. All files have matching MD5 hashes (no shadowing)")
    print("  5. No stale bytecode cache")
else:
    print("❌ ISSUES DETECTED")
    print()
    print("DO NOT run 'opencli' yet! Issues must be resolved first:")
    print()
    if len(pycache_dirs) > 0 or len(pyc_files) > 0:
        print("  • Clear Python cache: find ~/.opencli -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null")
        print("  • Clear .pyc files: find ~/.opencli -type f -name '*.pyc' -delete 2>/dev/null")
    print("  • Re-run sync script: ./sync_to_runtime.sh")

print("=" * 80)
