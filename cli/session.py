"""
Session management for OpenCLI
Session creation, loading, saving, and context management
"""

import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Session storage directory
SESSIONS_DIR = Path.home() / '.opencli' / 'sessions'
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


class Session:
    """OpenCLI conversation session"""
    
    def __init__(self, session_id: Optional[str] = None, model: Optional[str] = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.messages: List[Dict[str, Any]] = []
        self.model = model
        self.file = SESSIONS_DIR / f"{self.session_id}.json"
        self.cwd = os.getcwd()
        self.current_agent = 'assistant'
        self.permission_manager = None
        self.debug_mode = False

    def add(self, role: str, content: str) -> None:
        """Add a message to the session"""
        self.messages.append({"role": role, "content": content})

    def compact_context(self, max_tokens: int) -> None:
        """Compact context to fit within token limits"""
        from .utils import count_tokens
        
        if count_tokens(self.messages) > max_tokens * 0.8:
            # Keep first 2 messages (usually system prompt + first user) and last 10
            self.messages = self.messages[:2] + self.messages[-10:]
            print("\033[2m[Context compacted to fit window]\033[0m")

    def save(self) -> None:
        """Save session to disk"""
        try:
            with open(self.file, 'w') as f:
                json.dump({
                    "session_id": self.session_id,
                    "model": self.model,
                    "messages": self.messages,
                    "cwd": self.cwd,
                    "debug_mode": getattr(self, 'debug_mode', False),
                    "timestamp": datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save session: {e}")

    @classmethod
    def load(cls, session_id: str) -> Optional['Session']:
        """Load session from disk"""
        session_file = SESSIONS_DIR / f"{session_id}.json"
        
        if not session_file.exists():
            return None
            
        try:
            with open(session_file, 'r') as f:
                data = json.load(f)
            
            # Create session object
            session = cls(data["session_id"], data.get("model"))
            session.messages = data.get("messages", [])
            session.cwd = data.get("cwd", os.getcwd())
            session.debug_mode = data.get("debug_mode", False)

            # Fix malformed tool calls from old sessions
            session._fix_malformed_messages()
            
            return session
            
        except Exception as e:
            print(f"⚠️ Could not load session {session_id}: {e}")
            return None

    def _fix_malformed_messages(self) -> None:
        """Fix malformed tool calls from old sessions"""
        for msg in self.messages:
            if msg.get("role") == "assistant" and "tool_calls" in msg:
                # Ensure content field exists
                if "content" not in msg:
                    msg["content"] = None
                
                # Fix tool calls format
                for tc in msg.get("tool_calls", []):
                    if "type" not in tc:
                        tc["type"] = "function"
                    
                    if "function" in tc and "arguments" in tc["function"]:
                        # Ensure arguments is a dict, not a string
                        args = tc["function"]["arguments"]
                        if isinstance(args, str):
                            try:
                                tc["function"]["arguments"] = json.loads(args)
                            except json.JSONDecodeError:
                                # If can't parse, wrap in generic structure
                                tc["function"]["arguments"] = {"raw": args}

    def get_context_summary(self) -> Dict[str, Any]:
        """Get summary of session context"""
        from .utils import count_tokens
        
        return {
            "session_id": self.session_id,
            "model": self.model,
            "message_count": len(self.messages),
            "token_count": count_tokens(self.messages),
            "cwd": self.cwd,
            "debug_mode": self.debug_mode,
            "current_agent": self.current_agent,
            "has_permission_manager": self.permission_manager is not None
        }

    def clear_messages(self) -> None:
        """Clear all messages from session"""
        self.messages = []

    def get_last_n_messages(self, n: int) -> List[Dict[str, Any]]:
        """Get last N messages"""
        return self.messages[-n:] if n > 0 else []

    def count_messages_by_role(self) -> Dict[str, int]:
        """Count messages by role"""
        counts = {}
        for msg in self.messages:
            role = msg.get("role", "unknown")
            counts[role] = counts.get(role, 0) + 1
        return counts

    def export_conversation(self, format: str = "markdown") -> str:
        """Export conversation in specified format"""
        if format == "markdown":
            return self._export_markdown()
        elif format == "json":
            return json.dumps(self.messages, indent=2)
        elif format == "text":
            return self._export_text()
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _export_markdown(self) -> str:
        """Export conversation as markdown"""
        lines = [f"# OpenCLI Conversation - {self.session_id}\n"]
        lines.append(f"**Model:** {self.model}")
        lines.append(f"**Messages:** {len(self.messages)}")
        lines.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("\n---\n")
        
        for i, msg in enumerate(self.messages):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            
            if role == "user":
                lines.append(f"## 👤 User\n\n{content}\n")
            elif role == "assistant":
                lines.append(f"## 🤖 Assistant\n\n{content}\n")
            elif role == "system":
                lines.append(f"## ⚙️ System\n\n{content}\n")
            else:
                lines.append(f"## {role}\n\n{content}\n")
        
        return "\n".join(lines)

    def _export_text(self) -> str:
        """Export conversation as plain text"""
        lines = [f"OpenCLI Conversation - {self.session_id}"]
        lines.append(f"Model: {self.model}")
        lines.append(f"Messages: {len(self.messages)}")
        lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 50)
        
        for msg in self.messages:
            role = msg.get("role", "unknown").upper()
            content = msg.get("content", "")
            lines.append(f"\n[{role}]\n{content}\n")
        
        return "\n".join(lines)


def list_sessions() -> List[Dict[str, Any]]:
    """List all available sessions"""
    sessions = []
    
    for session_file in SESSIONS_DIR.glob("*.json"):
        try:
            with open(session_file, 'r') as f:
                data = json.load(f)
            
            sessions.append({
                "session_id": data.get("session_id"),
                "model": data.get("model"),
                "message_count": len(data.get("messages", [])),
                "timestamp": data.get("timestamp"),
                "file": str(session_file)
            })
        except:
            continue  # Skip corrupted session files
    
    # Sort by timestamp (newest first)
    sessions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return sessions


def delete_session(session_id: str) -> bool:
    """Delete a session"""
    session_file = SESSIONS_DIR / f"{session_id}.json"
    
    if session_file.exists():
        try:
            session_file.unlink()
            return True
        except Exception as e:
            print(f"⚠️ Could not delete session: {e}")
            return False
    
    return False


def cleanup_old_sessions(days: int = 30) -> int:
    """Clean up sessions older than specified days"""
    import time
    
    cutoff_time = time.time() - (days * 24 * 60 * 60)
    deleted_count = 0
    
    for session_file in SESSIONS_DIR.glob("*.json"):
        try:
            if session_file.stat().st_mtime < cutoff_time:
                session_file.unlink()
                deleted_count += 1
        except:
            continue
    
    return deleted_count


def create_session(model: Optional[str] = None) -> Session:
    """Create a new session"""
    return Session(model=model)