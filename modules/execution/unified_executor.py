"""
Unified Execution System - Single entry point for ALL execution

Consolidates:
- UnifiedCommandExecutor: step-based workflow
- CommandRouter: routing
- ToolRegistry: tool execution
- All permission-first flows

Result: ONE system for commands, tools, and APIs
"""

import asyncio
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from .registry import ExecutionRegistry, ExecutionType, ExecutionCategory, ExecutionRegistration
from .permission_manager import PermissionManager
from .async_runner import AsyncExecutionRunner
from .circuit_breaker import CircuitBreaker
from .retry_manager import RetryManager


class StepStatus(Enum):
    """Step execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ExecutionStep:
    """
    Single step in execution workflow

    Combines features from:
    - CommandStep: title, permission, execution
    - WorkflowStep: status tracking
    """
    id: str
    title: str
    execute_func: Callable
    requires_permission: bool = False
    description: str = ""
    timeout: int = 120
    can_run_background: bool = False
    args: tuple = ()
    kwargs: Dict[str, Any] = None
    status: StepStatus = StepStatus.PENDING
    result: Any = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.kwargs is None:
            self.kwargs = {}


class UnifiedExecutionSystem:
    """
    Single execution system for ALL commands, tools, and APIs

    Features:
    - Unified registration system
    - Permission-first execution
    - Step-based workflow
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
        self.permission_manager = PermissionManager()
        self.async_runner = AsyncExecutionRunner()
        self.circuit_breaker = CircuitBreaker()
        self.retry_manager = RetryManager()

        # Active executions
        self.active_executions: Dict[str, Dict[str, Any]] = {}

    # ========================================================================
    # MAIN EXECUTION ENTRY POINT
    # ========================================================================

    async def execute(
        self,
        type: ExecutionType,
        name: str,
        steps: Optional[List[ExecutionStep]] = None,
        **context
    ) -> Any:
        """
        Execute command/tool/API with unified flow

        Args:
            type: COMMAND, TOOL, or API
            name: Registered name
            steps: Execution steps (for commands with workflows)
            **context: Execution context (args, paths, etc.)

        Returns:
            Execution result

        Raises:
            PermissionError: If permission denied
            Exception: If execution fails
        """

        # Get registration
        registration = self.registry.get(type, name)
        if not registration:
            raise ValueError(f"Unknown {type.value}: {name}")

        # Check if enabled
        if not registration.enabled:
            raise PermissionError(f"{name} is disabled")

        # Check permission
        if registration.requires_approval:
            approved = await self.permission_manager.check_permission(
                registration,
                context,
                self.app,
                self.session
            )
            if not approved:
                raise PermissionError(f"Permission denied for {name}")

        # Record usage
        self.registry.record_usage(type, name)

        # Execute
        execution_id = f"{type.value}:{name}"

        try:
            # Execute with circuit breaker
            if steps:
                # Multi-step workflow
                result = await self.circuit_breaker.execute(
                    execution_id,
                    self._execute_workflow,
                    registration=registration,
                    steps=steps,
                    context=context
                )
            else:
                # Single execution
                result = await self.circuit_breaker.execute(
                    execution_id,
                    self._execute_single,
                    registration=registration,
                    context=context
                )

            return result

        except Exception as e:
            # Retry if enabled
            if registration.retry_on_failure:
                try:
                    if steps:
                        result = await self.retry_manager.retry(
                            self._execute_workflow,
                            registration=registration,
                            steps=steps,
                            context=context
                        )
                    else:
                        result = await self.retry_manager.retry(
                            self._execute_single,
                            registration=registration,
                            context=context
                        )
                    return result
                except Exception as retry_error:
                    raise retry_error
            raise e

    # ========================================================================
    # WORKFLOW EXECUTION
    # ========================================================================

    async def _execute_workflow(
        self,
        registration: ExecutionRegistration,
        steps: List[ExecutionStep],
        context: Dict[str, Any]
    ) -> List[Any]:
        """
        Execute multi-step workflow with live progress IN PERMISSION BUFFER

        CRITICAL FLOW:
        1. Show workflow in permission buffer (MultiLineInput widget)
        2. Execute steps with live updates IN BUFFER
        3. NO app.write() during execution (would exit buffer!)
        4. Complete and show final status
        5. Clear buffer after 2s
        6. NOW can write results to chat (buffer cleared)

        This keeps execution visible in buffer throughout, then returns
        to normal input after completion.
        """

        # Create workflow status
        workflow_status = {
            'steps': [
                {
                    'title': step.title,
                    'status': 'pending',
                    'id': step.id
                }
                for step in steps
            ],
            'current_step': 0,
            'total_steps': len(steps)
        }

        # Show initial workflow in permission buffer
        # This overlays the input widget - user sees workflow instead of input
        prompt_input = self.app.query_one("#prompt-input")
        prompt_data = {
            'title': f'{registration.category.value.title()}: {registration.name}',
            'message': 'Executing command steps...',
            'workflow_status': workflow_status,
            'options': [
                {
                    'text': 'Cancel execution',
                    'response': 'cancel'
                }
            ]
        }
        prompt_input.permission_prompt_data = prompt_data
        prompt_input.refresh(layout=True)

        # Execute each step
        results = []
        for i, step in enumerate(steps):
            # Check for cancellation
            if self.session._execution_cancelled:
                step.status = StepStatus.CANCELLED
                workflow_status['steps'][i]['status'] = 'cancelled'
                break

            # Update current step
            workflow_status['current_step'] = i
            workflow_status['steps'][i]['status'] = 'in_progress'
            step.status = StepStatus.IN_PROGRESS
            prompt_input.refresh()

            # Update statusline if background
            if step.can_run_background:
                self._update_statusline(step.title, '⋯', 'cyan')

            # Permission gate for this step?
            if step.requires_permission:
                approved = await self._wait_for_step_permission(step, workflow_status, prompt_input)
                if not approved:
                    step.status = StepStatus.CANCELLED
                    workflow_status['steps'][i]['status'] = 'cancelled'
                    raise PermissionError(f"Step '{step.title}' denied")

            # Execute step
            try:
                if asyncio.iscoroutinefunction(step.execute_func):
                    result = await self.async_runner.run_async(
                        step.execute_func,
                        timeout=step.timeout,
                        *step.args,
                        **step.kwargs
                    )
                else:
                    result = await self.async_runner.run_async(
                        step.execute_func,
                        timeout=step.timeout,
                        *step.args,
                        **step.kwargs
                    )

                # Success
                step.status = StepStatus.COMPLETED
                step.result = result
                workflow_status['steps'][i]['status'] = 'completed'
                results.append(result)

                # Update statusline
                if step.can_run_background:
                    self._update_statusline(step.title, '✓', 'green')

            except Exception as e:
                # Failure
                step.status = StepStatus.FAILED
                step.error = str(e)
                workflow_status['steps'][i]['status'] = 'failed'

                # Update statusline
                if step.can_run_background:
                    self._update_statusline(step.title, '✗', 'red')

                raise e

            finally:
                prompt_input.refresh()

        # Show completion in buffer for 2s
        await asyncio.sleep(2)

        # Clear permission buffer - returns to normal input
        prompt_input.permission_prompt_data = None
        prompt_input.refresh(layout=True)

        # NOW handler can write results to chat if needed
        # Buffer is cleared, won't interfere
        return results

    async def _wait_for_step_permission(
        self,
        step: ExecutionStep,
        workflow_status: Dict[str, Any],
        prompt_input
    ) -> bool:
        """Show permission prompt for individual step"""

        # Update prompt to show step permission
        step_prompt = {
            'title': f'Continue with {step.title}?',
            'message': step.description or f'Execute step: {step.title}',
            'workflow_status': workflow_status,
            'options': [
                {
                    'text': 'Yes, continue',
                    'response': 'allow'
                },
                {
                    'text': 'No, cancel workflow',
                    'response': 'cancel'
                }
            ]
        }

        prompt_input.permission_prompt_data = step_prompt
        prompt_input.refresh(layout=True)

        # Wait for approval
        self.session._awaiting_step_permission = True
        self.session._step_permission_response = None

        while self.session._awaiting_step_permission:
            await asyncio.sleep(0.1)

        # Check response
        response = getattr(self.session, '_step_permission_response', 'cancel')
        return response == 'allow'

    # ========================================================================
    # SINGLE EXECUTION
    # ========================================================================

    async def _execute_single(
        self,
        registration: ExecutionRegistration,
        context: Dict[str, Any]
    ) -> Any:
        """
        Execute single function (tool or simple command)

        For tools that need approval:
        1. Permission prompt shows IN BUFFER
        2. User approves
        3. Tool executes
        4. Result returned
        5. Handler can write to chat after

        For background tools:
        - Show status in togglable statusline (bottom)
        - Don't block buffer
        """

        # Show in statusline if background
        if registration.can_run_background:
            self._update_statusline(registration.name, '⋯', 'cyan')

        try:
            # Execute handler
            if asyncio.iscoroutinefunction(registration.handler):
                result = await self.async_runner.run_async(
                    registration.handler,
                    timeout=registration.timeout,
                    **context
                )
            else:
                result = await self.async_runner.run_async(
                    registration.handler,
                    timeout=registration.timeout,
                    **context
                )

            # Update statusline if background
            if registration.can_run_background:
                self._update_statusline(registration.name, '✓', 'green')
                await asyncio.sleep(2)
                self._clear_statusline(registration.name)

            return result

        except Exception as e:
            # Update statusline if background
            if registration.can_run_background:
                self._update_statusline(registration.name, '✗', 'red')
                await asyncio.sleep(2)
                self._clear_statusline(registration.name)
            raise

    # ========================================================================
    # STATUSLINE UPDATES
    # ========================================================================

    def _update_statusline(self, label: str, icon: str, color: str):
        """Update statusline indicator"""
        try:
            from modules.simple_tui import StatusLine
            status_line = self.app.query_one("StatusLine", StatusLine)
            status_line.show_indicator(label, icon, color)
        except Exception:
            pass

    def _clear_statusline(self, label: str):
        """Clear statusline indicator"""
        try:
            from modules.simple_tui import StatusLine
            status_line = self.app.query_one("StatusLine", StatusLine)
            status_line.hide_indicator(label)
        except Exception:
            pass

    # ========================================================================
    # CONVENIENCE METHODS
    # ========================================================================

    async def execute_command(
        self,
        name: str,
        steps: Optional[List[ExecutionStep]] = None,
        **context
    ) -> Any:
        """Execute command by name"""
        return await self.execute(ExecutionType.COMMAND, name, steps, **context)

    async def execute_tool(
        self,
        name: str,
        **context
    ) -> Any:
        """Execute tool by name"""
        return await self.execute(ExecutionType.TOOL, name, None, **context)

    async def execute_api(
        self,
        name: str,
        **context
    ) -> Any:
        """Execute API call by name"""
        return await self.execute(ExecutionType.API, name, None, **context)


# Global instance (initialized in OpenCLITUI.on_mount)
_unified_execution_system: Optional[UnifiedExecutionSystem] = None


def get_execution_system(app, session) -> UnifiedExecutionSystem:
    """Get or create global execution system"""
    global _unified_execution_system
    if _unified_execution_system is None:
        _unified_execution_system = UnifiedExecutionSystem(app, session)
    return _unified_execution_system
