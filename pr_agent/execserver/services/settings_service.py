"""
Settings service for ExeServer.

This module provides a service for managing application settings.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Tuple
from supabase import create_client, Client

logger = logging.getLogger(__name__)

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
            except Exception as e:
                logger.error(f"Failed to load settings: {str(e)}")
                self.settings = {}
    
    def _save_settings_to_file(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f)
        except Exception as e:
            logger.error(f"Failed to save settings to file: {str(e)}")
    
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
    
    async def validate_settings(self, settings: Dict[str, str]) -> Tuple[bool, Optional[str]]:
        """
        Validate settings
        
        Args:
            settings: Dict of settings to validate
            
        Returns:
            Tuple of (valid, error_message)
        """
        # Validate Supabase settings if provided
        if 'SUPABASE_URL' in settings and 'SUPABASE_ANON_KEY' in settings:
            supabase_url = settings['SUPABASE_URL']
            supabase_anon_key = settings['SUPABASE_ANON_KEY']
            
            if not supabase_url or not supabase_anon_key:
                return False, "Supabase URL and API key are required"
            
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
            
            if not github_token:
                return False, "GitHub token is required"
            
            # Additional GitHub token validation could be added here
            # For now, we just check that it's not empty
        
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
