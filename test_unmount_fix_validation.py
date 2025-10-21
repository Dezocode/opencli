#!/usr/bin/env python3
"""
Pytest to validate the on_unmount double-call fix is in runtime
Tests that old cached code is not being used
"""

import pytest
import sys
import asyncio
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
import inspect

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


class TestUnmountFixValidation:
    """Validate the on_unmount fix is present in runtime code"""

    def test_async_core_has_fix(self):
        """Test that async_interactive/core.py has the fix (no manual on_unmount)"""
        from modules.async_interactive import core

        # Read the source code of interactive_async function
        source = inspect.getsource(core.interactive_async)

        print("\n" + "="*80)
        print("CHECKING SOURCE CODE FOR FIX")
        print("="*80)

        # The fix should include this comment
        assert "# NOTE: Textual handles cleanup automatically via on_unmount()" in source, \
            "❌ Fix comment not found - old code may be running!"

        # The fix should NOT have manual on_unmount call in finally block
        assert "if hasattr(app, 'on_unmount'):" not in source or \
               source.find("if hasattr(app, 'on_unmount'):") < source.find("# NOTE: Textual handles cleanup"), \
            "❌ Manual on_unmount call still present - old code detected!"

        # The fix should have new logging
        assert "[TUI] Starting app.run_async()..." in source, \
            "❌ New startup logging not found - old code may be running!"

        assert "[TUI] TUI shutdown complete" in source, \
            "❌ New shutdown logging not found - old code may be running!"

        print("✅ Source code contains the fix")
        print(f"   - Fix comment present: YES")
        print(f"   - Manual on_unmount removed: YES")
        print(f"   - New logging added: YES")
        print("="*80 + "\n")

    def test_runtime_module_path(self):
        """Test that we're importing from the correct module path"""
        from modules.async_interactive import core

        module_file = Path(core.__file__)

        print("\n" + "="*80)
        print("RUNTIME MODULE PATH CHECK")
        print("="*80)
        print(f"Module file: {module_file}")

        # Should be in main opencli directory, not .cursor worktree
        assert ".cursor" not in str(module_file), \
            f"❌ Importing from cursor worktree: {module_file}"

        assert "opencli/modules/async_interactive" in str(module_file), \
            f"❌ Unexpected module path: {module_file}"

        print(f"✅ Importing from correct path")
        print(f"   Location: {module_file}")
        print("="*80 + "\n")

    @pytest.mark.asyncio
    async def test_on_unmount_called_once(self):
        """Test that on_unmount is only called once during TUI shutdown"""

        print("\n" + "="*80)
        print("TESTING ON_UNMOUNT CALL COUNT")
        print("="*80)

        # Track on_unmount calls
        unmount_calls = []

        # Mock OpenCLITUI
        from modules.tui.core import OpenCLITUI

        original_on_unmount = OpenCLITUI.on_unmount

        async def tracked_on_unmount(self):
            """Track when on_unmount is called"""
            unmount_calls.append({
                'timestamp': asyncio.get_event_loop().time(),
                'instance': id(self)
            })
            print(f"[TRACK] on_unmount called (call #{len(unmount_calls)})")
            # Don't actually run cleanup in test

        # Mock run_async to exit immediately
        async def mock_run_async(self):
            """Mock run_async that exits immediately"""
            print("[MOCK] run_async called")
            await asyncio.sleep(0.1)
            print("[MOCK] run_async completing")
            # Textual would normally call on_unmount here
            await tracked_on_unmount(self)

        # Mock client creation
        async def mock_create_async_client(config):
            """Mock client creation"""
            print("[MOCK] create_async_client called")
            return MagicMock()

        # Mock setup_permissions
        async def mock_setup_permissions(session):
            """Mock permission setup"""
            print("[MOCK] setup_permissions called")

        # Apply patches
        with patch('modules.async_interactive.core.create_async_client', mock_create_async_client):
            with patch('modules.async_interactive.core.setup_permissions', mock_setup_permissions):
                with patch.object(OpenCLITUI, 'on_unmount', tracked_on_unmount):
                    with patch.object(OpenCLITUI, 'run_async', mock_run_async):
                        # Run interactive_async
                        from modules.async_interactive import interactive_async

                        config = {
                            "model": "gpt-4",
                            "apiKey": "test",
                            "baseURL": "https://api.openai.com/v1"
                        }
                        from cli.session import Session
                        session = Session(model="gpt-4")

                        # Suppress stderr during test
                        with patch('sys.stderr'):
                            await interactive_async(config, session)

        print(f"\nTotal on_unmount calls: {len(unmount_calls)}")

        # Assert only called once
        assert len(unmount_calls) == 1, \
            f"❌ on_unmount called {len(unmount_calls)} times (expected 1) - Double unmount still happening!"

        print("✅ on_unmount only called once - Fix working!")
        print("="*80 + "\n")

    def test_file_modification_time(self):
        """Check when the core.py file was last modified"""
        from modules.async_interactive import core
        import datetime

        module_file = Path(core.__file__)
        mod_time = datetime.datetime.fromtimestamp(module_file.stat().st_mtime)

        print("\n" + "="*80)
        print("FILE MODIFICATION TIME")
        print("="*80)
        print(f"File: {module_file}")
        print(f"Last modified: {mod_time}")
        print(f"Current time: {datetime.datetime.now()}")

        # Check if modified recently (within last hour)
        time_diff = datetime.datetime.now() - mod_time
        print(f"Time since modification: {time_diff}")

        if time_diff.total_seconds() < 3600:
            print("✅ File modified recently (< 1 hour ago)")
        else:
            print(f"⚠️  File modified {time_diff} ago - may be stale")

        print("="*80 + "\n")

    def test_compare_worktree_and_main(self):
        """Compare the two versions of core.py to ensure they match"""
        main_path = Path("/Users/dezmondhollins/opencli/modules/async_interactive/core.py")
        worktree_path = Path("/Users/dezmondhollins/.cursor/worktrees/opencli/1760885693580-9b0a9f/modules/async_interactive/core.py")

        print("\n" + "="*80)
        print("COMPARING MAIN AND WORKTREE FILES")
        print("="*80)

        if not main_path.exists():
            print("❌ Main file not found")
            pytest.skip("Main file not found")

        if not worktree_path.exists():
            print("⚠️  Worktree file not found")
            pytest.skip("Worktree file not found")

        main_content = main_path.read_text()
        worktree_content = worktree_path.read_text()

        # Check for fix markers in both
        fix_markers = [
            "# NOTE: Textual handles cleanup automatically",
            "[TUI] Starting app.run_async()...",
            "[TUI] TUI shutdown complete"
        ]

        main_has_fix = all(marker in main_content for marker in fix_markers)
        worktree_has_fix = all(marker in worktree_content for marker in fix_markers)

        print(f"Main file has fix: {'YES ✅' if main_has_fix else 'NO ❌'}")
        print(f"Worktree file has fix: {'YES ✅' if worktree_has_fix else 'NO ❌'}")

        if main_has_fix and worktree_has_fix:
            print("✅ Both files have the fix")
        elif main_has_fix:
            print("⚠️  Only main file has the fix")
        elif worktree_has_fix:
            print("⚠️  Only worktree file has the fix")
        else:
            print("❌ Neither file has the fix!")

        print("="*80 + "\n")

        assert main_has_fix, "Main file missing the fix!"

    @pytest.mark.asyncio
    async def test_no_finally_block_unmount(self):
        """Verify the finally block doesn't call on_unmount"""
        from modules.async_interactive import core

        source = inspect.getsource(core.interactive_async)

        print("\n" + "="*80)
        print("CHECKING FINALLY BLOCK")
        print("="*80)

        # Extract finally block if present
        if "finally:" in source:
            # Find finally block
            finally_start = source.find("finally:")
            if finally_start != -1:
                finally_block = source[finally_start:finally_start+500]
                print("Finally block found:")
                print("-" * 40)
                print(finally_block[:300])
                print("-" * 40)

                # Should NOT have on_unmount call
                assert "await app.on_unmount()" not in finally_block, \
                    "❌ Finally block still calls on_unmount!"

                print("✅ Finally block does NOT call on_unmount")
            else:
                print("⚠️  Finally block text found but not located")
        else:
            print("✅ No finally block present (even better!)")

        print("="*80 + "\n")


