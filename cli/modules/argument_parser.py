"""
CLI Argument Parsing Module
Handles command-line argument parsing and validation for OpenCLI
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from ..config import load_config, setup_api_key


class OpenCLIArgumentParser:
    """Enhanced argument parser for OpenCLI with validation and help"""
    
    def __init__(self):
        """Initialize the argument parser with OpenCLI-specific arguments"""
        self.parser = argparse.ArgumentParser(add_help=False)
        self._setup_arguments()
    
    def _setup_arguments(self):
        """Setup all command-line arguments"""
        # Main arguments
        self.parser.add_argument('prompt', nargs='*', help='Initial prompt for OpenCLI')
        
        # Mode arguments
        self.parser.add_argument('-p', '--print', action='store_true', 
                               help='Print response and exit (non-interactive mode)')
        self.parser.add_argument('-c', '--continue', dest='cont', action='store_true',
                               help='Continue the most recent session')
        self.parser.add_argument('-r', '--resume', metavar='SESSION_ID',
                               help='Resume a specific session by ID')
        
        # Configuration arguments
        self.parser.add_argument('--model', metavar='MODEL_NAME',
                               help='Set the model to use for this session')
        self.parser.add_argument('--setup', action='store_true', 
                               help='Setup API key interactively')
        
        # System arguments
        self.parser.add_argument('--rollback', action='store_true', 
                               help='Emergency rollback to previous version')
        self.parser.add_argument('--fallback', action='store_true', 
                               help='Use fallback mode (disable TUI/async features)')
        
        # Help and information
        self.parser.add_argument('-h', '--help', action='store_true',
                               help='Show this help message and exit')
        self.parser.add_argument('--version', action='store_true',
                               help='Show version information and exit')
        
        # Debug and development arguments  
        self.parser.add_argument('--debug', action='store_true',
                               help='Enable debug mode with verbose output')
        self.parser.add_argument('--profile', action='store_true',
                               help='Enable performance profiling')
        
        # Advanced configuration
        self.parser.add_argument('--config-dir', metavar='PATH',
                               help='Override default configuration directory')
        self.parser.add_argument('--no-cache', action='store_true',
                               help='Disable caching for this session')
    
    def parse_args(self, args=None) -> argparse.Namespace:
        """Parse command-line arguments with validation"""
        parsed_args = self.parser.parse_args(args)
        
        # Validate argument combinations
        self._validate_arguments(parsed_args)
        
        return parsed_args
    
    def _validate_arguments(self, args: argparse.Namespace):
        """Validate argument combinations and values"""
        # Check for conflicting session arguments
        session_args = [args.cont, args.resume]
        if sum(bool(arg) for arg in session_args) > 1:
            self.parser.error("Cannot use --continue and --resume together")
        
        # Validate resume session ID format if provided
        if args.resume and not self._is_valid_session_id(args.resume):
            self.parser.error(f"Invalid session ID format: {args.resume}")
        
        # Check config directory if provided
        if args.config_dir:
            config_path = Path(args.config_dir)
            if not config_path.exists():
                self.parser.error(f"Configuration directory does not exist: {config_path}")
    
    def _is_valid_session_id(self, session_id: str) -> bool:
        """Validate session ID format"""
        # Basic validation - session IDs should be alphanumeric with some special chars
        if not session_id:
            return False
        return len(session_id) >= 6 and session_id.replace('-', '').replace('_', '').isalnum()
    
    def handle_special_commands(self, args: argparse.Namespace) -> bool:
        """Handle special commands that exit immediately. Returns True if command was handled."""
        
        # Emergency rollback
        if args.rollback:
            return self._handle_rollback()
        
        # Setup API key
        if args.setup:
            setup_api_key()
            return True
        
        # Show help
        if args.help:
            self._show_help()
            return True
        
        # Show version
        if args.version:
            self._show_version()
            return True
        
        return False
    
    def _handle_rollback(self) -> bool:
        """Handle emergency rollback command"""
        emergency_rollback_script = Path.home() / "opencli" / "emergency-rollback.sh"
        if emergency_rollback_script.exists():
            try:
                subprocess.run(['bash', str(emergency_rollback_script)], check=True)
                print("✅ Emergency rollback completed successfully")
            except subprocess.CalledProcessError as e:
                print(f"❌ Emergency rollback failed: {e}")
        else:
            print("❌ Emergency rollback script not found")
            print(f"Expected at: {emergency_rollback_script}")
            print("\nTo create an emergency rollback script:")
            print("1. Create the directory: mkdir -p ~/opencli")
            print("2. Create emergency-rollback.sh with your rollback commands")
        return True
    
    def _show_help(self):
        """Display comprehensive help information"""
        print("OpenCLI - OpenRouter CLI with Claude Code capabilities\n")
        print("Usage: opencli [options] [prompt]\n")
        
        print("Basic Options:")
        print("  -p, --print           Print response and exit (non-interactive)")
        print("  -c, --continue        Continue the most recent session")
        print("  -r, --resume ID       Resume a specific session by ID")
        print("  --model NAME          Set the model to use")
        print("  -h, --help            Show this help message")
        print("  --version             Show version information")
        print()
        
        print("Setup and Configuration:")
        print("  --setup               Setup API key interactively")
        print("  --config-dir PATH     Override default configuration directory")
        print("  --no-cache            Disable caching for this session")
        print()
        
        print("Advanced Options:")
        print("  --fallback            Use fallback mode (disable TUI)")
        print("  --debug               Enable debug mode")
        print("  --profile             Enable performance profiling")
        print("  --rollback            Emergency rollback (use if CLI is broken)")
        print()
        
        print("Examples:")
        print("  opencli                           # Start interactive mode")
        print("  opencli \"Hello, world!\"           # Quick prompt")
        print("  opencli -p \"What is Python?\"      # Print mode")
        print("  opencli -c                        # Continue last session")
        print("  opencli -r abc123                 # Resume specific session")
        print("  opencli --model gpt-4             # Use specific model")
        print()
        
        print("For more information, visit: https://github.com/your-repo/opencli")
    
    def _show_version(self):
        """Display version information"""
        # Try to load version from metadata
        config_dir = Path.home() / ".opencli"
        version_file = config_dir / "version.json"
        
        version_str = "unknown"
        if version_file.exists():
            try:
                import json
                with open(version_file) as f:
                    version_data = json.load(f)
                    version_str = version_data.get('version', 'unknown')
                    build_date = version_data.get('build_date', 'unknown')
                    commit_hash = version_data.get('commit_hash', 'unknown')
                    
                print(f"OpenCLI version {version_str}")
                print(f"Build date: {build_date}")
                print(f"Commit: {commit_hash}")
            except Exception:
                print(f"OpenCLI version {version_str}")
        else:
            print(f"OpenCLI version {version_str}")
        
        # Show Python version and platform info
        import platform
        print(f"Python {sys.version}")
        print(f"Platform: {platform.system()} {platform.release()}")
    
    def apply_config_overrides(self, args: argparse.Namespace, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply command-line argument overrides to configuration"""
        config = config.copy()  # Don't modify original
        
        # Apply model override
        if args.model:
            config["model"] = args.model
            print(f"Using model: {args.model}")
        
        # Apply debug mode
        if args.debug:
            config["debug"] = True
            print("Debug mode enabled")
        
        # Apply no-cache option
        if args.no_cache:
            config["use_cache"] = False
            print("Caching disabled for this session")
        
        # Apply fallback mode
        if args.fallback:
            config["fallback_mode"] = True
            print("Fallback mode enabled (TUI disabled)")
        
        # Apply profiling
        if args.profile:
            config["enable_profiling"] = True
            print("Performance profiling enabled")
        
        return config
    
    def get_execution_mode(self, args: argparse.Namespace) -> str:
        """Determine the execution mode based on arguments"""
        if args.print:
            return "print"
        elif args.cont or args.resume:
            return "resume"
        else:
            return "interactive"
    
    def should_use_fallback(self, args: argparse.Namespace) -> bool:
        """Determine if fallback mode should be used"""
        return args.fallback or args.debug


def create_argument_parser() -> OpenCLIArgumentParser:
    """Factory function to create a configured argument parser"""
    return OpenCLIArgumentParser()


def parse_cli_arguments(args=None) -> argparse.Namespace:
    """Convenience function to parse CLI arguments"""
    parser = create_argument_parser()
    return parser.parse_args(args)


def handle_cli_arguments(args=None) -> tuple[argparse.Namespace, Dict[str, Any], bool]:
    """
    Complete argument handling pipeline.
    
    Returns:
        tuple: (parsed_args, config, should_exit)
    """
    parser = create_argument_parser()
    parsed_args = parser.parse_args(args)
    
    # Handle special commands that exit immediately
    if parser.handle_special_commands(parsed_args):
        return parsed_args, {}, True
    
    # Load and apply configuration
    config = load_config()
    config = parser.apply_config_overrides(parsed_args, config)
    
    return parsed_args, config, False