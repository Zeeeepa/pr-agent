"""
Settings service for ExeServer.

This module provides a service for managing application settings.
"""

import os
import json
from typing import Dict, Any, Optional
from supabase import create_client, Client

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
        return self.settings
    
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
    
    async def validate_settings(self, settings: Dict[str, str]) -> bool:
        """
        Validate settings
        
        Args:
            settings: Dict of settings to validate
            
        Returns:
            True if valid
            
        Raises:
            Exception: If validation fails
        """
        # Validate Supabase settings if provided
        if 'SUPABASE_URL' in settings and 'SUPABASE_ANON_KEY' in settings:
            supabase_url = settings['SUPABASE_URL']
            supabase_anon_key = settings['SUPABASE_ANON_KEY']
            
            if not supabase_url or not supabase_anon_key:
                raise Exception("Supabase URL and API key are required")
            
            try:
                # Try to connect to Supabase
                supabase = create_client(supabase_url, supabase_anon_key)
                # Test a simple query
                supabase.table('events').select('*').limit(1).execute()
            except Exception as e:
                raise Exception(f"Failed to connect to Supabase: {str(e)}")
        
        # Validate GitHub token if provided
        if 'GITHUB_TOKEN' in settings:
            github_token = settings['GITHUB_TOKEN']
            
            if not github_token:
                raise Exception("GitHub token is required")
            
            # Additional GitHub token validation could be added here
        
        return True
    
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
