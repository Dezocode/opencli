"""
CLI Initialization System
Handles system initialization, configuration loading, and component setup for OpenCLI
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from ..config import load_config
from ..session import Session, SESSIONS_DIR
from ..utils import create_openai_client

# Configuration
CONFIG_DIR = Path.home() / ".opencli"


class ComponentInitializer:
    """Handles initialization of OpenCLI components with graceful fallbacks"""
    
    def __init__(self, config_dir: Path = None):
        """Initialize component manager
        
        Args:
            config_dir: Configuration directory path
        """
        self.config_dir = config_dir or CONFIG_DIR
        self.features = {}
        self.initialized_components = {}
    
    def initialize_async_tui(self) -> bool:
        """Initialize async TUI system with fallback detection

        Returns:
            True if TUI is available, False if fallback needed
        """
        try:
            # CRITICAL: Import from root-level modules, not cli/modules
            # sys.path has both ROOT_DIR and CLI_DIR, so we need absolute import
            import sys
            from pathlib import Path

            # Get root opencli directory (parent of cli/)
            root_dir = Path(__file__).parent.parent.parent
            if str(root_dir) not in sys.path:
                sys.path.insert(0, str(root_dir))

            from modules.async_interactive import interactive_async, run_interactive_async
            self.features['ASYNC_TUI'] = True
            self.initialized_components['async_tui'] = {
                'interactive_async': interactive_async,
                'run_interactive_async': run_interactive_async
            }
            return True
        except ImportError as e:
            self.features['ASYNC_TUI'] = False
            print(f"\033[2mTUI not available, using fallback mode: {e}\033[0m")
            return False
    
    def initialize_model_manager(self) -> bool:
        """Initialize model management system
        
        Returns:
            True if model manager is available
        """
        try:
            from modules.model_manager import ModelManager
            self.features['MODEL_MANAGER'] = True
            self.initialized_components['model_manager'] = ModelManager
            return True
        except ImportError:
            try:
                from model_manager import ModelManager
                self.features['MODEL_MANAGER'] = True
                self.initialized_components['model_manager'] = ModelManager
                return True
            except ImportError:
                self.features['MODEL_MANAGER'] = False
                return False
    
    def initialize_tool_system(self) -> bool:
        """Initialize tool call utilities
        
        Returns:
            True if tool system is available
        """
        try:
            from modules.tool_call_utils import normalize_tool_call_messages, extract_tool_calls_from_text
            self.features['TOOL_UTILS'] = True
            self.initialized_components['tool_utils'] = {
                'normalize_tool_call_messages': normalize_tool_call_messages,
                'extract_tool_calls_from_text': extract_tool_calls_from_text
            }
            return True
        except ImportError:
            self.features['TOOL_UTILS'] = False
            # Provide fallback implementations
            self.initialized_components['tool_utils'] = {
                'normalize_tool_call_messages': lambda x: x,
                'extract_tool_calls_from_text': lambda x: ([], x)
            }
            return False
    
    def initialize_uptime_checker(self) -> bool:
        """Initialize model uptime checking system
        
        Returns:
            True if uptime checker is available
        """
        try:
            from modules.uptime_checker import check_model_uptime, is_model_healthy, get_user_recommendation
            self.features['UPTIME_CHECKER'] = True
            self.initialized_components['uptime_checker'] = {
                'check_model_uptime': check_model_uptime,
                'is_model_healthy': is_model_healthy,
                'get_user_recommendation': get_user_recommendation
            }
            return True
        except ImportError:
            self.features['UPTIME_CHECKER'] = False
            # Provide None fallbacks
            self.initialized_components['uptime_checker'] = {
                'check_model_uptime': None,
                'is_model_healthy': None,
                'get_user_recommendation': None
            }
            return False
    
    def initialize_rich_prompt(self) -> bool:
        """Initialize rich prompt system
        
        Returns:
            True if rich prompt is available
        """
        try:
            from prompt_toolkit import PromptSession
            from prompt_toolkit.formatted_text import HTML, FormattedText
            from prompt_toolkit.styles import Style
            from prompt_toolkit import print_formatted_text
            self.features['RICH_PROMPT'] = True
            self.initialized_components['rich_prompt'] = {
                'PromptSession': PromptSession,
                'HTML': HTML,
                'FormattedText': FormattedText,
                'Style': Style,
                'print_formatted_text': print_formatted_text
            }
            return True
        except ImportError:
            self.features['RICH_PROMPT'] = False
            return False
    
    def initialize_agent_system(self) -> bool:
        """Initialize agent management system
        
        Returns:
            True if agent system is available
        """
        try:
            import yaml
            from agent_manager import AgentManager
            self.features['AGENT_SYSTEM'] = True
            self.initialized_components['agent_system'] = {
                'AgentManager': AgentManager,
                'yaml': yaml
            }
            return True
        except ImportError:
            self.features['AGENT_SYSTEM'] = False
            return False
    
    def initialize_command_registry(self) -> bool:
        """Initialize command registry system
        
        Returns:
            True if command registry is available
        """
        try:
            from command_registry import CommandRegistry
            self.features['COMMAND_REGISTRY'] = True
            self.initialized_components['command_registry'] = CommandRegistry
            return True
        except ImportError:
            self.features['COMMAND_REGISTRY'] = False
            return False
    
    def initialize_prompt_processor(self) -> bool:
        """Initialize prompt processing system
        
        Returns:
            True if prompt processor is available
        """
        try:
            from prompt_processor import PromptProcessor
            self.features['PROMPT_PROCESSOR'] = True
            self.initialized_components['prompt_processor'] = PromptProcessor
            return True
        except ImportError:
            self.features['PROMPT_PROCESSOR'] = False
            return False
    
    def initialize_tool_permissions(self) -> bool:
        """Initialize tool permission system
        
        Returns:
            True if tool permissions are available
        """
        try:
            from tool_permissions import ToolPermissionManager
            self.features['TOOL_PERMISSIONS'] = True
            self.initialized_components['tool_permissions'] = ToolPermissionManager
            return True
        except ImportError:
            self.features['TOOL_PERMISSIONS'] = False
            return False
    
    def initialize_api_server(self) -> bool:
        """Initialize API server system
        
        Returns:
            True if API server is available
        """
        try:
            from api_server import APIServer, SessionRegistry, MessageQueue
            self.features['API_SERVER'] = True
            self.initialized_components['api_server'] = {
                'APIServer': APIServer,
                'SessionRegistry': SessionRegistry,
                'MessageQueue': MessageQueue
            }
            return True
        except ImportError:
            self.features['API_SERVER'] = False
            return False
    
    def initialize_cache_manager(self) -> bool:
        """Initialize cache management system
        
        Returns:
            True if cache manager is available
        """
        try:
            from modules.cache_manager import get_cache_manager
            self.features['CACHE_MANAGER'] = True
            self.initialized_components['cache_manager'] = get_cache_manager
            return True
        except ImportError:
            self.features['CACHE_MANAGER'] = False
            return False
    
    def initialize_all_components(self) -> Dict[str, bool]:
        """Initialize all OpenCLI components
        
        Returns:
            Dictionary of component initialization status
        """
        results = {}
        
        # Initialize core components
        results['async_tui'] = self.initialize_async_tui()
        results['model_manager'] = self.initialize_model_manager()
        results['tool_system'] = self.initialize_tool_system()
        results['uptime_checker'] = self.initialize_uptime_checker()
        results['rich_prompt'] = self.initialize_rich_prompt()
        
        # Initialize feature components
        results['agent_system'] = self.initialize_agent_system()
        results['command_registry'] = self.initialize_command_registry()
        results['prompt_processor'] = self.initialize_prompt_processor()
        results['tool_permissions'] = self.initialize_tool_permissions()
        results['api_server'] = self.initialize_api_server()
        results['cache_manager'] = self.initialize_cache_manager()
        
        return results
    
    def get_component(self, component_name: str):
        """Get an initialized component
        
        Args:
            component_name: Name of component to retrieve
            
        Returns:
            Component instance or None if not available
        """
        return self.initialized_components.get(component_name)
    
    def is_feature_available(self, feature_name: str) -> bool:
        """Check if a feature is available
        
        Args:
            feature_name: Name of feature to check
            
        Returns:
            True if feature is available
        """
        return self.features.get(feature_name, False)


class SystemInitializer:
    """Handles OpenCLI system initialization and startup"""
    
    def __init__(self, config_dir: Path = None):
        """Initialize system manager
        
        Args:
            config_dir: Configuration directory path
        """
        self.config_dir = config_dir or CONFIG_DIR
        self.component_init = ComponentInitializer(config_dir)
        self.version_info = None
    
    def load_version_info(self) -> Dict[str, str]:
        """Load version information from metadata
        
        Returns:
            Dictionary with version information
        """
        if self.version_info:
            return self.version_info
            
        version_file = self.config_dir / "version.json"
        version_data = {
            'version': 'unknown',
            'build_date': 'unknown', 
            'commit_hash': 'unknown'
        }
        
        if version_file.exists():
            try:
                with open(version_file) as f:
                    loaded_data = json.load(f)
                    version_data.update(loaded_data)
            except Exception:
                pass
        
        self.version_info = version_data
        return version_data
    
    def check_stale_cache(self) -> Optional[Tuple[bool, int]]:
        """Check for stale Python cache files
        
        Returns:
            Tuple of (has_stale_cache, stale_count) or None if cache manager unavailable
        """
        if not self.component_init.is_feature_available('CACHE_MANAGER'):
            return None
            
        try:
            get_cache_manager = self.component_init.get_component('cache_manager')
            manager = get_cache_manager()
            stale = manager.find_all_stale_cache()
            
            if stale and len(stale) > 0:
                return True, len(stale)
            return False, 0
        except Exception:
            return None
    
    def create_session(self, args, config: Dict[str, Any]) -> Optional[Session]:
        """Create or load session based on arguments
        
        Args:
            args: Parsed command line arguments
            config: Configuration dictionary
            
        Returns:
            Session instance or None
        """
        session = None
        
        if hasattr(args, 'cont') and args.cont:
            session = Session.latest()
        elif hasattr(args, 'resume') and args.resume:
            session = Session.load(args.resume)
        
        # Create new session if none loaded
        if not session:
            model = getattr(args, 'model', None) or config.get("model")
            session = Session(model=model) if model else Session()
            
        return session
    
    def create_openai_client(self, config: Dict[str, Any]):
        """Create OpenAI client with configuration
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Configured OpenAI client
        """
        return create_openai_client(config)
    
    def display_startup_banner(self):
        """Display OpenCLI startup banner"""
        ascii_art = """
 ██████╗ ██████╗ ███████╗███╗   ██╗     ██████╗██╗     ██╗
