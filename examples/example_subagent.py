#!/usr/bin/env python3
"""
Example Subagent for OpenCLI
Demonstrates how to connect to an OpenCLI instance and interact with it
"""

import asyncio
import sys
import os

# Add modules directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))

from ipc_shell_api import SubagentAPI, connect_to_opencli


async def simple_echo_agent(session_id: str):
    """
    Simple agent that echoes back messages prefixed with "Echo:"
    """
    print(f"Connecting to OpenCLI session: {session_id}")

    api = await connect_to_opencli(
        session_id=session_id,
        agent_name="EchoAgent",
        description="Echoes back messages"
    )

    print("Connected! Listening for messages...")

    # Register message callback
    def on_message(content: str):
        print(f"Received: {content}")

    api.on_receive(on_message)

    # Keep connection alive and echo messages
    try:
        while True:
            msg = await api.receive(timeout=1.0)
            if msg:
                echo_msg = f"Echo: {msg}"
                print(f"Sending: {echo_msg}")
                await api.send(echo_msg)

            # Send heartbeat every 10 iterations
            await asyncio.sleep(0.1)

    except KeyboardInterrupt:
        print("\nDisconnecting...")
        await api.disconnect()


async def assistant_agent(session_id: str):
    """
    Agent that acts as an AI assistant
    Responds to user messages with helpful replies
    """
    print(f"Connecting to OpenCLI session: {session_id}")

    async with SubagentAPI("AssistantAgent", "AI Assistant") as api:
        await api.connect(session_id)
        print("Connected as Assistant Agent!")

        # Get shell history to understand context
        history = await api.shell.get_shell_history()
        print(f"Loaded {len(history)} messages from history")

        # Listen and respond
        while True:
            msg = await api.receive(timeout=1.0)
            if msg and msg.strip():
                # Process user message
                response = await process_message(msg, history)
                await api.send(response)


async def process_message(message: str, history: list) -> str:
    """Simple message processing logic"""
    # This is a placeholder - in real use, you'd call an AI model here
    if "hello" in message.lower():
        return "Hello! How can I help you today?"
    elif "help" in message.lower():
        return "I'm a subagent connected to your OpenCLI instance. I can assist with various tasks!"
    else:
        return f"I received your message: '{message}'. I'm processing it..."


async def monitoring_agent(session_id: str):
    """
    Agent that monitors the shell and provides status updates
    """
    print(f"Connecting to OpenCLI session: {session_id}")

    api = await connect_to_opencli(
        session_id=session_id,
        agent_name="MonitorAgent",
        description="Monitors shell activity"
    )

    print("Connected as Monitor Agent!")

    try:
        while True:
            # Check status every 30 seconds
            await asyncio.sleep(30)

            status = await api.shell.get_shell_status()
            print(f"Shell Status: {status}")

            # Send status update to shell
            await api.send(f"[Monitor] Status check at {status.get('time', 'unknown')}")

    except KeyboardInterrupt:
        print("\nStopping monitor...")
        await api.disconnect()


async def streaming_agent(session_id: str):
    """
    Agent that demonstrates streaming output
    """
    print(f"Connecting to OpenCLI session: {session_id}")

    api = await connect_to_opencli(
        session_id=session_id,
        agent_name="StreamAgent",
        description="Demonstrates streaming"
    )

    print("Connected! Streaming example message...")

    # Stream a message word by word
    async def word_generator():
        message = "This is a streaming message being sent word by word."
        for word in message.split():
            yield word + " "
            await asyncio.sleep(0.2)

    await api.stream_output(word_generator())

    print("Streaming complete!")
    await api.disconnect()


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python example_subagent.py <session_id> [agent_type]")
        print("\nAgent types:")
        print("  echo       - Simple echo agent (default)")
        print("  assistant  - AI assistant agent")
        print("  monitor    - Monitoring agent")
        print("  stream     - Streaming demo agent")
        sys.exit(1)

    session_id = sys.argv[1]
    agent_type = sys.argv[2] if len(sys.argv) > 2 else "echo"

    # Select agent type
    agents = {
        "echo": simple_echo_agent,
        "assistant": assistant_agent,
        "monitor": monitoring_agent,
        "stream": streaming_agent
    }

    agent_func = agents.get(agent_type)
    if not agent_func:
        print(f"Unknown agent type: {agent_type}")
        print(f"Available types: {', '.join(agents.keys())}")
        sys.exit(1)

    # Run the agent
    try:
        asyncio.run(agent_func(session_id))
    except KeyboardInterrupt:
        print("\nShutting down...")


if __name__ == "__main__":
    main()
