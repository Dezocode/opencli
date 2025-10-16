# Code Dictionary

Comprehensive per-file mapping of functions to their cross-file communications and purposes.

## advanced_profiler.py

- Module: `advanced_profiler`

- Function `AdvancedProfiler.__init__` (line 72)

  - Purpose: Args:

  - Signature summary: positional=self, sample_interval, duration

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `collections.defaultdict` at line 82 (unresolved)

      - Purpose: No docstring provided

      - Expression: `defaultdict`

- Function `AdvancedProfiler._categorize_thread` (line 86)

  - Purpose: Categorize thread by role

  - Signature summary: positional=self, thread_name

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `AdvancedProfiler.analyze` (line 198)

  - Purpose: Analyze captured data

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `collections.defaultdict` at line 207 (unresolved)

      - Purpose: No docstring provided

      - Expression: `defaultdict`

    - Calls `collections.Counter` at line 243 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Counter`

- Function `AdvancedProfiler.capture_sample` (line 100)

  - Purpose: Capture a single sample of all thread states

  - Signature summary: positional=self

  - Async: False, Returns: Dict

  - Cross-file communications:

    - Calls `time.time` at line 102 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

    - Calls `datetime.datetime.now` at line 105 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

    - Calls `sys._current_frames` at line 110 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys._current_frames`

    - Calls `threading.enumerate` at line 114 (unresolved)

      - Purpose: No docstring provided

      - Expression: `threading.enumerate`

    - Calls `traceback.extract_stack` at line 123 (unresolved)

      - Purpose: No docstring provided

      - Expression: `traceback.extract_stack`

- Function `AdvancedProfiler.generate_pdf_timeline` (line 247)

  - Purpose: Generate PDF timeline graph showing function activity hierarchy

  - Signature summary: positional=self, output_path

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `collections.defaultdict` at line 258 (unresolved)

      - Purpose: No docstring provided

      - Expression: `defaultdict`

    - Calls `matplotlib.pyplot.subplots` at line 266 (unresolved)

      - Purpose: No docstring provided

      - Expression: `plt.subplots`

    - Calls `matplotlib.patches.Rectangle` at line 287 (unresolved)

      - Purpose: No docstring provided

      - Expression: `mpatches.Rectangle`

    - Calls `matplotlib.patches.Patch` at line 331 (unresolved)

      - Purpose: No docstring provided

      - Expression: `mpatches.Patch`

    - Calls `matplotlib.pyplot.tight_layout` at line 336 (unresolved)

      - Purpose: No docstring provided

      - Expression: `plt.tight_layout`

    - Calls `matplotlib.backends.backend_pdf.PdfPages` at line 337 (unresolved)

      - Purpose: No docstring provided

      - Expression: `PdfPages`

    - Calls `matplotlib.pyplot.close` at line 339 (unresolved)

      - Purpose: No docstring provided

      - Expression: `plt.close`

- Function `AdvancedProfiler.profile` (line 166)

  - Purpose: Run profiling for specified duration with interval sampling

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `time.time` at line 188 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

    - Calls `time.sleep` at line 193 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.sleep`

- Function `AdvancedProfiler.save_raw_data` (line 344)

  - Purpose: Save raw profiling data as JSON for further analysis

  - Signature summary: positional=self, output_path

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.dump` at line 358 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dump`

- Function `main` (line 363)

  - Purpose: Main entry point

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `argparse.ArgumentParser` at line 367 (unresolved)

      - Purpose: No docstring provided

      - Expression: `argparse.ArgumentParser`


## agent_manager.py

- Module: `agent_manager`

- Function `AgentConfig.__init__` (line 17)

  - Purpose: No docstring provided

  - Signature summary: positional=self, name, config

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `AgentConfig.build_system_message` (line 36)

  - Purpose: Build complete system prompt with project context

  - Signature summary: positional=self, project_context

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `AgentConfig.matches_trigger` (line 28)

  - Purpose: Check if user input matches any triggers

  - Signature summary: positional=self, user_input

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `AgentManager.__init__` (line 124)

  - Purpose: No docstring provided

  - Signature summary: positional=self, config_dir

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `AgentManager.find_agents_md` (line 149)

  - Purpose: Find and read AGENTS.md file (closest to working dir)

  - Signature summary: positional=self, working_dir

  - Async: False, Returns: Optional[str]

  - Cross-file communications:

    - Calls `pathlib.Path` at line 163 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

- Function `AgentManager.get_agent_tools` (line 233)

  - Purpose: Get tools for specific agent (merge with base tools)

  - Signature summary: positional=self, agent_name, base_tools

  - Async: False, Returns: List[Dict]

  - Cross-file communications: none

- Function `AgentManager.list_agents` (line 243)

  - Purpose: List all available agents

  - Signature summary: positional=self

  - Async: False, Returns: List[Tuple[str, str]]

  - Cross-file communications: none

- Function `AgentManager.load_agents` (line 131)

  - Purpose: Load agent configurations from YAML files

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `yaml.safe_load` at line 137 (unresolved)

      - Purpose: No docstring provided

      - Expression: `yaml.safe_load`

- Function `AgentManager.prepare_messages` (line 191)

  - Purpose: Prepare optimized messages for agent with context management

  - Signature summary: positional=self, agent_name, messages, working_dir

  - Async: False, Returns: List[Dict]

  - Cross-file communications:

    - Calls `os.getcwd` at line 204 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.getcwd`

- Function `AgentManager.select_agent` (line 169)

  - Purpose: Select appropriate agent based on user input

  - Signature summary: positional=self, user_input, current_agent

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `ContextManager.compress_context` (line 68)

  - Purpose: Compress context using various strategies:

  - Signature summary: positional=messages, max_tokens, strategy

  - Async: False, Returns: List[Dict]

  - Cross-file communications: none

- Function `ContextManager.count_tokens` (line 63)

  - Purpose: Estimate token count (4 chars per token)

  - Signature summary: positional=messages

  - Async: False, Returns: int

  - Cross-file communications:

    - Calls `json.dumps` at line 65 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dumps`

- Function `ContextManager.optimize_tool_results` (line 100)

  - Purpose: Truncate excessively long tool results

  - Signature summary: positional=messages

  - Async: False, Returns: List[Dict]

  - Cross-file communications: none


## check_architecture.py

- Module: `check_architecture`

- Function `main` (line 15)

  - Purpose: No docstring provided

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `architecture_checker.check_architecture` at line 19 (unresolved)

      - Purpose: No docstring provided

      - Expression: `check_architecture`

    - Calls `architecture_checker.ArchitectureChecker` at line 22 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ArchitectureChecker`

    - Calls `sys.exit` at line 28 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.exit`


## cli/__init__.py

- Module: `cli`

- Functions: none

## cli/commands.py

- Module: `cli.commands`

- Function `_handle_api_command` (line 483)

  - Purpose: Handle the /api command

  - Signature summary: positional=args, session

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `api_server.SessionRegistry` at line 527 (unresolved)

      - Purpose: No docstring provided

      - Expression: `SessionRegistry`

    - Calls `api_server.APIServer` at line 508 (unresolved)

      - Purpose: No docstring provided

      - Expression: `APIServer`

    - Calls `api_server.MessageQueue` at line 536 (unresolved)

      - Purpose: No docstring provided

      - Expression: `MessageQueue`

- Function `_handle_commands_command` (line 369)

  - Purpose: Handle the /commands command

  - Signature summary: positional=args, command_registry

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `_handle_contribute_command` (line 547)

  - Purpose: Handle the /contribute command

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `upgrade_manager.UpgradeManager` at line 553 (unresolved)

      - Purpose: No docstring provided

      - Expression: `UpgradeManager`

- Function `_handle_permissions_command` (line 435)

  - Purpose: Handle the /permissions command

  - Signature summary: positional=args, session

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `_handle_rollback_command` (line 342)

  - Purpose: Handle the /rollback command

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `rollback_manager.RollbackManager` at line 349 (unresolved)

      - Purpose: No docstring provided

      - Expression: `RollbackManager`

- Function `_handle_upgrade_command` (line 302)

  - Purpose: Handle the /upgrade command

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `upgrade_manager.UpgradeManager` at line 308 (unresolved)

      - Purpose: No docstring provided

      - Expression: `UpgradeManager`

- Function `_show_help` (line 574)

  - Purpose: Show help for all commands

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `handle_slash_command` (line 55)

  - Purpose: Handle all slash commands

  - Signature summary: positional=cmd, args, session, config, agent_manager, command_registry

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `cli.utils.count_tokens` at line 98 (ok)

      - Purpose: Estimate token count for messages (simple approximation)

      - Expression: `count_tokens`

    - Calls `opencli.BACKGROUND_TASKS.items` at line 119 (unresolved)

      - Purpose: No docstring provided

      - Expression: `BACKGROUND_TASKS.items`


## cli/config.py

- Module: `cli.config`

- Function `get_api_key` (line 13)

  - Purpose: Get API key for specified provider from environment or config

  - Signature summary: positional=provider

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `os.getenv` at line 25 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.getenv`

- Function `get_config_value` (line 147)

  - Purpose: Get a specific configuration value

  - Signature summary: positional=key, default

  - Async: False, Returns: Any

  - Cross-file communications: none

- Function `load_config` (line 79)

  - Purpose: Load configuration from config file

  - Signature summary: (no parameters)

  - Async: False, Returns: Dict[str, Any]

  - Cross-file communications:

    - Calls `pathlib.Path.home` at line 81 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.home`

    - Calls `json.load` at line 108 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

- Function `migrate_legacy_config` (line 239)

  - Purpose: Migrate configuration from older versions

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path.home` at line 241 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.home`

    - Calls `shutil.copy2` at line 249 (unresolved)

      - Purpose: No docstring provided

      - Expression: `shutil.copy2`

- Function `print_config` (line 214)

  - Purpose: Print current configuration (hiding sensitive data)

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `reset_config` (line 163)

  - Purpose: Reset configuration to defaults

  - Signature summary: (no parameters)

  - Async: False, Returns: Dict[str, Any]

  - Cross-file communications:

    - Calls `pathlib.Path.home` at line 165 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.home`

- Function `save_config` (line 126)

  - Purpose: Save configuration to config file

  - Signature summary: positional=config

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path.home` at line 128 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.home`

    - Calls `json.dump` at line 134 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dump`

- Function `set_config_value` (line 156)

  - Purpose: Set a specific configuration value

  - Signature summary: positional=key, value

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `setup_api_key` (line 35)

  - Purpose: Interactive API key setup

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `update_config` (line 139)

  - Purpose: Update configuration with new values

  - Signature summary: positional=updates

  - Async: False, Returns: Dict[str, Any]

  - Cross-file communications: none

- Function `validate_config` (line 176)

  - Purpose: Validate configuration and return (is_valid, errors)

  - Signature summary: positional=config

  - Async: False, Returns: tuple[bool, list[str]]

  - Cross-file communications: none


## cli/main.py

- Module: `cli.main`

- Function `configure_openrouter_headers_cli` (line 170)

  - Purpose: Configure OpenRouter headers based on policy error

  - Signature summary: positional=policy_message, session, config, model_mgr

  - Async: False, Returns: str

  - Cross-file communications:

    - Calls `asyncio.run` at line 180 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.run`

    - Calls `modules.uptime_checker.check_model_uptime` at line 184 (ok)

      - Purpose: Check current uptime status for a model

      - Expression: `check_model_uptime`

    - Calls `asyncio.new_event_loop` at line 182 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.new_event_loop`

    - Calls `modules.uptime_checker.is_model_healthy` at line 190 (ok)

      - Purpose: Determine if model is healthy enough to attempt requests

      - Expression: `is_model_healthy`

    - Calls `modules.uptime_checker.get_user_recommendation` at line 192 (ok)

      - Purpose: Get recommendation for user based on uptime status

      - Expression: `get_user_recommendation`

    - Calls `os.getenv` at line 203 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.getenv`

- Function `ensure_prompt_at_bottom` (line 148)

  - Purpose: Move cursor to bottom of terminal and clear lines for prompt area

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `shutil.get_terminal_size` at line 151 (unresolved)

      - Purpose: No docstring provided

      - Expression: `shutil.get_terminal_size`

- Function `get_bottom_toolbar` (line 129)

  - Purpose: Create bottom toolbar for rich prompt

  - Signature summary: positional=session, config

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `cli.utils.count_tokens` at line 131 (ok)

      - Purpose: Estimate token count for messages (simple approximation)

      - Expression: `count_tokens`

    - Calls `os.getcwd` at line 136 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.getcwd`

    - Calls `cli.utils.format_model_name` at line 138 (ok)

      - Purpose: Format model name for display

      - Expression: `format_model_name`

    - Calls `prompt_toolkit.formatted_text.HTML` at line 145 (unresolved)

      - Purpose: No docstring provided

      - Expression: `HTML`

- Function `get_git_info` (line 118)

  - Purpose: Get current git repository information

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `subprocess.run` at line 122 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

    - Calls `pathlib.Path` at line 123 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

- Function `interactive` (line 271)

  - Purpose: Interactive CLI mode with fallback prompt interface

  - Signature summary: positional=config, session, initial

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `cli.utils.create_openai_client` at line 490 (ok)

      - Purpose: Create OpenAI client with provider-specific configuration

      - Expression: `create_openai_client`

    - Calls `cli.session.Session` at line 274 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Session`

    - Calls `model_manager.ModelManager` at line 275 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ModelManager`

    - Calls `agent_manager.AgentManager` at line 281 (unresolved)

      - Purpose: No docstring provided

      - Expression: `AgentManager`

    - Calls `command_registry.CommandRegistry` at line 291 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandRegistry`

    - Calls `prompt_processor.PromptProcessor` at line 299 (unresolved)

      - Purpose: No docstring provided

      - Expression: `PromptProcessor`

    - Calls `tool_permissions.ToolPermissionManager` at line 306 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ToolPermissionManager`

    - Calls `api_server.APIServer` at line 313 (unresolved)

      - Purpose: No docstring provided

      - Expression: `APIServer`

    - Calls `api_server.SessionRegistry` at line 319 (unresolved)

      - Purpose: No docstring provided

      - Expression: `SessionRegistry`

    - Calls `os.getpid` at line 322 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.getpid`

    - Calls `json.load` at line 338 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

    - Calls `cli.utils.format_model_name` at line 345 (ok)

      - Purpose: Format model name for display

      - Expression: `format_model_name`

    - Calls `prompt_toolkit.PromptSession` at line 351 (unresolved)

      - Purpose: No docstring provided

      - Expression: `PromptSession`

    - Calls `cli.commands.handle_slash_command` at line 426 (ok)

      - Purpose: Handle all slash commands

      - Expression: `handle_slash_command`

    - Calls `cli.utils.prepare_messages_with_context` at line 454 (ok)

      - Purpose: Prepare messages with additional context

      - Expression: `prepare_messages_with_context`

    - Calls `modules.async_interactive.extract_openrouter_policy_error` at line 483 (unresolved)

      - Purpose: No docstring provided

      - Expression: `extract_openrouter_policy_error`

    - Calls `modules.tool_call_utils.extract_tool_calls_from_text` at line 530 (ok)

      - Purpose: Extract tool calls embedded in text content.

      - Expression: `extract_tool_calls_from_text`

    - Calls `json.dumps` at line 536 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dumps`

    - Calls `types.SimpleNamespace` at line 552 (unresolved)

      - Purpose: No docstring provided

      - Expression: `SimpleNamespace`

    - Calls `cli.tools.execute_tool` at line 560 (ok)

      - Purpose: Execute a tool by name with given arguments

      - Expression: `execute_tool`

    - Calls `json.loads` at line 560 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.loads`

- Function `interactive.get_input` (line 357)

  - Purpose: No docstring provided

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `shutil.get_terminal_size` at line 358 (unresolved)

      - Purpose: No docstring provided

      - Expression: `shutil.get_terminal_size`

    - Calls `prompt_toolkit.print_formatted_text` at line 361 (unresolved)

      - Purpose: No docstring provided

      - Expression: `print_formatted_text`

    - Calls `prompt_toolkit.formatted_text.FormattedText` at line 361 (unresolved)

      - Purpose: No docstring provided

      - Expression: `FormattedText`

    - Calls `prompt_toolkit.formatted_text.HTML` at line 360 (unresolved)

      - Purpose: No docstring provided

      - Expression: `HTML`

- Function `main` (line 587)

  - Purpose: Main entry point for OpenCLI

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `argparse.ArgumentParser` at line 589 (unresolved)

      - Purpose: No docstring provided

      - Expression: `argparse.ArgumentParser`

    - Calls `pathlib.Path.home` at line 603 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.home`

    - Calls `subprocess.run` at line 605 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

    - Calls `cli.config.setup_api_key` at line 612 (ok)

      - Purpose: Interactive API key setup

      - Expression: `setup_api_key`

    - Calls `cli.config.load_config` at line 628 (ok)

      - Purpose: Load configuration from config file

      - Expression: `load_config`

    - Calls `modules.cache_manager.get_cache_manager` at line 635 (ok)

      - Purpose: Get singleton cache manager instance

      - Expression: `get_cache_manager`

    - Calls `cli.session.Session.latest` at line 650 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Session.latest`

    - Calls `cli.session.Session.load` at line 652 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Session.load`

    - Calls `sys.stdin.read` at line 658 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stdin.read`

    - Calls `cli.utils.create_openai_client` at line 659 (ok)

      - Purpose: Create OpenAI client with provider-specific configuration

      - Expression: `create_openai_client`

    - Calls `modules.async_interactive.run_interactive_async` at line 672 (unresolved)

      - Purpose: No docstring provided

      - Expression: `run_interactive_async`

    - Calls `api_server.SessionRegistry` at line 677 (unresolved)

      - Purpose: No docstring provided

      - Expression: `SessionRegistry`


## cli/session.py

- Module: `cli.session`

- Function `Session.__init__` (line 21)

  - Purpose: No docstring provided

  - Signature summary: positional=self, session_id, model

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `uuid.uuid4` at line 22 (unresolved)

      - Purpose: No docstring provided

      - Expression: `uuid.uuid4`

    - Calls `os.getcwd` at line 26 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.getcwd`

- Function `Session._export_markdown` (line 151)

  - Purpose: Export conversation as markdown

  - Signature summary: positional=self

  - Async: False, Returns: str

  - Cross-file communications:

    - Calls `datetime.datetime.now` at line 156 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

- Function `Session._export_text` (line 174)

  - Purpose: Export conversation as plain text

  - Signature summary: positional=self

  - Async: False, Returns: str

  - Cross-file communications:

    - Calls `datetime.datetime.now` at line 179 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

- Function `Session._fix_malformed_messages` (line 86)

  - Purpose: Fix malformed tool calls from old sessions

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.loads` at line 104 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.loads`

- Function `Session.add` (line 31)

  - Purpose: Add a message to the session

  - Signature summary: positional=self, role, content

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `Session.clear_messages` (line 124)

  - Purpose: Clear all messages from session

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `Session.compact_context` (line 35)

  - Purpose: Compact context to fit within token limits

  - Signature summary: positional=self, max_tokens

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `cli.utils.count_tokens` at line 39 (ok)

      - Purpose: Estimate token count for messages (simple approximation)

      - Expression: `count_tokens`

- Function `Session.count_messages_by_role` (line 132)

  - Purpose: Count messages by role

  - Signature summary: positional=self

  - Async: False, Returns: Dict[str, int]

  - Cross-file communications: none

- Function `Session.export_conversation` (line 140)

  - Purpose: Export conversation in specified format

  - Signature summary: positional=self, format

  - Async: False, Returns: str

  - Cross-file communications:

    - Calls `json.dumps` at line 145 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dumps`

- Function `Session.get_context_summary` (line 109)

  - Purpose: Get summary of session context

  - Signature summary: positional=self

  - Async: False, Returns: Dict[str, Any]

  - Cross-file communications:

    - Calls `cli.utils.count_tokens` at line 117 (ok)

      - Purpose: Estimate token count for messages (simple approximation)

      - Expression: `count_tokens`

- Function `Session.get_last_n_messages` (line 128)

  - Purpose: Get last N messages

  - Signature summary: positional=self, n

  - Async: False, Returns: List[Dict[str, Any]]

  - Cross-file communications: none

- Function `Session.load` (line 60)

  - Purpose: Load session from disk

  - Signature summary: positional=cls, session_id

  - Async: False, Returns: Optional['Session']

  - Cross-file communications:

    - Calls `json.load` at line 69 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

    - Calls `os.getcwd` at line 74 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.getcwd`

- Function `Session.save` (line 44)

  - Purpose: Save session to disk

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.dump` at line 48 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dump`

    - Calls `datetime.datetime.now` at line 54 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

- Function `cleanup_old_sessions` (line 229)

  - Purpose: Clean up sessions older than specified days

  - Signature summary: positional=days

  - Async: False, Returns: int

  - Cross-file communications:

    - Calls `time.time` at line 233 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

- Function `create_session` (line 247)

  - Purpose: Create a new session

  - Signature summary: positional=model

  - Async: False, Returns: Session

  - Cross-file communications: none

- Function `delete_session` (line 214)

  - Purpose: Delete a session

  - Signature summary: positional=session_id

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `list_sessions` (line 190)

  - Purpose: List all available sessions

  - Signature summary: (no parameters)

  - Async: False, Returns: List[Dict[str, Any]]

  - Cross-file communications:

    - Calls `json.load` at line 197 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`


## cli/tools.py

- Module: `cli.tools`

- Function `_grep_file` (line 204)

  - Purpose: Search for pattern in a single file

  - Signature summary: positional=pattern, file_path

  - Async: False, Returns: List[Dict[str, Any]]

  - Cross-file communications:

    - Calls `re.search` at line 210 (unresolved)

      - Purpose: No docstring provided

      - Expression: `re.search`

- Function `_is_text_file` (line 224)

  - Purpose: Check if file is likely a text file

  - Signature summary: positional=file_path

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `execute_bash` (line 117)

  - Purpose: Execute Bash tool - run shell command

  - Signature summary: positional=command, description

  - Async: False, Returns: Dict[str, Any]

  - Cross-file communications:

    - Calls `re.search` at line 129 (unresolved)

      - Purpose: No docstring provided

      - Expression: `re.search`

    - Calls `subprocess.run` at line 133 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

    - Calls `os.getcwd` at line 139 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.getcwd`

- Function `execute_edit` (line 87)

  - Purpose: Execute Edit tool - replace text in file

  - Signature summary: positional=file_path, old_string, new_string

  - Async: False, Returns: Dict[str, Any]

  - Cross-file communications: none

- Function `execute_glob` (line 157)

  - Purpose: Execute Glob tool - find files by pattern

  - Signature summary: positional=pattern

  - Async: False, Returns: Dict[str, Any]

  - Cross-file communications:

    - Calls `glob.glob` at line 160 (unresolved)

      - Purpose: No docstring provided

      - Expression: `glob.glob`

- Function `execute_grep` (line 173)

  - Purpose: Execute Grep tool - search for pattern in files

  - Signature summary: positional=pattern, path, recursive

  - Async: False, Returns: Dict[str, Any]

  - Cross-file communications:

    - Calls `pathlib.Path` at line 177 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

- Function `execute_read` (line 58)

  - Purpose: Execute Read tool - read file contents

  - Signature summary: positional=file_path

  - Async: False, Returns: Dict[str, Any]

  - Cross-file communications: none

- Function `execute_tool` (line 249)

  - Purpose: Execute a tool by name with given arguments

  - Signature summary: positional=name, args, permission_manager, current_dir

  - Async: False, Returns: Dict[str, Any]

  - Cross-file communications:

    - Calls `os.getcwd` at line 254 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.getcwd`

    - Calls `os.chdir` at line 289 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.chdir`

- Function `execute_write` (line 72)

  - Purpose: Execute Write tool - write content to file

  - Signature summary: positional=file_path, content

  - Async: False, Returns: Dict[str, Any]

  - Cross-file communications:

    - Calls `pathlib.Path` at line 76 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

- Function `get_tool_list` (line 294)

  - Purpose: Get list of available tools with descriptions

  - Signature summary: (no parameters)

  - Async: False, Returns: List[Dict[str, Any]]

  - Cross-file communications: none

- Function `validate_tool_args` (line 339)

  - Purpose: Validate tool arguments

  - Signature summary: positional=tool_name, args

  - Async: False, Returns: tuple[bool, Optional[str]]

  - Cross-file communications: none


## cli/utils.py

- Module: `cli.utils`

- Function `count_tokens` (line 13)

  - Purpose: Estimate token count for messages (simple approximation)

  - Signature summary: positional=messages

  - Async: False, Returns: int

  - Cross-file communications: none

- Function `create_openai_client` (line 67)

  - Purpose: Create OpenAI client with provider-specific configuration

  - Signature summary: positional=config

  - Async: False, Returns: OpenAI

  - Cross-file communications:

    - Calls `openai.OpenAI` at line 71 (unresolved)

      - Purpose: No docstring provided

      - Expression: `OpenAI`

- Function `ensure_directory_exists` (line 146)

  - Purpose: Ensure directory exists, create if needed

  - Signature summary: positional=path

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `escape_markdown` (line 190)

  - Purpose: Escape markdown special characters

  - Signature summary: positional=text

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `format_duration` (line 209)

  - Purpose: Format duration in human readable format

  - Signature summary: positional=seconds

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `format_file_size` (line 114)

  - Purpose: Format file size in human readable format

  - Signature summary: positional=size_bytes

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `format_model_name` (line 79)

  - Purpose: Format model name for display

  - Signature summary: positional=model

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `get_current_working_directory` (line 138)

  - Purpose: Get current working directory with error handling

  - Signature summary: (no parameters)

  - Async: False, Returns: str

  - Cross-file communications:

    - Calls `os.getcwd` at line 141 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.getcwd`

    - Calls `pathlib.Path.home` at line 143 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.home`

- Function `get_file_extension` (line 172)

  - Purpose: Get file extension from filename

  - Signature summary: positional=filename

  - Async: False, Returns: str

  - Cross-file communications:

    - Calls `pathlib.Path` at line 174 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

- Function `get_system_info` (line 221)

  - Purpose: Get basic system information

  - Signature summary: (no parameters)

  - Async: False, Returns: Dict[str, Any]

  - Cross-file communications:

    - Calls `platform.system` at line 227 (unresolved)

      - Purpose: No docstring provided

      - Expression: `platform.system`

    - Calls `platform.release` at line 228 (unresolved)

      - Purpose: No docstring provided

      - Expression: `platform.release`

    - Calls `platform.machine` at line 229 (unresolved)

      - Purpose: No docstring provided

      - Expression: `platform.machine`

    - Calls `sys.version.split` at line 230 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.version.split`

- Function `is_text_file` (line 177)

  - Purpose: Check if file is likely a text file based on extension

  - Signature summary: positional=filename

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `is_valid_session_id` (line 155)

  - Purpose: Validate session ID format

  - Signature summary: positional=session_id

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `parse_command_args` (line 200)

  - Purpose: Parse command string into command and arguments

  - Signature summary: positional=command

  - Async: False, Returns: tuple[str, List[str]]

  - Cross-file communications: none

- Function `prepare_messages_with_context` (line 24)

  - Purpose: Prepare messages with additional context

  - Signature summary: positional=messages, config_dir

  - Async: False, Returns: List[Dict[str, Any]]

  - Cross-file communications:

    - Calls `pathlib.Path.home` at line 27 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.home`

- Function `safe_json_loads` (line 123)

  - Purpose: Safely parse JSON with fallback

  - Signature summary: positional=json_str, default

  - Async: False, Returns: Any

  - Cross-file communications:

    - Calls `json.loads` at line 126 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.loads`

- Function `truncate_text` (line 131)

  - Purpose: Truncate text to specified length

  - Signature summary: positional=text, max_length, suffix

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `validate_api_key` (line 91)

  - Purpose: Basic API key validation

  - Signature summary: positional=api_key

  - Async: False, Returns: bool

  - Cross-file communications: none


## detailed_profiler.py

- Module: `detailed_profiler`

- Function `DetailedProfiler.__init__` (line 94)

  - Purpose: No docstring provided

  - Signature summary: positional=self, sample_interval, duration

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `collections.defaultdict` at line 121 (unresolved)

      - Purpose: No docstring provided

      - Expression: `defaultdict`

- Function `DetailedProfiler._add_user_input_markers` (line 624)

  - Purpose: Add vertical lines showing user input events

  - Signature summary: positional=self, ax

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `DetailedProfiler._analyze_discovery_window` (line 498)

  - Purpose: Analyze ±window_size seconds around an event timestamp

  - Signature summary: positional=self, event_timestamp, window_size

  - Async: False, Returns: Dict

  - Cross-file communications:

    - Calls `collections.defaultdict` at line 515 (unresolved)

      - Purpose: No docstring provided

      - Expression: `defaultdict`

- Function `DetailedProfiler._categorize_thread` (line 130)

  - Purpose: Categorize thread by role

  - Signature summary: positional=self, thread_name

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `DetailedProfiler._detect_blocking_state` (line 141)

  - Purpose: Detect if thread is blocked and what type

  - Signature summary: positional=self, stack

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `DetailedProfiler._generate_all_functions_coverage_page` (line 1061)

  - Purpose: Page 7: All Functions Coverage - Stock-Like Graph

  - Signature summary: positional=self, pdf

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `matplotlib.pyplot.subplots` at line 1063 (unresolved)

      - Purpose: No docstring provided

      - Expression: `plt.subplots`

    - Calls `matplotlib.pyplot.tight_layout` at line 1117 (unresolved)

      - Purpose: No docstring provided

      - Expression: `plt.tight_layout`

    - Calls `matplotlib.pyplot.close` at line 1119 (unresolved)

      - Purpose: No docstring provided

      - Expression: `plt.close`

- Function `DetailedProfiler._generate_blocking_analysis_page` (line 819)

  - Purpose: Page 3: Blocking analysis - when and where blocking occurs + USER INPUT MARKERS

  - Signature summary: positional=self, pdf

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `matplotlib.pyplot.subplots` at line 821 (unresolved)

      - Purpose: No docstring provided

      - Expression: `plt.subplots`

    - Calls `collections.defaultdict` at line 845 (unresolved)

      - Purpose: No docstring provided

      - Expression: `defaultdict`

    - Calls `matplotlib.pyplot.tight_layout` at line 875 (unresolved)

      - Purpose: No docstring provided

      - Expression: `plt.tight_layout`

    - Calls `matplotlib.pyplot.close` at line 877 (unresolved)

      - Purpose: No docstring provided

      - Expression: `plt.close`

- Function `DetailedProfiler._generate_event_propagation_page` (line 1121)

  - Purpose: Page 8: Event Propagation Analysis

  - Signature summary: positional=self, pdf

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `matplotlib.pyplot.subplots` at line 1123 (unresolved)

      - Purpose: No docstring provided

      - Expression: `plt.subplots`

    - Calls `collections.defaultdict` at line 1166 (unresolved)

      - Purpose: No docstring provided

      - Expression: `defaultdict`

    - Calls `matplotlib.pyplot.tight_layout` at line 1188 (unresolved)

      - Purpose: No docstring provided

      - Expression: `plt.tight_layout`

    - Calls `matplotlib.pyplot.close` at line 1190 (unresolved)

      - Purpose: No docstring provided

      - Expression: `plt.close`

- Function `DetailedProfiler._generate_function_hierarchy_page` (line 1004)

  - Purpose: Page 6: Hierarchical Function Call Graph

  - Signature summary: positional=self, pdf

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `matplotlib.pyplot.subplots` at line 1006 (unresolved)

      - Purpose: No docstring provided

      - Expression: `plt.subplots`

    - Calls `collections.defaultdict` at line 1009 (unresolved)

      - Purpose: No docstring provided

      - Expression: `defaultdict`

    - Calls `matplotlib.pyplot.tight_layout` at line 1057 (unresolved)

      - Purpose: No docstring provided

      - Expression: `plt.tight_layout`

    - Calls `matplotlib.pyplot.close` at line 1059 (unresolved)

      - Purpose: No docstring provided

      - Expression: `plt.close`

- Function `DetailedProfiler._generate_function_timeline_page` (line 768)

  - Purpose: Page 2: Function transition timeline with arrows + USER INPUT MARKERS

  - Signature summary: positional=self, pdf

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `matplotlib.pyplot.subplots` at line 770 (unresolved)

      - Purpose: No docstring provided

      - Expression: `plt.subplots`

    - Calls `matplotlib.pyplot.tight_layout` at line 815 (unresolved)

      - Purpose: No docstring provided

      - Expression: `plt.tight_layout`

    - Calls `matplotlib.pyplot.close` at line 817 (unresolved)

      - Purpose: No docstring provided

      - Expression: `plt.close`

- Function `DetailedProfiler._generate_handoff_analysis_page` (line 879)

  - Purpose: Page 4: Function handoff analysis

  - Signature summary: positional=self, pdf

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `matplotlib.pyplot.subplots` at line 881 (unresolved)

      - Purpose: No docstring provided

      - Expression: `plt.subplots`

    - Calls `collections.defaultdict` at line 884 (unresolved)

      - Purpose: No docstring provided

      - Expression: `defaultdict`

    - Calls `matplotlib.pyplot.tight_layout` at line 913 (unresolved)

      - Purpose: No docstring provided

      - Expression: `plt.tight_layout`

    - Calls `matplotlib.pyplot.close` at line 915 (unresolved)

      - Purpose: No docstring provided

      - Expression: `plt.close`

- Function `DetailedProfiler._generate_message_discovery_page` (line 1192)

  - Purpose: DYNAMIC PAGE: User Message #{idx} Discovery (±10s Analysis)

  - Signature summary: positional=self, pdf, message, idx

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `matplotlib.pyplot.figure` at line 1194 (unresolved)

      - Purpose: No docstring provided

      - Expression: `plt.figure`

    - Calls `collections.defaultdict` at line 1285 (unresolved)

      - Purpose: No docstring provided

      - Expression: `defaultdict`

    - Calls `matplotlib.pyplot.tight_layout` at line 1311 (unresolved)

      - Purpose: No docstring provided

      - Expression: `plt.tight_layout`

    - Calls `matplotlib.pyplot.close` at line 1313 (unresolved)

      - Purpose: No docstring provided

      - Expression: `plt.close`

- Function `DetailedProfiler._generate_permission_discovery_page` (line 1315)

  - Purpose: DYNAMIC PAGE: Permission Prompt #{idx} Discovery (±10s Analysis)

  - Signature summary: positional=self, pdf, prompt, idx

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `matplotlib.pyplot.figure` at line 1317 (unresolved)

      - Purpose: No docstring provided

      - Expression: `plt.figure`

    - Calls `collections.defaultdict` at line 1408 (unresolved)

      - Purpose: No docstring provided

      - Expression: `defaultdict`

    - Calls `matplotlib.pyplot.tight_layout` at line 1434 (unresolved)

      - Purpose: No docstring provided

      - Expression: `plt.tight_layout`

    - Calls `matplotlib.pyplot.close` at line 1436 (unresolved)

      - Purpose: No docstring provided

      - Expression: `plt.close`

- Function `DetailedProfiler._generate_state_distribution_page` (line 917)

  - Purpose: Page 5: State distribution analysis

  - Signature summary: positional=self, pdf

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `matplotlib.pyplot.subplots` at line 919 (unresolved)

      - Purpose: No docstring provided

      - Expression: `plt.subplots`

    - Calls `collections.defaultdict` at line 958 (unresolved)

      - Purpose: No docstring provided

      - Expression: `defaultdict`

    - Calls `matplotlib.pyplot.tight_layout` at line 1000 (unresolved)

      - Purpose: No docstring provided

      - Expression: `plt.tight_layout`

    - Calls `matplotlib.pyplot.close` at line 1002 (unresolved)

      - Purpose: No docstring provided

      - Expression: `plt.close`

- Function `DetailedProfiler._generate_thread_timeline_page` (line 649)

  - Purpose: Page 1: Detailed thread activity timeline with labeled functions + USER INPUT MARKERS

  - Signature summary: positional=self, pdf

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `matplotlib.pyplot.subplots` at line 651 (unresolved)

      - Purpose: No docstring provided

      - Expression: `plt.subplots`

    - Calls `matplotlib.patches.FancyBboxPatch` at line 698 (unresolved)

      - Purpose: No docstring provided

      - Expression: `FancyBboxPatch`

    - Calls `matplotlib.patches.Patch` at line 756 (unresolved)

      - Purpose: No docstring provided

      - Expression: `mpatches.Patch`

    - Calls `matplotlib.lines.Line2D` at line 757 (unresolved)

      - Purpose: No docstring provided

      - Expression: `mlines.Line2D`

    - Calls `matplotlib.pyplot.tight_layout` at line 764 (unresolved)

      - Purpose: No docstring provided

      - Expression: `plt.tight_layout`

    - Calls `matplotlib.pyplot.close` at line 766 (unresolved)

      - Purpose: No docstring provided

      - Expression: `plt.close`

- Function `DetailedProfiler._on_key_press` (line 168)

  - Purpose: Callback for keyboard events

  - Signature summary: positional=self, key

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `time.time` at line 173 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

    - Calls `datetime.datetime.now` at line 183 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

- Function `DetailedProfiler._start_keyboard_monitoring` (line 189)

  - Purpose: Start keyboard event monitoring

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pynput.keyboard.Listener` at line 196 (unresolved)

      - Purpose: No docstring provided

      - Expression: `keyboard.Listener`

- Function `DetailedProfiler._stop_keyboard_monitoring` (line 204)

  - Purpose: Stop keyboard event monitoring

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `DetailedProfiler.capture_sample` (line 210)

  - Purpose: Capture detailed sample of all thread states

  - Signature summary: positional=self

  - Async: False, Returns: Dict

  - Cross-file communications:

    - Calls `time.time` at line 212 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

    - Calls `datetime.datetime.now` at line 215 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

    - Calls `sys._current_frames` at line 219 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys._current_frames`

    - Calls `threading.enumerate` at line 221 (unresolved)

      - Purpose: No docstring provided

      - Expression: `threading.enumerate`

    - Calls `traceback.extract_stack` at line 229 (unresolved)

      - Purpose: No docstring provided

      - Expression: `traceback.extract_stack`

- Function `DetailedProfiler.generate_detailed_pdf` (line 576)

  - Purpose: Generate comprehensive DYNAMIC multi-page PDF with maximum detail

  - Signature summary: positional=self, output_path

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `matplotlib.backends.backend_pdf.PdfPages` at line 594 (unresolved)

      - Purpose: No docstring provided

      - Expression: `PdfPages`

- Function `DetailedProfiler.profile` (line 454)

  - Purpose: Run profiling

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `time.time` at line 478 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

    - Calls `time.sleep` at line 482 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.sleep`

- Function `DetailedProfiler.save_detailed_json` (line 1438)

  - Purpose: Save comprehensive raw data with ALL new structures

  - Signature summary: positional=self, output_path

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.dump` at line 1505 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dump`

- Function `main` (line 1519)

  - Purpose: No docstring provided

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `argparse.ArgumentParser` at line 1521 (unresolved)

      - Purpose: No docstring provided

      - Expression: `argparse.ArgumentParser`


## github_tool.py

- Module: `github_tool`

- Function `GitHubTool.check_auth` (line 16)

  - Purpose: Check if user is authenticated with gh CLI

  - Signature summary: (no parameters)

  - Async: False, Returns: Dict

  - Cross-file communications:

    - Calls `subprocess.run` at line 19 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `GitHubTool.execute_command` (line 48)

  - Purpose: Execute gh CLI command

  - Signature summary: positional=command, args

  - Async: False, Returns: str

  - Cross-file communications:

    - Calls `subprocess.run` at line 59 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `GitHubTool.gist_create` (line 192)

  - Purpose: Create gist from files

  - Signature summary: positional=files, description, public

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `GitHubTool.issue_create` (line 108)

  - Purpose: Create new issue

  - Signature summary: positional=title, body, repo

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `GitHubTool.issue_list` (line 87)

  - Purpose: List issues

  - Signature summary: positional=repo, limit, state

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `GitHubTool.issue_view` (line 97)

  - Purpose: View issue details

  - Signature summary: positional=number, repo

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `GitHubTool.pr_checkout` (line 153)

  - Purpose: Checkout pull request locally

  - Signature summary: positional=number, repo

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `GitHubTool.pr_create` (line 140)

  - Purpose: Create pull request

  - Signature summary: positional=title, body, base, head, repo

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `GitHubTool.pr_list` (line 119)

  - Purpose: List pull requests

  - Signature summary: positional=repo, limit, state

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `GitHubTool.pr_view` (line 129)

  - Purpose: View pull request details

  - Signature summary: positional=number, repo

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `GitHubTool.repo_view` (line 75)

  - Purpose: View repository details

  - Signature summary: positional=repo

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `GitHubTool.run_list` (line 182)

  - Purpose: List workflow runs

  - Signature summary: positional=repo, limit

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `GitHubTool.workflow_list` (line 162)

  - Purpose: List GitHub Actions workflows

  - Signature summary: positional=repo

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `GitHubTool.workflow_run` (line 173)

  - Purpose: Trigger workflow run

  - Signature summary: positional=workflow, repo

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `_build_repo_query` (line 209)

  - Purpose: Build GraphQL query for repo info

  - Signature summary: positional=repo

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `execute_github_tool` (line 216)

  - Purpose: Execute GitHub tool action

  - Signature summary: positional=action; kwarg=kwargs

  - Async: False, Returns: str

  - Cross-file communications:

    - Calls `json.dumps` at line 221 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dumps`


## inject_advanced_profiler.py

- Module: `inject_advanced_profiler`

- Function `inject_and_profile` (line 25)

  - Purpose: Run profiler in background thread within the current process

  - Signature summary: positional=interval, duration

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `advanced_profiler.AdvancedProfiler` at line 42 (unresolved)

      - Purpose: No docstring provided

      - Expression: `AdvancedProfiler`

    - Calls `threading.Thread` at line 63 (unresolved)

      - Purpose: No docstring provided

      - Expression: `threading.Thread`

- Function `inject_and_profile.profile_thread` (line 45)

  - Purpose: No docstring provided

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `traceback.print_exc` at line 61 (unresolved)

      - Purpose: No docstring provided

      - Expression: `traceback.print_exc`


## inject_detailed_profiler.py

- Module: `inject_detailed_profiler`

- Function `inject_profiler` (line 32)

  - Purpose: Inject detailed profiler into current process as background thread

  - Signature summary: positional=interval, duration

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `detailed_profiler.DetailedProfiler` at line 60 (unresolved)

      - Purpose: No docstring provided

      - Expression: `DetailedProfiler`

    - Calls `threading.Thread` at line 108 (unresolved)

      - Purpose: No docstring provided

      - Expression: `threading.Thread`

- Function `inject_profiler.profile_thread` (line 62)

  - Purpose: No docstring provided

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `subprocess.run` at line 97 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

    - Calls `traceback.print_exc` at line 105 (unresolved)

      - Purpose: No docstring provided

      - Expression: `traceback.print_exc`


## modules/__init__.py

- Module: `modules`

- Functions: none

## modules/agent_manager.py

- Module: `modules.agent_manager`

- Function `AgentConfig.__init__` (line 28)

  - Purpose: No docstring provided

  - Signature summary: positional=self, name, config

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `AgentConfig.build_system_message` (line 47)

  - Purpose: Build complete system prompt with project context

  - Signature summary: positional=self, project_context

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `AgentConfig.matches_trigger` (line 39)

  - Purpose: Check if user input matches any triggers

  - Signature summary: positional=self, user_input

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `AgentManager.__init__` (line 140)

  - Purpose: No docstring provided

  - Signature summary: positional=self, config_dir

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `context_builder.ContextBuilder` at line 150 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ContextBuilder`

- Function `AgentManager.find_agents_md` (line 200)

  - Purpose: Find and read AGENTS.md file (closest to working dir)

  - Signature summary: positional=self, working_dir

  - Async: False, Returns: Optional[str]

  - Cross-file communications:

    - Calls `pathlib.Path` at line 214 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

- Function `AgentManager.get_agent_tools` (line 324)

  - Purpose: Get tools for specific agent (merge with base tools)

  - Signature summary: positional=self, agent_name, base_tools

  - Async: False, Returns: List[Dict]

  - Cross-file communications: none

- Function `AgentManager.list_agents` (line 334)

  - Purpose: List all available agents

  - Signature summary: positional=self

  - Async: False, Returns: List[Tuple[str, str]]

  - Cross-file communications: none

- Function `AgentManager.load_agents` (line 157)

  - Purpose: Load agent configurations from YAML files

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `yaml.safe_load` at line 178 (unresolved)

      - Purpose: No docstring provided

      - Expression: `yaml.safe_load`

- Function `AgentManager.load_constitution` (line 192)

  - Purpose: Load constitution from agents/system_prompts/base/

  - Signature summary: positional=self

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `AgentManager.prepare_messages` (line 248)

  - Purpose: Prepare optimized messages for agent with context management

  - Signature summary: positional=self, agent_name, messages, working_dir, session_id

  - Async: False, Returns: List[Dict]

  - Cross-file communications:

    - Calls `os.getcwd` at line 279 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.getcwd`

    - Calls `modules.tool_call_utils.normalize_tool_call_messages` at line 321 (ok)

      - Purpose: Return a sanitized copy of messages with well-formed tool call payloads.

      - Expression: `normalize_tool_call_messages`

- Function `AgentManager.select_agent` (line 226)

  - Purpose: Select appropriate agent based on user input

  - Signature summary: positional=self, user_input, current_agent

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `ContextManager.compress_context` (line 84)

  - Purpose: Compress context using various strategies:

  - Signature summary: positional=messages, max_tokens, strategy

  - Async: False, Returns: List[Dict]

  - Cross-file communications: none

- Function `ContextManager.count_tokens` (line 79)

  - Purpose: Estimate token count (4 chars per token)

  - Signature summary: positional=messages

  - Async: False, Returns: int

  - Cross-file communications:

    - Calls `json.dumps` at line 81 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dumps`

- Function `ContextManager.optimize_tool_results` (line 116)

  - Purpose: Truncate excessively long tool results

  - Signature summary: positional=messages

  - Async: False, Returns: List[Dict]

  - Cross-file communications: none


## modules/ansi_background.py

- Module: `modules.ansi_background`

- Function `ANSIBackgroundMixin.__init__` (line 152)

  - Purpose: Initialize with color mode support

  - Signature summary: positional=self; kwonly=color_mode; vararg=args; kwarg=kwargs

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `color_manager.ColorManager.set_mode` at line 161 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ColorManager.set_mode`

- Function `ANSIBackgroundMixin.configure_from_dict` (line 165)

  - Purpose: Configure color mode from config dictionary

  - Signature summary: positional=self, config

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `color_manager.configure_color_mode` at line 172 (unresolved)

      - Purpose: No docstring provided

      - Expression: `configure_color_mode`

- Function `_patched_color_parse` (line 23)

  - Purpose: Patch Color.parse to accept 'default' keyword

  - Signature summary: positional=cls, color_text; vararg=args; kwarg=kwargs

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `_patched_domnode_rich_style` (line 111)

  - Purpose: Patch DOMNode.rich_style to use ColorManager

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `textual.color.Color` at line 116 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Color`

    - Calls `rich.style.Style` at line 117 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Style`

    - Calls `color_manager.ColorManager.process_foreground` at line 134 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ColorManager.process_foreground`

    - Calls `color_manager.ColorManager.process_background` at line 135 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ColorManager.process_background`

    - Calls `rich.style.Style.from_color` at line 137 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Style.from_color`

- Function `_patched_rich_style_with_offset` (line 73)

  - Purpose: Patch text selection styles to use ColorManager

  - Signature summary: positional=self, x, y

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `color_manager.ColorManager.process_foreground` at line 81 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ColorManager.process_foreground`

    - Calls `color_manager.ColorManager.process_background` at line 84 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ColorManager.process_background`

    - Calls `rich.style.Style` at line 88 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Style`

- Function `_patched_textual_rich_style` (line 39)

  - Purpose: Patch to use ColorManager for background processing

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `color_manager.ColorManager.process_foreground` at line 45 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ColorManager.process_foreground`

    - Calls `color_manager.ColorManager.process_background` at line 48 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ColorManager.process_background`

    - Calls `rich.style.Style` at line 52 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Style`

- Function `create_ansi_background_app` (line 176)

  - Purpose: Decorator to add configurable color mode support to a Textual App

  - Signature summary: positional=app_class

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `enable_ansi_backgrounds` (line 201)

  - Purpose: Global function to enable ANSI background mode

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `color_manager.ColorManager.set_mode` at line 208 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ColorManager.set_mode`

- Function `enable_full_ansi` (line 216)

  - Purpose: Enable full ANSI 256 color mode

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `color_manager.ColorManager.set_mode` at line 218 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ColorManager.set_mode`

- Function `enable_full_rgb` (line 211)

  - Purpose: Enable full RGB mode (Textual default)

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `color_manager.ColorManager.set_mode` at line 213 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ColorManager.set_mode`


## modules/api_client.py

- Module: `modules.api_client`

- Function `OpenCLIClient.__init__` (line 14)

  - Purpose: No docstring provided

  - Signature summary: positional=self, host, port

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `OpenCLIClient.get_messages` (line 78)

  - Purpose: Get messages for a session

  - Signature summary: positional=self, session_id

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `requests.get` at line 81 (unresolved)

      - Purpose: No docstring provided

      - Expression: `requests.get`

- Function `OpenCLIClient.get_session` (line 33)

  - Purpose: Get specific session information

  - Signature summary: positional=self, session_id

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `requests.get` at line 36 (unresolved)

      - Purpose: No docstring provided

      - Expression: `requests.get`

- Function `OpenCLIClient.get_status` (line 17)

  - Purpose: Get API server status

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `requests.get` at line 20 (unresolved)

      - Purpose: No docstring provided

      - Expression: `requests.get`

- Function `OpenCLIClient.heartbeat` (line 55)

  - Purpose: Send session heartbeat

  - Signature summary: positional=self, session_id

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `requests.post` at line 58 (unresolved)

      - Purpose: No docstring provided

      - Expression: `requests.post`

- Function `OpenCLIClient.list_sessions` (line 25)

  - Purpose: List all active OpenCLI sessions

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `requests.get` at line 28 (unresolved)

      - Purpose: No docstring provided

      - Expression: `requests.get`

- Function `OpenCLIClient.register_session` (line 41)

  - Purpose: Register a new session

  - Signature summary: positional=self, session_id, pid, model, agent, cwd

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `requests.post` at line 44 (unresolved)

      - Purpose: No docstring provided

      - Expression: `requests.post`

- Function `OpenCLIClient.send_message` (line 65)

  - Purpose: Send message to another session

  - Signature summary: positional=self, to_session, from_session, message_type, payload

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `requests.post` at line 68 (unresolved)

      - Purpose: No docstring provided

      - Expression: `requests.post`

- Function `main` (line 86)

  - Purpose: CLI interface for API client

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.dumps` at line 141 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dumps`


## modules/api_server.py

- Module: `modules.api_server`

- Function `APIServer.__init__` (line 286)

  - Purpose: No docstring provided

  - Signature summary: positional=self, config_dir

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `APIServer.is_running` (line 316)

  - Purpose: Check if server is running

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `APIServer.start` (line 292)

  - Purpose: Start API server in background thread

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `threading.Thread` at line 302 (unresolved)

      - Purpose: No docstring provided

      - Expression: `threading.Thread`

- Function `APIServer.stop` (line 310)

  - Purpose: Stop API server

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `APIServerConfig.__init__` (line 19)

  - Purpose: No docstring provided

  - Signature summary: positional=self, config_dir

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path.home` at line 20 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.home`

- Function `APIServerConfig._load_config` (line 31)

  - Purpose: Load API server configuration

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.load` at line 36 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

- Function `APIServerConfig.save_config` (line 50)

  - Purpose: Save API server configuration

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.dump` at line 53 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dump`

- Function `MessageQueue.__init__` (line 131)

  - Purpose: No docstring provided

  - Signature summary: positional=self, config_dir

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path.home` at line 132 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.home`

- Function `MessageQueue.get_messages` (line 156)

  - Purpose: Get messages for a session

  - Signature summary: positional=self, session_id, delete

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.load` at line 163 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

- Function `MessageQueue.send_message` (line 137)

  - Purpose: Send message to another session

  - Signature summary: positional=self, to_session, from_session, message_type, payload

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `time.time` at line 148 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

    - Calls `json.dump` at line 152 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dump`

- Function `OpenCLIAPIHandler._send_json` (line 182)

  - Purpose: Send JSON response

  - Signature summary: positional=self, data, status

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.dumps` at line 185 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dumps`

- Function `OpenCLIAPIHandler._set_headers` (line 175)

  - Purpose: Set HTTP response headers

  - Signature summary: positional=self, status, content_type

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `OpenCLIAPIHandler.do_GET` (line 187)

  - Purpose: Handle GET requests

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `urllib.parse.urlparse` at line 189 (unresolved)

      - Purpose: No docstring provided

      - Expression: `urlparse`

- Function `OpenCLIAPIHandler.do_POST` (line 228)

  - Purpose: Handle POST requests

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `urllib.parse.urlparse` at line 230 (unresolved)

      - Purpose: No docstring provided

      - Expression: `urlparse`

    - Calls `json.loads` at line 238 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.loads`

    - Calls `os.getpid` at line 251 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.getpid`

- Function `OpenCLIAPIHandler.log_message` (line 276)

  - Purpose: Suppress request logging

  - Signature summary: positional=self, format; vararg=args

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `SessionRegistry.__init__` (line 57)

  - Purpose: No docstring provided

  - Signature summary: positional=self, config_dir

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path.home` at line 58 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.home`

- Function `SessionRegistry.get_session` (line 118)

  - Purpose: Get specific session info

  - Signature summary: positional=self, session_id

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.load` at line 124 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

- Function `SessionRegistry.heartbeat` (line 84)

  - Purpose: Update session heartbeat

  - Signature summary: positional=self, session_id

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.load` at line 90 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

    - Calls `time.time` at line 91 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

    - Calls `json.dump` at line 93 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dump`

- Function `SessionRegistry.list_active_sessions` (line 97)

  - Purpose: List all active sessions (within timeout)

  - Signature summary: positional=self, timeout

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `time.time` at line 100 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

    - Calls `json.load` at line 105 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

- Function `SessionRegistry.register_session` (line 62)

  - Purpose: Register an active session

  - Signature summary: positional=self, session_id, pid, model, agent, cwd

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `time.time` at line 72 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

    - Calls `json.dump` at line 76 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dump`

- Function `SessionRegistry.unregister_session` (line 78)

  - Purpose: Unregister a session

  - Signature summary: positional=self, session_id

  - Async: False, Returns: None

  - Cross-file communications: none


## modules/architecture_checker.py

- Module: `modules.architecture_checker`

- Function `ArchitectureChecker.__init__` (line 52)

  - Purpose: No docstring provided

  - Signature summary: positional=self, blueprint_path

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path` at line 55 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

- Function `ArchitectureChecker._calculate_metrics` (line 230)

  - Purpose: Calculate codebase metrics

  - Signature summary: positional=self, report

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `ast.parse` at line 248 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ast.parse`

    - Calls `ast.walk` at line 249 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ast.walk`

- Function `ArchitectureChecker._check_file_sizes` (line 155)

  - Purpose: Check that files don't exceed max_lines

  - Signature summary: positional=self, report

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ArchitectureChecker._check_forbidden_imports` (line 186)

  - Purpose: Check forbidden import patterns across all files

  - Signature summary: positional=self, report

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ArchitectureChecker._check_metric_target` (line 274)

  - Purpose: Check if metric meets target

  - Signature summary: positional=self, report, metric, actual, target

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ArchitectureChecker._check_module_dependencies` (line 92)

  - Purpose: Check that modules only import allowed dependencies

  - Signature summary: positional=self, report

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `ast.parse` at line 114 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ast.parse`

- Function `ArchitectureChecker._check_ui_business_separation` (line 197)

  - Purpose: Check UI/business separation rule

  - Signature summary: positional=self, report, rule

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `ast.parse` at line 212 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ast.parse`

- Function `ArchitectureChecker._extract_imports` (line 300)

  - Purpose: Extract all import statements from AST

  - Signature summary: positional=self, tree

  - Async: False, Returns: List[str]

  - Cross-file communications:

    - Calls `ast.walk` at line 304 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ast.walk`

- Function `ArchitectureChecker._is_stdlib_import` (line 314)

  - Purpose: Check if import is from standard library

  - Signature summary: positional=self, import_name

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `ArchitectureChecker.check_all` (line 67)

  - Purpose: Run all compliance checks

  - Signature summary: positional=self

  - Async: False, Returns: ComplianceReport

  - Cross-file communications:

    - Calls `datetime.datetime.now` at line 82 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

- Function `ArchitectureChecker.format_report` (line 327)

  - Purpose: Format compliance report as readable text

  - Signature summary: positional=self, report

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `ArchitectureChecker.load_blueprint` (line 57)

  - Purpose: Load the architecture blueprint

  - Signature summary: positional=self

  - Async: False, Returns: bool

  - Cross-file communications:

    - Calls `yaml.safe_load` at line 61 (unresolved)

      - Purpose: No docstring provided

      - Expression: `yaml.safe_load`

- Function `ComplianceReport.add_violation` (line 35)

  - Purpose: Add a violation to the appropriate list

  - Signature summary: positional=self, violation

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ComplianceReport.has_errors` (line 44)

  - Purpose: Check if there are any errors

  - Signature summary: positional=self

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `check_architecture` (line 378)

  - Purpose: Convenience function to check architecture

  - Signature summary: positional=blueprint_path

  - Async: False, Returns: ComplianceReport

  - Cross-file communications: none


## modules/architecture_validator.py

- Module: `modules.architecture_validator`

- Function `ArchitectureValidator.__init__` (line 75)

  - Purpose: No docstring provided

  - Signature summary: positional=self, repo_path, arch_file

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path` at line 76 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

- Function `ArchitectureValidator._check_imports` (line 149)

  - Purpose: Check import compliance

  - Signature summary: positional=self, file_path, module_spec, report

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `ast.parse` at line 153 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ast.parse`

    - Calls `ast.walk` at line 156 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ast.walk`

- Function `ArchitectureValidator._check_module` (line 105)

  - Purpose: Check a single module for compliance

  - Signature summary: positional=self, module_spec, report

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ArchitectureValidator._match_import_pattern` (line 203)

  - Purpose: Match import pattern with wildcards

  - Signature summary: positional=self, pattern, actual

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `ArchitectureValidator.check_performance_budgets` (line 212)

  - Purpose: Check if performance budgets are met

  - Signature summary: positional=self, profile_stats

  - Async: False, Returns: List[ComplianceViolation]

  - Cross-file communications: none

- Function `ArchitectureValidator.check_threading_compliance` (line 238)

  - Purpose: Check if threading rules are followed

  - Signature summary: positional=self, thread_analysis

  - Async: False, Returns: List[ComplianceViolation]

  - Cross-file communications: none

- Function `ArchitectureValidator.load_blueprint` (line 80)

  - Purpose: Load and parse architecture.yml

  - Signature summary: positional=self

  - Async: False, Returns: bool

  - Cross-file communications:

    - Calls `yaml.safe_load` at line 84 (unresolved)

      - Purpose: No docstring provided

      - Expression: `yaml.safe_load`

- Function `ArchitectureValidator.validate_all` (line 90)

  - Purpose: Run all compliance checks

  - Signature summary: positional=self

  - Async: False, Returns: ComplianceReport

  - Cross-file communications: none

- Function `ComplianceReport.add_violation` (line 32)

  - Purpose: Add a violation and categorize by severity

  - Signature summary: positional=self, violation

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ComplianceReport.format_report` (line 40)

  - Purpose: Format compliance report for display

  - Signature summary: positional=self

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `validate_architecture` (line 281)

  - Purpose: Convenience function to validate architecture

  - Signature summary: positional=repo_path

  - Async: False, Returns: ComplianceReport

  - Cross-file communications: none


## modules/async_interactive.py

- Module: `modules.async_interactive`

- Functions: none

## modules/async_interactive/__init__.py

- Module: `modules.async_interactive`

- Functions: none

## modules/async_interactive/api_requests.py

- Module: `modules.async_interactive.api_requests`

- Function `perform_anthropic_request` (line 10)

  - Purpose: Make request to Anthropic API

  - Signature summary: positional=messages, config, tools, max_tokens

  - Async: True, Returns: Dict

  - Cross-file communications:

    - Calls `modules.async_interactive.message_handling.convert_messages_for_anthropic` at line 30 (ok)

      - Purpose: Convert OpenAI format messages to Anthropic format

      - Expression: `convert_messages_for_anthropic`

    - Calls `httpx.AsyncClient` at line 46 (unresolved)

      - Purpose: No docstring provided

      - Expression: `httpx.AsyncClient`

- Function `perform_google_request` (line 68)

  - Purpose: Make request to Google Gemini API

  - Signature summary: positional=messages, config, tools

  - Async: True, Returns: Dict

  - Cross-file communications:

    - Calls `httpx.AsyncClient` at line 112 (unresolved)

      - Purpose: No docstring provided

      - Expression: `httpx.AsyncClient`


## modules/async_interactive/buffer_system.py

- Module: `modules.async_interactive.buffer_system`

- Function `BufferManager.__init__` (line 126)

  - Purpose: No docstring provided

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `BufferManager.create_stream_buffer` (line 131)

  - Purpose: Create a new stream buffer with given parameters

  - Signature summary: positional=self; kwarg=kwargs

  - Async: False, Returns: StreamBuffer

  - Cross-file communications: none

- Function `BufferManager.interrupt_all` (line 148)

  - Purpose: Interrupt all active buffers

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `BufferManager.set_status_widget` (line 136)

  - Purpose: Set reference to status widget for updates

  - Signature summary: positional=self, widget

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `BufferManager.update_status` (line 140)

  - Purpose: Update status widget if available

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `StreamBuffer.__init__` (line 14)

  - Purpose: Args:

  - Signature summary: positional=self, chars_per_batch, batch_delay_ms

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `asyncio.Queue` at line 20 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.Queue`

- Function `StreamBuffer.add_chunk` (line 43)

  - Purpose: Add text chunk to buffer (called from streaming loop)

  - Signature summary: positional=self, text

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `StreamBuffer.drain_smooth` (line 83)

  - Purpose: Drain buffer with smooth pacing

  - Signature summary: positional=self, write_callback

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.wait_for` at line 98 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.wait_for`

    - Calls `asyncio.sleep` at line 107 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

- Function `StreamBuffer.finish_receiving` (line 51)

  - Purpose: Mark reception complete

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamBuffer.get_elapsed` (line 77)

  - Purpose: Get elapsed time in seconds

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `time.time` at line 81 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

- Function `StreamBuffer.get_status_message` (line 60)

  - Purpose: Get current spinner status message

  - Signature summary: positional=self, spinner_char

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `time.time` at line 65 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

- Function `StreamBuffer.interrupt` (line 55)

  - Purpose: User interrupted with ESC

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamBuffer.start` (line 34)

  - Purpose: Start buffer reception

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `time.time` at line 36 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`


## modules/async_interactive/client.py

- Module: `modules.async_interactive.client`

- Function `create_async_client` (line 8)

  - Purpose: Factory to create AsyncOpenAI client with provider defaults

  - Signature summary: positional=config

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `openai.AsyncOpenAI` at line 20 (unresolved)

      - Purpose: No docstring provided

      - Expression: `AsyncOpenAI`


## modules/async_interactive/core.py

- Module: `modules.async_interactive.core`

- Function `interactive_async` (line 23)

  - Purpose: Async interactive mode with Textual TUI - Main entry point

  - Signature summary: positional=config, session, initial_prompt

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.async_interactive.session.create_session` at line 34 (ok)

      - Purpose: Factory function to create a new session

      - Expression: `create_session`

    - Calls `modules.async_interactive.client.create_async_client` at line 37 (ok)

      - Purpose: Factory to create AsyncOpenAI client with provider defaults

      - Expression: `create_async_client`

    - Calls `modules.async_interactive.permissions.setup_permissions` at line 40 (ok)

      - Purpose: Setup permission manager for the session

      - Expression: `setup_permissions`

    - Calls `modules.tui.core.OpenCLITUI` at line 43 (unresolved)

      - Purpose: No docstring provided

      - Expression: `OpenCLITUI`

    - Calls `modules.async_interactive.ui_handlers.async_write` at line 47 (ok)

      - Purpose: Write to app - direct queue + ALWAYS yield for responsiveness

      - Expression: `async_write`

- Function `run_interactive_async` (line 53)

  - Purpose: Synchronous wrapper for interactive_async

  - Signature summary: positional=config, session, initial_prompt

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `asyncio.run` at line 55 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.run`


## modules/async_interactive/message_handling.py

- Module: `modules.async_interactive.message_handling`

- Function `_flatten_message_content` (line 38)

  - Purpose: Flatten message content to plain text

  - Signature summary: positional=content

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `convert_messages_for_anthropic` (line 58)

  - Purpose: Convert OpenAI format messages to Anthropic format

  - Signature summary: positional=messages

  - Async: False, Returns: Tuple[str, List[Dict]]

  - Cross-file communications: none

- Function `extract_openrouter_policy_error` (line 83)

  - Purpose: Extract policy violation details from OpenRouter errors

  - Signature summary: positional=error

  - Async: False, Returns: Optional[str]

  - Cross-file communications: none

- Function `normalize_tool_call_messages` (line 10)

  - Purpose: Normalize tool call messages to handle different formats

  - Signature summary: positional=messages

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `copy.deepcopy` at line 18 (unresolved)

      - Purpose: No docstring provided

      - Expression: `deepcopy`

    - Calls `json.loads` at line 28 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.loads`

- Function `prepare_messages_with_context` (line 99)

  - Purpose: Prepare messages with additional context like specs and goals

  - Signature summary: positional=messages, config, spec_memory, goal_tracker

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `copy.deepcopy` at line 112 (unresolved)

      - Purpose: No docstring provided

      - Expression: `deepcopy`


## modules/async_interactive/permissions.py

- Module: `modules.async_interactive.permissions`

- Function `setup_permissions` (line 8)

  - Purpose: Setup permission manager for the session

  - Signature summary: positional=session

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path.home` at line 30 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.home`

    - Calls `tool_permissions.ToolPermissionManager` at line 31 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ToolPermissionManager`


## modules/async_interactive/session.py

- Module: `modules.async_interactive.session`

- Function `Session.__init__` (line 15)

  - Purpose: No docstring provided

  - Signature summary: positional=self, model

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `uuid.uuid4` at line 16 (unresolved)

      - Purpose: No docstring provided

      - Expression: `uuid.uuid4`

    - Calls `os.getcwd` at line 19 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.getcwd`

- Function `Session.add` (line 24)

  - Purpose: Add a message to the session

  - Signature summary: positional=self, role, content

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `Session.get_messages` (line 28)

  - Purpose: Get all messages in the session

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `Session.save` (line 32)

  - Purpose: Save session to disk

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path.home` at line 34 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.home`

    - Calls `datetime.datetime.now` at line 43 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

    - Calls `json.dump` at line 47 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dump`

- Function `create_session` (line 50)

  - Purpose: Factory function to create a new session

  - Signature summary: positional=model

  - Async: False, Returns: None

  - Cross-file communications: none


## modules/async_interactive/streaming.py

- Module: `modules.async_interactive.streaming`

- Function `StreamHandler.__init__` (line 16)

  - Purpose: No docstring provided

  - Signature summary: positional=self, buffer_manager

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamHandler.interrupt` (line 200)

  - Purpose: Set interrupt flag to stop streaming

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamHandler.reset` (line 204)

  - Purpose: Reset interrupt flag

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamHandler.stream_anthropic` (line 107)

  - Purpose: Stream response from Anthropic API

  - Signature summary: positional=self, messages, config, tools

  - Async: True, Returns: AsyncIterator[Dict]

  - Cross-file communications:

    - Calls `modules.async_interactive.message_handling.convert_messages_for_anthropic` at line 128 (ok)

      - Purpose: Convert OpenAI format messages to Anthropic format

      - Expression: `convert_messages_for_anthropic`

    - Calls `httpx.AsyncClient` at line 149 (unresolved)

      - Purpose: No docstring provided

      - Expression: `httpx.AsyncClient`

    - Calls `json.loads` at line 175 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.loads`

- Function `StreamHandler.stream_openrouter` (line 20)

  - Purpose: Stream response from OpenRouter API

  - Signature summary: positional=self, messages, config, tools

  - Async: True, Returns: AsyncIterator[Dict]

  - Cross-file communications:

    - Calls `httpx.AsyncClient` at line 56 (unresolved)

      - Purpose: No docstring provided

      - Expression: `httpx.AsyncClient`

    - Calls `modules.async_interactive.message_handling.extract_openrouter_policy_error` at line 67 (ok)

      - Purpose: Extract policy violation details from OpenRouter errors

      - Expression: `extract_openrouter_policy_error`

    - Calls `json.loads` at line 86 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.loads`


## modules/async_interactive/tool_integration.py

- Module: `modules.async_interactive.tool_integration`

- Function `ToolExecutor.__init__` (line 16)

  - Purpose: No docstring provided

  - Signature summary: positional=self, app, session, permission_manager

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `modules.async_interactive.streaming.StreamHandler` at line 20 (unresolved)

      - Purpose: No docstring provided

      - Expression: `StreamHandler`

- Function `ToolExecutor._find_tool_registration` (line 110)

  - Purpose: Find tool registration by name

  - Signature summary: positional=self, tool_name

  - Async: False, Returns: Optional[Dict[str, Any]]

  - Cross-file communications: none

- Function `ToolExecutor.execute_multiple_tools` (line 117)

  - Purpose: Execute multiple tool calls in sequence

  - Signature summary: positional=self, tool_calls, stream_display

  - Async: True, Returns: List[Dict[str, Any]]

  - Cross-file communications:

    - Calls `asyncio.sleep` at line 135 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

- Function `ToolExecutor.execute_tool_call` (line 22)

  - Purpose: Execute a tool call with permission checking and streaming output

  - Signature summary: positional=self, tool_call, stream_display

  - Async: True, Returns: Dict[str, Any]

  - Cross-file communications:

    - Calls `json.loads` at line 44 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.loads`

    - Calls `modules.async_interactive.tools.execute_tool_async` at line 65 (ok)

      - Purpose: Execute a tool asynchronously

      - Expression: `execute_tool_async`

- Function `ToolExecutor.set_context` (line 139)

  - Purpose: Update execution context

  - Signature summary: positional=self, app, session, permission_manager

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `get_tool_executor` (line 152)

  - Purpose: Get or create global tool executor instance

  - Signature summary: positional=app, session, permission_manager

  - Async: False, Returns: ToolExecutor

  - Cross-file communications: none


## modules/async_interactive/tools.py

- Module: `modules.async_interactive.tools`

- Function `execute_bash` (line 90)

  - Purpose: Execute bash command synchronously

  - Signature summary: positional=command, description

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `subprocess.run` at line 93 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `execute_bash_async` (line 63)

  - Purpose: Execute bash command asynchronously

  - Signature summary: positional=command, description, timeout, current_dir, debug

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.create_subprocess_shell` at line 66 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.create_subprocess_shell`

    - Calls `asyncio.wait_for` at line 73 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.wait_for`

- Function `execute_edit` (line 44)

  - Purpose: Execute Edit tool

  - Signature summary: positional=file_path, old_string, new_string

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `execute_glob` (line 110)

  - Purpose: Execute Glob tool

  - Signature summary: positional=pattern

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `glob.glob` at line 113 (unresolved)

      - Purpose: No docstring provided

      - Expression: `glob.glob`

- Function `execute_grep` (line 125)

  - Purpose: Execute Grep tool synchronously

  - Signature summary: positional=pattern

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `execute_grep_async` (line 119)

  - Purpose: Execute Grep tool asynchronously

  - Signature summary: positional=pattern, timeout

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `execute_read` (line 23)

  - Purpose: Execute Read tool

  - Signature summary: positional=file_path

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `execute_tool` (line 153)

  - Purpose: Execute a tool synchronously

  - Signature summary: positional=name, args, permission_manager, current_dir, app

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `execute_tool_async` (line 131)

  - Purpose: Execute a tool asynchronously

  - Signature summary: positional=name, args, permission_manager, current_dir, app

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `execute_write` (line 33)

  - Purpose: Execute Write tool

  - Signature summary: positional=file_path, content

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path` at line 36 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`


## modules/async_interactive/ui_handlers.py

- Module: `modules.async_interactive.ui_handlers`

- Function `async_write` (line 8)

  - Purpose: Write to app - direct queue + ALWAYS yield for responsiveness

  - Signature summary: positional=app, text, end

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.sleep` at line 21 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

- Function `write_markdown_response` (line 24)

  - Purpose: Write a complete markdown response (replaces plain text streaming)

  - Signature summary: positional=app, markdown_text

  - Async: True, Returns: None

  - Cross-file communications: none


## modules/async_permissions.py

- Module: `modules.async_permissions`

- Function `AsyncPermissionHandler.__init__` (line 24)

  - Purpose: No docstring provided

  - Signature summary: positional=self, permission_manager, app

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `AsyncPermissionHandler._generate_prompt_data` (line 119)

  - Purpose: Generate permission prompt data for the tool

  - Signature summary: positional=self, tool_name, args, current_dir

  - Async: False, Returns: Optional[dict]

  - Cross-file communications:

    - Calls `permission_prompt.PermissionTemplates.file_edit` at line 128 (unresolved)

      - Purpose: No docstring provided

      - Expression: `PermissionTemplates.file_edit`

    - Calls `permission_prompt.PermissionTemplates.file_write` at line 135 (unresolved)

      - Purpose: No docstring provided

      - Expression: `PermissionTemplates.file_write`

    - Calls `permission_prompt.PermissionTemplates.bash_command` at line 141 (unresolved)

      - Purpose: No docstring provided

      - Expression: `PermissionTemplates.bash_command`

    - Calls `permission_prompt.PermissionTemplates.webfetch` at line 147 (unresolved)

      - Purpose: No docstring provided

      - Expression: `PermissionTemplates.webfetch`

    - Calls `permission_prompt.PermissionTemplates.configure_headers` at line 152 (unresolved)

      - Purpose: No docstring provided

      - Expression: `PermissionTemplates.configure_headers`

    - Calls `permission_prompt.PermissionTemplates.code_refactoring` at line 161 (unresolved)

      - Purpose: No docstring provided

      - Expression: `PermissionTemplates.code_refactoring`

- Function `AsyncPermissionHandler._show_permission_prompt` (line 53)

  - Purpose: Show permission prompt in TUI and wait for response

  - Signature summary: positional=self, tool_name, args, risk_level, current_dir

  - Async: True, Returns: Tuple[bool, str]

  - Cross-file communications:

    - Calls `asyncio.Event` at line 74 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.Event`

    - Calls `asyncio.wait_for` at line 83 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.wait_for`

- Function `AsyncPermissionHandler.check_and_prompt` (line 30)

  - Purpose: Check if tool execution requires permission and prompt if needed

  - Signature summary: positional=self, tool_name, args, current_dir

  - Async: True, Returns: Tuple[bool, str]

  - Cross-file communications: none

- Function `AsyncPermissionHandler.handle_response` (line 188)

  - Purpose: Handle permission response from UI

  - Signature summary: positional=self, response

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `get_global_handler` (line 216)

  - Purpose: Get the global permission handler

  - Signature summary: (no parameters)

  - Async: False, Returns: Optional[AsyncPermissionHandler]

  - Cross-file communications: none

- Function `set_global_handler` (line 210)

  - Purpose: Set the global permission handler

  - Signature summary: positional=handler

  - Async: False, Returns: None

  - Cross-file communications: none


## modules/async_runner.py

- Module: `modules.async_runner`

- Function `AsyncExecutionRunner.run_async` (line 15)

  - Purpose: Execute function asynchronously with timeout

  - Signature summary: positional=func, timeout; vararg=args; kwarg=kwargs

  - Async: True, Returns: Any

  - Cross-file communications:

    - Calls `asyncio.iscoroutinefunction` at line 38 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.iscoroutinefunction`

    - Calls `asyncio.wait_for` at line 62 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.wait_for`

    - Calls `asyncio.to_thread` at line 63 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.to_thread`

    - Calls `asyncio.TimeoutError` at line 70 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.TimeoutError`

    - Calls `traceback.print_exc` at line 74 (unresolved)

      - Purpose: No docstring provided

      - Expression: `traceback.print_exc`

- Function `AsyncExecutionRunner.run_bash_async` (line 78)

  - Purpose: Non-blocking bash execution with timeout

  - Signature summary: positional=command, timeout, description

  - Async: True, Returns: str

  - Cross-file communications:

    - Calls `asyncio.create_subprocess_shell` at line 95 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.create_subprocess_shell`

    - Calls `asyncio.wait_for` at line 101 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.wait_for`

    - Calls `asyncio.TimeoutError` at line 113 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.TimeoutError`


## modules/auto_refactor.py

- Module: `modules.auto_refactor`

- Function `AutoRefactorConfig.__post_init__` (line 29)

  - Purpose: No docstring provided

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `AutoRefactorManager.__init__` (line 81)

  - Purpose: No docstring provided

  - Signature summary: positional=self, repo_path, permission_handler

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path` at line 82 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

    - Calls `modules.refactor_executor.RefactoringExecutor` at line 84 (unresolved)

      - Purpose: No docstring provided

      - Expression: `RefactoringExecutor`

    - Calls `threading.Lock` at line 91 (unresolved)

      - Purpose: No docstring provided

      - Expression: `threading.Lock`

- Function `AutoRefactorManager._on_refactor_needed` (line 164)

  - Purpose: Called when a file needs refactoring

  - Signature summary: positional=self, file_path, line_count

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `AutoRefactorManager._process_refactoring` (line 188)

  - Purpose: Process a file that needs refactoring

  - Signature summary: positional=self, file_path, line_count

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `modules.code_analyzer.CodeAnalyzer` at line 192 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CodeAnalyzer`

    - Calls `pathlib.Path` at line 211 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

    - Calls `modules.refactor_executor.RefactoringPlan` at line 213 (unresolved)

      - Purpose: No docstring provided

      - Expression: `RefactoringPlan`

    - Calls `asyncio.get_event_loop` at line 251 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.get_event_loop`

    - Calls `asyncio.run_coroutine_threadsafe` at line 254 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.run_coroutine_threadsafe`

    - Calls `traceback.print_exc` at line 294 (unresolved)

      - Purpose: No docstring provided

      - Expression: `traceback.print_exc`

- Function `AutoRefactorManager._refactor_worker` (line 173)

  - Purpose: Worker thread that processes refactoring queue

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `time.sleep` at line 186 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.sleep`

- Function `AutoRefactorManager.cleanup` (line 347)

  - Purpose: Clean up resources

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `AutoRefactorManager.start` (line 93)

  - Purpose: Start file watching and auto-refactoring

  - Signature summary: positional=self, config

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `watchdog.observers.Observer` at line 109 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Observer`

    - Calls `threading.Thread` at line 120 (unresolved)

      - Purpose: No docstring provided

      - Expression: `threading.Thread`

- Function `AutoRefactorManager.status` (line 150)

  - Purpose: Get current status of auto-refactoring

  - Signature summary: positional=self

  - Async: False, Returns: Dict

  - Cross-file communications: none

- Function `AutoRefactorManager.stop` (line 131)

  - Purpose: Stop file watching and auto-refactoring

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `AutoRefactorManager.suggest_split` (line 296)

  - Purpose: Analyze a file and suggest how to split it

  - Signature summary: positional=self, file_path

  - Async: False, Returns: Dict

  - Cross-file communications:

    - Calls `pathlib.Path` at line 304 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

    - Calls `modules.code_analyzer.CodeAnalyzer` at line 308 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CodeAnalyzer`

- Function `RefactoringFileHandler.__init__` (line 39)

  - Purpose: No docstring provided

  - Signature summary: positional=self, config, on_refactor_needed

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `RefactoringFileHandler.on_modified` (line 45)

  - Purpose: Called when a file is modified

  - Signature summary: positional=self, event

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `time.time` at line 59 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

- Function `get_auto_refactor_manager` (line 357)

  - Purpose: Get or create global auto-refactor manager instance

  - Signature summary: (no parameters)

  - Async: False, Returns: AutoRefactorManager

  - Cross-file communications: none


## modules/buffer_widget.py

- Module: `modules.buffer_widget`

- Function `BufferStatusWidget.__init__` (line 59)

  - Purpose: No docstring provided

  - Signature summary: positional=self; vararg=args; kwarg=kwargs

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `random.choice` at line 61 (unresolved)

      - Purpose: No docstring provided

      - Expression: `random.choice`

- Function `BufferStatusWidget._render_status` (line 72)

  - Purpose: Render the current status with spinner and tip - Frontier colors

  - Signature summary: positional=self

  - Async: False, Returns: Text

  - Cross-file communications:

    - Calls `rich.text.Text` at line 74 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

    - Calls `rich.style.Style` at line 93 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Style`

- Function `BufferStatusWidget._update_animation` (line 67)

  - Purpose: Update spinner animation frame

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `BufferStatusWidget.mark_interrupted` (line 102)

  - Purpose: Mark as interrupted by user

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `BufferStatusWidget.mark_rendering` (line 107)

  - Purpose: Mark as rendering (receiving complete)

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `BufferStatusWidget.on_mount` (line 63)

  - Purpose: Start animation when widget mounts

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `BufferStatusWidget.update_progress` (line 97)

  - Purpose: Update progress metrics

  - Signature summary: positional=self, tokens, elapsed

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `BufferStatusWidget.watch_elapsed_seconds` (line 115)

  - Purpose: React to elapsed time changes

  - Signature summary: positional=self, new_value

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `BufferStatusWidget.watch_is_interrupted` (line 123)

  - Purpose: React to interrupt state changes

  - Signature summary: positional=self, new_value

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `BufferStatusWidget.watch_is_receiving` (line 119)

  - Purpose: React to receiving state changes

  - Signature summary: positional=self, new_value

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `BufferStatusWidget.watch_tokens_received` (line 111)

  - Purpose: React to token count changes

  - Signature summary: positional=self, new_value

  - Async: False, Returns: None

  - Cross-file communications: none


## modules/cache_manager.py

- Module: `modules.cache_manager`

- Function `CacheManager.__init__` (line 18)

  - Purpose: Initialize cache manager

  - Signature summary: positional=self, base_dir

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path` at line 29 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

- Function `CacheManager.check_stale_cache` (line 119)

  - Purpose: Check if a module's .pyc file is stale (older than .py source)

  - Signature summary: positional=self, module_name

  - Async: False, Returns: Optional[dict]

  - Cross-file communications:

    - Calls `pathlib.Path` at line 138 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

- Function `CacheManager.clear_cache` (line 31)

  - Purpose: Clear all .pyc files and __pycache__ directories

  - Signature summary: positional=self, verbose

  - Async: False, Returns: dict

  - Cross-file communications:

    - Calls `shutil.rmtree` at line 58 (unresolved)

      - Purpose: No docstring provided

      - Expression: `shutil.rmtree`

- Function `CacheManager.disable_dev_mode` (line 190)

  - Purpose: Disable development mode - allows .pyc creation

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `CacheManager.enable_dev_mode` (line 181)

  - Purpose: Enable development mode - prevents .pyc creation

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `CacheManager.find_all_stale_cache` (line 164)

  - Purpose: Find all modules with stale .pyc cache

  - Signature summary: positional=self

  - Async: False, Returns: List[dict]

  - Cross-file communications:

    - Calls `sys.modules.keys` at line 173 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.modules.keys`

- Function `CacheManager.reload_modules` (line 73)

  - Purpose: Reload Python modules that match patterns

  - Signature summary: positional=self, module_patterns

  - Async: False, Returns: dict

  - Cross-file communications:

    - Calls `sys.modules.keys` at line 98 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.modules.keys`

    - Calls `importlib.reload` at line 105 (unresolved)

      - Purpose: No docstring provided

      - Expression: `importlib.reload`

- Function `clear_opencli_cache` (line 206)

  - Purpose: Convenience function to clear OpenCLI cache

  - Signature summary: positional=verbose

  - Async: False, Returns: dict

  - Cross-file communications: none

- Function `get_cache_manager` (line 199)

  - Purpose: Get singleton cache manager instance

  - Signature summary: (no parameters)

  - Async: False, Returns: CacheManager

  - Cross-file communications: none


## modules/code_analyzer.py

- Module: `modules.code_analyzer`

- Function `CodeAnalyzer.__init__` (line 40)

  - Purpose: No docstring provided

  - Signature summary: positional=self, file_path

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path` at line 41 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

    - Calls `networkx.DiGraph` at line 43 (unresolved)

      - Purpose: No docstring provided

      - Expression: `nx.DiGraph`

    - Calls `networkx.Graph` at line 44 (unresolved)

      - Purpose: No docstring provided

      - Expression: `nx.Graph`

- Function `CodeAnalyzer._build_call_graph` (line 106)

  - Purpose: Build directed graph of function calls

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `CodeAnalyzer._build_data_graph` (line 116)

  - Purpose: Build undirected graph of shared data dependencies

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `CodeAnalyzer._calculate_max_nesting` (line 278)

  - Purpose: Calculate maximum nesting depth in file

  - Signature summary: positional=self

  - Async: False, Returns: int

  - Cross-file communications:

    - Calls `ast.parse` at line 282 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ast.parse`

- Function `CodeAnalyzer._calculate_max_nesting.visit_node` (line 286)

  - Purpose: No docstring provided

  - Signature summary: positional=node, depth

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `ast.iter_child_nodes` at line 290 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ast.iter_child_nodes`

- Function `CodeAnalyzer._extract_functions` (line 65)

  - Purpose: Extract all function definitions and their metadata

  - Signature summary: positional=self, tree

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `ast.walk` at line 76 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ast.walk`

- Function `CodeAnalyzer._generate_rationale` (line 243)

  - Purpose: Generate human-readable rationale for extraction

  - Signature summary: positional=self, component, cohesion, coupling, total_lines

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `CodeAnalyzer._suggest_module_name` (line 216)

  - Purpose: Suggest a module name based on function names

  - Signature summary: positional=self, functions

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `CodeAnalyzer.analyze` (line 46)

  - Purpose: Analyze the file and build graphs

  - Signature summary: positional=self

  - Async: False, Returns: bool

  - Cross-file communications:

    - Calls `ast.parse` at line 52 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ast.parse`

- Function `CodeAnalyzer.get_file_stats` (line 265)

  - Purpose: Get statistics about the file

  - Signature summary: positional=self

  - Async: False, Returns: Dict[str, int]

  - Cross-file communications: none

- Function `CodeAnalyzer.identify_clusters` (line 137)

  - Purpose: Identify clusters of functions that could be extracted

  - Signature summary: positional=self, min_cluster_size, min_lines

  - Async: False, Returns: List[FunctionCluster]

  - Cross-file communications:

    - Calls `networkx.Graph` at line 144 (unresolved)

      - Purpose: No docstring provided

      - Expression: `nx.Graph`

    - Calls `networkx.connected_components` at line 159 (unresolved)

      - Purpose: No docstring provided

      - Expression: `nx.connected_components`

- Function `analyze_file` (line 303)

  - Purpose: Convenience function to analyze a file

  - Signature summary: positional=file_path

  - Async: False, Returns: Tuple[CodeAnalyzer, List[FunctionCluster]]

  - Cross-file communications: none


## modules/color_manager.py

- Module: `modules.color_manager`

- Function `ColorManager.__new__` (line 32)

  - Purpose: Singleton pattern

  - Signature summary: positional=cls

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ColorManager._rgb_to_ansi` (line 126)

  - Purpose: Convert RGB color to nearest ANSI 256 color

  - Signature summary: positional=rgb_color

  - Async: False, Returns: RichColor

  - Cross-file communications:

    - Calls `rich.color.Color.from_rgb` at line 134 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Color.from_rgb`

- Function `ColorManager.create_style` (line 103)

  - Purpose: Create Rich Style with color mode processing

  - Signature summary: positional=cls, color, bgcolor; kwarg=kwargs

  - Async: False, Returns: RichStyle

  - Cross-file communications:

    - Calls `rich.style.Style` at line 119 (unresolved)

      - Purpose: No docstring provided

      - Expression: `RichStyle`

- Function `ColorManager.get_mode` (line 44)

  - Purpose: Get current color mode

  - Signature summary: positional=cls

  - Async: False, Returns: ColorMode

  - Cross-file communications: none

- Function `ColorManager.process_background` (line 59)

  - Purpose: Process background color based on current mode

  - Signature summary: positional=cls, bgcolor

  - Async: False, Returns: Optional[RichColor]

  - Cross-file communications: none

- Function `ColorManager.process_foreground` (line 85)

  - Purpose: Process foreground color based on current mode

  - Signature summary: positional=cls, color

  - Async: False, Returns: Optional[RichColor]

  - Cross-file communications: none

- Function `ColorManager.set_mode` (line 39)

  - Purpose: Set global color mode

  - Signature summary: positional=cls, mode

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ColorManager.should_force_ansi` (line 54)

  - Purpose: Check if all colors should be ANSI

  - Signature summary: positional=cls

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `ColorManager.should_strip_background` (line 49)

  - Purpose: Check if backgrounds should be stripped (ANSI mode)

  - Signature summary: positional=cls

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `configure_color_mode` (line 141)

  - Purpose: Configure color mode from TUI config

  - Signature summary: positional=config

  - Async: False, Returns: None

  - Cross-file communications: none


## modules/command_executor.py

- Module: `modules.command_executor`

- Function `CommandExecution.__init__` (line 304)

  - Purpose: No docstring provided

  - Signature summary: positional=self, command, permission, steps, app, session

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `CommandExecution.execute_with_live_progress` (line 368)

  - Purpose: Execute command with live progress updates using permission buffer manager

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `permission_buffer_manager.get_permission_buffer_manager` at line 372 (unresolved)

      - Purpose: No docstring provided

      - Expression: `get_permission_buffer_manager`

    - Calls `asyncio.sleep` at line 462 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

- Function `CommandExecution.show_initial_permission_prompt` (line 320)

  - Purpose: Show initial permission prompt for command

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `permission_buffer_manager.get_permission_buffer_manager` at line 348 (unresolved)

      - Purpose: No docstring provided

      - Expression: `get_permission_buffer_manager`

- Function `UnifiedCommandExecutor.__init__` (line 80)

  - Purpose: No docstring provided

  - Signature summary: positional=self, app, session

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `UnifiedCommandExecutor._clear_statusline_context` (line 286)

  - Purpose: Clear statusline indicator for category

  - Signature summary: positional=self, category

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `UnifiedCommandExecutor._register_default_commands` (line 89)

  - Purpose: Register default command permissions

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `UnifiedCommandExecutor._update_statusline_context` (line 264)

  - Purpose: Update statusline with current command context

  - Signature summary: positional=self, category, status

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `UnifiedCommandExecutor.execute_command` (line 192)

  - Purpose: Execute a command with permission-first flow

  - Signature summary: positional=self, command, steps, on_complete

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.sleep` at line 260 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

- Function `UnifiedCommandExecutor.get_permission` (line 179)

  - Purpose: Get permission info for a command

  - Signature summary: positional=self, command

  - Async: False, Returns: Optional[CommandPermission]

  - Cross-file communications: none

- Function `UnifiedCommandExecutor.register_command` (line 175)

  - Purpose: Register a new command with permissions

  - Signature summary: positional=self, permission

  - Async: False, Returns: None

  - Cross-file communications: none


## modules/command_registry.py

- Module: `modules.command_registry`

- Function `CommandRegistry.__init__` (line 12)

  - Purpose: Initialize command registry.

  - Signature summary: positional=self, config_dir, executor

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path.home` at line 19 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.home`

- Function `CommandRegistry._load_permissions` (line 71)

  - Purpose: Load command permissions from file

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.load` at line 84 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

- Function `CommandRegistry._save_permissions` (line 108)

  - Purpose: Save command permissions to file

  - Signature summary: positional=self, permissions

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.dump` at line 112 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dump`

- Function `CommandRegistry._save_usage_stats` (line 429)

  - Purpose: Persist usage statistics to file.

  - Signature summary: positional=self, stats

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.dump` at line 440 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dump`

- Function `CommandRegistry._score_command` (line 362)

  - Purpose: Calculate search score for a command.

  - Signature summary: positional=self, cmd, info, query, usage_count

  - Async: False, Returns: int

  - Cross-file communications: none

- Function `CommandRegistry.disable_command` (line 141)

  - Purpose: Disable a command

  - Signature summary: positional=self, command

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `CommandRegistry.enable_command` (line 129)

  - Purpose: Enable a command

  - Signature summary: positional=self, command

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `CommandRegistry.get_all_commands` (line 176)

  - Purpose: Get all available commands with metadata

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `CommandRegistry.get_command_info` (line 180)

  - Purpose: Get information about a specific command

  - Signature summary: positional=self, command

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `CommandRegistry.get_enabled_commands` (line 157)

  - Purpose: Get list of currently enabled commands

  - Signature summary: positional=self, feature_flags

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `CommandRegistry.get_most_used_commands` (line 468)

  - Purpose: Get most frequently used commands.

  - Signature summary: positional=self, limit

  - Async: False, Returns: List[Dict]

  - Cross-file communications: none

- Function `CommandRegistry.get_runtime_commands` (line 32)

  - Purpose: Get commands from runtime registry or fallback to static definitions.

  - Signature summary: positional=self

  - Async: False, Returns: Dict[str, Dict]

  - Cross-file communications: none

- Function `CommandRegistry.get_usage_stats` (line 414)

  - Purpose: Load command usage statistics from file.

  - Signature summary: positional=self

  - Async: False, Returns: Dict[str, int]

  - Cross-file communications:

    - Calls `json.load` at line 425 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

- Function `CommandRegistry.interactive_permission_setup` (line 187)

  - Purpose: Interactive setup to enable/disable commands one by one

  - Signature summary: positional=self, feature_flags

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `CommandRegistry.is_enabled` (line 116)

  - Purpose: Check if a command is enabled

  - Signature summary: positional=self, command

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `CommandRegistry.record_usage` (line 445)

  - Purpose: Increment usage counter for a command.

  - Signature summary: positional=self, command

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `CommandRegistry.search_commands` (line 257)

  - Purpose: Search commands with priority-based ranking.

  - Signature summary: positional=self, query, feature_flags, limit

  - Async: False, Returns: List[Dict]

  - Cross-file communications: none


## modules/command_registry/__init__.py

- Module: `modules.command_registry`

- Functions: none

## modules/command_registry/definitions.py

- Module: `modules.command_registry.definitions`

- Function `get_command_categories` (line 232)

  - Purpose: Get ordered command categories.

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `get_commands_by_category` (line 236)

  - Purpose: Get all commands in a specific category.

  - Signature summary: positional=category

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `get_commands_with_subcommands` (line 252)

  - Purpose: Get commands that have subcommands defined.

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `get_core_commands` (line 243)

  - Purpose: Get essential commands that should always be available.

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `get_feature_dependent_commands` (line 259)

  - Purpose: Get commands that require specific features.

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `get_static_commands` (line 228)

  - Purpose: Get static command definitions.

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `merge_runtime_commands` (line 285)

  - Purpose: Merge runtime commands with static definitions.

  - Signature summary: positional=runtime_commands

  - Async: False, Returns: dict

  - Cross-file communications: none

- Function `validate_command_definition` (line 266)

  - Purpose: Validate a command definition structure.

  - Signature summary: positional=cmd_name, cmd_info

  - Async: False, Returns: bool

  - Cross-file communications: none


## modules/command_router.py

- Module: `modules.command_router`

- Function `CommandRouter.__init__` (line 40)

  - Purpose: No docstring provided

  - Signature summary: positional=self, app, session

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `modules.execution.executor.get_executor` at line 45 (ok)

      - Purpose: Get or create global execution system

      - Expression: `get_executor`

- Function `CommandRouter._initialize_registrations` (line 65)

  - Purpose: Load all registrations into ExecutionSystem with SDK enforcement - ASYNC

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `sys.stderr.write` at line 164 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.write`

    - Calls `time.strftime` at line 74 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.strftime`

    - Calls `sys.stderr.flush` at line 165 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.flush`

    - Calls `time.time` at line 116 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

    - Calls `modules.commands.registry.register_all` at line 114 (ok)

      - Purpose: ONE registration function for EVERYTHING

      - Expression: `register_all`

    - Calls `traceback.print_exc` at line 137 (unresolved)

      - Purpose: No docstring provided

      - Expression: `traceback.print_exc`

    - Calls `modules.sdk.get_enforcement` at line 147 (unresolved)

      - Purpose: No docstring provided

      - Expression: `get_enforcement`

- Function `CommandRouter.get_active_command_count` (line 61)

  - Purpose: Get count of pending commands during initialization

  - Signature summary: positional=self

  - Async: False, Returns: int

  - Cross-file communications: none

- Function `CommandRouter.get_available_commands` (line 221)

  - Purpose: Get all registered commands

  - Signature summary: positional=self

  - Async: False, Returns: list

  - Cross-file communications: none

- Function `CommandRouter.get_sdk_state` (line 57)

  - Purpose: Get current SDK initialization state

  - Signature summary: positional=self

  - Async: False, Returns: SDKState

  - Cross-file communications: none

- Function `CommandRouter.is_registered` (line 216)

  - Purpose: Check if command is registered

  - Signature summary: positional=self, command

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `CommandRouter.route_command` (line 167)

  - Purpose: Route command through ExecutionSystem

  - Signature summary: positional=self, command, args

  - Async: True, Returns: bool

  - Cross-file communications:

    - Calls `traceback.print_exc` at line 212 (unresolved)

      - Purpose: No docstring provided

      - Expression: `traceback.print_exc`

- Function `route_command_unified` (line 226)

  - Purpose: Global routing function for async_interactive.py

  - Signature summary: positional=app, session, command, args

  - Async: True, Returns: bool

  - Cross-file communications:

    - Calls `sys.stderr.write` at line 283 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.write`

    - Calls `sys.stderr.flush` at line 284 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.flush`

    - Calls `asyncio.create_task` at line 271 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.create_task`

    - Calls `modules.sdk.show_startup_status` at line 271 (unresolved)

      - Purpose: No docstring provided

      - Expression: `show_startup_status`


## modules/command_suggestions.py

- Module: `modules.command_suggestions`

- Function `CommandMatch.__repr__` (line 53)

  - Purpose: No docstring provided

  - Signature summary: positional=self

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `CommandSuggestionBuffer.CommandSelected.__init__` (line 91)

  - Purpose: No docstring provided

  - Signature summary: positional=self, command, command_match

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `CommandSuggestionBuffer.ShowSuggestions.__init__` (line 79)

  - Purpose: No docstring provided

  - Signature summary: positional=self, query

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `CommandSuggestionBuffer.UpdateSuggestions.__init__` (line 85)

  - Purpose: No docstring provided

  - Signature summary: positional=self, query

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `CommandSuggestionBuffer.__init__` (line 100)

  - Purpose: Initialize the command suggestion buffer.

  - Signature summary: positional=self; kwonly=name, id, classes

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `CommandSuggestionBuffer.clear` (line 238)

  - Purpose: Clear all suggestions and reset state.

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `CommandSuggestionBuffer.get_selected_command` (line 216)

  - Purpose: Get the currently selected command match.

  - Signature summary: positional=self

  - Async: False, Returns: Optional[CommandMatch]

  - Cross-file communications: none

- Function `CommandSuggestionBuffer.move_selection_down` (line 211)

  - Purpose: Move selection down one item (with wrapping).

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `CommandSuggestionBuffer.move_selection_up` (line 206)

  - Purpose: Move selection up one item (with wrapping).

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `CommandSuggestionBuffer.render` (line 120)

  - Purpose: Render the suggestion buffer with Frontier colors.

  - Signature summary: positional=self

  - Async: False, Returns: RenderableType

  - Cross-file communications:

    - Calls `rich.text.Text` at line 140 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

- Function `CommandSuggestionBuffer.update_suggestions` (line 226)

  - Purpose: Update the suggestion list and reset selection.

  - Signature summary: positional=self, new_suggestions, query

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `check_command_health` (line 20)

  - Purpose: Check if a command is fully integrated with SDK and permission system.

  - Signature summary: positional=command_name, registry

  - Async: False, Returns: bool

  - Cross-file communications: none


## modules/commands/__init__.py

- Module: `modules.commands`

- Functions: none

## modules/commands/agent_commands.py

- Module: `modules.commands.agent_commands`

- Function `_load_agent_manager` (line 17)

  - Purpose: Best-effort AgentManager creation (mirrors default config path).

  - Signature summary: positional=session

  - Async: False, Returns: Optional[AgentManager]

  - Cross-file communications:

    - Calls `pathlib.Path.home` at line 21 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.home`

    - Calls `modules.agent_manager.AgentManager` at line 24 (unresolved)

      - Purpose: No docstring provided

      - Expression: `AgentManager`

    - Calls `pathlib.Path` at line 24 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

- Function `agent_architect` (line 172)

  - Purpose: No docstring provided

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `agent_assistant` (line 148)

  - Purpose: No docstring provided

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `agent_debugger` (line 152)

  - Purpose: No docstring provided

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `agent_documenter` (line 168)

  - Purpose: No docstring provided

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `agent_main` (line 139)

  - Purpose: Handle `/agent` with optional argument inside context.

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `agent_refactor` (line 160)

  - Purpose: No docstring provided

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `agent_reviewer` (line 156)

  - Purpose: No docstring provided

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `agent_tester` (line 164)

  - Purpose: No docstring provided

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `list_agents` (line 30)

  - Purpose: Show all available agents with their status - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_info_command_prompt` at line 46 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_info_command_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 57 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

    - Calls `pathlib.Path.cwd` at line 77 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.cwd`

- Function `set_agent` (line 91)

  - Purpose: Shared helper to switch the active agent - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session, agent_name

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_configuration_prompt` at line 120 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_configuration_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 127 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`


## modules/commands/api_commands.py

- Module: `modules.commands.api_commands`

- Functions: none

## modules/commands/basic_commands.py

- Module: `modules.commands.basic_commands`

- Function `_feature_flags` (line 21)

  - Purpose: Derive feature flags from the current session when possible.

  - Signature summary: positional=session

  - Async: False, Returns: Dict[str, bool]

  - Cross-file communications: none

- Function `clear_history` (line 173)

  - Purpose: Clear chat history - PERMISSION BUFFER INTEGRATED (DESTRUCTIVE)

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_destructive_command_prompt` at line 189 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_destructive_command_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 197 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

- Function `exit_session` (line 399)

  - Purpose: Exit the TUI application - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_destructive_command_prompt` at line 414 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_destructive_command_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 422 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

    - Calls `asyncio.sleep` at line 439 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

- Function `list_background_tasks` (line 221)

  - Purpose: Show background tasks tracked on the session - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_info_command_prompt` at line 230 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_info_command_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 240 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

- Function `show_command_overview` (line 260)

  - Purpose: Summarize enabled/disabled commands for the user - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.command_registry.CommandRegistry` at line 264 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandRegistry`

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_info_command_prompt` at line 273 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_info_command_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 284 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

    - Calls `pathlib.Path.cwd` at line 306 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.cwd`

- Function `show_help` (line 45)

  - Purpose: Display categorized command overview - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.command_registry.CommandRegistry` at line 49 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandRegistry`

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_info_command_prompt` at line 71 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_info_command_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 78 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

    - Calls `pathlib.Path.cwd` at line 96 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.cwd`

- Function `show_permissions` (line 322)

  - Purpose: Display stored permission choices for commands and tools - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.execution.permission_manager.PermissionManager` at line 326 (unresolved)

      - Purpose: No docstring provided

      - Expression: `PermissionManager`

    - Calls `modules.tool_permissions.ToolPermissionManager` at line 327 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ToolPermissionManager`

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_info_command_prompt` at line 336 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_info_command_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 347 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

    - Calls `pathlib.Path.cwd` at line 377 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.cwd`

- Function `show_status` (line 108)

  - Purpose: Show current session metadata - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path.cwd` at line 159 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.cwd`

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_info_command_prompt` at line 132 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_info_command_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 139 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

    - Calls `datetime.datetime.utcnow` at line 169 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.utcnow`


## modules/commands/command_router.py

- Module: `modules.commands.command_router`

- Function `CommandRouter.__init__` (line 27)

  - Purpose: No docstring provided

  - Signature summary: positional=self, app, session

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `modules.execution.executor.get_executor` at line 32 (ok)

      - Purpose: Get or create global execution system

      - Expression: `get_executor`

- Function `CommandRouter._initialize_registrations` (line 38)

  - Purpose: Load all registrations into ExecutionSystem with SDK enforcement - ASYNC

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.registry.register_all` at line 65 (ok)

      - Purpose: ONE registration function for EVERYTHING

      - Expression: `register_all`

    - Calls `modules.sdk.get_enforcement` at line 74 (unresolved)

      - Purpose: No docstring provided

      - Expression: `get_enforcement`

- Function `CommandRouter.get_available_commands` (line 151)

  - Purpose: Get all registered commands

  - Signature summary: positional=self

  - Async: False, Returns: list

  - Cross-file communications: none

- Function `CommandRouter.is_registered` (line 146)

  - Purpose: Check if command is registered

  - Signature summary: positional=self, command

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `CommandRouter.route_command` (line 97)

  - Purpose: Route command through ExecutionSystem

  - Signature summary: positional=self, command, args

  - Async: True, Returns: bool

  - Cross-file communications:

    - Calls `traceback.print_exc` at line 142 (unresolved)

      - Purpose: No docstring provided

      - Expression: `traceback.print_exc`

- Function `route_command_unified` (line 156)

  - Purpose: Global routing function for async_interactive.py

  - Signature summary: positional=app, session, command, args

  - Async: True, Returns: bool

  - Cross-file communications: none


## modules/commands/dev_commands.py

- Module: `modules.commands.dev_commands`

- Function `debug_toggle` (line 3)

  - Purpose: Toggle debug mode - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_configuration_prompt` at line 11 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_configuration_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 18 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

- Function `performance_monitor` (line 32)

  - Purpose: Performance monitoring controls - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_configuration_prompt` at line 49 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_configuration_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 56 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

    - Calls `modules.performance_monitor.get_monitor` at line 73 (ok)

      - Purpose: Get or create global performance monitor

      - Expression: `get_monitor`

- Function `reload_modules` (line 130)

  - Purpose: Hot-reload modules - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_configuration_prompt` at line 135 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_configuration_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 142 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

    - Calls `modules.cache_manager.get_cache_manager` at line 161 (ok)

      - Purpose: Get singleton cache manager instance

      - Expression: `get_cache_manager`


## modules/commands/diff_commands.py

- Module: `modules.commands.diff_commands`

- Function `_run_command` (line 16)

  - Purpose: No docstring provided

  - Signature summary: positional=cmd, cwd

  - Async: True, Returns: str

  - Cross-file communications:

    - Calls `asyncio.to_thread` at line 35 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.to_thread`

- Function `_run_command._runner` (line 17)

  - Purpose: No docstring provided

  - Signature summary: (no parameters)

  - Async: False, Returns: str

  - Cross-file communications:

    - Calls `subprocess.run` at line 19 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `_session_cwd` (line 10)

  - Purpose: No docstring provided

  - Signature summary: positional=session

  - Async: False, Returns: Path

  - Cross-file communications:

    - Calls `pathlib.Path` at line 12 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

    - Calls `pathlib.Path.cwd` at line 13 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.cwd`

- Function `diff_git` (line 79)

  - Purpose: Display unified diff against HEAD - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_info_command_prompt` at line 86 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_info_command_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 97 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

    - Calls `pathlib.Path.cwd` at line 112 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.cwd`

- Function `diff_overview` (line 38)

  - Purpose: Show a high-level overview of working tree state - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_info_command_prompt` at line 45 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_info_command_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 56 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

    - Calls `pathlib.Path.cwd` at line 71 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.cwd`

- Function `diff_worktree` (line 120)

  - Purpose: Placeholder for worktree comparisons - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_info_command_prompt` at line 127 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_info_command_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 138 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`


## modules/commands/inject_commands.py

- Module: `modules.commands.inject_commands`

- Functions: none

## modules/commands/local_commands.py

- Module: `modules.commands.local_commands`

- Function `local_setup` (line 3)

  - Purpose: Local model setup - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_workflow_prompt` at line 15 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_workflow_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 22 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`


## modules/commands/model_commands.py

- Module: `modules.commands.model_commands`

- Function `model_list` (line 3)

  - Purpose: List available models - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `importlib.import_module` at line 12 (unresolved)

      - Purpose: No docstring provided

      - Expression: `importlib.import_module`

    - Calls `modules.model_manager.ModelManager` at line 15 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ModelManager`

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_info_command_prompt` at line 20 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_info_command_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 30 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

    - Calls `pathlib.Path.cwd` at line 60 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.cwd`

- Function `model_list_providers` (line 135)

  - Purpose: List registered providers - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `importlib.import_module` at line 143 (unresolved)

      - Purpose: No docstring provided

      - Expression: `importlib.import_module`

    - Calls `modules.model_manager.ModelManager` at line 146 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ModelManager`

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_info_command_prompt` at line 151 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_info_command_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 161 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

    - Calls `pathlib.Path.cwd` at line 179 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.cwd`

- Function `model_switch` (line 74)

  - Purpose: Switch to a specific model - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session, model_name; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `importlib.import_module` at line 94 (unresolved)

      - Purpose: No docstring provided

      - Expression: `importlib.import_module`

    - Calls `modules.model_manager.ModelManager` at line 97 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ModelManager`

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_configuration_prompt` at line 103 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_configuration_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 110 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

- Function `model_switch_recent` (line 192)

  - Purpose: Switch to a recent model by index - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session, index

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `importlib.import_module` at line 200 (unresolved)

      - Purpose: No docstring provided

      - Expression: `importlib.import_module`

    - Calls `modules.model_manager.ModelManager` at line 203 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ModelManager`

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_configuration_prompt` at line 219 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_configuration_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 226 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

- Function `model_switch_recent_1` (line 237)

  - Purpose: Switch to most recent model - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `model_switch_recent_2` (line 242)

  - Purpose: Switch to 2nd most recent model - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications: none


## modules/commands/permission_templates.py

- Module: `modules.commands.permission_templates`

- Function `CommandPermissionTemplate.create_basic_command_prompt` (line 15)

  - Purpose: Create permission prompt for basic commands

  - Signature summary: positional=command_name, description, risk_level, category, preview_data

  - Async: False, Returns: Dict

  - Cross-file communications: none

- Function `CommandPermissionTemplate.create_configuration_prompt` (line 150)

  - Purpose: Create permission prompt for configuration commands

  - Signature summary: positional=command_name, current_settings, proposed_changes

  - Async: False, Returns: Dict

  - Cross-file communications: none

- Function `CommandPermissionTemplate.create_destructive_command_prompt` (line 70)

  - Purpose: Create permission prompt for destructive commands

  - Signature summary: positional=command_name, description, affected_items, warning_message

  - Async: False, Returns: Dict

  - Cross-file communications: none

- Function `CommandPermissionTemplate.create_info_command_prompt` (line 106)

  - Purpose: Create permission prompt for informational commands

  - Signature summary: positional=command_name, info_summary, allow_export

  - Async: False, Returns: Dict

  - Cross-file communications: none

- Function `CommandPermissionTemplate.create_workflow_prompt` (line 192)

  - Purpose: Create permission prompt for multi-step workflows

  - Signature summary: positional=workflow_name, steps, estimated_duration

  - Async: False, Returns: Dict

  - Cross-file communications: none

- Function `get_permission_manager_for_command` (line 232)

  - Purpose: Get permission manager instance for creating prompts

  - Signature summary: positional=app

  - Async: False, Returns: 'PermissionManager'

  - Cross-file communications:

    - Calls `modules.execution.permission_manager.get_permission_manager` at line 245 (ok)

      - Purpose: Get or create global permission manager instance

      - Expression: `get_permission_manager`


## modules/commands/provider_commands.py

- Module: `modules.commands.provider_commands`

- Function `_get_model_manager` (line 87)

  - Purpose: No docstring provided

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `model_manager.ModelManager` at line 90 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ModelManager`

    - Calls `modules.commands.model_manager.ModelManager` at line 93 (unresolved)

      - Purpose: No docstring provided

      - Expression: `LocalModelManager`

- Function `provider_add` (line 96)

  - Purpose: Add or update an API key for a provider - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_configuration_prompt` at line 120 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_configuration_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 127 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

- Function `provider_add_ollama` (line 140)

  - Purpose: Configure Ollama as a provider - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_configuration_prompt` at line 145 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_configuration_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 152 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

- Function `provider_list` (line 82)

  - Purpose: Alias for /providers list - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `provider_manage` (line 5)

  - Purpose: Manage API providers - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.model_manager.ModelManager` at line 14 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ModelManager`

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_info_command_prompt` at line 19 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_info_command_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 29 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

    - Calls `pathlib.Path.cwd` at line 67 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.cwd`

- Function `provider_remove` (line 166)

  - Purpose: Remove a stored provider API key - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_destructive_command_prompt` at line 189 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_destructive_command_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 197 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`


## modules/commands/refactor_commands.py

- Module: `modules.commands.refactor_commands`

- Functions: none

## modules/commands/registry.py

- Module: `modules.commands.registry`

- Function `_register_commands` (line 159)

  - Purpose: Register ALL commands - ASYNC

  - Signature summary: positional=executor

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `_register_tools` (line 818)

  - Purpose: Register ALL tools - ASYNC

  - Signature summary: positional=executor

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `_safe_register` (line 108)

  - Purpose: SDK-enforced registration with LIVE buffer update

  - Signature summary: positional=executor, exec_type, name, handler, category, risk_level, requires_approval, description; kwarg=kwargs

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `sdk.enforcement.enforce_handler` at line 129 (unresolved)

      - Purpose: No docstring provided

      - Expression: `enforce_handler`

    - Calls `asyncio.sleep` at line 156 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

- Function `register_all` (line 27)

  - Purpose: ONE registration function for EVERYTHING

  - Signature summary: positional=executor

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `time.time` at line 101 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

    - Calls `sys.stderr.write` at line 104 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.write`

    - Calls `time.strftime` at line 39 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.strftime`

    - Calls `sys.stderr.flush` at line 105 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.flush`

    - Calls `traceback.print_exc` at line 98 (unresolved)

      - Purpose: No docstring provided

      - Expression: `traceback.print_exc`

    - Calls `sdk.validation.validate_full_coverage` at line 91 (unresolved)

      - Purpose: No docstring provided

      - Expression: `validate_full_coverage`


## modules/commands/simple_tui.py

- Module: `modules.commands.simple_tui`

- Functions: none

## modules/commands/spec_commands.py

- Module: `modules.commands.spec_commands`

- Function `_render_result` (line 10)

  - Purpose: Helper to render Spec-Kit command output.

  - Signature summary: positional=app, result, heading

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `run_constitution` (line 59)

  - Purpose: Run constitution command - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_workflow_prompt` at line 72 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_workflow_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 79 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

    - Calls `modules.specify_wrapper.SpecifyWrapper` at line 87 (unresolved)

      - Purpose: No docstring provided

      - Expression: `SpecifyWrapper`

- Function `run_implement` (line 156)

  - Purpose: Run implement command - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_workflow_prompt` at line 167 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_workflow_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 174 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

    - Calls `modules.specify_wrapper.SpecifyWrapper` at line 182 (unresolved)

      - Purpose: No docstring provided

      - Expression: `SpecifyWrapper`

- Function `run_plan` (line 92)

  - Purpose: Run plan command - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_workflow_prompt` at line 105 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_workflow_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 112 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

    - Calls `modules.specify_wrapper.SpecifyWrapper` at line 120 (unresolved)

      - Purpose: No docstring provided

      - Expression: `SpecifyWrapper`

- Function `run_spec_check` (line 218)

  - Purpose: Run spec check command - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_info_command_prompt` at line 223 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_info_command_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 233 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

    - Calls `modules.specify_wrapper.SpecifyWrapper` at line 241 (unresolved)

      - Purpose: No docstring provided

      - Expression: `SpecifyWrapper`

    - Calls `pathlib.Path.cwd` at line 248 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.cwd`

- Function `run_specify` (line 25)

  - Purpose: Entry point for `/specify` - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_workflow_prompt` at line 39 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_workflow_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 46 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

    - Calls `modules.specify_wrapper.SpecifyWrapper` at line 54 (unresolved)

      - Purpose: No docstring provided

      - Expression: `SpecifyWrapper`

- Function `run_tasks` (line 125)

  - Purpose: Run tasks command - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_workflow_prompt` at line 136 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_workflow_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 143 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

    - Calls `modules.specify_wrapper.SpecifyWrapper` at line 151 (unresolved)

      - Purpose: No docstring provided

      - Expression: `SpecifyWrapper`

- Function `run_test` (line 187)

  - Purpose: Run test command - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_workflow_prompt` at line 198 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_workflow_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 205 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

    - Calls `modules.specify_wrapper.SpecifyWrapper` at line 213 (unresolved)

      - Purpose: No docstring provided

      - Expression: `SpecifyWrapper`


## modules/commands/system_commands.py

- Module: `modules.commands.system_commands`

- Function `api_server_control` (line 158)

  - Purpose: Control the OpenCLI API server - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `subprocess.run` at line 251 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_configuration_prompt` at line 184 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_configuration_prompt`

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_destructive_command_prompt` at line 199 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_destructive_command_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 207 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

    - Calls `subprocess.Popen` at line 252 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.Popen`

- Function `autorefactor` (line 350)

  - Purpose: Automatic code refactoring - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_destructive_command_prompt` at line 356 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_destructive_command_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 364 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

- Function `code_inject` (line 376)

  - Purpose: Code injection tool - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_destructive_command_prompt` at line 388 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_destructive_command_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 396 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

- Function `refactor_interactive` (line 325)

  - Purpose: Interactive refactoring mode - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_basic_command_prompt` at line 330 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_basic_command_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 338 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

- Function `restart_session` (line 3)

  - Purpose: Restart OpenCLI with the current session - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_destructive_command_prompt` at line 17 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_destructive_command_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 25 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

    - Calls `asyncio.create_task` at line 47 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.create_task`

    - Calls `asyncio.to_thread` at line 53 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.to_thread`

    - Calls `os.path.expanduser` at line 57 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.path.expanduser`

    - Calls `os.execv` at line 66 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.execv`

    - Calls `traceback.format_exc` at line 71 (unresolved)

      - Purpose: No docstring provided

      - Expression: `traceback.format_exc`

- Function `restart_session.persist_server` (line 43)

  - Purpose: No docstring provided

  - Signature summary: (no parameters)

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `rollback_opencli` (line 265)

  - Purpose: List available backups and guide through rollback - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `rollback_manager.RollbackManager` at line 270 (unresolved)

      - Purpose: No docstring provided

      - Expression: `RollbackManager`

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_info_command_prompt` at line 275 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_info_command_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 285 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

    - Calls `pathlib.Path.cwd` at line 312 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.cwd`

- Function `upgrade_opencli` (line 74)

  - Purpose: Reload OpenCLI modules - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_configuration_prompt` at line 92 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_configuration_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 99 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

    - Calls `importlib.reload` at line 114 (unresolved)

      - Purpose: No docstring provided

      - Expression: `importlib.reload`

    - Calls `traceback.format_exc` at line 155 (unresolved)

      - Purpose: No docstring provided

      - Expression: `traceback.format_exc`


## modules/concurrency_analyzer.py

- Module: `modules.concurrency_analyzer`

- Function `ConcurrencyAnalyzer.__init__` (line 88)

  - Purpose: No docstring provided

  - Signature summary: positional=self, file_path

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path` at line 89 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

- Function `ConcurrencyAnalyzer._categorize_functions` (line 254)

  - Purpose: Categorize functions as async or threading candidates

  - Signature summary: positional=self, report

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `ast.walk` at line 256 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ast.walk`

- Function `ConcurrencyAnalyzer._detect_blocking_io` (line 118)

  - Purpose: Detect blocking I/O operations

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `ast.walk` at line 120 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ast.walk`

    - Calls `pathlib.Path.cwd` at line 137 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.cwd`

- Function `ConcurrencyAnalyzer._detect_missing_async` (line 148)

  - Purpose: Detect functions that should be async

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `ast.walk` at line 156 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ast.walk`

    - Calls `pathlib.Path.cwd` at line 168 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.cwd`

- Function `ConcurrencyAnalyzer._detect_race_conditions` (line 214)

  - Purpose: Detect potential race conditions

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `ast.walk` at line 222 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ast.walk`

    - Calls `re.findall` at line 229 (unresolved)

      - Purpose: No docstring provided

      - Expression: `re.findall`

    - Calls `pathlib.Path.cwd` at line 245 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.cwd`

- Function `ConcurrencyAnalyzer._detect_ui_thread_violations` (line 177)

  - Purpose: Detect operations that shouldn't run on UI thread

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `ast.walk` at line 187 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ast.walk`

    - Calls `pathlib.Path.cwd` at line 205 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.cwd`

- Function `ConcurrencyAnalyzer.analyze` (line 94)

  - Purpose: Perform complete concurrency analysis

  - Signature summary: positional=self

  - Async: False, Returns: ConcurrencyReport

  - Cross-file communications:

    - Calls `ast.parse` at line 100 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ast.parse`

- Function `ConcurrencyReport.format_report` (line 35)

  - Purpose: Format concurrency report

  - Signature summary: positional=self

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `analyze_concurrency` (line 282)

  - Purpose: Convenience function to analyze a file for concurrency issues

  - Signature summary: positional=file_path

  - Async: False, Returns: ConcurrencyReport

  - Cross-file communications: none


## modules/context_builder.py

- Module: `modules.context_builder`

- Function `ContextBuilder.__init__` (line 18)

  - Purpose: No docstring provided

  - Signature summary: positional=self, config_dir

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ContextBuilder._cleanup_old_contexts` (line 268)

  - Purpose: Keep only the latest N context files, delete older ones

  - Signature summary: positional=self, cache, keep_latest

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path` at line 282 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

- Function `ContextBuilder._compile_context` (line 175)

  - Purpose: Compile full context from components

  - Signature summary: positional=self, agent_prompt, agents_md, agents_md_path, working_dir, cli_environment

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `ContextBuilder._get_cli_environment` (line 201)

  - Purpose: Get CLI environment information including available tools

  - Signature summary: positional=self

  - Async: False, Returns: str

  - Cross-file communications:

    - Calls `pathlib.Path.home` at line 208 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.home`

    - Calls `os.access` at line 216 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.access`

    - Calls `os.getenv` at line 231 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.getenv`

    - Calls `platform.system` at line 236 (unresolved)

      - Purpose: No docstring provided

      - Expression: `platform.system`

    - Calls `platform.release` at line 236 (unresolved)

      - Purpose: No docstring provided

      - Expression: `platform.release`

    - Calls `sys.version.split` at line 240 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.version.split`

- Function `ContextBuilder._is_recent_context` (line 254)

  - Purpose: Check if cache_key is in the most recent N contexts

  - Signature summary: positional=self, cache, cache_key, limit

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `ContextBuilder.build_context` (line 96)

  - Purpose: Build context for agent with caching

  - Signature summary: positional=self, agent_name, agent_system_prompt, working_dir, force_rebuild

  - Async: False, Returns: Tuple[str, bool]

  - Cross-file communications:

    - Calls `pathlib.Path` at line 131 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

    - Calls `datetime.datetime.now` at line 160 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

- Function `ContextBuilder.cleanup_old_temp_files` (line 309)

  - Purpose: Clean up temp files older than specified hours

  - Signature summary: positional=self, max_age_hours

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `time.time` at line 316 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

- Function `ContextBuilder.create_session_context_file` (line 297)

  - Purpose: Create temporary context file for session

  - Signature summary: positional=self, session_id, context

  - Async: False, Returns: Path

  - Cross-file communications: none

- Function `ContextBuilder.find_agents_md` (line 30)

  - Purpose: Find AGENTS.md file and return (content, file_path)

  - Signature summary: positional=self, working_dir

  - Async: False, Returns: Optional[Tuple[str, str]]

  - Cross-file communications:

    - Calls `pathlib.Path` at line 52 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

- Function `ContextBuilder.get_agents_md_hash` (line 68)

  - Purpose: Generate hash of AGENTS.md content

  - Signature summary: positional=self, content

  - Async: False, Returns: str

  - Cross-file communications:

    - Calls `hashlib.sha256` at line 70 (unresolved)

      - Purpose: No docstring provided

      - Expression: `hashlib.sha256`

- Function `ContextBuilder.get_cache_stats` (line 352)

  - Purpose: Get statistics about cached contexts

  - Signature summary: positional=self

  - Async: False, Returns: Dict

  - Cross-file communications: none

- Function `ContextBuilder.get_project_id` (line 91)

  - Purpose: Generate project ID from AGENTS.md file path

  - Signature summary: positional=self, file_path

  - Async: False, Returns: str

  - Cross-file communications:

    - Calls `pathlib.Path` at line 94 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

- Function `ContextBuilder.invalidate_cache` (line 326)

  - Purpose: Invalidate cache for project or all projects

  - Signature summary: positional=self, project_id

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path` at line 342 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

- Function `ContextBuilder.load_cache` (line 72)

  - Purpose: Load AGENTS.md cache

  - Signature summary: positional=self

  - Async: False, Returns: Dict

  - Cross-file communications:

    - Calls `json.load` at line 79 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

- Function `ContextBuilder.save_cache` (line 83)

  - Purpose: Save AGENTS.md cache

  - Signature summary: positional=self, cache

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.dump` at line 87 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dump`


## modules/core.py

- Module: `modules.core`

- Function `OpenCLITUI.__init__` (line 158)

  - Purpose: No docstring provided

  - Signature summary: positional=self, session, config

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `tui_config.get_tui_config` at line 162 (unresolved)

      - Purpose: No docstring provided

      - Expression: `get_tui_config`

    - Calls `color_manager.configure_color_mode` at line 172 (unresolved)

      - Purpose: No docstring provided

      - Expression: `configure_color_mode`

    - Calls `asyncio.Queue` at line 180 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.Queue`

- Function `OpenCLITUI._generate_ai_response` (line 359)

  - Purpose: Generate AI response (placeholder - implement based on your AI integration)

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `OpenCLITUI._handle_user_message` (line 313)

  - Purpose: Handle user message submission

  - Signature summary: positional=self, user_input, prompt_input

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `execution.permission_manager.get_permission_manager` at line 332 (unresolved)

      - Purpose: No docstring provided

      - Expression: `get_permission_manager`

    - Calls `command_router.route_command_unified` at line 343 (unresolved)

      - Purpose: No docstring provided

      - Expression: `route_command_unified`

    - Calls `traceback.print_exc` at line 350 (unresolved)

      - Purpose: No docstring provided

      - Expression: `traceback.print_exc`

- Function `OpenCLITUI._process_write_queue` (line 289)

  - Purpose: Process queued write operations

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.sleep` at line 296 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

- Function `OpenCLITUI._resolve_content_widget` (line 300)

  - Purpose: Resolve the content widget (StreamingDisplay or Static)

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `textual.widgets.Static` at line 311 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Static`

- Function `OpenCLITUI._write_direct` (line 275)

  - Purpose: Write directly to content widget

  - Signature summary: positional=self, text, end

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `OpenCLITUI.action_clear_screen` (line 381)

  - Purpose: Clear the screen content

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `OpenCLITUI.action_quit_app` (line 363)

  - Purpose: Quit the application

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `OpenCLITUI.action_toggle_performance` (line 367)

  - Purpose: Toggle performance monitoring

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `OpenCLITUI.action_toggle_refactoring` (line 374)

  - Purpose: Toggle refactoring monitoring

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `OpenCLITUI.clear_sdk_status` (line 414)

  - Purpose: Clear SDK initialization status

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `OpenCLITUI.compose` (line 190)

  - Purpose: Compose the TUI layout

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `textual.containers.Vertical` at line 192 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Vertical`

    - Calls `textual.containers.VerticalScroll` at line 196 (unresolved)

      - Purpose: No docstring provided

      - Expression: `VerticalScroll`

    - Calls `streaming_display.StreamingDisplay` at line 197 (unresolved)

      - Purpose: No docstring provided

      - Expression: `StreamingDisplay`

    - Calls `textual.widgets.Static` at line 217 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Static`

    - Calls `command_suggestions.CommandSuggestionBuffer` at line 203 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandSuggestionBuffer`

    - Calls `sdk_loading_buffer.SDKLoadingBuffer` at line 207 (unresolved)

      - Purpose: No docstring provided

      - Expression: `SDKLoadingBuffer`

    - Calls `textual.containers.Container` at line 210 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Container`

    - Calls `input_widget.MultiLineInput` at line 212 (unresolved)

      - Purpose: No docstring provided

      - Expression: `MultiLineInput`

    - Calls `modules.status_lines.PerformanceStatusLine` at line 220 (unresolved)

      - Purpose: No docstring provided

      - Expression: `PerformanceStatusLine`

    - Calls `modules.status_lines.RefactoringStatusLine` at line 221 (unresolved)

      - Purpose: No docstring provided

      - Expression: `RefactoringStatusLine`

    - Calls `modules.status_lines.StatusLine` at line 222 (unresolved)

      - Purpose: No docstring provided

      - Expression: `StatusLine`

- Function `OpenCLITUI.disable_docker_stats` (line 434)

  - Purpose: Disable Docker stats in status line

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `OpenCLITUI.enable_docker_stats` (line 429)

  - Purpose: Enable Docker stats in status line

  - Signature summary: positional=self, container_name

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `OpenCLITUI.on_key` (line 393)

  - Purpose: Handle global key events

  - Signature summary: positional=self, event

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `OpenCLITUI.on_mount` (line 224)

  - Purpose: Initialize the TUI when mounted

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `asyncio.create_task` at line 232 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.create_task`

- Function `OpenCLITUI.on_unmount` (line 440)

  - Purpose: Clean up when app is unmounted

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `OpenCLITUI.show_sdk_status` (line 409)

  - Purpose: Show SDK initialization status

  - Signature summary: positional=self, message

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `OpenCLITUI.start_spinner` (line 419)

  - Purpose: Start status line spinner

  - Signature summary: positional=self, mode

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `OpenCLITUI.stop_spinner` (line 424)

  - Purpose: Stop status line spinner

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `OpenCLITUI.write` (line 267)

  - Purpose: Queue a write operation to prevent blocking

  - Signature summary: positional=self, text, end

  - Async: False, Returns: None

  - Cross-file communications: none


## modules/diff_viewer.py

- Module: `modules.diff_viewer`

- Function `DiffHunk.__repr__` (line 35)

  - Purpose: No docstring provided

  - Signature summary: positional=self

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `DiffViewerWidget.HunkSelected.__init__` (line 68)

  - Purpose: No docstring provided

  - Signature summary: positional=self, hunk, index

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `DiffViewerWidget.ShowDiff.__init__` (line 62)

  - Purpose: No docstring provided

  - Signature summary: positional=self, hunks

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `DiffViewerWidget.__init__` (line 77)

  - Purpose: Initialize the diff viewer widget.

  - Signature summary: positional=self; kwonly=name, id, classes

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `DiffViewerWidget.close` (line 219)

  - Purpose: Close the diff viewer.

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `DiffViewerWidget.navigate_down` (line 207)

  - Purpose: Move selection down one hunk.

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `DiffViewerWidget.navigate_up` (line 201)

  - Purpose: Move selection up one hunk.

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `DiffViewerWidget.render` (line 98)

  - Purpose: Render the diff viewer with Frontier colors.

  - Signature summary: positional=self

  - Async: False, Returns: RenderableType

  - Cross-file communications:

    - Calls `rich.text.Text` at line 110 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

- Function `DiffViewerWidget.select_current_hunk` (line 213)

  - Purpose: Select the currently highlighted hunk.

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `DiffViewerWidget.set_hunks` (line 190)

  - Purpose: Set the diff hunks to display.

  - Signature summary: positional=self, hunks

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `docker_venv_diff` (line 324)

  - Purpose: Get diff between Docker venv and worktree.

  - Signature summary: positional=container_id, venv_path, worktree_path

  - Async: False, Returns: List[DiffHunk]

  - Cross-file communications:

    - Calls `tempfile.NamedTemporaryFile` at line 340 (unresolved)

      - Purpose: No docstring provided

      - Expression: `tempfile.NamedTemporaryFile`

    - Calls `subprocess.run` at line 351 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

    - Calls `os.unlink` at line 368 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.unlink`

- Function `git_diff_to_hunks` (line 290)

  - Purpose: Get diff hunks from git repository.

  - Signature summary: positional=repo_path, ref1, ref2

  - Async: False, Returns: List[DiffHunk]

  - Cross-file communications:

    - Calls `subprocess.run` at line 309 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `parse_unified_diff` (line 224)

  - Purpose: Parse unified diff format into DiffHunk objects.

  - Signature summary: positional=diff_text

  - Async: False, Returns: List[DiffHunk]

  - Cross-file communications: none


## modules/docker_async_handler.py

- Module: `modules.docker_async_handler`

- Function `DockerAsyncHandler.__init__` (line 20)

  - Purpose: Initialize async Docker handler.

  - Signature summary: positional=self, docker_manager, debug_callback

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `DockerAsyncHandler._safe_thread_call` (line 31)

  - Purpose: Safely execute function in thread with error handling and timeout.

  - Signature summary: positional=self, func; kwonly=timeout; vararg=args; kwarg=kwargs

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.wait_for` at line 45 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.wait_for`

    - Calls `asyncio.to_thread` at line 46 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.to_thread`

    - Calls `traceback.format_tb` at line 60 (unresolved)

      - Purpose: No docstring provided

      - Expression: `traceback.format_tb`

- Function `DockerAsyncHandler.check_docker_installed` (line 64)

  - Purpose: Check if Docker is installed (async).

  - Signature summary: positional=self

  - Async: True, Returns: Tuple[bool, str]

  - Cross-file communications: none

- Function `DockerAsyncHandler.check_docker_running` (line 83)

  - Purpose: Check if Docker daemon is running (async).

  - Signature summary: positional=self

  - Async: True, Returns: Tuple[bool, str]

  - Cross-file communications: none

- Function `DockerAsyncHandler.check_resource_safety` (line 320)

  - Purpose: Check resource safety (async).

  - Signature summary: positional=self, cpu_limit, memory_limit

  - Async: True, Returns: Tuple[bool, str]

  - Cross-file communications: none

- Function `DockerAsyncHandler.create_ollama_container` (line 162)

  - Purpose: Create Ollama container (async).

  - Signature summary: positional=self, gpu_enabled, cpu_limit, memory_limit

  - Async: True, Returns: Tuple[bool, str]

  - Cross-file communications: none

- Function `DockerAsyncHandler.get_container_stats` (line 261)

  - Purpose: Get container stats (async).

  - Signature summary: positional=self, container_name

  - Async: True, Returns: Optional[Dict]

  - Cross-file communications: none

- Function `DockerAsyncHandler.get_ollama_container_status` (line 102)

  - Purpose: Get Ollama container status (async).

  - Signature summary: positional=self

  - Async: True, Returns: Tuple[Optional[str], Optional[str], Optional[str]]

  - Cross-file communications: none

- Function `DockerAsyncHandler.get_system_resources` (line 302)

  - Purpose: Get system resources (async).

  - Signature summary: positional=self

  - Async: True, Returns: Dict

  - Cross-file communications: none

- Function `DockerAsyncHandler.is_ollama_running` (line 121)

  - Purpose: Check if Ollama container is running (async).

  - Signature summary: positional=self

  - Async: True, Returns: Tuple[bool, Optional[str]]

  - Cross-file communications: none

- Function `DockerAsyncHandler.list_containers` (line 239)

  - Purpose: List Docker containers (async).

  - Signature summary: positional=self, all_containers

  - Async: True, Returns: List[Dict]

  - Cross-file communications: none

- Function `DockerAsyncHandler.pull_image` (line 280)

  - Purpose: Pull a Docker image (async).

  - Signature summary: positional=self, image

  - Async: True, Returns: Tuple[bool, str]

  - Cross-file communications: none

- Function `DockerAsyncHandler.remove_ollama_container` (line 140)

  - Purpose: Remove Ollama container (async).

  - Signature summary: positional=self, force

  - Async: True, Returns: Tuple[bool, str]

  - Cross-file communications: none

- Function `DockerAsyncHandler.start_container` (line 193)

  - Purpose: Start a container (async).

  - Signature summary: positional=self, container_name

  - Async: True, Returns: Tuple[bool, str]

  - Cross-file communications: none

- Function `DockerAsyncHandler.stop_container` (line 215)

  - Purpose: Stop a container (async).

  - Signature summary: positional=self, container_name, timeout

  - Async: True, Returns: Tuple[bool, str]

  - Cross-file communications: none

- Function `OllamaAsyncHandler.__init__` (line 352)

  - Purpose: Initialize async Ollama handler.

  - Signature summary: positional=self, debug_callback

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `OllamaAsyncHandler.check_native_ollama` (line 360)

  - Purpose: Check for native Ollama installation (async with timeout).

  - Signature summary: positional=self

  - Async: True, Returns: Tuple[bool, Optional[str]]

  - Cross-file communications:

    - Calls `asyncio.wait_for` at line 389 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.wait_for`

    - Calls `asyncio.to_thread` at line 390 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.to_thread`

    - Calls `pathlib.Path` at line 379 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

- Function `OllamaAsyncHandler.check_ollama_server` (line 415)

  - Purpose: Check if Ollama server is running (async with timeout).

  - Signature summary: positional=self, timeout

  - Async: True, Returns: Tuple[bool, str]

  - Cross-file communications:

    - Calls `asyncio.wait_for` at line 428 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.wait_for`

    - Calls `asyncio.to_thread` at line 429 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.to_thread`

- Function `OllamaAsyncHandler.get_ollama_process_info` (line 503)

  - Purpose: Get Ollama process information (async with timeout).

  - Signature summary: positional=self

  - Async: True, Returns: Tuple[bool, Optional[str], Optional[str]]

  - Cross-file communications:

    - Calls `asyncio.wait_for` at line 512 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.wait_for`

    - Calls `asyncio.to_thread` at line 513 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.to_thread`

- Function `OllamaAsyncHandler.list_ollama_models` (line 453)

  - Purpose: List Ollama models (async with timeout).

  - Signature summary: positional=self, timeout

  - Async: True, Returns: Tuple[bool, List[Dict], str]

  - Cross-file communications:

    - Calls `asyncio.wait_for` at line 465 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.wait_for`

    - Calls `asyncio.to_thread` at line 466 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.to_thread`


## modules/docker_commands.py

- Module: `modules.docker_commands`

- Function `docker_main` (line 15)

  - Purpose: Parent /docker command - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_info_command_prompt` at line 20 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_info_command_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 30 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

- Function `docker_ollama_setup` (line 49)

  - Purpose: Docker Ollama setup - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_workflow_prompt` at line 61 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_workflow_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 68 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

    - Calls `docker_manager.DockerManager` at line 79 (unresolved)

      - Purpose: No docstring provided

      - Expression: `DockerManager`

    - Calls `docker_async_handler.DockerAsyncHandler` at line 80 (unresolved)

      - Purpose: No docstring provided

      - Expression: `DockerAsyncHandler`

- Function `docker_ollama_start` (line 143)

  - Purpose: Docker Ollama start - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_configuration_prompt` at line 148 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_configuration_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 155 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

    - Calls `docker_manager.DockerManager` at line 166 (unresolved)

      - Purpose: No docstring provided

      - Expression: `DockerManager`

    - Calls `docker_async_handler.DockerAsyncHandler` at line 167 (unresolved)

      - Purpose: No docstring provided

      - Expression: `DockerAsyncHandler`

- Function `docker_ollama_status` (line 449)

  - Purpose: Show status for the OpenCLI Ollama container - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_info_command_prompt` at line 454 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_info_command_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 464 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

    - Calls `docker_manager.DockerManager` at line 475 (unresolved)

      - Purpose: No docstring provided

      - Expression: `DockerManager`

    - Calls `docker_async_handler.DockerAsyncHandler` at line 476 (unresolved)

      - Purpose: No docstring provided

      - Expression: `DockerAsyncHandler`

    - Calls `pathlib.Path.cwd` at line 498 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.cwd`

- Function `docker_ollama_stop` (line 193)

  - Purpose: Docker Ollama stop - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_destructive_command_prompt` at line 204 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_destructive_command_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 212 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

    - Calls `docker_manager.DockerManager` at line 227 (unresolved)

      - Purpose: No docstring provided

      - Expression: `DockerManager`

    - Calls `docker_async_handler.DockerAsyncHandler` at line 228 (unresolved)

      - Purpose: No docstring provided

      - Expression: `DockerAsyncHandler`

- Function `docker_ps` (line 323)

  - Purpose: List running Docker containers - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_info_command_prompt` at line 328 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_info_command_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 338 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

    - Calls `docker_manager.DockerManager` at line 349 (unresolved)

      - Purpose: No docstring provided

      - Expression: `DockerManager`

    - Calls `docker_async_handler.DockerAsyncHandler` at line 350 (unresolved)

      - Purpose: No docstring provided

      - Expression: `DockerAsyncHandler`

    - Calls `pathlib.Path.cwd` at line 368 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.cwd`

- Function `docker_stats` (line 382)

  - Purpose: Show lightweight stats for running containers - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_info_command_prompt` at line 387 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_info_command_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 397 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

    - Calls `docker_manager.DockerManager` at line 408 (unresolved)

      - Purpose: No docstring provided

      - Expression: `DockerManager`

    - Calls `docker_async_handler.DockerAsyncHandler` at line 409 (unresolved)

      - Purpose: No docstring provided

      - Expression: `DockerAsyncHandler`

    - Calls `pathlib.Path.cwd` at line 437 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.cwd`

- Function `docker_status` (line 253)

  - Purpose: Show Docker daemon status - PERMISSION BUFFER INTEGRATED

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.commands.permission_templates.CommandPermissionTemplate.create_info_command_prompt` at line 258 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandPermissionTemplate.create_info_command_prompt`

    - Calls `modules.commands.permission_templates.get_permission_manager_for_command` at line 268 (ok)

      - Purpose: Get permission manager instance for creating prompts

      - Expression: `get_permission_manager_for_command`

    - Calls `docker_manager.DockerManager` at line 279 (unresolved)

      - Purpose: No docstring provided

      - Expression: `DockerManager`

    - Calls `docker_async_handler.DockerAsyncHandler` at line 280 (unresolved)

      - Purpose: No docstring provided

      - Expression: `DockerAsyncHandler`

    - Calls `pathlib.Path.cwd` at line 306 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.cwd`


## modules/docker_commands_unified.py

- Module: `modules.docker_commands_unified`

- Function `docker_ollama_setup_unified` (line 15)

  - Purpose: Execute Docker Ollama setup through PERMISSION BUFFER FIRST!

  - Signature summary: positional=app, session

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `importlib.import_module` at line 43 (unresolved)

      - Purpose: No docstring provided

      - Expression: `importlib.import_module`

    - Calls `modules.docker_manager.DockerManager` at line 47 (unresolved)

      - Purpose: No docstring provided

      - Expression: `DockerManager`

    - Calls `modules.docker_async_handler.DockerAsyncHandler` at line 48 (unresolved)

      - Purpose: No docstring provided

      - Expression: `DockerAsyncHandler`

    - Calls `permission_buffer_manager.get_permission_buffer_manager` at line 100 (unresolved)

      - Purpose: No docstring provided

      - Expression: `get_permission_buffer_manager`

    - Calls `modules.unified_command_executor.CommandStep` at line 226 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandStep`

- Function `docker_ollama_setup_unified.check_docker` (line 127)

  - Purpose: No docstring provided

  - Signature summary: (no parameters)

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `docker_ollama_setup_unified.check_existing` (line 144)

  - Purpose: No docstring provided

  - Signature summary: (no parameters)

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `docker_ollama_setup_unified.create_container` (line 197)

  - Purpose: No docstring provided

  - Signature summary: (no parameters)

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `docker_ollama_setup_unified.on_complete` (line 237)

  - Purpose: Called when setup completes successfully

  - Signature summary: positional=execution

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `docker_ollama_setup_unified.pull_image` (line 168)

  - Purpose: No docstring provided

  - Signature summary: (no parameters)

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.to_thread` at line 171 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.to_thread`

- Function `docker_ollama_setup_unified.verify_running` (line 220)

  - Purpose: No docstring provided

  - Signature summary: (no parameters)

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `docker_ollama_start_unified` (line 267)

  - Purpose: Start Ollama container through unified executor

  - Signature summary: positional=app, session

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `importlib.import_module` at line 280 (unresolved)

      - Purpose: No docstring provided

      - Expression: `importlib.import_module`

    - Calls `modules.docker_manager.DockerManager` at line 284 (unresolved)

      - Purpose: No docstring provided

      - Expression: `DockerManager`

    - Calls `modules.docker_async_handler.DockerAsyncHandler` at line 285 (unresolved)

      - Purpose: No docstring provided

      - Expression: `DockerAsyncHandler`

    - Calls `modules.unified_command_executor.CommandStep` at line 318 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandStep`

- Function `docker_ollama_start_unified.check_status` (line 289)

  - Purpose: No docstring provided

  - Signature summary: (no parameters)

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `docker_ollama_start_unified.start_container` (line 311)

  - Purpose: No docstring provided

  - Signature summary: (no parameters)

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `docker_ollama_stop_unified` (line 337)

  - Purpose: Stop Ollama container through unified executor

  - Signature summary: positional=app, session

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `importlib.import_module` at line 350 (unresolved)

      - Purpose: No docstring provided

      - Expression: `importlib.import_module`

    - Calls `modules.docker_manager.DockerManager` at line 354 (unresolved)

      - Purpose: No docstring provided

      - Expression: `DockerManager`

    - Calls `modules.docker_async_handler.DockerAsyncHandler` at line 355 (unresolved)

      - Purpose: No docstring provided

      - Expression: `DockerAsyncHandler`

    - Calls `modules.unified_command_executor.CommandStep` at line 382 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandStep`

- Function `docker_ollama_stop_unified.check_running` (line 359)

  - Purpose: No docstring provided

  - Signature summary: (no parameters)

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `docker_ollama_stop_unified.stop_container` (line 375)

  - Purpose: No docstring provided

  - Signature summary: (no parameters)

  - Async: True, Returns: None

  - Cross-file communications: none


## modules/docker_manager.py

- Module: `modules.docker_manager`

- Function `DockerManager.__init__` (line 26)

  - Purpose: No docstring provided

  - Signature summary: positional=self, config_dir

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path.home` at line 27 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.home`

- Function `DockerManager._load_config` (line 31)

  - Purpose: Load Docker configuration.

  - Signature summary: positional=self

  - Async: False, Returns: Dict

  - Cross-file communications:

    - Calls `json.load` at line 36 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

- Function `DockerManager._save_config` (line 48)

  - Purpose: Save Docker configuration.

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.dump` at line 52 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dump`

- Function `DockerManager.check_resource_safety` (line 154)

  - Purpose: Check if requested resources are safe.

  - Signature summary: positional=self, cpu_limit, memory_limit

  - Async: False, Returns: Tuple[bool, str]

  - Cross-file communications: none

- Function `DockerManager.create_ollama_container` (line 348)

  - Purpose: Create and start Ollama Docker container.

  - Signature summary: positional=self, gpu_enabled, cpu_limit, memory_limit

  - Async: False, Returns: Tuple[bool, str]

  - Cross-file communications:

    - Calls `subprocess.run` at line 394 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `DockerManager.get_container_stats` (line 241)

  - Purpose: Get real-time stats for a container.

  - Signature summary: positional=self, container_name

  - Async: False, Returns: Optional[Dict]

  - Cross-file communications:

    - Calls `subprocess.run` at line 251 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

    - Calls `json.loads` at line 259 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.loads`

- Function `DockerManager.get_ollama_container_status` (line 523)

  - Purpose: Get detailed status of Ollama container.

  - Signature summary: positional=self

  - Async: False, Returns: Dict

  - Cross-file communications: none

- Function `DockerManager.get_system_resources` (line 97)

  - Purpose: Get system resource information for safety checks.

  - Signature summary: positional=self

  - Async: False, Returns: Dict

  - Cross-file communications:

    - Calls `multiprocessing.cpu_count` at line 108 (unresolved)

      - Purpose: No docstring provided

      - Expression: `multiprocessing.cpu_count`

    - Calls `os.uname` at line 114 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.uname`

    - Calls `subprocess.run` at line 136 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

    - Calls `pathlib.Path.home` at line 137 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.home`

- Function `DockerManager.is_docker_installed` (line 54)

  - Purpose: Check if Docker is installed.

  - Signature summary: positional=self

  - Async: False, Returns: Tuple[bool, str]

  - Cross-file communications:

    - Calls `subprocess.run` at line 61 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `DockerManager.is_docker_running` (line 76)

  - Purpose: Check if Docker daemon is running.

  - Signature summary: positional=self

  - Async: False, Returns: Tuple[bool, str]

  - Cross-file communications:

    - Calls `subprocess.run` at line 83 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `DockerManager.is_ollama_running` (line 272)

  - Purpose: Check if Ollama container is running.

  - Signature summary: positional=self

  - Async: False, Returns: Tuple[bool, Optional[str]]

  - Cross-file communications: none

- Function `DockerManager.list_containers` (line 204)

  - Purpose: List Docker containers.

  - Signature summary: positional=self, all_containers

  - Async: False, Returns: List[Dict]

  - Cross-file communications:

    - Calls `subprocess.run` at line 218 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

    - Calls `json.loads` at line 232 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.loads`

- Function `DockerManager.pull_image` (line 496)

  - Purpose: Pull a Docker image.

  - Signature summary: positional=self, image

  - Async: False, Returns: Tuple[bool, str]

  - Cross-file communications:

    - Calls `subprocess.run` at line 507 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `DockerManager.remove_container` (line 465)

  - Purpose: Remove a container.

  - Signature summary: positional=self, container_name, force

  - Async: False, Returns: Tuple[bool, str]

  - Cross-file communications:

    - Calls `subprocess.run` at line 481 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `DockerManager.remove_ollama_container` (line 313)

  - Purpose: Remove OpenCLI Ollama container (including stopped/failed ones).

  - Signature summary: positional=self, force

  - Async: False, Returns: Tuple[bool, str]

  - Cross-file communications:

    - Calls `subprocess.run` at line 333 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `DockerManager.start_container` (line 412)

  - Purpose: Start a stopped container.

  - Signature summary: positional=self, container_name

  - Async: False, Returns: Tuple[bool, str]

  - Cross-file communications:

    - Calls `subprocess.run` at line 422 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `DockerManager.stop_container` (line 437)

  - Purpose: Stop a running container gracefully.

  - Signature summary: positional=self, container_name, timeout

  - Async: False, Returns: Tuple[bool, str]

  - Cross-file communications:

    - Calls `subprocess.run` at line 448 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`


## modules/docker_venv.py

- Module: `modules.docker_venv`

- Function `DockerVenvManager.__init__` (line 48)

  - Purpose: No docstring provided

  - Signature summary: positional=self, config_dir

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path.home` at line 49 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.home`

- Function `DockerVenvManager._load_venvs` (line 53)

  - Purpose: Load tracked virtual environments.

  - Signature summary: positional=self

  - Async: False, Returns: Dict[str, DockerVenv]

  - Cross-file communications:

    - Calls `json.load` at line 58 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

- Function `DockerVenvManager._save_venvs` (line 67)

  - Purpose: Save tracked virtual environments.

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.dump` at line 82 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dump`

- Function `DockerVenvManager.copy_from_venv` (line 376)

  - Purpose: Copy file/directory from venv container to local.

  - Signature summary: positional=self, name, container_path, local_path

  - Async: False, Returns: Tuple[bool, str]

  - Cross-file communications:

    - Calls `subprocess.run` at line 397 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `DockerVenvManager.copy_to_venv` (line 340)

  - Purpose: Copy file/directory from local to venv container.

  - Signature summary: positional=self, name, local_path, container_path

  - Async: False, Returns: Tuple[bool, str]

  - Cross-file communications:

    - Calls `subprocess.run` at line 361 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `DockerVenvManager.create_venv` (line 84)

  - Purpose: Create a new Docker-based virtual environment.

  - Signature summary: positional=self, name, python_version, packages, work_dir

  - Async: False, Returns: Tuple[bool, str]

  - Cross-file communications:

    - Calls `subprocess.run` at line 166 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

    - Calls `datetime.now` at line 177 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.datetime.now`

- Function `DockerVenvManager.delete_venv` (line 259)

  - Purpose: Delete a venv and optionally remove its files.

  - Signature summary: positional=self, name, remove_files

  - Async: False, Returns: Tuple[bool, str]

  - Cross-file communications:

    - Calls `subprocess.run` at line 275 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

    - Calls `shutil.rmtree` at line 294 (unresolved)

      - Purpose: No docstring provided

      - Expression: `shutil.rmtree`

- Function `DockerVenvManager.exec_in_venv` (line 301)

  - Purpose: Execute a command in the venv container.

  - Signature summary: positional=self, name, command, timeout

  - Async: False, Returns: Tuple[bool, str, str]

  - Cross-file communications:

    - Calls `subprocess.run` at line 325 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `DockerVenvManager.get_venv` (line 196)

  - Purpose: Get venv by name.

  - Signature summary: positional=self, name

  - Async: False, Returns: Optional[DockerVenv]

  - Cross-file communications: none

- Function `DockerVenvManager.get_venv_files` (line 412)

  - Purpose: List files in venv directory.

  - Signature summary: positional=self, name, directory

  - Async: False, Returns: List[str]

  - Cross-file communications: none

- Function `DockerVenvManager.is_venv_running` (line 200)

  - Purpose: Check if venv container is running.

  - Signature summary: positional=self, name

  - Async: False, Returns: bool

  - Cross-file communications:

    - Calls `subprocess.run` at line 207 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `DockerVenvManager.list_venvs` (line 192)

  - Purpose: List all tracked virtual environments.

  - Signature summary: positional=self

  - Async: False, Returns: List[DockerVenv]

  - Cross-file communications: none

- Function `DockerVenvManager.run_python_code` (line 433)

  - Purpose: Run Python code in the venv safely.

  - Signature summary: positional=self, name, code, timeout

  - Async: False, Returns: Tuple[bool, str, str]

  - Cross-file communications:

    - Calls `tempfile.NamedTemporaryFile` at line 450 (unresolved)

      - Purpose: No docstring provided

      - Expression: `tempfile.NamedTemporaryFile`

    - Calls `os.unlink` at line 481 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.unlink`

- Function `DockerVenvManager.start_venv` (line 217)

  - Purpose: Start a stopped venv container.

  - Signature summary: positional=self, name

  - Async: False, Returns: Tuple[bool, str]

  - Cross-file communications:

    - Calls `subprocess.run` at line 224 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `DockerVenvManager.stop_venv` (line 238)

  - Purpose: Stop a running venv container.

  - Signature summary: positional=self, name

  - Async: False, Returns: Tuple[bool, str]

  - Cross-file communications:

    - Calls `subprocess.run` at line 245 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`


## modules/dual_buffer_system.py

- Module: `modules.dual_buffer_system`

- Function `CommandBuffer.__init__` (line 124)

  - Purpose: No docstring provided

  - Signature summary: positional=self, app

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `CommandBuffer._refresh_display` (line 164)

  - Purpose: Rebuild and update the display

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `rich.text.Text` at line 168 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

- Function `CommandBuffer.write` (line 127)

  - Purpose: Write immediately to display.

  - Signature summary: positional=self, text, markdown, style

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `markdown_renderer.get_markdown_renderer` at line 140 (unresolved)

      - Purpose: No docstring provided

      - Expression: `get_markdown_renderer`

    - Calls `rich.text.Text` at line 155 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

    - Calls `asyncio.sleep` at line 162 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

- Function `DualBufferCoordinator.__init__` (line 195)

  - Purpose: No docstring provided

  - Signature summary: positional=self, app

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `asyncio.Lock` at line 199 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.Lock`

- Function `DualBufferCoordinator.finish_tool` (line 231)

  - Purpose: Finish a tool execution buffer.

  - Signature summary: positional=self, tool_buffer, success

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `DualBufferCoordinator.start_tool` (line 213)

  - Purpose: Start a new tool execution buffer.

  - Signature summary: positional=self, tool_name, tool_args

  - Async: True, Returns: ToolBuffer

  - Cross-file communications: none

- Function `DualBufferCoordinator.write_command` (line 201)

  - Purpose: Write to command buffer (immediate).

  - Signature summary: positional=self, text, markdown, style

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `ToolBuffer.__init__` (line 26)

  - Purpose: No docstring provided

  - Signature summary: positional=self, app, tool_name, tool_args

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ToolBuffer._refresh_display` (line 100)

  - Purpose: Rebuild and update the display

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `rich.text.Text` at line 104 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

- Function `ToolBuffer.finish` (line 75)

  - Purpose: Mark tool execution complete

  - Signature summary: positional=self, success

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `rich.text.Text` at line 93 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

- Function `ToolBuffer.start` (line 39)

  - Purpose: Start tool execution display

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `rich.text.Text` at line 50 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

- Function `ToolBuffer.write_chunk` (line 55)

  - Purpose: Stream a chunk of tool output

  - Signature summary: positional=self, text

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `rich.text.Text` at line 66 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

    - Calls `asyncio.sleep` at line 73 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`


## modules/execution/__init__.py

- Module: `modules.execution`

- Functions: none

## modules/execution/async_runner.py

- Module: `modules.execution.async_runner`

- Function `AsyncExecutionRunner.run_async` (line 15)

  - Purpose: Execute function asynchronously with timeout

  - Signature summary: positional=func, timeout; vararg=args; kwarg=kwargs

  - Async: True, Returns: Any

  - Cross-file communications:

    - Calls `asyncio.iscoroutinefunction` at line 38 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.iscoroutinefunction`

    - Calls `asyncio.wait_for` at line 45 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.wait_for`

    - Calls `asyncio.to_thread` at line 46 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.to_thread`

    - Calls `asyncio.TimeoutError` at line 53 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.TimeoutError`

- Function `AsyncExecutionRunner.run_bash_async` (line 56)

  - Purpose: Non-blocking bash execution with timeout

  - Signature summary: positional=command, timeout, description

  - Async: True, Returns: str

  - Cross-file communications:

    - Calls `asyncio.create_subprocess_shell` at line 73 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.create_subprocess_shell`

    - Calls `asyncio.wait_for` at line 79 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.wait_for`

    - Calls `asyncio.TimeoutError` at line 91 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.TimeoutError`


## modules/execution/circuit_breaker.py

- Module: `modules.execution.circuit_breaker`

- Function `CircuitBreaker.__init__` (line 29)

  - Purpose: Args:

  - Signature summary: positional=self, failure_threshold, timeout, success_threshold

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `CircuitBreaker.execute` (line 48)

  - Purpose: Execute function with circuit breaker protection

  - Signature summary: positional=self, execution_id, func; vararg=args; kwarg=kwargs

  - Async: True, Returns: Any

  - Cross-file communications:

    - Calls `time.time` at line 112 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

- Function `CircuitBreaker.get_state` (line 120)

  - Purpose: Get current circuit state

  - Signature summary: positional=self, execution_id

  - Async: False, Returns: CircuitState

  - Cross-file communications: none

- Function `CircuitBreaker.reset` (line 126)

  - Purpose: Reset circuit to closed state

  - Signature summary: positional=self, execution_id

  - Async: False, Returns: None

  - Cross-file communications: none


## modules/execution/enforcement.py

- Module: `modules.execution.enforcement`

- Function `SDKEnforcement.__init__` (line 55)

  - Purpose: No docstring provided

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `SDKEnforcement._attempt_conversion` (line 154)

  - Purpose: Attempt to convert handler to be compliant

  - Signature summary: positional=self, handler, validation

  - Async: False, Returns: Optional[Callable]

  - Cross-file communications: none

- Function `SDKEnforcement._wrap_add_context` (line 182)

  - Purpose: Wrap handler to add **context parameter

  - Signature summary: positional=self, handler

  - Async: False, Returns: Callable

  - Cross-file communications: none

- Function `SDKEnforcement._wrap_add_context.wrapped_handler` (line 195)

  - Purpose: SDK compliance wrapper - adds **context support

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `inspect.signature` at line 199 (unresolved)

      - Purpose: No docstring provided

      - Expression: `inspect.signature`

    - Calls `traceback.print_exc` at line 234 (unresolved)

      - Purpose: No docstring provided

      - Expression: `traceback.print_exc`

- Function `SDKEnforcement.enforce` (line 62)

  - Purpose: Enforce SDK compliance on handler

  - Signature summary: positional=self, name, handler, category, auto_convert

  - Async: False, Returns: EnforcementResult

  - Cross-file communications:

    - Calls `modules.execution.handler_interface.validate_handler` at line 82 (unresolved)

      - Purpose: No docstring provided

      - Expression: `validate_handler`

- Function `SDKEnforcement.get_rejected` (line 287)

  - Purpose: Get list of rejected handlers

  - Signature summary: positional=self

  - Async: False, Returns: List[EnforcementResult]

  - Cross-file communications: none

- Function `SDKEnforcement.get_summary` (line 246)

  - Purpose: Get enforcement summary for display

  - Signature summary: positional=self

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `SDKEnforcement.has_violations` (line 291)

  - Purpose: Check if any handlers were rejected

  - Signature summary: positional=self

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `enforce_handler` (line 308)

  - Purpose: Enforce SDK compliance on handler

  - Signature summary: positional=name, handler, category, auto_convert

  - Async: False, Returns: EnforcementResult

  - Cross-file communications: none

- Function `get_enforcement` (line 300)

  - Purpose: Get or create global enforcement instance

  - Signature summary: (no parameters)

  - Async: False, Returns: SDKEnforcement

  - Cross-file communications: none


## modules/execution/executor.py

- Module: `modules.execution.executor`

- Function `ExecutionStep.__post_init__` (line 56)

  - Purpose: No docstring provided

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ExecutionSystem.__init__` (line 75)

  - Purpose: No docstring provided

  - Signature summary: positional=self, app, session

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `modules.execution.registry.ExecutionRegistry` at line 80 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ExecutionRegistry`

    - Calls `modules.execution.permission_manager.PermissionManager` at line 81 (unresolved)

      - Purpose: No docstring provided

      - Expression: `PermissionManager`

    - Calls `modules.execution.async_runner.AsyncExecutionRunner` at line 82 (unresolved)

      - Purpose: No docstring provided

      - Expression: `AsyncExecutionRunner`

    - Calls `modules.execution.circuit_breaker.CircuitBreaker` at line 83 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CircuitBreaker`

    - Calls `modules.execution.retry_manager.RetryManager` at line 84 (unresolved)

      - Purpose: No docstring provided

      - Expression: `RetryManager`

- Function `ExecutionSystem._clear_statusline` (line 445)

  - Purpose: Clear statusline indicator

  - Signature summary: positional=self, label

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ExecutionSystem._execute_single` (line 377)

  - Purpose: Execute single function (tool or simple command)

  - Signature summary: positional=self, registration, context

  - Async: True, Returns: Any

  - Cross-file communications:

    - Calls `asyncio.iscoroutinefunction` at line 403 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.iscoroutinefunction`

    - Calls `asyncio.sleep` at line 428 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

- Function `ExecutionSystem._execute_workflow` (line 191)

  - Purpose: Execute multi-step workflow with live progress IN PERMISSION BUFFER

  - Signature summary: positional=self, registration, steps, context

  - Async: True, Returns: List[Any]

  - Cross-file communications:

    - Calls `asyncio.create_task` at line 240 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.create_task`

    - Calls `asyncio.sleep` at line 320 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

    - Calls `asyncio.iscoroutinefunction` at line 280 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.iscoroutinefunction`

- Function `ExecutionSystem._update_statusline` (line 436)

  - Purpose: Update statusline indicator

  - Signature summary: positional=self, label, icon, color

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ExecutionSystem._wait_for_step_permission` (line 333)

  - Purpose: Show permission prompt for individual step

  - Signature summary: positional=self, step, workflow_status, prompt_input

  - Async: True, Returns: bool

  - Cross-file communications:

    - Calls `permission_buffer_manager.get_permission_buffer_manager` at line 344 (unresolved)

      - Purpose: No docstring provided

      - Expression: `get_permission_buffer_manager`

- Function `ExecutionSystem.execute` (line 93)

  - Purpose: Execute command/tool/API with unified flow

  - Signature summary: positional=self, type, name, steps; kwarg=context

  - Async: True, Returns: Any

  - Cross-file communications: none

- Function `ExecutionSystem.execute_api` (line 475)

  - Purpose: Execute API call by name

  - Signature summary: positional=self, name; kwarg=context

  - Async: True, Returns: Any

  - Cross-file communications: none

- Function `ExecutionSystem.execute_command` (line 458)

  - Purpose: Execute command by name

  - Signature summary: positional=self, name, steps; kwarg=context

  - Async: True, Returns: Any

  - Cross-file communications: none

- Function `ExecutionSystem.execute_tool` (line 467)

  - Purpose: Execute tool by name

  - Signature summary: positional=self, name; kwarg=context

  - Async: True, Returns: Any

  - Cross-file communications: none

- Function `get_executor` (line 488)

  - Purpose: Get or create global execution system

  - Signature summary: positional=app, session

  - Async: False, Returns: ExecutionSystem

  - Cross-file communications: none


## modules/execution/permission_manager.py

- Module: `modules.execution.permission_manager`

- Function `PermissionManager.__init__` (line 42)

  - Purpose: No docstring provided

  - Signature summary: positional=self, config_dir

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path.home` at line 43 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.home`

- Function `PermissionManager._assess_api_risk` (line 247)

  - Purpose: Assess risk of API call

  - Signature summary: positional=self, registration, context

  - Async: False, Returns: RiskLevel

  - Cross-file communications: none

- Function `PermissionManager._assess_bash_risk` (line 223)

  - Purpose: Assess risk of bash command

  - Signature summary: positional=self, command

  - Async: False, Returns: RiskLevel

  - Cross-file communications: none

- Function `PermissionManager._assess_path_risk` (line 169)

  - Purpose: Assess risk level of file path

  - Signature summary: positional=self, file_path

  - Async: False, Returns: RiskLevel

  - Cross-file communications:

    - Calls `pathlib.Path.cwd` at line 179 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.cwd`

    - Calls `pathlib.Path` at line 192 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

    - Calls `pathlib.Path.home` at line 195 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.home`

- Function `PermissionManager._assess_total_risk` (line 121)

  - Purpose: Calculate total risk from multiple factors

  - Signature summary: positional=self, registration, context

  - Async: False, Returns: RiskLevel

  - Cross-file communications: none

- Function `PermissionManager._format_permission_message` (line 354)

  - Purpose: Format permission message with MARKDOWN like startup buffer - ROBUST

  - Signature summary: positional=self, registration, risk, context

  - Async: False, Returns: str

  - Cross-file communications:

    - Calls `pathlib.Path` at line 406 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

    - Calls `pathlib.Path.cwd` at line 407 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.cwd`

- Function `PermissionManager._load_permissions` (line 423)

  - Purpose: Load saved permissions

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.load` at line 430 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

- Function `PermissionManager._save_permissions` (line 437)

  - Purpose: Save permissions to file

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.dump` at line 446 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dump`

- Function `PermissionManager._show_permission_prompt` (line 267)

  - Purpose: Show permission prompt in permission buffer

  - Signature summary: positional=self, app, session, registration, risk, context

  - Async: True, Returns: bool

  - Cross-file communications:

    - Calls `permission_buffer_manager.get_permission_buffer_manager` at line 325 (unresolved)

      - Purpose: No docstring provided

      - Expression: `get_permission_buffer_manager`

    - Calls `traceback.print_exc` at line 350 (unresolved)

      - Purpose: No docstring provided

      - Expression: `traceback.print_exc`

- Function `PermissionManager.check_permission` (line 60)

  - Purpose: Check if execution should be permitted

  - Signature summary: positional=self, registration, context, app, session

  - Async: True, Returns: bool

  - Cross-file communications: none

- Function `PermissionManager.get_allowed_items` (line 459)

  - Purpose: Get all permanently allowed items

  - Signature summary: positional=self

  - Async: False, Returns: Dict[str, bool]

  - Cross-file communications: none

- Function `PermissionManager.remove_allowed_item` (line 463)

  - Purpose: Remove item from allowed list

  - Signature summary: positional=self, type, name

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `PermissionManager.set_auto_accept_permanent` (line 454)

  - Purpose: Enable/disable permanent auto-accept mode

  - Signature summary: positional=self, enabled

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `get_permission_manager` (line 478)

  - Purpose: Get or create global permission manager instance

  - Signature summary: positional=app, session

  - Async: False, Returns: None

  - Cross-file communications: none


## modules/execution/registry.py

- Module: `modules.execution.registry`

- Function `ExecutionRegistry.__init__` (line 109)

  - Purpose: No docstring provided

  - Signature summary: positional=self, config_dir

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path.home` at line 110 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.home`

- Function `ExecutionRegistry._load_registry_state` (line 431)

  - Purpose: Load enabled/disabled state

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.load` at line 438 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

- Function `ExecutionRegistry._load_usage_stats` (line 385)

  - Purpose: Load usage statistics from file

  - Signature summary: positional=self

  - Async: False, Returns: Dict[str, int]

  - Cross-file communications:

    - Calls `json.load` at line 392 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

- Function `ExecutionRegistry._save_registry_state` (line 450)

  - Purpose: Save enabled/disabled state

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.dump` at line 463 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dump`

- Function `ExecutionRegistry._save_usage_stats` (line 396)

  - Purpose: Save usage statistics to file

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.dump` at line 400 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dump`

- Function `ExecutionRegistry._score_match` (line 320)

  - Purpose: Calculate search score

  - Signature summary: positional=self, name, description, query, usage_count

  - Async: False, Returns: int

  - Cross-file communications: none

- Function `ExecutionRegistry.disable` (line 417)

  - Purpose: Disable command/tool/API

  - Signature summary: positional=self, type, name

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `ExecutionRegistry.enable` (line 408)

  - Purpose: Enable command/tool/API

  - Signature summary: positional=self, type, name

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `ExecutionRegistry.get` (line 177)

  - Purpose: Get registration by type and name

  - Signature summary: positional=self, type, name

  - Async: False, Returns: Optional[ExecutionRegistration]

  - Cross-file communications: none

- Function `ExecutionRegistry.get_all` (line 191)

  - Purpose: Get all registrations with optional filtering

  - Signature summary: positional=self, type, category, enabled_only

  - Async: False, Returns: List[ExecutionRegistration]

  - Cross-file communications: none

- Function `ExecutionRegistry.get_most_used` (line 375)

  - Purpose: Get most frequently used items

  - Signature summary: positional=self, type, limit

  - Async: False, Returns: List[ExecutionRegistration]

  - Cross-file communications: none

- Function `ExecutionRegistry.is_enabled` (line 426)

  - Purpose: Check if command/tool/API is enabled

  - Signature summary: positional=self, type, name

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `ExecutionRegistry.record_usage` (line 361)

  - Purpose: Track usage of command/tool/API

  - Signature summary: positional=self, type, name

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ExecutionRegistry.register` (line 129)

  - Purpose: Register command/tool/API

  - Signature summary: positional=self, type, name, handler, category, risk_level, requires_approval, description; kwarg=kwargs

  - Async: False, Returns: ExecutionRegistration

  - Cross-file communications: none

- Function `ExecutionRegistry.search_commands` (line 231)

  - Purpose: Search commands with priority-based ranking

  - Signature summary: positional=self, query, limit

  - Async: False, Returns: List[ExecutionRegistration]

  - Cross-file communications: none


## modules/execution/retry_manager.py

- Module: `modules.execution.retry_manager`

- Function `RetryManager.retry` (line 15)

  - Purpose: Retry function with exponential backoff

  - Signature summary: positional=func, max_retries, base_delay, max_delay; vararg=args; kwarg=kwargs

  - Async: True, Returns: Any

  - Cross-file communications:

    - Calls `asyncio.iscoroutinefunction` at line 45 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.iscoroutinefunction`

    - Calls `asyncio.to_thread` at line 48 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.to_thread`

    - Calls `asyncio.sleep` at line 65 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`


## modules/execution/unified_executor.py

- Module: `modules.execution.unified_executor`

- Function `ExecutionStep.__post_init__` (line 56)

  - Purpose: No docstring provided

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `UnifiedExecutionSystem.__init__` (line 75)

  - Purpose: No docstring provided

  - Signature summary: positional=self, app, session

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `modules.execution.registry.ExecutionRegistry` at line 80 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ExecutionRegistry`

    - Calls `modules.execution.permission_manager.UnifiedPermissionManager` at line 81 (unresolved)

      - Purpose: No docstring provided

      - Expression: `UnifiedPermissionManager`

    - Calls `modules.execution.async_runner.AsyncExecutionRunner` at line 82 (unresolved)

      - Purpose: No docstring provided

      - Expression: `AsyncExecutionRunner`

    - Calls `modules.execution.circuit_breaker.CircuitBreaker` at line 83 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CircuitBreaker`

    - Calls `modules.execution.retry_manager.RetryManager` at line 84 (unresolved)

      - Purpose: No docstring provided

      - Expression: `RetryManager`

- Function `UnifiedExecutionSystem._clear_statusline` (line 434)

  - Purpose: Clear statusline indicator

  - Signature summary: positional=self, label

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `UnifiedExecutionSystem._execute_single` (line 366)

  - Purpose: Execute single function (tool or simple command)

  - Signature summary: positional=self, registration, context

  - Async: True, Returns: Any

  - Cross-file communications:

    - Calls `asyncio.iscoroutinefunction` at line 392 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.iscoroutinefunction`

    - Calls `asyncio.sleep` at line 417 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

- Function `UnifiedExecutionSystem._execute_workflow` (line 191)

  - Purpose: Execute multi-step workflow with live progress IN PERMISSION BUFFER

  - Signature summary: positional=self, registration, steps, context

  - Async: True, Returns: List[Any]

  - Cross-file communications:

    - Calls `asyncio.iscoroutinefunction` at line 272 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.iscoroutinefunction`

    - Calls `asyncio.sleep` at line 313 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

- Function `UnifiedExecutionSystem._update_statusline` (line 425)

  - Purpose: Update statusline indicator

  - Signature summary: positional=self, label, icon, color

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `UnifiedExecutionSystem._wait_for_step_permission` (line 323)

  - Purpose: Show permission prompt for individual step

  - Signature summary: positional=self, step, workflow_status, prompt_input

  - Async: True, Returns: bool

  - Cross-file communications:

    - Calls `asyncio.sleep` at line 356 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

- Function `UnifiedExecutionSystem.execute` (line 93)

  - Purpose: Execute command/tool/API with unified flow

  - Signature summary: positional=self, type, name, steps; kwarg=context

  - Async: True, Returns: Any

  - Cross-file communications: none

- Function `UnifiedExecutionSystem.execute_api` (line 464)

  - Purpose: Execute API call by name

  - Signature summary: positional=self, name; kwarg=context

  - Async: True, Returns: Any

  - Cross-file communications: none

- Function `UnifiedExecutionSystem.execute_command` (line 447)

  - Purpose: Execute command by name

  - Signature summary: positional=self, name, steps; kwarg=context

  - Async: True, Returns: Any

  - Cross-file communications: none

- Function `UnifiedExecutionSystem.execute_tool` (line 456)

  - Purpose: Execute tool by name

  - Signature summary: positional=self, name; kwarg=context

  - Async: True, Returns: Any

  - Cross-file communications: none

- Function `get_execution_system` (line 477)

  - Purpose: Get or create global execution system

  - Signature summary: positional=app, session

  - Async: False, Returns: UnifiedExecutionSystem

  - Cross-file communications: none


## modules/frontier_colors.py

- Module: `modules.frontier_colors`

- Functions: none

## modules/github_tool.py

- Module: `modules.github_tool`

- Function `GitHubTool.check_auth` (line 16)

  - Purpose: Check if user is authenticated with gh CLI

  - Signature summary: (no parameters)

  - Async: False, Returns: Dict

  - Cross-file communications:

    - Calls `subprocess.run` at line 19 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `GitHubTool.execute_command` (line 48)

  - Purpose: Execute gh CLI command

  - Signature summary: positional=command, args

  - Async: False, Returns: str

  - Cross-file communications:

    - Calls `subprocess.run` at line 59 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `GitHubTool.gist_create` (line 192)

  - Purpose: Create gist from files

  - Signature summary: positional=files, description, public

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `GitHubTool.issue_create` (line 108)

  - Purpose: Create new issue

  - Signature summary: positional=title, body, repo

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `GitHubTool.issue_list` (line 87)

  - Purpose: List issues

  - Signature summary: positional=repo, limit, state

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `GitHubTool.issue_view` (line 97)

  - Purpose: View issue details

  - Signature summary: positional=number, repo

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `GitHubTool.pr_checkout` (line 153)

  - Purpose: Checkout pull request locally

  - Signature summary: positional=number, repo

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `GitHubTool.pr_create` (line 140)

  - Purpose: Create pull request

  - Signature summary: positional=title, body, base, head, repo

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `GitHubTool.pr_list` (line 119)

  - Purpose: List pull requests

  - Signature summary: positional=repo, limit, state

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `GitHubTool.pr_view` (line 129)

  - Purpose: View pull request details

  - Signature summary: positional=number, repo

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `GitHubTool.repo_view` (line 75)

  - Purpose: View repository details

  - Signature summary: positional=repo

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `GitHubTool.run_list` (line 182)

  - Purpose: List workflow runs

  - Signature summary: positional=repo, limit

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `GitHubTool.workflow_list` (line 162)

  - Purpose: List GitHub Actions workflows

  - Signature summary: positional=repo

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `GitHubTool.workflow_run` (line 173)

  - Purpose: Trigger workflow run

  - Signature summary: positional=workflow, repo

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `_build_repo_query` (line 209)

  - Purpose: Build GraphQL query for repo info

  - Signature summary: positional=repo

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `execute_github_tool` (line 216)

  - Purpose: Execute GitHub tool action

  - Signature summary: positional=action; kwarg=kwargs

  - Async: False, Returns: str

  - Cross-file communications:

    - Calls `json.dumps` at line 221 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dumps`


## modules/goal_tracker.py

- Module: `modules.goal_tracker`

- Function `GoalTracker.__init__` (line 23)

  - Purpose: Initialize goal tracker

  - Signature summary: positional=self, session_id, spec_memory, verbose

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `GoalTracker.add_progress` (line 120)

  - Purpose: Record progress on current goal

  - Signature summary: positional=self, action, result, metadata

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `datetime.datetime.now` at line 142 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

- Function `GoalTracker.complete_goal` (line 318)

  - Purpose: Mark current goal as complete

  - Signature summary: positional=self, outcome

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `datetime.datetime.now` at line 324 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

- Function `GoalTracker.create_checkpoint` (line 242)

  - Purpose: Create recovery checkpoint

  - Signature summary: positional=self, messages

  - Async: False, Returns: Dict

  - Cross-file communications:

    - Calls `uuid.uuid4` at line 253 (unresolved)

      - Purpose: No docstring provided

      - Expression: `uuid.uuid4`

    - Calls `datetime.datetime.now` at line 255 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

- Function `GoalTracker.get_context_for_system_message` (line 298)

  - Purpose: Format goal context for system message

  - Signature summary: positional=self

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `GoalTracker.get_goal_summary` (line 268)

  - Purpose: Get formatted summary of current goal and progress

  - Signature summary: positional=self

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `GoalTracker.get_statistics` (line 338)

  - Purpose: Get goal tracking statistics

  - Signature summary: positional=self

  - Async: False, Returns: Dict

  - Cross-file communications: none

- Function `GoalTracker.record_tool_call` (line 203)

  - Purpose: Record tool call with sanity check result

  - Signature summary: positional=self, tool_name, args, result, sanity_check

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `datetime.datetime.now` at line 217 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

- Function `GoalTracker.set_goal` (line 56)

  - Purpose: Set new goal and persist it

  - Signature summary: positional=self, description, phase, context

  - Async: False, Returns: str

  - Cross-file communications:

    - Calls `uuid.uuid4` at line 68 (unresolved)

      - Purpose: No docstring provided

      - Expression: `uuid.uuid4`

    - Calls `datetime.datetime.now` at line 76 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

- Function `GoalTracker.update_phase` (line 94)

  - Purpose: Move to next phase of goal

  - Signature summary: positional=self, new_phase

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `datetime.datetime.now` at line 104 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

- Function `GoalTracker.validate_tool_call` (line 148)

  - Purpose: Validate if tool call aligns with current goal (SANITY CHECK)

  - Signature summary: positional=self, tool_name, args

  - Async: False, Returns: Tuple[bool, str]

  - Cross-file communications: none


## modules/header_autoconfig.py

- Module: `modules.header_autoconfig`

- Function `_parse_headers_fallback` (line 103)

  - Purpose: Fallback parsing for other code example formats (curl, TypeScript, etc.)

  - Signature summary: positional=html

  - Async: False, Returns: Dict[str, str]

  - Cross-file communications:

    - Calls `re.search` at line 136 (unresolved)

      - Purpose: No docstring provided

      - Expression: `re.search`

- Function `_parse_headers_from_html` (line 50)

  - Purpose: Parse headers from Python example in HTML

  - Signature summary: positional=html

  - Async: False, Returns: Dict[str, str]

  - Cross-file communications:

    - Calls `re.search` at line 83 (unresolved)

      - Purpose: No docstring provided

      - Expression: `re.search`

- Function `auto_configure_headers` (line 162)

  - Purpose: Auto-configure headers for a model by fetching from API page

  - Signature summary: positional=model_id, current_headers

  - Async: True, Returns: Tuple[bool, Dict[str, str], str]

  - Cross-file communications: none

- Function `fetch_model_header_config` (line 11)

  - Purpose: Fetch required headers from model's API example page

  - Signature summary: positional=model_id

  - Async: True, Returns: Tuple[bool, Dict[str, str], str]

  - Cross-file communications:

    - Calls `httpx.AsyncClient` at line 24 (unresolved)

      - Purpose: No docstring provided

      - Expression: `httpx.AsyncClient`

- Function `get_default_headers` (line 149)

  - Purpose: Get default OpenCLI headers for OpenRouter

  - Signature summary: (no parameters)

  - Async: False, Returns: Dict[str, str]

  - Cross-file communications: none


## modules/input_widget/__init__.py

- Module: `modules.input_widget`

- Functions: none

## modules/input_widget/event_handler.py

- Module: `modules.input_widget.event_handler`

- Function `handle_key_event` (line 14)

  - Purpose: Handle key press with PERMISSION PRIORITY

  - Signature summary: positional=widget, event

  - Async: False, Returns: bool

  - Cross-file communications:

    - Calls `sys.stderr.write` at line 33 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.write`

    - Calls `sys.stderr.flush` at line 34 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.flush`

    - Calls `modules.input_widget.messages.PermissionCancelled` at line 67 (unresolved)

      - Purpose: No docstring provided

      - Expression: `PermissionCancelled`

    - Calls `modules.input_widget.messages.PermissionResponse` at line 62 (unresolved)

      - Purpose: No docstring provided

      - Expression: `PermissionResponse`

    - Calls `modules.input_widget.messages.CommandSuggestionNavigate` at line 84 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandSuggestionNavigate`

    - Calls `modules.input_widget.messages.CommandSuggestionSelect` at line 88 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandSuggestionSelect`

    - Calls `modules.input_widget.messages.HideCommandSuggestions` at line 92 (unresolved)

      - Purpose: No docstring provided

      - Expression: `HideCommandSuggestions`

- Function `handle_paste_event` (line 175)

  - Purpose: Handle paste events

  - Signature summary: positional=widget, event

  - Async: False, Returns: None

  - Cross-file communications: none


## modules/input_widget/messages.py

- Module: `modules.input_widget.messages`

- Function `CommandSuggestionNavigate.__init__` (line 42)

  - Purpose: No docstring provided

  - Signature summary: positional=self, direction

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `NavigationEvent.__init__` (line 54)

  - Purpose: No docstring provided

  - Signature summary: positional=self, event_type

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `PermissionResponse.__init__` (line 18)

  - Purpose: No docstring provided

  - Signature summary: positional=self, option

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ShowCommandSuggestions.__init__` (line 30)

  - Purpose: No docstring provided

  - Signature summary: positional=self, query

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `Submitted.__init__` (line 11)

  - Purpose: No docstring provided

  - Signature summary: positional=self, value

  - Async: False, Returns: None

  - Cross-file communications: none


## modules/input_widget/permission_renderer.py

- Module: `modules.input_widget.permission_renderer`

- Function `render_permission_prompt` (line 15)

  - Purpose: Render permission prompt with Frontier colors

  - Signature summary: positional=prompt_data, selected_option

  - Async: False, Returns: Text

  - Cross-file communications:

    - Calls `rich.text.Text` at line 26 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

    - Calls `frontier_colors.FRONTIER_COLORS.get` at line 40 (unresolved)

      - Purpose: No docstring provided

      - Expression: `FRONTIER_COLORS.get`

    - Calls `rich.style.Style` at line 115 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Style`

    - Calls `rich.text.Text.from_markup` at line 91 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text.from_markup`


## modules/input_widget/widget.py

- Module: `modules.input_widget.widget`

- Function `MultiLineInput.__init__` (line 42)

  - Purpose: No docstring provided

  - Signature summary: positional=self, placeholder; kwarg=kwargs

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `MultiLineInput._spin` (line 200)

  - Purpose: Async task that updates the spinner

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.sleep` at line 206 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

- Function `MultiLineInput.action_submit` (line 150)

  - Purpose: Submit the current value

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `modules.input_widget.messages.Submitted` at line 153 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Submitted`

- Function `MultiLineInput.clear` (line 155)

  - Purpose: Clear the input

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `MultiLineInput.on_blur` (line 59)

  - Purpose: Track when widget loses focus - trigger navigation event for permission auto-dismiss

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `sys.stderr.write` at line 67 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.write`

    - Calls `sys.stderr.flush` at line 68 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.flush`

    - Calls `modules.input_widget.messages.NavigationEvent` at line 72 (unresolved)

      - Purpose: No docstring provided

      - Expression: `NavigationEvent`

    - Calls `modules.input_widget.messages.PermissionCancelled` at line 75 (unresolved)

      - Purpose: No docstring provided

      - Expression: `PermissionCancelled`

- Function `MultiLineInput.on_focus` (line 52)

  - Purpose: Track when widget receives focus

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `sys.stderr.write` at line 55 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.write`

    - Calls `sys.stderr.flush` at line 56 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.flush`

- Function `MultiLineInput.on_key` (line 146)

  - Purpose: Handle key presses with PERMISSION PRIORITY

  - Signature summary: positional=self, event

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `modules.input_widget.event_handler.handle_key_event` at line 148 (ok)

      - Purpose: Handle key press with PERMISSION PRIORITY

      - Expression: `handle_key_event`

- Function `MultiLineInput.on_paste` (line 142)

  - Purpose: Handle paste events

  - Signature summary: positional=self, event

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `modules.input_widget.event_handler.handle_paste_event` at line 144 (ok)

      - Purpose: Handle paste events

      - Expression: `handle_paste_event`

- Function `MultiLineInput.render` (line 83)

  - Purpose: Render with PERMISSION PRIORITY

  - Signature summary: positional=self

  - Async: False, Returns: Text

  - Cross-file communications:

    - Calls `modules.input_widget.permission_renderer.render_permission_prompt` at line 90 (ok)

      - Purpose: Render permission prompt with Frontier colors

      - Expression: `render_permission_prompt`

    - Calls `rich.text.Text` at line 98 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

- Function `MultiLineInput.start_spinner` (line 181)

  - Purpose: Start the spinner animation

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `asyncio.create_task` at line 186 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.create_task`

- Function `MultiLineInput.stop_spinner` (line 188)

  - Purpose: Stop the spinner animation

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `MultiLineInput.watch_is_spinning` (line 210)

  - Purpose: React to spinning state changes

  - Signature summary: positional=self, old_value, new_value

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `MultiLineInput.watch_permission_prompt_data` (line 219)

  - Purpose: React to permission prompt changes - PRIORITY SYSTEM

  - Signature summary: positional=self, old_value, new_value

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `MultiLineInput.watch_spinner_frame` (line 215)

  - Purpose: React to frame changes

  - Signature summary: positional=self, old_value, new_value

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `MultiLineInput.watch_value` (line 160)

  - Purpose: Update when value changes - detect slash commands

  - Signature summary: positional=self, old_value, new_value

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `modules.input_widget.messages.ShowCommandSuggestions` at line 169 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ShowCommandSuggestions`

    - Calls `modules.input_widget.messages.HideCommandSuggestions` at line 173 (unresolved)

      - Purpose: No docstring provided

      - Expression: `HideCommandSuggestions`


## modules/ipc_shell_api.py

- Module: `modules.ipc_shell_api`

- Function `ShellAPI.__init__` (line 26)

  - Purpose: No docstring provided

  - Signature summary: positional=self, agent_name, description

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `opencli_ipc.IPCClient` at line 27 (unresolved)

      - Purpose: No docstring provided

      - Expression: `IPCClient`

- Function `ShellAPI._handle_message` (line 177)

  - Purpose: Handle incoming message from shell

  - Signature summary: positional=self, message

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `ShellAPI._handle_response` (line 193)

  - Purpose: Handle response from shell

  - Signature summary: positional=self, message

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `ShellAPI._wait_for_message` (line 198)

  - Purpose: Wait for a message to arrive

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.sleep` at line 201 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

- Function `ShellAPI._wait_for_response` (line 203)

  - Purpose: Wait for a response message

  - Signature summary: positional=self, msg_id

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.sleep` at line 213 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

- Function `ShellAPI.connect` (line 36)

  - Purpose: Connect to OpenCLI instance

  - Signature summary: positional=self, session_id

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `ShellAPI.disconnect` (line 41)

  - Purpose: Disconnect from OpenCLI instance

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `ShellAPI.execute_command` (line 89)

  - Purpose: Execute a command in the OpenCLI shell and get response

  - Signature summary: positional=self, command

  - Async: True, Returns: Dict[str, Any]

  - Cross-file communications: none

- Function `ShellAPI.get_shell_history` (line 137)

  - Purpose: Get message history from the shell

  - Signature summary: positional=self

  - Async: True, Returns: List[ShellMessage]

  - Cross-file communications: none

- Function `ShellAPI.get_shell_status` (line 161)

  - Purpose: Get current status of the shell

  - Signature summary: positional=self

  - Async: True, Returns: Dict[str, Any]

  - Cross-file communications: none

- Function `ShellAPI.on_message` (line 111)

  - Purpose: Register a callback for incoming messages

  - Signature summary: positional=self, callback

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ShellAPI.read_from_shell` (line 61)

  - Purpose: Read the next message from the shell

  - Signature summary: positional=self, timeout

  - Async: True, Returns: Optional[ShellMessage]

  - Cross-file communications:

    - Calls `asyncio.wait_for` at line 77 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.wait_for`

- Function `ShellAPI.stream_write` (line 120)

  - Purpose: Stream text to the shell (for real-time output)

  - Signature summary: positional=self, text_generator

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `ShellAPI.write_to_shell` (line 45)

  - Purpose: Write a message to the OpenCLI shell

  - Signature summary: positional=self, message, role

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `SubagentAPI.__aenter__` (line 280)

  - Purpose: Context manager support

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `SubagentAPI.__aexit__` (line 284)

  - Purpose: Context manager cleanup

  - Signature summary: positional=self, exc_type, exc_val, exc_tb

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `SubagentAPI.__init__` (line 225)

  - Purpose: No docstring provided

  - Signature summary: positional=self, agent_name, description

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `SubagentAPI.ask` (line 248)

  - Purpose: Ask a question and wait for response

  - Signature summary: positional=self, question, timeout

  - Async: True, Returns: Optional[str]

  - Cross-file communications: none

- Function `SubagentAPI.connect` (line 229)

  - Purpose: Connect to OpenCLI instance

  - Signature summary: positional=self, session_id

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `SubagentAPI.disconnect` (line 234)

  - Purpose: Disconnect from OpenCLI instance

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `SubagentAPI.on_receive` (line 262)

  - Purpose: Register callback for received messages

  - Signature summary: positional=self, callback

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `SubagentAPI.on_receive.wrapper` (line 264)

  - Purpose: No docstring provided

  - Signature summary: positional=msg

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `SubagentAPI.receive` (line 243)

  - Purpose: Receive a message from the shell

  - Signature summary: positional=self, timeout

  - Async: True, Returns: Optional[str]

  - Cross-file communications: none

- Function `SubagentAPI.run_command` (line 268)

  - Purpose: Run a command and get output

  - Signature summary: positional=self, command

  - Async: True, Returns: str

  - Cross-file communications: none

- Function `SubagentAPI.send` (line 239)

  - Purpose: Send a message to the shell

  - Signature summary: positional=self, message

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `SubagentAPI.stream_output` (line 276)

  - Purpose: Stream output to shell

  - Signature summary: positional=self, text_generator

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `connect_to_opencli` (line 292)

  - Purpose: Connect to an OpenCLI instance as a subagent

  - Signature summary: positional=session_id, agent_name, description

  - Async: True, Returns: SubagentAPI

  - Cross-file communications: none

- Function `send_to_opencli` (line 309)

  - Purpose: Quick send a message to OpenCLI without persistent connection

  - Signature summary: positional=session_id, message, agent_name

  - Async: True, Returns: None

  - Cross-file communications: none


## modules/markdown_renderer.py

- Module: `modules.markdown_renderer`

- Function `MarkdownRenderer.__init__` (line 18)

  - Purpose: No docstring provided

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `MarkdownRenderer._render_inline` (line 104)

  - Purpose: Render inline markdown elements (bold, italic, code, links)

  - Signature summary: positional=self, text

  - Async: False, Returns: Text

  - Cross-file communications:

    - Calls `rich.text.Text` at line 106 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

    - Calls `re.match` at line 135 (unresolved)

      - Purpose: No docstring provided

      - Expression: `re.match`

    - Calls `rich.style.Style` at line 146 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Style`

- Function `MarkdownRenderer.render` (line 21)

  - Purpose: Render markdown string to Rich Text object

  - Signature summary: positional=self, markdown_text

  - Async: False, Returns: Text

  - Cross-file communications:

    - Calls `rich.text.Text` at line 34 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

    - Calls `rich.style.Style` at line 86 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Style`

    - Calls `re.match` at line 80 (unresolved)

      - Purpose: No docstring provided

      - Expression: `re.match`

- Function `MarkdownRenderer.render_message` (line 151)

  - Purpose: Render a complete message (user or assistant) with proper formatting

  - Signature summary: positional=self, role, content, username

  - Async: False, Returns: Text

  - Cross-file communications:

    - Calls `rich.text.Text` at line 163 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

    - Calls `rich.style.Style` at line 181 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Style`

- Function `get_markdown_renderer` (line 191)

  - Purpose: Get the global markdown renderer instance

  - Signature summary: (no parameters)

  - Async: False, Returns: MarkdownRenderer

  - Cross-file communications: none


## modules/model_manager.py

- Module: `modules.model_manager`

- Function `ModelManager.__init__` (line 31)

  - Purpose: No docstring provided

  - Signature summary: positional=self, config_dir

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path.home` at line 32 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.home`

- Function `ModelManager._fetch_ollama_models` (line 691)

  - Purpose: Fetch models from Ollama server using /api/tags endpoint

  - Signature summary: positional=self, provider_info

  - Async: True, Returns: Dict

  - Cross-file communications:

    - Calls `httpx.AsyncClient` at line 698 (unresolved)

      - Purpose: No docstring provided

      - Expression: `httpx.AsyncClient`

- Function `ModelManager._fetch_openai_compatible` (line 648)

  - Purpose: Fetch models from OpenAI-compatible API

  - Signature summary: positional=self, provider, provider_info, api_key

  - Async: True, Returns: Dict

  - Cross-file communications:

    - Calls `httpx.AsyncClient` at line 665 (unresolved)

      - Purpose: No docstring provided

      - Expression: `httpx.AsyncClient`

- Function `ModelManager._get_anthropic_models` (line 736)

  - Purpose: Get predefined Anthropic models

  - Signature summary: positional=self

  - Async: False, Returns: Dict

  - Cross-file communications: none

- Function `ModelManager._get_google_models` (line 763)

  - Purpose: Get predefined Google AI models

  - Signature summary: positional=self

  - Async: False, Returns: Dict

  - Cross-file communications: none

- Function `ModelManager._load_config` (line 72)

  - Purpose: Load main config

  - Signature summary: positional=self

  - Async: False, Returns: Dict

  - Cross-file communications:

    - Calls `json.load` at line 79 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

- Function `ModelManager._load_models` (line 56)

  - Purpose: Load models database

  - Signature summary: positional=self

  - Async: False, Returns: Dict

  - Cross-file communications:

    - Calls `json.load` at line 60 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

    - Calls `copy.deepcopy` at line 66 (unresolved)

      - Purpose: No docstring provided

      - Expression: `deepcopy`

    - Calls `provider_settings.ensure_provider_defaults` at line 69 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ensure_provider_defaults`

- Function `ModelManager._save_config` (line 116)

  - Purpose: Save main config

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.dump` at line 119 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dump`

    - Calls `os.chmod` at line 122 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.chmod`

- Function `ModelManager._save_models` (line 107)

  - Purpose: Save models database

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.dump` at line 111 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dump`

    - Calls `os.chmod` at line 114 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.chmod`

- Function `ModelManager._save_to_secrets` (line 416)

  - Purpose: Save API key to .secrets file for compatibility

  - Signature summary: positional=self, provider, api_key

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.load` at line 424 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

    - Calls `json.dump` at line 440 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dump`

    - Calls `os.chmod` at line 443 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.chmod`

- Function `ModelManager._set_active_provider` (line 124)

  - Purpose: Update config to reflect active provider selection.

  - Signature summary: positional=self, provider, api_key

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ModelManager.add_api_key` (line 397)

  - Purpose: Add API key for provider

  - Signature summary: positional=self, provider, api_key

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ModelManager.detect_provider` (line 582)

  - Purpose: Auto-detect provider from API key format

  - Signature summary: positional=self, api_key

  - Async: False, Returns: Optional[str]

  - Cross-file communications: none

- Function `ModelManager.fetch_models_from_openrouter` (line 322)

  - Purpose: Fetch available models from OpenRouter API

  - Signature summary: positional=self, api_key

  - Async: True, Returns: Dict

  - Cross-file communications:

    - Calls `httpx.AsyncClient` at line 333 (unresolved)

      - Purpose: No docstring provided

      - Expression: `httpx.AsyncClient`

- Function `ModelManager.fetch_models_from_provider` (line 615)

  - Purpose: Fetch models from any supported provider

  - Signature summary: positional=self, provider, api_key

  - Async: True, Returns: Dict

  - Cross-file communications: none

- Function `ModelManager.get_configured_keys` (line 289)

  - Purpose: Get all configured API keys

  - Signature summary: positional=self

  - Async: False, Returns: Dict[str, str]

  - Cross-file communications:

    - Calls `json.load` at line 306 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

- Function `ModelManager.get_current_model` (line 484)

  - Purpose: Get current model from session or config

  - Signature summary: positional=self, session

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `ModelManager.get_provider_for_model` (line 163)

  - Purpose: Identify the provider associated with a given model.

  - Signature summary: positional=self, model_id

  - Async: False, Returns: Optional[str]

  - Cross-file communications: none

- Function `ModelManager.get_provider_headers` (line 189)

  - Purpose: Build effective headers for provider/model combination.

  - Signature summary: positional=self, provider, model_id

  - Async: False, Returns: Dict

  - Cross-file communications:

    - Calls `openrouter_headers.OpenRouterHeaderManager` at line 205 (unresolved)

      - Purpose: No docstring provided

      - Expression: `OpenRouterHeaderManager`

    - Calls `copy.deepcopy` at line 231 (unresolved)

      - Purpose: No docstring provided

      - Expression: `deepcopy`

    - Calls `os.getenv` at line 252 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.getenv`

- Function `ModelManager.get_provider_settings` (line 156)

  - Purpose: Return provider metadata with defaults applied.

  - Signature summary: positional=self, provider

  - Async: False, Returns: Dict

  - Cross-file communications:

    - Calls `copy.deepcopy` at line 160 (unresolved)

      - Purpose: No docstring provided

      - Expression: `deepcopy`

    - Calls `provider_settings.get_provider_defaults` at line 161 (unresolved)

      - Purpose: No docstring provided

      - Expression: `get_provider_defaults`

- Function `ModelManager.get_providers` (line 561)

  - Purpose: List configured providers

  - Signature summary: positional=self

  - Async: False, Returns: List[Dict]

  - Cross-file communications: none

- Function `ModelManager.get_recent_models` (line 543)

  - Purpose: Get recently used models with full info

  - Signature summary: positional=self

  - Async: False, Returns: List[Dict]

  - Cross-file communications: none

- Function `ModelManager.list_available_models` (line 445)

  - Purpose: List only models for which we have API keys

  - Signature summary: positional=self

  - Async: False, Returns: List[Dict]

  - Cross-file communications: none

- Function `ModelManager.list_available_models.sort_key` (line 468)

  - Purpose: No docstring provided

  - Signature summary: positional=m

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ModelManager.register_models` (line 374)

  - Purpose: Register models from API response

  - Signature summary: positional=self, provider, models

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ModelManager.switch_model` (line 490)

  - Purpose: Switch to a different model

  - Signature summary: positional=self, session, model_id

  - Async: False, Returns: Dict

  - Cross-file communications: none

- Function `ModelManager.update_provider_headers` (line 260)

  - Purpose: Persist custom headers for a provider (optionally scoped to a model).

  - Signature summary: positional=self, provider, new_headers, model_id

  - Async: False, Returns: None

  - Cross-file communications: none


## modules/model_recommendations.py

- Module: `modules.model_recommendations`

- Function `format_recommendation_text` (line 242)

  - Purpose: Format recommendations as readable text for CLI display

  - Signature summary: positional=recs, show_dual

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `get_ollama_pull_commands` (line 293)

  - Purpose: Generate ollama pull commands for recommended models

  - Signature summary: positional=recs, dual

  - Async: False, Returns: List[str]

  - Cross-file communications: none

- Function `get_recommendations` (line 217)

  - Purpose: Get model recommendations for a capability tier

  - Signature summary: positional=tier, is_apple_silicon

  - Async: False, Returns: Dict

  - Cross-file communications: none


## modules/multiline_input.py

- Module: `modules.multiline_input`

- Function `MultiLineInput.CommandSuggestionNavigate.__init__` (line 66)

  - Purpose: No docstring provided

  - Signature summary: positional=self, direction

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `MultiLineInput.NavigationEvent.__init__` (line 76)

  - Purpose: No docstring provided

  - Signature summary: positional=self, event_type

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `MultiLineInput.PermissionResponse.__init__` (line 46)

  - Purpose: No docstring provided

  - Signature summary: positional=self, option

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `MultiLineInput.ShowCommandSuggestions.__init__` (line 56)

  - Purpose: No docstring provided

  - Signature summary: positional=self, query

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `MultiLineInput.Submitted.__init__` (line 40)

  - Purpose: No docstring provided

  - Signature summary: positional=self, value

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `MultiLineInput.__init__` (line 80)

  - Purpose: No docstring provided

  - Signature summary: positional=self, placeholder; kwarg=kwargs

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `MultiLineInput._render_permission_prompt` (line 174)

  - Purpose: Render permission prompt with Frontier colors (no extra borders - prompt box is the border)

  - Signature summary: positional=self

  - Async: False, Returns: Text

  - Cross-file communications:

    - Calls `rich.text.Text` at line 178 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

    - Calls `frontier_colors.FRONTIER_COLORS.get` at line 192 (unresolved)

      - Purpose: No docstring provided

      - Expression: `FRONTIER_COLORS.get`

    - Calls `rich.style.Style` at line 269 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Style`

    - Calls `rich.text.Text.from_markup` at line 244 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text.from_markup`

- Function `MultiLineInput._spin` (line 522)

  - Purpose: Async task that updates the spinner

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.sleep` at line 528 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

- Function `MultiLineInput._wrap_text` (line 273)

  - Purpose: Wrap text to fit width

  - Signature summary: positional=self, text, width

  - Async: False, Returns: list[str]

  - Cross-file communications: none

- Function `MultiLineInput.action_submit` (line 458)

  - Purpose: Submit the current value

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `MultiLineInput.clear` (line 463)

  - Purpose: Clear the input

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `MultiLineInput.on_blur` (line 97)

  - Purpose: Track when widget loses focus - trigger navigation event for permission auto-dismiss

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `sys.stderr.write` at line 105 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.write`

    - Calls `sys.stderr.flush` at line 106 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.flush`

- Function `MultiLineInput.on_focus` (line 90)

  - Purpose: Track when widget receives focus

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `sys.stderr.write` at line 93 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.write`

    - Calls `sys.stderr.flush` at line 94 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.flush`

- Function `MultiLineInput.on_key` (line 319)

  - Purpose: Handle key presses

  - Signature summary: positional=self, event

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `sys.stderr.write` at line 330 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.write`

    - Calls `sys.stderr.flush` at line 331 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.flush`

- Function `MultiLineInput.on_paste` (line 299)

  - Purpose: Handle paste events

  - Signature summary: positional=self, event

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `MultiLineInput.render` (line 120)

  - Purpose: Render the current input with cursor or permission prompt

  - Signature summary: positional=self

  - Async: False, Returns: Text

  - Cross-file communications:

    - Calls `rich.text.Text` at line 128 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

- Function `MultiLineInput.start_spinner` (line 503)

  - Purpose: Start the spinner animation

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `asyncio.create_task` at line 508 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.create_task`

- Function `MultiLineInput.stop_spinner` (line 510)

  - Purpose: Stop the spinner animation

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `MultiLineInput.watch_is_spinning` (line 532)

  - Purpose: React to spinning state changes

  - Signature summary: positional=self, old_value, new_value

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `MultiLineInput.watch_permission_prompt_data` (line 541)

  - Purpose: React to permission prompt data changes - trigger layout update

  - Signature summary: positional=self, old_value, new_value

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `MultiLineInput.watch_spinner_frame` (line 537)

  - Purpose: React to frame changes - refresh already handled by _spin

  - Signature summary: positional=self, old_value, new_value

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `MultiLineInput.watch_value` (line 468)

  - Purpose: Update when value changes - detect slash commands

  - Signature summary: positional=self, old_value, new_value

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `os.getenv` at line 497 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.getenv`


## modules/multiline_input_backup.py

- Module: `modules.multiline_input_backup`

- Function `MultiLineInput.CommandSuggestionNavigate.__init__` (line 66)

  - Purpose: No docstring provided

  - Signature summary: positional=self, direction

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `MultiLineInput.NavigationEvent.__init__` (line 76)

  - Purpose: No docstring provided

  - Signature summary: positional=self, event_type

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `MultiLineInput.PermissionResponse.__init__` (line 46)

  - Purpose: No docstring provided

  - Signature summary: positional=self, option

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `MultiLineInput.ShowCommandSuggestions.__init__` (line 56)

  - Purpose: No docstring provided

  - Signature summary: positional=self, query

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `MultiLineInput.Submitted.__init__` (line 40)

  - Purpose: No docstring provided

  - Signature summary: positional=self, value

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `MultiLineInput.__init__` (line 80)

  - Purpose: No docstring provided

  - Signature summary: positional=self, placeholder; kwarg=kwargs

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `MultiLineInput._render_permission_prompt` (line 174)

  - Purpose: Render permission prompt with Frontier colors (no extra borders - prompt box is the border)

  - Signature summary: positional=self

  - Async: False, Returns: Text

  - Cross-file communications:

    - Calls `rich.text.Text` at line 178 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

    - Calls `frontier_colors.FRONTIER_COLORS.get` at line 192 (unresolved)

      - Purpose: No docstring provided

      - Expression: `FRONTIER_COLORS.get`

    - Calls `rich.style.Style` at line 269 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Style`

    - Calls `rich.text.Text.from_markup` at line 244 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text.from_markup`

- Function `MultiLineInput._spin` (line 522)

  - Purpose: Async task that updates the spinner

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.sleep` at line 528 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

- Function `MultiLineInput._wrap_text` (line 273)

  - Purpose: Wrap text to fit width

  - Signature summary: positional=self, text, width

  - Async: False, Returns: list[str]

  - Cross-file communications: none

- Function `MultiLineInput.action_submit` (line 458)

  - Purpose: Submit the current value

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `MultiLineInput.clear` (line 463)

  - Purpose: Clear the input

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `MultiLineInput.on_blur` (line 97)

  - Purpose: Track when widget loses focus - trigger navigation event for permission auto-dismiss

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `sys.stderr.write` at line 105 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.write`

    - Calls `sys.stderr.flush` at line 106 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.flush`

- Function `MultiLineInput.on_focus` (line 90)

  - Purpose: Track when widget receives focus

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `sys.stderr.write` at line 93 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.write`

    - Calls `sys.stderr.flush` at line 94 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.flush`

- Function `MultiLineInput.on_key` (line 319)

  - Purpose: Handle key presses

  - Signature summary: positional=self, event

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `sys.stderr.write` at line 330 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.write`

    - Calls `sys.stderr.flush` at line 331 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.flush`

- Function `MultiLineInput.on_paste` (line 299)

  - Purpose: Handle paste events

  - Signature summary: positional=self, event

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `MultiLineInput.render` (line 120)

  - Purpose: Render the current input with cursor or permission prompt

  - Signature summary: positional=self

  - Async: False, Returns: Text

  - Cross-file communications:

    - Calls `rich.text.Text` at line 128 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

- Function `MultiLineInput.start_spinner` (line 503)

  - Purpose: Start the spinner animation

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `asyncio.create_task` at line 508 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.create_task`

- Function `MultiLineInput.stop_spinner` (line 510)

  - Purpose: Stop the spinner animation

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `MultiLineInput.watch_is_spinning` (line 532)

  - Purpose: React to spinning state changes

  - Signature summary: positional=self, old_value, new_value

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `MultiLineInput.watch_permission_prompt_data` (line 541)

  - Purpose: React to permission prompt data changes - trigger layout update

  - Signature summary: positional=self, old_value, new_value

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `MultiLineInput.watch_spinner_frame` (line 537)

  - Purpose: React to frame changes - refresh already handled by _spin

  - Signature summary: positional=self, old_value, new_value

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `MultiLineInput.watch_value` (line 468)

  - Purpose: Update when value changes - detect slash commands

  - Signature summary: positional=self, old_value, new_value

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `os.getenv` at line 497 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.getenv`


## modules/opencli_ipc.py

- Module: `modules.opencli_ipc`

- Function `IPCClient.__init__` (line 275)

  - Purpose: No docstring provided

  - Signature summary: positional=self, agent_name, description, metadata

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `uuid.uuid4` at line 276 (unresolved)

      - Purpose: No docstring provided

      - Expression: `uuid.uuid4`

- Function `IPCClient._receive_loop` (line 370)

  - Purpose: Continuously receive messages

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `IPCClient._receive_message` (line 362)

  - Purpose: Receive a message from server

  - Signature summary: positional=self

  - Async: True, Returns: IPCMessage

  - Cross-file communications: none

- Function `IPCClient._send_message` (line 354)

  - Purpose: Send message to server

  - Signature summary: positional=self, message

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `IPCClient.connect` (line 287)

  - Purpose: Connect to OpenCLI instance

  - Signature summary: positional=self, session_id, socket_dir

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `os.path.join` at line 289 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.path.join`

    - Calls `os.path.exists` at line 291 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.path.exists`

    - Calls `asyncio.open_unix_connection` at line 295 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.open_unix_connection`

    - Calls `datetime.datetime.now` at line 307 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

    - Calls `uuid.uuid4` at line 308 (unresolved)

      - Purpose: No docstring provided

      - Expression: `uuid.uuid4`

    - Calls `asyncio.create_task` at line 320 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.create_task`

- Function `IPCClient.disconnect` (line 326)

  - Purpose: Disconnect from OpenCLI instance

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `datetime.datetime.now` at line 337 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

    - Calls `uuid.uuid4` at line 338 (unresolved)

      - Purpose: No docstring provided

      - Expression: `uuid.uuid4`

- Function `IPCClient.register_handler` (line 405)

  - Purpose: Register a message handler

  - Signature summary: positional=self, msg_type, handler

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `IPCClient.send_heartbeat` (line 401)

  - Purpose: Send heartbeat to maintain connection

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `IPCClient.send_message` (line 385)

  - Purpose: Send message to OpenCLI main instance

  - Signature summary: positional=self, msg_type, payload

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `datetime.datetime.now` at line 395 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

    - Calls `uuid.uuid4` at line 396 (unresolved)

      - Purpose: No docstring provided

      - Expression: `uuid.uuid4`

- Function `IPCMessage.from_json` (line 55)

  - Purpose: Deserialize from JSON

  - Signature summary: positional=data

  - Async: False, Returns: 'IPCMessage'

  - Cross-file communications:

    - Calls `json.loads` at line 57 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.loads`

- Function `IPCMessage.to_json` (line 50)

  - Purpose: Serialize to JSON

  - Signature summary: positional=self

  - Async: False, Returns: str

  - Cross-file communications:

    - Calls `json.dumps` at line 52 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dumps`

    - Calls `dataclasses.asdict` at line 52 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asdict`

- Function `IPCServer.__init__` (line 78)

  - Purpose: No docstring provided

  - Signature summary: positional=self, session_id, socket_dir

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `os.path.join` at line 80 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.path.join`

    - Calls `pathlib.Path` at line 88 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

    - Calls `os.path.exists` at line 91 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.path.exists`

    - Calls `os.unlink` at line 92 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.unlink`

- Function `IPCServer._handle_client` (line 123)

  - Purpose: Handle a client connection

  - Signature summary: positional=self, reader, writer

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `IPCServer._handle_heartbeat` (line 204)

  - Purpose: Handle heartbeat from subagent

  - Signature summary: positional=self, message

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `IPCServer._handle_registration` (line 162)

  - Purpose: Handle subagent registration

  - Signature summary: positional=self, message, writer

  - Async: True, Returns: str

  - Cross-file communications:

    - Calls `datetime.datetime.now` at line 186 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

    - Calls `uuid.uuid4` at line 187 (unresolved)

      - Purpose: No docstring provided

      - Expression: `uuid.uuid4`

- Function `IPCServer._handle_unregistration` (line 195)

  - Purpose: Handle subagent unregistration

  - Signature summary: positional=self, message

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `IPCServer._route_message` (line 210)

  - Purpose: Route message to appropriate handler

  - Signature summary: positional=self, message

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `IPCServer._send_message` (line 216)

  - Purpose: Send a message to a client

  - Signature summary: positional=self, writer, message

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `IPCServer.broadcast` (line 224)

  - Purpose: Broadcast message to all subagents

  - Signature summary: positional=self, msg_type, payload, exclude

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `datetime.datetime.now` at line 231 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

    - Calls `uuid.uuid4` at line 232 (unresolved)

      - Purpose: No docstring provided

      - Expression: `uuid.uuid4`

- Function `IPCServer.get_subagent_count` (line 260)

  - Purpose: Get number of registered subagents

  - Signature summary: positional=self

  - Async: False, Returns: int

  - Cross-file communications: none

- Function `IPCServer.get_subagents` (line 264)

  - Purpose: Get list of all subagents

  - Signature summary: positional=self

  - Async: False, Returns: List[SubagentInfo]

  - Cross-file communications: none

- Function `IPCServer.register_handler` (line 256)

  - Purpose: Register a message handler

  - Signature summary: positional=self, msg_type, handler

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `IPCServer.send_to_agent` (line 239)

  - Purpose: Send message to specific subagent

  - Signature summary: positional=self, agent_id, msg_type, payload

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `datetime.datetime.now` at line 249 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

    - Calls `uuid.uuid4` at line 250 (unresolved)

      - Purpose: No docstring provided

      - Expression: `uuid.uuid4`

- Function `IPCServer.start` (line 94)

  - Purpose: Start the IPC server

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.start_unix_server` at line 96 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.start_unix_server`

- Function `IPCServer.stop` (line 103)

  - Purpose: Stop the IPC server

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `os.path.exists` at line 118 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.path.exists`

    - Calls `os.unlink` at line 119 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.unlink`

- Function `create_ipc_client` (line 417)

  - Purpose: Create and return an IPC client instance

  - Signature summary: positional=agent_name, description, metadata

  - Async: False, Returns: IPCClient

  - Cross-file communications: none

- Function `create_ipc_server` (line 411)

  - Purpose: Create and return an IPC server instance

  - Signature summary: positional=session_id

  - Async: False, Returns: IPCServer

  - Cross-file communications: none


## modules/openrouter_headers.py

- Module: `modules.openrouter_headers`

- Function `OpenRouterHeaderManager.__init__` (line 42)

  - Purpose: Initialize header manager

  - Signature summary: positional=self, cache_dir

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path.home` at line 49 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.home`

- Function `OpenRouterHeaderManager._cache_headers` (line 240)

  - Purpose: Save headers to cache

  - Signature summary: positional=self, model_id, headers

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `datetime.datetime.now` at line 250 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

- Function `OpenRouterHeaderManager._extract_headers_from_code` (line 165)

  - Purpose: Extract headers from code example text using regex

  - Signature summary: positional=self, code_text

  - Async: False, Returns: Dict[str, str]

  - Cross-file communications:

    - Calls `re.search` at line 204 (unresolved)

      - Purpose: No docstring provided

      - Expression: `re.search`

- Function `OpenRouterHeaderManager._fetch_headers_from_api_page` (line 77)

  - Purpose: Fetch and parse headers from model's API page

  - Signature summary: positional=self, model_id

  - Async: False, Returns: Dict[str, str]

  - Cross-file communications:

    - Calls `httpx.get` at line 91 (unresolved)

      - Purpose: No docstring provided

      - Expression: `httpx.get`

- Function `OpenRouterHeaderManager._get_default_headers` (line 211)

  - Purpose: Default headers for OpenCLI

  - Signature summary: positional=self

  - Async: False, Returns: Dict[str, str]

  - Cross-file communications: none

- Function `OpenRouterHeaderManager._is_cache_valid` (line 223)

  - Purpose: Check if cached headers are still valid (24 hour TTL)

  - Signature summary: positional=self, cached_entry

  - Async: False, Returns: bool

  - Cross-file communications:

    - Calls `datetime.datetime.fromisoformat` at line 234 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.fromisoformat`

    - Calls `datetime.datetime.now` at line 235 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

    - Calls `datetime.timedelta` at line 236 (unresolved)

      - Purpose: No docstring provided

      - Expression: `timedelta`

- Function `OpenRouterHeaderManager._load_cache` (line 254)

  - Purpose: Load cached headers from disk

  - Signature summary: positional=self

  - Async: False, Returns: dict

  - Cross-file communications:

    - Calls `json.load` at line 264 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

- Function `OpenRouterHeaderManager._parse_headers` (line 107)

  - Purpose: Parse HTTP-Referer and X-Title from API page HTML

  - Signature summary: positional=self, html_content

  - Async: False, Returns: Dict[str, str]

  - Cross-file communications:

    - Calls `bs4.BeautifulSoup` at line 123 (unresolved)

      - Purpose: No docstring provided

      - Expression: `BeautifulSoup`

    - Calls `json.loads` at line 142 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.loads`

- Function `OpenRouterHeaderManager._save_cache` (line 269)

  - Purpose: Save cache to disk

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.dump` at line 276 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dump`

- Function `OpenRouterHeaderManager.clear_cache` (line 280)

  - Purpose: Clear all cached headers

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `OpenRouterHeaderManager.get_headers_for_model` (line 53)

  - Purpose: Get headers for a specific OpenRouter model

  - Signature summary: positional=self, model_id

  - Async: False, Returns: Dict[str, str]

  - Cross-file communications: none


## modules/performance_monitor.py

- Module: `modules.performance_monitor`

- Function `PerformanceMonitor.__init__` (line 18)

  - Purpose: No docstring provided

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `psutil.Process` at line 20 (unresolved)

      - Purpose: No docstring provided

      - Expression: `psutil.Process`

    - Calls `threading.Event` at line 22 (unresolved)

      - Purpose: No docstring provided

      - Expression: `threading.Event`

    - Calls `collections.deque` at line 40 (unresolved)

      - Purpose: No docstring provided

      - Expression: `deque`

- Function `PerformanceMonitor._calculate_token_rate` (line 102)

  - Purpose: Calculate tokens per second from recent timestamps

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `time.time` at line 109 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

- Function `PerformanceMonitor._detect_hotspot` (line 121)

  - Purpose: AGGRESSIVE thread profiling - ALL threads, FULL stacks, ALL files

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `sys._current_frames` at line 125 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys._current_frames`

    - Calls `traceback.extract_stack` at line 134 (unresolved)

      - Purpose: No docstring provided

      - Expression: `traceback.extract_stack`

- Function `PerformanceMonitor._monitor_loop` (line 59)

  - Purpose: Background thread - LIGHTWEIGHT metrics only

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `datetime.datetime.now` at line 70 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

- Function `PerformanceMonitor.get_cpu_trend` (line 176)

  - Purpose: Get CPU trend: rising, falling, stable

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `PerformanceMonitor.get_detailed_report` (line 249)

  - Purpose: Generate detailed performance report

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `PerformanceMonitor.get_status_line` (line 193)

  - Purpose: Generate statusline string for display

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `PerformanceMonitor.record_token` (line 170)

  - Purpose: Call this when a token is received/displayed

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `time.time` at line 172 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

- Function `PerformanceMonitor.start` (line 42)

  - Purpose: Start background monitoring thread

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `threading.Thread` at line 49 (unresolved)

      - Purpose: No docstring provided

      - Expression: `threading.Thread`

- Function `PerformanceMonitor.stop` (line 52)

  - Purpose: Stop background monitoring

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `get_monitor` (line 318)

  - Purpose: Get or create global performance monitor

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications: none


## modules/permission_buffer/__init__.py

- Module: `modules.permission_buffer`

- Functions: none

## modules/permission_buffer/enums.py

- Module: `modules.permission_buffer.enums`

- Functions: none

## modules/permission_buffer/manager.py

- Module: `modules.permission_buffer.manager`

- Function `PermissionBufferManager.__init__` (line 16)

  - Purpose: No docstring provided

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `threading.Lock` at line 18 (unresolved)

      - Purpose: No docstring provided

      - Expression: `threading.Lock`

- Function `PermissionBufferManager._auto_dismiss_task` (line 156)

  - Purpose: Auto-dismiss a task that has expired

  - Signature summary: positional=self, task

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `PermissionBufferManager._clear_ui` (line 162)

  - Purpose: Clear the permission prompt from the UI

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `PermissionBufferManager._process_queue` (line 68)

  - Purpose: Process the permission prompt queue

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `heapq.heappop` at line 81 (unresolved)

      - Purpose: No docstring provided

      - Expression: `heapq.heappop`

- Function `PermissionBufferManager._process_task` (line 94)

  - Purpose: Process a single permission task

  - Signature summary: positional=self, task

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `PermissionBufferManager._resolve_task` (line 128)

  - Purpose: Resolve a permission task with the given result

  - Signature summary: positional=self, task, result

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `PermissionBufferManager._show_in_ui` (line 113)

  - Purpose: Display the permission prompt in the UI

  - Signature summary: positional=self, task

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `PermissionBufferManager.cancel_current_prompt` (line 175)

  - Purpose: Cancel the currently displayed prompt

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `PermissionBufferManager.clear_queue` (line 185)

  - Purpose: Clear all pending prompts

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `heapq.heappop` at line 189 (unresolved)

      - Purpose: No docstring provided

      - Expression: `heapq.heappop`

- Function `PermissionBufferManager.get_stats` (line 181)

  - Purpose: Get performance statistics

  - Signature summary: positional=self

  - Async: False, Returns: Dict[str, Any]

  - Cross-file communications: none

- Function `PermissionBufferManager.handle_user_response` (line 170)

  - Purpose: Handle user response to the current permission prompt

  - Signature summary: positional=self, response

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `PermissionBufferManager.request_permission` (line 40)

  - Purpose: Request permission with priority-based queuing

  - Signature summary: positional=self, prompt_data, priority, auto_dismiss_after, callback

  - Async: True, Returns: Dict[str, Any]

  - Cross-file communications:

    - Calls `modules.permission_buffer.task._PromptTask` at line 49 (unresolved)

      - Purpose: No docstring provided

      - Expression: `_PromptTask`

    - Calls `asyncio.Future` at line 54 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.Future`

    - Calls `heapq.heappush` at line 58 (unresolved)

      - Purpose: No docstring provided

      - Expression: `heapq.heappush`

    - Calls `asyncio.create_task` at line 63 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.create_task`

- Function `PermissionBufferManager.set_app_context` (line 35)

  - Purpose: Set the TUI application context for UI integration

  - Signature summary: positional=self, app, prompt_input

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `get_permission_buffer_manager` (line 198)

  - Purpose: Get the global permission buffer manager instance

  - Signature summary: (no parameters)

  - Async: False, Returns: PermissionBufferManager

  - Cross-file communications: none


## modules/permission_buffer/task.py

- Module: `modules.permission_buffer.task`

- Function `_PromptTask.__lt__` (line 28)

  - Purpose: For priority queue ordering (lower number = higher priority)

  - Signature summary: positional=self, other

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `_PromptTask.should_auto_dismiss` (line 34)

  - Purpose: Check if this task should be auto-dismissed

  - Signature summary: positional=self

  - Async: False, Returns: bool

  - Cross-file communications:

    - Calls `time.time` at line 38 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

- Function `_PromptTask.to_dict` (line 40)

  - Purpose: Convert task to dictionary for serialization

  - Signature summary: positional=self

  - Async: False, Returns: Dict[str, Any]

  - Cross-file communications: none


## modules/permission_buffer_manager.py

- Module: `modules.permission_buffer_manager`

- Function `PermissionBufferManager.clear` (line 35)

  - Purpose: No docstring provided

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `PermissionBufferManager.get_active_task_count` (line 37)

  - Purpose: No docstring provided

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `PermissionBufferManager.resolve` (line 36)

  - Purpose: No docstring provided

  - Signature summary: positional=self, option

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `get_permission_buffer_manager` (line 39)

  - Purpose: No docstring provided

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `modules.permissions.get_unified_permission_manager` at line 20 (unresolved)

      - Purpose: No docstring provided

      - Expression: `get_unified_permission_manager`

    - Calls `permission_buffer.PermissionBufferManager` at line 40 (unresolved)

      - Purpose: No docstring provided

      - Expression: `PermissionBufferManager`


## modules/permission_prompt.py

- Module: `modules.permission_prompt`

- Function `get_unified_permission_manager` (line 40)

  - Purpose: No docstring provided

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications: none


## modules/permission_workflow.py

- Module: `modules.permission_workflow`

- Function `PermissionWorkflow.__init__` (line 41)

  - Purpose: No docstring provided

  - Signature summary: positional=self, workflow_id, title, steps

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `PermissionWorkflow.approve_current_step` (line 99)

  - Purpose: Mark current step as approved

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `PermissionWorkflow.cancel` (line 139)

  - Purpose: Cancel the workflow

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `PermissionWorkflow.execute_current_step` (line 105)

  - Purpose: Execute the current step

  - Signature summary: positional=self

  - Async: True, Returns: bool

  - Cross-file communications: none

- Function `PermissionWorkflow.get_current_step` (line 49)

  - Purpose: Get the current step

  - Signature summary: positional=self

  - Async: False, Returns: Optional[WorkflowStep]

  - Cross-file communications: none

- Function `PermissionWorkflow.get_permission_prompt_for_current_step` (line 72)

  - Purpose: Get permission prompt data for current step

  - Signature summary: positional=self

  - Async: False, Returns: Optional[Dict]

  - Cross-file communications: none

- Function `PermissionWorkflow.get_status_summary` (line 55)

  - Purpose: Get summary of workflow status

  - Signature summary: positional=self

  - Async: False, Returns: Dict

  - Cross-file communications: none

- Function `PermissionWorkflow.next_step` (line 129)

  - Purpose: Move to next step

  - Signature summary: positional=self

  - Async: True, Returns: bool

  - Cross-file communications: none

- Function `WorkflowManager.__init__` (line 150)

  - Purpose: No docstring provided

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `WorkflowManager.create_workflow` (line 153)

  - Purpose: Create and register a new workflow

  - Signature summary: positional=self, workflow_id, title, steps

  - Async: False, Returns: PermissionWorkflow

  - Cross-file communications: none

- Function `WorkflowManager.get_active_workflows` (line 168)

  - Purpose: Get all active workflows

  - Signature summary: positional=self

  - Async: False, Returns: List[PermissionWorkflow]

  - Cross-file communications: none

- Function `WorkflowManager.get_workflow` (line 159)

  - Purpose: Get a workflow by ID

  - Signature summary: positional=self, workflow_id

  - Async: False, Returns: Optional[PermissionWorkflow]

  - Cross-file communications: none

- Function `WorkflowManager.remove_workflow` (line 163)

  - Purpose: Remove a completed workflow

  - Signature summary: positional=self, workflow_id

  - Async: False, Returns: None

  - Cross-file communications: none


## modules/permissions/__init__.py

- Module: `modules.permissions`

- Functions: none

## modules/permissions/analytics.py

- Module: `modules.permissions.analytics`

- Function `AnalyticsManager.__init__` (line 16)

  - Purpose: No docstring provided

  - Signature summary: positional=self, enabled, max_response_times

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `AnalyticsManager._add_response_time` (line 104)

  - Purpose: Add response time to tracking

  - Signature summary: positional=self, response_time

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `AnalyticsManager._assess_system_health` (line 213)

  - Purpose: Assess overall system health

  - Signature summary: positional=self

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `AnalyticsManager._calculate_performance_score` (line 185)

  - Purpose: Calculate overall performance score (0-100)

  - Signature summary: positional=self

  - Async: False, Returns: float

  - Cross-file communications: none

- Function `AnalyticsManager._export_as_csv` (line 256)

  - Purpose: Export analytics as CSV format

  - Signature summary: positional=self, data

  - Async: False, Returns: str

  - Cross-file communications:

    - Calls `io.StringIO` at line 261 (unresolved)

      - Purpose: No docstring provided

      - Expression: `io.StringIO`

    - Calls `csv.writer` at line 262 (unresolved)

      - Purpose: No docstring provided

      - Expression: `csv.writer`

- Function `AnalyticsManager._format_uptime` (line 228)

  - Purpose: Format uptime in human readable format

  - Signature summary: positional=self, seconds

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `AnalyticsManager._initialize_metrics` (line 22)

  - Purpose: Initialize metrics tracking (Constitution compliant)

  - Signature summary: positional=self

  - Async: False, Returns: Dict[str, Any]

  - Cross-file communications:

    - Calls `datetime.datetime.now` at line 43 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

- Function `AnalyticsManager._update_response_time_stats` (line 119)

  - Purpose: Update response time statistics

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `AnalyticsManager.enabled` (line 288)

  - Purpose: Check if analytics is enabled

  - Signature summary: positional=self

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `AnalyticsManager.export_analytics` (line 242)

  - Purpose: Export analytics data in specified format (Constitution compliant)

  - Signature summary: positional=self, format

  - Async: False, Returns: str

  - Cross-file communications:

    - Calls `json.dumps` at line 250 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dumps`

- Function `AnalyticsManager.get_analytics_report` (line 127)

  - Purpose: Generate comprehensive analytics report (Constitution compliant)

  - Signature summary: positional=self

  - Async: False, Returns: Dict[str, Any]

  - Cross-file communications:

    - Calls `datetime.datetime.fromisoformat` at line 178 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.fromisoformat`

    - Calls `datetime.datetime.now` at line 179 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

- Function `AnalyticsManager.get_recent_response_times` (line 283)

  - Purpose: Get recent response times

  - Signature summary: positional=self, limit

  - Async: False, Returns: List[float]

  - Cross-file communications: none

- Function `AnalyticsManager.reset_analytics` (line 278)

  - Purpose: Reset all analytics data (Constitution compliant)

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `AnalyticsManager.set_enabled` (line 292)

  - Purpose: Enable or disable analytics

  - Signature summary: positional=self, enabled

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `AnalyticsManager.update_analytics` (line 46)

  - Purpose: Update analytics tracking (Constitution compliant)

  - Signature summary: positional=self, event_type, task, details

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `time.time` at line 51 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`


## modules/permissions/audit.py

- Module: `modules.permissions.audit`

- Function `AuditManager.__init__` (line 16)

  - Purpose: No docstring provided

  - Signature summary: positional=self, enabled, max_entries

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `threading.Lock` at line 20 (unresolved)

      - Purpose: No docstring provided

      - Expression: `threading.Lock`

- Function `AuditManager.clear_audit_log` (line 111)

  - Purpose: Clear all audit log entries

  - Signature summary: positional=self

  - Async: False, Returns: int

  - Cross-file communications: none

- Function `AuditManager.enabled` (line 123)

  - Purpose: Check if audit logging is enabled

  - Signature summary: positional=self

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `AuditManager.export_audit_log` (line 62)

  - Purpose: Export audit log for security analysis (Constitution compliant)

  - Signature summary: positional=self, format

  - Async: False, Returns: str

  - Cross-file communications:

    - Calls `json.dumps` at line 71 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dumps`

- Function `AuditManager.get_audit_log` (line 46)

  - Purpose: Get audit log entries with optional filtering (Constitution compliant)

  - Signature summary: positional=self, event_type, task_id

  - Async: False, Returns: List[Dict[str, Any]]

  - Cross-file communications: none

- Function `AuditManager.get_audit_stats` (line 78)

  - Purpose: Get audit logging statistics

  - Signature summary: positional=self

  - Async: False, Returns: Dict[str, Any]

  - Cross-file communications: none

- Function `AuditManager.get_recent_events` (line 127)

  - Purpose: Get recent audit events

  - Signature summary: positional=self, limit

  - Async: False, Returns: List[Dict[str, Any]]

  - Cross-file communications: none

- Function `AuditManager.log_event` (line 22)

  - Purpose: Add audit log entry (Constitution compliant security logging)

  - Signature summary: positional=self, event_type, task_id, details

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `time.time` at line 28 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

    - Calls `threading.get_ident` at line 31 (unresolved)

      - Purpose: No docstring provided

      - Expression: `threading.get_ident`

    - Calls `sys.stderr.write` at line 43 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.write`

    - Calls `sys.stderr.flush` at line 44 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.flush`

- Function `AuditManager.search_events` (line 132)

  - Purpose: Search audit events by criteria

  - Signature summary: positional=self; kwarg=criteria

  - Async: False, Returns: List[Dict[str, Any]]

  - Cross-file communications: none

- Function `AuditManager.set_enabled` (line 118)

  - Purpose: Enable or disable audit logging

  - Signature summary: positional=self, enabled

  - Async: False, Returns: None

  - Cross-file communications: none


## modules/permissions/cache.py

- Module: `modules.permissions.cache`

- Function `CacheManager.__init__` (line 17)

  - Purpose: No docstring provided

  - Signature summary: positional=self, enabled, ttl_seconds, max_entries

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `threading.Lock` at line 23 (unresolved)

      - Purpose: No docstring provided

      - Expression: `threading.Lock`

- Function `CacheManager._calculate_hit_ratio` (line 144)

  - Purpose: Calculate cache hit ratio (requires tracking hits/misses)

  - Signature summary: positional=self

  - Async: False, Returns: float

  - Cross-file communications: none

- Function `CacheManager._cleanup_expired` (line 86)

  - Purpose: Clean up expired cache entries

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `time.time` at line 88 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

- Function `CacheManager._evict_lru` (line 98)

  - Purpose: Evict least recently used entry

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `CacheManager.cache_response` (line 63)

  - Purpose: Cache permission response (Constitution compliant)

  - Signature summary: positional=self, cache_key, response

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `time.time` at line 68 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

- Function `CacheManager.clear_cache` (line 107)

  - Purpose: Clear all cached permission responses (Constitution compliant)

  - Signature summary: positional=self

  - Async: False, Returns: int

  - Cross-file communications: none

- Function `CacheManager.enabled` (line 170)

  - Purpose: Check if caching is enabled

  - Signature summary: positional=self

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `CacheManager.generate_cache_key` (line 25)

  - Purpose: Generate cache key for permission prompt (Constitution compliant)

  - Signature summary: positional=self, prompt_data

  - Async: False, Returns: str

  - Cross-file communications:

    - Calls `json.dumps` at line 36 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dumps`

    - Calls `hashlib.md5` at line 37 (unresolved)

      - Purpose: No docstring provided

      - Expression: `hashlib.md5`

- Function `CacheManager.get_cache_entry_info` (line 193)

  - Purpose: Get information about a specific cache entry

  - Signature summary: positional=self, cache_key

  - Async: False, Returns: Optional[Dict[str, Any]]

  - Cross-file communications:

    - Calls `time.time` at line 200 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

- Function `CacheManager.get_cache_keys` (line 180)

  - Purpose: Get all cache keys

  - Signature summary: positional=self

  - Async: False, Returns: list

  - Cross-file communications: none

- Function `CacheManager.get_cache_stats` (line 114)

  - Purpose: Get cache statistics (Constitution compliant)

  - Signature summary: positional=self

  - Async: False, Returns: Dict[str, Any]

  - Cross-file communications:

    - Calls `time.time` at line 116 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

- Function `CacheManager.get_cached_response` (line 39)

  - Purpose: Get cached response if still valid (Constitution compliant)

  - Signature summary: positional=self, cache_key

  - Async: False, Returns: Optional[Dict[str, Any]]

  - Cross-file communications:

    - Calls `time.time` at line 44 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

- Function `CacheManager.remove_by_key` (line 185)

  - Purpose: Remove specific cache entry by key

  - Signature summary: positional=self, cache_key

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `CacheManager.set_enabled` (line 150)

  - Purpose: Enable or disable caching

  - Signature summary: positional=self, enabled

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `CacheManager.set_max_entries` (line 160)

  - Purpose: Set maximum cache entries

  - Signature summary: positional=self, max_entries

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `CacheManager.set_ttl` (line 156)

  - Purpose: Set cache TTL in seconds

  - Signature summary: positional=self, ttl_seconds

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `CacheManager.size` (line 175)

  - Purpose: Get current cache size

  - Signature summary: positional=self

  - Async: False, Returns: int

  - Cross-file communications: none


## modules/permissions/enums.py

- Module: `modules.permissions.enums`

- Functions: none

## modules/permissions/i18n.py

- Module: `modules.permissions.i18n`

- Function `I18nManager.__init__` (line 13)

  - Purpose: No docstring provided

  - Signature summary: positional=self, enabled, default_locale

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `I18nManager._load_default_translations` (line 18)

  - Purpose: Load default translations (Constitution compliant - memory efficient)

  - Signature summary: positional=self

  - Async: False, Returns: Dict[str, Dict[str, str]]

  - Cross-file communications: none

- Function `I18nManager.add_custom_translation` (line 131)

  - Purpose: Add custom translation (Constitution compliant)

  - Signature summary: positional=self, locale, key, value

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `I18nManager.current_locale` (line 148)

  - Purpose: Get current locale

  - Signature summary: positional=self

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `I18nManager.enabled` (line 143)

  - Purpose: Check if i18n is enabled

  - Signature summary: positional=self

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `I18nManager.get_supported_locales` (line 138)

  - Purpose: Get list of supported locales (Constitution compliant)

  - Signature summary: positional=self

  - Async: False, Returns: List[str]

  - Cross-file communications: none

- Function `I18nManager.get_translation` (line 110)

  - Purpose: Get translated text for current locale (Constitution compliant)

  - Signature summary: positional=self, key, fallback

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `I18nManager.set_locale` (line 95)

  - Purpose: Set current locale for internationalization (Constitution compliant)

  - Signature summary: positional=self, locale

  - Async: False, Returns: bool

  - Cross-file communications:

    - Calls `sys.stderr.write` at line 106 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.write`

    - Calls `sys.stderr.flush` at line 107 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.flush`


## modules/permissions/integration.py

- Module: `modules.permissions.integration`

- Function `UnifiedPermissionManager.__init__` (line 20)

  - Purpose: No docstring provided

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `modules.permissions.manager.PermissionBufferManager` at line 21 (unresolved)

      - Purpose: No docstring provided

      - Expression: `PermissionBufferManager`

    - Calls `threading.Lock` at line 25 (unresolved)

      - Purpose: No docstring provided

      - Expression: `threading.Lock`

- Function `UnifiedPermissionManager._clear_current_prompt` (line 122)

  - Purpose: Internal method to clear current widget state

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `UnifiedPermissionManager._show_console_prompt` (line 129)

  - Purpose: Fallback console-based permission prompt

  - Signature summary: positional=self, prompt_data

  - Async: False, Returns: bool

  - Cross-file communications:

    - Calls `sys.stderr.write` at line 162 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.write`

    - Calls `sys.stderr.flush` at line 163 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.flush`

- Function `UnifiedPermissionManager.clear_permission_prompt` (line 110)

  - Purpose: Clear current permission prompt

  - Signature summary: positional=self

  - Async: False, Returns: bool

  - Cross-file communications:

    - Calls `sys.stderr.write` at line 118 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.write`

    - Calls `sys.stderr.flush` at line 119 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.flush`

- Function `UnifiedPermissionManager.get_buffer_manager` (line 166)

  - Purpose: Get the underlying buffer manager for advanced operations

  - Signature summary: positional=self

  - Async: False, Returns: PermissionBufferManager

  - Cross-file communications: none

- Function `UnifiedPermissionManager.get_current_widget` (line 170)

  - Purpose: Get current permission widget (for UI integration)

  - Signature summary: positional=self

  - Async: False, Returns: Optional[PermissionPrompt]

  - Cross-file communications: none

- Function `UnifiedPermissionManager.handle_permission_response` (line 75)

  - Purpose: Handle permission response from UI or other sources

  - Signature summary: positional=self, response, data

  - Async: False, Returns: bool

  - Cross-file communications:

    - Calls `sys.stderr.write` at line 106 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.write`

    - Calls `sys.stderr.flush` at line 107 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.flush`

- Function `UnifiedPermissionManager.register_response_handler` (line 32)

  - Purpose: Register a response handler for specific permission types

  - Signature summary: positional=self, handler_name, handler

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `UnifiedPermissionManager.set_ui_callback` (line 27)

  - Purpose: Set callback function for UI integration (e.g., TUI's _show_permission_prompt)

  - Signature summary: positional=self, callback

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `UnifiedPermissionManager.show_permission_prompt` (line 37)

  - Purpose: Show a permission prompt using the UI system

  - Signature summary: positional=self, prompt_data, handler_name

  - Async: False, Returns: bool

  - Cross-file communications:

    - Calls `sys.stderr.write` at line 71 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.write`

    - Calls `sys.stderr.flush` at line 72 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.flush`

    - Calls `modules.permissions.widget.PermissionPrompt` at line 51 (unresolved)

      - Purpose: No docstring provided

      - Expression: `PermissionPrompt`

- Function `UnifiedPermissionManager.shutdown` (line 174)

  - Purpose: Shutdown the unified permission manager

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `get_unified_permission_manager` (line 185)

  - Purpose: Get singleton unified permission manager instance

  - Signature summary: (no parameters)

  - Async: False, Returns: UnifiedPermissionManager

  - Cross-file communications: none

- Function `reset_unified_permission_manager` (line 195)

  - Purpose: Reset singleton (for testing)

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `show_api_permission_prompt` (line 223)

  - Purpose: Show API operation permission prompt

  - Signature summary: positional=api_name; kwarg=kwargs

  - Async: False, Returns: bool

  - Cross-file communications:

    - Calls `modules.permissions.templates.PermissionTemplates.create_api_permission_prompt` at line 226 (unresolved)

      - Purpose: No docstring provided

      - Expression: `PermissionTemplates.create_api_permission_prompt`

- Function `show_bash_permission_prompt` (line 214)

  - Purpose: Show bash command permission prompt

  - Signature summary: positional=command; kwarg=kwargs

  - Async: False, Returns: bool

  - Cross-file communications:

    - Calls `modules.permissions.templates.PermissionTemplates.create_bash_permission_prompt` at line 217 (unresolved)

      - Purpose: No docstring provided

      - Expression: `PermissionTemplates.create_bash_permission_prompt`

- Function `show_file_permission_prompt` (line 205)

  - Purpose: Show file operation permission prompt

  - Signature summary: positional=file_path, operation; kwarg=kwargs

  - Async: False, Returns: bool

  - Cross-file communications:

    - Calls `modules.permissions.templates.PermissionTemplates.create_file_permission_prompt` at line 208 (unresolved)

      - Purpose: No docstring provided

      - Expression: `PermissionTemplates.create_file_permission_prompt`

- Function `show_tool_permission_prompt` (line 232)

  - Purpose: Show tool execution permission prompt

  - Signature summary: positional=tool_name, tool_args; kwarg=kwargs

  - Async: False, Returns: bool

  - Cross-file communications:

    - Calls `modules.permissions.templates.PermissionTemplates.create_tool_permission_prompt` at line 235 (unresolved)

      - Purpose: No docstring provided

      - Expression: `PermissionTemplates.create_tool_permission_prompt`


## modules/permissions/manager.py

- Module: `modules.permissions.manager`

- Function `PermissionBufferManager.__init__` (line 24)

  - Purpose: No docstring provided

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `threading.Condition` at line 27 (unresolved)

      - Purpose: No docstring provided

      - Expression: `threading.Condition`

    - Calls `threading.Lock` at line 29 (unresolved)

      - Purpose: No docstring provided

      - Expression: `threading.Lock`

    - Calls `threading.Thread` at line 31 (unresolved)

      - Purpose: No docstring provided

      - Expression: `threading.Thread`

    - Calls `modules.permissions.i18n.I18nManager` at line 44 (unresolved)

      - Purpose: No docstring provided

      - Expression: `I18nManager`

    - Calls `modules.permissions.validation.ValidationManager` at line 45 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ValidationManager`

    - Calls `modules.permissions.analytics.AnalyticsManager` at line 46 (unresolved)

      - Purpose: No docstring provided

      - Expression: `AnalyticsManager`

    - Calls `modules.permissions.audit.AuditManager` at line 47 (unresolved)

      - Purpose: No docstring provided

      - Expression: `AuditManager`

    - Calls `modules.permissions.cache.CacheManager` at line 48 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CacheManager`

    - Calls `asyncio.get_event_loop` at line 53 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.get_event_loop`

    - Calls `asyncio.create_task` at line 55 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.create_task`

- Function `PermissionBufferManager._escalate_timeout` (line 140)

  - Purpose: Escalate timeout by increasing priority (Constitution compliant)

  - Signature summary: positional=self, task

  - Async: False, Returns: bool

  - Cross-file communications:

    - Calls `sys.stderr.write` at line 146 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.write`

    - Calls `sys.stderr.flush` at line 147 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.flush`

- Function `PermissionBufferManager._get_priority_task` (line 124)

  - Purpose: Get highest priority task from queue (Constitution compliant - blocking)

  - Signature summary: positional=self

  - Async: False, Returns: Optional[_PromptTask]

  - Cross-file communications:

    - Calls `heapq.heappop` at line 133 (unresolved)

      - Purpose: No docstring provided

      - Expression: `heapq.heappop`

- Function `PermissionBufferManager._get_queue_size` (line 135)

  - Purpose: Get current queue size (thread-safe)

  - Signature summary: positional=self

  - Async: False, Returns: int

  - Cross-file communications: none

- Function `PermissionBufferManager._periodic_cleanup` (line 163)

  - Purpose: Periodic cleanup of orphaned prompts (Constitution compliant)

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.sleep` at line 167 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

    - Calls `sys.stderr.write` at line 175 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.write`

    - Calls `sys.stderr.flush` at line 176 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.flush`

- Function `PermissionBufferManager._put_priority_task` (line 118)

  - Purpose: Add task to priority queue (Constitution compliant - thread-safe)

  - Signature summary: positional=self, task

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `heapq.heappush` at line 121 (unresolved)

      - Purpose: No docstring provided

      - Expression: `heapq.heappush`

- Function `PermissionBufferManager._resolve_current` (line 394)

  - Purpose: Resolve current prompt (internal method)

  - Signature summary: positional=self, selected_option, task

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `PermissionBufferManager._run` (line 369)

  - Purpose: Main worker thread loop (Constitution compliant)

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `sys.stderr.write` at line 391 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.write`

    - Calls `sys.stderr.flush` at line 392 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.flush`

- Function `PermissionBufferManager.add_custom_translation` (line 69)

  - Purpose: Add custom translation

  - Signature summary: positional=self, locale, key, value

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `PermissionBufferManager.cancel` (line 263)

  - Purpose: Cancel specific task by ID (Constitution compliant)

  - Signature summary: positional=self, task_id

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `PermissionBufferManager.cancel_all_active_tasks` (line 295)

  - Purpose: Cancel all active tasks (Constitution compliant)

  - Signature summary: positional=self

  - Async: False, Returns: int

  - Cross-file communications: none

- Function `PermissionBufferManager.cancel_batch_by_prefix` (line 310)

  - Purpose: Cancel all tasks whose IDs start with given prefix (Constitution compliant)

  - Signature summary: positional=self, task_id_prefix

  - Async: False, Returns: int

  - Cross-file communications: none

- Function `PermissionBufferManager.cleanup_orphaned_prompts` (line 344)

  - Purpose: Clean up orphaned prompts (Constitution compliant)

  - Signature summary: positional=self, max_age_seconds

  - Async: False, Returns: int

  - Cross-file communications:

    - Calls `time.time` at line 346 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

- Function `PermissionBufferManager.clear` (line 233)

  - Purpose: Clear prompt display (Constitution compliant)

  - Signature summary: positional=self, task

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `PermissionBufferManager.clear_prompt_cache` (line 109)

  - Purpose: Clear all cached permission responses

  - Signature summary: positional=self

  - Async: False, Returns: int

  - Cross-file communications: none

- Function `PermissionBufferManager.export_analytics` (line 91)

  - Purpose: Export analytics data in specified format

  - Signature summary: positional=self, format

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `PermissionBufferManager.export_audit_log` (line 104)

  - Purpose: Export audit log for security analysis

  - Signature summary: positional=self, format

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `PermissionBufferManager.get_active_task_count` (line 279)

  - Purpose: Get number of active tasks (Constitution compliant)

  - Signature summary: positional=self

  - Async: False, Returns: int

  - Cross-file communications: none

- Function `PermissionBufferManager.get_analytics_report` (line 87)

  - Purpose: Generate comprehensive analytics report

  - Signature summary: positional=self

  - Async: False, Returns: Dict[str, Any]

  - Cross-file communications: none

- Function `PermissionBufferManager.get_audit_log` (line 100)

  - Purpose: Get audit log entries with optional filtering

  - Signature summary: positional=self, event_type, task_id

  - Async: False, Returns: List[Dict[str, Any]]

  - Cross-file communications: none

- Function `PermissionBufferManager.get_cache_stats` (line 113)

  - Purpose: Get cache statistics

  - Signature summary: positional=self

  - Async: False, Returns: Dict[str, Any]

  - Cross-file communications: none

- Function `PermissionBufferManager.get_concurrent_prompt_status` (line 284)

  - Purpose: Get status of concurrent prompt handling (Constitution compliant)

  - Signature summary: positional=self

  - Async: False, Returns: Dict[str, Any]

  - Cross-file communications: none

- Function `PermissionBufferManager.get_supported_locales` (line 73)

  - Purpose: Get list of supported locales

  - Signature summary: positional=self

  - Async: False, Returns: List[str]

  - Cross-file communications: none

- Function `PermissionBufferManager.get_translation` (line 65)

  - Purpose: Get translated text for current locale

  - Signature summary: positional=self, key, fallback

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `PermissionBufferManager.reset_analytics` (line 95)

  - Purpose: Reset all analytics data

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `PermissionBufferManager.resolve` (line 195)

  - Purpose: Resolve current prompt with selected option (Constitution compliant)

  - Signature summary: positional=self, option

  - Async: False, Returns: bool

  - Cross-file communications:

    - Calls `time.time` at line 206 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

    - Calls `sys.stderr.write` at line 214 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.write`

    - Calls `sys.stderr.flush` at line 215 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.flush`

- Function `PermissionBufferManager.set_locale` (line 61)

  - Purpose: Set current locale for internationalization

  - Signature summary: positional=self, locale

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `PermissionBufferManager.shutdown` (line 329)

  - Purpose: Shutdown permission buffer manager (Constitution compliant)

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `PermissionBufferManager.update` (line 178)

  - Purpose: Update current prompt display (Constitution compliant)

  - Signature summary: positional=self, prompt_data

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `sys.stderr.write` at line 186 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.write`

    - Calls `sys.stderr.flush` at line 187 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.flush`

- Function `PermissionBufferManager.validate_prompt_data` (line 78)

  - Purpose: Validate permission prompt data

  - Signature summary: positional=self, prompt_data

  - Async: False, Returns: tuple[bool, Optional[str]]

  - Cross-file communications: none

- Function `PermissionBufferManager.validate_prompt_response` (line 82)

  - Purpose: Validate permission prompt response

  - Signature summary: positional=self, response, original_options

  - Async: False, Returns: tuple[bool, Optional[str]]

  - Cross-file communications: none

- Function `get_permission_buffer_manager` (line 400)

  - Purpose: Get singleton permission buffer manager instance

  - Signature summary: (no parameters)

  - Async: False, Returns: PermissionBufferManager

  - Cross-file communications: none


## modules/permissions/task.py

- Module: `modules.permissions.task`

- Function `TaskQueue.__init__` (line 222)

  - Purpose: No docstring provided

  - Signature summary: positional=self, max_size

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `threading.Lock` at line 225 (unresolved)

      - Purpose: No docstring provided

      - Expression: `threading.Lock`

- Function `TaskQueue.cleanup_expired` (line 282)

  - Purpose: Remove and return expired tasks

  - Signature summary: positional=self

  - Async: False, Returns: List[_PromptTask]

  - Cross-file communications: none

- Function `TaskQueue.clear` (line 260)

  - Purpose: Clear all tasks and return them

  - Signature summary: positional=self

  - Async: False, Returns: List[_PromptTask]

  - Cross-file communications: none

- Function `TaskQueue.get` (line 236)

  - Purpose: Get highest priority task

  - Signature summary: positional=self

  - Async: False, Returns: Optional[_PromptTask]

  - Cross-file communications: none

- Function `TaskQueue.get_all_tasks` (line 277)

  - Purpose: Get all tasks (for debugging/monitoring)

  - Signature summary: positional=self

  - Async: False, Returns: List[_PromptTask]

  - Cross-file communications: none

- Function `TaskQueue.is_empty` (line 272)

  - Purpose: Check if queue is empty

  - Signature summary: positional=self

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `TaskQueue.peek` (line 243)

  - Purpose: Peek at highest priority task without removing

  - Signature summary: positional=self

  - Async: False, Returns: Optional[_PromptTask]

  - Cross-file communications: none

- Function `TaskQueue.put` (line 227)

  - Purpose: Add task to queue

  - Signature summary: positional=self, task

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `TaskQueue.remove` (line 250)

  - Purpose: Remove specific task by ID

  - Signature summary: positional=self, task_id

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `TaskQueue.size` (line 267)

  - Purpose: Get queue size

  - Signature summary: positional=self

  - Async: False, Returns: int

  - Cross-file communications: none

- Function `_PromptTask.__lt__` (line 67)

  - Purpose: Comparison for priority queue (lower priority value = higher priority)

  - Signature summary: positional=self, other

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `_PromptTask.__post_init__` (line 59)

  - Purpose: Post-initialization setup

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `weakref.ref` at line 65 (unresolved)

      - Purpose: No docstring provided

      - Expression: `weakref.ref`

- Function `_PromptTask.__repr__` (line 211)

  - Purpose: String representation for debugging

  - Signature summary: positional=self

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `_PromptTask.auto_dismiss` (line 163)

  - Purpose: Auto-dismiss the task (timeout)

  - Signature summary: positional=self

  - Async: False, Returns: bool

  - Cross-file communications:

    - Calls `time.time` at line 169 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

    - Calls `asyncio.TimeoutError` at line 174 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.TimeoutError`

- Function `_PromptTask.cancel` (line 120)

  - Purpose: Cancel the task (Constitution compliant <100ms)

  - Signature summary: positional=self

  - Async: False, Returns: bool

  - Cross-file communications:

    - Calls `time.time` at line 126 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

- Function `_PromptTask.escalate_priority` (line 103)

  - Purpose: Escalate task priority (Constitution compliant)

  - Signature summary: positional=self

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `_PromptTask.get_age_seconds` (line 79)

  - Purpose: Get task age in seconds

  - Signature summary: positional=self

  - Async: False, Returns: float

  - Cross-file communications:

    - Calls `time.time` at line 81 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

- Function `_PromptTask.get_duration_seconds` (line 83)

  - Purpose: Get task duration if completed

  - Signature summary: positional=self

  - Async: False, Returns: Optional[float]

  - Cross-file communications: none

- Function `_PromptTask.is_expired` (line 89)

  - Purpose: Check if task has expired

  - Signature summary: positional=self

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `_PromptTask.is_orphaned` (line 95)

  - Purpose: Check if task is orphaned (references are dead)

  - Signature summary: positional=self

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `_PromptTask.resolve` (line 143)

  - Purpose: Resolve the task with response data

  - Signature summary: positional=self, response_data

  - Async: False, Returns: bool

  - Cross-file communications:

    - Calls `time.time` at line 149 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

- Function `_PromptTask.set_error` (line 178)

  - Purpose: Set error information for the task

  - Signature summary: positional=self, error_message

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `_PromptTask.start_auto_dismiss_timer` (line 184)

  - Purpose: Start auto-dismiss timer

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `threading.Timer` at line 189 (unresolved)

      - Purpose: No docstring provided

      - Expression: `threading.Timer`

- Function `_PromptTask.to_dict` (line 192)

  - Purpose: Convert task to dictionary for serialization

  - Signature summary: positional=self

  - Async: False, Returns: Dict[str, Any]

  - Cross-file communications: none


## modules/permissions/templates.py

- Module: `modules.permissions.templates`

- Function `PermissionTemplates.create_api_permission_prompt` (line 106)

  - Purpose: Create an API operation permission prompt

  - Signature summary: positional=api_name, endpoint, estimated_cost, data_details

  - Async: False, Returns: Dict[str, Any]

  - Cross-file communications: none

- Function `PermissionTemplates.create_bash_permission_prompt` (line 59)

  - Purpose: Create a bash command permission prompt

  - Signature summary: positional=command, risk_level, estimated_duration, working_directory

  - Async: False, Returns: Dict[str, Any]

  - Cross-file communications: none

- Function `PermissionTemplates.create_file_permission_prompt` (line 12)

  - Purpose: Create a file operation permission prompt

  - Signature summary: positional=file_path, operation, risk_level, details

  - Async: False, Returns: Dict[str, Any]

  - Cross-file communications:

    - Calls `pathlib.Path` at line 47 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

- Function `PermissionTemplates.create_generic_permission_prompt` (line 201)

  - Purpose: Create a generic permission prompt

  - Signature summary: positional=title, message, details, options

  - Async: False, Returns: Dict[str, Any]

  - Cross-file communications: none

- Function `PermissionTemplates.create_tool_permission_prompt` (line 155)

  - Purpose: Create a tool execution permission prompt

  - Signature summary: positional=tool_name, tool_args, risk_level, description

  - Async: False, Returns: Dict[str, Any]

  - Cross-file communications: none


## modules/permissions/validation.py

- Module: `modules.permissions.validation`

- Function `ValidationManager.__init__` (line 13)

  - Purpose: No docstring provided

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `re.compile` at line 16 (unresolved)

      - Purpose: No docstring provided

      - Expression: `re.compile`

- Function `ValidationManager._validate_color_format` (line 95)

  - Purpose: Validate color format (Constitution compliant)

  - Signature summary: positional=self, color

  - Async: False, Returns: Tuple[bool, Optional[str]]

  - Cross-file communications: none

- Function `ValidationManager.sanitize_string` (line 216)

  - Purpose: Sanitize string input for security

  - Signature summary: positional=self, text, max_length

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `ValidationManager.validate_priority_value` (line 201)

  - Purpose: Validate priority enum value

  - Signature summary: positional=self, priority

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `ValidationManager.validate_prompt_data` (line 18)

  - Purpose: Validate permission prompt data (Constitution compliant security)

  - Signature summary: positional=self, prompt_data

  - Async: False, Returns: Tuple[bool, Optional[str]]

  - Cross-file communications: none

- Function `ValidationManager.validate_prompt_response` (line 142)

  - Purpose: Validate permission prompt response (Constitution compliant security)

  - Signature summary: positional=self, response, original_options

  - Async: False, Returns: Tuple[bool, Optional[str]]

  - Cross-file communications:

    - Calls `json.dumps` at line 177 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dumps`

- Function `ValidationManager.validate_task_id` (line 185)

  - Purpose: Validate task ID format

  - Signature summary: positional=self, task_id

  - Async: False, Returns: bool

  - Cross-file communications: none


## modules/permissions/widget.py

- Module: `modules.permissions.widget`

- Function `PermissionPrompt.Responded.__init__` (line 31)

  - Purpose: No docstring provided

  - Signature summary: positional=self, response, data

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `PermissionPrompt.__init__` (line 36)

  - Purpose: Args:

  - Signature summary: positional=self, title, message, options, details; kwarg=kwargs

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `PermissionPrompt.action_cancel` (line 224)

  - Purpose: Cancel the prompt

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `PermissionPrompt.action_confirm` (line 214)

  - Purpose: Confirm the selected option

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `PermissionPrompt.hide` (line 238)

  - Purpose: Deactivate the prompt

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `PermissionPrompt.on_key` (line 172)

  - Purpose: Handle key presses for option selection

  - Signature summary: positional=self, event

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `PermissionPrompt.render` (line 56)

  - Purpose: Render the permission prompt as a formatted box with Frontier colors

  - Signature summary: positional=self

  - Async: False, Returns: Text

  - Cross-file communications:

    - Calls `rich.text.Text` at line 62 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

    - Calls `rich.style.Style` at line 168 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Style`

    - Calls `frontier_colors.FRONTIER_COLORS.get` at line 168 (unresolved)

      - Purpose: No docstring provided

      - Expression: `FRONTIER_COLORS.get`

- Function `PermissionPrompt.show` (line 232)

  - Purpose: Activate the prompt

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `PermissionPrompt.watch_is_active` (line 248)

  - Purpose: React to active state changes

  - Signature summary: positional=self, old_value, new_value

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `PermissionPrompt.watch_selected_option` (line 243)

  - Purpose: React to selection changes

  - Signature summary: positional=self, old_value, new_value

  - Async: False, Returns: None

  - Cross-file communications: none


## modules/profiler.py

- Module: `modules.profiler`

- Function `RuntimeProfiler.__init__` (line 40)

  - Purpose: No docstring provided

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `RuntimeProfiler.analyze_threads` (line 95)

  - Purpose: Analyze all running threads and detect potential issues

  - Signature summary: positional=self

  - Async: False, Returns: List[ThreadInfo]

  - Cross-file communications:

    - Calls `threading.enumerate` at line 99 (unresolved)

      - Purpose: No docstring provided

      - Expression: `threading.enumerate`

    - Calls `threading._active.get` at line 103 (unresolved)

      - Purpose: No docstring provided

      - Expression: `threading._active.get`

    - Calls `traceback.format_stack` at line 105 (unresolved)

      - Purpose: No docstring provided

      - Expression: `traceback.format_stack`

- Function `RuntimeProfiler.detect_blocking_threads` (line 122)

  - Purpose: Detect threads that appear to be blocked or deadlocked

  - Signature summary: positional=self, snapshot_interval

  - Async: False, Returns: List[ThreadInfo]

  - Cross-file communications:

    - Calls `time.sleep` at line 126 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.sleep`

- Function `RuntimeProfiler.format_profile_report` (line 170)

  - Purpose: Format profile statistics into readable report

  - Signature summary: positional=self, stats

  - Async: False, Returns: str

  - Cross-file communications:

    - Calls `datetime.datetime.now` at line 174 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

- Function `RuntimeProfiler.format_thread_report` (line 148)

  - Purpose: Format thread analysis into readable report

  - Signature summary: positional=self, threads

  - Async: False, Returns: str

  - Cross-file communications:

    - Calls `datetime.datetime.now` at line 152 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

- Function `RuntimeProfiler.set_performance_budget` (line 144)

  - Purpose: Set performance budget for a function

  - Signature summary: positional=self, function_name, max_time_ms

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `RuntimeProfiler.start_profiling` (line 46)

  - Purpose: Start performance profiling

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `cProfile.Profile` at line 51 (unresolved)

      - Purpose: No docstring provided

      - Expression: `cProfile.Profile`

- Function `RuntimeProfiler.stop_profiling` (line 55)

  - Purpose: Stop profiling and return statistics

  - Signature summary: positional=self

  - Async: False, Returns: ProfileStats

  - Cross-file communications:

    - Calls `io.StringIO` at line 64 (unresolved)

      - Purpose: No docstring provided

      - Expression: `io.StringIO`

    - Calls `pstats.Stats` at line 65 (unresolved)

      - Purpose: No docstring provided

      - Expression: `pstats.Stats`

- Function `get_profiler` (line 199)

  - Purpose: Get the global profiler instance

  - Signature summary: (no parameters)

  - Async: False, Returns: RuntimeProfiler

  - Cross-file communications: none


## modules/prompt_processor.py

- Module: `modules.prompt_processor`

- Function `PromptProcessor.__init__` (line 11)

  - Purpose: No docstring provided

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `re.compile` at line 32 (unresolved)

      - Purpose: No docstring provided

      - Expression: `re.compile`

- Function `PromptProcessor._get_next_placeholder_id` (line 189)

  - Purpose: Get next placeholder ID

  - Signature summary: positional=self

  - Async: False, Returns: int

  - Cross-file communications: none

- Function `PromptProcessor._is_likely_file_path` (line 266)

  - Purpose: Check if text looks like a file path

  - Signature summary: positional=self, text

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `PromptProcessor._is_valid_image_path` (line 181)

  - Purpose: Check if path has a valid image extension

  - Signature summary: positional=self, path

  - Async: False, Returns: bool

  - Cross-file communications:

    - Calls `pathlib.Path` at line 184 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

- Function `PromptProcessor._process_media_paths` (line 70)

  - Purpose: Detect and replace image/video file paths with placeholders

  - Signature summary: positional=self, text

  - Async: False, Returns: Tuple[str, list, list]

  - Cross-file communications:

    - Calls `pathlib.Path` at line 110 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

- Function `PromptProcessor._process_pasted_text` (line 139)

  - Purpose: Detect and collapse large pasted text blocks

  - Signature summary: positional=self, text

  - Async: False, Returns: Tuple[str, list]

  - Cross-file communications: none

- Function `PromptProcessor.create_message_with_images` (line 306)

  - Purpose: Create a message dict with text and image paths for API

  - Signature summary: positional=self, text, metadata

  - Async: False, Returns: dict

  - Cross-file communications: none

- Function `PromptProcessor.extract_images_from_metadata` (line 298)

  - Purpose: Extract list of image paths from metadata

  - Signature summary: positional=self, metadata

  - Async: False, Returns: list

  - Cross-file communications: none

- Function `PromptProcessor.format_display` (line 212)

  - Purpose: Format text for display with metadata annotations

  - Signature summary: positional=self, text, metadata

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `PromptProcessor.get_original_text` (line 194)

  - Purpose: Reconstruct original text from processed text and metadata

  - Signature summary: positional=self, processed_text, metadata

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `PromptProcessor.is_likely_command` (line 246)

  - Purpose: Check if text is likely a command (not a file path or paste)

  - Signature summary: positional=self, text

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `PromptProcessor.process_input` (line 43)

  - Purpose: Process input text, replacing images/videos and long pastes with placeholders

  - Signature summary: positional=self, text

  - Async: False, Returns: Tuple[str, dict]

  - Cross-file communications: none

- Function `PromptProcessor.should_process_as_paste` (line 238)

  - Purpose: Quick check if text should be treated as a paste

  - Signature summary: positional=self, text

  - Async: False, Returns: bool

  - Cross-file communications: none


## modules/provider_settings.py

- Module: `modules.provider_settings`

- Function `ensure_provider_defaults` (line 84)

  - Purpose: Merge persisted provider metadata with current defaults.

  - Signature summary: positional=existing

  - Async: False, Returns: Dict[str, Dict[str, Any]]

  - Cross-file communications:

    - Calls `copy.deepcopy` at line 104 (unresolved)

      - Purpose: No docstring provided

      - Expression: `deepcopy`

- Function `get_provider_defaults` (line 109)

  - Purpose: Return a deep copy of the default settings for the provider.

  - Signature summary: positional=provider_id

  - Async: False, Returns: Dict[str, Any]

  - Cross-file communications:

    - Calls `copy.deepcopy` at line 112 (unresolved)

      - Purpose: No docstring provided

      - Expression: `deepcopy`


## modules/refactor_executor.py

- Module: `modules.refactor_executor`

- Function `RefactoringExecutor.__init__` (line 120)

  - Purpose: No docstring provided

  - Signature summary: positional=self, repo_path

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path` at line 121 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

- Function `RefactoringExecutor._generate_diff` (line 306)

  - Purpose: Generate diff of changes

  - Signature summary: positional=self, worktree_path, changes

  - Async: False, Returns: str

  - Cross-file communications:

    - Calls `subprocess.run` at line 309 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `RefactoringExecutor._perform_extraction` (line 188)

  - Purpose: Perform the actual code extraction using rope library

  - Signature summary: positional=self, worktree_path, plan

  - Async: False, Returns: List[str]

  - Cross-file communications:

    - Calls `rope.base.project.Project` at line 198 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Project`

    - Calls `pathlib.Path` at line 265 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

    - Calls `rope.base.libutils.path_to_resource` at line 208 (unresolved)

      - Purpose: No docstring provided

      - Expression: `libutils.path_to_resource`

    - Calls `ast.parse` at line 231 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ast.parse`

    - Calls `ast.walk` at line 235 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ast.walk`

    - Calls `traceback.print_exc` at line 303 (unresolved)

      - Purpose: No docstring provided

      - Expression: `traceback.print_exc`

- Function `RefactoringExecutor._run_tests` (line 320)

  - Purpose: Run test suite in worktree

  - Signature summary: positional=self, worktree_path

  - Async: False, Returns: str

  - Cross-file communications:

    - Calls `subprocess.run` at line 324 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `RefactoringExecutor.apply_refactoring` (line 341)

  - Purpose: Apply approved refactoring to main branch

  - Signature summary: positional=self, result

  - Async: False, Returns: bool

  - Cross-file communications:

    - Calls `os.path.exists` at line 347 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.path.exists`

    - Calls `pathlib.Path` at line 353 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

    - Calls `shutil.copy2` at line 358 (unresolved)

      - Purpose: No docstring provided

      - Expression: `shutil.copy2`

- Function `RefactoringExecutor.cleanup` (line 378)

  - Purpose: Clean up all active worktrees

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `RefactoringExecutor.execute_extraction` (line 124)

  - Purpose: Execute a function extraction refactoring

  - Signature summary: positional=self, plan

  - Async: False, Returns: RefactoringResult

  - Cross-file communications: none

- Function `RefactoringExecutor.reject_refactoring` (line 369)

  - Purpose: Reject refactoring and clean up worktree

  - Signature summary: positional=self, result

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `WorktreeManager.__init__` (line 45)

  - Purpose: No docstring provided

  - Signature summary: positional=self, repo_path

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path` at line 46 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

- Function `WorktreeManager.cleanup_all` (line 111)

  - Purpose: Clean up all active worktrees

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `WorktreeManager.create_worktree` (line 49)

  - Purpose: Create a new git worktree for refactoring

  - Signature summary: positional=self, branch_name

  - Async: False, Returns: Optional[str]

  - Cross-file communications:

    - Calls `tempfile.mkdtemp` at line 53 (unresolved)

      - Purpose: No docstring provided

      - Expression: `tempfile.mkdtemp`

    - Calls `subprocess.run` at line 56 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `WorktreeManager.remove_worktree` (line 71)

  - Purpose: Remove a git worktree

  - Signature summary: positional=self, worktree_path

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `subprocess.run` at line 93 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

    - Calls `os.path.exists` at line 105 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.path.exists`

    - Calls `shutil.rmtree` at line 106 (unresolved)

      - Purpose: No docstring provided

      - Expression: `shutil.rmtree`


## modules/refactor_orchestrator.py

- Module: `modules.refactor_orchestrator`

- Function `RefactoringOrchestrator.__init__` (line 60)

  - Purpose: No docstring provided

  - Signature summary: positional=self, repo_path, permission_handler

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path` at line 61 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

    - Calls `modules.architecture_validator.ArchitectureValidator` at line 65 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ArchitectureValidator`

    - Calls `modules.refactor_executor.RefactoringExecutor` at line 66 (unresolved)

      - Purpose: No docstring provided

      - Expression: `RefactoringExecutor`

    - Calls `modules.profiler.RuntimeProfiler` at line 67 (unresolved)

      - Purpose: No docstring provided

      - Expression: `RuntimeProfiler`

    - Calls `modules.auto_refactor.AutoRefactorManager` at line 68 (unresolved)

      - Purpose: No docstring provided

      - Expression: `AutoRefactorManager`

- Function `RefactoringOrchestrator._calculate_priority` (line 255)

  - Purpose: Calculate refactoring priority (1-10)

  - Signature summary: positional=self, violations, concurrency_issues, improvements

  - Async: False, Returns: int

  - Cross-file communications: none

- Function `RefactoringOrchestrator._detect_degradation` (line 143)

  - Purpose: Detect functions that have degraded in performance

  - Signature summary: positional=self, stats

  - Async: False, Returns: List[Tuple[str, float, float]]

  - Cross-file communications: none

- Function `RefactoringOrchestrator._propose_performance_fix` (line 164)

  - Purpose: Propose a fix for degraded performance

  - Signature summary: positional=self, func_name, current_ms, baseline_ms

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `RefactoringOrchestrator._self_healing_loop` (line 118)

  - Purpose: Background loop that monitors and fixes degraded performance

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `time.sleep` at line 123 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.sleep`

- Function `RefactoringOrchestrator.analyze_file` (line 175)

  - Purpose: Comprehensive analysis of a file

  - Signature summary: positional=self, file_path

  - Async: False, Returns: RefactoringProposal

  - Cross-file communications:

    - Calls `pathlib.Path` at line 181 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

    - Calls `modules.concurrency_analyzer.ConcurrencyAnalyzer` at line 191 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ConcurrencyAnalyzer`

    - Calls `modules.code_analyzer.CodeAnalyzer` at line 195 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CodeAnalyzer`

    - Calls `modules.refactor_executor.RefactoringPlan` at line 208 (unresolved)

      - Purpose: No docstring provided

      - Expression: `RefactoringPlan`

- Function `RefactoringOrchestrator.apply_session` (line 348)

  - Purpose: Apply approved refactoring

  - Signature summary: positional=self, session

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `RefactoringOrchestrator.cleanup` (line 371)

  - Purpose: Cleanup resources

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `RefactoringOrchestrator.execute_proposal` (line 275)

  - Purpose: Execute a refactoring proposal in sandbox

  - Signature summary: positional=self, proposal

  - Async: True, Returns: RefactoringSession

  - Cross-file communications:

    - Calls `time.strftime` at line 284 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.strftime`

- Function `RefactoringOrchestrator.get_status` (line 360)

  - Purpose: Get current orchestrator status

  - Signature summary: positional=self

  - Async: False, Returns: Dict

  - Cross-file communications: none

- Function `RefactoringOrchestrator.reject_session` (line 355)

  - Purpose: Reject and cleanup session

  - Signature summary: positional=self, session

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `RefactoringOrchestrator.request_approval` (line 301)

  - Purpose: Request user approval for refactoring

  - Signature summary: positional=self, session

  - Async: True, Returns: Tuple[bool, str]

  - Cross-file communications: none

- Function `RefactoringOrchestrator.start_monitoring` (line 82)

  - Purpose: Start continuous monitoring and self-healing

  - Signature summary: positional=self, config

  - Async: False, Returns: Dict

  - Cross-file communications:

    - Calls `threading.Thread` at line 99 (unresolved)

      - Purpose: No docstring provided

      - Expression: `threading.Thread`

- Function `RefactoringOrchestrator.stop_monitoring` (line 108)

  - Purpose: Stop monitoring

  - Signature summary: positional=self

  - Async: False, Returns: Dict

  - Cross-file communications: none

- Function `get_orchestrator` (line 382)

  - Purpose: Get or create global orchestrator instance

  - Signature summary: positional=permission_handler

  - Async: False, Returns: RefactoringOrchestrator

  - Cross-file communications: none


## modules/registry.py

- Module: `modules.registry`

- Function `_register_commands` (line 118)

  - Purpose: Register ALL commands - ASYNC

  - Signature summary: positional=executor

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `_register_tools` (line 753)

  - Purpose: Register ALL tools - ASYNC

  - Signature summary: positional=executor

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `_safe_register` (line 52)

  - Purpose: SDK-enforced registration with LIVE buffer update

  - Signature summary: positional=executor, exec_type, name, handler, category, risk_level, requires_approval, description; kwarg=kwargs

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.sdk.enforcement.enforce_handler` at line 73 (ok)

      - Purpose: Enforce SDK compliance on handler

      - Expression: `enforce_handler`

    - Calls `sdk.get_enforcement` at line 97 (unresolved)

      - Purpose: No docstring provided

      - Expression: `get_enforcement`

- Function `register_all` (line 27)

  - Purpose: ONE registration function for EVERYTHING

  - Signature summary: positional=executor

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.sdk.validation.validate_full_coverage` at line 49 (ok)

      - Purpose: Validate that every expected command/tool has an SDK registration.

      - Expression: `validate_full_coverage`


## modules/rollback_manager.py

- Module: `modules.rollback_manager`

- Function `RollbackManager.__init__` (line 13)

  - Purpose: No docstring provided

  - Signature summary: positional=self, config_dir

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path.home` at line 15 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.home`

- Function `RollbackManager._get_dir_size` (line 71)

  - Purpose: Get human-readable directory size

  - Signature summary: positional=self, path

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `RollbackManager._verify_restoration` (line 290)

  - Purpose: Verify restored installation basic structure

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `RollbackManager.cleanup_old_backups` (line 313)

  - Purpose: Remove old backups, keeping only the most recent

  - Signature summary: positional=self, keep_latest

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `shutil.rmtree` at line 329 (unresolved)

      - Purpose: No docstring provided

      - Expression: `shutil.rmtree`

- Function `RollbackManager.create_safety_backup` (line 155)

  - Purpose: Create backup of current (potentially broken) state

  - Signature summary: positional=self, suffix

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `datetime.datetime.now` at line 157 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

    - Calls `pathlib.Path.home` at line 158 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.home`

    - Calls `shutil.copytree` at line 162 (unresolved)

      - Purpose: No docstring provided

      - Expression: `shutil.copytree`

- Function `RollbackManager.get_current_version` (line 89)

  - Purpose: Get currently installed version

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.load` at line 97 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

- Function `RollbackManager.list_backups` (line 17)

  - Purpose: List all available backups with metadata

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path.home` at line 20 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.home`

    - Calls `datetime.datetime.strptime` at line 32 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.strptime`

    - Calls `json.load` at line 42 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

    - Calls `datetime.datetime.now` at line 50 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

- Function `RollbackManager.perform_rollback` (line 178)

  - Purpose: Perform rollback to specified backup

  - Signature summary: positional=self, backup_path, create_safety

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `datetime.datetime.now` at line 279 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

    - Calls `json.load` at line 222 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

    - Calls `shutil.rmtree` at line 233 (unresolved)

      - Purpose: No docstring provided

      - Expression: `shutil.rmtree`

    - Calls `shutil.copytree` at line 253 (unresolved)

      - Purpose: No docstring provided

      - Expression: `shutil.copytree`

- Function `RollbackManager.verify_backup` (line 102)

  - Purpose: Verify backup is valid and complete

  - Signature summary: positional=self, backup_path

  - Async: False, Returns: None

  - Cross-file communications: none


## modules/sdk/__init__.py

- Module: `modules.sdk`

- Functions: none

## modules/sdk/enforcement.py

- Module: `modules.sdk.enforcement`

- Function `SDKEnforcement.__init__` (line 55)

  - Purpose: No docstring provided

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `SDKEnforcement._attempt_conversion` (line 154)

  - Purpose: Attempt to convert handler to be compliant

  - Signature summary: positional=self, handler, validation

  - Async: False, Returns: Optional[Callable]

  - Cross-file communications: none

- Function `SDKEnforcement._wrap_add_context` (line 182)

  - Purpose: Wrap handler to add **context parameter

  - Signature summary: positional=self, handler

  - Async: False, Returns: Callable

  - Cross-file communications: none

- Function `SDKEnforcement._wrap_add_context.wrapped_handler` (line 195)

  - Purpose: SDK compliance wrapper - adds **context support

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `inspect.signature` at line 199 (unresolved)

      - Purpose: No docstring provided

      - Expression: `inspect.signature`

    - Calls `traceback.print_exc` at line 234 (unresolved)

      - Purpose: No docstring provided

      - Expression: `traceback.print_exc`

- Function `SDKEnforcement.enforce` (line 62)

  - Purpose: Enforce SDK compliance on handler

  - Signature summary: positional=self, name, handler, category, auto_convert

  - Async: False, Returns: EnforcementResult

  - Cross-file communications:

    - Calls `modules.sdk.handler_interface.validate_handler` at line 82 (ok)

      - Purpose: Validate handler against SDK interface

      - Expression: `validate_handler`

- Function `SDKEnforcement.get_rejected` (line 287)

  - Purpose: Get list of rejected handlers

  - Signature summary: positional=self

  - Async: False, Returns: List[EnforcementResult]

  - Cross-file communications: none

- Function `SDKEnforcement.get_summary` (line 246)

  - Purpose: Get enforcement summary for display

  - Signature summary: positional=self

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `SDKEnforcement.has_violations` (line 291)

  - Purpose: Check if any handlers were rejected

  - Signature summary: positional=self

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `enforce_handler` (line 308)

  - Purpose: Enforce SDK compliance on handler

  - Signature summary: positional=name, handler, category, auto_convert

  - Async: False, Returns: EnforcementResult

  - Cross-file communications: none

- Function `get_enforcement` (line 300)

  - Purpose: Get or create global enforcement instance

  - Signature summary: (no parameters)

  - Async: False, Returns: SDKEnforcement

  - Cross-file communications: none


## modules/sdk/executor.py

- Module: `modules.sdk.executor`

- Function `ExecutionStep.__post_init__` (line 56)

  - Purpose: No docstring provided

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ExecutionSystem.__init__` (line 75)

  - Purpose: No docstring provided

  - Signature summary: positional=self, app, session

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `modules.sdk.registry.ExecutionRegistry` at line 80 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ExecutionRegistry`

    - Calls `modules.sdk.permission_manager.PermissionManager` at line 81 (unresolved)

      - Purpose: No docstring provided

      - Expression: `PermissionManager`

    - Calls `modules.sdk.async_runner.AsyncExecutionRunner` at line 82 (unresolved)

      - Purpose: No docstring provided

      - Expression: `AsyncExecutionRunner`

    - Calls `modules.sdk.circuit_breaker.CircuitBreaker` at line 83 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CircuitBreaker`

    - Calls `modules.sdk.retry_manager.RetryManager` at line 84 (unresolved)

      - Purpose: No docstring provided

      - Expression: `RetryManager`

- Function `ExecutionSystem._clear_statusline` (line 434)

  - Purpose: Clear statusline indicator

  - Signature summary: positional=self, label

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ExecutionSystem._execute_single` (line 366)

  - Purpose: Execute single function (tool or simple command)

  - Signature summary: positional=self, registration, context

  - Async: True, Returns: Any

  - Cross-file communications:

    - Calls `asyncio.iscoroutinefunction` at line 392 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.iscoroutinefunction`

    - Calls `asyncio.sleep` at line 417 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

- Function `ExecutionSystem._execute_workflow` (line 191)

  - Purpose: Execute multi-step workflow with live progress IN PERMISSION BUFFER

  - Signature summary: positional=self, registration, steps, context

  - Async: True, Returns: List[Any]

  - Cross-file communications:

    - Calls `asyncio.iscoroutinefunction` at line 272 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.iscoroutinefunction`

    - Calls `asyncio.sleep` at line 313 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

- Function `ExecutionSystem._update_statusline` (line 425)

  - Purpose: Update statusline indicator

  - Signature summary: positional=self, label, icon, color

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ExecutionSystem._wait_for_step_permission` (line 323)

  - Purpose: Show permission prompt for individual step

  - Signature summary: positional=self, step, workflow_status, prompt_input

  - Async: True, Returns: bool

  - Cross-file communications:

    - Calls `asyncio.sleep` at line 356 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

- Function `ExecutionSystem.execute` (line 93)

  - Purpose: Execute command/tool/API with unified flow

  - Signature summary: positional=self, type, name, steps; kwarg=context

  - Async: True, Returns: Any

  - Cross-file communications: none

- Function `ExecutionSystem.execute_api` (line 464)

  - Purpose: Execute API call by name

  - Signature summary: positional=self, name; kwarg=context

  - Async: True, Returns: Any

  - Cross-file communications: none

- Function `ExecutionSystem.execute_command` (line 447)

  - Purpose: Execute command by name

  - Signature summary: positional=self, name, steps; kwarg=context

  - Async: True, Returns: Any

  - Cross-file communications: none

- Function `ExecutionSystem.execute_tool` (line 456)

  - Purpose: Execute tool by name

  - Signature summary: positional=self, name; kwarg=context

  - Async: True, Returns: Any

  - Cross-file communications: none

- Function `get_executor` (line 477)

  - Purpose: Get or create global execution system

  - Signature summary: positional=app, session

  - Async: False, Returns: ExecutionSystem

  - Cross-file communications: none


## modules/sdk/handler_interface.py

- Module: `modules.sdk.handler_interface`

- Function `HandlerRegistration.is_compliant` (line 79)

  - Purpose: Check if handler is SDK compliant

  - Signature summary: positional=self

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `SDKCompliantHandler.__call__` (line 39)

  - Purpose: MANDATORY signature

  - Signature summary: positional=self, app, session; kwarg=context

  - Async: True, Returns: Any

  - Cross-file communications: none

- Function `validate_handler` (line 84)

  - Purpose: Validate handler against SDK interface

  - Signature summary: positional=handler, name

  - Async: False, Returns: HandlerRegistration

  - Cross-file communications:

    - Calls `asyncio.iscoroutinefunction` at line 96 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.iscoroutinefunction`

    - Calls `inspect.signature` at line 106 (unresolved)

      - Purpose: No docstring provided

      - Expression: `inspect.signature`


## modules/sdk/startup_buffer.py

- Module: `modules.sdk.startup_buffer`

- Function `StartupBuffer.__init__` (line 29)

  - Purpose: No docstring provided

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `modules.sdk.enforcement.get_enforcement` at line 30 (ok)

      - Purpose: Get or create global enforcement instance

      - Expression: `get_enforcement`

- Function `StartupBuffer._build_content` (line 80)

  - Purpose: Build display content

  - Signature summary: positional=self, executor

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `StartupBuffer.show` (line 32)

  - Purpose: Show startup buffer with module load status in SDK dropdown widget

  - Signature summary: positional=self, app, executor, duration_ms, auto_dismiss

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.sleep` at line 74 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

- Function `StartupBuffer.show_blocking` (line 149)

  - Purpose: Show startup buffer and wait for user to dismiss using SDK dropdown

  - Signature summary: positional=self, app, executor

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.sleep` at line 174 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

- Function `show_startup_status` (line 180)

  - Purpose: Show startup status in SDK dropdown (non-blocking)

  - Signature summary: positional=app, executor, block_on_violations, duration_ms

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.sdk.enforcement.get_enforcement` at line 196 (ok)

      - Purpose: Get or create global enforcement instance

      - Expression: `get_enforcement`


## modules/sdk/startup_diagnostics.py

- Module: `modules.sdk.startup_diagnostics`

- Function `StartupDiagnostics.__init__` (line 16)

  - Purpose: No docstring provided

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StartupDiagnostics.get_summary` (line 51)

  - Purpose: Get summary text for display

  - Signature summary: positional=self

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `StartupDiagnostics.show_in_buffer` (line 77)

  - Purpose: Show diagnostics in permission buffer (non-blocking)

  - Signature summary: positional=self, app, duration_ms

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `asyncio.create_task` at line 112 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.create_task`

- Function `StartupDiagnostics.show_in_buffer.auto_clear` (line 106)

  - Purpose: No docstring provided

  - Signature summary: (no parameters)

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.sleep` at line 107 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

- Function `StartupDiagnostics.validate_registry` (line 23)

  - Purpose: Validate all registered handlers

  - Signature summary: positional=self, executor

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `modules.sdk.handler_interface.validate_handler` at line 41 (ok)

      - Purpose: Validate handler against SDK interface

      - Expression: `validate_handler`

- Function `run_startup_diagnostics` (line 115)

  - Purpose: Run diagnostics and optionally show in buffer

  - Signature summary: positional=app, executor, show_buffer

  - Async: False, Returns: StartupDiagnostics

  - Cross-file communications: none


## modules/sdk/validation.py

- Module: `modules.sdk.validation`

- Function `_normalize_subcommand` (line 17)

  - Purpose: Build a fully-qualified command name while skipping dynamic placeholders.

  - Signature summary: positional=parent, subcommand

  - Async: False, Returns: str | None

  - Cross-file communications: none

- Function `collect_expected_commands` (line 33)

  - Purpose: Return the canonical set of command identifiers from CommandRegistry.

  - Signature summary: positional=executor

  - Async: False, Returns: Set[str]

  - Cross-file communications:

    - Calls `modules.command_registry.CommandRegistry` at line 42 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandRegistry`

- Function `collect_expected_tools` (line 60)

  - Purpose: Return the canonical set of tool identifiers from ToolPermissionManager.

  - Signature summary: (no parameters)

  - Async: False, Returns: Set[str]

  - Cross-file communications:

    - Calls `modules.tool_permissions.ToolPermissionManager` at line 64 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ToolPermissionManager`

- Function `validate_full_coverage` (line 68)

  - Purpose: Validate that every expected command/tool has an SDK registration.

  - Signature summary: positional=executor

  - Async: False, Returns: Dict[str, List[str]]

  - Cross-file communications: none


## modules/sdk_loading_buffer.py

- Module: `modules.sdk_loading_buffer`

- Function `SDKLoadingBuffer.__init__` (line 37)

  - Purpose: Initialize SDK loading buffer.

  - Signature summary: positional=self; kwarg=kwargs

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `SDKLoadingBuffer._spin` (line 135)

  - Purpose: Async task that updates the spinner frame.

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.sleep` at line 141 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

- Function `SDKLoadingBuffer.clear_data` (line 145)

  - Purpose: Clear all data.

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `SDKLoadingBuffer.render` (line 50)

  - Purpose: Render the loading buffer with Frontier colors.

  - Signature summary: positional=self

  - Async: False, Returns: RenderableType

  - Cross-file communications:

    - Calls `rich.text.Text` at line 52 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

- Function `SDKLoadingBuffer.start_loading` (line 116)

  - Purpose: Mark as loading and start spinner animation.

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `asyncio.create_task` at line 120 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.create_task`

- Function `SDKLoadingBuffer.stop_loading` (line 123)

  - Purpose: Mark as complete and stop spinner animation.

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `SDKLoadingBuffer.update_progress` (line 89)

  - Purpose: Update registration progress.

  - Signature summary: positional=self, command_count, tool_count, accepted_count, converted_count, rejected_count, latest_module

  - Async: False, Returns: None

  - Cross-file communications: none


## modules/selectable_richlog.py

- Module: `modules.selectable_richlog`

- Function `SelectableRichLog.__init__` (line 22)

  - Purpose: No docstring provided

  - Signature summary: positional=self; vararg=args; kwarg=kwargs

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `SelectableRichLog.can_focus` (line 30)

  - Purpose: No docstring provided

  - Signature summary: positional=self

  - Async: False, Returns: bool

  - Cross-file communications: none


## modules/shell_injector.py

- Module: `modules.shell_injector`

- Function `CommunicationLog.__init__` (line 61)

  - Purpose: No docstring provided

  - Signature summary: positional=self, log_dir

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path` at line 62 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

    - Calls `pathlib.Path.home` at line 62 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.home`

    - Calls `datetime.datetime.now` at line 69 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

- Function `CommunicationLog.export_session_log` (line 118)

  - Purpose: Export session log to JSON file

  - Signature summary: positional=self, output_file

  - Async: False, Returns: str

  - Cross-file communications:

    - Calls `datetime.datetime.now` at line 124 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

    - Calls `json.dump` at line 130 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dump`

- Function `CommunicationLog.get_goal_progress` (line 110)

  - Purpose: Get goal progress updates for an agent

  - Signature summary: positional=self, agent_id

  - Async: False, Returns: List[InjectionMessage]

  - Cross-file communications: none

- Function `CommunicationLog.get_injections_by_agent` (line 88)

  - Purpose: Get all injections involving a specific agent

  - Signature summary: positional=self, agent_id

  - Async: False, Returns: List[InjectionMessage]

  - Cross-file communications: none

- Function `CommunicationLog.get_injections_by_type` (line 95)

  - Purpose: Get all injections of a specific type

  - Signature summary: positional=self, injection_type

  - Async: False, Returns: List[InjectionMessage]

  - Cross-file communications: none

- Function `CommunicationLog.get_navigation_history` (line 102)

  - Purpose: Get navigation history for an agent

  - Signature summary: positional=self, agent_id

  - Async: False, Returns: List[InjectionMessage]

  - Cross-file communications: none

- Function `CommunicationLog.get_recent_injections` (line 84)

  - Purpose: Get recent injections

  - Signature summary: positional=self, limit

  - Async: False, Returns: List[InjectionMessage]

  - Cross-file communications: none

- Function `CommunicationLog.log_injection` (line 72)

  - Purpose: Log an injection message

  - Signature summary: positional=self, message

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `InjectionMessage.from_dict` (line 45)

  - Purpose: Create from dictionary

  - Signature summary: positional=data

  - Async: False, Returns: 'InjectionMessage'

  - Cross-file communications: none

- Function `InjectionMessage.from_json` (line 50)

  - Purpose: Create from JSON

  - Signature summary: positional=data

  - Async: False, Returns: 'InjectionMessage'

  - Cross-file communications:

    - Calls `json.loads` at line 52 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.loads`

- Function `InjectionMessage.to_dict` (line 36)

  - Purpose: Convert to dictionary

  - Signature summary: positional=self

  - Async: False, Returns: Dict

  - Cross-file communications:

    - Calls `dataclasses.asdict` at line 38 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asdict`

- Function `InjectionMessage.to_json` (line 40)

  - Purpose: Convert to JSON

  - Signature summary: positional=self

  - Async: False, Returns: str

  - Cross-file communications:

    - Calls `json.dumps` at line 42 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dumps`

- Function `ShellInjector.__init__` (line 141)

  - Purpose: No docstring provided

  - Signature summary: positional=self, ipc_server

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `asyncio.Queue` at line 144 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.Queue`

- Function `ShellInjector._process_injections` (line 240)

  - Purpose: Process injection queue

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `ShellInjector.get_communication_log` (line 271)

  - Purpose: Get the communication log

  - Signature summary: positional=self

  - Async: False, Returns: CommunicationLog

  - Cross-file communications: none

- Function `ShellInjector.get_log_summary` (line 275)

  - Purpose: Get summary of communication log

  - Signature summary: positional=self

  - Async: False, Returns: Dict[str, Any]

  - Cross-file communications: none

- Function `ShellInjector.inject_to_agent` (line 194)

  - Purpose: Inject message into subagent shell

  - Signature summary: positional=self, agent_id, injection_type, content, metadata

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `datetime.datetime.now` at line 218 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

    - Calls `uuid.uuid4` at line 219 (unresolved)

      - Purpose: No docstring provided

      - Expression: `uuid.uuid4`

- Function `ShellInjector.inject_to_opencli` (line 160)

  - Purpose: Inject message into OpenCLI prompt area

  - Signature summary: positional=self, injection_type, source_agent, content, metadata

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `datetime.datetime.now` at line 184 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

    - Calls `uuid.uuid4` at line 185 (unresolved)

      - Purpose: No docstring provided

      - Expression: `uuid.uuid4`

- Function `ShellInjector.start` (line 147)

  - Purpose: Start the injection processor

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.create_task` at line 149 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.create_task`

- Function `ShellInjector.stop` (line 151)

  - Purpose: Stop the injection processor

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `get_shell_injector` (line 298)

  - Purpose: Get singleton shell injector instance

  - Signature summary: positional=ipc_server

  - Async: False, Returns: ShellInjector

  - Cross-file communications: none


## modules/simple_tui.py

- Module: `modules.simple_tui`

- Functions: none

## modules/spec-kit/src/specify_cli/__init__.py

- Module: `modules.spec-kit.src.specify_cli`

- Function `BannerGroup.format_help` (line 303)

  - Purpose: No docstring provided

  - Signature summary: positional=self, ctx, formatter

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StepTracker.__init__` (line 103)

  - Purpose: No docstring provided

  - Signature summary: positional=self, title

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StepTracker._maybe_refresh` (line 141)

  - Purpose: No docstring provided

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StepTracker._update` (line 129)

  - Purpose: No docstring provided

  - Signature summary: positional=self, key, status, detail

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StepTracker.add` (line 112)

  - Purpose: No docstring provided

  - Signature summary: positional=self, key, label

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StepTracker.attach_refresh` (line 109)

  - Purpose: No docstring provided

  - Signature summary: positional=self, cb

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StepTracker.complete` (line 120)

  - Purpose: No docstring provided

  - Signature summary: positional=self, key, detail

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StepTracker.error` (line 123)

  - Purpose: No docstring provided

  - Signature summary: positional=self, key, detail

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StepTracker.render` (line 148)

  - Purpose: No docstring provided

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `rich.tree.Tree` at line 149 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Tree`

- Function `StepTracker.skip` (line 126)

  - Purpose: No docstring provided

  - Signature summary: positional=self, key, detail

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StepTracker.start` (line 117)

  - Purpose: No docstring provided

  - Signature summary: positional=self, key, detail

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `_github_auth_headers` (line 62)

  - Purpose: Return Authorization header dict only when a non-empty token exists.

  - Signature summary: positional=cli_token

  - Async: False, Returns: dict

  - Cross-file communications: none

- Function `_github_token` (line 58)

  - Purpose: Return sanitized GitHub token (cli arg takes precedence) or None.

  - Signature summary: positional=cli_token

  - Async: False, Returns: str | None

  - Cross-file communications:

    - Calls `os.getenv` at line 60 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.getenv`

- Function `callback` (line 335)

  - Purpose: Show banner when no subcommand is provided.

  - Signature summary: positional=ctx

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `rich.align.Align.center` at line 341 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Align.center`

- Function `check` (line 1110)

  - Purpose: Check that all required tools are installed.

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `check_tool` (line 374)

  - Purpose: Check if a tool is installed.

  - Signature summary: positional=tool, install_hint

  - Async: False, Returns: bool

  - Cross-file communications:

    - Calls `shutil.which` at line 386 (unresolved)

      - Purpose: No docstring provided

      - Expression: `shutil.which`

- Function `check_tool_for_tracker` (line 364)

  - Purpose: Check if a tool is installed and update tracker.

  - Signature summary: positional=tool, tracker

  - Async: False, Returns: bool

  - Cross-file communications:

    - Calls `shutil.which` at line 366 (unresolved)

      - Purpose: No docstring provided

      - Expression: `shutil.which`

- Function `download_and_extract_template` (line 549)

  - Purpose: Download the latest release and extract it to create a new project.

  - Signature summary: positional=project_path, ai_assistant, script_type, is_current_dir; kwonly=verbose, tracker, client, debug, github_token

  - Async: False, Returns: Path

  - Cross-file communications:

    - Calls `pathlib.Path.cwd` at line 553 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.cwd`

    - Calls `zipfile.ZipFile` at line 592 (unresolved)

      - Purpose: No docstring provided

      - Expression: `zipfile.ZipFile`

    - Calls `tempfile.TemporaryDirectory` at line 603 (unresolved)

      - Purpose: No docstring provided

      - Expression: `tempfile.TemporaryDirectory`

    - Calls `pathlib.Path` at line 604 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

    - Calls `shutil.copy2` at line 644 (unresolved)

      - Purpose: No docstring provided

      - Expression: `shutil.copy2`

    - Calls `shutil.copytree` at line 640 (unresolved)

      - Purpose: No docstring provided

      - Expression: `shutil.copytree`

    - Calls `shutil.move` at line 671 (unresolved)

      - Purpose: No docstring provided

      - Expression: `shutil.move`

    - Calls `rich.panel.Panel` at line 685 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Panel`

    - Calls `shutil.rmtree` at line 688 (unresolved)

      - Purpose: No docstring provided

      - Expression: `shutil.rmtree`

    - Calls `typer.Exit` at line 689 (unresolved)

      - Purpose: No docstring provided

      - Expression: `typer.Exit`

- Function `download_template_from_github` (line 437)

  - Purpose: No docstring provided

  - Signature summary: positional=ai_assistant, download_dir; kwonly=script_type, verbose, show_progress, client, debug, github_token

  - Async: False, Returns: Tuple[Path, dict]

  - Cross-file communications:

    - Calls `httpx.Client` at line 441 (unresolved)

      - Purpose: No docstring provided

      - Expression: `httpx.Client`

    - Calls `rich.panel.Panel` at line 536 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Panel`

    - Calls `typer.Exit` at line 537 (unresolved)

      - Purpose: No docstring provided

      - Expression: `typer.Exit`

    - Calls `rich.progress.Progress` at line 516 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Progress`

    - Calls `rich.progress.SpinnerColumn` at line 517 (unresolved)

      - Purpose: No docstring provided

      - Expression: `SpinnerColumn`

    - Calls `rich.progress.TextColumn` at line 519 (unresolved)

      - Purpose: No docstring provided

      - Expression: `TextColumn`

- Function `ensure_executable_scripts` (line 707)

  - Purpose: Ensure POSIX .sh scripts under .specify/scripts (recursively) have execute bits (no-op on Windows).

  - Signature summary: positional=project_path, tracker

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `os.chmod` at line 735 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.chmod`

- Function `get_key` (line 193)

  - Purpose: Get a single keypress in a cross-platform way using readchar.

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `readchar.readkey` at line 195 (unresolved)

      - Purpose: No docstring provided

      - Expression: `readchar.readkey`

- Function `init` (line 752)

  - Purpose: Initialize a new Specify project from the latest template.

  - Signature summary: positional=project_name, ai_assistant, script_type, ignore_agent_tools, no_git, here, force, skip_tls, debug, github_token

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `typer.Argument` at line 753 (unresolved)

      - Purpose: No docstring provided

      - Expression: `typer.Argument`

    - Calls `typer.Option` at line 762 (unresolved)

      - Purpose: No docstring provided

      - Expression: `typer.Option`

    - Calls `typer.Exit` at line 1018 (unresolved)

      - Purpose: No docstring provided

      - Expression: `typer.Exit`

    - Calls `pathlib.Path.cwd` at line 1011 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.cwd`

    - Calls `typer.confirm` at line 826 (unresolved)

      - Purpose: No docstring provided

      - Expression: `typer.confirm`

    - Calls `pathlib.Path` at line 831 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

    - Calls `rich.panel.Panel` at line 1105 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Panel`

    - Calls `sys.stdin.isatty` at line 941 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stdin.isatty`

    - Calls `rich.live.Live` at line 975 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Live`

    - Calls `httpx.Client` at line 981 (unresolved)

      - Purpose: No docstring provided

      - Expression: `httpx.Client`

    - Calls `sys.version.split` at line 1009 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.version.split`

    - Calls `shutil.rmtree` at line 1017 (unresolved)

      - Purpose: No docstring provided

      - Expression: `shutil.rmtree`

    - Calls `shlex.quote` at line 1067 (unresolved)

      - Purpose: No docstring provided

      - Expression: `shlex.quote`

- Function `init_git_repo` (line 413)

  - Purpose: Initialize a git repository in the specified path.

  - Signature summary: positional=project_path, quiet

  - Async: False, Returns: bool

  - Cross-file communications:

    - Calls `pathlib.Path.cwd` at line 418 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.cwd`

    - Calls `os.chdir` at line 434 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.chdir`

    - Calls `subprocess.run` at line 424 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `is_git_repo` (line 392)

  - Purpose: Check if the specified path is inside a git repository.

  - Signature summary: positional=path

  - Async: False, Returns: bool

  - Cross-file communications:

    - Calls `pathlib.Path.cwd` at line 395 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.cwd`

    - Calls `subprocess.run` at line 402 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `main` (line 1155)

  - Purpose: No docstring provided

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `run_command` (line 345)

  - Purpose: Run a shell command and optionally capture output.

  - Signature summary: positional=cmd, check_return, capture, shell

  - Async: False, Returns: Optional[str]

  - Cross-file communications:

    - Calls `subprocess.run` at line 352 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `select_with_arrows` (line 219)

  - Purpose: Interactive selection using arrow keys with Rich Live display.

  - Signature summary: positional=options, prompt_text, default_key

  - Async: False, Returns: str

  - Cross-file communications:

    - Calls `typer.Exit` at line 290 (unresolved)

      - Purpose: No docstring provided

      - Expression: `typer.Exit`

- Function `select_with_arrows.create_selection_panel` (line 239)

  - Purpose: Create the selection panel with current selection highlighted.

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `rich.table.Table.grid` at line 241 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Table.grid`

    - Calls `rich.panel.Panel` at line 254 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Panel`

- Function `select_with_arrows.run_selection_loop` (line 263)

  - Purpose: No docstring provided

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `rich.live.Live` at line 265 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Live`

    - Calls `typer.Exit` at line 284 (unresolved)

      - Purpose: No docstring provided

      - Expression: `typer.Exit`

- Function `show_banner` (line 318)

  - Purpose: Display the ASCII art banner.

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `rich.text.Text` at line 330 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

    - Calls `rich.align.Align.center` at line 330 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Align.center`


## modules/spec_memory.py

- Module: `modules.spec_memory`

- Function `SpecMemory.__init__` (line 15)

  - Purpose: Initialize spec memory for a project

  - Signature summary: positional=self, project_root

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path.cwd` at line 22 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.cwd`

- Function `SpecMemory._update_metadata` (line 194)

  - Purpose: Update metadata index

  - Signature summary: positional=self, category, data

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.load` at line 200 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

    - Calls `datetime.datetime.now` at line 212 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

    - Calls `json.dump` at line 215 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dump`

- Function `SpecMemory.clear_completed_goals` (line 226)

  - Purpose: Archive completed goals

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.load` at line 233 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

- Function `SpecMemory.format_context_for_system_message` (line 240)

  - Purpose: Format active context for system message

  - Signature summary: positional=self

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `SpecMemory.get_active_context` (line 161)

  - Purpose: Load all active specifications into context

  - Signature summary: positional=self

  - Async: False, Returns: Dict

  - Cross-file communications:

    - Calls `json.load` at line 185 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

- Function `SpecMemory.get_active_goals` (line 149)

  - Purpose: Get all active goals

  - Signature summary: positional=self

  - Async: False, Returns: List[Dict]

  - Cross-file communications:

    - Calls `json.load` at line 155 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

- Function `SpecMemory.get_metadata` (line 217)

  - Purpose: Get all metadata

  - Signature summary: positional=self

  - Async: False, Returns: Dict

  - Cross-file communications:

    - Calls `json.load` at line 223 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

- Function `SpecMemory.load_constitution` (line 53)

  - Purpose: Load project constitution if it exists

  - Signature summary: positional=self

  - Async: False, Returns: Optional[str]

  - Cross-file communications: none

- Function `SpecMemory.load_goal` (line 140)

  - Purpose: Load goal state

  - Signature summary: positional=self, goal_id

  - Async: False, Returns: Optional[Dict]

  - Cross-file communications:

    - Calls `json.load` at line 146 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

- Function `SpecMemory.load_plan` (line 110)

  - Purpose: Load implementation plan

  - Signature summary: positional=self, plan_name

  - Async: False, Returns: Optional[Dict]

  - Cross-file communications:

    - Calls `json.load` at line 117 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

- Function `SpecMemory.save_constitution` (line 32)

  - Purpose: Save project constitution (principles and governance)

  - Signature summary: positional=self, content

  - Async: False, Returns: Path

  - Cross-file communications:

    - Calls `datetime.datetime.now` at line 47 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

- Function `SpecMemory.save_feature_spec` (line 60)

  - Purpose: Save feature specification

  - Signature summary: positional=self, feature_name, spec

  - Async: False, Returns: Path

  - Cross-file communications:

    - Calls `datetime.datetime.now` at line 78 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

- Function `SpecMemory.save_goal` (line 120)

  - Purpose: Save current goal state

  - Signature summary: positional=self, goal_id, goal_data

  - Async: False, Returns: Path

  - Cross-file communications:

    - Calls `datetime.datetime.now` at line 133 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

    - Calls `json.dump` at line 136 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dump`

- Function `SpecMemory.save_plan` (line 85)

  - Purpose: Save implementation plan

  - Signature summary: positional=self, plan_name, plan

  - Async: False, Returns: Path

  - Cross-file communications:

    - Calls `json.dump` at line 100 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dump`

    - Calls `datetime.datetime.now` at line 102 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`


## modules/specify_wrapper.py

- Module: `modules.specify_wrapper`

- Function `SpecifyWrapper.__init__` (line 16)

  - Purpose: No docstring provided

  - Signature summary: positional=self, project_dir

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path.cwd` at line 17 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.cwd`

    - Calls `pathlib.Path` at line 18 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

    - Calls `sys.path.insert` at line 22 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.path.insert`

- Function `SpecifyWrapper.check_spec` (line 88)

  - Purpose: Run specify check command

  - Signature summary: positional=self

  - Async: False, Returns: Dict

  - Cross-file communications: none

- Function `SpecifyWrapper.format_spec_for_ai` (line 162)

  - Purpose: Format a spec command into instructions for the AI

  - Signature summary: positional=self, command, content

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `SpecifyWrapper.get_spec_commands` (line 92)

  - Purpose: Get list of available Specify slash commands

  - Signature summary: positional=self

  - Async: False, Returns: list

  - Cross-file communications: none

- Function `SpecifyWrapper.init_project` (line 73)

  - Purpose: Initialize a new Specify project

  - Signature summary: positional=self, project_name

  - Async: False, Returns: Dict

  - Cross-file communications: none

- Function `SpecifyWrapper.is_specify_project` (line 24)

  - Purpose: Check if current directory is a Specify project

  - Signature summary: positional=self

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `SpecifyWrapper.parse_slash_command` (line 139)

  - Purpose: Parse a slash command and extract command + content

  - Signature summary: positional=self, user_input

  - Async: False, Returns: Optional[Dict]

  - Cross-file communications: none

- Function `SpecifyWrapper.run_specify_command` (line 29)

  - Purpose: Run a specify command

  - Signature summary: positional=self, command, args

  - Async: False, Returns: Dict

  - Cross-file communications: none

- Function `get_specify_wrapper` (line 274)

  - Purpose: Get the global Specify wrapper instance

  - Signature summary: (no parameters)

  - Async: False, Returns: SpecifyWrapper

  - Cross-file communications: none


## modules/startup_buffer.py

- Module: `modules.startup_buffer`

- Function `StartupBuffer.__init__` (line 23)

  - Purpose: No docstring provided

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `modules.enforcement.get_enforcement` at line 24 (unresolved)

      - Purpose: No docstring provided

      - Expression: `get_enforcement`

- Function `StartupBuffer._build_content` (line 74)

  - Purpose: Build display content

  - Signature summary: positional=self, executor

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `StartupBuffer.show` (line 26)

  - Purpose: Show startup buffer with module load status in SDK dropdown widget

  - Signature summary: positional=self, app, executor, duration_ms, auto_dismiss

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.sleep` at line 68 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

- Function `StartupBuffer.show_blocking` (line 143)

  - Purpose: Show startup buffer and wait for user to dismiss using SDK dropdown

  - Signature summary: positional=self, app, executor

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.sleep` at line 168 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

- Function `show_startup_status` (line 174)

  - Purpose: Show startup status in SDK dropdown (non-blocking)

  - Signature summary: positional=app, executor, block_on_violations, duration_ms

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.enforcement.get_enforcement` at line 190 (unresolved)

      - Purpose: No docstring provided

      - Expression: `get_enforcement`


## modules/stream_buffer.py

- Module: `modules.stream_buffer`

- Function `BufferStatusDisplay.__init__` (line 126)

  - Purpose: Args:

  - Signature summary: positional=self, app, buffer

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `BufferStatusDisplay._update_loop` (line 166)

  - Purpose: Background task to update buffer status inline

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.sleep` at line 185 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

- Function `BufferStatusDisplay.start` (line 138)

  - Purpose: Start animated status display in chat

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.create_task` at line 151 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.create_task`

- Function `BufferStatusDisplay.stop` (line 153)

  - Purpose: Stop status updates and remove from chat

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `BufferStatusDisplay.write_final_status` (line 190)

  - Purpose: Write final status message (optional - widget removal handles display)

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamBuffer.__init__` (line 14)

  - Purpose: Args:

  - Signature summary: positional=self, chars_per_batch, batch_delay_ms

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `asyncio.Queue` at line 20 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.Queue`

- Function `StreamBuffer.add_chunk` (line 43)

  - Purpose: Add text chunk to buffer (called from streaming loop)

  - Signature summary: positional=self, text

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `StreamBuffer.drain_smooth` (line 83)

  - Purpose: Drain buffer with smooth pacing

  - Signature summary: positional=self, write_callback

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.wait_for` at line 98 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.wait_for`

    - Calls `asyncio.sleep` at line 107 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

- Function `StreamBuffer.finish_receiving` (line 51)

  - Purpose: Mark reception complete

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamBuffer.get_elapsed` (line 77)

  - Purpose: Get elapsed time in seconds

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `time.time` at line 81 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

- Function `StreamBuffer.get_status_message` (line 60)

  - Purpose: Get current spinner status message

  - Signature summary: positional=self, spinner_char

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `time.time` at line 65 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

- Function `StreamBuffer.interrupt` (line 55)

  - Purpose: User interrupted with ESC

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamBuffer.start` (line 34)

  - Purpose: Start buffer reception

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `time.time` at line 36 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`


## modules/stream_manager.py

- Module: `modules.stream_manager`

- Function `APIRetryManager.call_with_retry` (line 161)

  - Purpose: Retry API calls with exponential backoff

  - Signature summary: positional=client, max_retries, base_delay; kwarg=kwargs

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.sleep` at line 186 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

- Function `AsyncToolExecutor.execute_bash_async` (line 95)

  - Purpose: Non-blocking bash execution with timeout

  - Signature summary: positional=command, description, timeout

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.create_subprocess_shell` at line 108 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.create_subprocess_shell`

    - Calls `asyncio.wait_for` at line 114 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.wait_for`

- Function `AsyncToolExecutor.execute_read_async` (line 131)

  - Purpose: Async file read

  - Signature summary: positional=file_path

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.get_event_loop` at line 135 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.get_event_loop`

- Function `AsyncToolExecutor.execute_write_async` (line 144)

  - Purpose: Async file write

  - Signature summary: positional=file_path, content

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.get_event_loop` at line 147 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.get_event_loop`

- Function `StreamManager.__init__` (line 20)

  - Purpose: Args:

  - Signature summary: positional=self, timeout, heartbeat_interval

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `asyncio.Event` at line 28 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.Event`

    - Calls `time.time` at line 29 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

- Function `StreamManager._heartbeat_monitor` (line 67)

  - Purpose: Monitor for frozen streams and alert via callback

  - Signature summary: positional=self, callback

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.sleep` at line 72 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

    - Calls `time.time` at line 74 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

- Function `StreamManager.cancel` (line 82)

  - Purpose: Cancel the stream

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamManager.is_cancelled` (line 86)

  - Purpose: Check if stream was cancelled

  - Signature summary: positional=self

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `StreamManager.stream_with_timeout` (line 32)

  - Purpose: Execute coroutine with timeout protection

  - Signature summary: positional=self, coro, on_heartbeat

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.create_task` at line 48 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.create_task`

    - Calls `asyncio.wait_for` at line 53 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.wait_for`

- Function `StreamManager.update_activity` (line 78)

  - Purpose: Update last activity timestamp (call on stream progress)

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `time.time` at line 80 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

- Function `ToolCircuitBreaker.__init__` (line 192)

  - Purpose: Args:

  - Signature summary: positional=self, failure_threshold, timeout

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ToolCircuitBreaker.execute` (line 204)

  - Purpose: Execute tool with circuit breaker protection

  - Signature summary: positional=self, tool_func; vararg=args; kwarg=kwargs

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `time.time` at line 229 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`


## modules/streaming_display.py

- Module: `modules.streaming_display`

- Function `StreamingDisplay.__init__` (line 55)

  - Purpose: No docstring provided

  - Signature summary: positional=self; vararg=args; kwarg=kwargs

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `markdown_renderer.get_markdown_renderer` at line 62 (unresolved)

      - Purpose: No docstring provided

      - Expression: `get_markdown_renderer`

- Function `StreamingDisplay._apply_selection_highlight` (line 325)

  - Purpose: Apply visual highlight to selected text in a line

  - Signature summary: positional=self, content, line_number

  - Async: False, Returns: Text

  - Cross-file communications:

    - Calls `rich.text.Text` at line 343 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

    - Calls `rich.style.Style` at line 368 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Style`

- Function `StreamingDisplay._copy_selection` (line 486)

  - Purpose: Copy selected text to clipboard

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `platform.system` at line 508 (unresolved)

      - Purpose: No docstring provided

      - Expression: `platform.system`

    - Calls `subprocess.Popen` at line 522 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.Popen`

- Function `StreamingDisplay._get_scroll_offset` (line 227)

  - Purpose: Get the scroll offset from parent VerticalScroll container

  - Signature summary: positional=self

  - Async: False, Returns: int

  - Cross-file communications: none

- Function `StreamingDisplay._get_selected_text` (line 372)

  - Purpose: Get the currently selected text

  - Signature summary: positional=self

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `StreamingDisplay._get_total_lines` (line 240)

  - Purpose: Get total number of content lines

  - Signature summary: positional=self

  - Async: False, Returns: int

  - Cross-file communications: none

- Function `StreamingDisplay._handle_mouse_down` (line 254)

  - Purpose: Handle mouse down with widget-relative coordinates

  - Signature summary: positional=self, widget_x, widget_y

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamingDisplay._handle_mouse_move` (line 280)

  - Purpose: Handle mouse move with widget-relative coordinates

  - Signature summary: positional=self, widget_x, widget_y

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamingDisplay._handle_mouse_up` (line 299)

  - Purpose: Handle mouse up with widget-relative coordinates

  - Signature summary: positional=self, widget_x, widget_y

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamingDisplay._rebuild_display` (line 660)

  - Purpose: Rebuild the complete display from _lines with selection highlighting

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `rich.text.Text` at line 730 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

- Function `StreamingDisplay._scroll_to_bottom` (line 201)

  - Purpose: Scroll the parent container to bottom - NON-BLOCKING async version

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamingDisplay._scroll_to_bottom.do_scroll` (line 207)

  - Purpose: No docstring provided

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamingDisplay.action_copy_all` (line 534)

  - Purpose: Copy all text to clipboard (Cmd+C / Ctrl+C)

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `platform.system` at line 552 (unresolved)

      - Purpose: No docstring provided

      - Expression: `platform.system`

    - Calls `subprocess.Popen` at line 565 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.Popen`

- Function `StreamingDisplay.action_select_all` (line 528)

  - Purpose: Select all text (Ctrl+A)

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamingDisplay.add_buffer_status` (line 572)

  - Purpose: Add inline buffer status display showing streaming progress

  - Signature summary: positional=self, tokens, elapsed

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `rich.text.Text` at line 580 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

    - Calls `rich.style.Style` at line 584 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Style`

- Function `StreamingDisplay.add_permission_prompt` (line 616)

  - Purpose: Add a permission prompt to the display

  - Signature summary: positional=self, prompt_data

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamingDisplay.clear` (line 165)

  - Purpose: Clear all content

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamingDisplay.finish_stream` (line 75)

  - Purpose: Finish streaming and render markdown - REPLACES streamed content

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `rich.text.Text` at line 96 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

    - Calls `rich.style.Style` at line 89 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Style`

- Function `StreamingDisplay.remove_buffer_status` (line 610)

  - Purpose: Remove the buffer status line

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamingDisplay.remove_permission_prompt` (line 641)

  - Purpose: Remove the permission prompt from display

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamingDisplay.set_laser_colors` (line 172)

  - Purpose: Set laser color gradient

  - Signature summary: positional=self, colors

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamingDisplay.set_laser_enabled` (line 176)

  - Purpose: Enable/disable laser effect

  - Signature summary: positional=self, enabled

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamingDisplay.update_buffer_status` (line 592)

  - Purpose: Update the buffer status with new progress

  - Signature summary: positional=self, tokens, elapsed, spinner_frame

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `rich.text.Text` at line 600 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

    - Calls `rich.style.Style` at line 604 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Style`

- Function `StreamingDisplay.watch_selection_end` (line 319)

  - Purpose: Reactive watcher - disabled to preserve markdown formatting

  - Signature summary: positional=self, old_value, new_value

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamingDisplay.watch_selection_start` (line 314)

  - Purpose: Reactive watcher - disabled to preserve markdown formatting

  - Signature summary: positional=self, old_value, new_value

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamingDisplay.write` (line 113)

  - Purpose: Write text (compatibility with RichLog interface)

  - Signature summary: positional=self, text, style

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `rich.text.Text` at line 149 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

    - Calls `rich.text.Text.from_markup` at line 134 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text.from_markup`

- Function `StreamingDisplay.write_line` (line 161)

  - Purpose: Write a complete line (no laser effect) - alias for write()

  - Signature summary: positional=self, text, style

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamingDisplay.write_markdown` (line 180)

  - Purpose: Write markdown-formatted text with proper rendering

  - Signature summary: positional=self, text

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `rich.text.Text` at line 186 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

- Function `StreamingDisplay.write_stream` (line 67)

  - Purpose: Accumulate streaming text silently - display handled by buffer status

  - Signature summary: positional=self, text

  - Async: False, Returns: None

  - Cross-file communications: none


## modules/streaming_display/__init__.py

- Module: `modules.streaming_display`

- Functions: none

## modules/streaming_display/buffers.py

- Module: `modules.streaming_display.buffers`

- Function `BufferManager.__init__` (line 24)

  - Purpose: No docstring provided

  - Signature summary: positional=self, parent_widget

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `BufferManager._create_progress_bar` (line 203)

  - Purpose: Create a simple text progress bar

  - Signature summary: positional=self, progress, width

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `BufferManager.add_buffer_status` (line 43)

  - Purpose: Add buffer status overlay

  - Signature summary: positional=self, status_data

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `BufferManager.add_permission_prompt` (line 30)

  - Purpose: Add permission prompt overlay

  - Signature summary: positional=self, prompt_data

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `BufferManager.clear_all_overlays` (line 222)

  - Purpose: Clear all active overlays

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `BufferManager.get_overlay_count` (line 218)

  - Purpose: Get number of active overlays

  - Signature summary: positional=self

  - Async: False, Returns: int

  - Cross-file communications: none

- Function `BufferManager.get_overlay_render_order` (line 228)

  - Purpose: Get overlays in rendering order (bottom to top)

  - Signature summary: positional=self

  - Async: False, Returns: List[str]

  - Cross-file communications: none

- Function `BufferManager.has_active_overlays` (line 214)

  - Purpose: Check if there are any active overlays

  - Signature summary: positional=self

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `BufferManager.remove_buffer_status` (line 54)

  - Purpose: Remove buffer status overlay

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `BufferManager.remove_permission_prompt` (line 37)

  - Purpose: Remove permission prompt overlay

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `BufferManager.render_buffer_status` (line 149)

  - Purpose: Render buffer status overlay

  - Signature summary: positional=self

  - Async: False, Returns: Optional[Text]

  - Cross-file communications:

    - Calls `rich.text.Text` at line 200 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

    - Calls `frontier_colors.STATUS_COLORS.get` at line 201 (unresolved)

      - Purpose: No docstring provided

      - Expression: `STATUS_COLORS.get`

    - Calls `frontier_colors.FRONTIER_COLORS.get` at line 195 (unresolved)

      - Purpose: No docstring provided

      - Expression: `FRONTIER_COLORS.get`

- Function `BufferManager.render_permission_prompt` (line 60)

  - Purpose: Render permission prompt overlay

  - Signature summary: positional=self

  - Async: False, Returns: Optional[Text]

  - Cross-file communications:

    - Calls `rich.text.Text` at line 146 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

    - Calls `frontier_colors.FRONTIER_COLORS.get` at line 147 (unresolved)

      - Purpose: No docstring provided

      - Expression: `FRONTIER_COLORS.get`

- Function `BufferManager.update_buffer_status` (line 49)

  - Purpose: Update existing buffer status

  - Signature summary: positional=self, status_data

  - Async: False, Returns: None

  - Cross-file communications: none


## modules/streaming_display/core.py

- Module: `modules.streaming_display.core`

- Function `StreamingDisplay.__init__` (line 59)

  - Purpose: No docstring provided

  - Signature summary: positional=self; vararg=args; kwarg=kwargs

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `modules.streaming_display.selection.TextSelection` at line 70 (unresolved)

      - Purpose: No docstring provided

      - Expression: `TextSelection`

    - Calls `modules.streaming_display.markdown.MarkdownProcessor` at line 71 (unresolved)

      - Purpose: No docstring provided

      - Expression: `MarkdownProcessor`

    - Calls `modules.streaming_display.buffers.BufferManager` at line 72 (unresolved)

      - Purpose: No docstring provided

      - Expression: `BufferManager`

    - Calls `modules.streaming_display.mouse.MouseHandler` at line 73 (unresolved)

      - Purpose: No docstring provided

      - Expression: `MouseHandler`

- Function `StreamingDisplay._do_scroll` (line 281)

  - Purpose: Perform the actual scroll operation

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamingDisplay._get_scroll_offset` (line 297)

  - Purpose: Get current scroll offset

  - Signature summary: positional=self

  - Async: False, Returns: int

  - Cross-file communications: none

- Function `StreamingDisplay._get_total_lines` (line 309)

  - Purpose: Get total number of lines in content

  - Signature summary: positional=self

  - Async: False, Returns: int

  - Cross-file communications: none

- Function `StreamingDisplay._rebuild_display` (line 241)

  - Purpose: Rebuild the display content with all overlays

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `rich.text.Text` at line 250 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

- Function `StreamingDisplay._scroll_to_bottom` (line 273)

  - Purpose: Scroll to bottom of content

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamingDisplay.action_copy_all` (line 204)

  - Purpose: Copy all content to clipboard

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamingDisplay.action_select_all` (line 199)

  - Purpose: Select all content

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamingDisplay.add_buffer_status` (line 183)

  - Purpose: Add buffer status overlay

  - Signature summary: positional=self, status_data

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamingDisplay.add_permission_prompt` (line 173)

  - Purpose: Add permission prompt overlay

  - Signature summary: positional=self, prompt_data

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamingDisplay.buffer_manager` (line 85)

  - Purpose: No docstring provided

  - Signature summary: positional=self

  - Async: False, Returns: BufferManager

  - Cross-file communications: none

- Function `StreamingDisplay.clear` (line 152)

  - Purpose: Clear all content from the display

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamingDisplay.finish_stream` (line 97)

  - Purpose: Complete the stream and display accumulated content

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `rich.text.Text` at line 108 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

- Function `StreamingDisplay.markdown_processor` (line 81)

  - Purpose: No docstring provided

  - Signature summary: positional=self

  - Async: False, Returns: MarkdownProcessor

  - Cross-file communications: none

- Function `StreamingDisplay.mouse_handler` (line 89)

  - Purpose: No docstring provided

  - Signature summary: positional=self

  - Async: False, Returns: MouseHandler

  - Cross-file communications: none

- Function `StreamingDisplay.on_mouse_down` (line 212)

  - Purpose: Handle mouse button press

  - Signature summary: positional=self, event

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamingDisplay.on_mouse_move` (line 217)

  - Purpose: Handle mouse movement

  - Signature summary: positional=self, event

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamingDisplay.on_mouse_up` (line 222)

  - Purpose: Handle mouse button release

  - Signature summary: positional=self, event

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamingDisplay.remove_buffer_status` (line 193)

  - Purpose: Remove buffer status overlay

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamingDisplay.remove_permission_prompt` (line 178)

  - Purpose: Remove permission prompt overlay

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamingDisplay.set_laser_colors` (line 164)

  - Purpose: Set laser effect colors

  - Signature summary: positional=self, colors

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamingDisplay.set_laser_enabled` (line 168)

  - Purpose: Enable or disable laser effect

  - Signature summary: positional=self, enabled

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamingDisplay.text_selection` (line 77)

  - Purpose: No docstring provided

  - Signature summary: positional=self

  - Async: False, Returns: TextSelection

  - Cross-file communications: none

- Function `StreamingDisplay.update_buffer_status` (line 188)

  - Purpose: Update buffer status overlay

  - Signature summary: positional=self, status_data

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamingDisplay.watch_selection_end` (line 234)

  - Purpose: React to selection end changes

  - Signature summary: positional=self, old_value, new_value

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamingDisplay.watch_selection_start` (line 228)

  - Purpose: React to selection start changes

  - Signature summary: positional=self, old_value, new_value

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamingDisplay.write` (line 118)

  - Purpose: Write text to the display with optional styling

  - Signature summary: positional=self, text, style

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `rich.text.Text` at line 143 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

- Function `StreamingDisplay.write_line` (line 148)

  - Purpose: Write a complete line to the display

  - Signature summary: positional=self, text, style

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamingDisplay.write_markdown` (line 159)

  - Purpose: Write markdown text with formatting

  - Signature summary: positional=self, text

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StreamingDisplay.write_stream` (line 92)

  - Purpose: Accumulate streaming text silently - display handled by buffer status

  - Signature summary: positional=self, text

  - Async: False, Returns: None

  - Cross-file communications: none


## modules/streaming_display/markdown.py

- Module: `modules.streaming_display.markdown`

- Function `MarkdownProcessor.__init__` (line 27)

  - Purpose: No docstring provided

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `markdown_renderer.get_markdown_renderer` at line 28 (unresolved)

      - Purpose: No docstring provided

      - Expression: `get_markdown_renderer`

    - Calls `rich.console.Console` at line 29 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Console`

- Function `MarkdownProcessor.extract_code_blocks` (line 74)

  - Purpose: Extract code blocks from markdown text

  - Signature summary: positional=self, text

  - Async: False, Returns: list

  - Cross-file communications: none

- Function `MarkdownProcessor.format_code_block` (line 102)

  - Purpose: Format a code block with syntax highlighting

  - Signature summary: positional=self, code, language

  - Async: False, Returns: Text

  - Cross-file communications:

    - Calls `pygments.lexers.get_lexer_by_name` at line 111 (unresolved)

      - Purpose: No docstring provided

      - Expression: `get_lexer_by_name`

    - Calls `pygments.lexers.TextLexer` at line 115 (unresolved)

      - Purpose: No docstring provided

      - Expression: `TextLexer`

    - Calls `pygments.formatters.Terminal256Formatter` at line 117 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Terminal256Formatter`

    - Calls `pygments.highlight` at line 118 (unresolved)

      - Purpose: No docstring provided

      - Expression: `highlight`

    - Calls `rich.text.Text.from_ansi` at line 119 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text.from_ansi`

    - Calls `frontier_colors.FRONTIER_COLORS.get` at line 123 (unresolved)

      - Purpose: No docstring provided

      - Expression: `FRONTIER_COLORS.get`

    - Calls `rich.text.Text` at line 124 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

- Function `MarkdownProcessor.format_emphasis` (line 177)

  - Purpose: Format bold and italic text

  - Signature summary: positional=self, text

  - Async: False, Returns: Text

  - Cross-file communications:

    - Calls `rich.text.Text` at line 179 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

- Function `MarkdownProcessor.format_headers` (line 142)

  - Purpose: Format markdown headers

  - Signature summary: positional=self, text

  - Async: False, Returns: Text

  - Cross-file communications:

    - Calls `rich.text.Text` at line 145 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

    - Calls `frontier_colors.FRONTIER_COLORS.get` at line 168 (unresolved)

      - Purpose: No docstring provided

      - Expression: `FRONTIER_COLORS.get`

- Function `MarkdownProcessor.format_inline_code` (line 126)

  - Purpose: Format inline code spans

  - Signature summary: positional=self, text

  - Async: False, Returns: Text

  - Cross-file communications:

    - Calls `rich.text.Text` at line 128 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

    - Calls `frontier_colors.FRONTIER_COLORS.get` at line 137 (unresolved)

      - Purpose: No docstring provided

      - Expression: `FRONTIER_COLORS.get`

- Function `MarkdownProcessor.is_markdown_content` (line 55)

  - Purpose: Detect if text contains markdown formatting

  - Signature summary: positional=self, text

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `MarkdownProcessor.process_markdown` (line 31)

  - Purpose: Process markdown text into Rich Text object

  - Signature summary: positional=self, markdown_text

  - Async: False, Returns: Text

  - Cross-file communications:

    - Calls `rich.text.Text` at line 53 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

    - Calls `rich.markdown.Markdown` at line 42 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Markdown`

    - Calls `rich.text.Text.from_ansi` at line 49 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text.from_ansi`

- Function `get_markdown_renderer` (line 19)

  - Purpose: No docstring provided

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications: none


## modules/streaming_display/mouse.py

- Module: `modules.streaming_display.mouse`

- Function `MouseHandler.__init__` (line 22)

  - Purpose: No docstring provided

  - Signature summary: positional=self, parent_widget, text_selection

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `MouseHandler._is_word_char` (line 188)

  - Purpose: Check if character is part of a word

  - Signature summary: positional=self, char

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `MouseHandler._screen_to_content_coords` (line 92)

  - Purpose: Convert screen coordinates to content line/column

  - Signature summary: positional=self, screen_x, screen_y

  - Async: False, Returns: Tuple[Optional[int], Optional[int]]

  - Cross-file communications: none

- Function `MouseHandler._select_line_at_position` (line 163)

  - Purpose: Select the entire line at the given position

  - Signature summary: positional=self, line_idx

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `MouseHandler._select_word_at_position` (line 126)

  - Purpose: Select the word at the given position

  - Signature summary: positional=self, line_idx, col_idx

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `MouseHandler.get_click_count` (line 192)

  - Purpose: Get current click count for multi-click detection

  - Signature summary: positional=self

  - Async: False, Returns: int

  - Cross-file communications: none

- Function `MouseHandler.handle_mouse_down` (line 29)

  - Purpose: Handle mouse button press

  - Signature summary: positional=self, event

  - Async: False, Returns: bool

  - Cross-file communications:

    - Calls `time.time` at line 42 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

- Function `MouseHandler.handle_mouse_move` (line 67)

  - Purpose: Handle mouse movement during selection

  - Signature summary: positional=self, event

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `MouseHandler.handle_mouse_up` (line 85)

  - Purpose: Handle mouse button release

  - Signature summary: positional=self, event

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `MouseHandler.reset_click_count` (line 196)

  - Purpose: Reset click count

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none


## modules/streaming_display/selection.py

- Module: `modules.streaming_display.selection`

- Function `TextSelection.__init__` (line 19)

  - Purpose: No docstring provided

  - Signature summary: positional=self, parent_widget

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `TextSelection.apply_selection_highlight` (line 90)

  - Purpose: Apply selection highlighting to content lines

  - Signature summary: positional=self, content_lines

  - Async: False, Returns: list

  - Cross-file communications:

    - Calls `rich.style.Style` at line 104 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Style`

    - Calls `frontier_colors.FRONTIER_COLORS.get` at line 104 (unresolved)

      - Purpose: No docstring provided

      - Expression: `FRONTIER_COLORS.get`

    - Calls `rich.text.Text` at line 114 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

- Function `TextSelection.clear_selection` (line 40)

  - Purpose: Clear current selection

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `TextSelection.copy_all` (line 186)

  - Purpose: Copy all content to clipboard

  - Signature summary: positional=self, content_lines

  - Async: False, Returns: bool

  - Cross-file communications:

    - Calls `platform.system` at line 205 (unresolved)

      - Purpose: No docstring provided

      - Expression: `platform.system`

    - Calls `subprocess.Popen` at line 220 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.Popen`

- Function `TextSelection.copy_selection` (line 150)

  - Purpose: Copy selected text to clipboard

  - Signature summary: positional=self, content_lines

  - Async: False, Returns: bool

  - Cross-file communications:

    - Calls `platform.system` at line 160 (unresolved)

      - Purpose: No docstring provided

      - Expression: `platform.system`

    - Calls `subprocess.Popen` at line 176 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.Popen`

- Function `TextSelection.end_selection` (line 36)

  - Purpose: End text selection

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `TextSelection.get_selected_text` (line 52)

  - Purpose: Extract selected text from content lines

  - Signature summary: positional=self, content_lines

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `TextSelection.has_selection` (line 46)

  - Purpose: Check if there is an active selection

  - Signature summary: positional=self

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `TextSelection.select_all` (line 133)

  - Purpose: Select all text content

  - Signature summary: positional=self, content_lines

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `TextSelection.start_selection` (line 25)

  - Purpose: Start text selection at given position

  - Signature summary: positional=self, line, col

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `TextSelection.update_selection` (line 31)

  - Purpose: Update selection end position

  - Signature summary: positional=self, line, col

  - Async: False, Returns: None

  - Cross-file communications: none


## modules/streaming_display_legacy.py

- Module: `modules.streaming_display_legacy`

- Functions: none

## modules/system_capability.py

- Module: `modules.system_capability`

- Function `SystemCapability.__init__` (line 17)

  - Purpose: No docstring provided

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `platform.system` at line 18 (unresolved)

      - Purpose: No docstring provided

      - Expression: `platform.system`

    - Calls `platform.machine` at line 19 (unresolved)

      - Purpose: No docstring provided

      - Expression: `platform.machine`

    - Calls `platform.release` at line 20 (unresolved)

      - Purpose: No docstring provided

      - Expression: `platform.release`

- Function `SystemCapability._categorize_tier` (line 181)

  - Purpose: Categorize system capability into green/yellow/red tier

  - Signature summary: positional=self, ram_gb, vram_gb

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `SystemCapability._detect_gpu` (line 101)

  - Purpose: Detect GPU VRAM and type

  - Signature summary: positional=self

  - Async: False, Returns: Tuple[Optional[int], Optional[str]]

  - Cross-file communications:

    - Calls `subprocess.run` at line 156 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `SystemCapability._detect_ram` (line 52)

  - Purpose: Detect total system RAM in GB

  - Signature summary: positional=self

  - Async: False, Returns: int

  - Cross-file communications:

    - Calls `subprocess.run` at line 82 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `SystemCapability._is_apple_silicon` (line 177)

  - Purpose: Check if running on Apple Silicon (M1/M2/M3/etc.)

  - Signature summary: positional=self

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `SystemCapability.detect_capabilities` (line 24)

  - Purpose: Detect system capabilities (RAM, GPU, CPU)

  - Signature summary: positional=self

  - Async: False, Returns: Dict

  - Cross-file communications: none

- Function `SystemCapability.get_privacy_notice` (line 213)

  - Purpose: Return privacy notice about what we detect

  - Signature summary: positional=self

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `SystemCapability.get_tier_description` (line 204)

  - Purpose: Get human-readable description of capability tier

  - Signature summary: positional=self, tier

  - Async: False, Returns: str

  - Cross-file communications: none


## modules/tool_call_utils.py

- Module: `modules.tool_call_utils`

- Function `extract_tool_calls_from_text` (line 68)

  - Purpose: Extract tool calls embedded in text content.

  - Signature summary: positional=text

  - Async: False, Returns: Tuple[Optional[List[Dict[str, Any]]], str]

  - Cross-file communications:

    - Calls `re.finditer` at line 117 (unresolved)

      - Purpose: No docstring provided

      - Expression: `re.finditer`

    - Calls `json.loads` at line 126 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.loads`

    - Calls `uuid.uuid4` at line 132 (unresolved)

      - Purpose: No docstring provided

      - Expression: `uuid.uuid4`

    - Calls `json.dumps` at line 136 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dumps`

    - Calls `re.sub` at line 146 (unresolved)

      - Purpose: No docstring provided

      - Expression: `re.sub`

- Function `normalize_tool_call_messages` (line 12)

  - Purpose: Return a sanitized copy of messages with well-formed tool call payloads.

  - Signature summary: positional=messages

  - Async: False, Returns: List[Dict[str, Any]]

  - Cross-file communications:

    - Calls `copy.deepcopy` at line 35 (unresolved)

      - Purpose: No docstring provided

      - Expression: `deepcopy`

    - Calls `uuid.uuid4` at line 40 (unresolved)

      - Purpose: No docstring provided

      - Expression: `uuid.uuid4`


## modules/tool_permissions.py

- Module: `modules.tool_permissions`

- Function `ToolPermissionManager.__init__` (line 19)

  - Purpose: No docstring provided

  - Signature summary: positional=self, config_dir

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path.home` at line 20 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.home`

- Function `ToolPermissionManager._load_permissions` (line 42)

  - Purpose: Load tool permissions from file

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.load` at line 52 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

- Function `ToolPermissionManager._save_permissions` (line 56)

  - Purpose: Save permissions to file

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.dump` at line 60 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dump`

- Function `ToolPermissionManager.add_allowed_tool` (line 124)

  - Purpose: Add tool to allowed list (skip future prompts)

  - Signature summary: positional=self, tool_name

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ToolPermissionManager.assess_path_risk` (line 68)

  - Purpose: Assess risk level of file path

  - Signature summary: positional=self, file_path, current_dir

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path` at line 91 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

    - Calls `os.getcwd` at line 78 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.getcwd`

    - Calls `pathlib.Path.home` at line 94 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.home`

- Function `ToolPermissionManager.format_tool_preview` (line 205)

  - Purpose: Format tool operation for preview

  - Signature summary: positional=self, tool_name, args, path_risk, current_dir

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path` at line 240 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

    - Calls `os.getcwd` at line 237 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.getcwd`

- Function `ToolPermissionManager.get_allowed_tools` (line 294)

  - Purpose: Get list of allowed tools

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ToolPermissionManager.is_tool_allowed` (line 64)

  - Purpose: Check if tool is in allowed list

  - Signature summary: positional=self, tool_name

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ToolPermissionManager.prompt_for_permission` (line 244)

  - Purpose: Prompt user for permission to execute tool

  - Signature summary: positional=self, tool_name, args, current_dir

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ToolPermissionManager.remove_allowed_tool` (line 134)

  - Purpose: Remove tool from allowed list

  - Signature summary: positional=self, tool_name

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ToolPermissionManager.set_auto_accept` (line 142)

  - Purpose: Enable/disable global auto-accept mode

  - Signature summary: positional=self, enabled

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ToolPermissionManager.should_prompt` (line 148)

  - Purpose: Determine if we should prompt for permission

  - Signature summary: positional=self, tool_name, args, current_dir

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ToolPermissionManager.show_status` (line 298)

  - Purpose: Show current permission status

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none


## modules/tool_registry.py

- Module: `modules.tool_registry`

- Function `ToolRegistry.__init__` (line 70)

  - Purpose: No docstring provided

  - Signature summary: positional=self, app, session

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ToolRegistry._clear_statusline_for_tool` (line 317)

  - Purpose: Clear statusline indicator for tool

  - Signature summary: positional=self, tool_name

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ToolRegistry._register_default_tools` (line 79)

  - Purpose: Register default API tools and operations

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ToolRegistry._show_tool_permission_prompt` (line 254)

  - Purpose: Show permission prompt for tool execution

  - Signature summary: positional=self, permission

  - Async: True, Returns: bool

  - Cross-file communications:

    - Calls `permission_buffer_manager.get_permission_buffer_manager` at line 284 (unresolved)

      - Purpose: No docstring provided

      - Expression: `get_permission_buffer_manager`

- Function `ToolRegistry._update_statusline_for_tool` (line 299)

  - Purpose: Update statusline with tool status

  - Signature summary: positional=self, tool_name, status

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ToolRegistry.execute_tool` (line 161)

  - Purpose: Execute a tool with permission-first flow

  - Signature summary: positional=self, tool_name, execute_func; vararg=args; kwarg=kwargs

  - Async: True, Returns: Any

  - Cross-file communications:

    - Calls `asyncio.to_thread` at line 220 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.to_thread`

    - Calls `asyncio.sleep` at line 247 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

- Function `ToolRegistry.get_active_tools` (line 327)

  - Purpose: Get list of currently executing tools

  - Signature summary: positional=self

  - Async: False, Returns: List[ToolExecution]

  - Cross-file communications: none

- Function `ToolRegistry.get_background_tools` (line 331)

  - Purpose: Get list of tools running in background

  - Signature summary: positional=self

  - Async: False, Returns: List[ToolExecution]

  - Cross-file communications: none

- Function `ToolRegistry.register_tool` (line 157)

  - Purpose: Register a new tool with permissions

  - Signature summary: positional=self, permission

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `execute_tool_with_permissions` (line 348)

  - Purpose: Execute any tool with permission-first flow

  - Signature summary: positional=app, session, tool_name, execute_func; vararg=args; kwarg=kwargs

  - Async: True, Returns: Any

  - Cross-file communications: none

- Function `get_tool_registry` (line 340)

  - Purpose: Get or create global tool registry

  - Signature summary: positional=app, session

  - Async: False, Returns: ToolRegistry

  - Cross-file communications: none


## modules/tools/core_tools.py

- Module: `modules.tools.core_tools`

- Function `_base_dir` (line 25)

  - Purpose: No docstring provided

  - Signature summary: positional=session, context

  - Async: False, Returns: Path

  - Cross-file communications:

    - Calls `pathlib.Path` at line 29 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

    - Calls `pathlib.Path.cwd` at line 30 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.cwd`

- Function `_write_result` (line 21)

  - Purpose: No docstring provided

  - Signature summary: positional=app, header, body

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `tool_bash` (line 116)

  - Purpose: No docstring provided

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.to_thread` at line 139 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.to_thread`

- Function `tool_bash._run` (line 123)

  - Purpose: No docstring provided

  - Signature summary: (no parameters)

  - Async: False, Returns: str

  - Cross-file communications:

    - Calls `subprocess.run` at line 125 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `tool_configure_headers` (line 208)

  - Purpose: No docstring provided

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.header_autoconfig.auto_configure_headers` at line 217 (ok)

      - Purpose: Auto-configure headers for a model by fetching from API page

      - Expression: `auto_configure_headers`

    - Calls `json.dumps` at line 223 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.dumps`

- Function `tool_edit` (line 84)

  - Purpose: No docstring provided

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path` at line 93 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

    - Calls `asyncio.to_thread` at line 104 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.to_thread`

- Function `tool_edit._edit` (line 95)

  - Purpose: No docstring provided

  - Signature summary: (no parameters)

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `tool_github` (line 197)

  - Purpose: No docstring provided

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.to_thread` at line 203 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.to_thread`

- Function `tool_glob` (line 145)

  - Purpose: No docstring provided

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.to_thread` at line 163 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.to_thread`

- Function `tool_glob._search` (line 153)

  - Purpose: No docstring provided

  - Signature summary: (no parameters)

  - Async: False, Returns: str

  - Cross-file communications:

    - Calls `glob.glob` at line 154 (unresolved)

      - Purpose: No docstring provided

      - Expression: `glob.glob`

    - Calls `pathlib.Path` at line 158 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

- Function `tool_grep` (line 168)

  - Purpose: No docstring provided

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.to_thread` at line 192 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.to_thread`

- Function `tool_grep._search` (line 176)

  - Purpose: No docstring provided

  - Signature summary: (no parameters)

  - Async: False, Returns: str

  - Cross-file communications:

    - Calls `subprocess.run` at line 178 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `tool_read` (line 33)

  - Purpose: No docstring provided

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path` at line 39 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

    - Calls `asyncio.to_thread` at line 48 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.to_thread`

- Function `tool_read._read` (line 41)

  - Purpose: No docstring provided

  - Signature summary: (no parameters)

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `tool_write` (line 60)

  - Purpose: No docstring provided

  - Signature summary: positional=app, session; kwarg=context

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path` at line 67 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

    - Calls `asyncio.to_thread` at line 75 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.to_thread`

- Function `tool_write._write` (line 69)

  - Purpose: No docstring provided

  - Signature summary: (no parameters)

  - Async: False, Returns: str

  - Cross-file communications: none


## modules/tui/__init__.py

- Module: `modules.tui`

- Functions: none

## modules/tui/command_handlers.py

- Module: `modules.tui.command_handlers`

- Function `CommandHandlers._handle_user_message` (line 276)

  - Purpose: Handle user message submission (to be implemented by main TUI class)

  - Signature summary: positional=self, user_input, prompt_input

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `CommandHandlers.on_multi_line_input_command_suggestion_navigate` (line 198)

  - Purpose: Handle arrow key navigation in command suggestions

  - Signature summary: positional=self, event

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `CommandHandlers.on_multi_line_input_command_suggestion_select` (line 211)

  - Purpose: Handle Enter key with command suggestions active

  - Signature summary: positional=self, event

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `command_registry.CommandRegistry` at line 226 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandRegistry`

    - Calls `sys.stderr.write` at line 258 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.write`

    - Calls `sys.stderr.flush` at line 259 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.flush`

    - Calls `traceback.format_exc` at line 258 (unresolved)

      - Purpose: No docstring provided

      - Expression: `traceback.format_exc`

- Function `CommandHandlers.on_multi_line_input_hide_command_suggestions` (line 175)

  - Purpose: Handle hiding command suggestions

  - Signature summary: positional=self, event

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `sys.stderr.write` at line 195 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.write`

    - Calls `sys.stderr.flush` at line 196 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.flush`

- Function `CommandHandlers.on_multi_line_input_show_command_suggestions` (line 24)

  - Purpose: Handle slash command typed - show/update command suggestions

  - Signature summary: positional=self, event

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `os.getenv` at line 170 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.getenv`

    - Calls `command_suggestions.CommandMatch` at line 117 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandMatch`

    - Calls `command_registry.CommandRegistry` at line 97 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandRegistry`

    - Calls `sys.stderr.write` at line 166 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.write`

    - Calls `sys.stderr.flush` at line 161 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.flush`

    - Calls `traceback.format_exc` at line 173 (unresolved)

      - Purpose: No docstring provided

      - Expression: `traceback.format_exc`

- Function `CommandHandlers.on_multi_line_input_submitted` (line 261)

  - Purpose: Handle message submission from MultiLineInput

  - Signature summary: positional=self, event

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `asyncio.create_task` at line 274 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.create_task`


## modules/tui/core.py

- Module: `modules.tui.core`

- Function `OpenCLITUI.__init__` (line 155)

  - Purpose: No docstring provided

  - Signature summary: positional=self, session, config

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `tui_config.get_tui_config` at line 159 (unresolved)

      - Purpose: No docstring provided

      - Expression: `get_tui_config`

    - Calls `modules.color_manager.configure_color_mode` at line 165 (ok)

      - Purpose: Configure color mode from TUI config

      - Expression: `configure_color_mode`

    - Calls `color_manager.configure_color_mode` at line 169 (unresolved)

      - Purpose: No docstring provided

      - Expression: `configure_color_mode`

    - Calls `asyncio.Queue` at line 177 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.Queue`

- Function `OpenCLITUI._generate_ai_response` (line 412)

  - Purpose: Generate AI response using existing streaming infrastructure

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `modules.async_interactive.api_requests.perform_anthropic_request` at line 434 (ok)

      - Purpose: Make request to Anthropic API

      - Expression: `perform_anthropic_request`

    - Calls `modules.async_interactive.api_requests.perform_google_request` at line 436 (ok)

      - Purpose: Make request to Google Gemini API

      - Expression: `perform_google_request`

    - Calls `modules.async_interactive.streaming.StreamHandler` at line 442 (unresolved)

      - Purpose: No docstring provided

      - Expression: `StreamHandler`

    - Calls `modules.async_interactive.tool_integration.get_tool_executor` at line 481 (ok)

      - Purpose: Get or create global tool executor instance

      - Expression: `get_tool_executor`

    - Calls `traceback.print_exc` at line 524 (unresolved)

      - Purpose: No docstring provided

      - Expression: `traceback.print_exc`

- Function `OpenCLITUI._handle_api_operation_response` (line 235)

  - Purpose: Handle API operation permission responses

  - Signature summary: positional=self, response, data

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `OpenCLITUI._handle_bash_command_response` (line 230)

  - Purpose: Handle bash command permission responses

  - Signature summary: positional=self, response, data

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `OpenCLITUI._handle_file_operation_response` (line 225)

  - Purpose: Handle file operation permission responses

  - Signature summary: positional=self, response, data

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `OpenCLITUI._handle_tool_execution_response` (line 240)

  - Purpose: Handle tool execution permission responses

  - Signature summary: positional=self, response, data

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `OpenCLITUI._handle_user_message` (line 368)

  - Purpose: Handle user message submission

  - Signature summary: positional=self, user_input, prompt_input

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `execution.permission_manager.get_permission_manager` at line 387 (unresolved)

      - Purpose: No docstring provided

      - Expression: `get_permission_manager`

    - Calls `command_router.route_command_unified` at line 398 (unresolved)

      - Purpose: No docstring provided

      - Expression: `route_command_unified`

    - Calls `traceback.print_exc` at line 405 (unresolved)

      - Purpose: No docstring provided

      - Expression: `traceback.print_exc`

- Function `OpenCLITUI._process_write_queue` (line 344)

  - Purpose: Process queued write operations

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.sleep` at line 351 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

- Function `OpenCLITUI._resolve_content_widget` (line 355)

  - Purpose: Resolve the content widget (StreamingDisplay or Static)

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `textual.widgets.Static` at line 366 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Static`

- Function `OpenCLITUI._setup_permission_system` (line 190)

  - Purpose: Initialize unified permission system integration with TUI

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `modules.permissions.get_unified_permission_manager` at line 196 (unresolved)

      - Purpose: No docstring provided

      - Expression: `get_unified_permission_manager`

    - Calls `sys.stderr.write` at line 221 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.write`

    - Calls `sys.stderr.flush` at line 222 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.flush`

- Function `OpenCLITUI._write_direct` (line 330)

  - Purpose: Write directly to content widget

  - Signature summary: positional=self, text, end

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `OpenCLITUI.action_clear_screen` (line 544)

  - Purpose: Clear the screen content

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `OpenCLITUI.action_quit_app` (line 526)

  - Purpose: Quit the application

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `OpenCLITUI.action_toggle_performance` (line 530)

  - Purpose: Toggle performance monitoring

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `OpenCLITUI.action_toggle_refactoring` (line 537)

  - Purpose: Toggle refactoring monitoring

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `OpenCLITUI.clear_sdk_status` (line 577)

  - Purpose: Clear SDK initialization status

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `OpenCLITUI.compose` (line 245)

  - Purpose: Compose the TUI layout

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `textual.containers.Vertical` at line 247 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Vertical`

    - Calls `textual.containers.VerticalScroll` at line 251 (unresolved)

      - Purpose: No docstring provided

      - Expression: `VerticalScroll`

    - Calls `streaming_display.StreamingDisplay` at line 252 (unresolved)

      - Purpose: No docstring provided

      - Expression: `StreamingDisplay`

    - Calls `textual.widgets.Static` at line 272 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Static`

    - Calls `command_suggestions.CommandSuggestionBuffer` at line 258 (unresolved)

      - Purpose: No docstring provided

      - Expression: `CommandSuggestionBuffer`

    - Calls `sdk_loading_buffer.SDKLoadingBuffer` at line 262 (unresolved)

      - Purpose: No docstring provided

      - Expression: `SDKLoadingBuffer`

    - Calls `textual.containers.Container` at line 265 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Container`

    - Calls `input_widget.MultiLineInput` at line 267 (unresolved)

      - Purpose: No docstring provided

      - Expression: `MultiLineInput`

    - Calls `modules.tui.status_lines.PerformanceStatusLine` at line 275 (unresolved)

      - Purpose: No docstring provided

      - Expression: `PerformanceStatusLine`

    - Calls `modules.tui.status_lines.RefactoringStatusLine` at line 276 (unresolved)

      - Purpose: No docstring provided

      - Expression: `RefactoringStatusLine`

    - Calls `modules.tui.status_lines.StatusLine` at line 277 (unresolved)

      - Purpose: No docstring provided

      - Expression: `StatusLine`

- Function `OpenCLITUI.disable_docker_stats` (line 597)

  - Purpose: Disable Docker stats in status line

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `OpenCLITUI.enable_docker_stats` (line 592)

  - Purpose: Enable Docker stats in status line

  - Signature summary: positional=self, container_name

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `OpenCLITUI.on_key` (line 556)

  - Purpose: Handle global key events

  - Signature summary: positional=self, event

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `OpenCLITUI.on_mount` (line 279)

  - Purpose: Initialize the TUI when mounted

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `asyncio.create_task` at line 287 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.create_task`

- Function `OpenCLITUI.on_unmount` (line 603)

  - Purpose: Clean up when app is unmounted

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `OpenCLITUI.show_sdk_status` (line 572)

  - Purpose: Show SDK initialization status

  - Signature summary: positional=self, message

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `OpenCLITUI.start_spinner` (line 582)

  - Purpose: Start status line spinner

  - Signature summary: positional=self, mode

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `OpenCLITUI.stop_spinner` (line 587)

  - Purpose: Stop status line spinner

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `OpenCLITUI.write` (line 322)

  - Purpose: Queue a write operation to prevent blocking

  - Signature summary: positional=self, text, end

  - Async: False, Returns: None

  - Cross-file communications: none


## modules/tui/model_handlers.py

- Module: `modules.tui.model_handlers`

- Function `ModelHandlers._check_ollama_status` (line 276)

  - Purpose: Check if Ollama is running

  - Signature summary: positional=self

  - Async: False, Returns: bool

  - Cross-file communications:

    - Calls `subprocess.run` at line 280 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `ModelHandlers._cleanup_local_model_state` (line 311)

  - Purpose: Clean up local model selection state

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ModelHandlers._get_popular_models` (line 285)

  - Purpose: Get list of popular models for the browser

  - Signature summary: positional=self

  - Async: False, Returns: List[Dict[str, Any]]

  - Cross-file communications: none

- Function `ModelHandlers._handle_coder_selection` (line 230)

  - Purpose: Handle coder model selection and execute dual setup

  - Signature summary: positional=self, option_data

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `ModelHandlers._handle_local_model_step` (line 23)

  - Purpose: Handle multi-step local model selection workflow

  - Signature summary: positional=self, current_step, option_data

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `ModelHandlers._handle_planner_selection` (line 188)

  - Purpose: Handle planner model selection and show coder options

  - Signature summary: positional=self, option_data, recs, is_installed

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `ModelHandlers._handle_setup_type_selection` (line 58)

  - Purpose: Handle setup type selection (existing/single/dual)

  - Signature summary: positional=self, option_data, recs, is_installed

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `ModelHandlers._handle_single_model_selection` (line 171)

  - Purpose: Handle single model selection and execute installation

  - Signature summary: positional=self, option_data

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `ModelHandlers._show_dual_model_planner_options` (line 134)

  - Purpose: Show dual model planner selection options

  - Signature summary: positional=self, recs, is_installed

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `ModelHandlers._show_single_model_options` (line 82)

  - Purpose: Show single model selection options

  - Signature summary: positional=self, recs, is_installed

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `ModelHandlers.show_model_browser` (line 250)

  - Purpose: Show the Ollama model browser

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none


## modules/tui/permission_handlers.py

- Module: `modules.tui.permission_handlers`

- Function `PermissionHandlers._cleanup_local_model_state` (line 285)

  - Purpose: Clean up local model selection state

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `PermissionHandlers._clear_permission_prompt` (line 312)

  - Purpose: Clear permission prompt from MultiLineInput

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `PermissionHandlers._handle_async_permission_cancellation` (line 226)

  - Purpose: Handle async permission cancellation

  - Signature summary: positional=self, event

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `importlib.import_module` at line 236 (unresolved)

      - Purpose: No docstring provided

      - Expression: `importlib.import_module`

    - Calls `modules.async_permissions.get_global_handler` at line 241 (ok)

      - Purpose: Get the global permission handler

      - Expression: `get_global_handler`

- Function `PermissionHandlers._handle_async_permission_response` (line 202)

  - Purpose: Handle async permission response

  - Signature summary: positional=self, event

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `importlib.import_module` at line 209 (unresolved)

      - Purpose: No docstring provided

      - Expression: `importlib.import_module`

    - Calls `modules.async_permissions.get_global_handler` at line 214 (ok)

      - Purpose: Get the global permission handler

      - Expression: `get_global_handler`

- Function `PermissionHandlers._handle_generic_permission_cancellation` (line 273)

  - Purpose: Handle generic permission cancellation

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `PermissionHandlers._handle_generic_permission_response` (line 253)

  - Purpose: Handle generic permission response (SDK loading buffer, etc.)

  - Signature summary: positional=self, event

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `PermissionHandlers._handle_local_model_selection` (line 133)

  - Purpose: Handle local model selection response

  - Signature summary: positional=self, event

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `importlib.import_module` at line 140 (unresolved)

      - Purpose: No docstring provided

      - Expression: `importlib.import_module`

    - Calls `asyncio.create_task` at line 162 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.create_task`

- Function `PermissionHandlers._handle_model_browser_selection` (line 164)

  - Purpose: Handle model browser selection response

  - Signature summary: positional=self, event

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `importlib.import_module` at line 171 (unresolved)

      - Purpose: No docstring provided

      - Expression: `importlib.import_module`

- Function `PermissionHandlers._handle_provider_model_selection` (line 86)

  - Purpose: Handle provider model selection response

  - Signature summary: positional=self, event

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `importlib.import_module` at line 96 (unresolved)

      - Purpose: No docstring provided

      - Expression: `importlib.import_module`

    - Calls `modules.model_manager.ModelManager` at line 123 (unresolved)

      - Purpose: No docstring provided

      - Expression: `ModelManager`

- Function `PermissionHandlers._show_permission_prompt` (line 302)

  - Purpose: Show permission prompt inside MultiLineInput

  - Signature summary: positional=self, prompt_data

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `PermissionHandlers.on_multi_line_input_navigation_event` (line 61)

  - Purpose: Handle navigation events that should trigger permission auto-dismiss

  - Signature summary: positional=self, event

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `sys.stderr.write` at line 83 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.write`

    - Calls `sys.stderr.flush` at line 84 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.stderr.flush`

    - Calls `permissions.get_unified_permission_manager` at line 68 (unresolved)

      - Purpose: No docstring provided

      - Expression: `get_unified_permission_manager`

- Function `PermissionHandlers.on_multi_line_input_permission_cancelled` (line 52)

  - Purpose: Handle permission cancellation from MultiLineInput

  - Signature summary: positional=self, event

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `permissions.get_unified_permission_manager` at line 54 (unresolved)

      - Purpose: No docstring provided

      - Expression: `get_unified_permission_manager`

- Function `PermissionHandlers.on_multi_line_input_permission_response` (line 27)

  - Purpose: Handle permission response from MultiLineInput

  - Signature summary: positional=self, event

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `permissions.get_unified_permission_manager` at line 45 (unresolved)

      - Purpose: No docstring provided

      - Expression: `get_unified_permission_manager`

- Function `get_unified_permission_manager` (line 17)

  - Purpose: No docstring provided

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications: none


## modules/tui/status_lines.py

- Module: `modules.tui.status_lines`

- Function `PerformanceStatusLine.__init__` (line 25)

  - Purpose: No docstring provided

  - Signature summary: positional=self, session; kwarg=kwargs

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `PerformanceStatusLine._update_display` (line 41)

  - Purpose: Periodic update callback - lightweight (2 sec)

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `PerformanceStatusLine.on_mount` (line 31)

  - Purpose: Initialize performance monitor when mounted

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `performance_monitor.get_monitor` at line 38 (unresolved)

      - Purpose: No docstring provided

      - Expression: `get_monitor`

- Function `PerformanceStatusLine.render` (line 46)

  - Purpose: Render performance statusline

  - Signature summary: positional=self

  - Async: False, Returns: Text

  - Cross-file communications:

    - Calls `rich.text.Text` at line 58 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

    - Calls `rich.text.Text.from_markup` at line 56 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text.from_markup`

- Function `PerformanceStatusLine.toggle` (line 60)

  - Purpose: Toggle performance monitoring on/off, returns new state

  - Signature summary: positional=self

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `RefactoringStatusLine.__init__` (line 79)

  - Purpose: No docstring provided

  - Signature summary: positional=self, session; kwarg=kwargs

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `RefactoringStatusLine._update_display` (line 102)

  - Purpose: Periodic update callback - lightweight (2 sec)

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `RefactoringStatusLine.on_mount` (line 85)

  - Purpose: Initialize refactoring orchestrator when mounted

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `refactor_orchestrator.get_orchestrator` at line 96 (unresolved)

      - Purpose: No docstring provided

      - Expression: `get_orchestrator`

- Function `RefactoringStatusLine.render` (line 107)

  - Purpose: Render refactoring statusline

  - Signature summary: positional=self

  - Async: False, Returns: Text

  - Cross-file communications:

    - Calls `rich.text.Text` at line 119 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

    - Calls `rich.text.Text.from_markup` at line 117 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text.from_markup`

- Function `RefactoringStatusLine.toggle` (line 121)

  - Purpose: Toggle refactoring monitoring on/off, returns new state

  - Signature summary: positional=self

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `StatusLine.__init__` (line 149)

  - Purpose: No docstring provided

  - Signature summary: positional=self, session, config; kwarg=kwargs

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StatusLine._spin` (line 273)

  - Purpose: Async task that updates the spinner

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.sleep` at line 279 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

- Function `StatusLine._update_docker_stats` (line 303)

  - Purpose: Async task that periodically updates Docker container stats

  - Signature summary: positional=self, container_name

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `docker_manager.DockerManager` at line 310 (unresolved)

      - Purpose: No docstring provided

      - Expression: `DockerManager`

    - Calls `asyncio.to_thread` at line 314 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.to_thread`

    - Calls `asyncio.sleep` at line 327 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

- Function `StatusLine.clear_sdk_init_status` (line 267)

  - Purpose: Clear SDK initialization status and stop spinner

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StatusLine.disable_docker_stats` (line 292)

  - Purpose: Disable Docker stats monitoring

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StatusLine.enable_docker_stats` (line 283)

  - Purpose: Enable Docker stats monitoring in statusline

  - Signature summary: positional=self, container_name

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `asyncio.create_task` at line 288 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.create_task`

- Function `StatusLine.hide_indicator` (line 345)

  - Purpose: Hide a contextual indicator in the statusline

  - Signature summary: positional=self, category

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StatusLine.render` (line 156)

  - Purpose: Render status bar

  - Signature summary: positional=self

  - Async: False, Returns: Text

  - Cross-file communications:

    - Calls `rich.text.Text` at line 158 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

    - Calls `datetime.datetime.now` at line 169 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

    - Calls `os.path.basename` at line 180 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.path.basename`

- Function `StatusLine.set_sdk_init_status` (line 261)

  - Purpose: Set SDK initialization status message and start spinner

  - Signature summary: positional=self, message

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StatusLine.show_indicator` (line 336)

  - Purpose: Show a contextual indicator in the statusline

  - Signature summary: positional=self, category, icon, color

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `StatusLine.start_spinner` (line 240)

  - Purpose: Start the IPC activity spinner

  - Signature summary: positional=self, mode

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `asyncio.create_task` at line 246 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.create_task`

- Function `StatusLine.stop_spinner` (line 248)

  - Purpose: Stop the IPC activity spinner

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none


## modules/tui_config.py

- Module: `modules.tui_config`

- Function `TUIConfig.get` (line 30)

  - Purpose: Utility helper to fetch nested configuration values.

  - Signature summary: positional=self, path, default

  - Async: False, Returns: Any

  - Cross-file communications: none

- Function `get_tui_config` (line 42)

  - Purpose: Return the singleton TUI configuration object.

  - Signature summary: (no parameters)

  - Async: False, Returns: TUIConfig

  - Cross-file communications: none


## modules/unified_command_executor.py

- Module: `modules.unified_command_executor`

- Function `CommandExecution.__init__` (line 307)

  - Purpose: No docstring provided

  - Signature summary: positional=self, command, permission, steps, app, session

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `CommandExecution.execute_with_live_progress` (line 359)

  - Purpose: Execute command with live progress updates in permission buffer

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.sleep` at line 456 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

- Function `CommandExecution.show_initial_permission_prompt` (line 323)

  - Purpose: Show initial permission prompt for command

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `UnifiedCommandExecutor.__init__` (line 80)

  - Purpose: No docstring provided

  - Signature summary: positional=self, app, session

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `UnifiedCommandExecutor._clear_statusline_context` (line 289)

  - Purpose: Clear statusline indicator for category

  - Signature summary: positional=self, category

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `UnifiedCommandExecutor._register_default_commands` (line 89)

  - Purpose: Register default command permissions

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `UnifiedCommandExecutor._update_statusline_context` (line 267)

  - Purpose: Update statusline with current command context

  - Signature summary: positional=self, category, status

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `UnifiedCommandExecutor.execute_command` (line 192)

  - Purpose: Execute a command with permission-first flow

  - Signature summary: positional=self, command, steps, on_complete

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.sleep` at line 263 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

- Function `UnifiedCommandExecutor.get_permission` (line 179)

  - Purpose: Get permission info for a command

  - Signature summary: positional=self, command

  - Async: False, Returns: Optional[CommandPermission]

  - Cross-file communications: none

- Function `UnifiedCommandExecutor.register_command` (line 175)

  - Purpose: Register a new command with permissions

  - Signature summary: positional=self, permission

  - Async: False, Returns: None

  - Cross-file communications: none


## modules/unified_display.py

- Module: `modules.unified_display`

- Function `UnifiedDisplay.__init__` (line 112)

  - Purpose: Args:

  - Signature summary: positional=self, app, stream_buffer

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `UnifiedDisplay._drain_loop` (line 148)

  - Purpose: Background task that drains buffer smoothly

  - Signature summary: positional=self, write_callback

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `UnifiedDisplay.start` (line 124)

  - Purpose: Start the unified display system

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `UnifiedDisplay.start_draining` (line 132)

  - Purpose: Start draining the stream buffer in background.

  - Signature summary: positional=self, write_callback

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.create_task` at line 144 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.create_task`

- Function `UnifiedDisplay.stop` (line 128)

  - Purpose: Stop the display system

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `UnifiedDisplay.stop_draining` (line 156)

  - Purpose: Stop the drain task gracefully

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `UnifiedDisplay.write` (line 166)

  - Purpose: Write text through queue (respects buffer state).

  - Signature summary: positional=self, text, markdown; kwarg=kwargs

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `UnifiedDisplay.write_to_buffer` (line 177)

  - Purpose: Add chunk to stream buffer.

  - Signature summary: positional=self, chunk

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `WriteQueue.__init__` (line 21)

  - Purpose: No docstring provided

  - Signature summary: positional=self, app

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `asyncio.Queue` at line 23 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.Queue`

- Function `WriteQueue._process_writes` (line 41)

  - Purpose: Background worker that processes queued writes

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.sleep` at line 82 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.sleep`

    - Calls `markdown_renderer.get_markdown_renderer` at line 61 (unresolved)

      - Purpose: No docstring provided

      - Expression: `get_markdown_renderer`

    - Calls `rich.text.Text` at line 69 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Text`

- Function `WriteQueue.start_worker` (line 27)

  - Purpose: Start background worker that processes writes in order

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications:

    - Calls `asyncio.create_task` at line 30 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.create_task`

- Function `WriteQueue.stop_worker` (line 32)

  - Purpose: Stop the write worker

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `WriteQueue.wait_empty` (line 98)

  - Purpose: Wait for all queued writes to complete

  - Signature summary: positional=self

  - Async: True, Returns: None

  - Cross-file communications: none

- Function `WriteQueue.write` (line 86)

  - Purpose: Queue a write operation.

  - Signature summary: positional=self, text, markdown; kwarg=kwargs

  - Async: True, Returns: None

  - Cross-file communications: none


## modules/upgrade_manager.py

- Module: `modules.upgrade_manager`

- Function `UpgradeManager.__init__` (line 15)

  - Purpose: No docstring provided

  - Signature summary: positional=self, config_dir

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path.home` at line 17 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.home`

- Function `UpgradeManager._categorize_changes` (line 519)

  - Purpose: Helper to categorize changes from git diff output

  - Signature summary: positional=self, diff_output

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `UpgradeManager._perform_rollback` (line 941)

  - Purpose: Internal rollback to specific backup

  - Signature summary: positional=self, backup_dir

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `shutil.rmtree` at line 948 (unresolved)

      - Purpose: No docstring provided

      - Expression: `shutil.rmtree`

    - Calls `shutil.copytree` at line 951 (unresolved)

      - Purpose: No docstring provided

      - Expression: `shutil.copytree`

- Function `UpgradeManager._update_archive_manifest` (line 604)

  - Purpose: Update archive/VERSIONS.md manifest

  - Signature summary: positional=self, version

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `datetime.datetime.now` at line 607 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

- Function `UpgradeManager._verify_agent_system` (line 753)

  - Purpose: Verify agent system is functional

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `yaml.safe_load` at line 767 (unresolved)

      - Purpose: No docstring provided

      - Expression: `yaml.safe_load`

- Function `UpgradeManager._verify_context_system` (line 789)

  - Purpose: Verify context system directories exist

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `UpgradeManager._verify_file_integrity` (line 675)

  - Purpose: Verify required files exist

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path.home` at line 682 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.home`

- Function `UpgradeManager._verify_module_imports` (line 696)

  - Purpose: Test module imports

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `sys.path.insert` at line 701 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys.path.insert`

- Function `UpgradeManager._verify_version_metadata` (line 723)

  - Purpose: Verify version.json structure

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.load` at line 736 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

- Function `UpgradeManager.archive_version` (line 571)

  - Purpose: Archive current version installer

  - Signature summary: positional=self, version

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `shutil.copy2` at line 593 (unresolved)

      - Purpose: No docstring provided

      - Expression: `shutil.copy2`

- Function `UpgradeManager.cleanup_upgrade_worktree` (line 316)

  - Purpose: Remove upgrade worktree

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `shutil.rmtree` at line 326 (unresolved)

      - Purpose: No docstring provided

      - Expression: `shutil.rmtree`

- Function `UpgradeManager.compare_branches` (line 456)

  - Purpose: Compare current branch against Main branch

  - Signature summary: positional=self, current_branch

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `UpgradeManager.create_backup` (line 556)

  - Purpose: Create timestamped backup of current installation

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `datetime.datetime.now` at line 558 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

    - Calls `pathlib.Path.home` at line 559 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path.home`

    - Calls `shutil.copytree` at line 564 (unresolved)

      - Purpose: No docstring provided

      - Expression: `shutil.copytree`

- Function `UpgradeManager.create_secure_pr` (line 210)

  - Purpose: Create PR to upstream using user's own GitHub credentials

  - Signature summary: positional=self, branch_name, pr_title, pr_body

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `UpgradeManager.create_upgrade_worktree` (line 264)

  - Purpose: Create a git worktree for testing the upgrade from upstream

  - Signature summary: positional=self, new_version

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `shutil.rmtree` at line 285 (unresolved)

      - Purpose: No docstring provided

      - Expression: `shutil.rmtree`

- Function `UpgradeManager.detect_changes` (line 495)

  - Purpose: Detect what changed between versions

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `UpgradeManager.fetch_upstream` (line 165)

  - Purpose: Fetch latest changes from official upstream repo (read-only)

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `UpgradeManager.get_changelog` (line 97)

  - Purpose: Get changelog for specific version

  - Signature summary: positional=self, version

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.load` at line 105 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

- Function `UpgradeManager.get_current_branch` (line 131)

  - Purpose: Get current git branch

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `UpgradeManager.get_current_version` (line 71)

  - Purpose: Get currently installed version

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.load` at line 79 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

- Function `UpgradeManager.get_new_version` (line 84)

  - Purpose: Get version from repo

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.load` at line 92 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

- Function `UpgradeManager.get_repo_info` (line 184)

  - Purpose: Get repository information using gh CLI

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.loads` at line 191 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.loads`

- Function `UpgradeManager.get_verification_steps` (line 114)

  - Purpose: Get verification steps for specific version

  - Signature summary: positional=self, version

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `json.load` at line 122 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.load`

- Function `UpgradeManager.install_new_version` (line 632)

  - Purpose: Run installation script from repo or worktree

  - Signature summary: positional=self, worktree_path

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path` at line 637 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

- Function `UpgradeManager.log` (line 29)

  - Purpose: Log message to file and optionally print

  - Signature summary: positional=self, message, level

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `datetime.datetime.now` at line 31 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

- Function `UpgradeManager.perform_upgrade` (line 807)

  - Purpose: Perform full upgrade with verification

  - Signature summary: positional=self, auto_rollback, worktree_path

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `datetime.datetime.now` at line 929 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

- Function `UpgradeManager.preflight_checks` (line 330)

  - Purpose: Run pre-upgrade checks

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `UpgradeManager.run_command` (line 39)

  - Purpose: Run shell command and return result

  - Signature summary: positional=self, cmd, cwd, timeout

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `subprocess.run` at line 42 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `UpgradeManager.setup_upstream_remote` (line 138)

  - Purpose: Ensure upstream remote is configured for pulling official updates

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `UpgradeManager.validate_architecture_compliance` (line 408)

  - Purpose: Validate code follows architecture guidelines

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `UpgradeManager.verify_installation` (line 653)

  - Purpose: Run verification tests

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none


## modules/uptime_checker.py

- Module: `modules.uptime_checker`

- Function `_extract_uptime_from_json` (line 207)

  - Purpose: Recursively search JSON data for uptime-related fields.

  - Signature summary: positional=data

  - Async: False, Returns: Optional[float]

  - Cross-file communications: none

- Function `_extract_uptime_from_json.normalize` (line 216)

  - Purpose: No docstring provided

  - Signature summary: positional=value

  - Async: False, Returns: Optional[float]

  - Cross-file communications: none

- Function `_get_status_message` (line 248)

  - Purpose: Generate human-readable status message based on uptime percentage

  - Signature summary: positional=uptime

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `_parse_current_uptime` (line 69)

  - Purpose: Parse current uptime percentage from page text

  - Signature summary: positional=html

  - Async: False, Returns: Optional[float]

  - Cross-file communications:

    - Calls `re.search` at line 91 (unresolved)

      - Purpose: No docstring provided

      - Expression: `re.search`

- Function `_parse_uptime_from_graph` (line 101)

  - Purpose: Parse uptime from graph data or metadata

  - Signature summary: positional=html

  - Async: False, Returns: Optional[float]

  - Cross-file communications:

    - Calls `re.search` at line 197 (unresolved)

      - Purpose: No docstring provided

      - Expression: `re.search`

    - Calls `re.finditer` at line 185 (unresolved)

      - Purpose: No docstring provided

      - Expression: `re.finditer`

    - Calls `html.unescape` at line 154 (unresolved)

      - Purpose: No docstring provided

      - Expression: `html_lib.unescape`

    - Calls `json.loads` at line 155 (unresolved)

      - Purpose: No docstring provided

      - Expression: `json.loads`

    - Calls `re.findall` at line 163 (unresolved)

      - Purpose: No docstring provided

      - Expression: `re.findall`

- Function `check_model_uptime` (line 14)

  - Purpose: Check current uptime status for a model

  - Signature summary: positional=model_id

  - Async: True, Returns: Tuple[bool, Optional[float], str]

  - Cross-file communications:

    - Calls `time.time` at line 29 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

    - Calls `httpx.AsyncClient` at line 40 (unresolved)

      - Purpose: No docstring provided

      - Expression: `httpx.AsyncClient`

- Function `get_user_recommendation` (line 288)

  - Purpose: Get recommendation for user based on uptime status

  - Signature summary: positional=uptime, model_id

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `is_model_healthy` (line 270)

  - Purpose: Determine if model is healthy enough to attempt requests

  - Signature summary: positional=uptime

  - Async: False, Returns: bool

  - Cross-file communications: none


## modules/verbose_manager.py

- Module: `modules.verbose_manager`

- Function `PerformanceMonitor.__init__` (line 89)

  - Purpose: No docstring provided

  - Signature summary: positional=self, verbose_manager

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `PerformanceMonitor.clear` (line 169)

  - Purpose: Clear all metrics

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `PerformanceMonitor.get_operation_stats` (line 138)

  - Purpose: Get stats for specific operation type

  - Signature summary: positional=self, operation

  - Async: False, Returns: Dict

  - Cross-file communications: none

- Function `PerformanceMonitor.get_stats` (line 119)

  - Purpose: Get performance statistics

  - Signature summary: positional=self

  - Async: False, Returns: Dict

  - Cross-file communications: none

- Function `PerformanceMonitor.measure` (line 94)

  - Purpose: Context manager to measure operation duration

  - Signature summary: positional=self, operation

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `time.time` at line 108 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.time`

    - Calls `datetime.datetime.now` at line 103 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

- Function `PerformanceMonitor.print_summary` (line 153)

  - Purpose: Print performance summary

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `TokenCounter.__init__` (line 177)

  - Purpose: No docstring provided

  - Signature summary: positional=self, verbose_manager

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `TokenCounter.add_usage` (line 183)

  - Purpose: Record token usage from API response

  - Signature summary: positional=self, prompt_tokens, completion_tokens, cost

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `TokenCounter.clear` (line 219)

  - Purpose: Reset counters

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `TokenCounter.get_summary` (line 197)

  - Purpose: Get token usage summary

  - Signature summary: positional=self

  - Async: False, Returns: Dict

  - Cross-file communications: none

- Function `TokenCounter.print_summary` (line 207)

  - Purpose: Print token usage summary

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `VerbosityManager.__init__` (line 23)

  - Purpose: Args:

  - Signature summary: positional=self, level, app

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `VerbosityManager.debug` (line 65)

  - Purpose: Show in debug mode and above

  - Signature summary: positional=self, message

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `VerbosityManager.error` (line 53)

  - Purpose: Always show errors

  - Signature summary: positional=self, message

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `VerbosityManager.info` (line 57)

  - Purpose: Show in normal mode and above

  - Signature summary: positional=self, message

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `VerbosityManager.is_debug` (line 77)

  - Purpose: Check if debug mode is enabled

  - Signature summary: positional=self

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `VerbosityManager.is_trace` (line 81)

  - Purpose: Check if trace mode is enabled

  - Signature summary: positional=self

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `VerbosityManager.is_verbose` (line 73)

  - Purpose: Check if verbose mode is enabled

  - Signature summary: positional=self

  - Async: False, Returns: bool

  - Cross-file communications: none

- Function `VerbosityManager.log` (line 38)

  - Purpose: Log message if current verbosity allows

  - Signature summary: positional=self, message, level, end

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `VerbosityManager.set_level` (line 33)

  - Purpose: Change verbosity level

  - Signature summary: positional=self, level

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `VerbosityManager.trace` (line 69)

  - Purpose: Show only in trace mode

  - Signature summary: positional=self, message

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `VerbosityManager.verbose` (line 61)

  - Purpose: Show in verbose mode and above

  - Signature summary: positional=self, message

  - Async: False, Returns: None

  - Cross-file communications: none


## modules/worktree_integration.py

- Module: `modules.worktree_integration`

- Function `WorktreeManager.__init__` (line 31)

  - Purpose: No docstring provided

  - Signature summary: positional=self, repo_path

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `pathlib.Path` at line 32 (unresolved)

      - Purpose: No docstring provided

      - Expression: `Path`

    - Calls `os.getcwd` at line 32 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.getcwd`

- Function `WorktreeManager.create_worktree` (line 106)

  - Purpose: Create a new worktree.

  - Signature summary: positional=self, path, branch, new_branch

  - Async: False, Returns: Tuple[bool, str]

  - Cross-file communications:

    - Calls `subprocess.run` at line 135 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `WorktreeManager.create_worktree_for_venv` (line 343)

  - Purpose: Create a worktree specifically for a Docker venv.

  - Signature summary: positional=self, venv_name, base_branch

  - Async: False, Returns: Tuple[bool, str, str]

  - Cross-file communications: none

- Function `WorktreeManager.get_current_branch` (line 289)

  - Purpose: Get current branch name.

  - Signature summary: positional=self, worktree_path

  - Async: False, Returns: Optional[str]

  - Cross-file communications:

    - Calls `subprocess.run` at line 301 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `WorktreeManager.get_worktree_diff` (line 186)

  - Purpose: Get diff for a worktree.

  - Signature summary: positional=self, worktree_path, ref

  - Async: False, Returns: Tuple[bool, str]

  - Cross-file communications:

    - Calls `subprocess.run` at line 201 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `WorktreeManager.has_uncommitted_changes` (line 316)

  - Purpose: Check if worktree has uncommitted changes.

  - Signature summary: positional=self, worktree_path

  - Async: False, Returns: bool

  - Cross-file communications:

    - Calls `subprocess.run` at line 328 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `WorktreeManager.is_git_repo` (line 34)

  - Purpose: Check if current directory is a git repository.

  - Signature summary: positional=self

  - Async: False, Returns: bool

  - Cross-file communications:

    - Calls `subprocess.run` at line 37 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `WorktreeManager.list_worktrees` (line 46)

  - Purpose: List all worktrees in the repository.

  - Signature summary: positional=self

  - Async: False, Returns: List[Worktree]

  - Cross-file communications:

    - Calls `subprocess.run` at line 52 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `WorktreeManager.merge_venv_to_worktree` (line 216)

  - Purpose: Merge changes from Docker venv file to worktree file.

  - Signature summary: positional=self, venv_file_path, worktree_file_path, commit_message

  - Async: False, Returns: Tuple[bool, str, str]

  - Cross-file communications:

    - Calls `os.path.exists` at line 237 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.path.exists`

    - Calls `subprocess.run` at line 272 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

    - Calls `shutil.copy2` at line 257 (unresolved)

      - Purpose: No docstring provided

      - Expression: `shutil.copy2`

    - Calls `os.path.dirname` at line 261 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.path.dirname`

    - Calls `os.path.basename` at line 262 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.path.basename`

- Function `WorktreeManager.remove_worktree` (line 150)

  - Purpose: Remove a worktree.

  - Signature summary: positional=self, path, force

  - Async: False, Returns: Tuple[bool, str]

  - Cross-file communications:

    - Calls `subprocess.run` at line 171 (unresolved)

      - Purpose: No docstring provided

      - Expression: `subprocess.run`

- Function `merge_docker_venv_to_worktree` (line 376)

  - Purpose: High-level function to merge Docker venv file to worktree with diff.

  - Signature summary: positional=venv_manager, worktree_manager, venv_name, container_file, worktree_file, commit_message

  - Async: False, Returns: Tuple[bool, str, str]

  - Cross-file communications:

    - Calls `tempfile.TemporaryDirectory` at line 400 (unresolved)

      - Purpose: No docstring provided

      - Expression: `tempfile.TemporaryDirectory`

    - Calls `os.path.join` at line 401 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.path.join`

    - Calls `os.path.basename` at line 401 (unresolved)

      - Purpose: No docstring provided

      - Expression: `os.path.basename`


## opencli.py

- Module: `opencli`

- Functions: none

## run_with_profiler.py

- Module: `run_with_profiler`

- Functions: none

## thread_analyzer.py

- Module: `thread_analyzer`

- Function `ThreadAnalyzer.__init__` (line 39)

  - Purpose: No docstring provided

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ThreadAnalyzer._analyze_execution_health` (line 180)

  - Purpose: Analyze overall parallel execution health

  - Signature summary: positional=self, threads

  - Async: False, Returns: dict

  - Cross-file communications: none

- Function `ThreadAnalyzer._assess_blocking_severity` (line 60)

  - Purpose: Assess blocking severity and return (severity_level, severity_name, description)

  - Signature summary: positional=self, thread_info, thread_role

  - Async: False, Returns: tuple

  - Cross-file communications: none

- Function `ThreadAnalyzer._categorize_thread` (line 43)

  - Purpose: Categorize thread by role: LEAD, BACKGROUND, or USER

  - Signature summary: positional=self, thread_name

  - Async: False, Returns: str

  - Cross-file communications: none

- Function `ThreadAnalyzer._format_stack` (line 273)

  - Purpose: Format stack trace for display

  - Signature summary: positional=self, stack

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ThreadAnalyzer._identify_blocking_call` (line 249)

  - Purpose: Identify what the thread is blocked on

  - Signature summary: positional=self, frame, stack

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ThreadAnalyzer._is_thread_blocked` (line 226)

  - Purpose: Check if thread appears blocked

  - Signature summary: positional=self, frame, stack

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ThreadAnalyzer._print_thread` (line 358)

  - Purpose: Print individual thread with severity indicators

  - Signature summary: positional=self, t

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ThreadAnalyzer.capture_snapshot` (line 106)

  - Purpose: Capture current state of all threads

  - Signature summary: positional=self

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `datetime.datetime.now` at line 109 (unresolved)

      - Purpose: No docstring provided

      - Expression: `datetime.now`

    - Calls `sys._current_frames` at line 114 (unresolved)

      - Purpose: No docstring provided

      - Expression: `sys._current_frames`

    - Calls `threading.enumerate` at line 119 (unresolved)

      - Purpose: No docstring provided

      - Expression: `threading.enumerate`

    - Calls `traceback.extract_stack` at line 126 (unresolved)

      - Purpose: No docstring provided

      - Expression: `traceback.extract_stack`

    - Calls `asyncio.get_running_loop` at line 165 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.get_running_loop`

    - Calls `asyncio.all_tasks` at line 169 (unresolved)

      - Purpose: No docstring provided

      - Expression: `asyncio.all_tasks`

- Function `ThreadAnalyzer.compare_snapshots` (line 285)

  - Purpose: Compare two snapshots to find stuck threads

  - Signature summary: positional=self, snap1, snap2

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ThreadAnalyzer.monitor_continuous` (line 404)

  - Purpose: Monitor threads continuously

  - Signature summary: positional=self, interval, iterations

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `time.sleep` at line 424 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.sleep`

- Function `ThreadAnalyzer.print_snapshot` (line 311)

  - Purpose: Pretty print a snapshot with role categorization and severity ranking

  - Signature summary: positional=self, snapshot

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `ThreadAnalyzer.print_stuck_threads` (line 388)

  - Purpose: Print report of stuck threads

  - Signature summary: positional=self, stuck_threads

  - Async: False, Returns: None

  - Cross-file communications: none

- Function `monitor_in_app` (line 475)

  - Purpose: Import this function and call from within OpenCLI

  - Signature summary: positional=duration, interval

  - Async: False, Returns: None

  - Cross-file communications:

    - Calls `time.sleep` at line 501 (unresolved)

      - Purpose: No docstring provided

      - Expression: `time.sleep`

- Function `run_standalone` (line 429)

  - Purpose: Run as standalone monitoring tool

  - Signature summary: (no parameters)

  - Async: False, Returns: None

  - Cross-file communications: none

