# Webhook Setup and Real-time Notifications Implementation Plan

## Overview

This document outlines the implementation strategy for enhancing the PR-Agent's webhook setup and real-time notifications module. The implementation will focus on improving tunneling support, error handling, and adding circuit breaker patterns for API resilience.

## 1. Tunneling Support Implementation

### Create a Tunneling Utility Module

```python
# pr_agent/servers/tunneling.py

import logging
import subprocess
import time
from typing import Optional, Dict, Any, Tuple

logger = logging.getLogger(__name__)

class TunnelManager:
    """Manages tunneling services for local webhook development."""
    
    def __init__(self, port: int = 3000, preferred_service: str = "ngrok"):
        """
        Initialize the tunnel manager.
        
        Args:
            port: The local port to expose
            preferred_service: The preferred tunneling service ("ngrok" or "localtunnel")
        """
        self.port = port
        self.preferred_service = preferred_service
        self.tunnel_url = None
        self.process = None
        
    def start_tunnel(self) -> str:
        """
        Start a tunnel using the preferred service with fallback.
        
        Returns:
            The public URL of the tunnel
        """
        if self.preferred_service == "ngrok":
            success, url = self._start_ngrok()
            if not success and self.preferred_service == "ngrok":
                logger.warning("Failed to start ngrok, falling back to localtunnel")
                success, url = self._start_localtunnel()
        else:
            success, url = self._start_localtunnel()
            if not success:
                logger.warning("Failed to start localtunnel, falling back to ngrok")
                success, url = self._start_ngrok()
                
        if not success:
            raise RuntimeError("Failed to start any tunneling service")
            
        self.tunnel_url = url
        return url
        
    def _start_ngrok(self) -> Tuple[bool, Optional[str]]:
        """Start an ngrok tunnel."""
        try:
            # Implementation details for starting ngrok
            # Return the public URL if successful
            return True, "https://example.ngrok.io"
        except Exception as e:
            logger.error(f"Failed to start ngrok: {e}")
            return False, None
            
    def _start_localtunnel(self) -> Tuple[bool, Optional[str]]:
        """Start a localtunnel tunnel."""
        try:
            # Implementation details for starting localtunnel
            # Return the public URL if successful
            return True, "https://example.localtunnel.me"
        except Exception as e:
            logger.error(f"Failed to start localtunnel: {e}")
            return False, None
            
    def stop_tunnel(self) -> None:
        """Stop the active tunnel."""
        if self.process:
            self.process.terminate()
            self.process = None
        self.tunnel_url = None
```

### Integrate Tunneling with Server Startup

Modify the server startup code to optionally use tunneling in development mode:

```python
# pr_agent/servers/github_app.py (and other server files)

def start(use_tunnel: bool = False):
    """Start the FastAPI server with optional tunneling."""
    port = int(os.environ.get("PORT", "3000"))
    
    if use_tunnel:
        from pr_agent.servers.tunneling import TunnelManager
        tunnel_manager = TunnelManager(port=port)
        tunnel_url = tunnel_manager.start_tunnel()
        logger.info(f"Webhook server accessible via tunnel: {tunnel_url}")
        
    uvicorn.run(app, host="0.0.0.0", port=port)
```

## 2. Circuit Breaker Pattern Implementation

### Create a Circuit Breaker Utility

