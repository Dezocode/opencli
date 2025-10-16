"""
Tool definitions and execution for async interactive mode
"""

import os
import glob
import asyncio
import subprocess
from pathlib import Path


# Tool definitions - MUST match opencli.py exactly
TOOLS = [
    {"type": "function", "function": {"name": "Read", "description": "Read file contents. Safe tool, auto-executes.", "parameters": {"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]}}},
    {"type": "function", "function": {"name": "Write", "description": "Write to file. [REQUIRES PERMISSION] User will be prompted to approve this operation.", "parameters": {"type": "object", "properties": {"file_path": {"type": "string"}, "content": {"type": "string"}}, "required": ["file_path", "content"]}}},
    {"type": "function", "function": {"name": "Edit", "description": "Edit file by replacing text. [REQUIRES PERMISSION] User will be prompted to approve this operation.", "parameters": {"type": "object", "properties": {"file_path": {"type": "string"}, "old_string": {"type": "string"}, "new_string": {"type": "string"}}, "required": ["file_path", "old_string", "new_string"]}}},
    {"type": "function", "function": {"name": "Bash", "description": "Execute bash command. [REQUIRES PERMISSION] User will be prompted to approve this command before execution.", "parameters": {"type": "object", "properties": {"command": {"type": "string"}, "description": {"type": "string"}}, "required": ["command"]}}},
    {"type": "function", "function": {"name": "Glob", "description": "Find files by pattern. Safe tool, auto-executes.", "parameters": {"type": "object", "properties": {"pattern": {"type": "string"}}, "required": ["pattern"]}}},
    {"type": "function", "function": {"name": "Grep", "description": "Search files for pattern. Safe tool, auto-executes.", "parameters": {"type": "object", "properties": {"pattern": {"type": "string"}}, "required": ["pattern"]}}},
]


def execute_read(file_path):
    """Execute Read tool"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"status": "success", "content": content}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def execute_write(file_path, content):
    """Execute Write tool"""
    try:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"status": "success", "message": f"Written to {file_path}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def execute_edit(file_path, old_string, new_string):
    """Execute Edit tool"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if old_string not in content:
            return {"status": "error", "error": f"String not found in {file_path}"}
        
        new_content = content.replace(old_string, new_string)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return {"status": "success", "message": f"Edited {file_path}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def execute_bash_async(command, description=None, timeout=30, current_dir=None, debug=False):
    """Execute bash command asynchronously"""
    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=current_dir
        )
        
        stdout, stderr = await asyncio.wait_for(
            process.communicate(), 
            timeout=timeout
        )
        
        return {
            "status": "success",
            "stdout": stdout.decode('utf-8'),
            "stderr": stderr.decode('utf-8'),
            "returncode": process.returncode
        }
    except asyncio.TimeoutError:
        return {"status": "error", "error": f"Command timed out after {timeout}s"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def execute_bash(command, description=None):
    """Execute bash command synchronously"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=30
        )
        return {
            "status": "success",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def execute_glob(pattern):
    """Execute Glob tool"""
    try:
        matches = glob.glob(pattern, recursive=True)
        return {"status": "success", "matches": matches}
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def execute_grep_async(pattern, timeout=10):
    """Execute Grep tool asynchronously"""
    # Placeholder - implement full grep functionality
    return {"status": "success", "matches": []}


def execute_grep(pattern):
    """Execute Grep tool synchronously"""
    # Placeholder - implement full grep functionality  
    return {"status": "success", "matches": []}


async def execute_tool_async(name, args, permission_manager=None, current_dir=None, app=None):
    """Execute a tool asynchronously"""
    if name == "Read":
        return execute_read(args["file_path"])
    elif name == "Write":
        return execute_write(args["file_path"], args["content"])
    elif name == "Edit":
        return execute_edit(args["file_path"], args["old_string"], args["new_string"])
    elif name == "Bash":
        return await execute_bash_async(
            args["command"], 
            args.get("description"),
            current_dir=current_dir
        )
    elif name == "Glob":
        return execute_glob(args["pattern"])
    elif name == "Grep":
        return await execute_grep_async(args["pattern"])
    else:
        return {"status": "error", "error": f"Unknown tool: {name}"}


def execute_tool(name, args, permission_manager=None, current_dir=None, app=None):
    """Execute a tool synchronously"""
    if name == "Read":
        return execute_read(args["file_path"])
    elif name == "Write":
        return execute_write(args["file_path"], args["content"])
    elif name == "Edit":
        return execute_edit(args["file_path"], args["old_string"], args["new_string"])
    elif name == "Bash":
        return execute_bash(args["command"], args.get("description"))
    elif name == "Glob":
        return execute_glob(args["pattern"])
    elif name == "Grep":
        return execute_grep(args["pattern"])
    else:
        return {"status": "error", "error": f"Unknown tool: {name}"}