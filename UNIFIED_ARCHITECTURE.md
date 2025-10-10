# OpenCLI Unified Permission-First Architecture

## Overview

**ONE unified system** for ALL commands, tools, and API operations with permission-first execution.

## Problem: Multiple Separate Systems

### Current State (BROKEN)
```
Commands:
  ├─ CommandRegistry (old) - enable/disable, search, usage
  ├─ CommandRouter (new) - routing
  └─ Legacy handlers in async_interactive.py (13+ separate if blocks)

Tools/Permissions:
  ├─ ToolPermissionManager (old) - risk levels, path detection
  ├─ ToolRegistry (new) - tool permissions
  └─ AsyncToolExecutor (separate) - async execution

Buffers:
  ├─ DualBufferSystem (old) - ToolBuffer + CommandBuffer
  └─ Permission buffer (new) - in MultiLineInput

Execution:
  ├─ UnifiedCommandExecutor (new) - command steps
  ├─ AsyncToolExecutor (separate) - tool execution
  ├─ ToolCircuitBreaker (separate)
  └─ APIRetryManager (separate)
```

**Result:** Duplicate code, inconsistent flows, bugs, complexity

### Unified State (FIXED)
```
UnifiedExecutionSystem
  ├─ Registration
  │   ├─ Commands (with metadata)
  │   ├─ Tools (with permissions)
  │   └─ APIs (with retry/circuit breaker)
  │
  ├─ Permission Manager
  │   ├─ Risk assessment (command + tool + path)
  │   ├─ Approval gates
  │   └─ Session/persistent modes
  │
  ├─ Execution Engine
  │   ├─ Step-based workflow
  │   ├─ Async/multithreaded
  │   ├─ Circuit breaker
  │   ├─ Retry logic
  │   └─ Timeout protection
  │
  ├─ Progress Buffer
  │   ├─ Permission prompts
  │   ├─ Live progress
  │   ├─ Step indicators
  │   └─ Background status
  │
  └─ Usage Tracking
      ├─ Command frequency
      ├─ Tool usage
      └─ API call metrics
```

**Result:** Single source of truth, consistent behavior, maintainable

## Architecture

### Module Structure

```
modules/
  ├─ execution/
  │   ├─ __init__.py
  │   ├─ unified_executor.py       # Core execution engine
  │   ├─ permission_manager.py     # Unified permission system
  │   ├─ registry.py               # Command/tool/API registration
  │   ├─ async_runner.py           # Async execution with timeouts
  │   ├─ circuit_breaker.py        # Failure protection
  │   └─ retry_manager.py          # Retry logic
  │
  ├─ commands/
  │   ├─ __init__.py
  │   ├─ docker_commands.py        # /docker ollama setup/start/stop
  │   ├─ model_commands.py         # /model, /local
  │   ├─ provider_commands.py      # /provider, /api
  │   ├─ dev_commands.py           # /debug, /performance, /reload
  │   ├─ refactor_commands.py      # /refactor, /autorefactor
  │   ├─ system_commands.py        # /restart, /upgrade
  │   └─ spec_commands.py          # /specify, /plan, /implement, etc.
  │
  ├─ tools/
  │   ├─ __init__.py
  │   ├─ file_tools.py             # Read, Write, Edit
  │   ├─ search_tools.py           # Grep, Glob
  │   ├─ bash_tools.py             # Bash execution
  │   ├─ github_tools.py           # GitHub API
  │   └─ web_tools.py              # WebFetch, WebSearch
  │
  ├─ ui/
  │   ├─ __init__.py
  │   ├─ simple_tui.py             # Main TUI app
  │   ├─ multiline_input.py        # Input with permission buffer
  │   ├─ command_suggestions.py    # Auto-suggest
  │   └─ streaming_display.py      # Output display
  │
  └─ legacy/ (TO BE REMOVED)
      ├─ command_registry.py       # OLD - will merge features
      ├─ tool_permissions.py       # OLD - will merge features
      ├─ dual_buffer_system.py     # OLD - will remove
      └─ stream_manager.py (parts) # OLD - will extract and merge
```

### Core Classes

#### 1. UnifiedExecutionSystem

**Purpose:** Single entry point for ALL commands, tools, and APIs

