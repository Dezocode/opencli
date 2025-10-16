"""
OpenCLI API Server
Provides HTTP/WebSocket API for inter-CLI communication and external integrations
Enables session discovery, cross-session messaging, and tool invocation
"""

import json
import asyncio
import os
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, parse_qs
import threading
import time

class APIServerConfig:
    """Configuration for API server"""
    def __init__(self, config_dir=None):
        self.config_dir = config_dir or Path.home() / ".opencli"
        self.api_config_file = self.config_dir / "api_server.json"
        self.sessions_dir = self.config_dir / "sessions"
        self.ipc_dir = self.config_dir / "ipc"

        # Create IPC directory
        self.ipc_dir.mkdir(exist_ok=True)

        # Load or create config
        self.config = self._load_config()

    def _load_config(self):
        """Load API server configuration"""
        if self.api_config_file.exists():
            try:
                with open(self.api_config_file) as f:
                    return json.load(f)
            except:
                pass

        # Default configuration
        return {
            "enabled": False,
            "host": "127.0.0.1",
            "port": 7890,
            "allow_remote": False,
            "require_auth": False,
            "api_key": None
        }

    def save_config(self):
        """Save API server configuration"""
        with open(self.api_config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

class SessionRegistry:
    """Registry of active OpenCLI sessions"""
    def __init__(self, config_dir=None):
        self.config_dir = config_dir or Path.home() / ".opencli"
        self.ipc_dir = self.config_dir / "ipc"
        self.sessions_dir = self.config_dir / "sessions"

    def register_session(self, session_id, pid, model, agent, cwd):
        """Register an active session"""
        session_file = self.ipc_dir / f"session_{session_id}.json"
        session_data = {
            "session_id": session_id,
            "pid": pid,
            "model": model,
            "agent": agent,
            "cwd": cwd,
            "registered_at": time.time(),
            "last_heartbeat": time.time()
        }

        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)

    def unregister_session(self, session_id):
        """Unregister a session"""
        session_file = self.ipc_dir / f"session_{session_id}.json"
        if session_file.exists():
            session_file.unlink()

    def heartbeat(self, session_id):
        """Update session heartbeat"""
        session_file = self.ipc_dir / f"session_{session_id}.json"
        if session_file.exists():
            try:
                with open(session_file) as f:
                    data = json.load(f)
                data['last_heartbeat'] = time.time()
                with open(session_file, 'w') as f:
                    json.dump(data, f, indent=2)
            except:
                pass

    def list_active_sessions(self, timeout=300):
        """List all active sessions (within timeout)"""
        sessions = []
        current_time = time.time()

        for session_file in self.ipc_dir.glob("session_*.json"):
            try:
                with open(session_file) as f:
                    data = json.load(f)

                # Check if session is still active (heartbeat within timeout)
                if current_time - data.get('last_heartbeat', 0) < timeout:
                    sessions.append(data)
                else:
                    # Clean up stale session
                    session_file.unlink()
            except:
                pass

        return sessions

    def get_session(self, session_id):
        """Get specific session info"""
        session_file = self.ipc_dir / f"session_{session_id}.json"
        if session_file.exists():
            try:
                with open(session_file) as f:
                    return json.load(f)
            except:
                pass
        return None

class MessageQueue:
    """Inter-session message queue"""
    def __init__(self, config_dir=None):
        self.config_dir = config_dir or Path.home() / ".opencli"
        self.ipc_dir = self.config_dir / "ipc"
        self.queue_dir = self.ipc_dir / "messages"
        self.queue_dir.mkdir(exist_ok=True)

    def send_message(self, to_session, from_session, message_type, payload):
        """Send message to another session"""
        message_id = f"{int(time.time() * 1000)}_{from_session[:8]}"
        message_file = self.queue_dir / f"{to_session}_{message_id}.json"

        message_data = {
            "id": message_id,
            "to": to_session,
            "from": from_session,
            "type": message_type,
            "payload": payload,
            "timestamp": time.time()
        }

        with open(message_file, 'w') as f:
            json.dump(message_data, f, indent=2)

        return message_id

    def get_messages(self, session_id, delete=True):
        """Get messages for a session"""
        messages = []

        for msg_file in sorted(self.queue_dir.glob(f"{session_id}_*.json")):
            try:
                with open(msg_file) as f:
                    messages.append(json.load(f))

                if delete:
                    msg_file.unlink()
            except:
                pass

        return messages

class OpenCLIAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OpenCLI API"""

    def _set_headers(self, status=200, content_type='application/json'):
        """Set HTTP response headers"""
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def _send_json(self, data, status=200):
        """Send JSON response"""
        self._set_headers(status)
        self.wfile.write(json.dumps(data, indent=2).encode())

    def do_GET(self):
        """Handle GET requests"""
        parsed = urlparse(self.path)
        path = parsed.path

        # Initialize registry and queue
        registry = SessionRegistry()
        queue = MessageQueue()

        if path == '/api/sessions':
            # List active sessions
            sessions = registry.list_active_sessions()
            self._send_json({"sessions": sessions})

        elif path.startswith('/api/session/'):
            # Get specific session
            session_id = path.split('/')[-1]
            session = registry.get_session(session_id)

            if session:
                self._send_json({"session": session})
            else:
                self._send_json({"error": "Session not found"}, 404)

        elif path.startswith('/api/messages/'):
            # Get messages for session
            session_id = path.split('/')[-1]
            messages = queue.get_messages(session_id)
            self._send_json({"messages": messages})

        elif path == '/api/status':
            # Server status
            self._send_json({
                "status": "running",
                "version": "1.2.3",
                "active_sessions": len(registry.list_active_sessions())
            })

        else:
            self._send_json({"error": "Endpoint not found"}, 404)

    def do_POST(self):
        """Handle POST requests"""
        parsed = urlparse(self.path)
        path = parsed.path

        # Read POST data
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        try:
            data = json.loads(post_data.decode())
        except:
            self._send_json({"error": "Invalid JSON"}, 400)
            return

        # Initialize registry and queue
        registry = SessionRegistry()
        queue = MessageQueue()

        if path == '/api/session/register':
            # Register new session
            registry.register_session(
                data['session_id'],
                data.get('pid', os.getpid()),
                data.get('model'),
                data.get('agent'),
                data.get('cwd')
            )
            self._send_json({"status": "registered"})

        elif path == '/api/session/heartbeat':
            # Session heartbeat
            registry.heartbeat(data['session_id'])
            self._send_json({"status": "ok"})

        elif path == '/api/message/send':
            # Send message to session
            message_id = queue.send_message(
                data['to'],
                data['from'],
                data['type'],
                data['payload']
            )
            self._send_json({"status": "sent", "message_id": message_id})

        else:
            self._send_json({"error": "Endpoint not found"}, 404)

    def log_message(self, format, *args):
        """Suppress request logging"""
        pass

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Threaded HTTP server"""
    daemon_threads = True

class APIServer:
    """OpenCLI API Server"""
    def __init__(self, config_dir=None):
        self.config = APIServerConfig(config_dir)
        self.server = None
        self.thread = None
        self.running = False

    def start(self):
        """Start API server in background thread"""
        if self.running:
            return

        host = self.config.config['host']
        port = self.config.config['port']

        try:
            self.server = ThreadedHTTPServer((host, port), OpenCLIAPIHandler)
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            self.running = True
            return True
        except Exception as e:
            print(f"Failed to start API server: {e}")
            return False

    def stop(self):
        """Stop API server"""
        if self.server:
            self.server.shutdown()
            self.running = False

    def is_running(self):
        """Check if server is running"""
        return self.running and self.thread and self.thread.is_alive()
