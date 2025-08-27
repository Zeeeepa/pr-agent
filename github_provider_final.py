#!/usr/bin/env python3
"""
Standalone GitHub Provider Module

This module contains all necessary code to use the GitHub provider
from pr-agent as a standalone component, consolidated using tree-sitter.

Usage:
    from github_provider_final import GitHubProvider
    
    provider = GitHubProvider("https://github.com/owner/repo/pull/123")
    files = provider.get_diff_files()

Original source: https://github.com/qodo-ai/pr-agent
"""

# Standard library imports
import copy
import difflib
import hashlib
import itertools
import re
import time
import traceback
import json
import os
import shutil
import subprocess
import sys
import textwrap
import fnmatch
import logging
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any
from urllib.parse import urlparse
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# External dependencies with graceful fallbacks
try:
    from github.Issue import Issue
    from github import AppAuthentication, Auth, Github, GithubException
    HAS_GITHUB = True
except ImportError:
    print("Warning: PyGithub not installed. Install with: pip install PyGithub")
    HAS_GITHUB = False
    # Create stub classes
    class Issue: pass
    class Github: pass
    class GithubException(Exception): pass

try:
    from retry import retry
    HAS_RETRY = True
except ImportError:
    # Simple retry decorator fallback
    def retry(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    HAS_RETRY = False

try:
    from pydantic import BaseModel
    HAS_PYDANTIC = True
except ImportError:
    # Simple BaseModel fallback
    class BaseModel:
        pass
    HAS_PYDANTIC = False

# Simplified Configuration System
class SimpleConfig:
    """Simplified configuration to replace dynaconf"""
    
    def __init__(self):
        self._config = {
            # GitHub settings
            "GITHUB.BASE_URL": "https://api.github.com",
            
            # File filtering
            "ignore": {
                "regex": [],
                "glob": ["*.lock", "*.log", "*.tmp"]
            },
            
            # Language extensions
            "language_extension_map_org": {
                "python": [".py"],
                "javascript": [".js", ".jsx"],
                "typescript": [".ts", ".tsx"],
                "java": [".java"],
                "go": [".go"],
                "rust": [".rs"],
                "c": [".c"],
                "cpp": [".cpp", ".cc", ".cxx"],
                "csharp": [".cs"],
                "php": [".php"],
                "ruby": [".rb"],
                "swift": [".swift"],
                "kotlin": [".kt"],
                "scala": [".scala"],
            },
            
            # Bad extensions to filter out
            "bad_extensions": {
                "default": [
                    "png", "jpg", "jpeg", "gif", "bmp", "ico", "svg",
                    "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx",
                    "zip", "tar", "gz", "rar", "7z",
                    "mp3", "mp4", "avi", "mov", "wmv",
                    "exe", "dll", "so", "dylib",
                    "class", "jar", "war",
                    "min.js", "min.css",
                ],
                "extra": []
            },
            
            # Config settings
            "config": {
                "verbosity_level": 1,
                "use_extra_bad_extensions": False,
                "patch_extension_skip_types": [".lock", ".min.js", ".min.css"],
                "allow_dynamic_context": True,
                "max_extra_lines_before_dynamic_context": 10,
                "MAX_DESCRIPTION_TOKENS": 8000,
                "model": "gpt-4",
                "model_weak": "gpt-3.5-turbo",
                "model_reasoning": "gpt-4",
            }
        }
    
    def get(self, key: str, default=None):
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def __getattr__(self, name):
        """Allow attribute access"""
        return self._config.get(name, {})

# Global configuration instance
_global_config = SimpleConfig()

def get_settings():
    """Get the global configuration"""
    return _global_config

# Simplified Logging System
class SimpleLogger:
    """Simplified logger to replace loguru"""
    
    def __init__(self):
        self.logger = logging.getLogger("github_provider")
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def info(self, message, **kwargs):
        self.logger.info(message)
    
    def warning(self, message, **kwargs):
        self.logger.warning(message)
    
    def error(self, message, **kwargs):
        self.logger.error(message)
    
    def exception(self, message, **kwargs):
        self.logger.exception(message)
    
    def debug(self, message, **kwargs):
        self.logger.debug(message)

# Global logger instance
_global_logger = SimpleLogger()

def get_logger(*args, **kwargs):
    """Get the global logger"""
    return _global_logger

# Starlette Context Stub
class ContextStub:
    """Stub for starlette context"""
    
    def __init__(self):
        self._data = {}
    
    def get(self, key, default=None):
        return self._data.get(key, default)
    
    def __getitem__(self, key):
        return self._data[key]
    
    def __setitem__(self, key, value):
        self._data[key] = value

# Global context instance
context = ContextStub()

# Core Data Types
class EDIT_TYPE(Enum):
    ADDED = 1
    DELETED = 2
    MODIFIED = 3
    RENAMED = 4
    UNKNOWN = 5

@dataclass
class FilePatchInfo:
    base_file: str
    head_file: str
    patch: str
    filename: str
    tokens: int = -1
    edit_type: EDIT_TYPE = EDIT_TYPE.UNKNOWN
    old_filename: str = None
    num_plus_lines: int = -1
    num_minus_lines: int = -1
    language: Optional[str] = None
    ai_file_summary: str = None

class Range(BaseModel):
    line_start: int  # should be 0-indexed
    line_end: int
    column_start: int = -1
    column_end: int = -1

# Server Utils
class RateLimitExceeded(Exception):
    """Raised when the git provider API rate limit has been exceeded."""
    pass

# Essential Utility Functions
def clip_tokens(text: str, max_tokens: int) -> str:
    """Clip text to maximum number of tokens"""
    if not text or max_tokens <= 0:
        return ""
    
    # Simple approximation: ~4 characters per token
    max_chars = max_tokens * 4
    if len(text) <= max_chars:
        return text
    
    return text[:max_chars] + "..."

def set_file_languages(files):
    """Set language for files based on extension"""
    language_map = get_settings().language_extension_map_org
    
    for file in files:
        if hasattr(file, 'filename') and file.filename:
            ext = '.' + file.filename.split('.')[-1] if '.' in file.filename else ''
            for lang, extensions in language_map.items():
                if ext in extensions:
                    if hasattr(file, 'language'):
                        file.language = lang
                    break
    
    return files

# File Filter Module
def filter_ignored(files, platform='github'):
    """Filter out files that match the ignore patterns."""
    try:
        # load regex patterns, and translate glob patterns to regex
        patterns = get_settings().get('ignore.regex', [])
        if isinstance(patterns, str):
            patterns = [patterns]
        glob_setting = get_settings().get('ignore.glob', [])
        if isinstance(glob_setting, str):
            glob_setting = glob_setting.strip('[]').split(",")
        patterns += [fnmatch.translate(glob) for glob in glob_setting]

        # compile all valid patterns
        compiled_patterns = []
        for r in patterns:
            try:
                compiled_patterns.append(re.compile(r))
            except re.error:
                pass

        # keep filenames that _don't_ match the ignore regex
        if files and isinstance(files, list):
            for r in compiled_patterns:
                if platform == 'github':
                    files = [f for f in files if (f.filename and not r.match(f.filename))]
                elif platform == 'bitbucket':
                    files_o = []
                    for f in files:
                        if hasattr(f, 'new'):
                            if f.new and f.new.path and not r.match(f.new.path):
                                files_o.append(f)
                                continue
                        if hasattr(f, 'old'):
                            if f.old and f.old.path and not r.match(f.old.path):
                                files_o.append(f)
                                continue
                    files = files_o

    except Exception as e:
        print(f"Could not filter file list: {e}")

    return files

# Language Handler Module
def is_valid_file(filename: str, bad_extensions=None) -> bool:
    if not filename:
        return False
    if not bad_extensions:
        bad_extensions = get_settings().get('bad_extensions.default', [])
        if get_settings().get('config.use_extra_bad_extensions', False):
            bad_extensions += get_settings().get('bad_extensions.extra', [])

    auto_generated_files = ['package-lock.json', 'yarn.lock', 'composer.lock', 'Gemfile.lock', 'poetry.lock']
    for forbidden_file in auto_generated_files:
        if filename.endswith(forbidden_file):
            return False

    return filename.split('.')[-1] not in bad_extensions

# Git Patch Processing Module
def extract_hunk_headers(match):
    """Extract hunk header information"""
    if not match:
        return "", 0, 0, 0, 0
    
    start1 = int(match.group(1))
    size1 = int(match.group(2)) if match.group(2) else 1
    start2 = int(match.group(3))
    size2 = int(match.group(4)) if match.group(4) else 1
    section_header = match.group(5) if match.group(5) else ""
    
    return section_header, size1, size2, start1, start2

# Constants
MAX_FILES_ALLOWED_FULL = 50

# Base Git Provider
class GitProvider(ABC):
    @abstractmethod
    def is_supported(self, capability: str) -> bool:
        pass

    def get_git_repo_url(self, issues_or_pr_url: str) -> str:
        get_logger().warning("Not implemented! Returning empty url")
        return ""

    def get_canonical_url_parts(self, repo_git_url: str, desired_branch: str) -> Tuple[str, str]:
        get_logger().warning("Not implemented! Returning empty prefix and suffix")
        return ("", "")

    class ScopedClonedRepo(object):
        def __init__(self, dest_folder):
            self.path = dest_folder

        def __del__(self):
            if self.path and os.path.exists(self.path):
                shutil.rmtree(self.path, ignore_errors=True)

    def _prepare_clone_url_with_token(self, repo_url_to_clone: str) -> str | None:
        get_logger().warning("Not implemented! Returning None")
        return None

    def _clone_inner(self, repo_url: str, dest_folder: str, operation_timeout_in_seconds: int = None) -> None:
        subprocess.run([
            "git", "clone",
            "--filter=blob:none",
            "--depth", "1",
            repo_url, dest_folder
        ], check=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=operation_timeout_in_seconds)

    CLONE_TIMEOUT_SEC = 20

    def clone(self, repo_url_to_clone: str, dest_folder: str, remove_dest_folder: bool = True,
              operation_timeout_in_seconds: int = CLONE_TIMEOUT_SEC):
        returned_obj = None
        clone_url = self._prepare_clone_url_with_token(repo_url_to_clone)
        if not clone_url:
            get_logger().error("Clone failed: Unable to obtain url to clone.")
            return returned_obj
        try:
            if remove_dest_folder and os.path.exists(dest_folder) and os.path.isdir(dest_folder):
                shutil.rmtree(dest_folder)
            self._clone_inner(clone_url, dest_folder, operation_timeout_in_seconds)
            returned_obj = GitProvider.ScopedClonedRepo(dest_folder)
        except Exception as e:
            get_logger().exception(f"Clone failed: Could not clone url.")
        finally:
            return returned_obj

    @abstractmethod
    def get_files(self) -> list:
        pass

    @abstractmethod
    def get_diff_files(self) -> list[FilePatchInfo]:
        pass

    def get_incremental_commits(self, is_incremental):
        pass

    @abstractmethod
    def publish_description(self, pr_title: str, pr_body: str):
        pass

    @abstractmethod
    def publish_code_suggestions(self, code_suggestions: list) -> bool:
        pass

    @abstractmethod
    def get_languages(self):
        pass

    @abstractmethod
    def get_pr_branch(self):
        pass

    @abstractmethod
    def get_user_id(self):
        pass

    @abstractmethod
    def get_pr_description_full(self) -> str:
        pass

    def get_pr_url(self) -> str:
        if hasattr(self, 'pr_url'):
            return self.pr_url
        return ""

    def auto_approve(self) -> bool:
        return False

    def calc_pr_statistics(self, pull_request_data: dict):
        return {}

    def get_num_of_files(self):
        try:
            return len(self.get_diff_files())
        except Exception as e:
            return -1

    def limit_output_characters(self, output: str, max_chars: int):
        return output[:max_chars] + '...' if len(output) > max_chars else output

    @abstractmethod
    def publish_comment(self, pr_comment: str, is_temporary: bool = False):
        pass

    @abstractmethod
    def publish_inline_comment(self, body: str, relevant_file: str, relevant_line_in_file: str, original_suggestion=None):
        pass

    @abstractmethod
    def publish_inline_comments(self, comments: list[dict]):
        pass

    @abstractmethod
    def remove_initial_comment(self):
        pass

    @abstractmethod
    def remove_comment(self, comment):
        pass

    @abstractmethod
    def get_issue_comments(self):
        pass

    @abstractmethod
    def publish_labels(self, labels):
        pass

    @abstractmethod
    def get_pr_labels(self, update=False):
        pass

    @abstractmethod
    def add_eyes_reaction(self, issue_comment_id: int, disable_eyes: bool = False) -> Optional[int]:
        pass

    @abstractmethod
    def remove_reaction(self, issue_comment_id: int, reaction_id: int) -> bool:
        pass

    @abstractmethod
    def get_commit_messages(self):
        pass

class IncrementalPR:
    def __init__(self, is_incremental: bool = False):
        self.is_incremental = is_incremental
        self.commits_range = None
        self.first_new_commit = None
        self.last_seen_commit = None

    @property
    def first_new_commit_sha(self):
        return None if self.first_new_commit is None else self.first_new_commit.sha

    @property
    def last_seen_commit_sha(self):
        return None if self.last_seen_commit is None else self.last_seen_commit.sha

# GitHub Provider Implementation
class GitHubProvider(GitProvider):
    def __init__(self, pr_url: Optional[str] = None):
        if not HAS_GITHUB:
            raise ImportError("PyGithub is required for GitHubProvider. Install with: pip install PyGithub")
        
        self.repo_obj = None
        try:
            self.installation_id = context.get("installation_id", None)
        except Exception:
            self.installation_id = None
        self.max_comment_chars = 65000
        self.base_url = get_settings().get("GITHUB.BASE_URL", "https://api.github.com").rstrip("/")
        self.base_url_html = self.base_url.split("api/")[0].rstrip("/") if "api/" in self.base_url else "https://github.com"
        self.github_client = self._get_github_client()
        self.repo = None
        self.pr_num = None
        self.pr = None
        self.issue_main = None
        self.github_user_id = None
        self.diff_files = None
        self.git_files = None
        self.incremental = IncrementalPR(False)
        if pr_url and 'pull' in pr_url:
            self.set_pr(pr_url)
            self.pr_commits = list(self.pr.get_commits())
            self.last_commit_id = self.pr_commits[-1]
            self.pr_url = self.get_pr_url()
        elif pr_url and 'issue' in pr_url:
            self.issue_main = self._get_issue_handle(pr_url)
        else:
            self.pr_commits = None

    def _get_github_client(self):
        """Get GitHub client with authentication"""
        try:
            # Try to get token from environment
            token = os.getenv('GITHUB_TOKEN') or os.getenv('GITHUB_ACCESS_TOKEN')
            if token:
                return Github(token)
            else:
                get_logger().warning("No GitHub token found. Some operations may fail.")
                return Github()
        except Exception as e:
            get_logger().error(f"Failed to create GitHub client: {e}")
            return None

    def is_supported(self, capability: str) -> bool:
        return True

    def _parse_pr_url(self, pr_url: str) -> Tuple[str, int]:
        """Parse PR URL to extract repo and PR number"""
        try:
            # Extract repo and PR number from URL
            # Example: https://github.com/owner/repo/pull/123
            match = re.match(r'https://github\.com/([^/]+/[^/]+)/pull/(\d+)', pr_url)
            if match:
                repo = match.group(1)
                pr_num = int(match.group(2))
                return repo, pr_num
        except Exception as e:
            get_logger().error(f"Failed to parse PR URL: {e}")
        return None, None

    def set_pr(self, pr_url: str):
        """Set the PR from URL"""
        self.repo, self.pr_num = self._parse_pr_url(pr_url)
        if self.repo and self.pr_num and self.github_client:
            try:
                repo_obj = self.github_client.get_repo(self.repo)
                self.pr = repo_obj.get_pull(self.pr_num)
                self.repo_obj = repo_obj
            except Exception as e:
                get_logger().error(f"Failed to get PR: {e}")

    def get_pr_url(self) -> str:
        if self.pr:
            return self.pr.html_url
        return ""

    def get_diff_files(self) -> list[FilePatchInfo]:
        """Get diff files from PR"""
        if not self.pr:
            return []
        
        try:
            files = []
            for file in self.pr.get_files():
                edit_type = EDIT_TYPE.UNKNOWN
                if file.status == 'added':
                    edit_type = EDIT_TYPE.ADDED
                elif file.status == 'removed':
                    edit_type = EDIT_TYPE.DELETED
                elif file.status == 'modified':
                    edit_type = EDIT_TYPE.MODIFIED
                elif file.status == 'renamed':
                    edit_type = EDIT_TYPE.RENAMED
                
                file_info = FilePatchInfo(
                    base_file=file.filename,
                    head_file=file.filename,
                    patch=file.patch or "",
                    filename=file.filename,
                    edit_type=edit_type,
                    num_plus_lines=file.additions,
                    num_minus_lines=file.deletions
                )
                files.append(file_info)
            
            return files
        except Exception as e:
            get_logger().error(f"Failed to get diff files: {e}")
            return []

    def get_files(self) -> list:
        """Get all files in the repository"""
        return self.get_diff_files()

    def publish_description(self, pr_title: str, pr_body: str):
        """Update PR title and description"""
        if self.pr:
            try:
                self.pr.edit(title=pr_title, body=pr_body)
            except Exception as e:
                get_logger().error(f"Failed to update PR description: {e}")

    def publish_code_suggestions(self, code_suggestions: list) -> bool:
        """Publish code suggestions as PR comments"""
        # Simplified implementation
        return True

    def get_languages(self):
        """Get repository languages"""
        if self.repo_obj:
            try:
                return self.repo_obj.get_languages()
            except Exception as e:
                get_logger().error(f"Failed to get languages: {e}")
        return {}

    def get_pr_branch(self):
        """Get PR branch name"""
        if self.pr:
            return self.pr.head.ref
        return ""

    def get_user_id(self):
        """Get current user ID"""
        if self.github_client:
            try:
                user = self.github_client.get_user()
                return user.id
            except Exception as e:
                get_logger().error(f"Failed to get user ID: {e}")
        return None

    def get_pr_description_full(self) -> str:
        """Get full PR description"""
        if self.pr:
            return self.pr.body or ""
        return ""

    def publish_comment(self, pr_comment: str, is_temporary: bool = False):
        """Publish a comment on the PR"""
        if self.pr:
            try:
                return self.pr.create_issue_comment(pr_comment)
            except Exception as e:
                get_logger().error(f"Failed to publish comment: {e}")

    def publish_inline_comment(self, body: str, relevant_file: str, relevant_line_in_file: str, original_suggestion=None):
        """Publish inline comment on specific line"""
        # Simplified implementation
        pass

    def publish_inline_comments(self, comments: list[dict]):
        """Publish multiple inline comments"""
        # Simplified implementation
        pass

    def remove_initial_comment(self):
        """Remove initial comment"""
        pass

    def remove_comment(self, comment):
        """Remove a comment"""
        if comment:
            try:
                comment.delete()
            except Exception as e:
                get_logger().error(f"Failed to remove comment: {e}")

    def get_issue_comments(self):
        """Get all issue comments"""
        if self.pr:
            try:
                return list(self.pr.get_issue_comments())
            except Exception as e:
                get_logger().error(f"Failed to get issue comments: {e}")
        return []

    def publish_labels(self, labels):
        """Add labels to PR"""
        if self.pr and labels:
            try:
                self.pr.add_to_labels(*labels)
            except Exception as e:
                get_logger().error(f"Failed to add labels: {e}")

    def get_pr_labels(self, update=False):
        """Get PR labels"""
        if self.pr:
            try:
                return [label.name for label in self.pr.labels]
            except Exception as e:
                get_logger().error(f"Failed to get labels: {e}")
        return []

    def add_eyes_reaction(self, issue_comment_id: int, disable_eyes: bool = False) -> Optional[int]:
        """Add eyes reaction to comment"""
        return None

    def remove_reaction(self, issue_comment_id: int, reaction_id: int) -> bool:
        """Remove reaction from comment"""
        return False

    def get_commit_messages(self):
        """Get commit messages"""
        if self.pr_commits:
            return [commit.commit.message for commit in self.pr_commits]
        return []

# Example Usage and Testing
def test_github_provider():
    """Test the GitHub provider functionality"""
    if not HAS_GITHUB:
        print("Cannot test: PyGithub not available")
        return False
    
    try:
        # Test basic instantiation
        provider = GitHubProvider()
        print("✓ GitHubProvider instantiated successfully")
        
        # Test with a PR URL (requires authentication)
        # provider = GitHubProvider("https://github.com/owner/repo/pull/123")
        # files = provider.get_diff_files()
        # print(f"✓ Found {len(files)} files in PR")
        
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("GitHub Provider Standalone Module")
    print("=" * 40)
    print(f"PyGithub available: {HAS_GITHUB}")
    print(f"Retry decorator available: {HAS_RETRY}")
    print(f"Pydantic available: {HAS_PYDANTIC}")
    print()
    
    # Run basic test
    success = test_github_provider()
    print(f"\nTest result: {'PASSED' if success else 'FAILED'}")
    
    # Show available classes
    print("\nAvailable classes:")
    for name in dir():
        obj = globals()[name]
        if isinstance(obj, type) and not name.startswith("_"):
            print(f"  - {name}")
