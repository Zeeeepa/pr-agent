"""
Tests for configuration validation
"""

import os
import json
import pytest
import tempfile
from unittest.mock import patch, MagicMock

from pr_agent.execserver.services.settings_service import SettingsService
from pr_agent.execserver.services.config_validation_service import ConfigValidationService

@pytest.fixture
def settings_service():
    """Create a temporary settings file and service for testing"""
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write(b'{}')
        temp_path = temp.name
    
    service = SettingsService(settings_file=temp_path)
    yield service
    
    # Clean up
    os.unlink(temp_path)

@pytest.fixture
def config_validation_service(settings_service):
    """Create a config validation service for testing"""
    return ConfigValidationService(settings_service)

@pytest.mark.asyncio
async def test_validate_notification_settings_valid(config_validation_service):
    """Test validation of valid notification settings"""
    # Test with notifications disabled (should always be valid)
    settings = {"ENABLE_NOTIFICATIONS": False}
    valid, error = await config_validation_service.validate_notification_settings(settings)
    assert valid is True
    assert error is None
    
    # Test with notifications enabled but no webhook URL (still valid as it's optional)
    settings = {"ENABLE_NOTIFICATIONS": True}
    valid, error = await config_validation_service.validate_notification_settings(settings)
    assert valid is True
    assert error is None

@pytest.mark.asyncio
async def test_validate_notification_settings_invalid(config_validation_service):
    """Test validation of invalid notification settings"""
    # Test with invalid webhook URL
    settings = {
        "ENABLE_NOTIFICATIONS": True,
        "NOTIFICATION_WEBHOOK_URL": "invalid-url"
    }
    valid, error = await config_validation_service.validate_notification_settings(settings)
    assert valid is False
    assert "webhook URL must be a valid URL" in error

@pytest.mark.asyncio
async def test_validate_comment_settings_valid(config_validation_service):
    """Test validation of valid comment settings"""
    settings = {
        "COMMENT_TEMPLATE": "Summary: {summary}\nDetails: {details}",
        "COMMENT_STYLE": "detailed",
        "MAX_COMMENT_LENGTH": 5000
    }
    valid, error = await config_validation_service.validate_comment_settings(settings)
    assert valid is True
    assert error is None

@pytest.mark.asyncio
async def test_validate_comment_settings_invalid(config_validation_service):
    """Test validation of invalid comment settings"""
    # Test with missing placeholders
    settings = {
        "COMMENT_TEMPLATE": "This template has no placeholders"
    }
    valid, error = await config_validation_service.validate_comment_settings(settings)
    assert valid is False
    assert "missing required placeholders" in error
    
    # Test with invalid comment style
    settings = {
        "COMMENT_TEMPLATE": "Summary: {summary}\nDetails: {details}",
        "COMMENT_STYLE": "invalid-style"
    }
    valid, error = await config_validation_service.validate_comment_settings(settings)
    assert valid is False
    assert "Comment style must be one of" in error
    
    # Test with invalid max comment length
    settings = {
        "COMMENT_TEMPLATE": "Summary: {summary}\nDetails: {details}",
        "MAX_COMMENT_LENGTH": "not-a-number"
    }
    valid, error = await config_validation_service.validate_comment_settings(settings)
    assert valid is False
    assert "Max comment length must be a valid integer" in error

@pytest.mark.asyncio
async def test_validate_environment_config_valid(config_validation_service):
    """Test validation of valid environment configuration"""
    # Test development environment
    settings = {
        "ENVIRONMENT": "development",
        "LOG_LEVEL": "DEBUG",
        "LOG_FORMAT": "CONSOLE",
        "UI_PORT": 8000,
        "API_PORT": 8001
    }
    valid, error = await config_validation_service.validate_environment_config(settings)
    assert valid is True
    assert error is None
    
    # Test production environment with required settings
    settings = {
        "ENVIRONMENT": "production",
        "WEBHOOK_SECRET": "secret123",
        "CORS_ORIGINS": "https://example.com,https://api.example.com",
        "LOG_LEVEL": "INFO",
        "LOG_FORMAT": "JSON"
    }
    valid, error = await config_validation_service.validate_environment_config(settings)
    assert valid is True
    assert error is None

