"""
Error handling utilities for webhook servers.

This module provides standardized error handling for webhook endpoints,
including custom exception types and decorators for consistent error responses.
"""

import functools
import traceback
from typing import Any, Callable, Dict, Optional, TypeVar, cast

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette import status

from pr_agent.log import get_logger

logger = get_logger()

T = TypeVar("T")
AsyncEndpoint = Callable[..., Any]


class WebhookError(Exception):
    """Base exception for webhook-related errors."""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a webhook error.
        
        Args:
            message: Error message
            status_code: HTTP status code to return
            details: Additional error details for logging
        """
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class SignatureValidationError(WebhookError):
    """Exception raised when webhook signature validation fails."""
    
    def __init__(
        self,
        message: str = "Webhook signature validation failed",
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a signature validation error.
        
        Args:
            message: Error message
            details: Additional error details for logging
        """
        super().__init__(
            message,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details
        )


class WebhookProcessingError(WebhookError):
    """Exception raised when webhook processing fails."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a webhook processing error.
        
        Args:
            message: Error message
            details: Additional error details for logging
        """
        super().__init__(
            message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class MalformedWebhookError(WebhookError):
    """Exception raised when webhook payload is malformed."""
    
    def __init__(
        self,
        message: str = "Malformed webhook payload",
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a malformed webhook error.
        
        Args:
            message: Error message
            details: Additional error details for logging
        """
        super().__init__(
            message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


def handle_webhook_errors(func: AsyncEndpoint) -> AsyncEndpoint:
    """
    Decorator to standardize error handling for webhook endpoints.
    
    This decorator catches exceptions raised during webhook processing and
    returns appropriate HTTP responses with standardized error messages.
    
    Args:
        func: The FastAPI endpoint function to wrap
        
    Returns:
        Wrapped function with standardized error handling
    """
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except SignatureValidationError as e:
            logger.warning(
                f"Signature validation error: {e.message}",
                extra={"details": e.details}
            )
            return JSONResponse(
                status_code=e.status_code,
                content={"status": "error", "message": e.message}
            )
        except MalformedWebhookError as e:
            logger.warning(
                f"Malformed webhook error: {e.message}",
                extra={"details": e.details}
            )
            return JSONResponse(
                status_code=e.status_code,
                content={"status": "error", "message": e.message}
            )
        except WebhookProcessingError as e:
            logger.error(
                f"Webhook processing error: {e.message}",
                extra={"details": e.details}
            )
            return JSONResponse(
                status_code=e.status_code,
                content={"status": "error", "message": e.message}
            )
        except Exception as e:
            # Unhandled exception
            error_details = {
                "exception": str(e),
                "traceback": traceback.format_exc()
            }
            logger.exception(
                f"Unhandled exception in webhook handler: {str(e)}",
                extra={"details": error_details}
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"status": "error", "message": "Internal server error"}
            )
    
    return cast(AsyncEndpoint, wrapper)


def verify_webhook_signature(
    request: Request,
    payload_body: bytes,
    secret_token: str,
    header_name: str = "x-hub-signature-256"
) -> None:
    """
    Verify webhook signature and raise appropriate exceptions.
    
    This is a wrapper around the existing verify_signature function that
    raises standardized exceptions for better error handling.
    
    Args:
        request: The FastAPI request object
        payload_body: The raw request body
        secret_token: The webhook secret token
        header_name: The name of the header containing the signature
        
    Raises:
        SignatureValidationError: If signature validation fails
    """
    from pr_agent.servers.utils import verify_signature
    
    try:
        signature_header = request.headers.get(header_name)
        if not signature_header:
            raise SignatureValidationError(
                f"{header_name} header is missing!",
                details={"headers": dict(request.headers)}
            )
        
        verify_signature(payload_body, secret_token, signature_header)
    except Exception as e:
        if isinstance(e, SignatureValidationError):
            raise
        
        raise SignatureValidationError(
            f"Signature validation failed: {str(e)}",
            details={"exception": str(e)}
        )

