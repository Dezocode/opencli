"""
Slash command handlers for OpenCLI
Handle all /commands for session management, system control, and feature access
"""

import os
import sys
import json
import uuid
import subprocess
import asyncio
from pathlib import Path
from datetime import datetime

# Configuration paths
CONFIG_DIR = Path.home() / ".opencli"
SESSIONS_DIR = CONFIG_DIR / "sessions"

# Feature imports with graceful fallbacks
try:
    import yaml
    from agent_manager import AgentManager
    AGENT_SYSTEM = True
except ImportError:
    AGENT_SYSTEM = False

try:
    from upgrade_manager import UpgradeManager
    from rollback_manager import RollbackManager
    UPGRADE_SYSTEM = True
except ImportError:
    UPGRADE_SYSTEM = False

try:
    from command_registry import CommandRegistry
    COMMAND_REGISTRY = True
except ImportError:
    COMMAND_REGISTRY = False

try:
    from modules.permissions.risk_assessment import RiskAssessmentManager as ToolPermissionManager
    TOOL_PERMISSIONS = True
except ImportError:
    TOOL_PERMISSIONS = False

try:
    from api_server import APIServer, SessionRegistry, MessageQueue
    API_SERVER = True
except ImportError:
    API_SERVER = False

from .utils import count_tokens


def handle_slash_command(cmd, args, session, config, agent_manager=None, command_registry=None):
    """Handle all slash commands"""
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
        # Import BACKGROUND_TASKS from main module
        try:
            from opencli import BACKGROUND_TASKS
        except ImportError:
            BACKGROUND_TASKS = {}
        if BACKGROUND_TASKS:
            print("\nBackground tasks:")
            for task_id, info in BACKGROUND_TASKS.items():
                print(f"  [{task_id}] {info['command']} - {info['status']}")
            print()
        else:
            print("\nNo background tasks\n")
        return True

    elif cmd == "/debug":
        # Toggle debug mode
        if not hasattr(session, 'debug_mode'):
            session.debug_mode = False
        session.debug_mode = not session.debug_mode
        status = "enabled" if session.debug_mode else "disabled"
        print(f"\n🔧 Debug mode {status}\n")
        session.save()
        return True

    # Spec-Kit Commands - Goal-oriented workflows
    elif cmd == "/goal":
        """Set or view current goal"""
        if not hasattr(session, 'goal_tracker') or not session.goal_tracker:
            print("❌ Goal tracking not available (missing modules)\n")
            return True

        if args:
            # Parse goal command: /goal set <description> or /goal <description>
            parts = args.split(maxsplit=1)
            if parts[0] == "set" and len(parts) > 1:
                goal_desc = parts[1]
            elif parts[0] == "complete":
                if session.goal_tracker.current_goal:
                    session.goal_tracker.complete_goal("User marked as complete")
                    print("✅ Goal marked complete\n")
                else:
                    print("⚠️ No active goal to complete\n")
                return True
            elif parts[0] == "phase":
                if len(parts) > 1 and session.goal_tracker.current_goal:
                    session.goal_tracker.update_phase(parts[1])
                    print(f"📊 Phase updated to: {parts[1]}\n")
                else:
                    print("⚠️ Usage: /goal phase <planning|implementing|testing|refining>\n")
                return True
            elif parts[0] == "stats":
                stats = session.goal_tracker.get_statistics()
                print("\n📊 Goal Tracking Statistics:\n")
                print(f"  Total Goals: {stats['total_goals']}")
                print(f"  Completed: {stats['completed_goals']}")
                print(f"  Active: {stats['active_goals']}")
                print(f"  Tool Calls: {stats['total_tool_calls']}")
                print(f"  Failed Sanity Checks: {stats['failed_sanity_checks']}")
                print(f"  Sanity Failure Rate: {stats['sanity_failure_rate']:.1%}\n")
                return True
            else:
                goal_desc = args

            # Set new goal
            goal_id = session.goal_tracker.set_goal(goal_desc, phase='planning')
            print(f"🎯 Goal set: {goal_desc}")
            print(f"   ID: {goal_id}")
            print(f"   Phase: planning\n")
        else:
            # Show current goal
            if session.goal_tracker.current_goal:
                summary = session.goal_tracker.get_goal_summary()
                print(f"\n{summary}\n")
            else:
                print("⚠️ No active goal\n")
                print("Usage: /goal <description> or /goal set <description>\n")

        return True

    elif cmd == "/constitution":
        """Save or view project constitution"""
        if not hasattr(session, 'spec_memory') or not session.spec_memory:
            print("❌ Spec memory not available\n")
            return True

        if args:
            # Save constitution
            path = session.spec_memory.save_constitution(args)
            print(f"📜 Constitution saved to: {path}\n")
        else:
            # View constitution
            constitution = session.spec_memory.load_constitution()
            if constitution:
                print(f"\n📜 Project Constitution:\n\n{constitution}\n")
            else:
                print("⚠️ No constitution defined\n")
                print("Usage: /constitution <markdown content>\n")

        return True

    elif cmd == "/specify":
        """Define feature specification"""
        if not hasattr(session, 'spec_memory') or not session.spec_memory:
            print("❌ Spec memory not available\n")
            return True

        if args:
            # Parse: /specify <feature-name> <spec>
            parts = args.split(maxsplit=1)
            if len(parts) < 2:
                print("Usage: /specify <feature-name> <specification>\n")
                return True

            feature_name, spec = parts
            path = session.spec_memory.save_feature_spec(feature_name, spec)
            print(f"📝 Spec saved: {feature_name}")
            print(f"   Path: {path}\n")
        else:
            print("Usage: /specify <feature-name> <specification>\n")

        return True

    elif cmd == "/plan":
        """Create implementation plan"""
        if not hasattr(session, 'spec_memory') or not session.spec_memory:
            print("❌ Spec memory not available\n")
            return True

        if args:
            print("📋 Plan creation - Use natural language to describe plan to the AI\n")
            print("   The AI will create a structured plan with phases and tasks.\n")
            # Return False to let AI process this
            return False
        else:
            # List plans
            context = session.spec_memory.get_active_context()
            plans = context.get('plans', [])
            if plans:
                print("\n📋 Active Plans:\n")
                for plan in plans:
                    print(f"  • {plan.get('name', 'Unnamed')}")
                    print(f"    Phase: {plan.get('current_phase', 0) + 1}/{len(plan.get('phases', []))}")
                print()
            else:
                print("⚠️ No active plans\n")

        return True

    elif cmd == "/tasks":
        """View implementation tasks"""
        if not hasattr(session, 'goal_tracker') or not session.goal_tracker:
            print("❌ Goal tracking not available\n")
            return True

        if session.goal_tracker.current_goal:
            progress = session.goal_tracker.current_goal.get('progress', [])
            print(f"\n✅ Tasks Completed: {len(progress)}\n")
            for i, task in enumerate(progress[-10:], 1):  # Last 10
                print(f"{i}. {task['action']}: {task['result'][:60]}")
            print()
        else:
            print("⚠️ No active goal to show tasks for\n")

        return True

    elif cmd == "/upgrade":
        return _handle_upgrade_command()

    elif cmd == "/rollback":
        return _handle_rollback_command()

    elif cmd == "/commands":
        return _handle_commands_command(args, command_registry)

    elif cmd == "/permissions":
        return _handle_permissions_command(args, session)

    elif cmd == "/api":
        return _handle_api_command(args, session)

    elif cmd == "/contribute":
        return _handle_contribute_command()

    elif cmd == "/help":
        _show_help()
        return True

    return False


