"""
Main entry point and interactive modes for OpenCLI
CLI argument parsing, interactive mode, TUI integration
"""

import sys
import shutil
from pathlib import Path

# CLI modules
from .config import load_config
from .session import Session
from .modules.argument_parser import handle_cli_arguments
from .modules.initialization import initialize_opencli_system
from .modules.execution_flow import create_execution_flow_manager, create_interactive_executor
from .modules.interactive_helpers import get_bottom_toolbar, ensure_prompt_at_bottom

# Configuration
CONFIG_DIR = Path.home() / ".opencli"


def interactive(config, session=None, initial=None):
    """Interactive CLI mode with fallback prompt interface"""
    # Initialize OpenCLI system
    component_init, system_init, init_results = initialize_opencli_system(CONFIG_DIR)
    
    # Create or use provided session
    if not session:
        session = Session(model=config["model"])
    
    # Create OpenAI client
    client = system_init.create_openai_client(config)
    
    # Create execution flow manager
    execution_manager = create_execution_flow_manager(config, session, component_init, system_init)
    execution_manager.set_client(client)
    
    # Display startup information
    system_init.display_startup_banner()
    system_init.display_system_info(session, config)
    system_init.display_cache_warning()
    
    # Setup rich prompt if available
    get_input = setup_prompt_interface(component_init, session, config)
    
    # Handle initial input
    user_input = initial if initial else get_input()
    
    # Main interaction loop
    while True:
        if not user_input:
            try:
                user_input = get_input()
                continue
            except (KeyboardInterrupt, EOFError):
                print()
                return
        
        # Process input for images and pasted text
        processed_input, input_metadata = execution_manager.handle_user_input(user_input)
        
        # Handle exit commands
        if execution_manager.handle_exit_commands(user_input):
            return
        
        # Handle slash commands
        if execution_manager.handle_slash_commands(user_input):
            user_input = get_input()
            continue
        
        # Auto-select agent based on triggers
        execution_manager.auto_select_agent(processed_input)
        
        # Store original input in session
        prompt_processor = execution_manager.initialized_systems.get('prompt_processor')
        actual_input = prompt_processor.get_original_text(processed_input, input_metadata) if prompt_processor else user_input
        session.add("user", actual_input)
        
        # Execute conversation turn
        interactive_executor = create_interactive_executor(execution_manager)
        should_continue = interactive_executor.execute_conversation_turn()
        
        if not should_continue:
            break
        
        # Save session
        execution_manager.save_session()
        
        # Ensure prompt area stays at bottom of screen
        if component_init.is_feature_available('RICH_PROMPT'):
            ensure_prompt_at_bottom()
        
        try:
            user_input = get_input()
        except (KeyboardInterrupt, EOFError):
            print()
            return


def setup_prompt_interface(component_init, session, config):
    """Setup prompt interface based on available features
    
    Args:
        component_init: Component initializer
        session: Current session
        config: Configuration dictionary
        
    Returns:
        Input function for getting user input
    """
    if component_init.is_feature_available('RICH_PROMPT'):
        rich_prompt = component_init.get_component('rich_prompt')
        PromptSession = rich_prompt['PromptSession']
        HTML = rich_prompt['HTML']
        FormattedText = rich_prompt['FormattedText']
        print_formatted_text = rich_prompt['print_formatted_text']
        
        # Create prompt style
        try:
            Style = rich_prompt['Style']
            prompt_style = Style.from_dict({
                'prompt': '#00aa00',
                'border': '#888888',
                'violet': '#aa88ff',
                'cyan': '#7aa2f7',
                'gray': '#666666',
                'bottom-toolbar': 'noinherit',
                'bottom-toolbar.text': 'noinherit',
            })
        except:
            prompt_style = None
        
        prompt_session = PromptSession(
            style=prompt_style,
            bottom_toolbar=lambda: get_bottom_toolbar(session, config),
            multiline=False
        )
        
        def get_rich_input():
            width = shutil.get_terminal_size().columns - 4
            print_formatted_text(FormattedText([('class:border', '┌' + '─' * width + '┐')]))
            raw_result = prompt_session.prompt(HTML('<prompt>│ &gt; </prompt>'))
            print_formatted_text(FormattedText([('class:border', '└' + '─' * width + '┘')]))
            print()  # Single blank line after prompt box
            
            # Process the input and show what was detected
            prompt_processor = component_init.get_component('prompt_processor')
            if prompt_processor and raw_result.strip():
                processed, metadata = prompt_processor.process_input(raw_result)
                if metadata.get('images') or metadata.get('videos') or metadata.get('pasted_texts'):
                    print(f"\033[2m{prompt_processor.format_display(processed, metadata)}\033[0m")
            
            return raw_result.strip()
        
        return get_rich_input
    else:
        return lambda: input("> ").strip()


def main():
    """Main entry point for OpenCLI"""
    # Handle command line arguments
    parsed_args, config, should_exit = handle_cli_arguments()
    
    if should_exit:
        return
    
    # Initialize system
    component_init, system_init, init_results = initialize_opencli_system(CONFIG_DIR)
    
    # Create session
    session = system_init.create_session(parsed_args, config)
    
    # Get prompt from arguments
    prompt = ' '.join(parsed_args.prompt) if parsed_args.prompt else None
    
    # Handle print mode
    if hasattr(parsed_args, 'print') and parsed_args.print:
        if not prompt:
            prompt = sys.stdin.read().strip()
        client = system_init.create_openai_client(config)
        r = client.chat.completions.create(
            model=config["model"], 
            messages=[{"role": "user", "content": prompt}]
        )
        print(r.choices[0].message.content)
    else:
        # Determine execution mode
        # Prefer async TUI by default; legacy fallback only if explicitly requested
        use_fallback = bool(getattr(parsed_args, 'fallback', False))
        
        try:
            if use_fallback:
                # Fallback mode (old interactive)
                interactive(config, session, prompt)
            else:
                # TUI mode (async interactive with Textual)
                async_tui = component_init.get_component('async_tui')
                run_interactive_async = async_tui['run_interactive_async']
                run_interactive_async(config, session, prompt)
        finally:
            # Cleanup: Unregister session on exit
            if component_init.is_feature_available('API_SERVER') and session:
                try:
                    api_components = component_init.get_component('api_server')
                    SessionRegistry = api_components['SessionRegistry']
                    registry = SessionRegistry(CONFIG_DIR)
                    registry.unregister_session(session.session_id)
                except:
                    pass


if __name__ == "__main__":
    main()