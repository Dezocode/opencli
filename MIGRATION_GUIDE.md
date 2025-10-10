# Migration Guide: Legacy to Unified Execution System

## Overview

This guide shows how to migrate ALL commands, tools, and APIs from the legacy separate systems to the unified execution system.

## Benefits of Migration

### Before (Legacy)
- **13+ separate `if user_input.startswith()` blocks** in async_interactive.py
- **Duplicate permission systems** (CommandRegistry + ToolPermissionManager + more)
- **Inconsistent flows** - some use permission buffer, some don't
- **No unified progress tracking**
- **Duplicate async handling**

### After (Unified)
- **Single registration point** - ExecutionRegistry
- **Single permission system** - UnifiedPermissionManager
- **Consistent flow** - ALL go through UnifiedExecutionSystem
- **Live progress** - workflow status in permission buffer
- **Circuit breaker + retry** - built-in for everything

## Migration Steps

### 1. Register Command/Tool in ExecutionRegistry

**Old way (CommandRegistry):**
```python
# In command_registry.py
self.available_commands = {
    '/model': {
        'description': 'View or change model',
        'category': 'basic',
        'default_enabled': True
    }
}
```

**New way (Unified):**
```python
# In commands/model_commands.py
from execution import get_execution_system, ExecutionType, ExecutionCategory, RiskLevel

def register_model_commands(execution_system):
    """Register all model-related commands"""

    execution_system.registry.register(
        type=ExecutionType.COMMAND,
        name='/model',
        handler=model_command_handler,
        category=ExecutionCategory.MODEL,
        risk_level=RiskLevel.SAFE,
        requires_approval=False,
        description='View or change model',
        subcommands={
            'list': 'List all available models',
            'providers': 'Browse models by provider',
            '<model-id>': 'Switch to specified model'
        }
    )
```

### 2. Create Command Handler

**Old way (Direct handling):**
```python
# In async_interactive.py
if user_input.startswith('/model'):
    # Show model list
    app.write("Available models:\n")
    for model in models:
        app.write(f"  {model}\n")
    return
```

**New way (Unified handler):**
```python
# In commands/model_commands.py
async def model_command_handler(app, session, **context):
    """
    Handle /model command through unified system

    This function is registered with ExecutionRegistry and will be called
    by UnifiedExecutionSystem with proper permission checking.
    """

    # Show model list (or whatever the command does)
    models = await get_available_models()

    # Write to main chat (command completed, not in permission flow)
    app.write("Available models:\n")
    for model in models:
        app.write(f"  {model}\n")
```

### 3. For Multi-Step Commands, Use ExecutionStep

**Old way (Manual async):**
```python
if user_input.startswith('/docker ollama setup'):
    # Step 1
    app.write("Checking Docker...\n")
    is_running = await check_docker()

    # Step 2
    app.write("Pulling image...\n")
    await pull_image()

    # Step 3
    app.write("Creating container...\n")
    await create_container()
```

**New way (Unified workflow):**
```python
# In commands/docker_commands.py
from execution import ExecutionStep, StepStatus

async def docker_ollama_setup_handler(app, session, cpu_limit, memory_limit, gpu_enabled):
    """Docker Ollama setup with unified workflow"""

    # Get execution system
    exec_system = get_execution_system(app, session)

    # Define steps
    steps = [
        ExecutionStep(
            id="check_docker",
            title="Check Docker daemon status",
            execute_func=check_docker_func,
            requires_permission=False,
            timeout=10
        ),
        ExecutionStep(
            id="pull_image",
            title="Pull Ollama Docker image (~2.7GB)",
            execute_func=pull_image_func,
            requires_permission=True,  # Permission gate!
            timeout=600
        ),
        ExecutionStep(
            id="create_container",
            title=f"Create Ollama container ({cpu_limit} CPUs, {memory_limit})",
            execute_func=lambda: create_container_func(cpu_limit, memory_limit, gpu_enabled),
            requires_permission=True,  # Permission gate!
            timeout=60
        ),
        ExecutionStep(
            id="verify",
            title="Verify container is running",
            execute_func=verify_container_func,
            requires_permission=False,
            timeout=10
        )
    ]

    # Execute through unified system
    # This handles:
    # - Permission checking
    # - Live progress in permission buffer
    # - Step-by-step indicators (⋯ → ✓)
    # - Permission gates at each step
    # - Error handling
    # - Circuit breaker
    # - Retry logic
    results = await exec_system.execute_command(
        name='/docker ollama setup',
        steps=steps
    )

    return results
```

