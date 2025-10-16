"""
UI handling utilities for async interactive mode
"""

import asyncio


async def async_write(app, text, end="\n"):
    """
    Write to app - direct queue + ALWAYS yield for responsiveness
    
    CRITICAL: Async wrapper for app.write() to prevent UI blocking
    """
    # app.write() already queues writes in background thread (simple_tui.py:756)
    # Call directly - no extra threading needed
    app.write(text, end=end)

    # CRITICAL: ALWAYS yield to keep UI responsive during fast streaming
    # The queue batching (simple_tui.py:660) handles write efficiency
    # This yield ensures UI can update between chunks
    await asyncio.sleep(0)


async def write_markdown_response(app, markdown_text):
    """Write a complete markdown response (replaces plain text streaming)"""
    # Get the content widget and use its markdown renderer
    content = app._resolve_content_widget()
    
    if hasattr(content, 'write_markdown'):
        # Use the advanced markdown renderer if available
        await content.write_markdown(markdown_text)
    else:
        # Fallback to plain text
        await async_write(app, markdown_text)