```python
# pr_agent/servers/circuit_breaker.py

import time
import logging
from enum import Enum
from typing import Callable, Any, Dict, Optional
from functools import wraps

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation, requests pass through
    OPEN = "open"      # Circuit is open, requests fail fast
    HALF_OPEN = "half_open"  # Testing if service is back online

class CircuitBreaker:
    """
    Implements the circuit breaker pattern to prevent repeated calls to failing services.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        name: str = "default"
    ):
        """
        Initialize a circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening the circuit
            recovery_timeout: Seconds to wait before trying to recover (half-open state)
            name: Name of this circuit breaker for logging
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        
    def __call__(self, func):
        """Decorator to wrap a function with circuit breaker logic."""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await self.call(func, *args, **kwargs)
        return wrapper
        
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Call the protected function with circuit breaker logic.
        
        Args:
            func: The function to call
            *args, **kwargs: Arguments to pass to the function
            
        Returns:
            The result of the function call
            
        Raises:
            Exception: If the circuit is open or the function call fails
        """
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                # Try to recover
                logger.info(f"Circuit {self.name} trying to recover (half-open)")
                self.state = CircuitState.HALF_OPEN
            else:
                # Circuit is open, fail fast
                logger.warning(f"Circuit {self.name} is open, failing fast")
                raise RuntimeError(f"Circuit {self.name} is open")
                
        try:
            result = await func(*args, **kwargs)
            
            # If we were in half-open state and the call succeeded, close the circuit
            if self.state == CircuitState.HALF_OPEN:
                logger.info(f"Circuit {self.name} recovered, closing")
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                
            return result
            
        except Exception as e:
            # Record the failure
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            # If we've reached the threshold, open the circuit
            if self.state == CircuitState.CLOSED and self.failure_count >= self.failure_threshold:
                logger.warning(f"Circuit {self.name} opened after {self.failure_count} failures")
                self.state = CircuitState.OPEN
                
            # If we were testing in half-open state, go back to open
            if self.state == CircuitState.HALF_OPEN:
                logger.warning(f"Circuit {self.name} reopened after failed recovery attempt")
                self.state = CircuitState.OPEN
                
            raise e
```

### Apply Circuit Breaker to API Calls

Integrate the circuit breaker with API calls to Git providers:

```python
# Example integration in a Git provider class

from pr_agent.servers.circuit_breaker import CircuitBreaker

class GitHubProvider:
    # ...existing code...
    
    @CircuitBreaker(failure_threshold=3, recovery_timeout=60, name="github_api")
    async def create_comment(self, pr_id, body):
        # API call implementation
        pass
```

## 3. Enhanced Error Handling Implementation

### Create a Standardized Error Handler

```python
# pr_agent/servers/error_handler.py

import logging
import traceback
from typing import Dict, Any, Optional, Callable, Awaitable
from functools import wraps

logger = logging.getLogger(__name__)

class WebhookError(Exception):
    """Base exception for webhook-related errors."""
    
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)

class SignatureValidationError(WebhookError):
    """Exception raised when webhook signature validation fails."""
    
    def __init__(self, message: str = "Webhook signature validation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=403, details=details)

class WebhookProcessingError(WebhookError):
    """Exception raised when webhook processing fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)

def handle_webhook_errors(func: Callable) -> Callable:
    """
    Decorator to standardize error handling for webhook endpoints.
    
    Args:
        func: The FastAPI endpoint function to wrap
        
    Returns:
        Wrapped function with standardized error handling
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except SignatureValidationError as e:
            logger.warning(f"Signature validation error: {e.message}", extra={"details": e.details})
            return {"status": "error", "message": e.message, "status_code": e.status_code}
        except WebhookProcessingError as e:
            logger.error(f"Webhook processing error: {e.message}", extra={"details": e.details})
            return {"status": "error", "message": e.message, "status_code": e.status_code}
        except Exception as e:
            logger.exception(f"Unhandled exception in webhook handler: {str(e)}")
            return {"status": "error", "message": "Internal server error", "status_code": 500}
    
    return wrapper
```

### Apply Error Handling to Webhook Endpoints

Update the webhook endpoints to use the standardized error handling:

```python
# pr_agent/servers/github_app.py

from pr_agent.servers.error_handler import handle_webhook_errors, SignatureValidationError

@router.post("/api/v1/github_webhooks")
@handle_webhook_errors
async def handle_github_webhooks(background_tasks: BackgroundTasks, request: Request, response: Response):
    # Implementation with improved error handling
    pass
```