### 4. Register in Router

**Old way (Manual routing):**
```python
# In async_interactive.py
if user_input.startswith('/model'):
    # Handle model command
    ...
elif user_input.startswith('/docker'):
    # Handle docker command
    ...
# 13+ more if blocks
```

**New way (Unified routing):**
```python
# In modules/on_mount.py or similar initialization
from execution import get_execution_system
from commands.model_commands import register_model_commands
from commands.docker_commands import register_docker_commands
# ... more imports

def initialize_execution_system(app, session):
    """Initialize unified execution system with all commands/tools"""

    exec_system = get_execution_system(app, session)

    # Register all commands
    register_model_commands(exec_system)
    register_docker_commands(exec_system)
    register_provider_commands(exec_system)
    register_dev_commands(exec_system)
    # ... register all others

    # Register all tools
    register_file_tools(exec_system)
    register_search_tools(exec_system)
    register_bash_tools(exec_system)
    # ... register all others

    return exec_system
```

### 5. Update Main Handler

**Old way (Multiple if blocks):**
```python
# In async_interactive.py
if user_input.startswith('/'):
    if user_input.startswith('/model'):
        ...
    elif user_input.startswith('/docker'):
        ...
    elif user_input.startswith('/provider'):
        ...
    # ... 10+ more elif blocks
```

**New way (Single unified router):**
```python
# In async_interactive.py
if user_input.startswith('/'):
    # Get execution system
    from execution import get_execution_system, ExecutionType

    exec_system = get_execution_system(app, session)

    # Try to find registered command
    command_name = user_input.strip()

    # Check if registered
    registration = exec_system.registry.get(ExecutionType.COMMAND, command_name)

    if registration:
        # Execute through unified system
        try:
            result = await exec_system.execute_command(
                name=command_name,
                app=app,
                session=session,
                user_input=user_input
            )
            return
        except PermissionError:
            app.write("[yellow]Permission denied[/yellow]\n")
            return
        except Exception as e:
            app.write(f"[red]Error: {e}[/red]\n")
            return

    # Fall through to legacy handling (if not yet migrated)
    if user_input.startswith('/some_legacy_command'):
        # OLD CODE - to be removed after migration
        ...
```

## Example: Full Docker Command Migration

### File: `modules/commands/docker_commands.py`