██╔═══██╗██╔══██╗██╔════╝████╗  ██║    ██╔════╝██║     ██║
██║   ██║██████╔╝█████╗  ██╔██╗ ██║    ██║     ██║     ██║
██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║    ██║     ██║     ██║
╚██████╔╝██║     ███████╗██║ ╚████║    ╚██████╗███████╗██║
 ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝     ╚═════╝╚══════╝╚═╝
"""
        print(ascii_art)
    
    def display_system_info(self, session: Session, config: Dict[str, Any]):
        """Display system information and status
        
        Args:
            session: Current session
            config: Configuration dictionary
        """
        version_info = self.load_version_info()
        version_str = version_info['version']
        
        print(f"\033[2mOpenCLI - version {version_str}\033[0m")
        
        # Show agent info if available
        agent_info = ""
        if (self.component_init.is_feature_available('AGENT_SYSTEM') and 
            hasattr(session, 'current_agent')):
            agent_info = f" | Agent: {session.current_agent}"
        
        # Format model name
        from ..utils import format_model_name
        model_name = format_model_name(session.model or config['model'])
        
        print(f"\033[2mSession: {session.session_id[:8]} | Model: {model_name}{agent_info}\033[0m\n")
    
    def display_cache_warning(self):
        """Display cache warning if stale cache detected"""
        cache_status = self.check_stale_cache()
        if cache_status and cache_status[0]:  # has_stale_cache is True
            stale_count = cache_status[1]
            print(f"\n⚠️  WARNING: Found {stale_count} modules with stale bytecode cache")
            print("   Your .pyc files are older than source files.")
            print("   This can cause 'Unknown command' errors or outdated behavior.\n")
            print("   Recommended: Type '/reload' in the CLI to fix this")
            print("   Or run: find ~/opencli -name '*.pyc' -delete\n")


def create_component_initializer(config_dir: Path = None) -> ComponentInitializer:
    """Factory function to create component initializer
    
    Args:
        config_dir: Configuration directory path
        
    Returns:
        ComponentInitializer instance
    """
    return ComponentInitializer(config_dir)


def create_system_initializer(config_dir: Path = None) -> SystemInitializer:
    """Factory function to create system initializer
    
    Args:
        config_dir: Configuration directory path
        
    Returns:
        SystemInitializer instance
    """
    return SystemInitializer(config_dir)


def initialize_opencli_system(config_dir: Path = None) -> Tuple[ComponentInitializer, SystemInitializer, Dict[str, bool]]:
    """Complete OpenCLI system initialization
    
    Args:
        config_dir: Configuration directory path
        
    Returns:
        Tuple of (component_initializer, system_initializer, initialization_results)
    """
    system_init = create_system_initializer(config_dir)
    component_init = system_init.component_init
    
    # Initialize all components
    results = component_init.initialize_all_components()
    
    return component_init, system_init, results