import os
from dotenv import load_dotenv
from pr_agent.config_loader import get_settings

# Load environment variables from .env file
load_dotenv()

# GitHub configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_APP_ID = os.getenv("GITHUB_APP_ID")
GITHUB_APP_PRIVATE_KEY = os.getenv("GITHUB_APP_PRIVATE_KEY")
GITHUB_APP_INSTALLATION_ID = os.getenv("GITHUB_APP_INSTALLATION_ID")

# Database configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# PR-Agent configuration
def get_pr_agent_settings():
    """Get settings from PR-Agent configuration"""
    return get_settings()

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
    from pr_agent.servers.github_action_runner import get_setting_or_env as pr_agent_get_setting
    return pr_agent_get_setting(key, default)

# UI configuration
UI_PORT = int(os.getenv("UI_PORT", "8000"))
API_PORT = int(os.getenv("API_PORT", "8001"))

# Notification configuration
ENABLE_NOTIFICATIONS = os.getenv("ENABLE_NOTIFICATIONS", "False").lower() == "true"
