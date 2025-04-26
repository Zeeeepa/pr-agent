"""
Error handling module for PR-Agent.

This module provides a comprehensive error handling system with:
- Custom exception hierarchy
- Error classification
- Retry mechanisms with exponential backoff
- Structured error logging
"""

import time
import random
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union, cast

from pr_agent.log import get_logger

logger = get_logger()

# Type variable for function return type
T = TypeVar('T')


class PRAgentError(Exception):
    """Base exception class for all PR-Agent errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, 
                 details: Optional[Dict[str, Any]] = None):
        """
        Initialize the exception.
        
        Args:
            message: Human-readable error message
            status_code: Optional HTTP status code for API errors
            details: Optional dictionary with additional error details
        """
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class ConfigurationError(PRAgentError):
    """Raised when there's an issue with configuration settings."""
    pass


class AuthenticationError(PRAgentError):
    """Raised when authentication fails."""
    pass


class GitProviderError(PRAgentError):
    """Base class for Git provider related errors."""
    pass


class GitHubError(GitProviderError):
    """Raised when GitHub API operations fail."""
    pass


class GitLabError(GitProviderError):
    """Raised when GitLab API operations fail."""
    pass


class BitbucketError(GitProviderError):
    """Raised when Bitbucket API operations fail."""
    pass


class AzureDevOpsError(GitProviderError):
    """Raised when Azure DevOps API operations fail."""
    pass


class RateLimitError(PRAgentError):
    """Raised when a rate limit is hit."""
    
    def __init__(self, message: str, retry_after: Optional[int] = None, **kwargs):
        """
        Initialize the rate limit error.
        
        Args:
            message: Human-readable error message
            retry_after: Seconds to wait before retrying
            **kwargs: Additional keyword arguments
        """
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class AIProviderError(PRAgentError):
    """Raised when AI provider operations fail."""
    pass


class NetworkError(PRAgentError):
    """Raised when network operations fail."""
    pass


class TimeoutError(PRAgentError):
    """Raised when an operation times out."""
    pass


class ValidationError(PRAgentError):
    """Raised when input validation fails."""
    pass


class ResourceNotFoundError(PRAgentError):
    """Raised when a requested resource is not found."""
    pass


class PermissionError(PRAgentError):
    """Raised when an operation lacks required permissions."""
    pass


def with_retry(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    exceptions_to_retry: List[Type[Exception]] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Factor by which the delay increases
        exceptions_to_retry: List of exception types to retry on
        
    Returns:
        Decorated function with retry logic
    """
    if exceptions_to_retry is None:
        exceptions_to_retry = [
            NetworkError,
            TimeoutError,
            RateLimitError,
            GitProviderError,
        ]
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except tuple(exceptions_to_retry) as e:
                    last_exception = e
                    
                    # Don't retry on the last attempt
                    if attempt == max_retries:
                        break
                    
                    # Special handling for rate limit errors
                    if isinstance(e, RateLimitError) and e.retry_after:
                        retry_delay = e.retry_after
                    else:
                        # Add jitter to avoid thundering herd
                        jitter = random.uniform(0, 0.1 * delay)
                        retry_delay = min(delay + jitter, max_delay)
                        delay *= backoff_factor
                    
                    logger.warning(
                        f"Retrying {func.__name__} in {retry_delay:.2f}s after error: {str(e)}. "
                        f"Attempt {attempt + 1}/{max_retries + 1}"
                    )
                    
                    time.sleep(retry_delay)
            
            # If we get here, all retries failed
            if last_exception:
                logger.error(
                    f"All {max_retries} retries failed for {func.__name__}: {str(last_exception)}"
                )
                raise last_exception
            
            # This should never happen, but just in case
            raise RuntimeError(f"Unexpected error in retry logic for {func.__name__}")
        
        return cast(Callable[..., T], wrapper)
    
    return decorator


def handle_exceptions(
    default_message: str = "An unexpected error occurred",
    log_traceback: bool = True,
    reraise: bool = True,
    fallback_value: Any = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator for handling exceptions in a consistent way.
    
    Args:
        default_message: Default error message if exception doesn't have one
        log_traceback: Whether to log the full traceback
        reraise: Whether to reraise the exception after handling
        fallback_value: Value to return if reraise is False
        
    Returns:
        Decorated function with exception handling
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Get error details
                error_type = type(e).__name__
                error_message = str(e) or default_message
                
                # Log the error
                if log_traceback:
                    logger.exception(
                        f"Error in {func.__name__}: {error_type}: {error_message}"
                    )
                else:
                    logger.error(
                        f"Error in {func.__name__}: {error_type}: {error_message}"
                    )
                
                # Reraise or return fallback
                if reraise:
                    raise
                return fallback_value  # type: ignore
        
        return cast(Callable[..., T], wrapper)
    
    return decorator


def map_exception(
    from_exception: Type[Exception],
    to_exception: Type[PRAgentError],
    message: Optional[str] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to map external exceptions to PR-Agent exceptions.
    
    Args:
        from_exception: Source exception type to catch
        to_exception: Target PR-Agent exception type to raise
        message: Optional message override
        
    Returns:
        Decorated function with exception mapping
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except from_exception as e:
                error_message = message or str(e)
                raise to_exception(error_message) from e
        
        return cast(Callable[..., T], wrapper)
    
    return decorator