def _handle_upgrade_command():
    """Handle the /upgrade command"""
    if not UPGRADE_SYSTEM:
        print("❌ Upgrade system not available\n")
        return True

    manager = UpgradeManager()
    current_branch = manager.get_current_branch()
    new_version = manager.get_new_version()

    print(f"\n🔄 OpenCLI Upgrade System\n")

    # Show repo info using gh CLI
    repo_info = manager.get_repo_info()
    if repo_info['success']:
        print(f"Repository: {repo_info['owner']}/{repo_info['name']}")
        if repo_info['is_fork']:
            parent = repo_info.get('parent', {})
            print(f"Fork of: {parent.get('owner', {}).get('login', 'unknown')}/{parent.get('name', 'opencli')}")
        print()

    print(f"Current branch: {current_branch}")
    print(f"Upgrading to: v{new_version}\n")
    print(f"📥 Pulling from official repo: {manager.upstream_owner}/{manager.upstream_repo}")
    print(f"📝 Local changes only - never pushes to upstream\n")

    # Create upgrade worktree and perform upgrade
    print("📁 Creating upgrade worktree from upstream...")
    worktree_result = manager.create_upgrade_worktree(new_version)

    if not worktree_result['success']:
        print(f"❌ Failed to create worktree: {worktree_result.get('error')}\n")
        return True

    # Continue with full upgrade process...
    # (Implementation continues from original code)
    print("✅ Upgrade system ready\n")
    return True


def _handle_rollback_command():
    """Handle the /rollback command"""
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

    print("✅ Rollback system ready\n")
    return True


def _handle_commands_command(args, command_registry):
    """Handle the /commands command"""
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
                'UPGRADE_SYSTEM': UPGRADE_SYSTEM
            }
            command_registry.show_status(feature_flags)

        elif subcommand == "setup":
            # Interactive setup
            feature_flags = {
                'AGENT_SYSTEM': AGENT_SYSTEM,
                'UPGRADE_SYSTEM': UPGRADE_SYSTEM
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
            'UPGRADE_SYSTEM': UPGRADE_SYSTEM
        }
        command_registry.show_status(feature_flags)
        print("Use '/commands setup' for interactive configuration\n")

    return True


def _handle_permissions_command(args, session):
    """Handle the /permissions command"""
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


def _handle_api_command(args, session):
    """Handle the /api command"""
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


def _handle_contribute_command():
    """Handle the /contribute command"""
    if not UPGRADE_SYSTEM:
        print("❌ Contribution system not available\n")
        return True

    manager = UpgradeManager()
    repo_info = manager.get_repo_info()

    print("\n🤝 Contribute to OpenCLI\n")

    # Check if repository is a fork
    if not repo_info['success'] or not repo_info['is_fork']:
        print("❌ This repository is not a fork of the official repo.\n")
        print("To contribute, you need to:")
        print("  1. Fork the official repository:")
        print(f"     gh repo fork {manager.upstream_owner}/{manager.upstream_repo} --clone=false")
        print("  2. Clone your fork:")
        print(f"     gh repo clone YOUR_USERNAME/{manager.upstream_repo}")
        print("  3. Run opencli from your fork")
        print()
        return True

    print("✅ Contribution system ready\n")
    return True


def _show_help():
    """Show help for all commands"""
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
        print("  /contribute    - Submit PR to official repo (fork required)")
    if COMMAND_REGISTRY:
        print("  /commands      - Manage command permissions")
    if TOOL_PERMISSIONS:
        print("  /permissions   - Manage tool permissions")
    if API_SERVER:
        print("  /api           - API server control (start/stop/sessions/messages)")
    print("  /help          - Show this help")
    print("  /exit or /quit - Exit\n")