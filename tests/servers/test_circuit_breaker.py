"""
Tests for the circuit breaker module.
"""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pr_agent.servers.circuit_breaker import (CircuitBreaker, CircuitOpenError,
                                             CircuitState, circuit_breaker,
                                             get_circuit_breaker)


@pytest.mark.asyncio
async def test_circuit_breaker_success():
    """Test successful function call with circuit breaker."""
    breaker = CircuitBreaker(name="test_success")
    
    # Create a mock function that succeeds
    mock_func = AsyncMock()
    mock_func.return_value = "success"
    
    # Call the function through the circuit breaker
    result = await breaker.call(mock_func, "arg1", kwarg1="value1")
    
    # Check that the function was called with the correct arguments
    mock_func.assert_called_once_with("arg1", kwarg1="value1")
    
    # Check that the result is correct
    assert result == "success"
    
    # Check that the circuit is still closed
    assert breaker.state == CircuitState.CLOSED
    assert breaker.failure_count == 0


@pytest.mark.asyncio
async def test_circuit_breaker_failure():
    """Test circuit breaker opening after failures."""
    breaker = CircuitBreaker(failure_threshold=3, name="test_failure")
    
    # Create a mock function that fails
    mock_func = AsyncMock()
    mock_func.side_effect = ValueError("test failure")
    
    # Call the function through the circuit breaker multiple times
    for _ in range(3):
        with pytest.raises(ValueError):
            await breaker.call(mock_func)
    
    # Check that the circuit is now open
    assert breaker.state == CircuitState.OPEN
    assert breaker.failure_count == 3
    
    # Next call should fail fast with CircuitOpenError
    with pytest.raises(CircuitOpenError):
        await breaker.call(mock_func)
    
    # The mock function should not have been called again
    assert mock_func.call_count == 3


@pytest.mark.asyncio
async def test_circuit_breaker_recovery():
    """Test circuit breaker recovery after timeout."""
    breaker = CircuitBreaker(
        failure_threshold=2,
        recovery_timeout=0.1,  # Short timeout for testing
        name="test_recovery"
    )
    
    # Create a mock function that fails initially but succeeds later
    mock_func = AsyncMock()
    mock_func.side_effect = [
        ValueError("failure 1"),
        ValueError("failure 2"),
        "success"  # Third call succeeds
    ]
    
    # First two calls should fail and open the circuit
    for _ in range(2):
        with pytest.raises(ValueError):
            await breaker.call(mock_func)
    
    assert breaker.state == CircuitState.OPEN
    
    # Wait for the recovery timeout
    await asyncio.sleep(0.2)
    
    # Next call should succeed and close the circuit
    result = await breaker.call(mock_func)
    assert result == "success"
    assert breaker.state == CircuitState.CLOSED
    assert breaker.failure_count == 0


@pytest.mark.asyncio
async def test_circuit_breaker_half_open_failure():
    """Test circuit breaker going back to open after failed recovery attempt."""
    breaker = CircuitBreaker(
        failure_threshold=2,
        recovery_timeout=0.1,  # Short timeout for testing
        name="test_half_open_failure"
    )
    
    # Create a mock function that always fails
    mock_func = AsyncMock()
    mock_func.side_effect = ValueError("always fails")
    
    # First two calls should fail and open the circuit
    for _ in range(2):
        with pytest.raises(ValueError):
            await breaker.call(mock_func)
    
    assert breaker.state == CircuitState.OPEN
    
    # Wait for the recovery timeout
    await asyncio.sleep(0.2)
    
    # Next call should try to recover but fail again
    with pytest.raises(ValueError):
        await breaker.call(mock_func)
    
    # Circuit should be open again
    assert breaker.state == CircuitState.OPEN


@pytest.mark.asyncio
async def test_circuit_breaker_excluded_exceptions():
    """Test circuit breaker with excluded exceptions."""
    breaker = CircuitBreaker(
        failure_threshold=2,
        name="test_excluded",
        excluded_exceptions=[KeyError]
    )
    
    # Create a mock function that raises different exceptions
    mock_func = AsyncMock()
    mock_func.side_effect = [
        KeyError("excluded"),  # Should not count toward failure threshold
        KeyError("excluded"),  # Should not count toward failure threshold
        ValueError("counts"),  # Should count toward failure threshold
        ValueError("counts"),  # Should count toward failure threshold
    ]
    
    # First two calls should raise KeyError but not affect the circuit
    for _ in range(2):
        with pytest.raises(KeyError):
            await breaker.call(mock_func)
    
    assert breaker.state == CircuitState.CLOSED
    assert breaker.failure_count == 0
    
    # Next two calls should raise ValueError and open the circuit
    for _ in range(2):
        with pytest.raises(ValueError):
            await breaker.call(mock_func)
    
    assert breaker.state == CircuitState.OPEN
    assert breaker.failure_count == 2


@pytest.mark.asyncio
async def test_circuit_breaker_decorator():
    """Test circuit breaker as a decorator."""
    # Create a mock function that fails
    mock_func = AsyncMock()
    mock_func.side_effect = ValueError("test failure")
    
    # Apply the circuit breaker decorator
    breaker = CircuitBreaker(failure_threshold=2, name="test_decorator")
    decorated_func = breaker(mock_func)
    
    # Call the decorated function
    for _ in range(2):
        with pytest.raises(ValueError):
            await decorated_func("arg1", kwarg1="value1")
    
    # Check that the circuit is now open
    assert breaker.state == CircuitState.OPEN
    
    # Next call should fail fast with CircuitOpenError
    with pytest.raises(CircuitOpenError):
        await decorated_func("arg1", kwarg1="value1")


@pytest.mark.asyncio
async def test_get_circuit_breaker():
    """Test get_circuit_breaker function."""
    # Get two circuit breakers with the same name
    breaker1 = get_circuit_breaker("shared", failure_threshold=3)
    breaker2 = get_circuit_breaker("shared", failure_threshold=5)  # Different threshold, should be ignored
    
    # They should be the same object
    assert breaker1 is breaker2
    assert breaker1.failure_threshold == 3  # Should keep the first configuration
    
    # Create a mock function that fails
    mock_func = AsyncMock()
    mock_func.side_effect = ValueError("test failure")
    
    # Call the function through the first breaker
    for _ in range(3):
        with pytest.raises(ValueError):
            await breaker1.call(mock_func)
    
    # The circuit should be open
    assert breaker1.state == CircuitState.OPEN
    
    # The second breaker should also be open (same object)
    assert breaker2.state == CircuitState.OPEN


@pytest.mark.asyncio
async def test_circuit_breaker_function_decorator():
    """Test circuit_breaker function decorator."""
    # Create a mock function
    mock_func = AsyncMock()
    mock_func.side_effect = ValueError("test failure")
    
    # Apply the decorator
    decorated_func = circuit_breaker(
        name="test_func_decorator",
        failure_threshold=2
    )(mock_func)
    
    # Call the decorated function
    for _ in range(2):
        with pytest.raises(ValueError):
            await decorated_func("arg1", kwarg1="value1")
    
    # Next call should fail fast with CircuitOpenError
    with pytest.raises(CircuitOpenError):
        await decorated_func("arg1", kwarg1="value1")
    
    # Get the circuit breaker and check its state
    breaker = get_circuit_breaker("test_func_decorator")
    assert breaker.state == CircuitState.OPEN

