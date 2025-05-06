# PR Static Analysis System - Architecture Overview

This document provides an overview of the PR Static Analysis System architecture, including its components, interactions, and data flow.

## System Architecture

The PR Static Analysis System is designed as a modular, extensible system for analyzing pull requests. It consists of the following main components:

![Architecture Diagram](images/architecture_diagram.png)

### Core Components

1. **PR Analyzer**: The main orchestrator that coordinates the analysis process.
2. **Rule Engine**: Applies analysis rules to the PR and collects results.
3. **Analysis Context**: Provides data and utilities for rules to use during analysis.
4. **GitHub Integration**: Interfaces with GitHub to fetch PR data and post results.
5. **Reporting System**: Generates and formats analysis reports.

## Component Interactions

The following diagram shows how the components interact during the analysis process:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  GitHub API │     │ PR Analyzer │     │ Rule Engine │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       │  1. Fetch PR Data │                   │
       │◄──────────────────┤                   │
       │                   │                   │
       │  2. Return PR Data│                   │
       │───────────────────►                   │
       │                   │                   │
       │                   │ 3. Create Contexts│
       │                   │───────────────────┤
       │                   │                   │
       │                   │ 4. Apply Rules    │
       │                   │───────────────────►
       │                   │                   │
       │                   │ 5. Return Results │
       │                   │◄───────────────────
       │                   │                   │
┌──────┴──────┐     ┌──────┴──────┐     ┌──────┴──────┐
│  GitHub API │     │ PR Analyzer │     │ Rule Engine │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │                   
                           │ 6. Generate Report
                           ▼                   
                    ┌─────────────┐           
                    │  Reporting  │           
                    │   System    │           
                    └──────┬──────┘           
                           │                   
                           │ 7. Post Results  
                           ▼                   
                    ┌─────────────┐           
                    │  GitHub API │           
                    └─────────────┘           
```

## Data Flow

The data flows through the system as follows:

1. **Input**: The system receives a PR number and repository name.
2. **PR Data Retrieval**: The PR Analyzer uses the GitHub client to fetch PR data.
3. **Context Creation**: The PR Analyzer creates analysis contexts for the base and head branches.
4. **Rule Application**: The Rule Engine applies analysis rules to the contexts.
5. **Result Collection**: The Rule Engine collects results from all rules.
6. **Report Generation**: The Reporting System generates a report from the results.
7. **Output**: The report is returned to the caller and optionally posted to GitHub.

## Component Details

### PR Analyzer

The PR Analyzer is the main entry point for the analysis process. It:

- Retrieves PR data from GitHub
- Creates analysis contexts for the base and head branches
- Creates a diff context for comparing the branches
- Invokes the Rule Engine to apply rules
- Collects and aggregates results
- Generates a final analysis report

```python
class PRAnalyzer:
    def __init__(self, github_client, rule_engine):
        self.github_client = github_client
        self.rule_engine = rule_engine
        
    def analyze_pr(self, pr_number, repository):
        # Get PR data
        pr_data = self.github_client.get_pr(pr_number, repository)
        
        # Create analysis contexts
        base_context = self._create_analysis_context(pr_data.base)
        head_context = self._create_analysis_context(pr_data.head)
        
        # Create diff context
        diff_context = self._create_diff_context(base_context, head_context)
        
        # Apply rules
        results = self.rule_engine.apply_rules(diff_context)
        
        # Generate report
        return self._generate_report(results, pr_data)
```

### Rule Engine

The Rule Engine is responsible for applying analysis rules to the PR. It:

- Maintains a collection of rules
- Applies each rule to the analysis context
- Collects and aggregates results from all rules

```python
class RuleEngine:
    def __init__(self, rules):
        self.rules = rules
        
    def apply_rules(self, context):
        results = []
        for rule in self.rules:
            try:
                rule_results = rule.apply(context)
                results.extend(rule_results)
            except Exception as e:
                # Log the error and continue with other rules
                pass
        return results