## 4. Implementation of Tests

Create comprehensive tests for the new functionality:

```python
# tests/webhook/test_tunneling.py

import pytest
from unittest.mock import patch, MagicMock
from pr_agent.servers.tunneling import TunnelManager

def test_ngrok_tunnel_start():
    with patch('pr_agent.servers.tunneling.TunnelManager._start_ngrok') as mock_start:
        mock_start.return_value = (True, "https://test.ngrok.io")
        
        manager = TunnelManager(preferred_service="ngrok")
        url = manager.start_tunnel()
        
        assert url == "https://test.ngrok.io"
        assert manager.tunnel_url == "https://test.ngrok.io"
        mock_start.assert_called_once()

def test_ngrok_fallback_to_localtunnel():
    with patch('pr_agent.servers.tunneling.TunnelManager._start_ngrok') as mock_ngrok:
        with patch('pr_agent.servers.tunneling.TunnelManager._start_localtunnel') as mock_localtunnel:
            mock_ngrok.return_value = (False, None)
            mock_localtunnel.return_value = (True, "https://test.localtunnel.me")
            
            manager = TunnelManager(preferred_service="ngrok")
            url = manager.start_tunnel()
            
            assert url == "https://test.localtunnel.me"
            assert manager.tunnel_url == "https://test.localtunnel.me"
            mock_ngrok.assert_called_once()
            mock_localtunnel.assert_called_once()
```

```python
# tests/webhook/test_circuit_breaker.py

import pytest
import asyncio
from pr_agent.servers.circuit_breaker import CircuitBreaker, CircuitState

@pytest.mark.asyncio
async def test_circuit_breaker_opens_after_failures():
    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=0.1)
    
    # Create a function that will fail
    async def failing_function():
        raise ValueError("Test failure")
    
    # First 3 calls should try and fail
    for _ in range(3):
        with pytest.raises(ValueError):
            await breaker.call(failing_function)
    
    # Circuit should now be open
    assert breaker.state == CircuitState.OPEN
    
    # Next call should fail fast with RuntimeError
    with pytest.raises(RuntimeError):
        await breaker.call(failing_function)
```

## 5. Documentation Updates

Create documentation for the new features:

```markdown
# Webhook Development Guide

## Local Development with Tunneling

PR-Agent supports local webhook development using tunneling services like ngrok and localtunnel. This allows you to receive webhook events from Git providers on your local development machine.

### Setup

1. Install the required dependencies:
   ```
   pip install pyngrok localtunnel
   ```

2. Start the server with tunneling enabled:
   ```
   python -m pr_agent.servers.github_app --use-tunnel
   ```

3. The server will automatically create a tunnel and display the public URL.

4. Configure your Git provider webhook to use this URL.

### Configuration Options

- `TUNNEL_SERVICE`: Set to "ngrok" or "localtunnel" (default: "ngrok")
- `TUNNEL_AUTH_TOKEN`: Authentication token for ngrok (if required)
- `TUNNEL_REGION`: Region for localtunnel (if required)

## Error Handling and Resilience

PR-Agent implements several patterns to ensure webhook reliability:

1. **Circuit Breaker Pattern**: Prevents cascading failures when Git provider APIs are unavailable
2. **Standardized Error Handling**: Consistent error responses and logging
3. **Automatic Retries**: Exponential backoff for transient failures

### Circuit Breaker Configuration

The circuit breaker can be configured with the following settings:

- `CIRCUIT_BREAKER_FAILURE_THRESHOLD`: Number of failures before opening the circuit (default: 5)
- `CIRCUIT_BREAKER_RECOVERY_TIMEOUT`: Seconds to wait before trying to recover (default: 30)
```

## Implementation Timeline

1. **Week 1**: Implement tunneling support and write tests
2. **Week 2**: Implement circuit breaker pattern and write tests
3. **Week 3**: Enhance error handling and write tests
4. **Week 4**: Update documentation and perform integration testing