```python
"""
Docker Commands - Unified execution system integration

All Docker commands registered with ExecutionRegistry and executed
through UnifiedExecutionSystem with permission-first flow.
"""

from execution import (
    get_execution_system,
    ExecutionType,
    ExecutionCategory,
    ExecutionStep,
    RiskLevel
)


def register_docker_commands(exec_system):
    """Register all Docker commands"""

    # /docker ollama setup
    exec_system.registry.register(
        type=ExecutionType.COMMAND,
        name='/docker ollama setup',
        handler=docker_ollama_setup_handler,
        category=ExecutionCategory.DOCKER,
        risk_level=RiskLevel.HIGH,
        requires_approval=True,
        description='Set up Ollama in Docker container',
        estimated_duration='5-15 minutes',
        resources_needed=['docker', 'network', 'disk'],
        can_run_background=True
    )

    # /docker ollama start
    exec_system.registry.register(
        type=ExecutionType.COMMAND,
        name='/docker ollama start',
        handler=docker_ollama_start_handler,
        category=ExecutionCategory.DOCKER,
        risk_level=RiskLevel.MEDIUM,
        requires_approval=True,
        description='Start Ollama Docker container',
        estimated_duration='< 10 seconds'
    )

    # /docker ollama stop
    exec_system.registry.register(
        type=ExecutionType.COMMAND,
        name='/docker ollama stop',
        handler=docker_ollama_stop_handler,
        category=ExecutionCategory.DOCKER,
        risk_level=RiskLevel.LOW,
        requires_approval=True,
        description='Stop Ollama Docker container',
        estimated_duration='< 10 seconds'
    )


async def docker_ollama_setup_handler(app, session, cpu_limit, memory_limit, gpu_enabled):
    """Handler for /docker ollama setup"""

    # Import Docker utilities
    from modules.docker_manager import DockerManager
    from modules.docker_async_handler import DockerAsyncHandler

    docker_mgr = DockerManager()
    docker_async = DockerAsyncHandler(docker_mgr)

    # Get execution system
    exec_system = get_execution_system(app, session)

    # Define workflow steps
    steps = [
        ExecutionStep(
            id="check_docker",
            title="Check Docker daemon status",
            execute_func=docker_async.check_docker_running,
            requires_permission=False,
            timeout=10
        ),
        ExecutionStep(
            id="check_existing",
            title="Check for existing Ollama containers",
            execute_func=docker_async.get_ollama_container_status,
            requires_permission=False,
            timeout=10
        ),
        ExecutionStep(
            id="pull_image",
            title="Pull Ollama Docker image (~2.7GB)",
            execute_func=lambda: docker_async.pull_ollama_image(),
            requires_permission=True,  # Permission gate
            timeout=600,
            can_run_background=True
        ),
        ExecutionStep(
            id="create_container",
            title=f"Create Ollama container ({cpu_limit}, {memory_limit})",
            execute_func=lambda: docker_async.create_ollama_container(
                cpu_limit=cpu_limit,
                memory_limit=memory_limit,
                gpu_enabled=gpu_enabled
            ),
            requires_permission=True,  # Permission gate
            timeout=60
        ),
        ExecutionStep(
            id="verify",
            title="Verify container is running",
            execute_func=docker_async.verify_ollama_running,
            requires_permission=False,
            timeout=10
        )
    ]

    # Execute workflow
    # This automatically:
    # - Shows permission prompt
    # - Shows live progress in buffer
    # - Updates step indicators
    # - Handles permission gates
    # - Shows in statusline if background
    # - Handles errors with circuit breaker
    # - Retries if configured
    results = await exec_system.execute_command(
        name='/docker ollama setup',
        steps=steps
    )

    # Show completion message
    app.write("[green]✓ Docker Ollama setup complete![/green]\n")
    app.write("Ollama is now available at: http://localhost:11434\n")

    return results


async def docker_ollama_start_handler(app, session):
    """Handler for /docker ollama start"""
    # Similar implementation
    pass


async def docker_ollama_stop_handler(app, session):
    """Handler for /docker ollama stop"""
    # Similar implementation
    pass
```

## Tool Migration Example

### File: `modules/tools/file_tools.py`

