#!/usr/bin/env python3
"""
OpenCLI - OpenRouter CLI with Claude Code capabilities
A fast, feature-rich terminal interface for OpenRouter API
"""

import os, sys, json, argparse, subprocess, uuid, readline, signal, shutil
from pathlib import Path
from datetime import datetime
from openai import OpenAI

# Add modules directory to path for imports
MODULES_DIR = Path.home() / ".opencli" / "modules"
if MODULES_DIR.exists() and str(MODULES_DIR) not in sys.path:
    sys.path.insert(0, str(MODULES_DIR))

# Agent system imports
try:
    import yaml
    from agent_manager import AgentManager
    AGENT_SYSTEM = True
except ImportError as e:
    AGENT_SYSTEM = False
    print(f"\033[2mAgent system not available: {e}\033[0m")

# GitHub tool imports
try:
    from github_tool import execute_github_tool, GitHubTool
    GITHUB_TOOL = True
except ImportError:
    GITHUB_TOOL = False

# Upgrade/Rollback system imports
try:
    from upgrade_manager import UpgradeManager
    from rollback_manager import RollbackManager
    UPGRADE_SYSTEM = True
except ImportError:
    UPGRADE_SYSTEM = False

# Command registry imports
try:
    from command_registry import CommandRegistry
    COMMAND_REGISTRY = True
except ImportError:
    COMMAND_REGISTRY = False

# Prompt processor imports
try:
    from prompt_processor import PromptProcessor
    PROMPT_PROCESSOR = True
except ImportError:
    PROMPT_PROCESSOR = False

# Tool permission system imports
try:
    from tool_permissions import ToolPermissionManager
    TOOL_PERMISSIONS = True
except ImportError:
    TOOL_PERMISSIONS = False

# API server imports
try:
    from api_server import APIServer, SessionRegistry, MessageQueue
    from api_client import OpenCLIClient
    API_SERVER = True
except ImportError:
    API_SERVER = False

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.formatted_text import HTML, FormattedText
    from prompt_toolkit.styles import Style
    from prompt_toolkit import print_formatted_text
    RICH_PROMPT = True
except ImportError:
    RICH_PROMPT = False

# Configuration paths
CONFIG_DIR = Path.home() / ".opencli"
SESSIONS_DIR = CONFIG_DIR / "sessions"
BASHES_DIR = CONFIG_DIR / "bashes"
CONFIG_FILE = CONFIG_DIR / "config.json"
SECRETS_FILE = CONFIG_DIR / ".secrets"

# Create directories
for d in [CONFIG_DIR, SESSIONS_DIR, BASHES_DIR]:
    d.mkdir(exist_ok=True)

# Set secure permissions on secrets file
if SECRETS_FILE.exists():
    os.chmod(SECRETS_FILE, 0o600)

DEFAULT_CONFIG = {
    "model": "x-ai/grok-4-fast:free",
    "baseURL": "https://openrouter.ai/api/v1",
    "maxTurns": 25,
    "contextWindow": 128000
}

BACKGROUND_TASKS = {}

ASCII_ART = """
 ██████╗ ██████╗ ███████╗███╗   ██╗     ██████╗██╗     ██╗
██╔═══██╗██╔══██╗██╔════╝████╗  ██║    ██╔════╝██║     ██║
██║   ██║██████╔╝█████╗  ██╔██╗ ██║    ██║     ██║     ██║
██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║    ██║     ██║     ██║
╚██████╔╝██║     ███████╗██║ ╚████║    ╚██████╗███████╗██║
 ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝     ╚═════╝╚══════╝╚═╝
"""

PROMPT_STYLE = Style.from_dict({
    'prompt': '#00aa00',
    'border': '#888888',
    'violet': '#aa88ff',
    'cyan': '#7aa2f7',
    'gray': '#666666',
    'bottom-toolbar': 'noinherit',
    'bottom-toolbar.text': 'noinherit',
}) if RICH_PROMPT else None

def get_api_key():
    """Get API key from environment or secrets file"""
    # Try environment variable first
    key = os.getenv('OPENROUTER_API_KEY')
    if key:
        return key

    # Try secrets file
    if SECRETS_FILE.exists():
        try:
            with open(SECRETS_FILE) as f:
                data = json.load(f)
                return data.get('apiKey')
        except:
            pass

    # Prompt user to set it up
    print("\n⚠️  No OpenRouter API key found!")
    print("\nSet your API key by either:")
    print("  1. Export OPENROUTER_API_KEY environment variable")
    print("  2. Run: opencli --setup\n")
    sys.exit(1)

