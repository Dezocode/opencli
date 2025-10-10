"""
Core tool handlers registered with the ExecutionSystem.

These implementations avoid importing the legacy `opencli` module so they can
run safely inside the unified SDK runtime without unintended side effects.
"""

from __future__ import annotations

import asyncio
import glob
import json
import subprocess
from pathlib import Path
from typing import Any, Dict

from github_tool import execute_github_tool
from header_autoconfig import auto_configure_headers


def _write_result(app, header: str, body: str) -> None:
    app.write(f"[bold cyan]{header}[/bold cyan]\n{body}\n\n")


def _base_dir(session, context) -> Path:
    if context.get("cwd"):
        return Path(context["cwd"]).expanduser().resolve()
    if hasattr(session, "cwd") and session.cwd:
        return Path(session.cwd).expanduser().resolve()
    return Path.cwd()


async def tool_read(app, session, **context):
    file_path = context.get("file_path") or context.get("path")
    if not file_path:
        app.write("[red]Read tool requires `file_path`.[/red]\n\n")
        return None

    target = Path(file_path).expanduser()

    def _read() -> str:
        try:
            return target.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return target.read_text(encoding="utf-8", errors="replace")

    try:
        result = await asyncio.to_thread(_read)
    except FileNotFoundError:
        app.write(f"[red]File not found:[/red] {target}\n\n")
        return None
    except Exception as exc:
        app.write(f"[red]Failed to read {target}: {exc}[/red]\n\n")
        return None

    _write_result(app, f"Contents of {target}", result)
    return result


async def tool_write(app, session, **context):
    file_path = context.get("file_path")
    content = context.get("content")
    if not file_path or content is None:
        app.write("[red]Write tool requires `file_path` and `content`.[/red]\n\n")
        return None

    target = Path(file_path).expanduser()

    def _write() -> str:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(str(content), encoding="utf-8")
        return f"Wrote {len(str(content))} chars to {target}"

    try:
        result = await asyncio.to_thread(_write)
    except Exception as exc:
        app.write(f"[red]Failed to write {target}: {exc}[/red]\n\n")
        return None

    _write_result(app, "Write Result", result)
    return result


async def tool_edit(app, session, **context):
    file_path = context.get("file_path")
    old_string = context.get("old_string")
    new_string = context.get("new_string")

    if not all([file_path, old_string, new_string]):
        app.write("[red]Edit tool requires `file_path`, `old_string`, and `new_string`.[/red]\n\n")
        return None

    target = Path(file_path).expanduser()

    def _edit() -> str:
        text = target.read_text(encoding="utf-8")
        if old_string not in text:
            return "The original text was not found; no changes applied."
        updated = text.replace(old_string, new_string, 1)
        target.write_text(updated, encoding="utf-8")
        return "File updated successfully."

    try:
        result = await asyncio.to_thread(_edit)
    except FileNotFoundError:
        app.write(f"[red]File not found:[/red] {target}\n\n")
        return None
    except Exception as exc:
        app.write(f"[red]Failed to edit {target}: {exc}[/red]\n\n")
        return None

    _write_result(app, "Edit Result", result)
    return result


async def tool_bash(app, session, **context):
    command = context.get("command")
    description = context.get("description")
    if not command:
        app.write("[red]Bash tool requires `command`.[/red]\n\n")
        return None

    def _run() -> str:
        try:
            completed = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=context.get("timeout", 120),
            )
            output = completed.stdout + completed.stderr
            if not output.strip():
                output = "Command completed with no output."
            return output.strip()
        except Exception as exc:
            return f"Error executing bash command: {exc}"

    result = await asyncio.to_thread(_run)
    header = f"$ {command}" if not description else f"$ {command} — {description}"
    _write_result(app, header, result)
    return result


async def tool_glob(app, session, **context):
    pattern = context.get("pattern")
    if not pattern:
        app.write("[red]Glob tool requires `pattern`.[/red]\n\n")
        return None

    base = _base_dir(session, context)

    def _search() -> str:
        matches = glob.glob(str(base / pattern), recursive=True)
        if not matches:
            return "No files matched."
        try:
            relative = [str(Path(match).resolve().relative_to(base)) for match in matches]
        except Exception:
            relative = matches
        return "\n".join(sorted(relative))

    result = await asyncio.to_thread(_search)
    _write_result(app, f"Glob: {pattern}", result)
    return result


async def tool_grep(app, session, **context):
    pattern = context.get("pattern")
    if not pattern:
        app.write("[red]Grep tool requires `pattern`.[/red]\n\n")
        return None

    base = _base_dir(session, context)

    def _search() -> str:
        try:
            completed = subprocess.run(
                ["grep", "-rnI", pattern, str(base)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = completed.stdout
        except FileNotFoundError:
            output = "grep command not available on this system."
        except subprocess.TimeoutExpired:
            output = "grep search timed out."

        return output.strip() or "No matches found."

    result = await asyncio.to_thread(_search)
    _write_result(app, f"Grep: {pattern}", result)
    return result


async def tool_github(app, session, **context):
    action = context.get("action")
    if not action:
        app.write("[red]GitHub tool requires `action`.[/red]\n\n")
        return None

    result = await asyncio.to_thread(execute_github_tool, action, **context)
    _write_result(app, f"GitHub: {action}", result)
    return result


async def tool_configure_headers(app, session, **context):
    provider = context.get("provider")
    model = context.get("model")
    current_headers = context.get("current_headers", {}) or {}

    if not model:
        app.write("[red]ConfigureHeaders tool requires `model`.[/red]\n\n")
        return None

    success, new_headers, message = await auto_configure_headers(model, current_headers)
    payload: Dict[str, Any] = {
        "success": success,
        "message": message,
        "headers": new_headers or {},
    }
    pretty = json.dumps(payload, indent=2)
    title = f"Header configuration for {provider or 'active provider'}"
    _write_result(app, title, pretty)
    return payload
