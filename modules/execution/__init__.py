"""
Unified Execution System - Single entry point for commands, tools, and APIs

Consolidates:
- CommandRegistry (search, usage tracking, enable/disable)
- CommandRouter (routing)
- ToolRegistry (tool permissions)
- ToolPermissionManager (path risk, approval)
- UnifiedCommandExecutor (step-based workflow)
- AsyncToolExecutor (async execution)
- Circuit breaker and retry logic

Result: ONE system for EVERYTHING
"""

from .registry import ExecutionRegistry, ExecutionType, ExecutionCategory, ExecutionRegistration
from .permission_manager import PermissionManager, RiskLevel
from .executor import ExecutionSystem
from .async_runner import AsyncExecutionRunner
from .circuit_breaker import CircuitBreaker
from .retry_manager import RetryManager

__all__ = [
    'ExecutionRegistry',
    'ExecutionType',
    'ExecutionCategory',
    'ExecutionRegistration',
    'PermissionManager',
    'RiskLevel',
    'ExecutionSystem',
    'AsyncExecutionRunner',
    'CircuitBreaker',
    'RetryManager',
]
