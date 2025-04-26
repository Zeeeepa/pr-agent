"""
Enhanced logging module for PR-Agent.

This module provides advanced logging capabilities:
- Structured logging with JSON format
- Correlation IDs for request tracking
- Performance metrics
- Log levels and filtering
"""

import json
import time
import uuid
import inspect
import functools
from typing import Any, Callable, Dict, Optional, TypeVar, cast

from pr_agent.log import get_logger

logger = get_logger()

# Type variable for function return type
T = TypeVar('T')


class RequestContext:
    """Context manager for tracking request-specific data."""
    
    _context = {}
    
    @classmethod
    def get_correlation_id(cls) -> str:
        """Get the current correlation ID or generate a new one."""
        if 'correlation_id' not in cls._context:
            cls._context['correlation_id'] = str(uuid.uuid4())
        return cls._context['correlation_id']
    
    @classmethod
    def set_correlation_id(cls, correlation_id: str) -> None:
        """Set the correlation ID for the current context."""
        cls._context['correlation_id'] = correlation_id
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Get a value from the context."""
        return cls._context.get(key, default)
    
    @classmethod
    def set(cls, key: str, value: Any) -> None:
        """Set a value in the context."""
        cls._context[key] = value
    
    @classmethod
    def clear(cls) -> None:
        """Clear the current context."""
        cls._context.clear()


def with_correlation_id(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to ensure a correlation ID is set for the function call.
    
    Args:
        func: The function to decorate
        
    Returns:
        Decorated function with correlation ID handling
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        # Generate a correlation ID if not already set
        correlation_id = RequestContext.get_correlation_id()
        
        # Log the function call with correlation ID
        logger.info(
            f"Function call",
            extra={
                "correlation_id": correlation_id,
                "function": func.__name__,
                "module": func.__module__,
            }
        )
        
        try:
            return func(*args, **kwargs)
        finally:
            # Log completion
            logger.info(
                f"Function completed",
                extra={
                    "correlation_id": correlation_id,
                    "function": func.__name__,
                    "module": func.__module__,
                }
            )
    
    return cast(Callable[..., T], wrapper)


def log_performance(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to log function performance metrics.
    
    Args:
        func: The function to decorate
        
    Returns:
        Decorated function with performance logging
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        correlation_id = RequestContext.get_correlation_id()
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            success = True
            return result
        except Exception as e:
            success = False
            error_type = type(e).__name__
            error_message = str(e)
            raise
        finally:
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            
            # Get caller information
            frame = inspect.currentframe()
            if frame:
                caller_frame = frame.f_back
                if caller_frame:
                    caller_info = {
                        "file": caller_frame.f_code.co_filename,
                        "line": caller_frame.f_lineno,
                        "function": caller_frame.f_code.co_name,
                    }
                else:
                    caller_info = {"file": "unknown", "line": 0, "function": "unknown"}
            else:
                caller_info = {"file": "unknown", "line": 0, "function": "unknown"}
            
            # Log performance data
            log_data = {
                "correlation_id": correlation_id,
                "function": func.__name__,
                "module": func.__module__,
                "duration_ms": duration_ms,
                "success": success,
                "caller": caller_info,
            }
            
            if not success:
                log_data["error_type"] = error_type
                log_data["error_message"] = error_message
            
            if duration_ms > 1000:  # Log as warning if execution takes more than 1 second
                logger.warning(f"Slow function execution: {func.__name__}", extra=log_data)
            else:
                logger.info(f"Function performance: {func.__name__}", extra=log_data)
    
    return cast(Callable[..., T], wrapper)


def log_method_calls(cls: Any) -> Any:
    """
    Class decorator to log all method calls.
    
    Args:
        cls: The class to decorate
        
    Returns:
        Decorated class with method call logging
    """
    for name, method in inspect.getmembers(cls, inspect.isfunction):
        # Skip private methods and special methods
        if not name.startswith('_'):
            setattr(cls, name, with_correlation_id(log_performance(method)))
    return cls


def structured_log(
    message: str,
    level: str = "info",
    correlation_id: Optional[str] = None,
    **kwargs: Any
) -> None:
    """
    Log a structured message with consistent format.
    
    Args:
        message: The log message
        level: Log level (debug, info, warning, error, critical)
        correlation_id: Optional correlation ID (uses current context if None)
        **kwargs: Additional fields to include in the log
    """
    if correlation_id is None:
        correlation_id = RequestContext.get_correlation_id()
    
    log_data = {
        "message": message,
        "correlation_id": correlation_id,
        "timestamp": time.time(),
        **kwargs
    }
    
    log_method = getattr(logger, level.lower())
    log_method(message, extra=log_data)


class PerformanceTracker:
    """Utility for tracking performance of code blocks."""
    
    def __init__(self, operation_name: str):
        """
        Initialize the performance tracker.
        
        Args:
            operation_name: Name of the operation being tracked
        """
        self.operation_name = operation_name
        self.start_time = None
        self.correlation_id = RequestContext.get_correlation_id()
    
    def __enter__(self) -> 'PerformanceTracker':
        """Start tracking performance."""
        self.start_time = time.time()
        logger.debug(
            f"Starting operation: {self.operation_name}",
            extra={
                "correlation_id": self.correlation_id,
                "operation": self.operation_name,
            }
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Stop tracking and log performance."""
        if self.start_time is None:
            return
        
        duration_ms = (time.time() - self.start_time) * 1000
        
        log_data = {
            "correlation_id": self.correlation_id,
            "operation": self.operation_name,
            "duration_ms": duration_ms,
            "success": exc_type is None,
        }
        
        if exc_type is not None:
            log_data["error_type"] = exc_type.__name__
            log_data["error_message"] = str(exc_val) if exc_val else ""
            
            logger.error(
                f"Operation failed: {self.operation_name} ({duration_ms:.2f}ms)",
                extra=log_data
            )
        else:
            if duration_ms > 1000:  # Log as warning if execution takes more than 1 second
                logger.warning(
                    f"Slow operation: {self.operation_name} ({duration_ms:.2f}ms)",
                    extra=log_data
                )
            else:
                logger.info(
                    f"Operation completed: {self.operation_name} ({duration_ms:.2f}ms)",
                    extra=log_data
                )
