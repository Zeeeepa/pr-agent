"""
Settings service for ExeServer.

This module provides a service for managing application settings.
"""

import os
import json
from typing import Dict, Any, Optional
from supabase import create_client, Client
import requests
from github import Github, GithubException, BadCredentialsException, RateLimitExceededException

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
        validation_results = {}
        
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
                validation_results['supabase'] = "valid"
            except Exception as e:
                error_message = str(e)
                # Check for specific Supabase error types
                if "404" in error_message:
                    raise Exception("Supabase URL is invalid or the table 'events' does not exist")
                elif "401" in error_message or "403" in error_message:
                    raise Exception("Supabase API key is invalid or lacks necessary permissions")
                else:
                    raise Exception(f"Failed to connect to Supabase: {error_message}")
        
        # Validate GitHub token if provided
        if 'GITHUB_TOKEN' in settings:
            github_token = settings['GITHUB_TOKEN']
            
            if not github_token:
                raise Exception("GitHub token is required")
            
            try:
                # Create a GitHub client with the token
                github = Github(github_token)
                
                # Test the token by getting the authenticated user
                user = github.get_user()
                user_data = {
                    "login": user.login,
                    "name": user.name,
                    "email": user.email
                }
                
                # Test rate limit to ensure token is valid
                rate_limit = github.get_rate_limit()
                
                validation_results['github'] = {
                    "status": "valid",
                    "user": user_data,
                    "rate_limit": {
                        "remaining": rate_limit.core.remaining,
                        "limit": rate_limit.core.limit,
                        "reset": str(rate_limit.core.reset)
                    }
                }
            except BadCredentialsException:
                raise Exception("GitHub token is invalid. Please check your token and try again.")
            except RateLimitExceededException:
                raise Exception("GitHub API rate limit exceeded. Please try again later.")
            except GithubException as e:
                if e.status == 401:
                    raise Exception("GitHub token is invalid or expired. Please generate a new token.")
                elif e.status == 403:
                    raise Exception("GitHub token lacks necessary permissions. Ensure it has the required scopes.")
                else:
                    raise Exception(f"GitHub API error: {e.data.get('message', str(e))}")
            except Exception as e:
                raise Exception(f"Failed to validate GitHub token: {str(e)}")
        
        return validation_results
    
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
