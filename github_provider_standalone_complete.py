#!/usr/bin/env python3
"""
Standalone GitHub Provider Module

This module contains all necessary code to use the GitHub provider
from pr-agent as a standalone component.

Usage:
    from github_provider_standalone import GitHubProvider
    
    provider = GitHubProvider("https://github.com/owner/repo/pull/123")
    files = provider.get_diff_files()

Original source: https://github.com/qodo-ai/pr-agent
"""

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
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any
from urllib.parse import urlparse
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import fnmatch
import logging
from pathlib import Path

# External dependencies (with graceful fallbacks)
try:
    from github.Issue import Issue
    from github import AppAuthentication, Auth, Github, GithubException
    HAS_GITHUB = True
except ImportError:
    print("Warning: PyGithub not installed. Install with: pip install PyGithub")
    HAS_GITHUB = False

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
import logging
import sys

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
from dataclasses import dataclass
from enum import Enum
from typing import Optional


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


# Essential Utility Functions
def get_model(model_type: str = "model_weak") -> str:
    if model_type == "model_weak" and get_settings().get("config.model_weak"):
        return get_settings().config.model_weak
    elif model_type == "model_reasoning" and get_settings().get("config.model_reasoning"):
        return get_settings().config.model_reasoning
    return get_settings().config.model

# File Filter Module
import fnmatch
import re



def filter_ignored(files, platform = 'github'):
    """
    Filter out files that match the ignore patterns.
    """

    try:
        # load regex patterns, and translate glob patterns to regex
        patterns = get_settings().ignore.regex
        if isinstance(patterns, str):
            patterns = [patterns]
        glob_setting = get_settings().ignore.glob
        if isinstance(glob_setting, str):  # --ignore.glob=[.*utils.py], --ignore.glob=.*utils.py
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
                    # files = [f for f in files if (f.new.path and not r.match(f.new.path))]
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
                elif platform == 'gitlab':
                    # files = [f for f in files if (f['new_path'] and not r.match(f['new_path']))]
                    files_o = []
                    for f in files:
                        if 'new_path' in f and f['new_path'] and not r.match(f['new_path']):
                            files_o.append(f)
                            continue
                        if 'old_path' in f and f['old_path'] and not r.match(f['old_path']):
                            files_o.append(f)
                            continue
                    files = files_o
                elif platform == 'azure':
                    files = [f for f in files if not r.match(f)]
                elif platform == 'gitea':
                    files = [f for f in files if not r.match(f.get("filename", ""))]


    except Exception as e:
        print(f"Could not filter file list: {e}")

    return files


# Git Patch Processing Module
from __future__ import annotations

import re
import traceback



def extend_patch(original_file_str, patch_str, patch_extra_lines_before=0,
                 patch_extra_lines_after=0, filename: str = "", new_file_str="") -> str:
    if not patch_str or (patch_extra_lines_before == 0 and patch_extra_lines_after == 0) or not original_file_str:
        return patch_str

    original_file_str = decode_if_bytes(original_file_str)
    new_file_str = decode_if_bytes(new_file_str)
    if not original_file_str:
        return patch_str

    if should_skip_patch(filename):
        return patch_str

    try:
        extended_patch_str = process_patch_lines(patch_str, original_file_str,
                                                 patch_extra_lines_before, patch_extra_lines_after, new_file_str)
    except Exception as e:
        get_logger().warning(f"Failed to extend patch: {e}", artifact={"traceback": traceback.format_exc()})
        return patch_str

    return extended_patch_str


def decode_if_bytes(original_file_str):
    if isinstance(original_file_str, (bytes, bytearray)):
        try:
            return original_file_str.decode('utf-8')
        except UnicodeDecodeError:
            encodings_to_try = ['iso-8859-1', 'latin-1', 'ascii', 'utf-16']
            for encoding in encodings_to_try:
                try:
                    return original_file_str.decode(encoding)
                except UnicodeDecodeError:
                    continue
            return ""
    return original_file_str


def should_skip_patch(filename):
    patch_extension_skip_types = get_settings().config.patch_extension_skip_types
    if patch_extension_skip_types and filename:
        return any(filename.endswith(skip_type) for skip_type in patch_extension_skip_types)
    return False


def process_patch_lines(patch_str, original_file_str, patch_extra_lines_before, patch_extra_lines_after, new_file_str=""):
    allow_dynamic_context = get_settings().config.allow_dynamic_context
    patch_extra_lines_before_dynamic = get_settings().config.max_extra_lines_before_dynamic_context

    file_original_lines = original_file_str.splitlines()
    file_new_lines = new_file_str.splitlines() if new_file_str else []
    len_original_lines = len(file_original_lines)
    patch_lines = patch_str.splitlines()
    extended_patch_lines = []

    is_valid_hunk = True
    start1, size1, start2, size2 = -1, -1, -1, -1
    RE_HUNK_HEADER = re.compile(
        r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@[ ]?(.*)")
    try:
        for i,line in enumerate(patch_lines):
            if line.startswith('@@'):
                match = RE_HUNK_HEADER.match(line)
                # identify hunk header
                if match:
                    # finish processing previous hunk
                    if is_valid_hunk and (start1 != -1 and patch_extra_lines_after > 0):
                        delta_lines_original = [f' {line}' for line in file_original_lines[start1 + size1 - 1:start1 + size1 - 1 + patch_extra_lines_after]]
                        extended_patch_lines.extend(delta_lines_original)

                    section_header, size1, size2, start1, start2 = extract_hunk_headers(match)

                    is_valid_hunk = check_if_hunk_lines_matches_to_file(i, file_original_lines, patch_lines, start1)

                    if is_valid_hunk and (patch_extra_lines_before > 0 or patch_extra_lines_after > 0):
                        def _calc_context_limits(patch_lines_before):
                            extended_start1 = max(1, start1 - patch_lines_before)
                            extended_size1 = size1 + (start1 - extended_start1) + patch_extra_lines_after
                            extended_start2 = max(1, start2 - patch_lines_before)
                            extended_size2 = size2 + (start2 - extended_start2) + patch_extra_lines_after
                            if extended_start1 - 1 + extended_size1 > len_original_lines:
                                # we cannot extend beyond the original file
                                delta_cap = extended_start1 - 1 + extended_size1 - len_original_lines
                                extended_size1 = max(extended_size1 - delta_cap, size1)
                                extended_size2 = max(extended_size2 - delta_cap, size2)
                            return extended_start1, extended_size1, extended_start2, extended_size2

                        if allow_dynamic_context and file_new_lines:
                            extended_start1, extended_size1, extended_start2, extended_size2 = \
                                _calc_context_limits(patch_extra_lines_before_dynamic)

                            lines_before_original = file_original_lines[extended_start1 - 1:start1 - 1]
                            lines_before_new = file_new_lines[extended_start2 - 1:start2 - 1]
                            found_header = False
                            for i, line in enumerate(lines_before_original):
                                if section_header in line:
                                    # Update start and size in one line each
                                    extended_start1, extended_start2 = extended_start1 + i, extended_start2 + i
                                    extended_size1, extended_size2 = extended_size1 - i, extended_size2 - i
                                    lines_before_original_dynamic_context = lines_before_original[i:]
                                    lines_before_new_dynamic_context = lines_before_new[i:]
                                    if lines_before_original_dynamic_context == lines_before_new_dynamic_context:
                                        # get_logger().debug(f"found dynamic context match for section header: {section_header}")
                                        found_header = True
                                        section_header = ''
                                    else:
                                        pass  # its ok to be here. We cant apply dynamic context if the lines are different if 'old' and 'new' hunks
                                    break

                            if not found_header:
                                # get_logger().debug(f"Section header not found in the extra lines before the hunk")
                                extended_start1, extended_size1, extended_start2, extended_size2 = \
                                    _calc_context_limits(patch_extra_lines_before)
                        else:
                            extended_start1, extended_size1, extended_start2, extended_size2 = \
                                _calc_context_limits(patch_extra_lines_before)

                        # check if extra lines before hunk are different in original and new file
                        delta_lines_original = [f' {line}' for line in file_original_lines[extended_start1 - 1:start1 - 1]]
                        if file_new_lines:
                            delta_lines_new = [f' {line}' for line in file_new_lines[extended_start2 - 1:start2 - 1]]
                            if delta_lines_original != delta_lines_new:
                                found_mini_match = False
                                for i in range(len(delta_lines_original)):
                                    if delta_lines_original[i:] == delta_lines_new[i:]:
                                        delta_lines_original = delta_lines_original[i:]
                                        delta_lines_new = delta_lines_new[i:]
                                        extended_start1 += i
                                        extended_size1 -= i
                                        extended_start2 += i
                                        extended_size2 -= i
                                        found_mini_match = True
                                        break
                                if not found_mini_match:
                                    extended_start1 = start1
                                    extended_size1 = size1
                                    extended_start2 = start2
                                    extended_size2 = size2
                                    delta_lines_original = []
                                    # get_logger().debug(f"Extra lines before hunk are different in original and new file",
                                    #                    artifact={"delta_lines_original": delta_lines_original,
                                    #                              "delta_lines_new": delta_lines_new})

                        #  logic to remove section header if its in the extra delta lines (in dynamic context, this is also done)
                        if section_header and not allow_dynamic_context:
                            for line in delta_lines_original:
                                if section_header in line:
                                    section_header = ''  # remove section header if it is in the extra delta lines
                                    break
                    else:
                        extended_start1 = start1
                        extended_size1 = size1
                        extended_start2 = start2
                        extended_size2 = size2
                        delta_lines_original = []
                    extended_patch_lines.append('')
                    extended_patch_lines.append(
                        f'@@ -{extended_start1},{extended_size1} '
                        f'+{extended_start2},{extended_size2} @@ {section_header}')
                    extended_patch_lines.extend(delta_lines_original)  # one to zero based
                    continue
            extended_patch_lines.append(line)
    except Exception as e:
        get_logger().warning(f"Failed to extend patch: {e}", artifact={"traceback": traceback.format_exc()})
        return patch_str

    # finish processing last hunk
    if start1 != -1 and patch_extra_lines_after > 0 and is_valid_hunk:
        delta_lines_original = file_original_lines[start1 + size1 - 1:start1 + size1 - 1 + patch_extra_lines_after]
        # add space at the beginning of each extra line
        delta_lines_original = [f' {line}' for line in delta_lines_original]
        extended_patch_lines.extend(delta_lines_original)

    extended_patch_str = '\n'.join(extended_patch_lines)
    return extended_patch_str

def check_if_hunk_lines_matches_to_file(i, original_lines, patch_lines, start1):
    """
    Check if the hunk lines match the original file content. We saw cases where the hunk header line doesn't match the original file content, and then
    extending the hunk with extra lines before the hunk header can cause the hunk to be invalid.
    """
    is_valid_hunk = True
    try:
        if i + 1 < len(patch_lines) and patch_lines[i + 1][0] == ' ': # an existing line in the file
            if patch_lines[i + 1].strip() != original_lines[start1 - 1].strip():
                # check if different encoding is needed
                original_line = original_lines[start1 - 1].strip()
                for encoding in ['iso-8859-1', 'latin-1', 'ascii', 'utf-16']:
                    try:
                        if original_line.encode(encoding).decode().strip() == patch_lines[i + 1].strip():
                            get_logger().info(f"Detected different encoding in hunk header line {start1}, needed encoding: {encoding}")
                            return False # we still want to avoid extending the hunk. But we don't want to log an error
                    except:
                        pass

                is_valid_hunk = False
                get_logger().info(
                    f"Invalid hunk in PR, line {start1} in hunk header doesn't match the original file content")
    except:
        pass
    return is_valid_hunk


def extract_hunk_headers(match):
    res = list(match.groups())
    for i in range(len(res)):
        if res[i] is None:
            res[i] = 0
    try:
        start1, size1, start2, size2 = map(int, res[:4])
    except:  # '@@ -0,0 +1 @@' case
        start1, size1, size2 = map(int, res[:3])
        start2 = 0
    section_header = res[4]
    return section_header, size1, size2, start1, start2


def omit_deletion_hunks(patch_lines) -> str:
    """
    Omit deletion hunks from the patch and return the modified patch.
    Args:
    - patch_lines: a list of strings representing the lines of the patch
    Returns:
    - A string representing the modified patch with deletion hunks omitted
    """

    temp_hunk = []
    added_patched = []
    add_hunk = False
    inside_hunk = False
    RE_HUNK_HEADER = re.compile(
        r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))?\ @@[ ]?(.*)")

    for line in patch_lines:
        if line.startswith('@@'):
            match = RE_HUNK_HEADER.match(line)
            if match:
                # finish previous hunk
                if inside_hunk and add_hunk:
                    added_patched.extend(temp_hunk)
                    temp_hunk = []
                    add_hunk = False
                temp_hunk.append(line)
                inside_hunk = True
        else:
            temp_hunk.append(line)
            if line:
                edit_type = line[0]
                if edit_type == '+':
                    add_hunk = True
    if inside_hunk and add_hunk:
        added_patched.extend(temp_hunk)

    return '\n'.join(added_patched)