@pytest.mark.asyncio
async def test_full_tui_lifecycle():
    """Full integration test of TUI lifecycle"""

    print("\n" + "="*80)
    print("FULL TUI LIFECYCLE TEST")
    print("="*80)

    lifecycle_events = []

    from modules.tui.core import OpenCLITUI

    # Track lifecycle events
    original_on_mount = OpenCLITUI.on_mount
    original_on_unmount = OpenCLITUI.on_unmount

    def tracked_on_mount(self):
        lifecycle_events.append('on_mount')
        print("[LIFECYCLE] on_mount called")
        # Don't call actual mount in test

    async def tracked_on_unmount(self):
        lifecycle_events.append('on_unmount')
        print(f"[LIFECYCLE] on_unmount called (total: {lifecycle_events.count('on_unmount')})")
        # Don't call actual unmount in test

    async def mock_run_async(self):
        lifecycle_events.append('run_async_start')
        print("[LIFECYCLE] run_async started")
        await asyncio.sleep(0.05)
        lifecycle_events.append('run_async_end')
        print("[LIFECYCLE] run_async ending")
        # Simulate Textual calling on_unmount at end
        await tracked_on_unmount(self)

    # Mock client and permissions
    async def mock_create_async_client(config):
        print("[MOCK] create_async_client called")
        return MagicMock()

    async def mock_setup_permissions(session):
        print("[MOCK] setup_permissions called")

    with patch('modules.async_interactive.core.create_async_client', mock_create_async_client):
        with patch('modules.async_interactive.core.setup_permissions', mock_setup_permissions):
            with patch.object(OpenCLITUI, 'on_mount', tracked_on_mount):
                with patch.object(OpenCLITUI, 'on_unmount', tracked_on_unmount):
                    with patch.object(OpenCLITUI, 'run_async', mock_run_async):
                        from modules.async_interactive import interactive_async

                        config = {
                            "model": "gpt-4",
                            "apiKey": "test",
                            "baseURL": "https://api.openai.com/v1"
                        }
                        from cli.session import Session
                        session = Session(model="gpt-4")

                        with patch('sys.stderr'):
                            await interactive_async(config, session)

    print("\nLifecycle events:")
    for i, event in enumerate(lifecycle_events, 1):
        print(f"  {i}. {event}")

    # Count on_unmount calls
    unmount_count = lifecycle_events.count('on_unmount')
    print(f"\nTotal on_unmount calls: {unmount_count}")

    assert unmount_count == 1, \
        f"❌ on_unmount called {unmount_count} times! Expected 1. Old code still active!"

    print("✅ TUI lifecycle correct - on_unmount called exactly once")
    print("="*80 + "\n")


if __name__ == "__main__":
    # Run with verbose output
    pytest.main([__file__, "-v", "-s", "--tb=short"])
