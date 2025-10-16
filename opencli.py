#!/usr/bin/env python3
"""
OpenCLI - OpenRouter CLI with Claude Code capabilities
A fast, feature-rich terminal interface for OpenRouter API

This is the main entry point that delegates to modular CLI components.
"""

import os
import sys
from pathlib import Path

# Development mode - prevent .pyc creation if OPENCLI_DEV=1
if os.getenv('OPENCLI_DEV') == '1':
    sys.dont_write_bytecode = True
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

# Add both root modules and CLI modules to path
ROOT_DIR = Path(__file__).parent
CLI_DIR = ROOT_DIR / "cli"

# Add root directory first (for modules/ at root level)
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Add CLI directory second (for cli/modules/)
if str(CLI_DIR) not in sys.path:
    sys.path.insert(0, str(CLI_DIR))

# Import and delegate to main CLI module
try:
    from cli.main import main
    
    # Export commonly used components for backward compatibility
    from cli.config import load_config, setup_api_key, get_api_key
    from cli.session import Session, create_session, list_sessions, delete_session
    from cli.tools import execute_tool, TOOLS
    from cli.utils import count_tokens, prepare_messages_with_context, create_openai_client
    from cli.commands import handle_slash_command
    
    # Define BACKGROUND_TASKS for commands module
    BACKGROUND_TASKS = {}

except ImportError as e:
    print(f"❌ Failed to import CLI modules: {e}")
    print("This usually means the modular refactoring is incomplete or there are import issues.")
    sys.exit(1)


if __name__ == "__main__":
    main()