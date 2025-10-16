#!/usr/bin/env python3
"""
Test actual user input flow in OpenCLI
"""

import sys
import os
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

def test_user_message_flow():
    """Test what happens when a user enters a message"""
    print("Testing user message flow...")
    
    try:
        # Import components
        from cli.config import load_config
        from cli.session import Session
        from cli.utils import create_openai_client
        from cli.modules.initialization import initialize_opencli_system
        from cli.modules.execution_flow import create_execution_flow_manager, create_interactive_executor
        
        # Load config
        config = load_config()
        print(f"Config loaded: {config.get('model')}")
        
        # Create session
        session = Session(model=config.get('model'))
        session.messages = []  # Start fresh
        print(f"Session: {session.session_id[:8]}")
        
        # Initialize system
        config_dir = Path.home() / '.opencli'
        component_init, system_init, results = initialize_opencli_system(config_dir)
        print(f"Components: {sum(results.values())}/{len(results)}")
        
        # Create execution manager
        execution_mgr = create_execution_flow_manager(config, session, component_init, system_init)
        
        # Create and set client
        client = create_openai_client(config)
        execution_mgr.set_client(client)
        print("Client set")
        
        # Simulate user input
        user_message = "Hello, can you hear me?"
        print(f"\nSimulating user message: '{user_message}'")
        
        # Process input
        processed_input, input_metadata = execution_mgr.handle_user_input(user_message)
        print(f"Processed: '{processed_input}'")
        
        # Add to session
        session.add("user", user_message)
        print(f"Session messages: {len(session.messages)}")
        
        # Create executor
        executor = create_interactive_executor(execution_mgr)
        
        # Try to execute a turn
        print("\nAttempting to execute conversation turn...")
        
        # Prepare messages
        prepared = execution_mgr.prepare_messages_for_api()
        print(f"Prepared {len(prepared)} messages for API")
        
        # Try to create stream
        print("\nCreating API stream...")
        stream = execution_mgr.create_api_stream(prepared)
        print(f"Stream created: {stream is not None}")
        
        # Process response
        if stream:
            print("\nProcessing stream...")
            streaming_processor = execution_mgr.get_streaming_processor()
            full_content, tool_calls = streaming_processor.process_stream_response(stream)
            print(f"Response: {full_content[:100] if full_content else 'No response'}")
            
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_user_message_flow()
    sys.exit(0 if success else 1)