def handle_patch_deletions(patch: str, original_file_content_str: str,
                           new_file_content_str: str, file_name: str, edit_type: EDIT_TYPE = EDIT_TYPE.UNKNOWN) -> str:
    """
    Handle entire file or deletion patches.

    This function takes a patch, original file content, new file content, and file name as input.
    It handles entire file or deletion patches and returns the modified patch with deletion hunks omitted.

    Args:
        patch (str): The patch to be handled.
        original_file_content_str (str): The original content of the file.
        new_file_content_str (str): The new content of the file.
        file_name (str): The name of the file.

    Returns:
        str: The modified patch with deletion hunks omitted.

    """
    if not new_file_content_str and (edit_type == EDIT_TYPE.DELETED or edit_type == EDIT_TYPE.UNKNOWN):
        # logic for handling deleted files - don't show patch, just show that the file was deleted
        if get_settings().config.verbosity_level > 0:
            get_logger().info(f"Processing file: {file_name}, minimizing deletion file")
        patch = None # file was deleted
    else:
        patch_lines = patch.splitlines()
        patch_new = omit_deletion_hunks(patch_lines)
        if patch != patch_new:
            if get_settings().config.verbosity_level > 0:
                get_logger().info(f"Processing file: {file_name}, hunks were deleted")
            patch = patch_new
    return patch