def setup_api_key():
    """Interactive setup for API key"""
    print("\n🔧 OpenCLI Setup\n")
    print("Get your OpenRouter API key from: https://openrouter.ai/keys\n")

    api_key = input("Enter your OpenRouter API key: ").strip()

    if not api_key:
        print("❌ No API key provided")
        sys.exit(1)

    # Verify key format
    if not api_key.startswith('sk-'):
        print("⚠️  Warning: API key doesn't start with 'sk-' - this might be incorrect")

    # Save to secrets file with secure permissions
    with open(SECRETS_FILE, 'w', encoding='utf-8') as f:
        json.dump({"apiKey": api_key}, f, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())

    os.chmod(SECRETS_FILE, 0o600)

    # Verify the key was saved correctly
    with open(SECRETS_FILE, 'r', encoding='utf-8') as f:
        saved_data = json.load(f)
        saved_key = saved_data.get('apiKey', '')

    if saved_key == api_key:
        print(f"\n✅ API key saved securely to {SECRETS_FILE}")
        print(f"   Key length: {len(api_key)} characters")
        print("   File permissions set to 600 (owner read/write only)\n")
    else:
        print(f"\n❌ Error: API key verification failed!")
        print(f"   Expected length: {len(api_key)}, saved length: {len(saved_key)}")
        sys.exit(1)

def load_config():
    config = DEFAULT_CONFIG.copy()
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            config.update(json.load(f))
    config['apiKey'] = get_api_key()
    return config

