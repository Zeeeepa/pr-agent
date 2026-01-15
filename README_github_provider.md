# Standalone GitHub Provider Module

This module contains a fully functional standalone GitHub provider extracted from the [pr-agent](https://github.com/qodo-ai/pr-agent) project using tree-sitter based code analysis and consolidation.

## Features

✅ **Complete GitHub API Integration** - Full GitHub provider functionality  
✅ **Zero Internal Dependencies** - No pr-agent dependencies required  
✅ **Simplified Configuration** - Easy-to-use configuration system  
✅ **Graceful Fallbacks** - Works with or without optional dependencies  
✅ **Tree-sitter Generated** - Programmatically extracted and consolidated  

## Installation

### Required Dependencies
```bash
pip install PyGithub>=2.0.0
```

### Optional Dependencies
```bash
pip install retry>=0.9.2 pydantic>=1.8.0
```

## Quick Start

```python
from github_provider_final import GitHubProvider
import os

# Set your GitHub token
os.environ['GITHUB_TOKEN'] = 'your_github_token_here'

# Initialize with a PR URL
provider = GitHubProvider("https://github.com/owner/repo/pull/123")

# Get diff files
files = provider.get_diff_files()
print(f"Found {len(files)} changed files")

# Get PR information
print(f"PR URL: {provider.get_pr_url()}")
print(f"PR Branch: {provider.get_pr_branch()}")
print(f"Languages: {provider.get_languages()}")

# Work with files
for file in files:
    print(f"File: {file.filename}")
    print(f"  Type: {file.edit_type}")
    print(f"  +{file.num_plus_lines} -{file.num_minus_lines}")
```

## Core Classes

### GitHubProvider
Main class for GitHub API interactions.

```python
provider = GitHubProvider(pr_url="https://github.com/owner/repo/pull/123")

# Core methods
files = provider.get_diff_files()          # Get changed files
languages = provider.get_languages()       # Get repo languages  
comments = provider.get_issue_comments()   # Get PR comments
provider.publish_comment("Hello!")         # Add comment
provider.publish_labels(["bug", "fix"])    # Add labels
```

### FilePatchInfo
Data class representing a file change.

```python
@dataclass
class FilePatchInfo:
    filename: str           # File path
    patch: str             # Git patch content
    edit_type: EDIT_TYPE   # ADDED, DELETED, MODIFIED, RENAMED
    num_plus_lines: int    # Lines added
    num_minus_lines: int   # Lines removed
    language: str          # Programming language
```

### Configuration
Simplified configuration system.

```python
from github_provider_final import get_settings

config = get_settings()
config.get("GITHUB.BASE_URL")  # "https://api.github.com"
config.get("config.model")     # "gpt-4"
```

## Advanced Usage

### Custom Configuration
```python
from github_provider_final import get_settings

# Modify configuration
settings = get_settings()
settings._config["GITHUB.BASE_URL"] = "https://github.enterprise.com/api/v3"
settings._config["config"]["verbosity_level"] = 2
```

### File Filtering
```python
from github_provider_final import filter_ignored, is_valid_file

# Filter files based on ignore patterns
filtered_files = filter_ignored(files, platform='github')

# Check if file is valid (not in bad extensions)
if is_valid_file("script.py"):
    print("Valid Python file")
```

### Language Detection
```python
from github_provider_final import set_file_languages

# Set language for files based on extensions
files_with_languages = set_file_languages(files)
```

## Authentication

The module supports multiple authentication methods:

### Environment Variables
```bash
export GITHUB_TOKEN="your_token_here"
# or
export GITHUB_ACCESS_TOKEN="your_token_here"
```

### GitHub App Authentication
```python
# For GitHub Apps (requires additional setup)
provider = GitHubProvider()
# The module will automatically detect app authentication if configured
```

## Error Handling

The module includes comprehensive error handling:

```python
try:
    provider = GitHubProvider("https://github.com/owner/repo/pull/123")
    files = provider.get_diff_files()
except Exception as e:
    print(f"Error: {e}")
```

## Logging

Built-in logging with configurable levels:

```python
from github_provider_final import get_logger

logger = get_logger()
logger.info("Processing PR...")
logger.error("Failed to fetch files")
```

## Tree-sitter Generation

This module was generated using tree-sitter for precise code extraction:

```bash
# Generate the module (if you have the pr-agent source)
python github_provider_codemod.py /path/to/pr-agent

# The generated module includes:
# - All necessary classes and functions
# - Simplified configuration system  
# - Graceful dependency handling
# - Complete GitHub API integration
```

## Comparison with Original

| Feature | Original pr-agent | Standalone Module |
|---------|------------------|-------------------|
| Dependencies | 50+ packages | 1 required (PyGithub) |
| Configuration | Complex TOML system | Simple dict-based |
| Size | Full framework | Single file |
| Setup | Multi-step installation | Drop-in ready |
| Logging | Loguru + complex setup | Standard logging |

## Limitations

- Simplified configuration (no TOML file support)
- Basic logging (no advanced loguru features)
- No AI/LLM integration (focused on GitHub API only)
- Some advanced pr-agent features not included

## Contributing

This module is generated from the pr-agent codebase. To contribute:

1. Make changes to the original pr-agent repository
2. Regenerate this module using the tree-sitter codemod
3. Test the standalone functionality

## License

This code is derived from [pr-agent](https://github.com/qodo-ai/pr-agent) and maintains the same license terms.

## Examples

### Analyze a Pull Request
```python
import os
from github_provider_final import GitHubProvider

os.environ['GITHUB_TOKEN'] = 'your_token'

provider = GitHubProvider("https://github.com/microsoft/vscode/pull/12345")

print(f"PR: {provider.get_pr_url()}")
print(f"Branch: {provider.get_pr_branch()}")
print(f"Description: {provider.get_pr_description_full()[:100]}...")

files = provider.get_diff_files()
print(f"\nChanged files ({len(files)}):")
for file in files[:5]:  # Show first 5 files
    print(f"  {file.filename} ({file.edit_type.name})")
    print(f"    +{file.num_plus_lines} -{file.num_minus_lines} lines")
```

### Add Comments and Labels
```python
# Add a comment
provider.publish_comment("Great work on this PR! 🚀")

# Add labels
provider.publish_labels(["enhancement", "ready-for-review"])

# Get existing comments
comments = provider.get_issue_comments()
print(f"PR has {len(comments)} comments")
```

### Repository Analysis
```python
# Get repository languages
languages = provider.get_languages()
print("Repository languages:")
for lang, bytes_count in languages.items():
    print(f"  {lang}: {bytes_count:,} bytes")

# Get commit messages
commits = provider.get_commit_messages()
print(f"\nCommit messages ({len(commits)}):")
for msg in commits[:3]:
    print(f"  - {msg.split()[0] if msg else 'Empty commit'}")
```

This standalone module provides all the essential GitHub provider functionality from pr-agent in a single, easy-to-use file with minimal dependencies.

