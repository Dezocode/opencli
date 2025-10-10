"""
OpenCLI Handler SDK - MANDATORY Interface

ALL handlers (commands, tools, opentools) MUST comply with this interface.
"""

from typing import Any, Dict, Protocol, runtime_checkable
from dataclasses import dataclass
from enum import Enum


class HandlerCompliance(Enum):
    """SDK compliance status"""
    COMPLIANT = "compliant"
    MISSING_CONTEXT = "missing_context"
    WRONG_SIGNATURE = "wrong_signature"
    NOT_ASYNC = "not_async"
    INVALID = "invalid"


@runtime_checkable
class SDKCompliantHandler(Protocol):
    """
    MANDATORY interface for ALL handlers

    Registration requires:
    1. async def handler(app, session, **context) signature
    2. Returns Any (result or None)
    3. Does NOT manage permission buffer manually
    4. Writes output to app.write() for chat

    ExecutionSystem will:
    - Call PermissionManager BEFORE handler
    - Show permission buffer if required
    - Call handler with context after approval
    - Handler just does work
    """

    async def __call__(
        self,
        app: Any,
        session: Any,
        **context: Dict[str, Any]
    ) -> Any:
        """
        MANDATORY signature

        Args:
            app: TUI application instance (has .write() method)
            session: Session instance (has state)
            **context: Execution context from ExecutionSystem
                - May include: args, paths, options, etc.

        Returns:
            Any: Result value (or None)

        RULES:
        - DO NOT touch prompt_input.permission_prompt_data
        - DO NOT manually call ExecutionSystem
        - DO write results with app.write()
        - DO return result value
        """
        ...


@dataclass
class HandlerRegistration:
    """
    SDK registration data

    Used for startup diagnostics and validation
    """
    name: str
    handler: Any
    module: str
    compliance: HandlerCompliance
    error: str = ""

    def is_compliant(self) -> bool:
        """Check if handler is SDK compliant"""
        return self.compliance == HandlerCompliance.COMPLIANT


def validate_handler(handler: Any, name: str) -> HandlerRegistration:
    """
    Validate handler against SDK interface

    Returns HandlerRegistration with compliance status
    """
    import inspect
    import asyncio

    module = handler.__module__ if hasattr(handler, '__module__') else 'unknown'

    # Check if async
    if not asyncio.iscoroutinefunction(handler):
        return HandlerRegistration(
            name=name,
            handler=handler,
            module=module,
            compliance=HandlerCompliance.NOT_ASYNC,
            error="Handler must be async function"
        )

    # Check signature
    sig = inspect.signature(handler)
    params = list(sig.parameters.keys())

    if len(params) < 2:
        return HandlerRegistration(
            name=name,
            handler=handler,
            module=module,
            compliance=HandlerCompliance.WRONG_SIGNATURE,
            error=f"Expected (app, session, **context), got {params}"
        )

    if params[0] != 'app' or params[1] != 'session':
        return HandlerRegistration(
            name=name,
            handler=handler,
            module=module,
            compliance=HandlerCompliance.WRONG_SIGNATURE,
            error=f"First params must be 'app', 'session', got {params[:2]}"
        )

    # Check for **context
    has_var_keyword = any(
        p.kind == inspect.Parameter.VAR_KEYWORD
        for p in sig.parameters.values()
    )

    if not has_var_keyword:
        return HandlerRegistration(
            name=name,
            handler=handler,
            module=module,
            compliance=HandlerCompliance.MISSING_CONTEXT,
            error="Missing **context parameter"
        )

    # Compliant!
    return HandlerRegistration(
        name=name,
        handler=handler,
        module=module,
        compliance=HandlerCompliance.COMPLIANT
    )
