#!/usr/bin/env python3
"""
Test to demonstrate prompt area is async from message area
"""
import asyncio
import sys
import os

# Add modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from simple_tui import OpenCLITUI
from collections import namedtuple

# Mock session
MockSession = namedtuple('Session', ['session_id', 'cwd', 'messages', 'model'])
session = MockSession(
    session_id='test-async-1234',
    cwd=os.getcwd(),
    messages=[],
    model='test-model'
)

# Mock config
config = {
    'model': 'test-model',
    'apiKey': 'test-key',
    'baseURL': 'test-url'
}

async def test_async_streaming():
    """Simulate API streaming to test async behavior"""
    app = OpenCLITUI(session=session, config=config)

    async def stream_messages():
        """Simulate streaming API response"""
        await asyncio.sleep(1)  # Wait for mount

        print("Starting simulated streaming...")
        message = "This is a simulated streaming response. " * 50

        # Stream character by character
        for char in message:
            app.write(char, end="")  # This should return INSTANTLY
            await asyncio.sleep(0.001)  # Tiny delay

        app.write("\n\n")  # End streaming
        print("Streaming complete!")

        # Give the UI time to render then exit cleanly for tests
        await asyncio.sleep(0.5)
        app.action_quit_app()

    # Set message handler
    async def handle_input(user_input: str):
        if user_input.lower() == 'test':
            await stream_messages()

    app.message_handler = handle_input
    app.initial_prompt = 'test'  # Auto-trigger streaming

    # Run app
    await app.run_async()

if __name__ == "__main__":
    print("=" * 60)
    print("ASYNC WRITE TEST - Background Thread Architecture")
    print("=" * 60)
    print()
    print("This test demonstrates:")
    print("  ✓ Prompt area completely decoupled from message area")
    print("  ✓ Write queue using thread-safe Queue")
    print("  ✓ Background thread processing writes independently")
    print("  ✓ Main event loop free for typing/scrolling")
    print()
    print("During streaming:")
    print("  - You SHOULD be able to type")
    print("  - You SHOULD be able to scroll")
    print("  - UI should remain responsive")
    print()
    print("=" * 60)
    print()

    asyncio.run(test_async_streaming())
