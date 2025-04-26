from os.path import abspath, dirname, join
from pathlib import Path
from typing import Any, Dict, Optional, Union
import os
from functools import lru_cache

from dynaconf import Dynaconf
from starlette_context import context

PR_AGENT_TOML_KEY = 'pr-agent'

current_dir = dirname(abspath(__file__))
global_settings = Dynaconf(
    envvar_prefix=False,
    merge_enabled=True,
    settings_files=[join(current_dir, f) for f in [
        "settings/configuration.toml",
        "settings/ignore.toml",
        "settings/language_extensions.toml",
        "settings/pr_reviewer_prompts.toml",
        "settings/pr_questions_prompts.toml",
        "settings/pr_line_questions_prompts.toml",
        "settings/pr_description_prompts.toml",
        "settings/code_suggestions/pr_code_suggestions_prompts.toml",
        "settings/code_suggestions/pr_code_suggestions_prompts_not_decoupled.toml",
        "settings/code_suggestions/pr_code_suggestions_reflect_prompts.toml",
        "settings/pr_information_from_user_prompts.toml",
        "settings/pr_update_changelog_prompts.toml",
        "settings/pr_custom_labels.toml",
        "settings/pr_add_docs.toml",
        "settings/custom_labels.toml",
        "settings/pr_help_prompts.toml",
        "settings/pr_help_docs_prompts.toml",
        "settings/pr_help_docs_headings_prompts.toml",
        "settings/.secrets.toml",
        "settings_prod/.secrets.toml",
    ]]
)


def get_settings(use_context=False):
    """
    Retrieves the current settings.

    This function attempts to fetch the settings from the starlette_context's context object. If it fails,
    it defaults to the global settings defined outside of this function.

    Returns:
        Dynaconf: The current settings object, either from the context or the global default.
    """
    try:
        return context["settings"]
    except Exception:
        return global_settings


# Add local configuration from pyproject.toml of the project being reviewed
def _find_repository_root() -> Optional[Path]:
    """
    Identify project root directory by recursively searching for the .git directory in the parent directories.
    """
    cwd = Path.cwd().resolve()
    no_way_up = False
    while not no_way_up:
        no_way_up = cwd == cwd.parent
        if (cwd / ".git").is_dir():
            return cwd
        cwd = cwd.parent
    return None


def _find_pyproject() -> Optional[Path]:
    """
    Search for file pyproject.toml in the repository root.
    """
    repo_root = _find_repository_root()
    if repo_root:
        pyproject = repo_root / "pyproject.toml"
        return pyproject if pyproject.is_file() else None
    return None


pyproject_path = _find_pyproject()
if pyproject_path is not None:
    get_settings().load_file(pyproject_path, env=f'tool.{PR_AGENT_TOML_KEY}')


class ConfigManager:
    """
    Centralized configuration management system for PR-Agent.
    
    This class provides a unified interface for accessing configuration settings
    from various sources with a clear precedence order:
    1. Environment variables
    2. Local configuration files (.pr_agent.toml)
    3. Global configuration files (settings/*.toml)
    4. Default values
    
    Usage:
        config = ConfigManager()
        github_token = config.get("GITHUB_TOKEN")
        debug_mode = config.get("DEBUG", False)
    """
    
    def __init__(self):
        """Initialize the configuration manager."""
        self._settings = get_settings()
        
    @lru_cache(maxsize=128)
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value with proper precedence.
        
        Args:
            key: The configuration key to look up
            default: Default value if the key is not found
            
        Returns:
            The configuration value or the default
        """
        # First check environment variables (highest precedence)
        env_value = os.getenv(key)
        if env_value is not None:
            return self._convert_value(env_value)
            
        # Then check settings from configuration files
        try:
            return self._settings.get(key, default)
        except Exception:
            return default
    
    def _convert_value(self, value: str) -> Union[str, int, float, bool]:
        """
        Convert string values to appropriate types.
        
        Args:
            value: The string value to convert
            
        Returns:
            The converted value
        """
        # Try to convert to boolean
        if value.lower() in ('true', 'yes', '1'):
            return True
        if value.lower() in ('false', 'no', '0'):
            return False
            
        # Try to convert to number
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            # Return as string if not a number
            return value
            
    def get_dict(self, prefix: str) -> Dict[str, Any]:
        """
        Get all configuration values with a specific prefix.
        
        Args:
            prefix: The prefix to filter configuration keys
            
        Returns:
            Dictionary of configuration values
        """
        result = {}
        
        # Get from environment variables
        for key, value in os.environ.items():
            if key.startswith(prefix):
                result[key] = self._convert_value(value)
                
        # Get from settings
        try:
            settings_dict = self._settings.as_dict()
            for key, value in settings_dict.items():
                if key.startswith(prefix) and key not in result:
                    result[key] = value
        except Exception:
            pass
            
        return result
        
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value at runtime.
        
        Args:
            key: The configuration key
            value: The value to set
        """
        self._settings.set(key, value)
        
        # Clear the cache when setting a new value
        self.get.cache_clear()


# Create a singleton instance
config_manager = ConfigManager()
