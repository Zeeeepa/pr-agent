# PR Static Analysis System - API Reference

This document provides a reference for the PR Static Analysis System API.

## Core Module

### PRAnalyzer

```python
class PRAnalyzer:
    """Main orchestrator for PR analysis."""
    
    def __init__(self, github_client, rule_engine):
        """
        Initialize the PR analyzer.
        
        Args:
            github_client: The GitHub client to use for fetching PR data.
            rule_engine: The rule engine to use for applying rules.
        """
        pass
        
    def analyze_pr(self, pr_number, repository):
        """
        Analyze a PR and return results.
        
        Args:
            pr_number: The PR number to analyze.
            repository: The repository name in the format "owner/repo".
            
        Returns:
            A dictionary containing the analysis results.
        """
        pass
        
    def _create_analysis_context(self, pr_part):
        """
        Create an analysis context for a PR part.
        
        Args:
            pr_part: The PR part (base or head) to create a context for.
            
        Returns:
            An AnalysisContext object.
        """
        pass
        
    def _create_diff_context(self, base_context, head_context):
        """
        Create a diff context for comparing base and head contexts.
        
        Args:
            base_context: The base context.
            head_context: The head context.
            
        Returns:
            A DiffContext object.
        """
        pass
        
    def _generate_report(self, results, pr_data):
        """
        Generate a report from analysis results.
        
        Args:
            results: The analysis results.
            pr_data: The PR data.
            
        Returns:
            A dictionary containing the report.
        """
        pass
```

### RuleEngine

```python
class RuleEngine:
    """Engine for applying analysis rules."""
    
    def __init__(self, rules):
        """
        Initialize the rule engine.
        
        Args:
            rules: A list of rules to apply.
        """
        pass
        
    def apply_rules(self, context):
        """
        Apply all rules to the context and return results.
        
        Args:
            context: The context to apply rules to.
            
        Returns:
            A list of AnalysisResult objects.
        """
        pass
        
    def get_rules(self):
        """
        Get all rules.
        
        Returns:
            A list of rules.
        """
        pass
        
    def add_rule(self, rule):
        """
        Add a rule to the engine.
        
        Args:
            rule: The rule to add.
        """
        pass
        
    def remove_rule(self, rule_id):
        """
        Remove a rule from the engine.
        
        Args:
            rule_id: The ID of the rule to remove.
        """
        pass
```

### AnalysisContext

```python
class AnalysisContext:
    """Context for PR analysis."""
    
    def __init__(self, repo_name, ref, sha):
        """
        Initialize the analysis context.
        
        Args:
            repo_name: The repository name in the format "owner/repo".
            ref: The Git reference (branch or tag).
            sha: The commit SHA.
        """
        pass
        
    def get_file_content(self, file_path):
        """
        Get the content of a file.
        
        Args:
            file_path: The path to the file.
            
        Returns:
            The content of the file as a string.
        """
        pass
        
    def get_files(self):
        """
        Get all files in the repository.
        
        Returns:
            A list of file paths.
        """
        pass
        
    def get_files_by_extension(self, extension):
        """
        Get all files with a specific extension.
        
        Args:
            extension: The file extension to filter by.
            
        Returns:
            A list of file paths.
        """
        pass
        
    def get_symbols(self):
        """
        Get all symbols in the repository.
        
        Returns:
            A list of symbols.
        """
        pass
        
    def get_symbol_references(self, symbol):
        """
        Get all references to a symbol.
        
        Args:
            symbol: The symbol to get references for.
            
        Returns:
            A list of references.
        """
        pass
```

### DiffContext

```python
class DiffContext:
    """Context for diff analysis."""
    
    def __init__(self, base_context, head_context):
        """
        Initialize the diff context.
        
        Args:
            base_context: The base context.
            head_context: The head context.
        """
        pass
        
    def get_file_changes(self):
        """
        Get all file changes between base and head.
        
        Returns:
            A dictionary mapping file paths to change types ("added", "modified", "deleted").
        """
        pass
        
    def get_symbol_changes(self):
        """
        Get all symbol changes between base and head.
        
        Returns:
            A dictionary mapping symbols to change types ("added", "modified", "deleted").
        """
        pass
```

