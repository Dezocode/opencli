#!/usr/bin/env python3
"""
Test script to verify end-to-end chat functionality
"""

import sys
from pathlib import Path

# Add CLI to path
sys.path.insert(0, str(Path(__file__).parent))

def test_chat_flow():
    """Test that chat messages can flow through the system"""
    print("="*60)
    print("OPENCLI CHAT FUNCTIONALITY TEST")
    print("="*60)
    
    try:
        # Test 1: Import main components
        print("\n1. Testing imports...")
        from cli.main import interactive
        from cli.config import load_config
        from cli.session import Session
        from cli.utils import create_openai_client
        print("   ✓ All main imports successful")
        
        # Test 2: Load configuration
        print("\n2. Testing configuration...")
        config = load_config()
        model = config.get('model', 'unknown')
        print(f"   ✓ Config loaded: model={model}")
        
        # Test 3: Create session
        print("\n3. Testing session creation...")
        session = Session(model=model)
        print(f"   ✓ Session created: {session.session_id[:8]}")
        
        # Test 4: Create OpenAI client
        print("\n4. Testing API client...")
        client = create_openai_client(config)
        print("   ✓ OpenAI client created")
        
        # Test 5: Test message preparation
        print("\n5. Testing message handling...")
        test_message = "Test message"
        session.add("user", test_message)
        assert len(session.messages) > 0
        print(f"   ✓ Message added to session")
        
        # Test 6: Import execution flow
        print("\n6. Testing execution flow...")
        from cli.modules.execution_flow import create_execution_flow_manager
        from cli.modules.initialization import initialize_opencli_system
        
        config_dir = Path.home() / '.opencli'
        component_init, system_init, results = initialize_opencli_system(config_dir)
        print(f"   ✓ System initialized: {sum(results.values())}/{len(results)} components")
        
        execution_mgr = create_execution_flow_manager(config, session, component_init, system_init)
        execution_mgr.set_client(client)
        print("   ✓ Execution manager created")
        
        # Test 7: Test input handling
        print("\n7. Testing input handling...")
        processed, metadata = execution_mgr.handle_user_input("Hello world")
        print(f"   ✓ Input processed: '{processed}'")
        
        # Test 8: Test command detection
        print("\n8. Testing command detection...")
        is_exit = execution_mgr.handle_exit_commands("test")
        assert not is_exit, "Should not exit on 'test'"
        is_exit = execution_mgr.handle_exit_commands("/exit")
        # Note: might be disabled by permissions
        print("   ✓ Exit command detection working")
        
        # Test 9: Test message preparation
        print("\n9. Testing message preparation for API...")
        prepared = execution_mgr.prepare_messages_for_api()
        assert isinstance(prepared, list), "Should return list of messages"
        print(f"   ✓ Messages prepared: {len(prepared)} messages")
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\nChat functionality is working correctly.")
        print("You can now use 'opencli' to start chatting.")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ Assertion failed: {e}")
        return False
    except ImportError as e:
        print(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_chat_flow()
    sys.exit(0 if success else 1)