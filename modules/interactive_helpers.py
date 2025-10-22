"""
CLI Interactive Helpers
Helper functions for interactive mode operations and OpenRouter configuration
"""

import os
import asyncio
from typing import Dict, Any

def configure_openrouter_headers_cli(policy_message: str, session, config, model_mgr) -> str:
    """Configure OpenRouter headers based on policy error
    
    Args:
        policy_message: Policy error message
        session: Current session
        config: Configuration dictionary
        model_mgr: Model manager instance
        
    Returns:
        Action to take: "retry" or "denied"
    """
    provider_id = model_mgr.get_provider_for_model(session.model or config.get("model")) or config.get("provider") or "openrouter"
    current_headers = config.get("defaultHeaders", {}) or {}
    model_id = session.model or config.get("model")
    
    # Check model uptime if available
    if provider_id == "openrouter" and model_id:
        try:
            from modules.uptime_checker import check_model_uptime, is_model_healthy, get_user_recommendation
            
            print("\n🔍 Checking model availability...")
            try:
                try:
                    success, uptime, status_msg = asyncio.run(check_model_uptime(model_id))
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    try:
                        success, uptime, status_msg = loop.run_until_complete(check_model_uptime(model_id))
                    finally:
                        loop.close()
                
                if success and uptime is not None:
                    print(f"📊 {status_msg}\n")
                    if not is_model_healthy(uptime):
                        recommendation = get_user_recommendation(uptime, model_id)
                        print(f"⚠️  Warning: Low Model Availability\n\n{recommendation}\n")
                else:
                    print(f"⚠️  Could not fetch uptime: {status_msg}\n")
            except Exception as uptime_error:
                print(f"⚠️  Could not fetch uptime: {uptime_error}\n")
        except ImportError:
            pass  # Uptime checker not available
    
    # Check for environment variables
    proposed = {}
    env_referer = os.getenv("OPENROUTER_SITE_URL")
    env_title = os.getenv("OPENROUTER_APP_NAME")
    if env_referer:
        proposed["HTTP-Referer"] = env_referer
    if env_title:
        proposed["X-Title"] = env_title
    if not proposed:
        proposed = None
    
    args = {
        "provider": provider_id,
        "model": session.model or config.get("model"),
        "issue": policy_message,
        "current_headers": current_headers,
        "proposed_headers": proposed
    }
    
    # Check permissions
    allow_update = True
    if getattr(session, "permission_manager", None):
        should_prompt, reason, _ = session.permission_manager.should_prompt(
            "ConfigureHeaders",
            args,
            session.cwd
        )
        if should_prompt:
            print(f"\n⚠️  {policy_message}\n")
            if proposed:
                print("Suggested headers (from environment variables):")
                for key, value in proposed.items():
                    print(f"  • {key}: {value}")
            else:
                print("This OpenRouter model requires HTTP-Referer and X-Title headers.")
                print("Provide the values you registered at https://openrouter.ai/settings/privacy.\n")
            response = input("Allow OpenCLI to update these headers now? [y/N]: ").strip().lower()
            allow_update = response in ("y", "yes")
    else:
        print(f"\n⚠️  {policy_message}\n")
    
    if not allow_update:
        print("Headers unchanged. Update your OpenRouter privacy settings or set OPENROUTER_SITE_URL / OPENROUTER_APP_NAME and try again.\n")
        return "denied"
    
    # Apply proposed headers if available
    if proposed:
        model_mgr.update_provider_headers(provider_id, proposed, None)
        config.update(model_mgr.config)
        print("\n✅ Applied header overrides from environment.\n")
        return "retry"
    
    # Interactive header input
    referer_default = current_headers.get("HTTP-Referer", "")
    title_default = current_headers.get("X-Title", "")
    referer = input(f"HTTP-Referer [{referer_default}]: ").strip() or referer_default
    title = input(f"X-Title [{title_default}]: ").strip() or title_default
    
    new_headers = {}
    if referer:
        new_headers["HTTP-Referer"] = referer
    if title:
        new_headers["X-Title"] = title
    
    if not new_headers:
        print("No header values provided. Headers unchanged.\n")
        return "denied"
    
    model_mgr.update_provider_headers(provider_id, new_headers, None)
    config.update(model_mgr.config)
    print("\n✅ Updated OpenRouter headers.\n")
    return "retry"


def get_git_info():
    """Get current git repository information
    
    Returns:
        Tuple of (repo_name, branch)
    """
    try:
        import subprocess
        from pathlib import Path
        
        branch = subprocess.run(['git', 'branch', '--show-current'], 
                              capture_output=True, text=True, timeout=1).stdout.strip()
        repo = subprocess.run(['git', 'rev-parse', '--show-toplevel'], 
                            capture_output=True, text=True, timeout=1).stdout.strip()
        repo_name = Path(repo).name if repo else ''
        return repo_name, branch
    except:
        return '', ''


def get_bottom_toolbar(session, config):
    """Create bottom toolbar for rich prompt
    
    Args:
        session: Current session
        config: Configuration dictionary
        
    Returns:
        HTML formatted toolbar
    """
    from ..utils import count_tokens, format_model_name
    
    tokens = count_tokens(session.messages)
    context = config.get("contextWindow", 128000)
    percent = int((tokens / context) * 100) if context > 0 else 0
    
    repo_name, branch = get_git_info()
    cwd = os.getcwd()
    
    line1 = f'<violet>Session: {session.session_id[:8]} | Model: {format_model_name(session.model or config["model"])} | Tokens: {tokens}/{context} ({percent}%)</violet>'
    
    if repo_name and branch:
        line2 = f'\n<cyan>{cwd}</cyan> <cyan>{repo_name}</cyan> <ansibrightblack>({branch})</ansibrightblack>'
    else:
        line2 = f'\n<cyan>{cwd}</cyan>'
    
    try:
        from prompt_toolkit.formatted_text import HTML
        return HTML(f'{line1}{line2}')
    except ImportError:
        return f'{line1}{line2}'


def ensure_prompt_at_bottom():
    """Move cursor to bottom of terminal and clear lines for prompt area"""
    try:
        import shutil
        term_height = shutil.get_terminal_size().lines
        
        # Reserve 5 lines at bottom (3 for prompt box, 2 for status bar)
        reserved_lines = 5
        
        # Move cursor to position where prompt should start
        prompt_start_row = term_height - reserved_lines + 1
        
        # Move cursor to bottom area
        print(f"\033[{prompt_start_row};1H", end='', flush=True)
        
        # Clear from cursor to end of screen
        print("\033[J", end='', flush=True)
        
    except:
        # Fallback: just add some newlines
        print("\n" * 3, end='', flush=True)