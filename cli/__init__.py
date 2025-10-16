"""
OpenCLI modular command-line interface
Refactored from monolithic opencli.py into focused modules
"""

# Export main components for easy access
from .main import main, interactive
from .config import load_config, setup_api_key, get_api_key
from .session import Session, create_session, list_sessions, delete_session
from .tools import execute_tool, TOOLS
from .utils import count_tokens, prepare_messages_with_context, create_openai_client
from .commands import handle_slash_command

__all__ = [
    'main',
    'interactive',
    'load_config',
    'setup_api_key', 
    'get_api_key',
    'Session',
    'create_session',
    'list_sessions',
    'delete_session',
    'execute_tool',
    'TOOLS',
    'create_openai_client',
    'count_tokens',
    'prepare_messages_with_context',
    'handle_slash_command'
]