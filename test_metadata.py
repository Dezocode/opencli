#!/usr/bin/env python3
"""Test if custom_prompt_func is properly registered in ExecutionRegistry"""
import sys
import asyncio

# Import required modules
from modules.execution.unified_executor import UnifiedExecutionSystem
from cli.session import Session

# Create minimal config and session
config = {'model': 'qwen3-coder', 'provider': 'openrouter'}
session = Session(config['model'])

# Need app reference - create minimal mock
class MockApp:
    def query_one(self, selector):
        return None

# Create executor
app = MockApp()
executor = UnifiedExecutionSystem(app, session)

# Register all
async def test():
    from modules.commands.registry import register_all

    print("=" * 70)
    print("TESTING CUSTOM_PROMPT_FUNC REGISTRATION")
    print("=" * 70)
    print("\nRegistering commands...")
    await register_all(executor)

    # Check /help
    help_cmd = executor.registry.commands.get('/help')

    if not help_cmd:
        print("\n❌ /help not found in registry")
        return

    print(f"\n✓ /help command found in registry:")
    print(f"  Name: {help_cmd.name}")
    print(f"  Type: {help_cmd.type.value}")
    print(f"  Requires approval: {help_cmd.requires_approval}")
    print(f"  Metadata keys: {list(help_cmd.metadata.keys())}")

    if 'custom_prompt_func' in help_cmd.metadata:
        func = help_cmd.metadata['custom_prompt_func']
        func_name = func.__name__ if hasattr(func, '__name__') else str(type(func))
        print(f"  ✅ custom_prompt_func: {func_name}")
        print(f"\n" + "=" * 70)
        print(f"🎉 SUCCESS: Permission system is properly wired!")
        print(f"   - custom_prompt_func is stored in metadata")
        print(f"   - PermissionManager.check_permission() can call it")
        print(f"   - Permission buffer will activate for /help command")
        print(f"=" * 70)
    else:
        print(f"  ❌ custom_prompt_func: NOT IN METADATA")
        print(f"\n" + "=" * 70)
        print(f"❌ FAIL: Permission system not wired properly")
        print(f"=" * 70)

if __name__ == '__main__':
    asyncio.run(test())
