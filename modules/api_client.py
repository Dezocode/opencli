"""
OpenCLI API Client
Client library for communicating with OpenCLI API server
Enables external tools and other CLIs to interact with OpenCLI sessions
"""

import json
import requests
from pathlib import Path

class OpenCLIClient:
    """Client for OpenCLI API"""

    def __init__(self, host="127.0.0.1", port=7890):
        self.base_url = f"http://{host}:{port}"

    def get_status(self):
        """Get API server status"""
        try:
            response = requests.get(f"{self.base_url}/api/status")
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def list_sessions(self):
        """List all active OpenCLI sessions"""
        try:
            response = requests.get(f"{self.base_url}/api/sessions")
            return response.json().get('sessions', [])
        except Exception as e:
            return []

    def get_session(self, session_id):
        """Get specific session information"""
        try:
            response = requests.get(f"{self.base_url}/api/session/{session_id}")
            return response.json().get('session')
        except Exception as e:
            return None

    def register_session(self, session_id, pid, model, agent, cwd):
        """Register a new session"""
        try:
            response = requests.post(f"{self.base_url}/api/session/register", json={
                "session_id": session_id,
                "pid": pid,
                "model": model,
                "agent": agent,
                "cwd": cwd
            })
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def heartbeat(self, session_id):
        """Send session heartbeat"""
        try:
            response = requests.post(f"{self.base_url}/api/session/heartbeat", json={
                "session_id": session_id
            })
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def send_message(self, to_session, from_session, message_type, payload):
        """Send message to another session"""
        try:
            response = requests.post(f"{self.base_url}/api/message/send", json={
                "to": to_session,
                "from": from_session,
                "type": message_type,
                "payload": payload
            })
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def get_messages(self, session_id):
        """Get messages for a session"""
        try:
            response = requests.get(f"{self.base_url}/api/messages/{session_id}")
            return response.json().get('messages', [])
        except Exception as e:
            return []

def main():
    """CLI interface for API client"""
    import sys

    if len(sys.argv) < 2:
        print("OpenCLI API Client")
        print("\nUsage:")
        print("  python -m api_client status")
        print("  python -m api_client sessions")
        print("  python -m api_client session <session_id>")
        print("  python -m api_client messages <session_id>")
        print("  python -m api_client send <to_session> <from_session> <type> <payload>")
        return

    client = OpenCLIClient()
    command = sys.argv[1]

    if command == "status":
        print(json.dumps(client.get_status(), indent=2))

    elif command == "sessions":
        sessions = client.list_sessions()
        print(f"Active sessions: {len(sessions)}\n")
        for session in sessions:
            print(f"Session: {session['session_id'][:8]}")
            print(f"  Model: {session.get('model')}")
            print(f"  Agent: {session.get('agent')}")
            print(f"  PID: {session.get('pid')}")
            print(f"  CWD: {session.get('cwd')}")
            print()

    elif command == "session" and len(sys.argv) > 2:
        session_id = sys.argv[2]
        session = client.get_session(session_id)
        if session:
            print(json.dumps(session, indent=2))
        else:
            print(f"Session {session_id} not found")

    elif command == "messages" and len(sys.argv) > 2:
        session_id = sys.argv[2]
        messages = client.get_messages(session_id)
        print(f"Messages for session {session_id[:8]}: {len(messages)}\n")
        for msg in messages:
            print(f"From: {msg['from'][:8]} | Type: {msg['type']}")
            print(f"Payload: {msg['payload']}")
            print()

    elif command == "send" and len(sys.argv) > 5:
        to_session = sys.argv[2]
        from_session = sys.argv[3]
        msg_type = sys.argv[4]
        payload = sys.argv[5]

        result = client.send_message(to_session, from_session, msg_type, payload)
        print(json.dumps(result, indent=2))

    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
