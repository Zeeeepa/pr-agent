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
            
            # Check if the key follows the expected format (eyJ...)
            if not supabase_anon_key.startswith('eyJ'):
                return False, "Supabase API key appears to be invalid (incorrect format)"
            
            try:
                # Try to connect to Supabase
                supabase = create_client(supabase_url, supabase_anon_key)
                
                # Test a simple query to verify connection
                try:
                    result = supabase.table('migrations').select('*').limit(1).execute()
                    # If we get here, the connection was successful
                    return True, None
                except Exception as query_error:
                    error_str = str(query_error).lower()
                    
                    # Check if this is a "table doesn't exist" error, which is okay
                    # as migrations will create it
                    if "not found" in error_str and "relation" in error_str:
                        # This is expected for a new database
                        logger.info("Supabase connection valid, but migrations table not found")
                        return True, None
                    else:
                        # This is an unexpected error
                        return False, f"Failed to query Supabase: {str(query_error)}"
                
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
            
            # Check if the token follows the expected format (ghp_, gho_, ghu_, ghs_, or ghr_)
            if not re.match(r'^(ghp_|gho_|ghu_|ghs_|ghr_)', github_token):
                return False, "GitHub token appears to be invalid (incorrect format). Personal access tokens should start with ghp_, gho_, ghu_, ghs_, or ghr_."
            
            # Validate token with GitHub API
            try:
                headers = {
                    'Authorization': f'token {github_token}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                response = requests.get('https://api.github.com/user', headers=headers)
                
                if response.status_code == 200:
                    return True, None
                elif response.status_code == 401:
                    return False, "GitHub token validation failed: Unauthorized. The token may be invalid or expired."
                elif response.status_code == 403:
                    return False, "GitHub token validation failed: Forbidden. The token may not have the required permissions."
                else:
                    return False, f"GitHub token validation failed: {response.json().get('message', 'Unknown error')}"
            except Exception as e:
                return False, f"GitHub token validation failed: {str(e)}"
        
        return True, None
        
    async def validate_supabase_credentials(self, url: str, key: str) -> Tuple[bool, Optional[str]]:
        """
        Validate Supabase credentials
        
        Args:
            url: Supabase URL
            key: Supabase API key
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Validate URL format
            if not url or not url.startswith(('http://', 'https://')):
                return False, "Supabase URL must be a valid URL starting with http:// or https://"
            
            # Validate API key format
            if not key or len(key) < 10:
                return False, "Supabase API key appears to be invalid (too short)"
            
            # Try to connect to Supabase
            supabase = create_client(url, key)
            
            # Test a simple query to verify connection
            try:
                supabase.table('migrations').select('*').limit(1).execute()
                return True, None
            except Exception as query_error:
                error_str = str(query_error).lower()
                
                # Check if this is a "table doesn't exist" error, which is okay
                if "not found" in error_str and "relation" in error_str:
                    return True, None
                else:
                    return False, f"Failed to query Supabase: {str(query_error)}"
                
        except Exception as e:
            return False, f"Failed to connect to Supabase: {str(e)}"
            
    async def validate_github_token(self, token: str) -> Tuple[bool, Optional[str]]:
        """
        Validate GitHub token
        
        Args:
            token: GitHub token
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Validate token format
            if not token or len(token) < 10:
                return False, "GitHub token appears to be invalid (too short)"
            
            # Validate token with GitHub API
            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            response = requests.get('https://api.github.com/user', headers=headers)
            
            if response.status_code == 200:
                return True, None
            elif response.status_code == 401:
                return False, "GitHub token validation failed: Unauthorized. The token may be invalid or expired."
            elif response.status_code == 403:
                return False, "GitHub token validation failed: Forbidden. The token may not have the required permissions."
            else:
                return False, f"GitHub token validation failed: {response.json().get('message', 'Unknown error')}"
        except Exception as e:
            return False, f"GitHub token validation failed: {str(e)}"
