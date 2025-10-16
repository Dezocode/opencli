"""
Command Definitions Module
Static command definitions extracted from command_registry.py
Centralizes all command metadata and categorization
"""

# Core command categories in priority order
COMMAND_CATEGORIES = ['basic', 'spec-driven', 'agents', 'advanced', 'system']

# Static command definitions with full metadata
STATIC_COMMAND_DEFINITIONS = {
    '/model': {
        'description': 'View or change model',
        'category': 'basic',
        'default_enabled': True,
        'requires_args': False,
        'subcommands': {
            'list': 'List all available models (default)',
            'providers': 'Browse models by provider with interactive selection',
            '<model-id>': 'Switch to specified model',
            'r1': 'Switch to most recent model',
            'r2': 'Switch to 2nd most recent model'
        }
    },
    '/agent': {
        'description': 'Switch to specific agent',
        'category': 'agents',
        'default_enabled': True,
        'requires_args': False,
        'requires_feature': 'AGENT_SYSTEM',
        'subcommands': {
            'assistant': 'General-purpose coding assistant',
            'debugger': 'Bug finding and fixing specialist',
            'reviewer': 'Code review and quality analysis',
            'refactor': 'Code refactoring expert',
            'tester': 'Test writing specialist',
            'documenter': 'Documentation expert',
            'architect': 'System design specialist'
        }
    },
    '/agents': {
        'description': 'List all available agents',
        'category': 'agents',
        'default_enabled': True,
        'requires_args': False,
        'requires_feature': 'AGENT_SYSTEM'
    },
    '/status': {
        'description': 'Show session info',
        'category': 'basic',
        'default_enabled': True,
        'requires_args': False
    },
    '/clear': {
        'description': 'Clear conversation history',
        'category': 'basic',
        'default_enabled': True,
        'requires_args': False
    },
    '/bashes': {
        'description': 'List background tasks',
        'category': 'advanced',
        'default_enabled': True,
        'requires_args': False
    },
    '/upgrade': {
        'description': 'Upgrade to latest version',
        'category': 'system',
        'default_enabled': True,
        'requires_args': False,
        'requires_feature': 'UPGRADE_SYSTEM'
    },
    '/rollback': {
        'description': 'Rollback to previous version',
        'category': 'system',
        'default_enabled': True,
        'requires_args': False,
        'requires_feature': 'UPGRADE_SYSTEM'
    },
    '/help': {
        'description': 'Show help menu',
        'category': 'basic',
        'default_enabled': True,
        'requires_args': False
    },
    '/commands': {
        'description': 'Manage command permissions',
        'category': 'system',
        'default_enabled': True,
        'requires_args': False
    },
    '/exit': {
        'description': 'Exit the session',
        'category': 'basic',
        'default_enabled': True,
        'requires_args': False
    },
    '/quit': {
        'description': 'Exit the session',
        'category': 'basic',
        'default_enabled': True,
        'requires_args': False
    },
    '/permissions': {
        'description': 'Manage tool permissions',
        'category': 'system',
        'default_enabled': True,
        'requires_args': False,
        'requires_feature': 'TOOL_PERMISSIONS'
    },
    '/api': {
        'description': 'IPC server control (start/stop/status)',
        'category': 'advanced',
        'default_enabled': True,
        'requires_args': False,
        'subcommands': {
            'start': 'Start IPC server',
            'stop': 'Stop IPC server',
            'status': 'Show IPC server status'
        }
    },
    '/docker': {
        'description': 'Manage Docker containers for local models',
        'category': 'advanced',
        'default_enabled': True,
        'requires_args': False,
        'subcommands': {
            'status': 'Show Docker daemon and container status',
            'ps': 'List running containers',
            'stats': 'Show container resource usage',
            'ollama setup': 'Setup Ollama in Docker (interactive)',
            'ollama start': 'Start Ollama container',
            'ollama stop': 'Stop Ollama container',
            'ollama status': 'Show Ollama container status'
        }
    },
    '/diff': {
        'description': 'View code diffs with interactive navigation',
        'category': 'advanced',
        'default_enabled': True,
        'requires_args': False,
        'subcommands': {
            'git': 'Show git diff for current repository',
            'worktree': 'Compare worktree with venv/Docker',
            'files <file1> <file2>': 'Compare two files'
        }
    },
    '/providers': {
        'description': 'Manage API provider keys with auto-detection',
        'category': 'basic',
        'default_enabled': True,
        'requires_args': False,
        'subcommands': {
            'list': 'List all configured providers',
            'add': 'Add a new provider key (auto-detects provider)',
            'add ollama': 'Add Ollama local server as provider',
            'remove': 'Remove a provider key'
        }
    },
    '/specify': {
        'description': 'Create spec describing what to build (Spec-Kit)',
        'category': 'spec-driven',
        'default_enabled': True,
        'requires_args': True
    },
    '/constitution': {
        'description': 'Create project principles and guidelines (Spec-Kit)',
        'category': 'spec-driven',
        'default_enabled': True,
        'requires_args': True
    },
    '/plan': {
        'description': 'Create technical implementation plan (Spec-Kit)',
        'category': 'spec-driven',
        'default_enabled': True,
        'requires_args': True
    },
    '/tasks': {
        'description': 'Break down plan into actionable tasks (Spec-Kit)',
        'category': 'spec-driven',
        'default_enabled': True,
        'requires_args': False
    },
    '/implement': {
        'description': 'Implement tasks from the plan (Spec-Kit)',
        'category': 'spec-driven',
        'default_enabled': True,
        'requires_args': False
    },
    '/test': {
        'description': 'Create and run tests (Spec-Kit)',
        'category': 'spec-driven',
        'default_enabled': True,
        'requires_args': False
    },
    '/spec-check': {
        'description': 'Validate spec completeness (Spec-Kit)',
        'category': 'spec-driven',
        'default_enabled': True,
        'requires_args': False
    },
    '/local': {
        'description': 'Local model recommendations for Ollama',
        'category': 'basic',
        'default_enabled': True,
        'requires_args': False
    },
    '/debug': {
        'description': 'Toggle debug mode',
        'category': 'advanced',
        'default_enabled': True,
        'requires_args': False
    },
    '/performance': {
        'description': 'Performance monitoring controls',
        'category': 'advanced',
        'default_enabled': True,
        'requires_args': False
    },
    '/reload': {
        'description': 'Hot-reload modules (clear cache and reimport)',
        'category': 'advanced',
        'default_enabled': True,
        'requires_args': False
    }
}

