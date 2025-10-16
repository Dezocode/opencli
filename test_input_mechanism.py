#!/usr/bin/env python3
"""
Test the input mechanism to see why messages aren't being sent
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_input_flow():
    """Test the actual input flow"""
    print("Testing input mechanism...")
    
    try:
        from cli.modules.initialization import initialize_opencli_system
        from cli.config import load_config
        from cli.session import Session
        
        # Initialize
        config_dir = Path.home() / '.opencli'
        component_init, system_init, results = initialize_opencli_system(config_dir)
        
        config = load_config()
        session = Session(model=config.get('model'))
        
        print(f"Components available: {list(k for k, v in results.items() if v)}")
        
        # Check prompt processor
        prompt_processor = component_init.get_component('prompt_processor')
        print(f"Prompt processor: {prompt_processor is not None}")
        
        # Test the setup_prompt_interface function
        from cli.main import setup_prompt_interface
        
        get_input = setup_prompt_interface(component_init, session, config)
        print(f"Input function created: {get_input}")
        
        # Check if it's using rich or simple
        if component_init.is_feature_available('RICH_PROMPT'):
            print("Using RICH prompt")
        else:
            print("Using SIMPLE prompt (fallback)")
            
        # Test getting input (non-interactive)
        print("\nWould normally wait for input here...")
        print("The input function is:", type(get_input))
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_input_flow()