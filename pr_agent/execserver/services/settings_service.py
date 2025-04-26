"""
Settings service for ExeServer.

This module provides a service for managing application settings.
"""

import os
import json
import requests
from typing import Dict, Any, Optional
from supabase import create_client, Client
from github import Github

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
    
    async def validate_github_token(self, token: str) -> bool:
        """
        Validate GitHub token
        
        Args:
            token: GitHub token to validate
            
        Returns:
            True if valid
            
        Raises:
            Exception: If validation fails
        """
        if not token:
            raise Exception("GitHub token is required")
        
        try:
            # Try to connect to GitHub API
            g = Github(token)
            
            # Test user access
            user = g.get_user()
            user_login = user.login
            
            # Check rate limit to ensure token is valid
            rate_limit = g.get_rate_limit()
            core_rate_limit = rate_limit.core
            
            # Check if rate limit is too low (less than 10% remaining)
            if core_rate_limit.remaining < (core_rate_limit.limit * 0.1):
                raise Exception(f"GitHub API rate limit is too low: {core_rate_limit.remaining}/{core_rate_limit.limit} remaining")
            
            # Try to list repositories to verify permissions
            repos = list(user.get_repos(limit=1))
            
            return True
        except Exception as e:
            raise Exception(f"GitHub token validation failed: {str(e)}")
    
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
            await self.validate_github_token(github_token)
        
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
