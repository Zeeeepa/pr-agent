"""
Settings Service

This module provides a service for managing application settings
"""

import os
import json
import logging
import re
from typing import Dict, Any, Optional, Tuple
from supabase import create_client, Client
import requests

logger = logging.getLogger(__name__)

class SettingsService:
    """
    Service for managing application settings
    """
    
    def __init__(self, settings_file: str = None):
        """
        Initialize the settings service
        
        Args:
            settings_file: Path to the settings file
        """
        self.settings_file = settings_file or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'settings.json')
        self._settings = {}
        self._load_settings()
        self._config_validation_service = None
    
    def _load_settings(self):
        """Load settings from the settings file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    self._settings = json.load(f)
            else:
                self._settings = {}
        except Exception as e:
            logger.error(f"Failed to load settings: {str(e)}")
            self._settings = {}
    
    def _save_settings(self):
        """Save settings to the settings file"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            
            with open(self.settings_file, 'w') as f:
                json.dump(self._settings, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save settings: {str(e)}")
            raise
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value
        
        Args:
            key: Setting key
            default: Default value if setting is not found
            
        Returns:
            Setting value or default
        """
        return self._settings.get(key, default)
    
    def set_setting(self, key: str, value: Any):
        """
        Set a setting value
        
        Args:
            key: Setting key
            value: Setting value
        """
        self._settings[key] = value
        self._save_settings()
    
    async def get_settings(self) -> Dict[str, Any]:
        """
        Get all settings
        
        Returns:
            Dictionary of all settings
        """
        return self._settings.copy()
    
    async def save_settings(self, settings: Dict[str, Any]):
        """
        Save multiple settings
        
        Args:
            settings: Dictionary of settings to save
        """
        self._settings.update(settings)
        self._save_settings()
    
    @property
    def config_validation_service(self):
        """
        Get the config validation service
        
        Returns:
            Config validation service instance
        """
        if self._config_validation_service is None:
            # Import here to avoid circular imports
            from .config_validation_service import ConfigValidationService
            self._config_validation_service = ConfigValidationService(self)
        
        return self._config_validation_service
    
    async def validate_settings(self, settings: Dict[str, str]) -> Tuple[bool, Optional[str]]:
        """
        Validate settings
        
        Args:
            settings: Dict of settings to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate Supabase settings if provided
        if 'SUPABASE_URL' in settings or 'SUPABASE_ANON_KEY' in settings:
            # Both URL and key must be provided together
            if 'SUPABASE_URL' not in settings or 'SUPABASE_ANON_KEY' not in settings:
                return False, "Both Supabase URL and API key must be provided together"
            
            supabase_url = settings['SUPABASE_URL']
            supabase_anon_key = settings['SUPABASE_ANON_KEY']
            
            # Validate URL format
            if not supabase_url or not supabase_url.startswith(('http://', 'https://')):
                return False, "Supabase URL must be a valid URL starting with http:// or https://"
            
            # Validate API key format (should be a non-empty string)
            if not supabase_anon_key or len(supabase_anon_key) < 10:
                return False, "Supabase API key appears to be invalid (too short)"
            
            # Validate key format (should match Supabase key pattern)
            if not re.match(r'^ey[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$', supabase_anon_key):
                return False, "Supabase API key format is invalid. It should be a JWT token."
            
            try:
                # Try to connect to Supabase
                supabase = create_client(supabase_url, supabase_anon_key)
                
                # Test a simple query to verify connection
                result = supabase.table('migrations').select('*').limit(1).execute()
                
                # If we get here, the connection was successful
                # Now check if the required tables exist
                required_tables = ['events', 'projects', 'triggers', 'workflows', 'workflow_runs']
                missing_tables = []
                
                for table in required_tables:
                    try:
                        supabase.table(table).select('*').limit(1).execute()
                    except Exception:
                        missing_tables.append(table)
                
                if missing_tables:
                    # Tables are missing, but connection is valid
                    # This is okay, as migrations will create them
                    logger.info(f"Supabase connection valid, but missing tables: {', '.join(missing_tables)}")
                    return True, None
                
                return True, None
            except Exception as e:
                error_message = str(e)
                # Check for specific error types to provide better feedback
                if "not found" in error_message.lower():
                    return False, "Failed to connect to Supabase: Table not found. Database may need migration."
                elif "unauthorized" in error_message.lower() or "authentication" in error_message.lower():
                    return False, "Failed to connect to Supabase: Invalid API key or unauthorized access."
                elif "network" in error_message.lower() or "connection" in error_message.lower():
                    return False, "Failed to connect to Supabase: Network or connection error."
                else:
                    return False, f"Failed to connect to Supabase: {error_message}"
        
        # Validate GitHub token if provided
        if 'GITHUB_TOKEN' in settings:
            github_token = settings['GITHUB_TOKEN']
            
            # Validate token format (should be a non-empty string)
            if not github_token or len(github_token) < 10:
                return False, "GitHub token appears to be invalid (too short)"
            
            # Validate token format (should match GitHub token pattern)
            if not re.match(r'^(ghp_|github_pat_)[A-Za-z0-9_]+$', github_token):
                return False, "GitHub token format is invalid. It should start with 'ghp_' or 'github_pat_'."
            
            # Validate token with GitHub API
            try:
                headers = {
                    'Authorization': f'token {github_token}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
                
                if response.status_code == 401:
                    return False, "GitHub token validation failed: Invalid or expired token"
                elif response.status_code == 403:
                    return False, "GitHub token validation failed: Token has insufficient permissions"
                elif response.status_code != 200:
                    return False, f"GitHub token validation failed: {response.json().get('message', 'Unknown error')}"
                
                # Check token scopes
                scopes = response.headers.get('X-OAuth-Scopes', '')
                required_scopes = ['repo']
                missing_scopes = [scope for scope in required_scopes if scope not in scopes]
                
                if missing_scopes:
                    return False, f"GitHub token is missing required scopes: {', '.join(missing_scopes)}"
                
                # Get user info for display
                user_data = response.json()
                username = user_data.get('login', 'Unknown')
                logger.info(f"GitHub token validated successfully for user: {username}")
                
                # Test repository access
                try:
                    repo_response = requests.get('https://api.github.com/user/repos?per_page=1', headers=headers, timeout=10)
                    if repo_response.status_code != 200:
                        return False, "GitHub token validation failed: Unable to access repositories"
                except Exception as e:
                    logger.error(f"Error testing repository access: {str(e)}")
                    # Don't fail validation for this, as the token might still be valid
            except requests.exceptions.Timeout:
                return False, "GitHub token validation failed: Connection timed out"
            except requests.exceptions.ConnectionError:
                return False, "GitHub token validation failed: Connection error"
            except Exception as e:
                return False, f"GitHub token validation failed: {str(e)}"
        
        # Use the config validation service to validate other settings
        if hasattr(self, 'config_validation_service'):
            valid, error, _ = await self.config_validation_service.validate_all_settings(settings)
            if not valid:
                return False, error
        
        return True, None
