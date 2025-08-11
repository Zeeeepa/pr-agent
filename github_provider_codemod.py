#!/usr/bin/env python3
"""
Advanced GitHub Provider Codemod using Tree-sitter

This script creates a fully functional standalone GitHub provider module
by intelligently extracting, adapting, and consolidating all dependencies.
"""

import os
import re
import ast
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass
from collections import defaultdict

try:
    import tree_sitter_python as tspython
    from tree_sitter import Language, Parser, Node
except ImportError:
    print("Error: tree-sitter-python not installed. Run: pip install tree-sitter tree-sitter-python")
    sys.exit(1)


class GitHubProviderCodemod:
    """Advanced codemod to create standalone GitHub provider"""
    
    def __init__(self, pr_agent_root: str):
        self.pr_agent_root = Path(pr_agent_root)
        self.parser = Parser(Language(tspython.language()))
        
        # Core files to extract
        self.core_files = {
            "pr_agent/git_providers/github_provider.py": "github_provider",
            "pr_agent/git_providers/git_provider.py": "git_provider", 
            "pr_agent/algo/types.py": "types",
            "pr_agent/algo/file_filter.py": "file_filter",
            "pr_agent/algo/git_patch_processing.py": "git_patch_processing",
            "pr_agent/algo/language_handler.py": "language_handler",
            "pr_agent/algo/utils.py": "utils",
            "pr_agent/config_loader.py": "config_loader",
            "pr_agent/log/__init__.py": "logging",
            "pr_agent/servers/utils.py": "server_utils",
        }
        
        # Track extracted code
        self.extracted_code = {}
        self.dependencies = defaultdict(set)
        
    def read_file(self, file_path: str) -> str:
        """Read file content"""
        full_path = self.pr_agent_root / file_path
        if not full_path.exists():
            return ""
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def parse_file(self, file_path: str) -> Tuple[Node, str]:
        """Parse file and return AST and source"""
        source = self.read_file(file_path)
        if not source:
            return None, ""
        tree = self.parser.parse(bytes(source, 'utf8'))
        return tree.root_node, source
    
    def extract_imports(self, node: Node, source: str) -> List[str]:
        """Extract import statements"""
        imports = []
        
        def visit_node(n: Node):
            if n.type in ['import_statement', 'import_from_statement']:
                import_text = source[n.start_byte:n.end_byte].strip()
                imports.append(import_text)
            for child in n.children:
                visit_node(child)
        
        visit_node(node)
        return imports
    
    def extract_definitions(self, node: Node, source: str) -> Dict[str, str]:
        """Extract class and function definitions"""
        definitions = {}
        
        def visit_node(n: Node):
            if n.type in ['class_definition', 'function_definition']:
                # Get the name
                name = None
                for child in n.children:
                    if child.type == 'identifier':
                        name = source[child.start_byte:child.end_byte]
                        break
                
                if name:
                    def_source = source[n.start_byte:n.end_byte]
                    definitions[name] = def_source
            
            # Also extract constants and enums at module level
            elif n.type == 'assignment':
                assign_text = source[n.start_byte:n.end_byte]
                if re.match(r'^[A-Z_][A-Z0-9_]*\s*=', assign_text):
                    var_name = assign_text.split('=')[0].strip()
                    definitions[var_name] = assign_text
            
            for child in n.children:
                visit_node(child)
        
        visit_node(node)
        return definitions
    
    def create_simplified_config(self) -> str:
        """Create a simplified configuration system"""
        return '''
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
'''
    
    def create_simplified_logging(self) -> str:
        """Create simplified logging system"""
        return '''
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
'''
    
    def create_context_stub(self) -> str:
        """Create starlette context stub"""
        return '''
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
'''
    
    def adapt_imports(self, source: str) -> str:
        """Adapt imports to work in standalone module"""
        lines = source.split('\n')
        adapted_lines = []
        
        for line in lines:
            # Skip pr_agent internal imports
            if re.match(r'from\s+pr_agent\.|from\s+\.\.|import\s+pr_agent', line):
                continue
            
            # Skip starlette_context import
            if 'starlette_context' in line:
                continue
                
            # Skip dynaconf import
            if 'dynaconf' in line:
                continue
                
            # Adapt specific imports
            if 'from pr_agent.config_loader import get_settings' in line:
                continue  # We'll define our own
            
            if 'from pr_agent.log import get_logger' in line:
                continue  # We'll define our own
                
            adapted_lines.append(line)
        
        return '\n'.join(adapted_lines)
    
    def adapt_code(self, source: str, module_name: str) -> str:
        """Adapt code to work in standalone context"""
        # Remove internal imports and adapt references
        adapted = self.adapt_imports(source)
        
        # Fix specific patterns
        patterns = [
            # Remove context usage that's not needed
            (r'context\.get\([^)]+\)', 'None'),
            # Simplify settings access
            (r'get_settings\(\)\.get\(([^)]+)\)', r'get_settings().get(\1)'),
        ]
        
        for pattern, replacement in patterns:
            adapted = re.sub(pattern, replacement, adapted)
        
        return adapted
    
    def extract_essential_functions(self, source: str) -> List[str]:
        """Extract only essential utility functions"""
        tree = self.parser.parse(bytes(source, 'utf8'))
        root = tree.root_node
        
        # Essential functions we need
        essential_funcs = {
            'clip_tokens', 'find_line_number_of_relevant_line_in_file',
            'load_large_diff', 'set_file_languages', 'extract_hunk_headers',
            'filter_ignored', 'is_valid_file', 'sort_files_by_main_languages',
            'get_main_pr_language', 'emphasize_header', 'get_model'
        }
        
        extracted = []
        
        def visit_node(n: Node):
            if n.type == 'function_definition':
                # Get function name
                for child in n.children:
                    if child.type == 'identifier':
                        func_name = source[child.start_byte:child.end_byte]
                        if func_name in essential_funcs:
                            func_source = source[n.start_byte:n.end_byte]
                            extracted.append(func_source)
                        break
            
            for child in n.children:
                visit_node(child)
        
        visit_node(root)
        return extracted
    
    def generate_standalone_module(self) -> str:
        """Generate the complete standalone module"""
        output = []
        
        # Header
        output.extend([
            '#!/usr/bin/env python3',
            '"""',
            'Standalone GitHub Provider Module',
            '',
            'This module contains all necessary code to use the GitHub provider',
            'from pr-agent as a standalone component.',
            '',
            'Usage:',
            '    from github_provider_standalone import GitHubProvider',
            '    ',
            '    provider = GitHubProvider("https://github.com/owner/repo/pull/123")',
            '    files = provider.get_diff_files()',
            '',
            'Original source: https://github.com/qodo-ai/pr-agent',
            '"""',
            '',
        ])
        
        # Standard library imports
        std_imports = [
            'import copy', 'import difflib', 'import hashlib', 'import itertools',
            'import re', 'import time', 'import traceback', 'import json', 'import os',
            'import shutil', 'import subprocess', 'import sys', 'import textwrap',
            'from datetime import datetime', 'from typing import Optional, Tuple, List, Dict, Any',
            'from urllib.parse import urlparse', 'from abc import ABC, abstractmethod',
            'from dataclasses import dataclass', 'from enum import Enum', 'import fnmatch',
            'import logging', 'from pathlib import Path'
        ]
        
        output.extend(std_imports)
        output.append('')
        
        # External dependencies with error handling
        output.extend([
            '# External dependencies (with graceful fallbacks)',
            'try:',
            '    from github.Issue import Issue',
            '    from github import AppAuthentication, Auth, Github, GithubException',
            '    HAS_GITHUB = True',
            'except ImportError:',
            '    print("Warning: PyGithub not installed. Install with: pip install PyGithub")',
            '    HAS_GITHUB = False',
            '',
            'try:',
            '    from retry import retry',
            '    HAS_RETRY = True',
            'except ImportError:',
            '    # Simple retry decorator fallback',
            '    def retry(*args, **kwargs):',
            '        def decorator(func):',
            '            return func',
            '        return decorator',
            '    HAS_RETRY = False',
            '',
            'try:',
            '    from pydantic import BaseModel',
            '    HAS_PYDANTIC = True',
            'except ImportError:',
            '    # Simple BaseModel fallback',
            '    class BaseModel:',
            '        pass',
            '    HAS_PYDANTIC = False',
            '',
        ])
        
        # Add simplified configuration
        output.append(self.create_simplified_config())
        output.append('')
        
        # Add simplified logging
        output.append(self.create_simplified_logging())
        output.append('')
        
        # Add context stub
        output.append(self.create_context_stub())
        output.append('')
        
        # Extract and add core types
        types_source = self.read_file("pr_agent/algo/types.py")
        if types_source:
            adapted_types = self.adapt_code(types_source, "types")
            output.append("# Core Data Types")
            output.append(adapted_types)
            output.append('')
        
        # Add essential utility functions
        utils_source = self.read_file("pr_agent/algo/utils.py")
        if utils_source:
            essential_funcs = self.extract_essential_functions(utils_source)
            if essential_funcs:
                output.append("# Essential Utility Functions")
                for func in essential_funcs:
                    adapted_func = self.adapt_code(func, "utils")
                    output.append(adapted_func)
                    output.append('')
        
        # Add algorithmic modules
        for file_path, module_name in [
            ("pr_agent/algo/file_filter.py", "file_filter"),
            ("pr_agent/algo/git_patch_processing.py", "git_patch_processing"),
            ("pr_agent/algo/language_handler.py", "language_handler"),
            ("pr_agent/servers/utils.py", "server_utils"),
        ]:
            source = self.read_file(file_path)
            if source:
                adapted = self.adapt_code(source, module_name)
                output.append(f"# {module_name.replace('_', ' ').title()} Module")
                output.append(adapted)
                output.append('')
        
        # Add base GitProvider class
        git_provider_source = self.read_file("pr_agent/git_providers/git_provider.py")
        if git_provider_source:
            adapted_git_provider = self.adapt_code(git_provider_source, "git_provider")
            output.append("# Base Git Provider")
            output.append(adapted_git_provider)
            output.append('')
        
        # Add GitHub provider
        github_provider_source = self.read_file("pr_agent/git_providers/github_provider.py")
        if github_provider_source:
            adapted_github_provider = self.adapt_code(github_provider_source, "github_provider")
            output.append("# GitHub Provider Implementation")
            output.append(adapted_github_provider)
            output.append('')
        
        # Add example usage
        output.extend([
            '# Example Usage and Testing',
            'def test_github_provider():',
            '    """Test the GitHub provider functionality"""',
            '    if not HAS_GITHUB:',
            '        print("Cannot test: PyGithub not available")',
            '        return False',
            '    ',
            '    try:',
            '        # Test basic instantiation',
            '        provider = GitHubProvider()',
            '        print("✓ GitHubProvider instantiated successfully")',
            '        ',
            '        # Test with a PR URL (requires authentication)',
            '        # provider = GitHubProvider("https://github.com/owner/repo/pull/123")',
            '        # files = provider.get_diff_files()',
            '        # print(f"✓ Found {len(files)} files in PR")',
            '        ',
            '        return True',
            '    except Exception as e:',
            '        print(f"✗ Test failed: {e}")',
            '        return False',
            '',
            'if __name__ == "__main__":',
            '    print("GitHub Provider Standalone Module")',
            '    print("=" * 40)',
            '    print(f"PyGithub available: {HAS_GITHUB}")',
            '    print(f"Retry decorator available: {HAS_RETRY}")',
            '    print(f"Pydantic available: {HAS_PYDANTIC}")',
            '    print()',
            '    ',
            '    # Run basic test',
            '    success = test_github_provider()',
            '    print(f"\\nTest result: {\'PASSED\' if success else \'FAILED\'}")',
            '    ',
            '    # Show available classes',
            '    print("\\nAvailable classes:")',
            '    for name in dir():',
            '        obj = globals()[name]',
            '        if isinstance(obj, type) and not name.startswith("_"):',
            '            print(f"  - {name}")',
        ])
        
        return '\n'.join(output)
    
    def run(self) -> str:
        """Run the codemod and generate standalone module"""
        print("Generating standalone GitHub provider module...")
        
        # Generate the complete module
        standalone_code = self.generate_standalone_module()
        
        print(f"Generated standalone module ({len(standalone_code)} characters)")
        return standalone_code


def main():
    """Main execution"""
    if len(sys.argv) > 1:
        pr_agent_root = sys.argv[1]
    else:
        pr_agent_root = "."
    
    codemod = GitHubProviderCodemod(pr_agent_root)
    standalone_code = codemod.run()
    
    # Write output
    output_file = "github_provider_standalone_complete.py"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(standalone_code)
    
    print(f"Complete standalone module written to: {output_file}")
    
    # Also create a requirements.txt
    requirements = [
        "PyGithub>=1.55.0",
        "retry>=0.9.2", 
        "pydantic>=1.8.0",
        "requests>=2.25.0",
    ]
    
    with open("requirements_github_provider.txt", 'w') as f:
        f.write('\n'.join(requirements))
    
    print("Requirements written to: requirements_github_provider.txt")


if __name__ == "__main__":
    main()