@pytest.mark.asyncio
async def test_validate_environment_config_invalid(config_validation_service):
    """Test validation of invalid environment configuration"""
    # Test invalid environment
    settings = {"ENVIRONMENT": "invalid-env"}
    valid, error = await config_validation_service.validate_environment_config(settings)
    assert valid is False
    assert "Environment must be one of" in error
    
    # Test production environment with missing required settings
    settings = {"ENVIRONMENT": "production"}
    valid, error = await config_validation_service.validate_environment_config(settings)
    assert valid is False
    assert "Production environment requires" in error
    
    # Test production environment with wildcard CORS origin
    settings = {
        "ENVIRONMENT": "production",
        "WEBHOOK_SECRET": "secret123",
        "CORS_ORIGINS": "*"
    }
    valid, error = await config_validation_service.validate_environment_config(settings)
    assert valid is False
    assert "Wildcard CORS origin" in error
    
    # Test invalid log level
    settings = {"LOG_LEVEL": "TRACE"}
    valid, error = await config_validation_service.validate_environment_config(settings)
    assert valid is False
    assert "Log level must be one of" in error
    
    # Test invalid port
    settings = {"UI_PORT": "not-a-port"}
    valid, error = await config_validation_service.validate_environment_config(settings)
    assert valid is False
    assert "UI_PORT must be a valid integer" in error

@pytest.mark.asyncio
async def test_validate_settings_persistence(config_validation_service):
    """Test validation of settings persistence"""
    # Test with valid settings file path
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp_dir = os.path.dirname(temp.name)
        test_file = os.path.join(temp_dir, "test_settings.json")
        
    settings = {"SETTINGS_FILE_PATH": test_file}
    valid, error = await config_validation_service.validate_settings_persistence(settings)
    assert valid is True
    assert error is None
    
    # Clean up
    if os.path.exists(test_file):
        os.unlink(test_file)

@pytest.mark.asyncio
async def test_validate_ui_components_valid(config_validation_service):
    """Test validation of valid UI components"""
    settings = {
        "UI_THEME": "dark",
        "UI_LANGUAGE": "en",
        "UI_CUSTOM_CSS": "{ color: #333; }"
    }
    valid, error = await config_validation_service.validate_ui_components(settings)
    assert valid is True
    assert error is None

@pytest.mark.asyncio
async def test_validate_ui_components_invalid(config_validation_service):
    """Test validation of invalid UI components"""
    # Test invalid theme
    settings = {"UI_THEME": "neon"}
    valid, error = await config_validation_service.validate_ui_components(settings)
    assert valid is False
    assert "UI theme must be one of" in error
    
    # Test invalid language
    settings = {"UI_LANGUAGE": "klingon"}
    valid, error = await config_validation_service.validate_ui_components(settings)
    assert valid is False
    assert "UI language must be one of" in error

@pytest.mark.asyncio
async def test_validate_all_settings(config_validation_service):
    """Test validation of all settings together"""
    # Test with all valid settings
    settings = {
        "ENABLE_NOTIFICATIONS": False,
        "COMMENT_TEMPLATE": "Summary: {summary}\nDetails: {details}",
        "COMMENT_STYLE": "detailed",
        "MAX_COMMENT_LENGTH": 5000,
        "ENVIRONMENT": "development",
        "LOG_LEVEL": "INFO",
        "LOG_FORMAT": "CONSOLE",
        "UI_PORT": 8000,
        "API_PORT": 8001,
        "UI_THEME": "dark",
        "UI_LANGUAGE": "en"
    }
    
    # Mock the settings service validate_settings method to always return valid
    with patch.object(config_validation_service.settings_service, 'validate_settings', 
                     return_value=(True, None)):
        valid, error, results = await config_validation_service.validate_all_settings(settings)
        assert valid is True
        assert error is None
        assert "notification_settings" in results
        assert "comment_settings" in results
        assert "environment_config" in results
        assert "settings_persistence" in results
        assert "ui_components" in results
        
        # Check that all individual validations passed
        for category, result in results.items():
            assert result["valid"] is True
            assert result["error"] is None

@pytest.mark.asyncio
async def test_validate_all_settings_with_invalid(config_validation_service):
    """Test validation of all settings with some invalid settings"""
    # Test with some invalid settings
    settings = {
        "ENABLE_NOTIFICATIONS": True,
        "NOTIFICATION_WEBHOOK_URL": "invalid-url",  # Invalid
        "COMMENT_TEMPLATE": "Summary: {summary}\nDetails: {details}",
        "COMMENT_STYLE": "detailed",
        "ENVIRONMENT": "development",
        "UI_THEME": "invalid-theme"  # Invalid
    }
    
    # Mock the settings service validate_settings method to always return valid
    with patch.object(config_validation_service.settings_service, 'validate_settings', 
                     return_value=(True, None)):
        valid, error, results = await config_validation_service.validate_all_settings(settings)
        assert valid is False
        assert "Notification settings validation failed" in error
        
        # Check that the notification settings validation failed
        assert results["notification_settings"]["valid"] is False
        assert "webhook URL must be a valid URL" in results["notification_settings"]["error"]

