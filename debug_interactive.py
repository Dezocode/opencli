#!/usr/bin/env python3
"""
Debug the interactive mode to see where messages get stuck
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def debug_interactive():
    """Debug interactive mode"""
    from cli.config import load_config
    from cli.session import Session
    from cli.modules.initialization import initialize_opencli_system
    from cli.modules.execution_flow import create_execution_flow_manager, create_interactive_executor
    
    # Initialize
    config_dir = Path.home() / '.opencli'
    component_init, system_init, results = initialize_opencli_system(config_dir)
    
    config = load_config()
    session = Session(model=config.get('model'))
    
    # Create execution manager
    execution_manager = create_execution_flow_manager(config, session, component_init, system_init)
    
    # Create a mock client
    from unittest.mock import MagicMock
    mock_client = MagicMock()
    execution_manager.set_client(mock_client)
    
    # Simulate user input
    test_message = "Hello world"
    print(f"Simulating user message: '{test_message}'")
    
    # Process like the interactive loop does
    processed_input, input_metadata = execution_manager.handle_user_input(test_message)
    print(f"1. Processed input: '{processed_input}'")
    
    # Check exit commands
    is_exit = execution_manager.handle_exit_commands(test_message)
    print(f"2. Is exit command: {is_exit}")
    
    # Check slash commands
    is_command = execution_manager.handle_slash_commands(test_message)
    print(f"3. Is slash command: {is_command}")
    
    # Auto-select agent
    execution_manager.auto_select_agent(processed_input)
    print(f"4. Agent selected")
    
    # Add to session
    prompt_processor = execution_manager.initialized_systems.get('prompt_processor')
    actual_input = prompt_processor.get_original_text(processed_input, input_metadata) if prompt_processor else test_message
    session.add("user", actual_input)
    print(f"5. Added to session: {len(session.messages)} messages")
    print(f"   Message content: {session.messages[-1]}")
    
    # Create executor
    executor = create_interactive_executor(execution_manager)
    print(f"6. Executor created")
    
    # Now check what happens when we try to execute
    print("\n7. Attempting conversation turn...")
    
    # Mock the API call to see what's happening
    def mock_create(*args, **kwargs):
        print(f"   API called with model: {kwargs.get('model', 'unknown')}")
        print(f"   Messages: {len(kwargs.get('messages', []))} messages")
        # Simulate a simple response
        response = MagicMock()
        response.choices = [MagicMock()]
        response.choices[0].delta.content = "Hello! I can hear you."
        response.choices[0].delta.tool_calls = None
        return [response]  # Return as iterable for streaming
    
    mock_client.chat.completions.create = mock_create
    
    # Execute turn
    try:
        should_continue = executor.execute_conversation_turn()
        print(f"8. Turn executed: should_continue={should_continue}")
    except Exception as e:
        print(f"8. Error during turn: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n9. Final session state: {len(session.messages)} messages")
    for i, msg in enumerate(session.messages):
        print(f"   [{i}] {msg['role']}: {msg['content'][:50] if msg['content'] else '(empty)'}...")

if __name__ == "__main__":
    debug_interactive()