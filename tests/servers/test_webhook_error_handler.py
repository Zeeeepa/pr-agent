"""
Tests for the webhook error handler module.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette import status

from pr_agent.servers.webhook_error_handler import (MalformedWebhookError,
                                                   SignatureValidationError,
                                                   WebhookError,
                                                   WebhookProcessingError,
                                                   handle_webhook_errors,
                                                   verify_webhook_signature)


@pytest.mark.asyncio
async def test_handle_webhook_errors_success():
    """Test successful function call with error handler."""
    # Create a mock function that succeeds
    mock_func = AsyncMock()
    mock_func.return_value = {"status": "success"}
    
    # Apply the error handler decorator
    decorated_func = handle_webhook_errors(mock_func)
    
    # Call the decorated function
    result = await decorated_func()
    
    # Check that the function was called
    mock_func.assert_called_once()
    
    # Check that the result is correct
    assert result == {"status": "success"}


@pytest.mark.asyncio
async def test_handle_webhook_errors_signature_validation():
    """Test error handler with signature validation error."""
    # Create a mock function that raises a signature validation error
    mock_func = AsyncMock()
    mock_func.side_effect = SignatureValidationError(
        message="Invalid signature",
        details={"header": "test-header"}
    )
    
    # Apply the error handler decorator
    decorated_func = handle_webhook_errors(mock_func)
    
    # Call the decorated function
    result = await decorated_func()
    
    # Check that the function was called
    mock_func.assert_called_once()
    
    # Check that the result is a JSONResponse with the correct status code and content
    assert isinstance(result, JSONResponse)
    assert result.status_code == status.HTTP_403_FORBIDDEN
    assert result.body.decode() == '{"status":"error","message":"Invalid signature"}'


@pytest.mark.asyncio
async def test_handle_webhook_errors_malformed_webhook():
    """Test error handler with malformed webhook error."""
    # Create a mock function that raises a malformed webhook error
    mock_func = AsyncMock()
    mock_func.side_effect = MalformedWebhookError(
        message="Invalid JSON",
        details={"payload": "invalid"}
    )
    
    # Apply the error handler decorator
    decorated_func = handle_webhook_errors(mock_func)
    
    # Call the decorated function
    result = await decorated_func()
    
    # Check that the function was called
    mock_func.assert_called_once()
    
    # Check that the result is a JSONResponse with the correct status code and content
    assert isinstance(result, JSONResponse)
    assert result.status_code == status.HTTP_400_BAD_REQUEST
    assert result.body.decode() == '{"status":"error","message":"Invalid JSON"}'


@pytest.mark.asyncio
async def test_handle_webhook_errors_processing_error():
    """Test error handler with webhook processing error."""
    # Create a mock function that raises a webhook processing error
    mock_func = AsyncMock()
    mock_func.side_effect = WebhookProcessingError(
        message="Processing failed",
        details={"reason": "test-reason"}
    )
    
    # Apply the error handler decorator
    decorated_func = handle_webhook_errors(mock_func)
    
    # Call the decorated function
    result = await decorated_func()
    
    # Check that the function was called
    mock_func.assert_called_once()
    
    # Check that the result is a JSONResponse with the correct status code and content
    assert isinstance(result, JSONResponse)
    assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert result.body.decode() == '{"status":"error","message":"Processing failed"}'


@pytest.mark.asyncio
async def test_handle_webhook_errors_unhandled_exception():
    """Test error handler with unhandled exception."""
    # Create a mock function that raises an unhandled exception
    mock_func = AsyncMock()
    mock_func.side_effect = ValueError("Unhandled error")
    
    # Apply the error handler decorator
    decorated_func = handle_webhook_errors(mock_func)
    
    # Call the decorated function
    result = await decorated_func()
    
    # Check that the function was called
    mock_func.assert_called_once()
    
    # Check that the result is a JSONResponse with the correct status code and content
    assert isinstance(result, JSONResponse)
    assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert result.body.decode() == '{"status":"error","message":"Internal server error"}'


def test_verify_webhook_signature_success():
    """Test successful webhook signature verification."""
    # Create mock request and utils.verify_signature
    mock_request = MagicMock(spec=Request)
    mock_request.headers = {"x-hub-signature-256": "test-signature"}
    
    with patch("pr_agent.servers.webhook_error_handler.verify_signature") as mock_verify:
        # Call the function
        verify_webhook_signature(
            request=mock_request,
            payload_body=b"test-payload",
            secret_token="test-secret"
        )
        
        # Check that verify_signature was called with the correct arguments
        mock_verify.assert_called_once_with(
            b"test-payload",
            "test-secret",
            "test-signature"
        )


def test_verify_webhook_signature_missing_header():
    """Test webhook signature verification with missing header."""
    # Create mock request with missing header
    mock_request = MagicMock(spec=Request)
    mock_request.headers = {}
    
    with patch("pr_agent.servers.webhook_error_handler.verify_signature") as mock_verify:
        # Call the function and expect an exception
        with pytest.raises(SignatureValidationError) as excinfo:
            verify_webhook_signature(
                request=mock_request,
                payload_body=b"test-payload",
                secret_token="test-secret"
            )
        
        # Check that the exception has the correct message
        assert "x-hub-signature-256 header is missing" in str(excinfo.value)
        
        # Check that verify_signature was not called
        mock_verify.assert_not_called()


def test_verify_webhook_signature_validation_failure():
    """Test webhook signature verification with validation failure."""
    # Create mock request
    mock_request = MagicMock(spec=Request)
    mock_request.headers = {"x-hub-signature-256": "test-signature"}
    
    with patch("pr_agent.servers.webhook_error_handler.verify_signature") as mock_verify:
        # Make verify_signature raise an exception
        mock_verify.side_effect = ValueError("Signature mismatch")
        
        # Call the function and expect an exception
        with pytest.raises(SignatureValidationError) as excinfo:
            verify_webhook_signature(
                request=mock_request,
                payload_body=b"test-payload",
                secret_token="test-secret"
            )
        
        # Check that the exception has the correct message
        assert "Signature validation failed" in str(excinfo.value)
        
        # Check that verify_signature was called
        mock_verify.assert_called_once()

