"""
Circuit Breaker - Prevent cascading failures in execution

Consolidates ToolCircuitBreaker from stream_manager.py
"""

import time
from typing import Dict, Callable, Any
from enum import Enum


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"       # Normal operation
    OPEN = "open"           # Failing, reject requests
    HALF_OPEN = "half_open" # Testing if recovered


class CircuitBreaker:
    """
    Prevent cascading failures in command/tool/API execution

    Pattern:
    - CLOSED: Allow all requests
    - OPEN: Reject all requests (after threshold failures)
    - HALF_OPEN: Allow one test request after timeout
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        success_threshold: int = 2
    ):
        """
        Args:
            failure_threshold: Failures before opening circuit
            timeout: Seconds to wait before trying again
            success_threshold: Successes needed to close circuit
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold

        # State per execution ID
        self.circuits: Dict[str, Dict[str, Any]] = {}

    async def execute(
        self,
        execution_id: str,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute function with circuit breaker protection

        Args:
            execution_id: Unique ID for this execution type
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            Exception: If circuit is open or execution fails
        """
        # Initialize circuit if new
        if execution_id not in self.circuits:
            self.circuits[execution_id] = {
                'state': CircuitState.CLOSED,
                'failures': 0,
                'successes': 0,
                'last_failure_time': None
            }

        circuit = self.circuits[execution_id]

        # Check circuit state
        if circuit['state'] == CircuitState.OPEN:
            # Check if timeout expired
            if circuit['last_failure_time']:
                elapsed = time.time() - circuit['last_failure_time']
                if elapsed >= self.timeout:
                    # Try half-open
                    circuit['state'] = CircuitState.HALF_OPEN
                else:
                    raise Exception(
                        f"Circuit breaker OPEN for {execution_id}. "
                        f"Retry in {self.timeout - elapsed:.0f}s"
                    )

        # Execute
        try:
            result = await func(*args, **kwargs)

            # Success
            circuit['failures'] = 0
            if circuit['state'] == CircuitState.HALF_OPEN:
                circuit['successes'] += 1
                if circuit['successes'] >= self.success_threshold:
                    circuit['state'] = CircuitState.CLOSED
                    circuit['successes'] = 0

            return result

        except Exception as e:
            # Failure
            circuit['failures'] += 1
            circuit['last_failure_time'] = time.time()

            if circuit['failures'] >= self.failure_threshold:
                circuit['state'] = CircuitState.OPEN
                circuit['successes'] = 0

            raise e

    def get_state(self, execution_id: str) -> CircuitState:
        """Get current circuit state"""
        if execution_id not in self.circuits:
            return CircuitState.CLOSED
        return self.circuits[execution_id]['state']

    def reset(self, execution_id: str):
        """Reset circuit to closed state"""
        if execution_id in self.circuits:
            self.circuits[execution_id] = {
                'state': CircuitState.CLOSED,
                'failures': 0,
                'successes': 0,
                'last_failure_time': None
            }
