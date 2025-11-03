"""
Async Interactive Mode for OpenCLI - Main Module
Refactored modular architecture with focused components

⚠️  DEPRECATED: Direct permission imports removed in Phase 3
   Use: from modules.authz import check_authorization
"""

# Import from modular components
from .async_interactive.core import interactive_async, run_interactive_async
from .async_interactive.session import create_session
from .async_interactive.client import create_async_client
from .async_interactive.ui_handlers import async_write, write_markdown_response
from .async_interactive.tools import (
    TOOLS, execute_tool_async, execute_tool,
    execute_read, execute_write, execute_edit, 
    execute_bash_async, execute_bash,
    execute_glob, execute_grep_async, execute_grep
)
from .async_interactive.message_handling import (
    normalize_tool_call_messages, 
    prepare_messages_with_context,
    convert_messages_for_anthropic,
    extract_openrouter_policy_error
)
from .async_interactive.api_requests import perform_anthropic_request, perform_google_request
# PHASE 3: Removed direct permission import - use authz facade instead

# Re-export main functions for backward compatibility
__all__ = [
    'interactive_async',
    'run_interactive_async',
    'create_session', 
    'create_async_client',
    'async_write',
    'write_markdown_response',
    'TOOLS',
    'execute_tool_async',
    'execute_tool',
    'normalize_tool_call_messages',
    'prepare_messages_with_context',
    'perform_anthropic_request',
    'perform_google_request'
]