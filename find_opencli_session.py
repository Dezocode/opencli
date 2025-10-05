#!/usr/bin/env python3
"""
Find Active OpenCLI Sessions
Scans for available IPC sockets
"""

import os
from pathlib import Path


def find_active_sessions():
    """Find all active OpenCLI IPC sessions"""
    socket_dir = Path("/tmp/opencli")

    if not socket_dir.exists():
        return []

    sessions = []
    for socket_file in socket_dir.glob("opencli_*.sock"):
        # Extract session ID from filename
        # Format: opencli_{session_id}.sock
        filename = socket_file.name
        if filename.startswith("opencli_") and filename.endswith(".sock"):
            session_id = filename[8:-5]  # Remove "opencli_" prefix and ".sock" suffix
            sessions.append({
                "session_id": session_id,
                "socket_path": str(socket_file),
                "exists": socket_file.exists()
            })

    return sessions


if __name__ == "__main__":
    print("🔍 Scanning for active OpenCLI sessions...\n")

    sessions = find_active_sessions()

    if not sessions:
        print("❌ No active sessions found")
        print("\nTo start an IPC server:")
        print("  1. Run OpenCLI")
        print("  2. Use /api start command")
        print("  3. The session ID will be displayed")
    else:
        print(f"✓ Found {len(sessions)} active session(s):\n")
        for i, session in enumerate(sessions, 1):
            print(f"{i}. Session ID: {session['session_id']}")
            print(f"   Socket: {session['socket_path']}")
            print(f"   Status: {'✓ Active' if session['exists'] else '✗ Inactive'}")
            print()

        print("To connect Claude Code to a session:")
        print(f"  python3 claude_code_bridge.py {sessions[0]['session_id']}")
