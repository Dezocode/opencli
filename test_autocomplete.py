#!/usr/bin/env python3
"""Test command autocomplete system without running full CLI"""

import sys
from pathlib import Path

# Add modules directory to path
sys.path.insert(0, str(Path(__file__).parent / "modules"))

print("Testing Command Autocomplete Components\n" + "="*50)

# Test 1: Imports
print("\n1. Testing imports...")
try:
    from command_registry import CommandRegistry
    from command_suggestions import CommandMatch, CommandSuggestionBuffer
    from multiline_input import MultiLineInput
    print("   ✅ All imports successful")
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Command Registry Search
print("\n2. Testing CommandRegistry.search_commands()...")
try:
    registry = CommandRegistry()

    # Test search for '/mod'
    results = registry.search_commands('/mod')
    print(f"   Query: '/mod' → {len(results)} matches")
    for r in results[:3]:
        print(f"      {r['name']} (score: {r['score']})")

    # Test search for '/'
    results = registry.search_commands('/')
    print(f"   Query: '/' → {len(results)} total commands")

    print("   ✅ Search working")
except Exception as e:
    print(f"   ❌ Search failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: CommandMatch dataclass
print("\n3. Testing CommandMatch dataclass...")
try:
    match = CommandMatch(
        name='/test',
        description='Test command',
        category='basic',
        score=1000,
        usage_count=5
    )
    print(f"   Created: {match}")
    print("   ✅ CommandMatch working")
except Exception as e:
    print(f"   ❌ CommandMatch failed: {e}")
    sys.exit(1)

# Test 4: Message Types
print("\n4. Testing MultiLineInput message types...")
try:
    # Check that message types exist
    assert hasattr(MultiLineInput, 'ShowCommandSuggestions')
    assert hasattr(MultiLineInput, 'HideCommandSuggestions')
    assert hasattr(MultiLineInput, 'CommandSuggestionNavigate')
    assert hasattr(MultiLineInput, 'CommandSuggestionSelect')
    print("   ✅ All message types defined")
except Exception as e:
    print(f"   ❌ Message types missing: {e}")
    sys.exit(1)

# Test 5: Check watch_value method exists and has slash detection
print("\n5. Testing MultiLineInput.watch_value() slash detection...")
try:
    import inspect
    source = inspect.getsource(MultiLineInput.watch_value)

    if "new_value.startswith('/')" in source:
        print("   ✅ Slash detection code present")
    else:
        print("   ❌ Slash detection code missing!")
        sys.exit(1)

    if "ShowCommandSuggestions" in source:
        print("   ✅ ShowCommandSuggestions message posting present")
    else:
        print("   ❌ ShowCommandSuggestions message posting missing!")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ watch_value inspection failed: {e}")
    sys.exit(1)

print("\n" + "="*50)
print("✅ ALL TESTS PASSED")
print("\nIf autocomplete still doesn't work in CLI:")
print("1. Restart OpenCLI: python3 opencli.py")
print("2. Or use: ./dev-mode.sh (clears cache)")
print("3. Or type: /reload (hot-reload)")
print("4. Enable debug: export OPENCLI_DEBUG_AUTOCOMPLETE=1")
print("5. Check log: cat /tmp/opencli-autocomplete-debug.log")
