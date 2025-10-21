"""Response Generator Mixin - AI response generation logic

Handles all AI response generation including:
- API requests
- Streaming responses
- Tool execution
"""


class ResponseGeneratorMixin:
    """Mixin for generating AI responses in TUI"""

    async def _generate_ai_response(self) -> None:
        """Generate AI response using existing streaming infrastructure"""
        try:
            from ..async_interactive.api_requests import perform_anthropic_request, perform_google_request
            stream_display = self._resolve_content_widget()
            if not hasattr(stream_display, 'write_stream'):
                self.write("[dim]Streaming display not available[/dim]\n")
                return

            # Show streaming indicator and start streaming mode
            self.write("🔄 Thinking...")
            stream_display.write_stream("")

            # Prepare API request
            messages = self.session.get_messages()

            # Get tools for API request
            from ..async_interactive.tools import TOOLS

            # Use appropriate API based on model
            model = self.config.get("model", "")
            if "claude" in model.lower():
                response = await perform_anthropic_request(messages, self.config, tools=TOOLS)
            elif "gemini" in model.lower():
                response = await perform_google_request(messages, self.config, tools=TOOLS)
            else:
                # Default to OpenRouter
                from ..async_interactive.streaming import StreamHandler
                from ..async_interactive.tool_integration import get_tool_executor

                handler = StreamHandler()
                tool_executor = get_tool_executor(self, self.session)
                assistant_text = ""
                tool_calls = []

                async for chunk in handler.stream_openrouter(messages, self.config, tools=TOOLS):
                    if chunk.get("type") == "content":
                        content = chunk["content"]
                        assistant_text += content
                        stream_display.write_stream(content)  # Stream directly to display
                    elif chunk.get("type") == "tool_call":
                        # Handle tool calls
                        tool_calls.extend(chunk.get("tool_calls", []))
                    elif chunk.get("type") == "error":
                        stream_display.finish_stream()
                        self.write(f"[red]Error: {chunk['error']}[/red]\n")
                        raise Exception(chunk['error'])
                    elif chunk.get("type") == "done":
                        break

                # Finish text streaming
                stream_display.finish_stream()
                if assistant_text:
                    self.session.add('assistant', assistant_text)

                # Execute tool calls if any
                if tool_calls:
                    for tool_call in tool_calls:
                        try:
                            result = await tool_executor.execute_tool_call(tool_call, stream_display)
                            # Add tool result to session
                            self.session.add('tool', f"Tool {tool_call.get('name', 'Unknown')}: {result}")
                        except Exception as e:
                            self.write(f"[red]Tool execution error: {e}[/red]\n")
                return

            # Handle non-streaming responses
            if response.get("status") == "success":
                from ..async_interactive.tool_integration import get_tool_executor
                tool_executor = get_tool_executor(self, self.session)

                data = response["data"]
                content = data.get("content", [])

                if content and isinstance(content, list):
                    # Process content blocks
                    text_content = ""
                    tool_calls = []

                    for block in content:
                        if block.get("type") == "text":
                            text_content += block.get("text", "")
                        elif block.get("type") == "tool_use":
                            # Anthropic tool call format
                            tool_calls.append({
                                "name": block.get("name"),
                                "arguments": block.get("input", {})
                            })

                    # Show text response
                    if text_content:
                        self.session.add('assistant', text_content)
                        self.write(f"\n{text_content}\n")

                    # Execute tool calls
                    if tool_calls:
                        for tool_call in tool_calls:
                            try:
                                result = await tool_executor.execute_tool_call(tool_call, stream_display)
                                self.session.add('tool', f"Tool {tool_call.get('name', 'Unknown')}: {result}")
                            except Exception as e:
                                self.write(f"[red]Tool execution error: {e}[/red]\n")
                else:
                    self.write("[red]No content in response[/red]\n")
            else:
                self.write(f"[red]API Error: {response.get('error', 'Unknown error')}[/red]\n")

            stream_display.finish_stream()

        except Exception as e:
            self.write(f"[red]Response generation error: {e}[/red]\n")
            import traceback
            traceback.print_exc()
