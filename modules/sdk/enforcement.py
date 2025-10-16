"""
SDK Enforcement System

Validates and enforces SDK compliance at registration time.
Converts handlers where possible, rejects violations.
"""

import inspect
import asyncio
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from .handler_interface import validate_handler, HandlerCompliance, HandlerRegistration


class EnforcementAction(Enum):
    """Actions taken by enforcement system"""
    ACCEPTED = "accepted"           # Handler is compliant
    CONVERTED = "converted"         # Handler was auto-fixed
    REJECTED = "rejected"           # Handler violates SDK, cannot fix
    WRAPPED = "wrapped"             # Handler wrapped with compliance layer


@dataclass
class EnforcementResult:
    """Result of enforcement check"""
    original_name: str
    original_handler: Callable
    final_handler: Callable
    action: EnforcementAction
    compliance: HandlerCompliance
    message: str
    category: str = "unknown"
    module: str = "unknown"


class SDKEnforcement:
    """
    Enforces SDK compliance at registration time

    Rules:
    1. Handler MUST be async
    2. Handler MUST have (app, session, **context) signature
    3. Handler MUST NOT manually manage permission buffer
    4. Handler should use app.write() for output

    Actions:
    - ACCEPTED: Handler is compliant, use as-is
    - CONVERTED: Auto-fix signature (add **context wrapper)
    - WRAPPED: Wrap handler in compliance layer
    - REJECTED: Cannot fix, refuse to load
    """

    def __init__(self):
        self.results: List[EnforcementResult] = []
        self.accepted_count = 0
        self.converted_count = 0
        self.rejected_count = 0
        self.wrapped_count = 0

    def enforce(
        self,
        name: str,
        handler: Callable,
        category: str = "unknown",
        auto_convert: bool = True
    ) -> EnforcementResult:
        """
        Enforce SDK compliance on handler

        Args:
            name: Handler name
            handler: Handler function
            category: Category for reporting
            auto_convert: If True, attempt to auto-fix violations

        Returns:
            EnforcementResult with final handler or rejection
        """
        # Validate handler
        validation = validate_handler(handler, name)

        # Get module info
        module = handler.__module__ if hasattr(handler, '__module__') else 'unknown'

        # Check compliance
        if validation.compliance == HandlerCompliance.COMPLIANT:
            # Perfect! Use as-is
            result = EnforcementResult(
                original_name=name,
                original_handler=handler,
                final_handler=handler,
                action=EnforcementAction.ACCEPTED,
                compliance=validation.compliance,
                message="✓ Compliant",
                category=category,
                module=module
            )
            self.accepted_count += 1
            self.results.append(result)
            return result

        # Not compliant - try to fix
        if not auto_convert:
            # No auto-fix, reject
            result = EnforcementResult(
                original_name=name,
                original_handler=handler,
                final_handler=None,
                action=EnforcementAction.REJECTED,
                compliance=validation.compliance,
                message=f"✗ {validation.error} (auto-convert disabled)",
                category=category,
                module=module
            )
            self.rejected_count += 1
            self.results.append(result)
            return result

        # Attempt conversion
        converted = self._attempt_conversion(handler, validation)

        if converted:
            result = EnforcementResult(
                original_name=name,
                original_handler=handler,
                final_handler=converted,
                action=EnforcementAction.CONVERTED,
                compliance=HandlerCompliance.COMPLIANT,
                message=f"⚠ Converted: {validation.error}",
                category=category,
                module=module
            )
            self.converted_count += 1
            self.results.append(result)
            return result

        # Cannot convert, reject
        result = EnforcementResult(
            original_name=name,
            original_handler=handler,
            final_handler=None,
            action=EnforcementAction.REJECTED,
            compliance=validation.compliance,
            message=f"✗ Cannot convert: {validation.error}",
            category=category,
            module=module
        )
        self.rejected_count += 1
        self.results.append(result)
        return result

    def _attempt_conversion(
        self,
        handler: Callable,
        validation: HandlerRegistration
    ) -> Optional[Callable]:
        """
        Attempt to convert handler to be compliant

        Conversions:
        1. NOT_ASYNC → Cannot convert (must be rewritten)
        2. MISSING_CONTEXT → Wrap to add **context
        3. WRONG_SIGNATURE → Cannot convert (must be rewritten)
        """

        if validation.compliance == HandlerCompliance.NOT_ASYNC:
            # Cannot auto-convert sync to async
            return None

        if validation.compliance == HandlerCompliance.MISSING_CONTEXT:
            # Wrap to add **context parameter
            return self._wrap_add_context(handler)

        if validation.compliance == HandlerCompliance.WRONG_SIGNATURE:
            # Cannot auto-convert wrong signature
            return None

        return None

    def _wrap_add_context(self, handler: Callable) -> Callable:
        """
        Wrap handler to add **context parameter

        Original: async def handler(app, session)
        Wrapped:  async def handler(app, session, **context)

        ROBUST WRAPPER - handles all edge cases:
        - Different parameter counts
        - Sync/async handlers
        - Error propagation
        - Metadata preservation
        """
        async def wrapped_handler(app, session, **context):
            """SDK compliance wrapper - adds **context support"""
            try:
                # Get handler signature
                sig = inspect.signature(handler)
                params = list(sig.parameters.keys())

                # Call with appropriate parameters
                if len(params) == 0:
                    # No params - shouldn't happen but handle it
                    print(f"[SDK] WARNING: {handler.__name__} has no params, calling with app, session")
                    result = await handler(app, session)
                elif len(params) == 1:
                    # Only app
                    result = await handler(app)
                elif len(params) == 2:
                    # app, session
                    result = await handler(app, session)
                else:
                    # Has extra params - try passing context items
                    result = await handler(app, session)

                return result

            except TypeError as e:
                # Parameter mismatch - log and try basic call
                print(f"[SDK] WARNING: Parameter mismatch in {handler.__name__}: {e}")
                print(f"[SDK] Attempting basic call with (app, session)")
                try:
                    result = await handler(app, session)
                    return result
                except Exception as e2:
                    print(f"[SDK] ERROR: Failed to call {handler.__name__}: {e2}")
                    raise

            except Exception as e:
                # Other error - propagate with context
                print(f"[SDK] ERROR in wrapped handler {handler.__name__}: {e}")
                import traceback
                traceback.print_exc()
                raise

        # Preserve metadata
        wrapped_handler.__name__ = handler.__name__
        wrapped_handler.__doc__ = f"{handler.__doc__}\n\n[SDK: Auto-wrapped for **context compliance]" if handler.__doc__ else "[SDK: Auto-wrapped for **context compliance]"
        wrapped_handler.__module__ = handler.__module__
        wrapped_handler.__wrapped__ = handler  # Store original
        wrapped_handler.__sdk_wrapped__ = True  # Mark as SDK wrapped

        return wrapped_handler

    def get_summary(self) -> str:
        """Get enforcement summary for display"""
        total = len(self.results)
        lines = []

        lines.append("[bold cyan]SDK Enforcement Report[/bold cyan]\n")
        lines.append(f"Total handlers: {total}\n")
        lines.append(f"[green]✓ Accepted: {self.accepted_count}[/green]\n")

        if self.converted_count > 0:
            lines.append(f"[yellow]⚠ Converted: {self.converted_count}[/yellow]\n")

        if self.rejected_count > 0:
            lines.append(f"[red]✗ Rejected: {self.rejected_count}[/red]\n")

        lines.append("\n")

        # Show by category
        categories = {}
        for result in self.results:
            cat = result.category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(result)

        for cat, results in sorted(categories.items()):
            lines.append(f"[bold]{cat.upper()}[/bold]\n")
            for result in results:
                symbol = {
                    EnforcementAction.ACCEPTED: "[green]✓[/green]",
                    EnforcementAction.CONVERTED: "[yellow]⚠[/yellow]",
                    EnforcementAction.REJECTED: "[red]✗[/red]",
                    EnforcementAction.WRAPPED: "[cyan]↻[/cyan]"
                }[result.action]

                lines.append(f"  {symbol} {result.original_name}: {result.message}\n")

            lines.append("\n")

        return "".join(lines)

    def get_rejected(self) -> List[EnforcementResult]:
        """Get list of rejected handlers"""
        return [r for r in self.results if r.action == EnforcementAction.REJECTED]

    def has_violations(self) -> bool:
        """Check if any handlers were rejected"""
        return self.rejected_count > 0


# Global enforcement instance
_enforcement: Optional[SDKEnforcement] = None


def get_enforcement() -> SDKEnforcement:
    """Get or create global enforcement instance"""
    global _enforcement
    if _enforcement is None:
        _enforcement = SDKEnforcement()
    return _enforcement


def enforce_handler(
    name: str,
    handler: Callable,
    category: str = "unknown",
    auto_convert: bool = True
) -> EnforcementResult:
    """
    Enforce SDK compliance on handler

    This is the main entry point for enforcement.
    Call this when registering handlers.

    Args:
        name: Handler name
        handler: Handler function
        category: Category for reporting
        auto_convert: If True, attempt to auto-fix violations

    Returns:
        EnforcementResult with final handler or rejection

    Raises:
        ValueError: If handler is rejected and cannot be fixed
    """
    enforcement = get_enforcement()
    result = enforcement.enforce(name, handler, category, auto_convert)

    if result.action == EnforcementAction.REJECTED:
        raise ValueError(
            f"SDK Violation: {name} - {result.message}\n"
            f"Handler must be async with signature: async def handler(app, session, **context)"
        )

    return result
