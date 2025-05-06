"""
Circuit breaker pattern implementation for PR-Agent.

This module provides a circuit breaker implementation to prevent repeated calls to
failing services and improve system resilience.
"""

import asyncio
import functools
import time
from enum import Enum
from typing import Any, Callable, Dict, Optional, TypeVar, cast

from pr_agent.log import get_logger

logger = get_logger()

T = TypeVar("T")
AsyncCallable = Callable[..., Any]


class CircuitState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation, requests pass through
    OPEN = "open"          # Circuit is open, requests fail fast
    HALF_OPEN = "half_open"  # Testing if service is back online


class CircuitOpenError(Exception):
    """Exception raised when a circuit is open."""
    
    def __init__(self, circuit_name: str):
        self.circuit_name = circuit_name
        super().__init__(f"Circuit '{circuit_name}' is open")


class CircuitBreaker:
    """
    Implements the circuit breaker pattern to prevent repeated calls to failing services.
    
    The circuit breaker monitors for failures in the service. Once the failures reach
    a certain threshold, the circuit breaker trips and all further calls to the service
    will fail immediately without actually making the external call (failing fast).
    
    After a timeout period, the circuit breaker allows a trial call to see if the service
    is back online. If the call succeeds, the circuit is closed and calls flow through
    normally. If the call fails, the circuit remains open for another timeout period.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        name: str = "default",
        excluded_exceptions: Optional[list] = None,
    ):
        """
        Initialize a circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening the circuit
            recovery_timeout: Seconds to wait before trying to recover (half-open state)
            name: Name of this circuit breaker for logging
            excluded_exceptions: List of exception types that should not count as failures
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name
        self.excluded_exceptions = excluded_exceptions or []
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        self._lock = asyncio.Lock()
        
    def __call__(self, func: AsyncCallable) -> AsyncCallable:
        """Decorator to wrap a function with circuit breaker logic."""
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await self.call(func, *args, **kwargs)
        return cast(AsyncCallable, wrapper)
        
    async def call(self, func: AsyncCallable, *args: Any, **kwargs: Any) -> Any:
        """
        Call the protected function with circuit breaker logic.
        
        Args:
            func: The function to call
            *args, **kwargs: Arguments to pass to the function
            
        Returns:
            The result of the function call
            
        Raises:
            CircuitOpenError: If the circuit is open
            Exception: If the function call fails
        """
        async with self._lock:
            if self.state == CircuitState.OPEN:
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    # Try to recover
                    logger.info(f"Circuit '{self.name}' trying to recover (half-open)")
                    self.state = CircuitState.HALF_OPEN
                else:
                    # Circuit is open, fail fast
                    logger.warning(f"Circuit '{self.name}' is open, failing fast")
                    raise CircuitOpenError(self.name)
                
        try:
            result = await func(*args, **kwargs)
            
            # If we were in half-open state and the call succeeded, close the circuit
            if self.state == CircuitState.HALF_OPEN:
                async with self._lock:
                    logger.info(f"Circuit '{self.name}' recovered, closing")
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                
            return result
            
        except Exception as e:
            # Check if this exception should be excluded from circuit breaker logic
            if any(isinstance(e, exc_type) for exc_type in self.excluded_exceptions):
                # Re-raise but don't count as a circuit failure
                raise
                
            # Record the failure
            async with self._lock:
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                # If we've reached the threshold, open the circuit
                if self.state == CircuitState.CLOSED and self.failure_count >= self.failure_threshold:
                    logger.warning(f"Circuit '{self.name}' opened after {self.failure_count} failures")
                    self.state = CircuitState.OPEN
                    
                # If we were testing in half-open state, go back to open
                if self.state == CircuitState.HALF_OPEN:
                    logger.warning(f"Circuit '{self.name}' reopened after failed recovery attempt")
                    self.state = CircuitState.OPEN
                
            # Re-raise the original exception
            raise


# Global registry of circuit breakers
_circuit_breakers: Dict[str, CircuitBreaker] = {}


def get_circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: int = 30,
    excluded_exceptions: Optional[list] = None,
) -> CircuitBreaker:
    """
    Get or create a circuit breaker with the given name.
    
    This function ensures that only one circuit breaker exists with a given name,
    allowing different parts of the code to share the same circuit breaker state.
    
    Args:
        name: Name of the circuit breaker
        failure_threshold: Number of failures before opening the circuit
        recovery_timeout: Seconds to wait before trying to recover
        excluded_exceptions: List of exception types that should not count as failures
        
    Returns:
        A CircuitBreaker instance
    """
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            name=name,
            excluded_exceptions=excluded_exceptions,
        )
    return _circuit_breakers[name]


def circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: int = 30,
    excluded_exceptions: Optional[list] = None,
) -> Callable[[AsyncCallable], AsyncCallable]:
    """
    Decorator to apply a circuit breaker to a function.
    
    This is a convenience function that creates or retrieves a circuit breaker
    and applies it to the decorated function.
    
    Args:
        name: Name of the circuit breaker
        failure_threshold: Number of failures before opening the circuit
        recovery_timeout: Seconds to wait before trying to recover
        excluded_exceptions: List of exception types that should not count as failures
        
    Returns:
        A decorator function that applies the circuit breaker
    """
    breaker = get_circuit_breaker(
        name=name,
        failure_threshold=failure_threshold,
        recovery_timeout=recovery_timeout,
        excluded_exceptions=excluded_exceptions,
    )
    
    def decorator(func: AsyncCallable) -> AsyncCallable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await breaker.call(func, *args, **kwargs)
        return cast(AsyncCallable, wrapper)
        
    return decorator

