"""
Tool execution functions for OpenCLI
File operations, bash commands, search tools
"""

import os
import glob
import subprocess
import re
from pathlib import Path
from typing import Dict, Any, List, Optional


# Tool definitions for OpenCLI
TOOLS = [
    {
        "name": "Read",
        "description": "Read file contents",
        "parameters": ["file_path"],
        "safe": True
    },
    {
        "name": "Write",
        "description": "Write content to file",
        "parameters": ["file_path", "content"],
        "safe": False,
        "requires_permission": True
    },
    {
        "name": "Edit",
        "description": "Edit file by replacing text",
        "parameters": ["file_path", "old_string", "new_string"],
        "safe": False,
        "requires_permission": True
    },
    {
        "name": "Bash",
        "description": "Execute shell command",
        "parameters": ["command", "description"],
        "safe": False,
        "requires_permission": True
    },
    {
        "name": "Glob",
        "description": "Find files by pattern",
        "parameters": ["pattern"],
        "safe": True
    },
    {
        "name": "Grep",
        "description": "Search for pattern in files",
        "parameters": ["pattern", "path", "recursive"],
        "safe": True
    }
]


def execute_read(file_path: str) -> Dict[str, Any]:
    """Execute Read tool - read file contents"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"status": "success", "content": content}
    except FileNotFoundError:
        return {"status": "error", "error": f"File not found: {file_path}"}
    except PermissionError:
        return {"status": "error", "error": f"Permission denied: {file_path}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def execute_write(file_path: str, content: str) -> Dict[str, Any]:
    """Execute Write tool - write content to file"""
    try:
        # Create directories if they don't exist
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"status": "success", "message": f"Successfully wrote to {file_path}"}
    except PermissionError:
        return {"status": "error", "error": f"Permission denied: {file_path}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def execute_edit(file_path: str, old_string: str, new_string: str) -> Dict[str, Any]:
    """Execute Edit tool - replace text in file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if old_string not in content:
            return {"status": "error", "error": f"String not found in {file_path}"}
        
        # Count occurrences to warn about multiple matches
        count = content.count(old_string)
        if count > 1:
            return {
                "status": "warning", 
                "message": f"Found {count} occurrences. Only first occurrence will be replaced.",
                "content": content.replace(old_string, new_string, 1)
            }
        
        new_content = content.replace(old_string, new_string)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        return {"status": "success", "message": f"Successfully edited {file_path}"}
    except FileNotFoundError:
        return {"status": "error", "error": f"File not found: {file_path}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def execute_bash(command: str, description: Optional[str] = None) -> Dict[str, Any]:
    """Execute Bash tool - run shell command"""
    try:
        # Security: Basic command validation
        dangerous_patterns = [
            r'rm\s+-rf\s+/',      # rm -rf /
            r':\(\)\{.*\};:',     # fork bomb
            r'>\s*/dev/sd[a-z]',  # write to disk
            r'dd\s+if=.*of=/',    # disk operations
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, command):
                return {"status": "error", "error": "Command blocked for security reasons"}
        
        # Execute command with timeout
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,  # 30 second timeout
            cwd=os.getcwd()
        )
        
        return {
            "status": "success",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "command": command,
            "description": description
        }
        
    except subprocess.TimeoutExpired:
        return {"status": "error", "error": "Command timed out after 30 seconds"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def execute_glob(pattern: str) -> Dict[str, Any]:
    """Execute Glob tool - find files by pattern"""
    try:
        matches = glob.glob(pattern, recursive=True)
        matches.sort()  # Sort for consistent output
        
        return {
            "status": "success",
            "pattern": pattern,
            "matches": matches,
            "count": len(matches)
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def execute_grep(pattern: str, path: str = ".", recursive: bool = True) -> Dict[str, Any]:
    """Execute Grep tool - search for pattern in files"""
    try:
        matches = []
        search_path = Path(path)
        
        if search_path.is_file():
            # Search in single file
            matches.extend(_grep_file(pattern, search_path))
        elif search_path.is_dir():
            # Search in directory
            if recursive:
                for file_path in search_path.rglob("*"):
                    if file_path.is_file() and _is_text_file(file_path):
                        matches.extend(_grep_file(pattern, file_path))
            else:
                for file_path in search_path.iterdir():
                    if file_path.is_file() and _is_text_file(file_path):
                        matches.extend(_grep_file(pattern, file_path))
        
        return {
            "status": "success",
            "pattern": pattern,
            "path": str(path),
            "matches": matches,
            "count": len(matches)
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def _grep_file(pattern: str, file_path: Path) -> List[Dict[str, Any]]:
    """Search for pattern in a single file"""
    matches = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    matches.append({
                        "file": str(file_path),
                        "line": line_num,
                        "content": line.rstrip(),
                        "match": pattern
                    })
    except Exception:
        # Skip files that can't be read
        pass
    
    return matches


def _is_text_file(file_path: Path) -> bool:
    """Check if file is likely a text file"""
    # Skip binary files, images, etc.
    binary_extensions = {
        '.bin', '.exe', '.dll', '.so', '.dylib',
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico',
        '.mp3', '.mp4', '.avi', '.mov', '.wav',
        '.zip', '.tar', '.gz', '.bz2', '.xz',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx',
        '.sqlite', '.db', '.sqlite3'
    }
    
    if file_path.suffix.lower() in binary_extensions:
        return False
    
    # Check file size (skip very large files)
    try:
        if file_path.stat().st_size > 10 * 1024 * 1024:  # 10MB limit
            return False
    except:
        return False
    
    return True


def execute_tool(name: str, args: Dict[str, Any], permission_manager=None, current_dir: Optional[str] = None) -> Dict[str, Any]:
    """Execute a tool by name with given arguments"""
    # Change directory if specified
    original_dir = None
    if current_dir:
        original_dir = os.getcwd()
        try:
            os.chdir(current_dir)
        except Exception as e:
            return {"status": "error", "error": f"Cannot change to directory {current_dir}: {e}"}
    
    try:
        # Route to appropriate tool executor
        if name == "Read":
            return execute_read(args.get("file_path", ""))
        elif name == "Write":
            return execute_write(args.get("file_path", ""), args.get("content", ""))
        elif name == "Edit":
            return execute_edit(
                args.get("file_path", ""),
                args.get("old_string", ""),
                args.get("new_string", "")
            )
        elif name == "Bash":
            return execute_bash(args.get("command", ""), args.get("description"))
        elif name == "Glob":
            return execute_glob(args.get("pattern", ""))
        elif name == "Grep":
            return execute_grep(
                args.get("pattern", ""),
                args.get("path", "."),
                args.get("recursive", True)
            )
        else:
            return {"status": "error", "error": f"Unknown tool: {name}"}
            
    finally:
        # Restore original directory
        if original_dir:
            try:
                os.chdir(original_dir)
            except:
                pass


def get_tool_list() -> List[Dict[str, Any]]:
    """Get list of available tools with descriptions"""
    return [
        {
            "name": "Read",
            "description": "Read file contents",
            "parameters": ["file_path"],
            "safe": True
        },
        {
            "name": "Write", 
            "description": "Write content to file",
            "parameters": ["file_path", "content"],
            "safe": False,
            "requires_permission": True
        },
        {
            "name": "Edit",
            "description": "Edit file by replacing text",
            "parameters": ["file_path", "old_string", "new_string"],
            "safe": False,
            "requires_permission": True
        },
        {
            "name": "Bash",
            "description": "Execute shell command", 
            "parameters": ["command", "description"],
            "safe": False,
            "requires_permission": True
        },
        {
            "name": "Glob",
            "description": "Find files by pattern",
            "parameters": ["pattern"],
            "safe": True
        },
        {
            "name": "Grep",
            "description": "Search for pattern in files",
            "parameters": ["pattern", "path", "recursive"],
            "safe": True
        }
    ]


def validate_tool_args(tool_name: str, args: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """Validate tool arguments"""
    tool_specs = {
        "Read": {"required": ["file_path"], "optional": []},
        "Write": {"required": ["file_path", "content"], "optional": []},
        "Edit": {"required": ["file_path", "old_string", "new_string"], "optional": []},
        "Bash": {"required": ["command"], "optional": ["description"]},
        "Glob": {"required": ["pattern"], "optional": []},
        "Grep": {"required": ["pattern"], "optional": ["path", "recursive"]}
    }
    
    if tool_name not in tool_specs:
        return False, f"Unknown tool: {tool_name}"
    
    spec = tool_specs[tool_name]
    
    # Check required parameters
    for param in spec["required"]:
        if param not in args:
            return False, f"Missing required parameter: {param}"
        if not args[param]:  # Check for empty values
            return False, f"Empty value for required parameter: {param}"
    
    # Check for unexpected parameters
    valid_params = set(spec["required"] + spec["optional"])
    provided_params = set(args.keys())
    unexpected = provided_params - valid_params
    
    if unexpected:
        return False, f"Unexpected parameters: {', '.join(unexpected)}"
    
    return True, None