"""
Dual Buffer System - Separate streaming for commands and tool outputs

Architecture:
- CommandBuffer: Immediate writes for system messages, chat, debug
- ToolBuffer: Smooth streaming for tool execution results
- Both coordinate to prevent interleaving
"""

import asyncio
from typing import Optional, Dict, Any
from collections import deque
from rich.text import Text


class ToolBuffer:
    """
    Streaming buffer for tool execution output.

    Features:
    - Smooth character-by-character streaming
    - Collapsible sections
    - Visual indicators (⏺ for running, ✓ for complete)
    """

    def __init__(self, app, tool_name: str, tool_args: Dict[str, Any]):
        self.app = app
        self.tool_name = tool_name
        self.tool_args = tool_args
        self.output = ""
        self.streaming = False
        self.complete = False
        self.collapsed = False

        # Visual state
        self.status_line = None
        self.output_lines = []

    async def start(self):
        """Start tool execution display"""
        self.streaming = True

        # Format args for display
        args_str = ", ".join(f"{k}={v}" for k, v in self.tool_args.items())
        self.status_line = f"⏺ {self.tool_name}({args_str})"

        # Write status
        content = self.app._resolve_content_widget()
        if content and hasattr(content, '_lines'):
            status_text = Text()
            status_text.append(self.status_line, style="cyan bold")
            content._lines.append(status_text)
            self._refresh_display()

    async def write_chunk(self, text: str):
        """Stream a chunk of tool output"""
        if not text:
            return

        self.output += text

        # Update display with new output
        content = self.app._resolve_content_widget()
        if content and hasattr(content, '_lines'):
            # Add indented output line
            output_text = Text()
            output_text.append("  ⎿  ", style="dim")
            output_text.append(text, style="default")

            self.output_lines.append(output_text)
            self._refresh_display()

        await asyncio.sleep(0)  # Yield

    async def finish(self, success: bool = True):
        """Mark tool execution complete"""
        self.streaming = False
        self.complete = True

        # Update status indicator
        indicator = "✓" if success else "✗"
        color = "green" if success else "red"

        args_str = ", ".join(f"{k}={v}" for k, v in self.tool_args.items())
        self.status_line = f"{indicator} {self.tool_name}({args_str})"

        # Update first line with completion status
        content = self.app._resolve_content_widget()
        if content and hasattr(content, '_lines'):
            # Find and update the status line
            for i, line in enumerate(content._lines):
                if isinstance(line, Text) and self.tool_name in line.plain:
                    status_text = Text()
                    status_text.append(self.status_line, style=f"{color} bold")
                    content._lines[i] = status_text
                    break

            self._refresh_display()

    def _refresh_display(self):
        """Rebuild and update the display"""
        content = self.app._resolve_content_widget()
        if content and hasattr(content, 'update'):
            display_text = Text()
            for line in content._lines:
                if isinstance(line, Text):
                    display_text.append_text(line)
                else:
                    display_text.append(str(line))
                display_text.append("\n")
            content.update(display_text)


class CommandBuffer:
    """
    Immediate write buffer for system messages, chat, debug output.

    Features:
    - No delay - appears instantly
    - Markdown rendering
    - Direct writes
    """

    def __init__(self, app):
        self.app = app

    async def write(self, text: str, markdown: bool = False, style: str = "default"):
        """
        Write immediately to display.

        Args:
            text: Text to write
            markdown: Render as markdown
            style: Rich style string
        """
        if markdown and not text.startswith("["):
            # Render as markdown
            try:
                from markdown_renderer import get_markdown_renderer
                renderer = get_markdown_renderer()
                rendered = renderer.render(text)

                content = self.app._resolve_content_widget()
                if content and hasattr(content, '_lines'):
                    content._lines.append(rendered)
                    self._refresh_display()
                else:
                    self.app.write(text)
            except:
                self.app.write(text)
        else:
            # Direct write with style
            content = self.app._resolve_content_widget()
            if content and hasattr(content, '_lines'):
                line_text = Text()
                line_text.append(text, style=style)
                content._lines.append(line_text)
                self._refresh_display()
            else:
                self.app.write(text)

        await asyncio.sleep(0)  # Yield

    def _refresh_display(self):
        """Rebuild and update the display"""
        content = self.app._resolve_content_widget()
        if content and hasattr(content, 'update'):
            display_text = Text()
            for line in content._lines:
                if isinstance(line, Text):
                    display_text.append_text(line)
                else:
                    display_text.append(str(line))
                display_text.append("\n")
            content.update(display_text)


class DualBufferCoordinator:
    """
    Coordinates CommandBuffer and ToolBuffer to prevent conflicts.

    Usage:
        coordinator = DualBufferCoordinator(app)

        # System message
        await coordinator.write_command("Model loaded")

        # Tool execution
        tool_buf = await coordinator.start_tool("Bash", {"command": "ls"})
        await tool_buf.write_chunk("file1.py\n")
        await tool_buf.write_chunk("file2.py\n")
        await tool_buf.finish()
    """

    def __init__(self, app):
        self.app = app
        self.command_buffer = CommandBuffer(app)
        self.active_tool_buffers: Dict[str, ToolBuffer] = {}
        self._write_lock = asyncio.Lock()

    async def write_command(self, text: str, markdown: bool = False, style: str = "default"):
        """
        Write to command buffer (immediate).

        Args:
            text: Text to write
            markdown: Render as markdown
            style: Rich style
        """
        async with self._write_lock:
            await self.command_buffer.write(text, markdown=markdown, style=style)

    async def start_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> ToolBuffer:
        """
        Start a new tool execution buffer.

        Args:
            tool_name: Name of the tool (e.g., "Bash", "Read")
            tool_args: Tool arguments

        Returns:
            ToolBuffer instance for streaming output
        """
        async with self._write_lock:
            tool_id = f"{tool_name}_{len(self.active_tool_buffers)}"
            tool_buffer = ToolBuffer(self.app, tool_name, tool_args)
            self.active_tool_buffers[tool_id] = tool_buffer
            await tool_buffer.start()
            return tool_buffer

    async def finish_tool(self, tool_buffer: ToolBuffer, success: bool = True):
        """
        Finish a tool execution buffer.

        Args:
            tool_buffer: The ToolBuffer instance
            success: Whether execution succeeded
        """
        async with self._write_lock:
            await tool_buffer.finish(success)

            # Remove from active buffers
            for tool_id, buf in list(self.active_tool_buffers.items()):
                if buf is tool_buffer:
                    del self.active_tool_buffers[tool_id]
                    break