def get_static_commands():
    """Get static command definitions."""
    return STATIC_COMMAND_DEFINITIONS.copy()

def get_command_categories():
    """Get ordered command categories."""
    return COMMAND_CATEGORIES.copy()

def get_commands_by_category(category: str):
    """Get all commands in a specific category."""
    return {
        cmd: info for cmd, info in STATIC_COMMAND_DEFINITIONS.items()
        if info.get('category') == category
    }

def get_core_commands():
    """Get essential commands that should always be available."""
    core_commands = ['/help', '/commands', '/status', '/exit', '/quit']
    return {
        cmd: STATIC_COMMAND_DEFINITIONS[cmd] 
        for cmd in core_commands 
        if cmd in STATIC_COMMAND_DEFINITIONS
    }

def get_commands_with_subcommands():
    """Get commands that have subcommands defined."""
    return {
        cmd: info for cmd, info in STATIC_COMMAND_DEFINITIONS.items()
        if 'subcommands' in info
    }

def get_feature_dependent_commands():
    """Get commands that require specific features."""
    return {
        cmd: info for cmd, info in STATIC_COMMAND_DEFINITIONS.items()
        if 'requires_feature' in info
    }

def validate_command_definition(cmd_name: str, cmd_info: dict) -> bool:
    """Validate a command definition structure."""
    required_fields = ['description', 'category', 'default_enabled']
    
    # Check required fields
    for field in required_fields:
        if field not in cmd_info:
            return False
            
    # Validate category
    if cmd_info['category'] not in COMMAND_CATEGORIES:
        return False
        
    # Validate boolean fields
    if not isinstance(cmd_info['default_enabled'], bool):
        return False
        
    return True

def merge_runtime_commands(runtime_commands: dict) -> dict:
    """Merge runtime commands with static definitions."""
    merged = get_static_commands()
    
    for cmd_name, runtime_info in runtime_commands.items():
        if cmd_name in merged:
            # Preserve subcommands from static definition
            static_info = merged[cmd_name]
            merged_info = runtime_info.copy()
            
            if 'subcommands' in static_info:
                merged_info['subcommands'] = static_info['subcommands']
                
            merged[cmd_name] = merged_info
        else:
            # New runtime command
            merged[cmd_name] = runtime_info
            
    return merged