def decouple_and_convert_to_hunks_with_lines_numbers(patch: str, file) -> str:
    """
    Convert a given patch string into a string with line numbers for each hunk, indicating the new and old content of
    the file.

    Args:
        patch (str): The patch string to be converted.
        file: An object containing the filename of the file being patched.

    Returns:
        str: A string with line numbers for each hunk, indicating the new and old content of the file.

    example output:
## src/file.ts
__new hunk__
881        line1
882        line2
883        line3
887 +      line4
888 +      line5
889        line6
890        line7
...
__old hunk__
        line1
        line2
-       line3
-       line4
        line5
        line6
           ...
    """

    # Add a header for the file
    if file:
        # if the file was deleted, return a message indicating that the file was deleted
        if hasattr(file, 'edit_type') and file.edit_type == EDIT_TYPE.DELETED:
            return f"\n\n## File '{file.filename.strip()}' was deleted\n"

        patch_with_lines_str = f"\n\n## File: '{file.filename.strip()}'\n"
    else:
        patch_with_lines_str = ""

    patch_lines = patch.splitlines()
    RE_HUNK_HEADER = re.compile(
        r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@[ ]?(.*)")
    new_content_lines = []
    old_content_lines = []
    match = None
    start1, size1, start2, size2 = -1, -1, -1, -1
    prev_header_line = []
    header_line = []
    for line_i, line in enumerate(patch_lines):
        if 'no newline at end of file' in line.lower():
            continue

        if line.startswith('@@'):
            header_line = line
            match = RE_HUNK_HEADER.match(line)
            if match and (new_content_lines or old_content_lines):  # found a new hunk, split the previous lines
                if prev_header_line:
                    patch_with_lines_str += f'\n{prev_header_line}\n'
                is_plus_lines = is_minus_lines = False
                if new_content_lines:
                    is_plus_lines = any([line.startswith('+') for line in new_content_lines])
                if old_content_lines:
                    is_minus_lines = any([line.startswith('-') for line in old_content_lines])
                if is_plus_lines or is_minus_lines: # notice 'True' here - we always present __new hunk__ for section, otherwise LLM gets confused
                    patch_with_lines_str = patch_with_lines_str.rstrip() + '\n__new hunk__\n'
                    for i, line_new in enumerate(new_content_lines):
                        patch_with_lines_str += f"{start2 + i} {line_new}\n"
                if is_minus_lines:
                    patch_with_lines_str = patch_with_lines_str.rstrip() + '\n__old hunk__\n'
                    for line_old in old_content_lines:
                        patch_with_lines_str += f"{line_old}\n"
                new_content_lines = []
                old_content_lines = []
            if match:
                prev_header_line = header_line

            section_header, size1, size2, start1, start2 = extract_hunk_headers(match)

        elif line.startswith('+'):
            new_content_lines.append(line)
        elif line.startswith('-'):
            old_content_lines.append(line)
        else:
            if not line and line_i: # if this line is empty and the next line is a hunk header, skip it
                if line_i + 1 < len(patch_lines) and patch_lines[line_i + 1].startswith('@@'):
                    continue
                elif line_i + 1 == len(patch_lines):
                    continue
            new_content_lines.append(line)
            old_content_lines.append(line)

    # finishing last hunk
    if match and new_content_lines:
        patch_with_lines_str += f'\n{header_line}\n'
        is_plus_lines = is_minus_lines = False
        if new_content_lines:
            is_plus_lines = any([line.startswith('+') for line in new_content_lines])
        if old_content_lines:
            is_minus_lines = any([line.startswith('-') for line in old_content_lines])
        if is_plus_lines or is_minus_lines:  # notice 'True' here - we always present __new hunk__ for section, otherwise LLM gets confused
            patch_with_lines_str = patch_with_lines_str.rstrip() + '\n__new hunk__\n'
            for i, line_new in enumerate(new_content_lines):
                patch_with_lines_str += f"{start2 + i} {line_new}\n"
        if is_minus_lines:
            patch_with_lines_str = patch_with_lines_str.rstrip() + '\n__old hunk__\n'
            for line_old in old_content_lines:
                patch_with_lines_str += f"{line_old}\n"

    return patch_with_lines_str.rstrip()


def extract_hunk_lines_from_patch(patch: str, file_name, line_start, line_end, side, remove_trailing_chars: bool = True) -> tuple[str, str]:
    try:
        patch_with_lines_str = f"\n\n## File: '{file_name.strip()}'\n\n"
        selected_lines = ""
        patch_lines = patch.splitlines()
        RE_HUNK_HEADER = re.compile(
            r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@[ ]?(.*)")
        match = None
        start1, size1, start2, size2 = -1, -1, -1, -1
        skip_hunk = False
        selected_lines_num = 0
        for line in patch_lines:
            if 'no newline at end of file' in line.lower():
                continue

            if line.startswith('@@'):
                skip_hunk = False
                selected_lines_num = 0
                header_line = line

                match = RE_HUNK_HEADER.match(line)

                section_header, size1, size2, start1, start2 = extract_hunk_headers(match)

                # check if line range is in this hunk
                if side.lower() == 'left':
                    # check if line range is in this hunk
                    if not (start1 <= line_start <= start1 + size1):
                        skip_hunk = True
                        continue
                elif side.lower() == 'right':
                    if not (start2 <= line_start <= start2 + size2):
                        skip_hunk = True
                        continue
                patch_with_lines_str += f'\n{header_line}\n'

            elif not skip_hunk:
                if side.lower() == 'right' and line_start <= start2 + selected_lines_num <= line_end:
                    selected_lines += line + '\n'
                if side.lower() == 'left' and start1 <= selected_lines_num + start1 <= line_end:
                    selected_lines += line + '\n'
                patch_with_lines_str += line + '\n'
                if not line.startswith('-'): # currently we don't support /ask line for deleted lines
                    selected_lines_num += 1
    except Exception as e:
        get_logger().error(f"Failed to extract hunk lines from patch: {e}", artifact={"traceback": traceback.format_exc()})
        return "", ""

    if remove_trailing_chars:
        patch_with_lines_str = patch_with_lines_str.rstrip()
        selected_lines = selected_lines.rstrip()

    return patch_with_lines_str, selected_lines


# Language Handler Module
# Language Selection, source: https://github.com/bigcode-project/bigcode-dataset/blob/main/language_selection/programming-languages-to-file-extensions.json  # noqa E501
from typing import Dict



def filter_bad_extensions(files):
    # Bad Extensions, source: https://github.com/EleutherAI/github-downloader/blob/345e7c4cbb9e0dc8a0615fd995a08bf9d73b3fe6/download_repo_text.py  # noqa: E501
    bad_extensions = get_settings().bad_extensions.default
    if get_settings().config.use_extra_bad_extensions:
        bad_extensions += get_settings().bad_extensions.extra
    return [f for f in files if f.filename is not None and is_valid_file(f.filename, bad_extensions)]


def is_valid_file(filename:str, bad_extensions=None) -> bool:
    if not filename:
        return False
    if not bad_extensions:
        bad_extensions = get_settings().bad_extensions.default
        if get_settings().config.use_extra_bad_extensions:
            bad_extensions += get_settings().bad_extensions.extra

    auto_generated_files = ['package-lock.json', 'yarn.lock', 'composer.lock', 'Gemfile.lock', 'poetry.lock']
    for forbidden_file in auto_generated_files:
        if filename.endswith(forbidden_file):
            return False

    return filename.split('.')[-1] not in bad_extensions


def sort_files_by_main_languages(languages: Dict, files: list):
    """
    Sort files by their main language, put the files that are in the main language first and the rest files after
    """
    # sort languages by their size
    languages_sorted_list = [k for k, v in sorted(languages.items(), key=lambda item: item[1], reverse=True)]
    # languages_sorted = sorted(languages, key=lambda x: x[1], reverse=True)
    # get all extensions for the languages
    main_extensions = []
    language_extension_map_org = get_settings().language_extension_map_org
    language_extension_map = {k.lower(): v for k, v in language_extension_map_org.items()}
    for language in languages_sorted_list:
        if language.lower() in language_extension_map:
            main_extensions.append(language_extension_map[language.lower()])
        else:
            main_extensions.append([])

    # filter out files bad extensions
    files_filtered = filter_bad_extensions(files)

    # sort files by their extension, put the files that are in the main extension first
    # and the rest files after, map languages_sorted to their respective files
    files_sorted = []
    rest_files = {}

    # if no languages detected, put all files in the "Other" category
    if not languages:
        files_sorted = [({"language": "Other", "files": list(files_filtered)})]
        return files_sorted

    main_extensions_flat = []
    for ext in main_extensions:
        main_extensions_flat.extend(ext)

    for extensions, lang in zip(main_extensions, languages_sorted_list):  # noqa: B905
        tmp = []
        for file in files_filtered:
            extension_str = f".{file.filename.split('.')[-1]}"
            if extension_str in extensions:
                tmp.append(file)
            else:
                if (file.filename not in rest_files) and (extension_str not in main_extensions_flat):
                    rest_files[file.filename] = file
        if len(tmp) > 0:
            files_sorted.append({"language": lang, "files": tmp})
    files_sorted.append({"language": "Other", "files": list(rest_files.values())})
    return files_sorted


# Server Utils Module
import hashlib
import hmac
import time
from collections import defaultdict
from typing import Any, Callable

from fastapi import HTTPException


def verify_signature(payload_body, secret_token, signature_header):
    """Verify that the payload was sent from GitHub by validating SHA256.

    Raise and return 403 if not authorized.

    Args:
        payload_body: original request body to verify (request.body())
        secret_token: GitHub app webhook token (WEBHOOK_SECRET)
        signature_header: header received from GitHub (x-hub-signature-256)
    """
    if not signature_header:
        raise HTTPException(status_code=403, detail="x-hub-signature-256 header is missing!")
    hash_object = hmac.new(secret_token.encode('utf-8'), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    if not hmac.compare_digest(expected_signature, signature_header):
        raise HTTPException(status_code=403, detail="Request signatures didn't match!")


class RateLimitExceeded(Exception):
    """Raised when the git provider API rate limit has been exceeded."""
    pass


class DefaultDictWithTimeout(defaultdict):
    """A defaultdict with a time-to-live (TTL)."""

    def __init__(
        self,
        default_factory: Callable[[], Any] = None,
        ttl: int = None,
        refresh_interval: int = 60,
        update_key_time_on_get: bool = True,
        *args,
        **kwargs,
    ):
        """
        Args:
            default_factory: The default factory to use for keys that are not in the dictionary.
            ttl: The time-to-live (TTL) in seconds.
            refresh_interval: How often to refresh the dict and delete items older than the TTL.
            update_key_time_on_get: Whether to update the access time of a key also on get (or only when set).
        """
        super().__init__(default_factory, *args, **kwargs)
        self.__key_times = dict()
        self.__ttl = ttl
        self.__refresh_interval = refresh_interval
        self.__update_key_time_on_get = update_key_time_on_get
        self.__last_refresh = self.__time() - self.__refresh_interval

    @staticmethod
    def __time():
        return time.monotonic()

    def __refresh(self):
        if self.__ttl is None:
            return
        request_time = self.__time()
        if request_time - self.__last_refresh > self.__refresh_interval:
            return
        to_delete = [key for key, key_time in self.__key_times.items() if request_time - key_time > self.__ttl]
        for key in to_delete:
            del self[key]
        self.__last_refresh = request_time

    def __getitem__(self, __key):
        if self.__update_key_time_on_get:
            self.__key_times[__key] = self.__time()
        self.__refresh()
        return super().__getitem__(__key)

    def __setitem__(self, __key, __value):
        self.__key_times[__key] = self.__time()
        return super().__setitem__(__key, __value)

    def __delitem__(self, __key):
        del self.__key_times[__key]
        return super().__delitem__(__key)


# Base Git Provider
from abc import ABC, abstractmethod
# enum EDIT_TYPE (ADDED, DELETED, MODIFIED, RENAMED)
import os
import shutil
import subprocess
from typing import Optional, Tuple


MAX_FILES_ALLOWED_FULL = 50

class GitProvider(ABC):
    @abstractmethod
    def is_supported(self, capability: str) -> bool:
        pass

    #Given a url (issues or PR/MR) - get the .git repo url to which they belong. Needs to be implemented by the provider.
    def get_git_repo_url(self, issues_or_pr_url: str) -> str:
        get_logger().warning("Not implemented! Returning empty url")
        return ""

    # Given a git repo url, return prefix and suffix of the provider in order to view a given file belonging to that repo. Needs to be implemented by the provider.
    # For example: For a git: https://git_provider.com/MY_PROJECT/MY_REPO.git and desired branch: <MY_BRANCH> then it should return ('https://git_provider.com/projects/MY_PROJECT/repos/MY_REPO/.../<MY_BRANCH>', '?=<SOME HEADER>')
    # so that to properly view the file: docs/readme.md -> <PREFIX>/docs/readme.md<SUFFIX> -> https://git_provider.com/projects/MY_PROJECT/repos/MY_REPO/<MY_BRANCH>/docs/readme.md?=<SOME HEADER>)
    def get_canonical_url_parts(self, repo_git_url:str, desired_branch:str) -> Tuple[str, str]:
        get_logger().warning("Not implemented! Returning empty prefix and suffix")
        return ("", "")


    #Clone related API
    #An object which ensures deletion of a cloned repo, once it becomes out of scope.
    # Example usage:
    #    with TemporaryDirectory() as tmp_dir:
    #            returned_obj: GitProvider.ScopedClonedRepo = self.git_provider.clone(self.repo_url, tmp_dir, remove_dest_folder=False)
    #            print(returned_obj.path) #Use returned_obj.path.
    #    #From this point, returned_obj.path may be deleted at any point and therefore must not be used.
    class ScopedClonedRepo(object):
        def __init__(self, dest_folder):
            self.path = dest_folder

        def __del__(self):
            if self.path and os.path.exists(self.path):
                shutil.rmtree(self.path, ignore_errors=True)

    #Method to allow implementors to manipulate the repo url to clone (such as embedding tokens in the url string). Needs to be implemented by the provider.
    def _prepare_clone_url_with_token(self, repo_url_to_clone: str) -> str | None:
        get_logger().warning("Not implemented! Returning None")
        return None

    # Does a shallow clone, using a forked process to support a timeout guard.
    # In case operation has failed, it is expected to throw an exception as this method does not return a value.
    def _clone_inner(self, repo_url: str, dest_folder: str, operation_timeout_in_seconds: int=None) -> None:
        #The following ought to be equivalent to:
        # #Repo.clone_from(repo_url, dest_folder)
        # , but with throwing an exception upon timeout.
        # Note: This can only be used in context that supports using pipes.
        subprocess.run([
            "git", "clone",
            "--filter=blob:none",
            "--depth", "1",
            repo_url, dest_folder
        ], check=True,  # check=True will raise an exception if the command fails
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=operation_timeout_in_seconds)

    CLONE_TIMEOUT_SEC = 20
    # Clone a given url to a destination folder. If successful, returns an object that wraps the destination folder,
    # deleting it once it is garbage collected. See: GitProvider.ScopedClonedRepo for more details.
    def clone(self, repo_url_to_clone: str, dest_folder: str, remove_dest_folder: bool = True,
              operation_timeout_in_seconds: int=CLONE_TIMEOUT_SEC) -> ScopedClonedRepo|None:
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
            get_logger().exception(f"Clone failed: Could not clone url.",
                artifact={"error": str(e), "url": clone_url, "dest_folder": dest_folder})
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

    def edit_comment(self, comment, body: str):
        pass

    def edit_comment_from_comment_id(self, comment_id: int, body: str):
        pass

    def get_comment_body_from_comment_id(self, comment_id: int) -> str:
        pass

    def reply_to_comment_from_comment_id(self, comment_id: int, body: str):
        pass

    def get_pr_description(self, full: bool = True, split_changes_walkthrough=False) -> str | tuple:
        from pr_agent.algo.utils import clip_tokens
        max_tokens_description = get_settings().get("CONFIG.MAX_DESCRIPTION_TOKENS", None)
        description = self.get_pr_description_full() if full else self.get_user_description()
        if split_changes_walkthrough:
            description, files = process_description(description)
            if max_tokens_description:
                description = clip_tokens(description, max_tokens_description)
            return description, files
        else:
            if max_tokens_description:
                description = clip_tokens(description, max_tokens_description)
            return description

    def get_user_description(self) -> str:
        if hasattr(self, 'user_description') and not (self.user_description is None):
            return self.user_description

        description = (self.get_pr_description_full() or "").strip()
        description_lowercase = description.lower()
        get_logger().debug(f"Existing description", description=description_lowercase)

        # if the existing description wasn't generated by the pr-agent, just return it as-is
        if not self._is_generated_by_pr_agent(description_lowercase):
            get_logger().info(f"Existing description was not generated by the pr-agent")
            self.user_description = description
            return description

        # if the existing description was generated by the pr-agent, but it doesn't contain a user description,
        # return nothing (empty string) because it means there is no user description
        user_description_header = "### **user description**"
        if user_description_header not in description_lowercase:
            get_logger().info(f"Existing description was generated by the pr-agent, but it doesn't contain a user description")
            return ""

        # otherwise, extract the original user description from the existing pr-agent description and return it
        # user_description_start_position = description_lowercase.find(user_description_header) + len(user_description_header)
        # return description[user_description_start_position:].split("\n", 1)[-1].strip()

        # the 'user description' is in the beginning. extract and return it
        possible_headers = self._possible_headers()
        start_position = description_lowercase.find(user_description_header) + len(user_description_header)
        end_position = len(description)
        for header in possible_headers: # try to clip at the next header
            if header != user_description_header and header in description_lowercase:
                end_position = min(end_position, description_lowercase.find(header))
        if end_position != len(description) and end_position > start_position:
            original_user_description = description[start_position:end_position].strip()
            if original_user_description.endswith("___"):
                original_user_description = original_user_description[:-3].strip()
        else:
            original_user_description = description.split("___")[0].strip()
            if original_user_description.lower().startswith(user_description_header):
                original_user_description = original_user_description[len(user_description_header):].strip()

        get_logger().info(f"Extracted user description from existing description",
                          description=original_user_description)
        self.user_description = original_user_description
        return original_user_description

    def _possible_headers(self):
        return ("### **user description**", "### **pr type**", "### **pr description**", "### **pr labels**", "### **type**", "### **description**",
                "### **labels**", "### 🤖 generated by pr agent")

    def _is_generated_by_pr_agent(self, description_lowercase: str) -> bool:
        possible_headers = self._possible_headers()
        return any(description_lowercase.startswith(header) for header in possible_headers)

    @abstractmethod
    def get_repo_settings(self):
        pass

    def get_workspace_name(self):
        return ""

    def get_pr_id(self):
        return ""

    def get_line_link(self, relevant_file: str, relevant_line_start: int, relevant_line_end: int = None) -> str:
        return ""

    def get_lines_link_original_file(self, filepath:str, component_range: Range) -> str:
        return ""

    #### comments operations ####
    @abstractmethod
    def publish_comment(self, pr_comment: str, is_temporary: bool = False):
        pass

    def publish_persistent_comment(self, pr_comment: str,
                                   initial_header: str,
                                   update_header: bool = True,
                                   name='review',
                                   final_update_message=True):
        return self.publish_comment(pr_comment)

    def publish_persistent_comment_full(self, pr_comment: str,
                                   initial_header: str,
                                   update_header: bool = True,
                                   name='review',
                                   final_update_message=True):
        try:
            prev_comments = list(self.get_issue_comments())
            for comment in prev_comments:
                if comment.body.startswith(initial_header):
                    latest_commit_url = self.get_latest_commit_url()
                    comment_url = self.get_comment_url(comment)
                    if update_header:
                        updated_header = f"{initial_header}\n\n#### ({name.capitalize()} updated until commit {latest_commit_url})\n"
                        pr_comment_updated = pr_comment.replace(initial_header, updated_header)
                    else:
                        pr_comment_updated = pr_comment
                    get_logger().info(f"Persistent mode - updating comment {comment_url} to latest {name} message")
                    # response = self.mr.notes.update(comment.id, {'body': pr_comment_updated})
                    self.edit_comment(comment, pr_comment_updated)
                    if final_update_message:
                        return self.publish_comment(
                            f"**[Persistent {name}]({comment_url})** updated to latest commit {latest_commit_url}")
                    return comment
        except Exception as e:
            get_logger().exception(f"Failed to update persistent review, error: {e}")
            pass
        return self.publish_comment(pr_comment)

    @abstractmethod
    def publish_inline_comment(self, body: str, relevant_file: str, relevant_line_in_file: str, original_suggestion=None):
        pass

    def create_inline_comment(self, body: str, relevant_file: str, relevant_line_in_file: str,
                              absolute_position: int = None):
        raise NotImplementedError("This git provider does not support creating inline comments yet")

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

    def get_comment_url(self, comment) -> str:
        return ""

    def get_review_thread_comments(self, comment_id: int) -> list[dict]:
        pass

    #### labels operations ####
    @abstractmethod
    def publish_labels(self, labels):
        pass

    @abstractmethod
    def get_pr_labels(self, update=False):
        pass

    def get_repo_labels(self):
        pass

    @abstractmethod
    def add_eyes_reaction(self, issue_comment_id: int, disable_eyes: bool = False) -> Optional[int]:
        pass

    @abstractmethod
    def remove_reaction(self, issue_comment_id: int, reaction_id: int) -> bool:
        pass

    #### commits operations ####
    @abstractmethod
    def get_commit_messages(self):
        pass

    def get_pr_url(self) -> str:
        if hasattr(self, 'pr_url'):
            return self.pr_url
        return ""

    def get_latest_commit_url(self) -> str:
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


def get_main_pr_language(languages, files) -> str:
    """
    Get the main language of the commit. Return an empty string if cannot determine.
    """
    main_language_str = ""
    if not languages:
        get_logger().info("No languages detected")
        return main_language_str
    if not files:
        get_logger().info("No files in diff")
        return main_language_str

    try:
        top_language = max(languages, key=languages.get).lower()

        # validate that the specific commit uses the main language
        extension_list = []
        for file in files:
            if not file:
                continue
            if isinstance(file, str):
                file = FilePatchInfo(base_file=None, head_file=None, patch=None, filename=file)
            extension_list.append(file.filename.rsplit('.')[-1])

        # get the most common extension
        most_common_extension = '.' + max(set(extension_list), key=extension_list.count)
        try:
            language_extension_map_org = get_settings().language_extension_map_org
            language_extension_map = {k.lower(): v for k, v in language_extension_map_org.items()}

            if top_language in language_extension_map and most_common_extension in language_extension_map[top_language]:
                main_language_str = top_language
            else:
                for language, extensions in language_extension_map.items():
                    if most_common_extension in extensions:
                        main_language_str = language
                        break
        except Exception as e:
            get_logger().exception(f"Failed to get main language: {e}")
            pass

        ## old approach:
        # most_common_extension = max(set(extension_list), key=extension_list.count)
        # if most_common_extension == 'py' and top_language == 'python' or \
        #         most_common_extension == 'js' and top_language == 'javascript' or \
        #         most_common_extension == 'ts' and top_language == 'typescript' or \
        #         most_common_extension == 'tsx' and top_language == 'typescript' or \
        #         most_common_extension == 'go' and top_language == 'go' or \
        #         most_common_extension == 'java' and top_language == 'java' or \
        #         most_common_extension == 'c' and top_language == 'c' or \
        #         most_common_extension == 'cpp' and top_language == 'c++' or \
        #         most_common_extension == 'cs' and top_language == 'c#' or \
        #         most_common_extension == 'swift' and top_language == 'swift' or \
        #         most_common_extension == 'php' and top_language == 'php' or \
        #         most_common_extension == 'rb' and top_language == 'ruby' or \
        #         most_common_extension == 'rs' and top_language == 'rust' or \
        #         most_common_extension == 'scala' and top_language == 'scala' or \
        #         most_common_extension == 'kt' and top_language == 'kotlin' or \
        #         most_common_extension == 'pl' and top_language == 'perl' or \
        #         most_common_extension == top_language:
        #     main_language_str = top_language

    except Exception as e:
        get_logger().exception(e)
        pass

    return main_language_str




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
import copy
import difflib
import hashlib
import itertools
import re
import time
import traceback
import json
from datetime import datetime
from typing import Optional, Tuple
from urllib.parse import urlparse

from github.Issue import Issue
from github import AppAuthentication, Auth, Github, GithubException
from retry import retry

                          find_line_number_of_relevant_line_in_file,
                          load_large_diff, set_file_languages)
from .git_provider import (MAX_FILES_ALLOWED_FULL, FilePatchInfo, GitProvider,
                           IncrementalPR)


class GithubProvider(GitProvider):
    def __init__(self, pr_url: Optional[str] = None):
        self.repo_obj = None
        try:
            self.installation_id = None
        except Exception:
            self.installation_id = None
        self.max_comment_chars = 65000
        self.base_url = get_settings().get("GITHUB.BASE_URL", "https://api.github.com").rstrip("/") # "https://api.github.com"
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
            self.pr_url = self.get_pr_url() # pr_url for github actions can be as api.github.com, so we need to get the url from the pr object
        elif pr_url and 'issue' in pr_url: #url is an issue
            self.issue_main = self._get_issue_handle(pr_url)
        else: #Instantiated the provider without a PR / Issue
            self.pr_commits = None

    def _get_issue_handle(self, issue_url) -> Optional[Issue]:
        repo_name, issue_number = self._parse_issue_url(issue_url)
        if not repo_name or not issue_number:
            get_logger().error(f"Given url: {issue_url} is not a valid issue.")
            return None
        # else: Check if can get a valid Repo handle:
        try:
            repo_obj = self.github_client.get_repo(repo_name)
            if not repo_obj:
                get_logger().error(f"Given url: {issue_url}, belonging to owner/repo: {repo_name} does "
                                   f"not have a valid repository: {self.get_git_repo_url(issue_url)}")
                return None
            # else: Valid repo handle:
            return repo_obj.get_issue(issue_number)
        except Exception as e:
            get_logger().exception(f"Failed to get an issue object for issue: {issue_url}, belonging to owner/repo: {repo_name}")
            return None

    def get_incremental_commits(self, incremental=IncrementalPR(False)):
        self.incremental = incremental
        if self.incremental.is_incremental:
            self.unreviewed_files_set = dict()
            self._get_incremental_commits()

    def is_supported(self, capability: str) -> bool:
        return True

    def _get_owner_and_repo_path(self, given_url: str) -> str:
        try:
            repo_path = None
            if 'issues' in given_url:
                repo_path, _ = self._parse_issue_url(given_url)
            elif 'pull' in given_url:
                repo_path, _ = self._parse_pr_url(given_url)
            elif given_url.endswith('.git'):
                parsed_url = urlparse(given_url)
                repo_path = (parsed_url.path.split('.git')[0])[1:] # /<owner>/<repo>.git -> <owner>/<repo>
            if not repo_path:
                get_logger().error(f"url is neither an issues url nor a PR url nor a valid git url: {given_url}. Returning empty result.")
                return ""
            return repo_path
        except Exception as e:
            get_logger().exception(f"unable to parse url: {given_url}. Returning empty result.")
            return ""

    def get_git_repo_url(self, issues_or_pr_url: str) -> str:
        repo_path = self._get_owner_and_repo_path(issues_or_pr_url) #Return: <OWNER>/<REPO>
        if not repo_path or repo_path not in issues_or_pr_url:
            get_logger().error(f"Unable to retrieve owner/path from url: {issues_or_pr_url}")
            return ""
        return f"{self.base_url_html}/{repo_path}.git" #https://github.com / <OWNER>/<REPO>.git

    # Given a git repo url, return prefix and suffix of the provider in order to view a given file belonging to that repo.
    # Example: https://github.com/qodo-ai/pr-agent.git and branch: v0.8 -> prefix: "https://github.com/qodo-ai/pr-agent/blob/v0.8", suffix: ""
    # In case git url is not provided, provider will use PR context (which includes branch) to determine the prefix and suffix.
    def get_canonical_url_parts(self, repo_git_url:str, desired_branch:str) -> Tuple[str, str]:
        owner = None
        repo = None
        scheme_and_netloc = None

        if repo_git_url or self.issue_main: #Either user provided an external git url, which may be different than what this provider was initialized with, or an issue:
            desired_branch = desired_branch if repo_git_url else self.issue_main.repository.default_branch
            html_url = repo_git_url if repo_git_url else self.issue_main.html_url
            parsed_git_url = urlparse(html_url)
            scheme_and_netloc = parsed_git_url.scheme + "://" + parsed_git_url.netloc
            repo_path = self._get_owner_and_repo_path(html_url)
            if repo_path.count('/') == 1: #Has to have the form <owner>/<repo>
                owner, repo = repo_path.split('/')
            else:
                get_logger().error(f"Invalid repo_path: {repo_path} from url: {html_url}")
                return ("", "")

        if (not owner or not repo) and self.repo: #"else" - User did not provide an external git url, or not an issue, use self.repo object
            owner, repo = self.repo.split('/')
            scheme_and_netloc = self.base_url_html
            desired_branch = self.repo_obj.default_branch
        if not all([scheme_and_netloc, owner, repo]): #"else": Not invoked from a PR context,but no provided git url for context
            get_logger().error(f"Unable to get canonical url parts since missing context (PR or explicit git url)")
            return ("", "")

        prefix = f"{scheme_and_netloc}/{owner}/{repo}/blob/{desired_branch}"
        suffix = ""  # github does not add a suffix
        return (prefix, suffix)

    def get_pr_url(self) -> str:
        return self.pr.html_url

    def set_pr(self, pr_url: str):
        self.repo, self.pr_num = self._parse_pr_url(pr_url)
        self.pr = self._get_pr()

    def _get_incremental_commits(self):
        if not self.pr_commits:
            self.pr_commits = list(self.pr.get_commits())

        self.previous_review = self.get_previous_review(full=True, incremental=True)
        if self.previous_review:
            self.incremental.commits_range = self.get_commit_range()
            # Get all files changed during the commit range

            for commit in self.incremental.commits_range:
                if commit.commit.message.startswith(f"Merge branch '{self._get_repo().default_branch}'"):
                    get_logger().info(f"Skipping merge commit {commit.commit.message}")
                    continue
                self.unreviewed_files_set.update({file.filename: file for file in commit.files})
        else:
            get_logger().info("No previous review found, will review the entire PR")
            self.incremental.is_incremental = False

    def get_commit_range(self):
        last_review_time = self.previous_review.created_at
        first_new_commit_index = None
        for index in range(len(self.pr_commits) - 1, -1, -1):
            if self.pr_commits[index].commit.author.date > last_review_time:
                self.incremental.first_new_commit = self.pr_commits[index]
                first_new_commit_index = index
            else:
                self.incremental.last_seen_commit = self.pr_commits[index]
                break
        return self.pr_commits[first_new_commit_index:] if first_new_commit_index is not None else []

    def get_previous_review(self, *, full: bool, incremental: bool):
        if not (full or incremental):
            raise ValueError("At least one of full or incremental must be True")
        if not getattr(self, "comments", None):
            self.comments = list(self.pr.get_issue_comments())
        prefixes = []
        if full:
            prefixes.append(PRReviewHeader.REGULAR.value)
        if incremental:
            prefixes.append(PRReviewHeader.INCREMENTAL.value)
        for index in range(len(self.comments) - 1, -1, -1):
            if any(self.comments[index].body.startswith(prefix) for prefix in prefixes):
                return self.comments[index]

    def get_files(self):
        if self.incremental.is_incremental and self.unreviewed_files_set:
            return self.unreviewed_files_set.values()
        try:
            git_files = None
            if git_files:
                return git_files
            self.git_files = list(self.pr.get_files()) # 'list' to handle pagination
            context["git_files"] = self.git_files
            return self.git_files
        except Exception:
            if not self.git_files:
                self.git_files = list(self.pr.get_files())
            return self.git_files

    def get_num_of_files(self):
        if hasattr(self.git_files, "totalCount"):
            return self.git_files.totalCount
        else:
            try:
                return len(self.git_files)
            except Exception as e:
                return -1

    @retry(exceptions=RateLimitExceeded,
           tries=get_settings().github.ratelimit_retries, delay=2, backoff=2, jitter=(1, 3))
    def get_diff_files(self) -> list[FilePatchInfo]:
        """
        Retrieves the list of files that have been modified, added, deleted, or renamed in a pull request in GitHub,
        along with their content and patch information.

        Returns:
            diff_files (List[FilePatchInfo]): List of FilePatchInfo objects representing the modified, added, deleted,
            or renamed files in the merge request.
        """
        try:
            try:
                diff_files = None
                if diff_files:
                    return diff_files
            except Exception:
                pass

            if self.diff_files:
                return self.diff_files

            # filter files using [ignore] patterns
            files_original = self.get_files()
            files = filter_ignored(files_original)
            if files_original != files:
                try:
                    names_original = [file.filename for file in files_original]
                    names_new = [file.filename for file in files]
                    get_logger().info(f"Filtered out [ignore] files for pull request:", extra=
                    {"files": names_original,
                     "filtered_files": names_new})
                except Exception:
                    pass

            diff_files = []
            invalid_files_names = []
            is_close_to_rate_limit = False

            # The base.sha will point to the current state of the base branch (including parallel merges), not the original base commit when the PR was created
            # We can fix this by finding the merge base commit between the PR head and base branches
            # Note that The pr.head.sha is actually correct as is - it points to the latest commit in your PR branch.
            # This SHA isn't affected by parallel merges to the base branch since it's specific to your PR's branch.
            repo = self.repo_obj
            pr = self.pr
            try:
                compare = repo.compare(pr.base.sha, pr.head.sha) # communication with GitHub
                merge_base_commit = compare.merge_base_commit
            except Exception as e:
                get_logger().error(f"Failed to get merge base commit: {e}")
                merge_base_commit = pr.base
            if merge_base_commit.sha != pr.base.sha:
                get_logger().info(
                    f"Using merge base commit {merge_base_commit.sha} instead of base commit ")

            counter_valid = 0
            for file in files:
                if not is_valid_file(file.filename):
                    invalid_files_names.append(file.filename)
                    continue

                patch = file.patch
                if is_close_to_rate_limit:
                    new_file_content_str = ""
                    original_file_content_str = ""
                else:
                    # allow only a limited number of files to be fully loaded. We can manage the rest with diffs only
                    counter_valid += 1
                    avoid_load = False
                    if counter_valid >= MAX_FILES_ALLOWED_FULL and patch and not self.incremental.is_incremental:
                        avoid_load = True
                        if counter_valid == MAX_FILES_ALLOWED_FULL:
                            get_logger().info(f"Too many files in PR, will avoid loading full content for rest of files")

                    if avoid_load:
                        new_file_content_str = ""
                    else:
                        new_file_content_str = self._get_pr_file_content(file, self.pr.head.sha)  # communication with GitHub

                    if self.incremental.is_incremental and self.unreviewed_files_set:
                        original_file_content_str = self._get_pr_file_content(file, self.incremental.last_seen_commit_sha)
                        patch = load_large_diff(file.filename, new_file_content_str, original_file_content_str)
                        self.unreviewed_files_set[file.filename] = patch
                    else:
                        if avoid_load:
                            original_file_content_str = ""
                        else:
                            original_file_content_str = self._get_pr_file_content(file, merge_base_commit.sha)
                            # original_file_content_str = self._get_pr_file_content(file, self.pr.base.sha)
                        if not patch:
                            patch = load_large_diff(file.filename, new_file_content_str, original_file_content_str)


                if file.status == 'added':
                    edit_type = EDIT_TYPE.ADDED
                elif file.status == 'removed':
                    edit_type = EDIT_TYPE.DELETED
                elif file.status == 'renamed':
                    edit_type = EDIT_TYPE.RENAMED
                elif file.status == 'modified':
                    edit_type = EDIT_TYPE.MODIFIED
                else:
                    get_logger().error(f"Unknown edit type: {file.status}")
                    edit_type = EDIT_TYPE.UNKNOWN

                # count number of lines added and removed
                if hasattr(file, 'additions') and hasattr(file, 'deletions'):
                    num_plus_lines = file.additions
                    num_minus_lines = file.deletions
                else:
                    patch_lines = patch.splitlines(keepends=True)
                    num_plus_lines = len([line for line in patch_lines if line.startswith('+')])
                    num_minus_lines = len([line for line in patch_lines if line.startswith('-')])

                file_patch_canonical_structure = FilePatchInfo(original_file_content_str, new_file_content_str, patch,
                                                               file.filename, edit_type=edit_type,
                                                               num_plus_lines=num_plus_lines,
                                                               num_minus_lines=num_minus_lines,)
                diff_files.append(file_patch_canonical_structure)
            if invalid_files_names:
                get_logger().info(f"Filtered out files with invalid extensions: {invalid_files_names}")

            self.diff_files = diff_files
            try:
                context["diff_files"] = diff_files
            except Exception:
                pass

            return diff_files

        except Exception as e:
            get_logger().error(f"Failing to get diff files: {e}",
                               artifact={"traceback": traceback.format_exc()})
            raise RateLimitExceeded("Rate limit exceeded for GitHub API.") from e

    def publish_description(self, pr_title: str, pr_body: str):
        self.pr.edit(title=pr_title, body=pr_body)

    def get_latest_commit_url(self) -> str:
        return self.last_commit_id.html_url

    def get_comment_url(self, comment) -> str:
        return comment.html_url

    def publish_persistent_comment(self, pr_comment: str,
                                   initial_header: str,
                                   update_header: bool = True,
                                   name='review',
                                   final_update_message=True):
        self.publish_persistent_comment_full(pr_comment, initial_header, update_header, name, final_update_message)

    def publish_comment(self, pr_comment: str, is_temporary: bool = False):
        if not self.pr and not self.issue_main:
            get_logger().error("Cannot publish a comment if missing PR/Issue context")
            return None

        if is_temporary and not get_settings().config.publish_output_progress:
            get_logger().debug(f"Skipping publish_comment for temporary comment: {pr_comment}")
            return None
        pr_comment = self.limit_output_characters(pr_comment, self.max_comment_chars)

        # In case this is an issue, can publish the comment on the issue.
        if self.issue_main:
            return self.issue_main.create_comment(pr_comment)

        response = self.pr.create_issue_comment(pr_comment)
        if hasattr(response, "user") and hasattr(response.user, "login"):
            self.github_user_id = response.user.login
        response.is_temporary = is_temporary
        if not hasattr(self.pr, 'comments_list'):
            self.pr.comments_list = []
        self.pr.comments_list.append(response)
        return response

    def publish_inline_comment(self, body: str, relevant_file: str, relevant_line_in_file: str, original_suggestion=None):
        body = self.limit_output_characters(body, self.max_comment_chars)
        self.publish_inline_comments([self.create_inline_comment(body, relevant_file, relevant_line_in_file)])


    def create_inline_comment(self, body: str, relevant_file: str, relevant_line_in_file: str,
                              absolute_position: int = None):
        body = self.limit_output_characters(body, self.max_comment_chars)
        position, absolute_position = find_line_number_of_relevant_line_in_file(self.diff_files,
                                                                                relevant_file.strip('`'),
                                                                                relevant_line_in_file,
                                                                                absolute_position)
        if position == -1:
            get_logger().info(f"Could not find position for {relevant_file} {relevant_line_in_file}")
            subject_type = "FILE"
        else:
            subject_type = "LINE"
        path = relevant_file.strip()
        return dict(body=body, path=path, position=position) if subject_type == "LINE" else {}

    def publish_inline_comments(self, comments: list[dict], disable_fallback: bool = False):
        try:
            # publish all comments in a single message
            self.pr.create_review(commit=self.last_commit_id, comments=comments)
        except Exception as e:
            get_logger().info(f"Initially failed to publish inline comments as committable")

            if (getattr(e, "status", None) == 422 and not disable_fallback):
                pass  # continue to try _publish_inline_comments_fallback_with_verification
            else:
                raise e # will end up with publishing the comments one by one

            try:
                self._publish_inline_comments_fallback_with_verification(comments)
            except Exception as e:
                get_logger().error(f"Failed to publish inline code comments fallback, error: {e}")
                raise e    
    
    def get_review_thread_comments(self, comment_id: int) -> list[dict]:
        """
        Retrieves all comments in the same thread as the given comment.
        
        Args:
            comment_id: Review comment ID
                
        Returns:
            List of comments in the same thread
        """
        try:
            # Fetch all comments with a single API call
            all_comments = list(self.pr.get_comments())
            
            # Find the target comment by ID
            target_comment = next((c for c in all_comments if c.id == comment_id), None)
            if not target_comment:
                return []
        
            # Get root comment id
            root_comment_id = target_comment.raw_data.get("in_reply_to_id", target_comment.id)
            # Build the thread - include the root comment and all replies to it
            thread_comments = [
                c for c in all_comments if
                c.id == root_comment_id or c.raw_data.get("in_reply_to_id") == root_comment_id
            ]
        
        
            return thread_comments
                
        except Exception as e:
            get_logger().exception(f"Failed to get review comments for an inline ask command", artifact={"comment_id": comment_id, "error": e})
            return []

    def _publish_inline_comments_fallback_with_verification(self, comments: list[dict]):
        """
        Check each inline comment separately against the GitHub API and discard of invalid comments,
        then publish all the remaining valid comments in a single review.
        For invalid comments, also try removing the suggestion part and posting the comment just on the first line.
        """
        verified_comments, invalid_comments = self._verify_code_comments(comments)

        # publish as a group the verified comments
        if verified_comments:
            try:
                self.pr.create_review(commit=self.last_commit_id, comments=verified_comments)
            except:
                pass

        # try to publish one by one the invalid comments as a one-line code comment
        if invalid_comments and get_settings().github.try_fix_invalid_inline_comments:
            fixed_comments_as_one_liner = self._try_fix_invalid_inline_comments(
                [comment for comment, _ in invalid_comments])
            for comment in fixed_comments_as_one_liner:
                try:
                    self.publish_inline_comments([comment], disable_fallback=True)
                    get_logger().info(f"Published invalid comment as a single line comment: {comment}")
                except:
                    get_logger().error(f"Failed to publish invalid comment as a single line comment: {comment}")

    def _verify_code_comment(self, comment: dict):
        is_verified = False
        e = None
        try:
            # event ="" # By leaving this blank, you set the review action state to PENDING
            input = dict(commit_id=self.last_commit_id.sha, comments=[comment])
            headers, data = self.pr._requester.requestJsonAndCheck(
                "POST", f"{self.pr.url}/reviews", input=input)
            pending_review_id = data["id"]
            is_verified = True
        except Exception as err:
            is_verified = False
            pending_review_id = None
            e = err
        if pending_review_id is not None:
            try:
                self.pr._requester.requestJsonAndCheck("DELETE", f"{self.pr.url}/reviews/{pending_review_id}")
            except Exception:
                pass
        return is_verified, e

    def _verify_code_comments(self, comments: list[dict]) -> tuple[list[dict], list[tuple[dict, Exception]]]:
        """Very each comment against the GitHub API and return 2 lists: 1 of verified and 1 of invalid comments"""
        verified_comments = []
        invalid_comments = []
        for comment in comments:
            time.sleep(1)  # for avoiding secondary rate limit
            is_verified, e = self._verify_code_comment(comment)
            if is_verified:
                verified_comments.append(comment)
            else:
                invalid_comments.append((comment, e))
        return verified_comments, invalid_comments

    def _try_fix_invalid_inline_comments(self, invalid_comments: list[dict]) -> list[dict]:
        """
        Try fixing invalid comments by removing the suggestion part and setting the comment just on the first line.
        Return only comments that have been modified in some way.
        This is a best-effort attempt to fix invalid comments, and should be verified accordingly.
        """
        import copy
        fixed_comments = []
        for comment in invalid_comments:
            try:
                fixed_comment = copy.deepcopy(comment)  # avoid modifying the original comment dict for later logging
                if "```suggestion" in comment["body"]:
                    fixed_comment["body"] = comment["body"].split("```suggestion")[0]
                if "start_line" in comment:
                    fixed_comment["line"] = comment["start_line"]
                    del fixed_comment["start_line"]
                if "start_side" in comment:
                    fixed_comment["side"] = comment["start_side"]
                    del fixed_comment["start_side"]
                if fixed_comment != comment:
                    fixed_comments.append(fixed_comment)
            except Exception as e:
                get_logger().error(f"Failed to fix inline comment, error: {e}")
        return fixed_comments

    def publish_code_suggestions(self, code_suggestions: list) -> bool:
        """
        Publishes code suggestions as comments on the PR.
        """
        post_parameters_list = []

        code_suggestions_validated = self.validate_comments_inside_hunks(code_suggestions)

        for suggestion in code_suggestions_validated:
            body = suggestion['body']
            relevant_file = suggestion['relevant_file']
            relevant_lines_start = suggestion['relevant_lines_start']
            relevant_lines_end = suggestion['relevant_lines_end']

            if not relevant_lines_start or relevant_lines_start == -1:
                get_logger().exception(
                    f"Failed to publish code suggestion, relevant_lines_start is {relevant_lines_start}")
                continue

            if relevant_lines_end < relevant_lines_start:
                get_logger().exception(f"Failed to publish code suggestion, "
                                  f"relevant_lines_end is {relevant_lines_end} and "
                                  f"relevant_lines_start is {relevant_lines_start}")
                continue

            if relevant_lines_end > relevant_lines_start:
                post_parameters = {
                    "body": body,
                    "path": relevant_file,
                    "line": relevant_lines_end,
                    "start_line": relevant_lines_start,
                    "start_side": "RIGHT",
                }
            else:  # API is different for single line comments
                post_parameters = {
                    "body": body,
                    "path": relevant_file,
                    "line": relevant_lines_start,
                    "side": "RIGHT",
                }
            post_parameters_list.append(post_parameters)

        try:
            self.publish_inline_comments(post_parameters_list)
            return True
        except Exception as e:
            get_logger().error(f"Failed to publish code suggestion, error: {e}")
            return False

    def edit_comment(self, comment, body: str):
        try:
            body = self.limit_output_characters(body, self.max_comment_chars)
            comment.edit(body=body)
        except GithubException as e:
            if hasattr(e, "status") and e.status == 403:
                # Log as warning for permission-related issues (usually due to polling)
                get_logger().warning(
                    "Failed to edit github comment due to permission restrictions",
                    artifact={"error": e})
            else:
                get_logger().exception(f"Failed to edit github comment", artifact={"error": e})

    def edit_comment_from_comment_id(self, comment_id: int, body: str):
        try:
            # self.pr.get_issue_comment(comment_id).edit(body)
            body = self.limit_output_characters(body, self.max_comment_chars)
            headers, data_patch = self.pr._requester.requestJsonAndCheck(
                "PATCH", f"{self.base_url}/repos/{self.repo}/issues/comments/{comment_id}",
                input={"body": body}
            )
        except Exception as e:
            get_logger().exception(f"Failed to edit comment, error: {e}")

    def reply_to_comment_from_comment_id(self, comment_id: int, body: str):
        try:
            # self.pr.get_issue_comment(comment_id).edit(body)
            body = self.limit_output_characters(body, self.max_comment_chars)
            headers, data_patch = self.pr._requester.requestJsonAndCheck(
                "POST", f"{self.base_url}/repos/{self.repo}/pulls/{self.pr_num}/comments/{comment_id}/replies",
                input={"body": body}
            )
        except Exception as e:
            get_logger().exception(f"Failed to reply comment, error: {e}")

    def get_comment_body_from_comment_id(self, comment_id: int):
        try:
            # self.pr.get_issue_comment(comment_id).edit(body)
            headers, data_patch = self.pr._requester.requestJsonAndCheck(
                "GET", f"{self.base_url}/repos/{self.repo}/issues/comments/{comment_id}"
            )
            return data_patch.get("body","")
        except Exception as e:
            get_logger().exception(f"Failed to edit comment, error: {e}")
            return None

    def publish_file_comments(self, file_comments: list) -> bool:
        try:
            headers, existing_comments = self.pr._requester.requestJsonAndCheck(
                "GET", f"{self.pr.url}/comments"
            )
            for comment in file_comments:
                comment['commit_id'] = self.last_commit_id.sha
                comment['body'] = self.limit_output_characters(comment['body'], self.max_comment_chars)

                found = False
                for existing_comment in existing_comments:
                    comment['commit_id'] = self.last_commit_id.sha
                    our_app_name = get_settings().get("GITHUB.APP_NAME", "")
                    same_comment_creator = False
                    if self.deployment_type == 'app':
                        same_comment_creator = our_app_name.lower() in existing_comment['user']['login'].lower()
                    elif self.deployment_type == 'user':
                        same_comment_creator = self.github_user_id == existing_comment['user']['login']
                    if existing_comment['subject_type'] == 'file' and comment['path'] == existing_comment['path'] and same_comment_creator:

                        headers, data_patch = self.pr._requester.requestJsonAndCheck(
                            "PATCH", f"{self.base_url}/repos/{self.repo}/pulls/comments/{existing_comment['id']}", input={"body":comment['body']}
                        )
                        found = True
                        break
                if not found:
                    headers, data_post = self.pr._requester.requestJsonAndCheck(
                        "POST", f"{self.pr.url}/comments", input=comment
                    )
            return True
        except Exception as e:
            get_logger().error(f"Failed to publish diffview file summary, error: {e}")
            return False

    def remove_initial_comment(self):
        try:
            for comment in getattr(self.pr, 'comments_list', []):
                if comment.is_temporary:
                    self.remove_comment(comment)
        except Exception as e:
            get_logger().exception(f"Failed to remove initial comment, error: {e}")

    def remove_comment(self, comment):
        try:
            comment.delete()
        except Exception as e:
            get_logger().exception(f"Failed to remove comment, error: {e}")

    def get_title(self):
        return self.pr.title

    def get_languages(self):
        languages = self._get_repo().get_languages()
        return languages

    def get_pr_branch(self):
        return self.pr.head.ref

    def get_pr_owner_id(self) -> str | None:
        if not self.repo:
            return None
        return self.repo.split('/')[0]

    def get_pr_description_full(self):
        return self.pr.body

    def get_user_id(self):
        if not self.github_user_id:
            try:
                self.github_user_id = self.github_client.get_user().raw_data['login']
            except Exception as e:
                self.github_user_id = ""
                # logging.exception(f"Failed to get user id, error: {e}")
        return self.github_user_id

    def get_notifications(self, since: datetime):
        deployment_type = get_settings().get("GITHUB.DEPLOYMENT_TYPE", "user")

        if deployment_type != 'user':
            raise ValueError("Deployment mode must be set to 'user' to get notifications")

        notifications = self.github_client.get_user().get_notifications(since=since)
        return notifications

    def get_issue_comments(self):
        return self.pr.get_issue_comments()

    def get_repo_settings(self):
        try:
            # contents = self.repo_obj.get_contents(".pr_agent.toml", ref=self.pr.head.sha).decoded_content

            # more logical to take 'pr_agent.toml' from the default branch
            contents = self.repo_obj.get_contents(".pr_agent.toml").decoded_content
            return contents
        except Exception:
            return ""

    def get_workspace_name(self):
        return self.repo.split('/')[0]

    def add_eyes_reaction(self, issue_comment_id: int, disable_eyes: bool = False) -> Optional[int]:
        if disable_eyes:
            return None
        try:
            headers, data_patch = self.pr._requester.requestJsonAndCheck(
                "POST", f"{self.base_url}/repos/{self.repo}/issues/comments/{issue_comment_id}/reactions",
                input={"content": "eyes"}
            )
            return data_patch.get("id", None)
        except Exception as e:
            get_logger().warning(f"Failed to add eyes reaction, error: {e}")
            return None

    def remove_reaction(self, issue_comment_id: int, reaction_id: str) -> bool:
        try:
            # self.pr.get_issue_comment(issue_comment_id).delete_reaction(reaction_id)
            headers, data_patch = self.pr._requester.requestJsonAndCheck(
                "DELETE",
                f"{self.base_url}/repos/{self.repo}/issues/comments/{issue_comment_id}/reactions/{reaction_id}"
            )
            return True
        except Exception as e:
            get_logger().exception(f"Failed to remove eyes reaction, error: {e}")
            return False

    def _parse_pr_url(self, pr_url: str) -> Tuple[str, int]:
        parsed_url = urlparse(pr_url)

        if parsed_url.path.startswith('/api/v3'):
            parsed_url = urlparse(pr_url.replace("/api/v3", ""))

        path_parts = parsed_url.path.strip('/').split('/')
        if 'api.github.com' in parsed_url.netloc or '/api/v3' in pr_url:
            if len(path_parts) < 5 or path_parts[3] != 'pulls':
                raise ValueError("The provided URL does not appear to be a GitHub PR URL")
            repo_name = '/'.join(path_parts[1:3])
            try:
                pr_number = int(path_parts[4])
            except ValueError as e:
                raise ValueError("Unable to convert PR number to integer") from e
            return repo_name, pr_number

        if len(path_parts) < 4 or path_parts[2] != 'pull':
            raise ValueError("The provided URL does not appear to be a GitHub PR URL")

        repo_name = '/'.join(path_parts[:2])
        try:
            pr_number = int(path_parts[3])
        except ValueError as e:
            raise ValueError("Unable to convert PR number to integer") from e

        return repo_name, pr_number

    def _parse_issue_url(self, issue_url: str) -> Tuple[str, int]:
        parsed_url = urlparse(issue_url)

        if parsed_url.path.startswith('/api/v3'): #Check if came from github app
            parsed_url = urlparse(issue_url.replace("/api/v3", ""))

        path_parts = parsed_url.path.strip('/').split('/')
        if 'api.github.com' in parsed_url.netloc or '/api/v3' in issue_url: #Check if came from github app
            if len(path_parts) < 5 or path_parts[3] != 'issues':
                raise ValueError("The provided URL does not appear to be a GitHub ISSUE URL")
            repo_name = '/'.join(path_parts[1:3])
            try:
                issue_number = int(path_parts[4])
            except ValueError as e:
                raise ValueError("Unable to convert issue number to integer") from e
            return repo_name, issue_number

        if len(path_parts) < 4 or path_parts[2] != 'issues':
            raise ValueError("The provided URL does not appear to be a GitHub PR issue")

        repo_name = '/'.join(path_parts[:2])
        try:
            issue_number = int(path_parts[3])
        except ValueError as e:
            raise ValueError("Unable to convert issue number to integer") from e

        return repo_name, issue_number

    def _get_github_client(self):
        self.deployment_type = get_settings().get("GITHUB.DEPLOYMENT_TYPE", "user")
        self.auth = None
        if self.deployment_type == 'app':
            try:
                private_key = get_settings().github.private_key
                app_id = get_settings().github.app_id
            except AttributeError as e:
                raise ValueError("GitHub app ID and private key are required when using GitHub app deployment") from e
            if not self.installation_id:
                raise ValueError("GitHub app installation ID is required when using GitHub app deployment")
            auth = AppAuthentication(app_id=app_id, private_key=private_key,
                                     installation_id=self.installation_id)
            self.auth = auth
        elif self.deployment_type == 'user':
            try:
                token = get_settings().github.user_token
            except AttributeError as e:
                raise ValueError(
                    "GitHub token is required when using user deployment. See: "
                    "https://github.com/Codium-ai/pr-agent#method-2-run-from-source") from e
            self.auth = Auth.Token(token)
        if self.auth:
            return Github(auth=self.auth, base_url=self.base_url)
        else:
            raise ValueError("Could not authenticate to GitHub")

    def _get_repo(self):
        if hasattr(self, 'repo_obj') and \
                hasattr(self.repo_obj, 'full_name') and \
                self.repo_obj.full_name == self.repo:
            return self.repo_obj
        else:
            self.repo_obj = self.github_client.get_repo(self.repo)
            return self.repo_obj


    def _get_pr(self):
        return self._get_repo().get_pull(self.pr_num)

    def get_pr_file_content(self, file_path: str, branch: str) -> str:
        try:
            file_content_str = str(
                self._get_repo()
                .get_contents(file_path, ref=branch)
                .decoded_content.decode()
            )
        except Exception:
            file_content_str = ""
        return file_content_str

    def create_or_update_pr_file(
        self, file_path: str, branch: str, contents="", message=""
    ) -> None:
        try:
            file_obj = self._get_repo().get_contents(file_path, ref=branch)
            sha1=file_obj.sha
        except Exception:
            sha1=""
        self.repo_obj.update_file(
            path=file_path,
            message=message,
            content=contents,
            sha=sha1,
            branch=branch,
        )

    def _get_pr_file_content(self, file: FilePatchInfo, sha: str) -> str:
        return self.get_pr_file_content(file.filename, sha)

    def publish_labels(self, pr_types):
        try:
            label_color_map = {"Bug fix": "1d76db", "Tests": "e99695", "Bug fix with tests": "c5def5",
                               "Enhancement": "bfd4f2", "Documentation": "d4c5f9",
                               "Other": "d1bcf9"}
            post_parameters = []
            for p in pr_types:
                color = label_color_map.get(p, "d1bcf9")  # default to "Other" color
                post_parameters.append({"name": p, "color": color})
            headers, data = self.pr._requester.requestJsonAndCheck(
                "PUT", f"{self.pr.issue_url}/labels", input=post_parameters
            )
        except Exception as e:
            get_logger().warning(f"Failed to publish labels, error: {e}")

    def get_pr_labels(self, update=False):
        try:
            if not update:
                labels =self.pr.labels
                return [label.name for label in labels]
            else: # obtain the latest labels. Maybe they changed while the AI was running
                headers, labels = self.pr._requester.requestJsonAndCheck(
                    "GET", f"{self.pr.issue_url}/labels")
                return [label['name'] for label in labels]

        except Exception as e:
            get_logger().exception(f"Failed to get labels, error: {e}")
            return []

    def get_repo_labels(self):
        labels = self.repo_obj.get_labels()
        return [label for label in itertools.islice(labels, 50)]

    def get_commit_messages(self):
        """
        Retrieves the commit messages of a pull request.

        Returns:
            str: A string containing the commit messages of the pull request.
        """
        max_tokens = get_settings().get("CONFIG.MAX_COMMITS_TOKENS", None)
        try:
            commit_list = self.pr.get_commits()
            commit_messages = [commit.commit.message for commit in commit_list]
            commit_messages_str = "\n".join([f"{i + 1}. {message}" for i, message in enumerate(commit_messages)])
        except Exception:
            commit_messages_str = ""
        if max_tokens:
            commit_messages_str = clip_tokens(commit_messages_str, max_tokens)
        return commit_messages_str

    def generate_link_to_relevant_line_number(self, suggestion) -> str:
        try:
            relevant_file = suggestion['relevant_file'].strip('`').strip("'").strip('\n')
            relevant_line_str = suggestion['relevant_line'].strip('\n')
            if not relevant_line_str:
                return ""

            position, absolute_position = find_line_number_of_relevant_line_in_file \
                (self.diff_files, relevant_file, relevant_line_str)

            if absolute_position != -1:
                # # link to right file only
                # link = f"https://github.com/{self.repo}/blob/{self.pr.head.sha}/{relevant_file}" \
                #        + "#" + f"L{absolute_position}"

                # link to diff
                sha_file = hashlib.sha256(relevant_file.encode('utf-8')).hexdigest()
                link = f"{self.base_url_html}/{self.repo}/pull/{self.pr_num}/files#diff-{sha_file}R{absolute_position}"
                return link
        except Exception as e:
            get_logger().info(f"Failed adding line link, error: {e}")

        return ""

    def get_line_link(self, relevant_file: str, relevant_line_start: int, relevant_line_end: int = None) -> str:
        sha_file = hashlib.sha256(relevant_file.encode('utf-8')).hexdigest()
        if relevant_line_start == -1:
            link = f"{self.base_url_html}/{self.repo}/pull/{self.pr_num}/files#diff-{sha_file}"
        elif relevant_line_end:
            link = f"{self.base_url_html}/{self.repo}/pull/{self.pr_num}/files#diff-{sha_file}R{relevant_line_start}-R{relevant_line_end}"
        else:
            link = f"{self.base_url_html}/{self.repo}/pull/{self.pr_num}/files#diff-{sha_file}R{relevant_line_start}"
        return link

    def get_lines_link_original_file(self, filepath: str, component_range: Range) -> str:
        """
        Returns the link to the original file on GitHub that corresponds to the given filepath and component range.

        Args:
            filepath (str): The path of the file.
            component_range (Range): The range of lines that represent the component.

        Returns:
            str: The link to the original file on GitHub.

        Example:
            >>> filepath = "path/to/file.py"
            >>> component_range = Range(line_start=10, line_end=20)
            >>> link = get_lines_link_original_file(filepath, component_range)
            >>> print(link)
            "https://github.com/{repo}/blob/{commit_sha}/{filepath}/#L11-L21"
        """
        line_start = component_range.line_start + 1
        line_end = component_range.line_end + 1
        # link = (f"https://github.com/{self.repo}/blob/{self.last_commit_id.sha}/{filepath}/"
        #         f"#L{line_start}-L{line_end}")
        link = (f"{self.base_url_html}/{self.repo}/blob/{self.last_commit_id.sha}/{filepath}/"
                f"#L{line_start}-L{line_end}")

        return link

    def get_pr_id(self):
        try:
            pr_id = f"{self.repo}/{self.pr_num}"
            return pr_id
        except:
            return ""

    def fetch_sub_issues(self, issue_url):
        """
        Fetch sub-issues linked to the given GitHub issue URL using GraphQL via PyGitHub.
        """
        sub_issues = set()

        # Extract owner, repo, and issue number from URL
        parts = issue_url.rstrip("/").split("/")
        owner, repo, issue_number = parts[-4], parts[-3], parts[-1]

        try:
            # Gets Issue ID from Issue Number
            query = f"""
            query {{
                repository(owner: "{owner}", name: "{repo}") {{
                    issue(number: {issue_number}) {{
                        id
                    }}
                }}
            }}
            """
            response_tuple = self.github_client._Github__requester.requestJson("POST", "/graphql",
                                                                               input={"query": query})

            # Extract the JSON response from the tuple and parses it
            if isinstance(response_tuple, tuple) and len(response_tuple) == 3:
                response_json = json.loads(response_tuple[2])
            else:
                get_logger().error(f"Unexpected response format: {response_tuple}")
                return sub_issues


            issue_id = response_json.get("data", {}).get("repository", {}).get("issue", {}).get("id")

            if not issue_id:
                get_logger().warning(f"Issue ID not found for {issue_url}")
                return sub_issues

            # Fetch Sub-Issues
            sub_issues_query = f"""
            query {{
                node(id: "{issue_id}") {{
                    ... on Issue {{
                        subIssues(first: 10) {{
                            nodes {{
                                url
                            }}
                        }}
                    }}
                }}
            }}
            """
            sub_issues_response_tuple = self.github_client._Github__requester.requestJson("POST", "/graphql", input={
                "query": sub_issues_query})

            # Extract the JSON response from the tuple and parses it
            if isinstance(sub_issues_response_tuple, tuple) and len(sub_issues_response_tuple) == 3:
                sub_issues_response_json = json.loads(sub_issues_response_tuple[2])
            else:
                get_logger().error("Unexpected sub-issues response format", artifact={"response": sub_issues_response_tuple})
                return sub_issues

            if not sub_issues_response_json.get("data", {}).get("node", {}).get("subIssues"):
                get_logger().error("Invalid sub-issues response structure")
                return sub_issues
    
            nodes = sub_issues_response_json.get("data", {}).get("node", {}).get("subIssues", {}).get("nodes", [])
            get_logger().info(f"Github Sub-issues fetched: {len(nodes)}", artifact={"nodes": nodes})

            for sub_issue in nodes:
                if "url" in sub_issue:
                    sub_issues.add(sub_issue["url"])

        except Exception as e:
            get_logger().exception(f"Failed to fetch sub-issues. Error: {e}")

        return sub_issues

    def auto_approve(self) -> bool:
        try:
            res = self.pr.create_review(event="APPROVE")
            if res.state == "APPROVED":
                return True
            return False
        except Exception as e:
            get_logger().exception(f"Failed to auto-approve, error: {e}")
            return False

    def calc_pr_statistics(self, pull_request_data: dict):
            return {}

    def validate_comments_inside_hunks(self, code_suggestions):
        """
        validate that all committable comments are inside PR hunks - this is a must for committable comments in GitHub
        """
        code_suggestions_copy = copy.deepcopy(code_suggestions)
        diff_files = self.get_diff_files()
        RE_HUNK_HEADER = re.compile(
            r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@[ ]?(.*)")

        diff_files = set_file_languages(diff_files)

        for suggestion in code_suggestions_copy:
            try:
                relevant_file_path = suggestion['relevant_file']
                for file in diff_files:
                    if file.filename == relevant_file_path:

                        # generate on-demand the patches range for the relevant file
                        patch_str = file.patch
                        if not hasattr(file, 'patches_range'):
                            file.patches_range = []
                            patch_lines = patch_str.splitlines()
                            for i, line in enumerate(patch_lines):
                                if line.startswith('@@'):
                                    match = RE_HUNK_HEADER.match(line)
                                    # identify hunk header
                                    if match:
                                        section_header, size1, size2, start1, start2 = extract_hunk_headers(match)
                                        file.patches_range.append({'start': start2, 'end': start2 + size2 - 1})

                        patches_range = file.patches_range
                        comment_start_line = suggestion.get('relevant_lines_start', None)
                        comment_end_line = suggestion.get('relevant_lines_end', None)
                        original_suggestion = suggestion.get('original_suggestion', None) # needed for diff code
                        if not comment_start_line or not comment_end_line or not original_suggestion:
                            continue

                        # check if the comment is inside a valid hunk
                        is_valid_hunk = False
                        min_distance = float('inf')
                        patch_range_min = None
                        # find the hunk that contains the comment, or the closest one
                        for i, patch_range in enumerate(patches_range):
                            d1 = comment_start_line - patch_range['start']
                            d2 = patch_range['end'] - comment_end_line
                            if d1 >= 0 and d2 >= 0:  # found a valid hunk
                                is_valid_hunk = True
                                min_distance = 0
                                patch_range_min = patch_range
                                break
                            elif d1 * d2 <= 0:  # comment is possibly inside the hunk
                                d1_clip = abs(min(0, d1))
                                d2_clip = abs(min(0, d2))
                                d = max(d1_clip, d2_clip)
                                if d < min_distance:
                                    patch_range_min = patch_range
                                    min_distance = min(min_distance, d)
                        if not is_valid_hunk:
                            if min_distance < 10:  # 10 lines - a reasonable distance to consider the comment inside the hunk
                                # make the suggestion non-committable, yet multi line
                                suggestion['relevant_lines_start'] = max(suggestion['relevant_lines_start'], patch_range_min['start'])
                                suggestion['relevant_lines_end'] = min(suggestion['relevant_lines_end'], patch_range_min['end'])
                                body = suggestion['body'].strip()

                                # present new diff code in collapsible
                                existing_code = original_suggestion['existing_code'].rstrip() + "\n"
                                improved_code = original_suggestion['improved_code'].rstrip() + "\n"
                                diff = difflib.unified_diff(existing_code.split('\n'),
                                                            improved_code.split('\n'), n=999)
                                patch_orig = "\n".join(diff)
                                patch = "\n".join(patch_orig.splitlines()[5:]).strip('\n')
                                diff_code = f"\n\n<details><summary>New proposed code:</summary>\n\n```diff\n{patch.rstrip()}\n```"
                                # replace ```suggestion ... ``` with diff_code, using regex:
                                body = re.sub(r'```suggestion.*?```', diff_code, body, flags=re.DOTALL)
                                body += "\n\n</details>"
                                suggestion['body'] = body
                                get_logger().info(f"Comment was moved to a valid hunk, "
                                                  f"start_line={suggestion['relevant_lines_start']}, end_line={suggestion['relevant_lines_end']}, file={file.filename}")
                            else:
                                get_logger().error(f"Comment is not inside a valid hunk, "
                                                   f"start_line={suggestion['relevant_lines_start']}, end_line={suggestion['relevant_lines_end']}, file={file.filename}")
            except Exception as e:
                get_logger().error(f"Failed to process patch for committable comment, error: {e}")
        return code_suggestions_copy

    #Clone related
    def _prepare_clone_url_with_token(self, repo_url_to_clone: str) -> str | None:
        scheme = "https://"

        #For example, to clone:
        #https://github.com/Codium-ai/pr-agent-pro.git
        #Need to embed inside the github token:
        #https://<token>@github.com/Codium-ai/pr-agent-pro.git

        github_token = self.auth.token
        github_base_url = self.base_url_html
        if not all([github_token, github_base_url]):
            get_logger().error("Either missing auth token or missing base url")
            return None
        if scheme not in github_base_url:
            get_logger().error(f"Base url: {github_base_url} is missing prefix: {scheme}")
            return None
        github_com = github_base_url.split(scheme)[1]  # e.g. 'github.com' or github.<org>.com
        if not github_com:
            get_logger().error(f"Base url: {github_base_url} has an empty base url")
            return None
        if github_com not in repo_url_to_clone:
            get_logger().error(f"url to clone: {repo_url_to_clone} does not contain {github_com}")
            return None
        repo_full_name = repo_url_to_clone.split(github_com)[-1]
        if not repo_full_name:
            get_logger().error(f"url to clone: {repo_url_to_clone} is malformed")
            return None

        clone_url = scheme
        if self.deployment_type == 'app':
            clone_url += "git:"
        clone_url += f"{github_token}@{github_com}{repo_full_name}"
        return clone_url


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