```

### Analysis Context

The Analysis Context provides data and utilities for rules to use during analysis. It:

- Represents a snapshot of the codebase at a specific commit
- Provides methods for accessing file content, symbols, and references
- Caches data to improve performance

```python
class AnalysisContext:
    def __init__(self, repo_name, ref, sha):
        self.repo_name = repo_name
        self.ref = ref
        self.sha = sha
        self.codebase = self._load_codebase(repo_name, ref, sha)
        
    def get_file_content(self, file_path):
        return self.codebase.get_file_content(file_path)
        
    def get_files(self):
        return self.codebase.get_files()
        
    def get_symbols(self):
        return self.codebase.get_symbols()
```

### GitHub Integration

The GitHub Integration interfaces with GitHub to fetch PR data and post results. It includes:

- **GitHub Client**: Interacts with the GitHub API
- **Webhook Handler**: Receives GitHub webhook events
- **PR Data Model**: Represents GitHub pull requests
- **Comment Formatter**: Formats analysis results as GitHub comments

```python
class GitHubClient:
    def __init__(self, token):
        self.client = Github(token)
        
    def get_pr(self, pr_number, repository):
        repo = self.client.get_repo(repository)
        return repo.get_pull(pr_number)
        
    def post_comment(self, pr, comment):
        pr.create_issue_comment(comment)
```

### Reporting System

The Reporting System generates and formats analysis reports. It includes:

- **Report Generator**: Creates analysis reports from rule results
- **Report Formatters**: Format reports for different output formats (Markdown, HTML, JSON)
- **Visualization Components**: Visualize analysis results

```python
class ReportGenerator:
    def generate_report(self, results, pr_context):
        report = {
            "pr": {
                "number": pr_context.number,
                "title": pr_context.title,
                "url": pr_context.html_url,
                "base": pr_context.base.ref,
                "head": pr_context.head.ref,
            },
            "summary": self._generate_summary(results),
            "results": [result.to_dict() for result in results],
            "timestamp": self._get_timestamp(),
        }
        return report
```

## Folder Structure

The system is organized into the following folder structure:

```
pr_analysis/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── pr_analyzer.py         # Main PR analysis orchestrator
│   ├── rule_engine.py         # Engine for applying analysis rules
│   └── analysis_context.py    # Context for PR analysis
├── rules/
│   ├── __init__.py
│   ├── base_rule.py           # Base class for analysis rules
│   ├── code_integrity_rules.py # Rules for code integrity
│   ├── parameter_rules.py     # Rules for parameter validation
│   └── implementation_rules.py # Rules for implementation validation
├── github/
│   ├── __init__.py
│   ├── webhook_handler.py     # Handler for GitHub webhooks
│   ├── pr_client.py           # Client for interacting with GitHub PRs
│   └── comment_formatter.py   # Formatter for GitHub comments
├── reporting/
│   ├── __init__.py
│   ├── report_generator.py    # Generator for analysis reports
│   ├── report_formatter.py    # Formatter for analysis reports
│   └── visualization.py       # Visualization components
└── utils/
    ├── __init__.py
    ├── diff_utils.py          # Utilities for diff analysis
    └── config_utils.py        # Utilities for configuration
```

## Dependencies

The system depends on the following external libraries:

- **PyGithub**: For interacting with the GitHub API
- **Flask**: For the webhook server
- **Jinja2**: For HTML report templates
- **Markdown**: For Markdown report formatting
- **Pygments**: For syntax highlighting in reports
- **PyYAML**: For configuration file parsing

## Extension Points

The system is designed to be extensible at the following points:

- **Rules**: New rules can be added by subclassing `BaseRule`
- **Report Formatters**: New formatters can be added by implementing the formatter interface
- **Visualization Components**: New visualizations can be added to the reporting system
- **GitHub Integration**: The GitHub integration can be extended to support additional features

See the [Extension Guide](extension_guide.md) for more information on extending the system.