```python
class UnifiedExecutionSystem:
    """
    Unified execution system for commands, tools, and APIs

    Features:
    - Single registration system
    - Unified permission gates
    - Step-based workflow execution
    - Live progress in permission buffer
    - Background status in statusline
    - Circuit breaker + retry
    - Usage tracking
    """

    def __init__(self, app, session):
        self.app = app
        self.session = session

        # Components
        self.registry = ExecutionRegistry()
        self.permission_manager = UnifiedPermissionManager()
        self.async_runner = AsyncExecutionRunner()
        self.circuit_breaker = CircuitBreaker()
        self.retry_manager = RetryManager()

        # State
        self.active_executions = {}

    async def execute(
        self,
        type: ExecutionType,  # COMMAND, TOOL, or API
        name: str,
        steps: List[ExecutionStep],
        **kwargs
    ) -> Any:
        """Execute command/tool/API with unified flow"""

        # 1. Get registration info
        registration = self.registry.get(type, name)

        # 2. Check permission
        if registration.requires_approval:
            approved = await self.permission_manager.check_permission(
                registration, kwargs
            )
            if not approved:
                raise PermissionError()

        # 3. Execute steps with circuit breaker
        execution_id = self._create_execution_id(type, name)

        try:
            result = await self.circuit_breaker.execute(
                execution_id,
                self._execute_steps,
                steps=steps,
                **kwargs
            )
            return result

        except Exception as e:
            # Retry if applicable
            if registration.retry_on_failure:
                result = await self.retry_manager.retry(
                    self._execute_steps,
                    steps=steps,
                    **kwargs
                )
                return result
            raise

    async def _execute_steps(
        self,
        steps: List[ExecutionStep],
        **kwargs
    ) -> Any:
        """Execute workflow steps with live progress"""

        # Show in permission buffer
        workflow_status = {
            'steps': [{'title': s.title, 'status': 'pending'} for s in steps],
            'current_step': 0
        }

        prompt_input = self.app.query_one("#prompt-input")
        prompt_input.permission_prompt_data['workflow_status'] = workflow_status
        prompt_input.refresh()

        results = []
        for i, step in enumerate(steps):
            # Update current step
            workflow_status['current_step'] = i
            workflow_status['steps'][i]['status'] = 'in_progress'
            prompt_input.refresh()

            # Permission gate for this step?
            if step.requires_permission:
                approved = await self._wait_for_step_permission(step)
                if not approved:
                    raise PermissionError(f"Step {step.title} denied")

            # Execute
            if step.async_execution:
                result = await self.async_runner.run_async(
                    step.execute_func,
                    timeout=step.timeout,
                    *step.args,
                    **step.kwargs
                )
            else:
                result = await step.execute_func(*step.args, **step.kwargs)

            # Update status
            workflow_status['steps'][i]['status'] = 'completed'
            results.append(result)

            # Show in statusline if background
            if step.background:
                self._update_statusline(step.title, 'completed')

        return results
```

#### 2. ExecutionRegistry

**Purpose:** Single registry for ALL commands, tools, and APIs

```python
class ExecutionType(Enum):
    COMMAND = "command"
    TOOL = "tool"
    API = "api"

class ExecutionCategory(Enum):
    # Command categories
    DOCKER = "docker"
    MODEL = "model"
    PROVIDER = "provider"
    DEV = "dev"
    REFACTOR = "refactor"
    SYSTEM = "system"
    SPEC = "spec"

    # Tool categories
    FILE = "file"
    SEARCH = "search"
    BASH = "bash"
    NETWORK = "network"

    # API categories
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"

class ExecutionRegistration:
    """Registration info for command/tool/API"""
    type: ExecutionType
    name: str
    category: ExecutionCategory
    risk_level: RiskLevel
    requires_approval: bool
    retry_on_failure: bool
    timeout: int
    description: str
    handler: Callable
    metadata: Dict[str, Any]

class ExecutionRegistry:
    """Central registry for all executable items"""

    def __init__(self):
        self.commands: Dict[str, ExecutionRegistration] = {}
        self.tools: Dict[str, ExecutionRegistration] = {}
        self.apis: Dict[str, ExecutionRegistration] = {}

        # Legacy features from CommandRegistry
        self.usage_stats: Dict[str, int] = {}
        self.enabled: Dict[str, bool] = {}

        # Initialize with all commands/tools/APIs
        self._register_all()

    def register(
        self,
        type: ExecutionType,
        name: str,
        handler: Callable,
        **kwargs
    ):
        """Register command/tool/API"""
        registration = ExecutionRegistration(
            type=type,
            name=name,
            handler=handler,
            **kwargs
        )

        if type == ExecutionType.COMMAND:
            self.commands[name] = registration
        elif type == ExecutionType.TOOL:
            self.tools[name] = registration
        elif type == ExecutionType.API:
            self.apis[name] = registration

    def get(self, type: ExecutionType, name: str) -> ExecutionRegistration:
        """Get registration by type and name"""
        if type == ExecutionType.COMMAND:
            return self.commands.get(name)
        elif type == ExecutionType.TOOL:
            return self.tools.get(name)
        elif type == ExecutionType.API:
            return self.apis.get(name)

    def search_commands(self, query: str) -> List[ExecutionRegistration]:
        """Search commands (from CommandRegistry)"""
        # Implementation from old CommandRegistry.search_commands()
        pass

    def record_usage(self, type: ExecutionType, name: str):
        """Track usage (from CommandRegistry)"""
        key = f"{type.value}:{name}"
        self.usage_stats[key] = self.usage_stats.get(key, 0) + 1
```