## Rules Module

### BaseRule

```python
class BaseRule:
    """Base class for all analysis rules."""
    
    def __init__(self, rule_id, name, description):
        """
        Initialize the rule.
        
        Args:
            rule_id: The ID of the rule.
            name: The name of the rule.
            description: The description of the rule.
        """
        pass
        
    def apply(self, context):
        """
        Apply the rule to the context and return results.
        
        Args:
            context: The context to apply the rule to.
            
        Returns:
            A list of AnalysisResult objects.
        """
        pass
```

### AnalysisResult

```python
class AnalysisResult:
    """Represents a result from an analysis rule."""
    
    def __init__(self, rule_id, severity, message, file=None, line=None, column=None):
        """
        Initialize the result.
        
        Args:
            rule_id: The ID of the rule that generated the result.
            severity: The severity of the result ("error", "warning", "info").
            message: The message describing the result.
            file: The file path where the issue was found.
            line: The line number where the issue was found.
            column: The column number where the issue was found.
        """
        pass
        
    def to_dict(self):
        """
        Convert the result to a dictionary.
        
        Returns:
            A dictionary representation of the result.
        """
        pass
```

## GitHub Module

### GitHubClient

```python
class GitHubClient:
    """Client for interacting with the GitHub API."""
    
    def __init__(self, token):
        """
        Initialize the client.
        
        Args:
            token: The GitHub API token.
        """
        pass
        
    def get_pr(self, pr_number, repository):
        """
        Get a PR by number and repository.
        
        Args:
            pr_number: The PR number.
            repository: The repository name in the format "owner/repo".
            
        Returns:
            A GitHub PR object.
        """
        pass
        
    def get_pr_files(self, pr):
        """
        Get files changed in a PR.
        
        Args:
            pr: The PR object.
            
        Returns:
            A list of file objects.
        """
        pass
        
    def get_pr_commits(self, pr):
        """
        Get commits in a PR.
        
        Args:
            pr: The PR object.
            
        Returns:
            A list of commit objects.
        """
        pass
        
    def post_comment(self, pr, comment):
        """
        Post a comment on a PR.
        
        Args:
            pr: The PR object.
            comment: The comment text.
        """
        pass
        
    def post_review_comment(self, pr, comment, commit, path, position):
        """
        Post a review comment on a specific line in a PR.
        
        Args:
            pr: The PR object.
            comment: The comment text.
            commit: The commit SHA.
            path: The file path.
            position: The position in the diff.
        """
        pass
```

### GitHubWebhookHandler

```python
class GitHubWebhookHandler:
    """Handler for GitHub webhooks."""
    
    def __init__(self, pr_analyzer):
        """
        Initialize the handler.
        
        Args:
            pr_analyzer: The PR analyzer to use for analyzing PRs.
        """
        pass
        
    def setup_routes(self):
        """Set up the webhook routes."""
        pass
        
    def handle_webhook(self):
        """
        Handle a GitHub webhook event.
        
        Returns:
            A Flask response.
        """
        pass
        
    def handle_pull_request(self, payload):
        """
        Handle a pull request event.
        
        Args:
            payload: The webhook payload.
            
        Returns:
            A Flask response.
        """
        pass
        
    def post_results(self, results, pr_number, repository):
        """
        Post analysis results to GitHub.
        
        Args:
            results: The analysis results.
            pr_number: The PR number.
            repository: The repository name.
        """
        pass
```

## Reporting Module

### ReportGenerator

```python
class ReportGenerator:
    """Generator for analysis reports."""
    
    def generate_report(self, results, pr_context):
        """
        Generate a report from analysis results.
        
        Args:
            results: The analysis results.
            pr_context: The PR context.
            
        Returns:
            A dictionary containing the report.
        """
        pass
        
    def _generate_summary(self, results):
        """
        Generate a summary of the analysis results.
        
        Args:
            results: The analysis results.
            
        Returns:
            A dictionary containing the summary.
        """
        pass
        
    def _get_timestamp(self):
        """
        Get the current timestamp.
        
        Returns:
            The current timestamp as an ISO 8601 string.
        """
        pass
```

### MarkdownReportFormatter

