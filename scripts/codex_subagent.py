#!/usr/bin/env python3
"""
Codex Subagent IPC Client
Connects to an OpenCLI IPC socket and mirrors Claude-style background comms.
"""

import argparse
import asyncio
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULES = ROOT / "modules"
for path in (MODULES, ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

try:
    from opencli_ipc import IPCClient, MessageType
except ImportError:
    sys.stderr.write("Could not import opencli_ipc. Run from the project root.\n")
    sys.exit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Attach to an OpenCLI IPC session as a subagent.")
    parser.add_argument("session", nargs="?", help="Session ID to attach to (e.g. 1234-...)")
    parser.add_argument("--socket", dest="socket_path", help="Explicit socket path (overrides session argument)")
    parser.add_argument("--name", default="Codex Subagent", help="Display name reported to OpenCLI")
    parser.add_argument("--description", default="Background Codex automation agent", help="Agent description")
    parser.add_argument("--metadata", help="Optional metadata key=value pairs (comma separated)")
    parser.add_argument("--heartbeat", type=int, default=30, help="Heartbeat interval in seconds")
    parser.add_argument("--role", default="assistant", choices=["assistant", "user"], help="Default role when sending messages")
    parser.add_argument("--quiet", action="store_true", help="Suppress incoming message echo")
    parser.add_argument("--no-stdin", action="store_true", help="Disable interactive stdin prompt")
    parser.add_argument("--duration", type=float, help="Auto-disconnect after N seconds (default: run until interrupted)")
    return parser.parse_args()


def parse_metadata(meta: str | None) -> dict:
    if not meta:
        return {}
    result = {}
    for pair in meta.split(","):
        if "=" not in pair:
            continue
        key, value = pair.split("=", 1)
        result[key.strip()] = value.strip()
    return result


def resolve_session(args: argparse.Namespace) -> tuple[str, str]:
    if args.socket_path:
        socket_path = Path(args.socket_path).expanduser()
        if not socket_path.exists():
            raise FileNotFoundError(f"Socket not found: {socket_path}")
        session_id = socket_path.stem.replace("opencli_", "")
        socket_dir = str(socket_path.parent)
        return session_id, socket_dir

    if not args.session:
        raise ValueError("Session ID or --socket must be provided")

    session_id = args.session.strip()
    socket_dir = os.environ.get("OPENCLI_SOCKET_DIR", "/tmp/opencli")
    return session_id, socket_dir


async def stdin_loop(client: IPCClient, role: str):
    loop = asyncio.get_running_loop()
    while client.connected:
        line = await loop.run_in_executor(None, sys.stdin.readline)
        if not line:
            break
        payload = line.strip()
        if not payload:
            continue
        if payload.startswith("/status "):
            await client.send_message(
                MessageType.STATUS.value,
                {"status": payload[len("/status "):], "timestamp": datetime.now().isoformat()}
            )
            continue
        if payload == "/id":
            print(f"agent_id={client.agent_id}")
            continue
        await client.send_message(
            MessageType.MESSAGE.value,
            {"role": role, "content": payload}
        )


async def heartbeat_loop(client: IPCClient, interval: int):
    try:
        while client.connected:
            await asyncio.sleep(interval)
            if client.connected:
                await client.send_heartbeat()
    except asyncio.CancelledError:
        pass


async def run_client():
    args = parse_args()
    session_id, socket_dir = resolve_session(args)

    metadata = parse_metadata(args.metadata)
    metadata.setdefault("agent_uuid", str(uuid.uuid4()))

    client = IPCClient(
        agent_name=args.name,
        description=args.description,
        metadata=metadata
    )

    # Hook message handlers
    async def echo(message):
        if not args.quiet:
            ts = datetime.fromtimestamp(message.timestamp).isoformat(timespec="seconds")
            origin = message.sender_id[:8]
            print(f"[{ts}] {message.msg_type} from {origin}: {message.payload}")

    client.register_handler(MessageType.MESSAGE.value, echo)
    client.register_handler(MessageType.COMMAND.value, echo)
    client.register_handler(MessageType.STATUS.value, echo)
    client.register_handler(MessageType.RESPONSE.value, echo)
    client.register_handler(MessageType.INJECTION.value, echo)

    # Connect using explicit socket directory if provided
    await client.connect(session_id=session_id, socket_dir=socket_dir)

    # Kick off heartbeat and optional stdin loops
    tasks = [asyncio.create_task(heartbeat_loop(client, max(5, args.heartbeat)))]
    if not args.no_stdin:
        tasks.append(asyncio.create_task(stdin_loop(client, args.role)))

    if args.duration and args.duration > 0:
        async def auto_disconnect():
            await asyncio.sleep(args.duration)
            if client.connected:
                print(f"Auto-disconnecting after {args.duration} seconds")
                await client.disconnect()

        tasks.append(asyncio.create_task(auto_disconnect()))

    print("Connected. Type messages to send (Ctrl+D to stop). Use /status <text> for status updates.")

    try:
        while client.connected:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        if client.connected:
            await client.disconnect()


def main():
    try:
        asyncio.run(run_client())
    except KeyboardInterrupt:
        print("\nInterrupted")
    except Exception as exc:
        sys.stderr.write(f"Error: {exc}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
