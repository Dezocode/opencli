#!/usr/bin/env python3
"""
Test script to verify single UnifiedPermissionManager instance
Phase 10: Verify Single Instance
"""

import sys
sys.path.insert(0, '/home/runner/work/opencli/opencli')

# Test multiple calls to get_unified_permission_manager
from modules.permissions import get_unified_permission_manager

print("=" * 60)
print("Testing Single Instance (Phase 10)")
print("=" * 60)

print("\n1. Getting first instance...")
manager1 = get_unified_permission_manager()
id1 = id(manager1)
print(f"   Instance 1 ID: {id1}")

print("\n2. Getting second instance...")
manager2 = get_unified_permission_manager()
id2 = id(manager2)
print(f"   Instance 2 ID: {id2}")

print("\n3. Getting third instance...")
manager3 = get_unified_permission_manager()
id3 = id(manager3)
print(f"   Instance 3 ID: {id3}")

print("\n" + "=" * 60)
if id1 == id2 == id3:
    print("✅ SUCCESS: Single instance verified!")
    print(f"   All three calls returned same instance: {id1}")
else:
    print("❌ FAILURE: Multiple instances detected!")
    print(f"   Instance 1: {id1}")
    print(f"   Instance 2: {id2}")
    print(f"   Instance 3: {id3}")
    sys.exit(1)

print("=" * 60)
