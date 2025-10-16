"""
Utility functions for OpenCLI
Token counting, message preparation, client creation
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from openai import OpenAI


def count_tokens(messages: List[Dict[str, Any]]) -> int:
    """Estimate token count for messages (simple approximation)"""
    total_chars = 0
    for msg in messages:
        content = str(msg.get('content', ''))
        total_chars += len(content)
    
    # Rough approximation: 1 token ≈ 4 characters
    return total_chars // 4


def prepare_messages_with_context(messages: List[Dict[str, Any]], config_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Prepare messages with additional context"""
    if not config_dir:
        config_dir = Path.home() / '.opencli'
    
    prepared_messages = messages.copy()
    
    # Add system context if available
    system_context = []
    
    # Check for project context
    project_context_file = config_dir / 'project_context.md'
    if project_context_file.exists():
        try:
            with open(project_context_file, 'r') as f:
                context = f.read().strip()
                if context:
                    system_context.append(f"Project Context:\n{context}")
        except:
            pass
    
    # Check for custom instructions
    instructions_file = config_dir / 'instructions.md'
    if instructions_file.exists():
        try:
            with open(instructions_file, 'r') as f:
                instructions = f.read().strip()
                if instructions:
                    system_context.append(f"Custom Instructions:\n{instructions}")
        except:
            pass
    
    # Add accumulated context as system message
    if system_context:
        context_message = {
            "role": "system",
            "content": "\n\n".join(system_context)
        }
        prepared_messages.insert(0, context_message)
    
    return prepared_messages


def create_openai_client(config: Dict[str, Any]) -> OpenAI:
    """Create OpenAI client with provider-specific configuration"""
    headers = config.get("defaultHeaders", {})
    
    return OpenAI(
        base_url=config.get("baseURL", "https://api.openai.com/v1"),
        api_key=config.get("apiKey", ""),
        default_headers=headers,
        timeout=config.get("timeout", 60)
    )


def format_model_name(model: str) -> str:
    """Format model name for display"""
    if not model:
        return "Unknown"
    
    # Remove provider prefixes for cleaner display
    if "/" in model:
        return model.split("/")[-1]
    
    return model


def validate_api_key(api_key: str) -> bool:
    """Basic API key validation"""
    if not api_key:
        return False
    
    # Basic format checks
    if len(api_key) < 10:
        return False
    
    # Check for placeholder values
    placeholder_patterns = [
        "your_api_key_here",
        "sk-placeholder",
        "test_key",
        "dummy_key"
    ]
    
    if api_key.lower() in placeholder_patterns:
        return False
    
    return True


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Safely parse JSON with fallback"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def get_current_working_directory() -> str:
    """Get current working directory with error handling"""
    try:
        return os.getcwd()
    except OSError:
        return str(Path.home())


def ensure_directory_exists(path: Path) -> bool:
    """Ensure directory exists, create if needed"""
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def is_valid_session_id(session_id: str) -> bool:
    """Validate session ID format"""
    if not session_id:
        return False
    
    # Check length (UUID is 36 chars)
    if len(session_id) < 8 or len(session_id) > 50:
        return False
    
    # Check for invalid characters
    valid_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
    if not all(c in valid_chars for c in session_id):
        return False
    
    return True


def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return Path(filename).suffix.lower()


def is_text_file(filename: str) -> bool:
    """Check if file is likely a text file based on extension"""
    text_extensions = {
        '.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml',
        '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.log',
        '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd',
        '.c', '.cpp', '.h', '.hpp', '.java', '.kt', '.swift', '.go',
        '.rs', '.php', '.rb', '.pl', '.r', '.m', '.mm', '.sql'
    }
    
    return get_file_extension(filename) in text_extensions


def escape_markdown(text: str) -> str:
    """Escape markdown special characters"""
    special_chars = ['*', '_', '`', '[', ']', '(', ')', '#', '+', '-', '.', '!']
    
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    
    return text


def parse_command_args(command: str) -> tuple[str, List[str]]:
    """Parse command string into command and arguments"""
    parts = command.strip().split()
    if not parts:
        return "", []
    
    return parts[0], parts[1:]


def format_duration(seconds: float) -> str:
    """Format duration in human readable format"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def get_system_info() -> Dict[str, Any]:
    """Get basic system information"""
    import platform
    import sys
    
    return {
        "platform": platform.system(),
        "platform_version": platform.release(), 
        "architecture": platform.machine(),
        "python_version": sys.version.split()[0],
        "python_executable": sys.executable,
        "working_directory": get_current_working_directory()
    }