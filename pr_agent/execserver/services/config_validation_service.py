"""
Configuration Validation Service

This module provides a service for validating configuration options
"""

import os
import re
import logging
import json
from typing import Dict, Any, Optional, Tuple, List
import requests

logger = logging.getLogger(__name__)

class ConfigValidationService:
    """
    Service for validating configuration options
    """
    
    def __init__(self, settings_service=None):
        """
        Initialize the config validation service
        
        Args:
            settings_service: Optional settings service instance
        """
        self.settings_service = settings_service
    
    async def validate_notification_settings(self, settings: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate notification settings
        
        Args:
            settings: Dict of settings to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if notifications are enabled
        if 'ENABLE_NOTIFICATIONS' in settings:
            enable_notifications = settings['ENABLE_NOTIFICATIONS']
            
            # Convert string to boolean if needed
            if isinstance(enable_notifications, str):
                enable_notifications = enable_notifications.lower() in ('true', 'yes', '1')
            
            # If notifications are enabled, validate required settings
            if enable_notifications:
                # Check for required notification settings
                if 'NOTIFICATION_WEBHOOK_URL' in settings:
                    webhook_url = settings['NOTIFICATION_WEBHOOK_URL']
                    
                    # Validate webhook URL format
                    if not webhook_url or not webhook_url.startswith(('http://', 'https://')):
                        return False, "Notification webhook URL must be a valid URL starting with http:// or https://"
                    
                    # Optionally test the webhook connection
                    try:
                        # Simple HEAD request to verify the URL is reachable
                        response = requests.head(webhook_url, timeout=5)
                        if response.status_code >= 400:
                            return False, f"Notification webhook URL returned error status: {response.status_code}"
                    except requests.exceptions.Timeout:
                        return False, "Notification webhook URL connection timed out"
                    except requests.exceptions.ConnectionError:
                        return False, "Notification webhook URL connection error"
                    except Exception as e:
                        logger.warning(f"Failed to test notification webhook URL: {str(e)}")
                        # Don't fail validation for this, as the URL might still be valid
        
        return True, None
    
    async def validate_comment_settings(self, settings: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate comment settings
        
        Args:
            settings: Dict of settings to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate comment template settings
        if 'COMMENT_TEMPLATE' in settings:
            comment_template = settings['COMMENT_TEMPLATE']
            
            # Check if template is a valid string
            if not isinstance(comment_template, str):
                return False, "Comment template must be a string"
            
            # Check if template is too long
            if len(comment_template) > 10000:
                return False, "Comment template is too long (max 10000 characters)"
            
            # Check for required placeholders
            required_placeholders = ['{summary}', '{details}']
            missing_placeholders = [p for p in required_placeholders if p not in comment_template]
            
            if missing_placeholders:
                return False, f"Comment template is missing required placeholders: {', '.join(missing_placeholders)}"
        
        # Validate comment style settings
        if 'COMMENT_STYLE' in settings:
            comment_style = settings['COMMENT_STYLE']
            valid_styles = ['detailed', 'concise', 'minimal']
            
            if comment_style not in valid_styles:
                return False, f"Comment style must be one of: {', '.join(valid_styles)}"
        
        # Validate max comment length
        if 'MAX_COMMENT_LENGTH' in settings:
            max_length = settings['MAX_COMMENT_LENGTH']
            
            # Convert to integer if needed
            if isinstance(max_length, str):
                try:
                    max_length = int(max_length)
                except ValueError:
                    return False, "Max comment length must be a valid integer"
            
            # Check if value is reasonable
            if not isinstance(max_length, int) or max_length < 100 or max_length > 100000:
                return False, "Max comment length must be between 100 and 100000"
        
        return True, None
    
    async def validate_environment_config(self, settings: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate environment configuration
        
        Args:
            settings: Dict of settings to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate environment-specific settings
        if 'ENVIRONMENT' in settings:
            environment = settings['ENVIRONMENT']
            valid_environments = ['development', 'testing', 'production']
            
            if environment not in valid_environments:
                return False, f"Environment must be one of: {', '.join(valid_environments)}"
            
            # Validate production-specific requirements
            if environment == 'production':
                # Check for required production settings
                required_settings = ['WEBHOOK_SECRET', 'CORS_ORIGINS']
                missing_settings = [s for s in required_settings if s not in settings or not settings[s]]
                
                if missing_settings:
                    return False, f"Production environment requires the following settings: {', '.join(missing_settings)}"
                
                # Validate CORS origins for production
                if 'CORS_ORIGINS' in settings:
                    cors_origins = settings['CORS_ORIGINS']
                    
                    # Parse string to list if needed
                    if isinstance(cors_origins, str):
                        cors_origins = [origin.strip() for origin in cors_origins.split(',')]
                    
                    # Validate each origin
                    for origin in cors_origins:
                        if origin == '*':
                            return False, "Wildcard CORS origin (*) is not allowed in production environment"
                        
                        if not origin.startswith(('http://', 'https://')):
                            return False, f"Invalid CORS origin: {origin}. Must start with http:// or https://"
        
        # Validate log level
        if 'LOG_LEVEL' in settings:
            log_level = settings['LOG_LEVEL']
            valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            
            if log_level not in valid_log_levels:
                return False, f"Log level must be one of: {', '.join(valid_log_levels)}"
        
        # Validate log format
        if 'LOG_FORMAT' in settings:
            log_format = settings['LOG_FORMAT']
            valid_formats = ['CONSOLE', 'JSON']
            
            if log_format not in valid_formats:
                return False, f"Log format must be one of: {', '.join(valid_formats)}"
        
        # Validate port settings
        for port_setting in ['UI_PORT', 'API_PORT']:
            if port_setting in settings:
                port = settings[port_setting]
                
                # Convert to integer if needed
                if isinstance(port, str):
                    try:
                        port = int(port)
                    except ValueError:
                        return False, f"{port_setting} must be a valid integer"
                
                # Check if port is in valid range
                if not isinstance(port, int) or port < 1 or port > 65535:
                    return False, f"{port_setting} must be between 1 and 65535"
        
        return True, None
    
    async def validate_settings_persistence(self, settings: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate settings persistence
        
        Args:
            settings: Dict of settings to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if settings file path is valid
        if 'SETTINGS_FILE_PATH' in settings:
            file_path = settings['SETTINGS_FILE_PATH']
            
            # Check if path is a string
            if not isinstance(file_path, str):
                return False, "Settings file path must be a string"
            
            # Check if directory exists
            dir_path = os.path.dirname(file_path)
            if dir_path and not os.path.exists(dir_path):
                try:
                    # Try to create the directory
                    os.makedirs(dir_path, exist_ok=True)
                except Exception as e:
                    return False, f"Failed to create settings directory: {str(e)}"
            
            # Check if file is writable
            try:
                # Try to write to the file
                with open(file_path, 'a') as f:
                    pass
            except Exception as e:
                return False, f"Settings file is not writable: {str(e)}"
        
        return True, None
    
    async def validate_ui_components(self, settings: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate settings UI components
        
        Args:
            settings: Dict of settings to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate UI theme settings
        if 'UI_THEME' in settings:
            theme = settings['UI_THEME']
            valid_themes = ['light', 'dark', 'system']
            
            if theme not in valid_themes:
                return False, f"UI theme must be one of: {', '.join(valid_themes)}"
        
        # Validate UI language settings
        if 'UI_LANGUAGE' in settings:
            language = settings['UI_LANGUAGE']
            valid_languages = ['en', 'es', 'fr', 'de', 'ja', 'zh']
            
            if language not in valid_languages:
                return False, f"UI language must be one of: {', '.join(valid_languages)}"
        
        # Validate UI customization settings
        if 'UI_CUSTOM_CSS' in settings:
            custom_css = settings['UI_CUSTOM_CSS']
            
            # Check if CSS is valid
            if custom_css and not custom_css.strip().startswith('{') and not custom_css.strip().endswith('}'):
                return False, "Custom CSS must be a valid CSS object"
        
        return True, None
    
    async def validate_all_settings(self, settings: Dict[str, Any]) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Validate all settings
        
        Args:
            settings: Dict of settings to validate
            
        Returns:
            Tuple of (is_valid, error_message, validation_results)
        """
        validation_results = {}
        
        # Validate notification settings
        valid, error = await self.validate_notification_settings(settings)
        validation_results['notification_settings'] = {'valid': valid, 'error': error}
        if not valid:
            return False, f"Notification settings validation failed: {error}", validation_results
        
        # Validate comment settings
        valid, error = await self.validate_comment_settings(settings)
        validation_results['comment_settings'] = {'valid': valid, 'error': error}
        if not valid:
            return False, f"Comment settings validation failed: {error}", validation_results
        
        # Validate environment configuration
        valid, error = await self.validate_environment_config(settings)
        validation_results['environment_config'] = {'valid': valid, 'error': error}
        if not valid:
            return False, f"Environment configuration validation failed: {error}", validation_results
        
        # Validate settings persistence
        valid, error = await self.validate_settings_persistence(settings)
        validation_results['settings_persistence'] = {'valid': valid, 'error': error}
        if not valid:
            return False, f"Settings persistence validation failed: {error}", validation_results
        
        # Validate UI components
        valid, error = await self.validate_ui_components(settings)
        validation_results['ui_components'] = {'valid': valid, 'error': error}
        if not valid:
            return False, f"UI components validation failed: {error}", validation_results
        
        # If we have a settings service, use it to validate other settings
        if self.settings_service:
            valid, error = await self.settings_service.validate_settings(settings)
            validation_results['other_settings'] = {'valid': valid, 'error': error}
            if not valid:
                return False, error, validation_results
        
        return True, None, validation_results

