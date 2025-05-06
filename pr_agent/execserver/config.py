"""
Configuration module for ExeServer.

This module provides centralized configuration management for the ExeServer module,
leveraging the PR-Agent's configuration system.
"""

import os

from dotenv import load_dotenv

from pr_agent.config_loader import config_manager
from pr_agent.error_handler import ConfigurationError

# Load environment variables from .env file
load_dotenv()

# Configuration keys with defaults
CONFIG_DEFAULTS = {
    # GitHub configuration
    "GITHUB_TOKEN": None,
    "GITHUB_APP_ID": None,
    "GITHUB_APP_PRIVATE_KEY": None,
    "GITHUB_APP_INSTALLATION_ID": None,

    # Database configuration
    "SUPABASE_URL": None,
    "SUPABASE_ANON_KEY": None,

    # UI configuration
    "UI_PORT": 8000,
    "API_PORT": 8001,

    # Notification configuration
    "ENABLE_NOTIFICATIONS": False,

    # Security configuration
    "WEBHOOK_SECRET": None,
    "CORS_ORIGINS": ["*"],  # Default to allow all origins (for development)

    # Logging configuration
    "LOG_LEVEL": "INFO",
    "LOG_FORMAT": "CONSOLE",
}

# Global settings service instance
_settings_service = None

def set_settings_service(settings_service):
    """Set the global settings service instance"""
    global _settings_service
    _settings_service = settings_service


def get_config(key, default=None):
    """
    Get a configuration value with proper error handling.

    Args:
        key: Configuration key
        default: Default value if not found

    Returns:
        Configuration value

    Raises:
        ConfigurationError: If the key is required but not found
    """
    # Check settings service first if available
    global _settings_service
    if _settings_service:
        value = _settings_service.get_setting(key)
        if value is not None:
            return value

    # Use the default from CONFIG_DEFAULTS if provided
    if default is None and key in CONFIG_DEFAULTS:
        default = CONFIG_DEFAULTS[key]

    # Handle the case where default is a list (like CORS_ORIGINS)
    if isinstance(default, list):
        value = os.getenv(key)
        if value is not None:
            # Parse comma-separated string into list if from environment
            return [item.strip() for item in value.split(',')]
        return default

    value = config_manager.get(key, default)

    # Raise error if value is required but not found
    # GitHub App ID, Private Key, and Installation ID are optional
    if value is None and default is None and key not in ["GITHUB_APP_ID", "GITHUB_APP_PRIVATE_KEY", "GITHUB_APP_INSTALLATION_ID", "SUPABASE_URL", "SUPABASE_ANON_KEY"]:
        raise ConfigurationError(f"Required configuration '{key}' not found")

    return value


# GitHub configuration
def get_github_token():
    """Get GitHub token with proper error handling."""
    return get_config("GITHUB_TOKEN")


def get_github_app_id():
    """Get GitHub App ID with proper error handling."""
    return get_config("GITHUB_APP_ID")


def get_github_app_private_key():
    """Get GitHub App private key with proper error handling."""
    return get_config("GITHUB_APP_PRIVATE_KEY")


def get_github_app_installation_id():
    """Get GitHub App installation ID with proper error handling."""
    return get_config("GITHUB_APP_INSTALLATION_ID")


# Database configuration
def get_supabase_url():
    """Get Supabase URL with proper error handling."""
    return get_config("SUPABASE_URL")


def get_supabase_anon_key():
    """Get Supabase anonymous key with proper error handling."""
    return get_config("SUPABASE_ANON_KEY")


# UI configuration
def get_ui_port():
    """Get UI port with proper error handling."""
    return get_config("UI_PORT")


def get_api_port():
    """Get API port with proper error handling."""
    return get_config("API_PORT")


# Notification configuration
def get_enable_notifications():
    """Get notification setting with proper error handling."""
    return get_config("ENABLE_NOTIFICATIONS")


# Security configuration
def get_webhook_secret():
    """Get webhook secret with proper error handling."""
    return get_config("WEBHOOK_SECRET")


def get_cors_origins():
    """Get CORS origins with proper error handling."""
    return get_config("CORS_ORIGINS")


# Logging configuration
def get_log_level():
    """Get log level with proper error handling."""
    return get_config("LOG_LEVEL")


def get_log_format():
    """Get log format with proper error handling."""
    return get_config("LOG_FORMAT")


# Utility function to get settings from environment or PR-Agent config
def get_setting_or_env(key, default=None):
    """
    Get a setting from environment variables or PR-Agent config

    Args:
        key (str): The key to look for
        default: Default value if key is not found

    Returns:
        The value of the setting or default
    """
    return get_config(key, default)
