"""
Session management for async interactive mode
"""

import os
import json
import uuid
from datetime import datetime
from pathlib import Path


class Session:
    """Lightweight session object for async interactive mode"""
    
    def __init__(self, model=None):
        self.session_id = str(uuid.uuid4())
        self.messages = []
        self.model = model
        self.cwd = os.getcwd()
        self.current_agent = 'assistant'
        self.permission_manager = None
        self.debug_mode = False

    def add(self, role, content):
        """Add a message to the session"""
        self.messages.append({"role": role, "content": content})

    def get_messages(self):
        """Get all messages in the session"""
        return self.messages.copy()

    def save(self):
        """Save session to disk"""
        sessions_dir = Path.home() / '.opencli' / 'sessions'
        sessions_dir.mkdir(parents=True, exist_ok=True)
        
        session_data = {
            "session_id": self.session_id,
            "model": self.model,
            "messages": self.messages,
            "cwd": self.cwd,
            "debug_mode": getattr(self, 'debug_mode', False),
            "timestamp": datetime.now().isoformat()
        }
        
        with open(sessions_dir / f"{self.session_id}.json", 'w') as f:
            json.dump(session_data, f, indent=2)


def create_session(model=None):
    """Factory function to create a new session"""
    return Session(model=model)