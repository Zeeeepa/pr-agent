"""
Settings service for ExeServer.

This module provides a service for managing application settings.
"""

import os
import json
import re
from typing import Dict, Any, Optional, Tuple
from supabase import create_client, Client
import requests

class SettingsService:
    """
    Service for managing application settings
    """
    def __init__(self):
        """Initialize the settings service"""
        self.settings = {}
        self.settings_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'settings.json')
        self._load_settings()
    
    def _load_settings(self):
        """Load settings from file if it exists"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
            except Exception:
                self.settings = {}
    
    def _save_settings_to_file(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f)
        except Exception:
            pass
    
    async def get_settings(self) -> Dict[str, str]:
        """
        Get all settings
        
        Returns:
            Dict of settings
        """
        # Return a copy of settings with sensitive information masked
        masked_settings = self.settings.copy()
        for key in masked_settings:
            if any(sensitive in key.upper() for sensitive in ['TOKEN', 'KEY', 'SECRET', 'PASSWORD']):
                if masked_settings[key]:
                    masked_settings[key] = f"{masked_settings[key][:4]}{'*' * (len(masked_settings[key]) - 8)}{masked_settings[key][-4:]}" if len(masked_settings[key]) > 8 else "********"
        return masked_settings
    
    async def save_settings(self, settings: Dict[str, str]) -> bool:
        """
        Save settings
        
        Args:
            settings: Dict of settings to save
            
        Returns:
            True if successful
        """
        # Update settings
        self.settings.update(settings)
        
        # Save to file
        self._save_settings_to_file()
        
        return True
    
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
            
            try:
                # Try to connect to Supabase
                supabase = create_client(supabase_url, supabase_anon_key)
                # Test a simple query
                supabase.table('events').select('*').limit(1).execute()
            except Exception as e:
                return False, f"Failed to connect to Supabase: {str(e)}"
        
        # Validate GitHub token if provided
        if 'GITHUB_TOKEN' in settings:
            github_token = settings['GITHUB_TOKEN']
            
            # Validate token format (should be a non-empty string)
            if not github_token or len(github_token) < 10:
                return False, "GitHub token appears to be invalid (too short)"
            
            # Validate token with GitHub API
            try:
                headers = {
                    'Authorization': f'token {github_token}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                response = requests.get('https://api.github.com/user', headers=headers)
                
                if response.status_code != 200:
                    return False, f"GitHub token validation failed: {response.json().get('message', 'Unknown error')}"
            except Exception as e:
                return False, f"GitHub token validation failed: {str(e)}"
        
        return True, None
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value
        
        Args:
            key: Setting key
            default: Default value if not found
            
        Returns:
            Setting value or default
        """
        return self.settings.get(key, default)