```python
class MarkdownReportFormatter:
    """Formatter for Markdown reports."""
    
    def format_report(self, report):
        """
        Format a report as Markdown.
        
        Args:
            report: The report to format.
            
        Returns:
            A Markdown string.
        """
        pass
        
    def _get_severity_icon(self, severity):
        """
        Get an icon for a severity level.
        
        Args:
            severity: The severity level.
            
        Returns:
            An emoji icon.
        """
        pass
```

### HTMLReportFormatter

```python
class HTMLReportFormatter:
    """Formatter for HTML reports."""
    
    def format_report(self, report):
        """
        Format a report as HTML.
        
        Args:
            report: The report to format.
            
        Returns:
            An HTML string.
        """
        pass
```

### JSONReportFormatter

```python
class JSONReportFormatter:
    """Formatter for JSON reports."""
    
    def format_report(self, report):
        """
        Format a report as JSON.
        
        Args:
            report: The report to format.
            
        Returns:
            A JSON string.
        """
        pass
```

### ReportVisualizer

```python
class ReportVisualizer:
    """Visualizer for analysis reports."""
    
    def generate_summary_chart(self, report):
        """
        Generate a summary chart for a report.
        
        Args:
            report: The report to visualize.
            
        Returns:
            An HTML string containing the chart.
        """
        pass
        
    def generate_severity_distribution(self, report):
        """
        Generate a severity distribution chart for a report.
        
        Args:
            report: The report to visualize.
            
        Returns:
            An HTML string containing the chart.
        """
        pass
        
    def generate_file_heatmap(self, report):
        """
        Generate a file heatmap for a report.
        
        Args:
            report: The report to visualize.
            
        Returns:
            An HTML string containing the heatmap.
        """
        pass
```

## Utils Module

### DiffUtils

```python
class DiffUtils:
    """Utilities for diff analysis."""
    
    @staticmethod
    def get_file_diff(base_content, head_content):
        """
        Get the diff between two file contents.
        
        Args:
            base_content: The base file content.
            head_content: The head file content.
            
        Returns:
            A diff object.
        """
        pass
        
    @staticmethod
    def get_line_changes(diff):
        """
        Get line changes from a diff.
        
        Args:
            diff: The diff object.
            
        Returns:
            A dictionary mapping line numbers to change types.
        """
        pass
```

### ConfigUtils

```python
class ConfigUtils:
    """Utilities for configuration."""
    
    @staticmethod
    def load_config(config_path):
        """
        Load configuration from a file.
        
        Args:
            config_path: The path to the configuration file.
            
        Returns:
            A dictionary containing the configuration.
        """
        pass
        
    @staticmethod
    def get_config_value(config, key, default=None):
        """
        Get a value from the configuration.
        
        Args:
            config: The configuration dictionary.
            key: The key to get.
            default: The default value to return if the key is not found.
            
        Returns:
            The value for the key, or the default value if the key is not found.
        """
        pass
```

## Command Line Interface

```
Usage: pr-analysis [OPTIONS] COMMAND [ARGS]...

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  analyze  Analyze a pull request.
  server   Start the webhook server.
```

### Analyze Command

```
Usage: pr-analysis analyze [OPTIONS]

  Analyze a pull request.

Options:
  -r, --repo TEXT     The repository in the format "owner/repo".  [required]
  -p, --pr INTEGER    The pull request number.  [required]
  -o, --output TEXT   The output file to write the results to.
  -f, --format TEXT   The output format (markdown, html, json).  [default: markdown]
  -c, --comment       Whether to post the results as a comment on the PR.
  -k, --check         Whether to create a GitHub check run.
  -g, --config TEXT   Path to the configuration file.  [default: pr_analysis_config.yaml]
  -v, --verbose       Enable verbose output.
  -h, --help          Show this message and exit.
```

### Server Command

```
Usage: pr-analysis server [OPTIONS]

  Start the webhook server.

Options:
  -h, --host TEXT     The host to bind to.  [default: 127.0.0.1]
  -p, --port INTEGER  The port to listen on.  [default: 8000]
  -g, --config TEXT   Path to the configuration file.  [default: pr_analysis_config.yaml]
  -v, --verbose       Enable verbose output.
  --help              Show this message and exit.
```

