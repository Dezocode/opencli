"""
CLI Execution Flow Module
Handles interactive execution, streaming, and tool integration for OpenCLI
"""

import os
import json
from typing import Dict, Any
from types import SimpleNamespace

from ..session import Session
from ..tools import execute_tool, TOOLS
from ..utils import prepare_messages_with_context


class ExecutionFlowManager:
    """Manages the execution flow for OpenCLI interactive sessions"""
    
    def __init__(self, config: Dict[str, Any], session: Session, component_init, system_init):
        """Initialize execution flow manager
        
        Args:
            config: Configuration dictionary
            session: Current session
            component_init: Component initializer
            system_init: System initializer
        """
        self.config = config
        self.session = session
        self.component_init = component_init
        self.system_init = system_init
        self.client = None
        self.initialized_systems = {}
        
        # Initialize systems
        self._initialize_execution_systems()
    
    def _initialize_execution_systems(self):
        """Initialize systems needed for execution"""
        config_dir = self.system_init.config_dir
        
        # Initialize agent manager if available
        self.initialized_systems['agent_manager'] = None
        if self.component_init.is_feature_available('AGENT_SYSTEM'):
            try:
                AgentManager = self.component_init.get_component('agent_system')['AgentManager']
                agent_manager = AgentManager(config_dir)
                if hasattr(self.session, 'current_agent') and self.session.current_agent not in agent_manager.agents:
                    self.session.current_agent = 'assistant'
                self.initialized_systems['agent_manager'] = agent_manager
            except Exception as e:
                print(f"\033[33m⚠️  Agent system initialization failed: {e}\033[0m\n")
        
        # Initialize command registry
        self.initialized_systems['command_registry'] = None
        if self.component_init.is_feature_available('COMMAND_REGISTRY'):
            try:
                CommandRegistry = self.component_init.get_component('command_registry')
                command_registry = CommandRegistry(config_dir)
                self.initialized_systems['command_registry'] = command_registry
            except Exception as e:
                print(f"\033[33m⚠️  Command registry initialization failed: {e}\033[0m\n")
        
        # Initialize prompt processor
        self.initialized_systems['prompt_processor'] = None
        if self.component_init.is_feature_available('PROMPT_PROCESSOR'):
            try:
                PromptProcessor = self.component_init.get_component('prompt_processor')
                prompt_processor = PromptProcessor()
                self.initialized_systems['prompt_processor'] = prompt_processor
            except Exception as e:
                print(f"\033[33m⚠️  Prompt processor initialization failed: {e}\033[0m\n")
        
        # Initialize unified permission manager
        try:
            from modules.permissions import get_unified_permission_manager
            self.session.permission_manager = get_unified_permission_manager()
            print("✓ Unified permission manager initialized")
        except Exception as e:
            print(f"\033[33m⚠️  Unified permission manager initialization failed: {e}\033[0m\n")
            # Fallback to old system
            if self.component_init.is_feature_available('TOOL_PERMISSIONS'):
                try:
                    ToolPermissionManager = self.component_init.get_component('tool_permissions')
                    self.session.permission_manager = ToolPermissionManager(config_dir)
                except Exception as e2:
                    print(f"\033[33m⚠️  Tool permission system initialization also failed: {e2}\033[0m\n")
        
        # Initialize API server and register session
        if self.component_init.is_feature_available('API_SERVER'):
            try:
                api_components = self.component_init.get_component('api_server')
                APIServer = api_components['APIServer']
                SessionRegistry = api_components['SessionRegistry']
                
                self.session.api_server = APIServer(config_dir)
                # Auto-start API server if enabled in config
                if self.session.api_server.config.config.get('enabled', False):
                    self.session.api_server.start()
                
                # Register this session
                registry = SessionRegistry(config_dir)
                registry.register_session(
                    self.session.session_id,
                    os.getpid(),
                    self.session.model or self.config['model'],
                    getattr(self.session, 'current_agent', 'assistant'),
                    self.session.cwd
                )
            except Exception as e:
                print(f"\033[33m⚠️  API server initialization failed: {e}\033[0m\n")
    
    def set_client(self, client):
        """Set the OpenAI client for execution

        Args:
            client: Configured OpenAI client
        """
        self.client = client

    async def handle_user_prompt(self, user_input: str, prompt_widget=None):
        """Delegate conversation turn to modular ConversationManager."""
        import sys
        sys.stderr.write(f"\n[EXEC] handle_user_prompt called (delegated): '{user_input}'\n")
        sys.stderr.flush()

        # Commands handled elsewhere (router) — keep as-is
        if user_input.strip().startswith('/'):
            app = prompt_widget.app if prompt_widget and hasattr(prompt_widget, 'app') else None
            if app:
                try:
                    from modules.command_router import route_command_unified
                except ImportError:
                    from cli.modules.command_router import route_command_unified
                parts = user_input.strip().split(maxsplit=1)
                command_name = parts[0]
                command_args = parts[1] if len(parts) > 1 else None
                handled = await route_command_unified(app, self.session, command_name, command_args)
                if handled:
                    return

        # Use the new modular conversation manager for normal turns
        try:
            from modules.conversation_manager import ConversationManager
            manager = ConversationManager(self.config, self.session)
            await manager.handle_user_prompt(user_input, prompt_widget)
        except Exception as e:
            # Fallback to original minimal behavior if import fails
            self.session.add('user', user_input)
            if prompt_widget and hasattr(prompt_widget, 'app'):
                prompt_widget.app.write(f"[red]Conversation error: {e}[/red]\n")

    async def _prepare_messages(self, messages):
        """Prepare messages with context (port from dev6)

        Adds:
        - Constitution principles
        - AGENTS.md content
        - Spec/goal context
        - Working directory
        - Tool definitions
        """
        import sys
        sys.stderr.write(f"[EXEC] Preparing messages with context...\n")
        sys.stderr.flush()

        # Import preparation helper
        try:
            from modules.async_interactive.message_handling import prepare_messages_with_context
            return await prepare_messages_with_context(messages, self.session, self.config)
        except Exception as e:
            sys.stderr.write(f"[EXEC] WARNING: prepare_messages_with_context failed: {e}\n")
            sys.stderr.flush()
            # Fallback: return messages as-is
            return messages

    async def _stream_ai_response(self, prepared_messages, prompt_widget=None):
        """Stream AI response using BufferManager and StreamHandler

        Args:
            prepared_messages: Messages prepared with context
            prompt_widget: Optional widget for spinner control
        """
        import sys
        from modules.async_interactive.streaming import StreamHandler
        from modules.async_interactive.buffer_system import BufferManager
        from modules.async_interactive.tool_integration import get_tool_executor

        sys.stderr.write(f"[EXEC] Streaming AI response...\n")
        sys.stderr.flush()

        # Start spinner if widget available
        if prompt_widget:
            try:
                if hasattr(prompt_widget, 'start_spinner'):
                    prompt_widget.start_spinner()
            except:
                pass

        # Create buffer manager
        buffer_manager = BufferManager()

        # Create stream handler
        stream_handler = StreamHandler()

        # Create tool executor
        tool_executor = get_tool_executor(self, self.session)

        try:
            # Get app for writing output
            app = prompt_widget.app if prompt_widget and hasattr(prompt_widget, 'app') else None

            if app:
                app.write("🔄 Thinking...\n")

            # Stream from API
            model = self.config.get("model", "")
            assistant_text = ""
            tool_calls = []

            if "claude" in model.lower():
                # Use Anthropic streaming
                async for chunk in stream_handler.stream_anthropic(prepared_messages, self.config):
                    if chunk.get("type") == "content":
                        content = chunk["content"]
                        assistant_text += content
                        if app:
                            app.write(content, end="")
                    elif chunk.get("type") == "tool_call":
                        tool_calls.extend(chunk.get("tool_calls", []))
                    elif chunk.get("type") == "error":
                        if app:
                            app.write(f"\n[red]Error: {chunk['error']}[/red]\n")
                        return
            else:
                # Use OpenRouter streaming
                async for chunk in stream_handler.stream_openrouter(prepared_messages, self.config):
                    if chunk.get("type") == "content":
                        content = chunk["content"]
                        assistant_text += content
                        if app:
                            app.write(content, end="")
                    elif chunk.get("type") == "tool_call":
                        tool_calls.extend(chunk.get("tool_calls", []))
                    elif chunk.get("type") == "error":
                        if app:
                            app.write(f"\n[red]Error: {chunk['error']}[/red]\n")
                        return

            # Add assistant message to session
            if assistant_text:
                self.session.add('assistant', assistant_text)
                if app:
                    app.write("\n")

            # Execute tool calls
            if tool_calls and tool_executor:
                for tool_call in tool_calls:
                    try:
                        result = await tool_executor.execute_tool_call(tool_call)
                        self.session.add('tool', f"Tool {tool_call.get('name', 'Unknown')}: {result}")
                        if app:
                            app.write(f"\n[dim]Tool: {tool_call.get('name')}[/dim]\n")
                    except Exception as e:
                        if app:
                            app.write(f"[red]Tool error: {e}[/red]\n")

        finally:
            # Stop spinner
            if prompt_widget:
                try:
                    if hasattr(prompt_widget, 'stop_spinner'):
                        prompt_widget.stop_spinner()
                except:
                    pass

    def handle_user_input(self, user_input: str) -> tuple[str, Dict[str, Any]]:
        """Process user input with prompt processor if available
        
        Args:
            user_input: Raw user input
            
        Returns:
            Tuple of (processed_input, input_metadata)
        """
        processed_input = user_input
        input_metadata = {}
        
        prompt_processor = self.initialized_systems.get('prompt_processor')
        if prompt_processor:
            processed_input, input_metadata = prompt_processor.process_input(user_input)
        
        return processed_input, input_metadata
    
    def handle_exit_commands(self, user_input: str) -> bool:
        """Handle exit/quit commands
        
        Args:
            user_input: User input to check
            
        Returns:
            True if should exit, False otherwise
        """
        if user_input.lower() in ['exit', 'quit', '/exit', '/quit']:
            # Normalize to slash version for permission check
            if user_input.lower() in ['exit', '/exit']:
                cmd_to_check = '/exit'
            else:  # quit or /quit
                cmd_to_check = '/quit'
            
            # Check permission if command registry is available
            command_registry = self.initialized_systems.get('command_registry')
            if command_registry:
                if not command_registry.is_enabled(cmd_to_check):
                    print(f"\n❌ Command '{cmd_to_check}' is disabled")
                    print(f"Use /commands to enable it\n")
                    return False
            
            # Exit allowed
            print("\nGoodbye!\n")
            return True
        
        return False
    
    def handle_slash_commands(self, user_input: str) -> bool:
        """Handle slash commands
        
        Args:
            user_input: User input to check
            
        Returns:
            True if command was handled, False otherwise
        """
        # Check if this is a command (not a file path or pasted content)
        is_command = False
        if user_input.startswith('/'):
            prompt_processor = self.initialized_systems.get('prompt_processor')
            if prompt_processor:
                # Use prompt processor to check if it's likely a command vs file path
                is_command = prompt_processor.is_likely_command(user_input)
            else:
                # No prompt processor - assume slash = command
                is_command = True
        
        if is_command:
            # Use SDK command router instead of legacy handler
            import asyncio
            try:
                # Import the SDK command router
                from modules.command_router import route_command_unified

                # Parse command
                parts = user_input.split(maxsplit=1)
                cmd = parts[0] if parts[0] != '/' else '/help'  # Handle bare "/" as help
                args = parts[1] if len(parts) > 1 else None

                # Create a dummy app object for the router (CLI doesn't have Textual app)
                class DummyApp:
                    def __init__(self):
                        self._command_router = None
                        self._startup_buffer_shown = False

                    def write(self, text, end="\n"):
                        print(text, end=end)

                    async def _initialize_command_router(self):
                        # Initialize command router if needed
                        if not hasattr(self, '_command_router') or not self._command_router:
                            from modules.command_router import CommandRouter
                            self._command_router = CommandRouter(self, None)  # session not needed for routing
                            await self._command_router._initialize_registrations()

                dummy_app = DummyApp()

                # Run the async command routing
                result = asyncio.run(route_command_unified(dummy_app, self.session, cmd, args))
                return result

            except Exception as e:
                print(f"Command routing error: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        return False
    
    def auto_select_agent(self, processed_input: str) -> None:
        """Auto-select agent based on input triggers
        
        Args:
            processed_input: Processed user input
        """
        agent_manager = self.initialized_systems.get('agent_manager')
        if (self.component_init.is_feature_available('AGENT_SYSTEM') and 
            agent_manager and hasattr(self.session, 'current_agent')):
            
            new_agent = agent_manager.select_agent(processed_input, self.session.current_agent)
            if new_agent != self.session.current_agent:
                print(f"\033[2m→ Switching to {new_agent} agent\033[0m")
                self.session.current_agent = new_agent
    
    def prepare_messages_for_api(self):
        """Prepare messages for API call with agent system if available
        
        Returns:
            Prepared messages list
        """
        agent_manager = self.initialized_systems.get('agent_manager')
        if (self.component_init.is_feature_available('AGENT_SYSTEM') and 
            agent_manager and hasattr(self.session, 'current_agent')):
            
            return agent_manager.prepare_messages(
                self.session.current_agent,
                self.session.messages,
                self.session.cwd,
                self.session.session_id  # Pass session ID for caching
            )
        else:
            # Fallback: use prepare_messages_with_context() to inject constitution + AGENTS.md
            self.session.compact_context(self.config.get("contextWindow", 128000))
            config_dir = self.system_init.config_dir
            return prepare_messages_with_context(self.session.messages, config_dir)
    
    def create_api_stream(self, prepared_messages):
        """Create API stream for chat completion
        
        Args:
            prepared_messages: Prepared messages for API
            
        Returns:
            Stream object from API call
        """
        try:
            # Try with tools first
            stream = self.client.chat.completions.create(
                model=self.session.model or self.config["model"],
                messages=prepared_messages,
                tools=TOOLS,
                stream=True
            )
            return stream
        except (TypeError, Exception) as tools_error:
            # If tools parameter not supported, try without it
            if "tools" in str(tools_error).lower() or "unexpected" in str(tools_error).lower():
                stream = self.client.chat.completions.create(
                    model=self.session.model or self.config["model"],
                    messages=prepared_messages,
                    stream=True
                )
                return stream
            else:
                raise
    
    def get_streaming_processor(self):
        """Get streaming processor for this execution manager
        
        Returns:
            StreamingProcessor instance
        """
        if not hasattr(self, '_streaming_processor'):
            from .streaming_processor import create_streaming_processor
            self._streaming_processor = create_streaming_processor(self.session, self.component_init)
        return self._streaming_processor
    
    def get_error_handler(self):
        """Get error handler for this execution manager
        
        Returns:
            CLIErrorHandler instance
        """
        if not hasattr(self, '_error_handler'):
            from .error_handling import create_cli_error_handler
            self._error_handler = create_cli_error_handler(self.component_init, self.system_init)
        return self._error_handler
    
    def complete_turn(self, full_content: str) -> None:
        """Complete a conversation turn
        
        Args:
            full_content: Full content from assistant
        """
        if full_content:
            self.session.add("assistant", full_content)
            print("\n")
    
    def save_session(self) -> None:
        """Save the current session"""
        self.session.save()


class InteractiveExecutor:
    """Orchestrates interactive execution flow"""
    
    def __init__(self, execution_manager: ExecutionFlowManager):
        """Initialize interactive executor
        
        Args:
            execution_manager: Execution flow manager
        """
        self.execution_manager = execution_manager
    
    def execute_conversation_turn(self) -> bool:
        """Execute a single conversation turn
        
        Returns:
            True to continue conversation, False to break
        """
        try:
            for turn in range(self.execution_manager.config.get("maxTurns", 25)):
                # Prepare messages with agent system if available
                prepared_messages = self.execution_manager.prepare_messages_for_api()
                
                stream = None
                policy_abort = False
                policy_attempt = 0
                
                while True:
                    try:
                        stream = self.execution_manager.create_api_stream(prepared_messages)
                        break
                    except Exception as e:
                        error_handler = self.execution_manager.get_error_handler()
                        action = error_handler.handle_api_error(e, self.execution_manager.session, self.execution_manager.config)
                        if action == "retry":
                            # Update client with new config
                            self.execution_manager.client = self.execution_manager.system_init.create_openai_client(self.execution_manager.config)
                            policy_attempt += 1
                            if policy_attempt >= 3:
                                print("⚠️  Repeated header updates still failed.\n")
                                policy_abort = True
                                break
                            continue
                        else:
                            policy_abort = True
                            break
                
                if policy_abort or stream is None:
                    break
                
                # Process streaming response
                streaming_processor = self.execution_manager.get_streaming_processor()
                full_content, tool_calls_dict = streaming_processor.process_stream_response(stream)
                
                # Execute tool calls if present
                if streaming_processor.execute_tool_calls(tool_calls_dict, full_content):
                    continue  # Continue for next turn if tools were executed
                
                # Complete the turn
                self.execution_manager.complete_turn(full_content)
                break
            
            return True
            
        except KeyboardInterrupt:
            error_handler = self.execution_manager.get_error_handler()
            return error_handler.handle_keyboard_interrupt()
        except Exception as e:
            error_handler = self.execution_manager.get_error_handler()
            error_handler.handle_general_error(e, "conversation execution")
            return True


def create_execution_flow_manager(config: Dict[str, Any], session: Session, component_init, system_init) -> ExecutionFlowManager:
    """Factory function to create execution flow manager
    
    Args:
        config: Configuration dictionary
        session: Current session
        component_init: Component initializer
        system_init: System initializer
        
    Returns:
        ExecutionFlowManager instance
    """
    return ExecutionFlowManager(config, session, component_init, system_init)


def create_interactive_executor(execution_manager: ExecutionFlowManager) -> InteractiveExecutor:
    """Factory function to create interactive executor
    
    Args:
        execution_manager: Execution flow manager
        
    Returns:
        InteractiveExecutor instance
    """
    return InteractiveExecutor(execution_manager)