def count_tokens(messages):
    return sum(len(json.dumps(m)) // 4 for m in messages)

# Tool definitions
# Note: Tools marked [REQUIRES PERMISSION] will prompt user before execution
TOOLS = [
    {"type": "function", "function": {"name": "Read", "description": "Read file contents. Safe tool, auto-executes.", "parameters": {"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]}}},
    {"type": "function", "function": {"name": "Write", "description": "Write to file. [REQUIRES PERMISSION] User will be prompted to approve this operation.", "parameters": {"type": "object", "properties": {"file_path": {"type": "string"}, "content": {"type": "string"}}, "required": ["file_path", "content"]}}},
    {"type": "function", "function": {"name": "Edit", "description": "Edit file by replacing text. [REQUIRES PERMISSION] User will be prompted to approve this operation.", "parameters": {"type": "object", "properties": {"file_path": {"type": "string"}, "old_string": {"type": "string"}, "new_string": {"type": "string"}}, "required": ["file_path", "old_string", "new_string"]}}},
    {"type": "function", "function": {"name": "Bash", "description": "Execute bash command. [REQUIRES PERMISSION] User will be prompted to approve this command before execution.", "parameters": {"type": "object", "properties": {"command": {"type": "string"}, "description": {"type": "string"}}, "required": ["command"]}}},
    {"type": "function", "function": {"name": "Glob", "description": "Find files by pattern. Safe tool, auto-executes.", "parameters": {"type": "object", "properties": {"pattern": {"type": "string"}}, "required": ["pattern"]}}},
    {"type": "function", "function": {"name": "Grep", "description": "Search files for pattern. Safe tool, auto-executes.", "parameters": {"type": "object", "properties": {"pattern": {"type": "string"}}, "required": ["pattern"]}}},
]

# Add GitHub tool if available
if GITHUB_TOOL:
    TOOLS.append({
        "type": "function",
        "function": {
            "name": "GitHub",
            "description": "Interact with GitHub using gh CLI. Actions: auth_status, repo_view, issue_list, issue_view, issue_create, pr_list, pr_view, pr_create, pr_checkout, workflow_list, workflow_run, run_list, gist_create",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "GitHub action to perform"
                    },
                    "repo": {
                        "type": "string",
                        "description": "Repository (owner/repo format, optional)"
                    },
                    "number": {
                        "type": "integer",
                        "description": "Issue or PR number"
                    },
                    "title": {
                        "type": "string",
                        "description": "Title for issue/PR"
                    },
                    "body": {
                        "type": "string",
                        "description": "Body content for issue/PR"
                    },
                    "state": {
                        "type": "string",
                        "description": "State filter (open, closed, all)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of items to return"
                    }
                },
                "required": ["action"]
            }
        }
    })

def execute_read(file_path):
    try:
        with open(file_path) as f:
            return '\n'.join(f"{i+1}→{l.rstrip()}" for i, l in enumerate(f))
    except Exception as e:
        return f"Error: {e}"

def execute_write(file_path, content):
    try:
        os.makedirs(os.path.dirname(file_path) or '.', exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(content)
        return f"File created successfully at: {file_path}"
    except Exception as e:
        return f"Error: {e}"

def execute_edit(file_path, old_string, new_string):
    try:
        with open(file_path) as f:
            content = f.read()
        if old_string not in content:
            return f"Error: old_string not found"
        with open(file_path, 'w') as f:
            f.write(content.replace(old_string, new_string, 1))
        return f"The file {file_path} has been updated."
    except Exception as e:
        return f"Error: {e}"

def execute_bash(command, description=None):
    try:
        r = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
        return (r.stdout + r.stderr).strip() or "Tool ran without output or errors"
    except Exception as e:
        return f"Error: {e}"

def execute_glob(pattern):
    from glob import glob
    matches = glob(f"**/{pattern}", recursive=True)
    return '\n'.join(sorted(matches)) or "No files matched"

def execute_grep(pattern):
    try:
        r = subprocess.run(["grep", "-rl", pattern, "."], capture_output=True, text=True, timeout=10)
        return r.stdout or "No matches"
    except:
        return "No matches"

def execute_tool(name, args, permission_manager=None, current_dir=None):
    """Execute a tool, checking permissions for risky operations"""

    # Check if permission is required
    if permission_manager and TOOL_PERMISSIONS:
        should_prompt, reason, path_risk = permission_manager.should_prompt(name, args, current_dir)

        if should_prompt:
            # Show permission prompt with path risk information
            allowed, remember, session_mode = permission_manager.prompt_for_permission(name, args, current_dir)

            if not allowed:
                return f"❌ Operation cancelled by user"

    # Execute the tool
    tools = {
        "Read": lambda: execute_read(args["file_path"]),
        "Write": lambda: execute_write(args["file_path"], args["content"]),
        "Edit": lambda: execute_edit(args["file_path"], args["old_string"], args["new_string"]),
        "Bash": lambda: execute_bash(args["command"], args.get("description")),
        "Glob": lambda: execute_glob(args["pattern"]),
        "Grep": lambda: execute_grep(args["pattern"])
    }

    # Add GitHub tool if available
    if GITHUB_TOOL and name == "GitHub":
        return execute_github_tool(**args)

    return tools.get(name, lambda: f"Unknown tool")()

class Session:
    def __init__(self, session_id=None, model=None):
        self.session_id = session_id or str(uuid.uuid4())
        self.messages = []
        self.model = model
        self.file = SESSIONS_DIR / f"{self.session_id}.json"
        self.cwd = os.getcwd()
        self.current_agent = 'assistant'
        self.permission_manager = None

    def add(self, role, content):
        self.messages.append({"role": role, "content": content})

    def compact_context(self, max_tokens):
        if count_tokens(self.messages) > max_tokens * 0.8:
            self.messages = self.messages[:2] + self.messages[-10:]
            print("\033[2m[Context compacted to fit window]\033[0m")

    def save(self):
        with open(self.file, 'w') as f:
            json.dump({
                "session_id": self.session_id,
                "model": self.model,
                "messages": self.messages,
                "cwd": self.cwd,
                "timestamp": datetime.now().isoformat()
            }, f)

    @classmethod
    def load(cls, sid):
        f = SESSIONS_DIR / f"{sid}.json"
        if not f.exists():
            return None
        d = json.load(open(f))
        s = cls(d["session_id"], d.get("model"))
        s.messages = d["messages"]
        s.cwd = d.get("cwd", os.getcwd())
        return s

    @classmethod
    def latest(cls):
        sessions = list(SESSIONS_DIR.glob("*.json"))
        return cls.load(max(sessions, key=lambda p: p.stat().st_mtime).stem) if sessions else None

def handle_slash_command(cmd, args, session, config, agent_manager=None, command_registry=None):
    # Check command permissions
    if command_registry and not command_registry.is_enabled(cmd):
        print(f"\n❌ Command '{cmd}' is disabled")
        print(f"Use /commands to enable it\n")
        return True

    if cmd == "/model":
        if args:
            session.model = args
            print(f"✓ Model changed to: {args}\n")
        else:
            print(f"Current model: {session.model or config['model']}\n")
        return True

    elif cmd == "/agent":
        if not AGENT_SYSTEM or not agent_manager:
            print("❌ Agent system not available (install pyyaml)\n")
            return True
        if args:
            if args in agent_manager.agents:
                session.current_agent = args
                print(f"✓ Agent changed to: {args}\n")
            else:
                print(f"❌ Unknown agent: {args}")
                print("Available agents:", ', '.join(agent_manager.agents.keys()), "\n")
        else:
            print(f"Current agent: {session.current_agent}\n")
        return True

    elif cmd == "/agents":
        if not AGENT_SYSTEM or not agent_manager:
            print("❌ Agent system not available (install pyyaml)\n")
            return True
        print("\n📋 Available Agents:\n")
        for name, desc in agent_manager.list_agents():
            marker = "→" if name == session.current_agent else " "
            print(f"{marker} {name:15} {desc}")
        print()
        return True

    elif cmd == "/status":
        tokens = count_tokens(session.messages)
        print(f"\nSession ID: {session.session_id}")
        print(f"Model: {session.model or config['model']}")
        print(f"Messages: {len(session.messages)}")
        print(f"Tokens used: {tokens}/{config.get('contextWindow', 128000)}")
        print(f"Working dir: {session.cwd}\n")
        return True

    elif cmd == "/clear":
        session.messages = []
        print("✓ Conversation cleared\n")
        return True

    elif cmd == "/bashes":
        if BACKGROUND_TASKS:
            print("\nBackground tasks:")
            for task_id, info in BACKGROUND_TASKS.items():
                print(f"  [{task_id}] {info['command']} - {info['status']}")
            print()
        else:
            print("\nNo background tasks\n")
        return True

    elif cmd == "/upgrade":
        if not UPGRADE_SYSTEM:
            print("❌ Upgrade system not available\n")
            return True

        print("\n🔄 OpenCLI Upgrade System\n")

        manager = UpgradeManager()

        # Pre-flight checks
        print("Running pre-flight checks...")
        preflight = manager.preflight_checks()

        for check in preflight['checks']:
            status = "✓" if check['passed'] else "✗"
            print(f"  {status} {check['name']}: {check['message']}")

            if check.get('warning'):
                print(f"    ⚠️  {check['message']}")

        print()

        if not preflight['passed']:
            print("❌ Pre-flight checks failed. Cannot proceed with upgrade.\n")
            return True

        # Get versions
        current_version = manager.get_current_version()
        new_version = manager.get_new_version()

        print(f"Current version: v{current_version}")
        print(f"New version: v{new_version}")
        print()

        # Detect changes
        print("Detecting changes...")
        changes = manager.detect_changes()

        change_count = sum(len(v) for v in changes.values())
        if change_count == 0:
            print("No changes detected. Already up to date.\n")
            return True

        print(f"\n{change_count} files changed:")
        for category, files in changes.items():
            if files:
                print(f"\n  {category.upper()}:")
                for file in files[:5]:  # Show first 5
                    print(f"    • {file}")
                if len(files) > 5:
                    print(f"    ... and {len(files) - 5} more")

        print()

        # Show changelog
        changelog = manager.get_changelog(new_version)
        if changelog:
            print("Changelog:")
            for change in changelog:
                print(f"  • {change}")
            print()

        # Confirm
        try:
            response = input("Proceed with upgrade? (y/n): ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nCancelled.\n")
            return True

        if response != 'y':
            print("Cancelled.\n")
            return True

        # Perform upgrade
        print("\n🚀 Starting upgrade...\n")
        result = manager.perform_upgrade(auto_rollback=True)

        if result['success']:
            print("✅ Upgrade completed successfully!\n")
            print(f"Upgraded from v{result['current_version']} to v{result['new_version']}\n")

            if result.get('backup_dir'):
                print(f"📦 Backup created at: {result['backup_dir']}")
                print()

            # Show verification steps if available
            verification_steps = result.get('verification_steps', [])
            if verification_steps:
                print("📋 Verification checklist:")
                for step in verification_steps:
                    print(f"  ☐ {step}")
                print()

            print("🎯 Please restart opencli to use the new version")
            print()

            # Offer to exit
            try:
                response = input("Exit now? (y/n): ").strip().lower()
            except (KeyboardInterrupt, EOFError):
                print()
                return True

            if response == 'y':
                sys.exit(0)
        else:
            print(f"❌ Upgrade failed at stage: {result['stage']}\n")

            if result.get('rollback_performed'):
                print("🔄 Automatic rollback performed. System restored to previous state.\n")
            else:
                print("⚠️  No automatic rollback. Use /rollback to manually restore.\n")

        return True

    elif cmd == "/rollback":
        if not UPGRADE_SYSTEM:
            print("❌ Rollback system not available\n")
            return True

        print("\n🔄 OpenCLI Rollback System\n")

        manager = RollbackManager()

        # List available backups
        backups = manager.list_backups()

        if not backups:
            print("❌ No backups found\n")
            print("Cannot rollback without backups.\n")
            return True

        print("Available backups:\n")
        for i, backup in enumerate(backups, 1):
            print(f"  {i}. v{backup['version']} ({backup['timestamp_str']}) - {backup['age']}")
            print(f"     Size: {backup['size']}")
            print()

        # Get selection
        try:
            response = input(f"Select backup to restore (1-{len(backups)}, or 'q' to cancel): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nCancelled.\n")
            return True

        if response.lower() == 'q':
            print("Cancelled.\n")
            return True

        try:
            choice = int(response)
            if choice < 1 or choice > len(backups):
                print("❌ Invalid choice\n")
                return True
        except ValueError:
            print("❌ Invalid input\n")
            return True

        selected_backup = backups[choice - 1]

        # Show what will happen
        current_version = manager.get_current_version()
        backup_version = selected_backup['version']

        print(f"\nYou are about to rollback:")
        print(f"  From: v{current_version}")
        print(f"  To: v{backup_version}")
        print()
        print("⚠️  This will:")
        print("  • Replace all files in ~/.opencli")
        print("  • Restore previous modules")
        print("  • Restore previous agent configs")
        print("  • Keep current sessions (safe)")
        print()

        # Confirm
        try:
            response = input("Continue? (y/n): ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nCancelled.\n")
            return True

        if response != 'y':
            print("Cancelled.\n")
            return True

        # Perform rollback
        print("\n🔄 Starting rollback...\n")
        result = manager.perform_rollback(selected_backup['path'], create_safety=True)

        if result['success']:
            print("✅ Rollback complete!\n")
            print(f"Restored version: v{result['backup_version']}")
            print()

            if result.get('safety_backup'):
                print(f"📦 Previous (broken) installation backed up at:")
                print(f"    {result['safety_backup']}")
                print()

            print("🎯 Please restart opencli to use the restored version")
            print()

            # Offer to exit
            try:
                response = input("Exit now? (y/n): ").strip().lower()
            except (KeyboardInterrupt, EOFError):
                print()
                return True

            if response == 'y':
                sys.exit(0)
        else:
            print(f"❌ Rollback failed at stage: {result['stage']}\n")
            print("Try manual recovery:")
            print(f"  rm -rf ~/.opencli")
            print(f"  cp -r {selected_backup['path']} ~/.opencli")
            print()

        return True

    elif cmd == "/commands":
        if not COMMAND_REGISTRY or not command_registry:
            print("❌ Command registry not available\n")
            return True

        # Show subcommands
        if args:
            subcommand = args.split()[0].lower()

            if subcommand == "status":
                # Show command status
                feature_flags = {
                    'AGENT_SYSTEM': AGENT_SYSTEM,
                    'UPGRADE_SYSTEM': UPGRADE_SYSTEM,
                    'GITHUB_TOOL': GITHUB_TOOL
                }
                command_registry.show_status(feature_flags)

            elif subcommand == "setup":
                # Interactive setup
                feature_flags = {
                    'AGENT_SYSTEM': AGENT_SYSTEM,
                    'UPGRADE_SYSTEM': UPGRADE_SYSTEM,
                    'GITHUB_TOOL': GITHUB_TOOL
                }
                command_registry.interactive_permission_setup(feature_flags)

            elif subcommand == "enable":
                # Enable specific command
                parts = args.split(maxsplit=1)
                if len(parts) < 2:
                    print("Usage: /commands enable <command>\n")
                else:
                    cmd_to_enable = parts[1]
                    success, message = command_registry.enable_command(cmd_to_enable)
                    print(f"\n{message}\n")

            elif subcommand == "disable":
                # Disable specific command
                parts = args.split(maxsplit=1)
                if len(parts) < 2:
                    print("Usage: /commands disable <command>\n")
                else:
                    cmd_to_disable = parts[1]
                    success, message = command_registry.disable_command(cmd_to_disable)
                    print(f"\n{message}\n")

            else:
                print(f"\n❌ Unknown subcommand: {subcommand}")
                print("\nAvailable subcommands:")
                print("  /commands status   - Show command status")
                print("  /commands setup    - Interactive permission setup")
                print("  /commands enable <cmd>   - Enable a command")
                print("  /commands disable <cmd>  - Disable a command\n")

        else:
            # No args - show status by default
            feature_flags = {
                'AGENT_SYSTEM': AGENT_SYSTEM,
                'UPGRADE_SYSTEM': UPGRADE_SYSTEM,
                'GITHUB_TOOL': GITHUB_TOOL
            }
            command_registry.show_status(feature_flags)
            print("Use '/commands setup' for interactive configuration\n")

        return True

    elif cmd == "/permissions":
        if not TOOL_PERMISSIONS or not session.permission_manager:
            print("❌ Tool permission system not available\n")
            return True

        if args:
            subcommand = args.split()[0].lower()

            if subcommand == "status":
                session.permission_manager.show_status()

            elif subcommand == "allow":
                parts = args.split(maxsplit=1)
                if len(parts) < 2:
                    print("Usage: /permissions allow <tool>\n")
                else:
                    tool = parts[1]
                    session.permission_manager.add_allowed_tool(tool)
                    print(f"✓ {tool} added to allowed tools\n")

            elif subcommand == "deny":
                parts = args.split(maxsplit=1)
                if len(parts) < 2:
                    print("Usage: /permissions deny <tool>\n")
                else:
                    tool = parts[1]
                    session.permission_manager.remove_allowed_tool(tool)
                    print(f"✓ {tool} removed from allowed tools\n")

            elif subcommand == "auto":
                enabled = len(args.split()) > 1 and args.split()[1].lower() in ['on', 'true', 'yes']
                session.permission_manager.set_auto_accept(enabled)
                print(f"✓ Auto-accept {'enabled' if enabled else 'disabled'}\n")

            else:
                print(f"\n❌ Unknown subcommand: {subcommand}")
                print("\nAvailable subcommands:")
                print("  /permissions status        - Show permission status")
                print("  /permissions allow <tool>  - Always allow a tool")
                print("  /permissions deny <tool>   - Remove tool from allowed list")
                print("  /permissions auto on|off   - Enable/disable auto-accept\n")
        else:
            session.permission_manager.show_status()

        return True

    elif cmd == "/api":
        if not API_SERVER:
            print("❌ API server not available\n")
            return True

        if not args:
            # Show API status
            if hasattr(session, 'api_server') and session.api_server:
                if session.api_server.is_running():
                    config = session.api_server.config.config
                    print(f"\n🌐 API Server Status: RUNNING")
                    print(f"   URL: http://{config['host']}:{config['port']}")
                    print(f"   Active sessions: {len(SessionRegistry().list_active_sessions())}")
                else:
                    print("\n🌐 API Server Status: STOPPED")
            else:
                print("\n🌐 API Server Status: NOT INITIALIZED")
            print()
            return True

        subcommand = args.split()[0].lower()

        if subcommand == "start":
            if not hasattr(session, 'api_server'):
                session.api_server = APIServer(CONFIG_DIR)

            if session.api_server.is_running():
                print("✓ API server already running\n")
            else:
                if session.api_server.start():
                    config = session.api_server.config.config
                    print(f"✓ API server started at http://{config['host']}:{config['port']}\n")
                else:
                    print("❌ Failed to start API server\n")

        elif subcommand == "stop":
            if hasattr(session, 'api_server') and session.api_server:
                session.api_server.stop()
                print("✓ API server stopped\n")
            else:
                print("❌ API server not running\n")

        elif subcommand == "sessions":
            registry = SessionRegistry(CONFIG_DIR)
            sessions_list = registry.list_active_sessions()
            print(f"\n📋 Active Sessions: {len(sessions_list)}\n")
            for s in sessions_list:
                print(f"  {s['session_id'][:8]} | {s.get('model', 'unknown')} | {s.get('agent', 'assistant')}")
                print(f"    PID: {s.get('pid')} | CWD: {s.get('cwd')}")
            print()

        elif subcommand == "messages":
            queue = MessageQueue(CONFIG_DIR)
            messages = queue.get_messages(session.session_id, delete=False)
            print(f"\n📬 Messages for this session: {len(messages)}\n")
            for msg in messages:
                print(f"  From: {msg['from'][:8]} | Type: {msg['type']}")
                print(f"  {msg['payload']}")
                print()

        return True

    elif cmd == "/help":
        print("\nAvailable commands:")
        print("  /model [name]  - View or change model")
        if AGENT_SYSTEM:
            print("  /agent [name]  - Switch to specific agent")
            print("  /agents        - List all available agents")
        print("  /status        - Show session info")
        print("  /clear         - Clear conversation")
        print("  /bashes        - List background tasks")
        if UPGRADE_SYSTEM:
            print("  /upgrade       - Upgrade to latest version")
            print("  /rollback      - Rollback to previous version")
        if COMMAND_REGISTRY:
            print("  /commands      - Manage command permissions")
        if TOOL_PERMISSIONS:
            print("  /permissions   - Manage tool permissions")
        if API_SERVER:
            print("  /api           - API server control (start/stop/sessions/messages)")
        print("  /help          - Show this help")
        print("  /exit or /quit - Exit\n")
        return True

    return False

def get_git_info():
    try:
        branch = subprocess.run(['git', 'branch', '--show-current'], capture_output=True, text=True, timeout=1).stdout.strip()
        repo = subprocess.run(['git', 'rev-parse', '--show-toplevel'], capture_output=True, text=True, timeout=1).stdout.strip()
        repo_name = Path(repo).name if repo else ''
        return repo_name, branch
    except:
        return '', ''

def get_bottom_toolbar(session, config):
    tokens = count_tokens(session.messages)
    context = config.get("contextWindow", 128000)
    percent = int((tokens / context) * 100) if context > 0 else 0

    repo_name, branch = get_git_info()
    cwd = os.getcwd()

    line1 = f'<violet>Session: {session.session_id[:8]} | Model: {session.model or config["model"]} | Tokens: {tokens}/{context} ({percent}%)</violet>'

    if repo_name and branch:
        line2 = f'\n<cyan>{cwd}</cyan> <cyan>{repo_name}</cyan> <ansibrightblack>({branch})</ansibrightblack>'
    else:
        line2 = f'\n<cyan>{cwd}</cyan>'

    return HTML(f'{line1}{line2}')

def interactive(config, session=None, initial=None):
    client = OpenAI(base_url=config["baseURL"], api_key=config["apiKey"])
    session = session or Session(model=config["model"])

    # Initialize agent manager if available
    agent_manager = None
    if AGENT_SYSTEM:
        try:
            agent_manager = AgentManager(CONFIG_DIR)
            if session.current_agent not in agent_manager.agents:
                session.current_agent = 'assistant'
        except Exception as e:
            print(f"\033[33m⚠️  Agent system initialization failed: {e}\033[0m\n")

    # Initialize command registry
    command_registry = None
    if COMMAND_REGISTRY:
        try:
            command_registry = CommandRegistry(CONFIG_DIR)
        except Exception as e:
            print(f"\033[33m⚠️  Command registry initialization failed: {e}\033[0m\n")

    # Initialize prompt processor
    prompt_processor = None
    if PROMPT_PROCESSOR:
        try:
            prompt_processor = PromptProcessor()
        except Exception as e:
            print(f"\033[33m⚠️  Prompt processor initialization failed: {e}\033[0m\n")

    # Initialize tool permission manager
    if TOOL_PERMISSIONS:
        try:
            session.permission_manager = ToolPermissionManager(CONFIG_DIR)
        except Exception as e:
            print(f"\033[33m⚠️  Tool permission system initialization failed: {e}\033[0m\n")

    # Initialize API server and register session
    if API_SERVER:
        try:
            session.api_server = APIServer(CONFIG_DIR)
            # Auto-start API server if enabled in config
            if session.api_server.config.config.get('enabled', False):
                session.api_server.start()

            # Register this session
            registry = SessionRegistry(CONFIG_DIR)
            registry.register_session(
                session.session_id,
                os.getpid(),
                session.model or config['model'],
                session.current_agent,
                session.cwd
            )
        except Exception as e:
            print(f"\033[33m⚠️  API server initialization failed: {e}\033[0m\n")

    print(ASCII_ART)

    # Load version from metadata
    version_file = CONFIG_DIR / "version.json"
    version_str = "unknown"
    if version_file.exists():
        try:
            import json
            with open(version_file) as f:
                version_data = json.load(f)
                version_str = version_data.get('version', 'unknown')
        except:
            pass

    print(f"\033[2mOpenCLI - version {version_str}\033[0m")
    agent_info = f" | Agent: {session.current_agent}" if AGENT_SYSTEM and agent_manager else ""
    print(f"\033[2mSession: {session.session_id[:8]} | Model: {session.model or config['model']}{agent_info}\033[0m\n")

    if RICH_PROMPT:
        from prompt_toolkit.document import Document
        from prompt_toolkit.buffer import Buffer

        prompt_session = PromptSession(
            style=PROMPT_STYLE,
            bottom_toolbar=lambda: get_bottom_toolbar(session, config),
            multiline=False
        )

        def get_input():
            width = shutil.get_terminal_size().columns - 4
            print_formatted_text(FormattedText([('class:border', '┌' + '─' * width + '┐')]))
            raw_result = prompt_session.prompt(HTML('<prompt>│ &gt; </prompt>'))
            print_formatted_text(FormattedText([('class:border', '└' + '─' * width + '┘')]))
            print()  # Single blank line after prompt box

            # Process the input and show what was detected
            if prompt_processor and raw_result.strip():
                processed, metadata = prompt_processor.process_input(raw_result)
                if metadata.get('images') or metadata.get('videos') or metadata.get('pasted_texts'):
                    print(f"\033[2m{prompt_processor.format_display(processed, metadata)}\033[0m")

            return raw_result.strip()
    else:
        get_input = lambda: input("> ").strip()

    user_input = initial if initial else get_input()

    while True:
        if not user_input:
            try:
                user_input = get_input()
                continue
            except (KeyboardInterrupt, EOFError):
                print()
                return

        # Process input for images and pasted text FIRST (before command detection)
        # This allows file paths starting with / to be recognized as paths, not commands
        # Note: Processing already done in get_input() for display, but we need to do it again
        # here to get the metadata for command detection
        processed_input = user_input
        input_metadata = {}

        if prompt_processor:
            processed_input, input_metadata = prompt_processor.process_input(user_input)

        # Handle exit/quit (with or without /)
        if user_input.lower() in ['exit', 'quit', '/exit', '/quit']:
            # Normalize to slash version for permission check
            if user_input.lower() in ['exit', '/exit']:
                cmd_to_check = '/exit'
            else:  # quit or /quit
                cmd_to_check = '/quit'

            # Check permission if command registry is available
            if command_registry:
                if not command_registry.is_enabled(cmd_to_check):
                    print(f"\n❌ Command '{cmd_to_check}' is disabled")
                    print(f"Use /commands to enable it\n")
                    user_input = get_input()
                    continue
            # Exit allowed
            print("\nGoodbye!\n")
            return

        # Check if this is a command (not a file path or pasted content)
        is_command = False
        if user_input.startswith('/'):
            if prompt_processor:
                # Use prompt processor to check if it's likely a command vs file path
                is_command = prompt_processor.is_likely_command(user_input)
            else:
                # No prompt processor - assume slash = command
                is_command = True

        if is_command:
            # Treat as command
            parts = user_input.split(maxsplit=1)
            cmd = parts[0]
            args = parts[1] if len(parts) > 1 else None
            if handle_slash_command(cmd, args, session, config, agent_manager, command_registry):
                user_input = get_input()
                continue

        # Auto-select agent based on triggers
        if AGENT_SYSTEM and agent_manager:
            new_agent = agent_manager.select_agent(processed_input, session.current_agent)
            if new_agent != session.current_agent:
                print(f"\033[2m→ Switching to {new_agent} agent\033[0m")
                session.current_agent = new_agent

        # Store original input (with image paths intact)
        actual_input = prompt_processor.get_original_text(processed_input, input_metadata) if prompt_processor else user_input
        session.add("user", actual_input)

        try:
            for turn in range(config.get("maxTurns", 25)):
                # Prepare messages with agent system if available (do this INSIDE the loop so tool results are included)
                if AGENT_SYSTEM and agent_manager:
                    prepared_messages = agent_manager.prepare_messages(
                        session.current_agent,
                        session.messages,
                        session.cwd,
                        session.session_id  # Pass session ID for caching
                    )
                else:
                    # Fallback to basic context compaction
                    session.compact_context(config.get("contextWindow", 128000))
                    prepared_messages = session.messages

                # Use prepared messages for API call
                stream = client.chat.completions.create(
                    model=session.model or config["model"],
                    messages=prepared_messages,
                    tools=TOOLS,
                    stream=True
                )

                full_content = ""
                tool_calls_dict = {}

                print()
                for chunk in stream:
                    delta = chunk.choices[0].delta if chunk.choices else None
                    if not delta:
                        continue

                    if delta.tool_calls:
                        for tc in delta.tool_calls:
                            idx = tc.index
                            if idx not in tool_calls_dict:
                                tool_calls_dict[idx] = {"id": tc.id or "", "name": "", "arguments": ""}
                            if tc.function:
                                if tc.function.name:
                                    tool_calls_dict[idx]["name"] = tc.function.name
                                if tc.function.arguments:
                                    tool_calls_dict[idx]["arguments"] += tc.function.arguments

                    if delta.content:
                        full_content += delta.content
                        print(delta.content, end='', flush=True)

                if tool_calls_dict:
                    print()
                    from types import SimpleNamespace
                    tool_calls = []
                    for idx, tc_data in tool_calls_dict.items():
                        tc_obj = SimpleNamespace(
                            id=tc_data["id"],
                            function=SimpleNamespace(name=tc_data["name"], arguments=tc_data["arguments"])
                        )
                        tool_calls.append(tc_obj)

                    session.messages.append({"role": "assistant", "tool_calls": [{"id": tc.id, "function": {"name": tc.function.name, "arguments": tc.function.arguments}} for tc in tool_calls]})

                    for tc in tool_calls:
                        print(f"\033[2m⚙ {tc.function.name}\033[0m")
                        result = execute_tool(tc.function.name, json.loads(tc.function.arguments), session.permission_manager, session.cwd)
                        session.messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
                    continue

                if full_content:
                    session.add("assistant", full_content)
                    print("\n")
                    break

        except KeyboardInterrupt:
            print("\n\033[2m[Interrupted]\033[0m\n")
        except Exception as e:
            print(f"\n\033[31mError: {e}\033[0m\n")

        session.save()

        try:
            user_input = get_input()
        except (KeyboardInterrupt, EOFError):
            print()
            return

def main():
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument('prompt', nargs='*')
    p.add_argument('-p', '--print', action='store_true')
    p.add_argument('-c', '--continue', dest='cont', action='store_true')
    p.add_argument('-r', '--resume')
    p.add_argument('--model')
    p.add_argument('--setup', action='store_true', help='Setup API key')
    p.add_argument('--rollback', action='store_true', help='Emergency rollback to previous version')
    p.add_argument('-h', '--help', action='store_true')
    args = p.parse_args()

    # Emergency rollback - runs independently
    if args.rollback:
        emergency_rollback_script = Path.home() / "opencli" / "emergency-rollback.sh"
        if emergency_rollback_script.exists():
            subprocess.run(['bash', str(emergency_rollback_script)])
        else:
            print("❌ Emergency rollback script not found")
            print(f"Expected at: {emergency_rollback_script}")
        return

    if args.setup:
        setup_api_key()
        return

    if args.help:
        print("Usage: opencli [options] [prompt]\n")
        print("OpenCLI - OpenRouter CLI with Claude Code capabilities\n")
        print("Options:")
        print("  -p, --print     Print and exit")
        print("  -c, --continue  Continue last session")
        print("  -r, --resume    Resume session")
        print("  --model         Set model")
        print("  --setup         Setup API key")
        print("  --rollback      Emergency rollback (use if CLI is broken)")
        return

    config = load_config()
    if args.model:
        config["model"] = args.model

    session = None
    if args.cont:
        session = Session.latest()
    elif args.resume:
        session = Session.load(args.resume)

    prompt = ' '.join(args.prompt) if args.prompt else None

    if args.print:
        if not prompt:
            prompt = sys.stdin.read().strip()
        client = OpenAI(base_url=config["baseURL"], api_key=config["apiKey"])
        r = client.chat.completions.create(model=config["model"], messages=[{"role": "user", "content": prompt}])
        print(r.choices[0].message.content)
    else:
        try:
            interactive(config, session, prompt)
        finally:
            # Cleanup: Unregister session on exit
            if API_SERVER and session:
                try:
                    registry = SessionRegistry(CONFIG_DIR)
                    registry.unregister_session(session.session_id)
                except:
                    pass

if __name__ == "__main__":
    main()