```python
"""
File Tools - Read, Write, Edit

All file operations registered with ExecutionRegistry with proper
path risk assessment and permission checking.
"""

from execution import (
    get_execution_system,
    ExecutionType,
    ExecutionCategory,
    RiskLevel
)


def register_file_tools(exec_system):
    """Register all file tools"""

    # Read tool
    exec_system.registry.register(
        type=ExecutionType.TOOL,
        name='Read',
        handler=read_tool_handler,
        category=ExecutionCategory.FILE,
        risk_level=RiskLevel.SAFE,
        requires_approval=False,  # Safe operation
        description='Read file contents'
    )

    # Write tool
    exec_system.registry.register(
        type=ExecutionType.TOOL,
        name='Write',
        handler=write_tool_handler,
        category=ExecutionCategory.FILE,
        risk_level=RiskLevel.MEDIUM,
        requires_approval=True,  # Risky operation
        description='Write file contents'
    )

    # Edit tool
    exec_system.registry.register(
        type=ExecutionType.TOOL,
        name='Edit',
        handler=edit_tool_handler,
        category=ExecutionCategory.FILE,
        risk_level=RiskLevel.MEDIUM,
        requires_approval=True,  # Risky operation
        description='Edit file with search/replace'
    )


async def read_tool_handler(file_path: str, offset: int = 0, limit: int = None):
    """Handler for Read tool"""
    # Actual file reading logic
    with open(file_path, 'r') as f:
        if offset:
            for _ in range(offset):
                f.readline()

        if limit:
            lines = [f.readline() for _ in range(limit)]
        else:
            lines = f.readlines()

    return ''.join(lines)


async def write_tool_handler(file_path: str, content: str):
    """Handler for Write tool"""
    # Path risk will be automatically assessed by UnifiedPermissionManager
    with open(file_path, 'w') as f:
        f.write(content)

    return f"✓ Written to {file_path}"


async def edit_tool_handler(file_path: str, old_string: str, new_string: str, replace_all: bool = False):
    """Handler for Edit tool"""
    # Read current content
    with open(file_path, 'r') as f:
        content = f.read()

    # Replace
    if replace_all:
        new_content = content.replace(old_string, new_string)
    else:
        new_content = content.replace(old_string, new_string, 1)

    # Write back
    with open(file_path, 'w') as f:
        f.write(new_content)

    return f"✓ Edited {file_path}"
```

## Migration Checklist

### Per Command/Tool

- [ ] Create handler function in appropriate `commands/` or `tools/` module
- [ ] Register with `ExecutionRegistry` including risk level and permissions
- [ ] For multi-step commands, create `ExecutionStep` list
- [ ] Test permission flow works correctly
- [ ] Remove old handling code from `async_interactive.py`
- [ ] Update any documentation

### Commands to Migrate

- [ ] `/docker` (ollama setup/start/stop/status) - HIGH PRIORITY
- [ ] `/model` (list/providers/switch)
- [ ] `/local` (local model setup)
- [ ] `/provider` (add/remove/list)
- [ ] `/debug` (toggle debug mode)
- [ ] `/performance` (performance monitoring)
- [ ] `/reload` (module reload)
- [ ] `/refactor` (refactoring tools)
- [ ] `/autorefactor` (auto refactoring)
- [ ] `/restart` (restart session)
- [ ] `/upgrade` (upgrade OpenCLI)
- [ ] `/api` (API server control)
- [ ] `/inject` (code injection)

### Tools to Migrate

- [ ] `Read` (file reading)
- [ ] `Write` (file writing)
- [ ] `Edit` (file editing)
- [ ] `Grep` (content search)
- [ ] `Glob` (file search)
- [ ] `Bash` (shell execution)
- [ ] `GitHub` (GitHub API)
- [ ] `WebFetch` (web content)
- [ ] `WebSearch` (web search)

### APIs to Migrate

- [ ] OpenAI chat completion
- [ ] Anthropic messages
- [ ] Google Gemini
- [ ] Any other API calls

## Testing

After migration, test each command/tool:

```bash
# Start OpenCLI
opencli

# Test command
/docker ollama setup

# Expected:
# 1. Permission prompt shows in buffer
# 2. User approves
# 3. Resource selection shows in buffer
# 4. User selects resources
# 5. Workflow progress shows in buffer with live step indicators
# 6. Permission gates work for risky steps
# 7. Completion message shows
# 8. Buffer clears after 2s

# Test should be smooth with NO:
# - Buffer exits
# - Hangs or stalls
# - Missing progress updates
# - Broken permission gates
```

## Benefits After Migration

✅ **Single system** - no more duplicate code
✅ **Consistent behavior** - all commands/tools work the same
✅ **Permission-first** - all operations respect permission gates
✅ **Live progress** - user sees what's happening
✅ **Circuit breaker** - automatic failure protection
✅ **Retry logic** - automatic retry for transient failures
✅ **Usage tracking** - all operations tracked automatically
✅ **Easy maintenance** - one place to fix bugs
✅ **Easy extension** - clear pattern to add new commands/tools
