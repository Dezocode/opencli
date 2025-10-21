#!/usr/bin/env python3
"""Test that executor has valid app and session references"""

import sys
sys.path.insert(0, '/Users/dezmondhollins/.opencli')

from cli.session import Session
from modules.tui.core import OpenCLITUI
from modules.command_router import CommandRouter
from modules.execution.executor import get_executor

print("=" * 80)
print("TESTING EXECUTOR REFERENCES")
print("=" * 80)

# Create session and fake app
session = Session(model='test_model')

class FakeApp:
    def __init__(self):
        self.name = "FakeApp1"
    def query_one(self, *args):
        return None
    def set_focus(self, *args):
        pass
    def write(self, *args):
        pass

app1 = FakeApp()
print(f"\n[1] Created app1: {app1.name}")

# Create first router (should create executor)
print("\n[2] Creating first CommandRouter...")
router1 = CommandRouter(app1, session)
print(f"   router1.app = {router1.app.name}")
print(f"   router1.session = {router1.session}")
print(f"   router1.executor = {router1.executor}")
print(f"   router1.executor.app = {router1.executor.app.name if router1.executor.app else None}")
print(f"   router1.executor.session = {router1.executor.session}")

# Create second app
app2 = FakeApp()
app2.name = "FakeApp2"
print(f"\n[3] Created app2: {app2.name}")

# Create second router (should reuse executor - SINGLETON!)
print("\n[4] Creating second CommandRouter with app2...")
router2 = CommandRouter(app2, session)
print(f"   router2.app = {router2.app.name}")
print(f"   router2.session = {router2.session}")
print(f"   router2.executor = {router2.executor}")
print(f"   router2.executor.app = {router2.executor.app.name if router2.executor.app else None}")
print(f"   router2.executor.session = {router2.executor.session}")

# Check if executor is same instance
print(f"\n[5] router1.executor is router2.executor? {router1.executor is router2.executor}")

# THE ISSUE: executor still has app1, not app2!
if router2.executor.app.name == "FakeApp1":
    print(f"\n❌ ISSUE FOUND: router2.executor.app still points to FakeApp1!")
    print(f"   Expected: FakeApp2")
    print(f"   This explains why permission prompts fail!")
else:
    print(f"\n✅ executor.app correctly updated to {router2.executor.app.name}")

print("\n" + "=" * 80)
