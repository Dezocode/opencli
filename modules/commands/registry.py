"""
Central Registration - ONE place for ALL commands and tools

Everything registers here with PROPER categorization.
NO duplicates, NO legacy code.

Every registration includes:
- ExecutionType (COMMAND, TOOL, API)
- ExecutionCategory (DOCKER, MODEL, FILE, etc.)
- RiskLevel (SAFE, LOW, MEDIUM, HIGH, CRITICAL)
- requires_approval (bool)
- description (str)

SDK ENFORCEMENT:
All handlers validated at registration time.
Non-compliant handlers auto-converted or rejected.

STREAMLINED FLOW:
register_all(executor) → SDK Enforcement → ExecutionRegistry → PermissionManager → Buffer
"""

from ..execution.registry import ExecutionType, ExecutionCategory, RiskLevel
from ..sdk.enforcement import enforce_handler, EnforcementAction
from ..sdk.validation import validate_full_coverage


def _update_sdk_buffer(app, current_step: str = None, current_file: str = None, cmd_count: int = None, tool_count: int = None):
    """Helper to update SDK loading progress in command suggestions buffer - NON-BLOCKING"""
    try:
        if not app or not hasattr(app, 'query_one'):
            return  # Not a TUI app

        suggestions_buffer = app.query_one("#command-suggestions")

        # Update with whatever info we have
        suggestions_buffer.update_sdk_progress(
            current_step=current_step,
            current_file=current_file,
            command_count=cmd_count,
            tool_count=tool_count
        )
    except:
        pass  # Silently fail - don't block registration


async def register_all(executor):
    """
    ONE registration function for EVERYTHING

    Enforces SDK compliance, then registers with ExecutionSystem.
    ALL ASYNC - non-blocking registration.
    """
    import sys
    import time

    start_time = time.time()
    sys.stderr.write(f"\n[SDK.register_all] ========== STARTING REGISTRATION ==========\n")
    sys.stderr.write(f"[SDK.register_all] Start time: {time.strftime('%H:%M:%S')}\n")
    sys.stderr.write(f"[SDK.register_all] Executor: {executor}\n")
    sys.stderr.flush()

    # ========================================================================
    # COMMANDS
    # ========================================================================
    try:
        sys.stderr.write(f"[SDK.register_all] Registering commands...\n")
        sys.stderr.flush()
        cmd_start = time.time()

        from .command_registry import register_all_commands
        await register_all_commands(executor, _safe_register, _update_sdk_buffer)

        cmd_duration = time.time() - cmd_start
        cmd_count = len(executor.registry.commands)
        sys.stderr.write(f"[SDK.register_all] ✓ Commands registered: {cmd_count} (took {cmd_duration:.2f}s)\n")
        sys.stderr.flush()
    except Exception as e:
        sys.stderr.write(f"[SDK.register_all] ✗ FAILED during command registration: {type(e).__name__}: {e}\n")
        sys.stderr.flush()
        import traceback
        traceback.print_exc(file=sys.stderr)
        raise

    # ========================================================================
    # TOOLS
    # ========================================================================
    try:
        sys.stderr.write(f"[SDK.register_all] Registering tools...\n")
        sys.stderr.flush()
        tool_start = time.time()

        from .tool_registry import register_all_tools
        await register_all_tools(executor, _safe_register, _update_sdk_buffer)

        tool_duration = time.time() - tool_start
        tool_count = len(executor.registry.tools)
        sys.stderr.write(f"[SDK.register_all] ✓ Tools registered: {tool_count} (took {tool_duration:.2f}s)\n")
        sys.stderr.flush()
    except Exception as e:
        sys.stderr.write(f"[SDK.register_all] ✗ FAILED during tool registration: {type(e).__name__}: {e}\n")
        sys.stderr.flush()
        import traceback
        traceback.print_exc(file=sys.stderr)
        raise

    # ========================================================================
    # COVERAGE VALIDATION
    # ========================================================================
    try:
        sys.stderr.write(f"[SDK.register_all] Validating registration coverage...\n")
        sys.stderr.flush()
        validate_full_coverage(executor)
        sys.stderr.write(f"[SDK.register_all] ✓ Coverage validation passed\n")
        sys.stderr.flush()
    except Exception as e:
        sys.stderr.write(f"[SDK.register_all] ⚠ Coverage validation warning: {e}\n")
        sys.stderr.flush()
        # Don't raise - validation warnings shouldn't block startup

    total_duration = time.time() - start_time
    sys.stderr.write(f"[SDK.register_all] ========== REGISTRATION COMPLETE ==========\n")
    sys.stderr.write(f"[SDK.register_all] Total duration: {total_duration:.2f}s\n")
    sys.stderr.write(f"[SDK.register_all] Commands: {len(executor.registry.commands)} | Tools: {len(executor.registry.tools)}\n\n")
    sys.stderr.flush()


async def _safe_register(
    executor,
    exec_type: ExecutionType,
    name: str,
    handler,
    category: ExecutionCategory,
    risk_level: RiskLevel,
    requires_approval: bool,
    description: str,
    custom_prompt_func=None,
    **kwargs
):
    """
    SDK-enforced registration with LIVE buffer update

    Validates handler, auto-converts if needed, then registers.
    Raises ValueError if handler cannot be made compliant.

    Args:
        executor: UnifiedExecutionSystem instance
        exec_type: COMMAND, TOOL, or API
        name: Command/tool identifier (e.g., '/help')
        handler: Main execution function
        category: Organization category
        risk_level: Risk assessment level
        requires_approval: Whether to show permission prompt
        description: Human-readable description
        custom_prompt_func: Optional interactive prompt function (for SDK-compliant commands)
        **kwargs: Additional registration options (metadata, resources, etc.)
    """
    # Enforce SDK compliance
    cat_name = category.value if hasattr(category, 'value') else str(category)

    print(f"[SDK] Enforcing: {name}")
    result = enforce_handler(name, handler, cat_name, auto_convert=True)
    print(f"[SDK]   Action: {result.action.value}")
    print(f"[SDK]   Compliance: {result.compliance.value}")
    print(f"[SDK]   Message: {result.message}")

    # Use final handler (may be converted/wrapped)
    final_handler = result.final_handler

    # Add custom_prompt_func to metadata if provided
    if custom_prompt_func is not None:
        if 'metadata' not in kwargs:
            kwargs['metadata'] = {}
        kwargs['metadata']['custom_prompt_func'] = custom_prompt_func
        print(f"[SDK]   Custom prompt: {custom_prompt_func.__name__ if hasattr(custom_prompt_func, '__name__') else 'provided'}")

        import sys
        if name == '/help':
            sys.stderr.write(f"\n[_safe_register] Added custom_prompt_func for {name}\n")
            sys.stderr.write(f"[_safe_register] kwargs['metadata'] = {kwargs['metadata']}\n")
            sys.stderr.write(f"[_safe_register] custom_prompt_func = {custom_prompt_func}\n")
            sys.stderr.flush()

    # Register with executor (ACTUAL registration, not recursive!)
    executor.registry.register(
        exec_type,
        name,
        final_handler,
        category,
        risk_level,
        requires_approval,
        description,
        **kwargs
    )

    # Yield to event loop to keep UI responsive during registration
    import asyncio
    await asyncio.sleep(0)