#### 3. UnifiedPermissionManager

**Purpose:** Unified permission checking for all execution types

```python
class RiskLevel(Enum):
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class UnifiedPermissionManager:
    """
    Unified permission system

    Combines:
    - Command permissions (enable/disable)
    - Tool permissions (risk levels, path checking)
    - API permissions (rate limits, costs)
    """

    def __init__(self):
        self.config_dir = Path.home() / ".opencli"
        self.permissions_file = self.config_dir / "permissions.json"

        # Modes
        self.auto_accept = False
        self.accept_all_session = False

        # Load saved preferences
        self.permissions = self._load_permissions()

    async def check_permission(
        self,
        registration: ExecutionRegistration,
        context: Dict[str, Any]
    ) -> bool:
        """
        Check if execution should be permitted

        Args:
            registration: What's being executed
            context: Execution context (args, paths, etc.)

        Returns:
            True if approved, False if denied
        """

        # Quick checks
        if not registration.requires_approval:
            return True

        if self.auto_accept or self.accept_all_session:
            # Still check for critical risks
            risk = self._assess_total_risk(registration, context)
            if risk == RiskLevel.CRITICAL:
                # Always prompt for critical
                pass
            else:
                return True

        # Check if previously approved
        if self._is_permanently_approved(registration):
            return True

        # Assess total risk
        total_risk = self._assess_total_risk(registration, context)

        # Show permission prompt
        return await self._show_permission_prompt(
            registration,
            total_risk,
            context
        )

    def _assess_total_risk(
        self,
        registration: ExecutionRegistration,
        context: Dict[str, Any]
    ) -> RiskLevel:
        """
        Calculate total risk from multiple factors

        Combines:
        - Registration base risk
        - Path risk (for file operations)
        - API cost risk
        - System impact risk
        """

        risks = [registration.risk_level]

        # Path risk (from ToolPermissionManager)
        if 'file_path' in context:
            path_risk = self._assess_path_risk(context['file_path'])
            risks.append(path_risk)

        # API cost risk
        if registration.type == ExecutionType.API:
            cost_risk = self._assess_api_cost_risk(registration, context)
            risks.append(cost_risk)

        # Return highest risk
        return max(risks, key=lambda r: ['safe', 'low', 'medium', 'high', 'critical'].index(r.value))

    def _assess_path_risk(self, file_path: str) -> RiskLevel:
        """Path risk assessment (from ToolPermissionManager)"""
        # Implementation from old ToolPermissionManager.assess_path_risk()
        pass

    async def _show_permission_prompt(
        self,
        registration: ExecutionRegistration,
        risk: RiskLevel,
        context: Dict[str, Any]
    ) -> bool:
        """Show permission prompt in permission buffer"""
        # Implementation similar to current system
        pass
```

## Migration Plan

### Phase 1: Create Unified System ✅
1. Create `execution/` module structure
2. Implement `UnifiedExecutionSystem` class
3. Implement `ExecutionRegistry` class
4. Implement `UnifiedPermissionManager` class
5. Move async execution, circuit breaker, retry logic

### Phase 2: Migrate Commands 🔄
1. Move all command handlers to `commands/` modules
2. Register each command with `ExecutionRegistry`
3. Update `async_interactive.py` to use unified system
4. Remove legacy `if user_input.startswith()` blocks

### Phase 3: Migrate Tools 🔄
1. Move all tool logic to `tools/` modules
2. Register each tool with `ExecutionRegistry`
3. Update tool call sites to use unified system
4. Remove old `ToolPermissionManager` and `AsyncToolExecutor`

### Phase 4: Clean Up 🔄
1. Remove `legacy/` modules
2. Remove `dual_buffer_system.py`
3. Update imports throughout codebase
4. Test end-to-end

## Benefits

### Single Source of Truth
- One registry for everything
- One permission system
- One execution engine
- One buffer system

### Consistency
- All commands behave the same
- All tools behave the same
- All APIs behave the same
- Permission flow identical

### Maintainability
- Clear module organization
- Easy to add new commands/tools
- No duplicate code
- Easier to debug

### Features Preserved
- Command enable/disable (from CommandRegistry)
- Usage tracking (from CommandRegistry)
- Search/autocomplete (from CommandRegistry)
- Path risk detection (from ToolPermissionManager)
- Async execution (from AsyncToolExecutor)
- Circuit breaker (from ToolCircuitBreaker)
- Retry logic (from APIRetryManager)
- Live progress (from UnifiedCommandExecutor)
- Background status (from ToolRegistry)

### New Capabilities
- Commands can have retry logic
- Tools can show in statusline
- APIs can have permission gates
- All have usage tracking
- All have circuit breaker protection
