# PR Static Analysis Reporting System

A comprehensive reporting system for PR static analysis, including report generation, formatting, and visualization.

## Overview

The PR Static Analysis Reporting System provides tools for generating, formatting, and visualizing static analysis reports for pull requests. It includes the following components:

- **ReportGenerator**: Generates comprehensive analysis reports from static analysis results
- **ReportFormatter**: Formats reports in different formats (Markdown, HTML, JSON)
- **ReportVisualizer**: Provides visualization components for analysis results
- **Integration**: Integrates with the core analysis engine and GitHub

## Installation

```bash
pip install pr_static_analysis
```

## Usage

### Basic Usage

```python
from pr_static_analysis.report import (
    ReportGenerator,
    MarkdownReportFormatter
)

# Create a report generator with a Markdown formatter
generator = ReportGenerator(formatter=MarkdownReportFormatter())

# Generate a report from analysis results
results = [
    {
        "severity": "error",
        "message": "Missing return type annotation",
        "file": "example.py",
        "line": 10,
        "recommendation": "Add a return type annotation to the function"
    },
    {
        "severity": "warning",
        "message": "Unused variable",
        "file": "example.py",
        "line": 15,
        "recommendation": "Remove the unused variable or use it"
    }
]

report = generator.generate_report(results)
print(report)
```

### Using the Integration

```python
from pr_static_analysis.report import create_markdown_report_integration

# Create an integration with a Markdown formatter and chart visualizer
integration = create_markdown_report_integration()

# Generate a report from analysis results
results = [
    {
        "severity": "error",
        "message": "Missing return type annotation",
        "file": "example.py",
        "line": 10,
        "recommendation": "Add a return type annotation to the function"
    },
    {
        "severity": "warning",
        "message": "Unused variable",
        "file": "example.py",
        "line": 15,
        "recommendation": "Remove the unused variable or use it"
    }
]

report = integration.generate_report(results)

# Post the report to GitHub
def github_api_callback(url, data):
    # Make an API call to GitHub
    # ...
    return {"id": 12345}

integration.post_report_to_github(
    report=report,
    pr_number=123,
    repo_owner="owner",
    repo_name="repo",
    github_api_callback=github_api_callback
)
```

## Components

### ReportGenerator

The `ReportGenerator` class is responsible for generating analysis reports from static analysis results. It aggregates results from different analysis rules and provides summary and detailed information about the analysis.

### ReportFormatter

The `ReportFormatter` classes are responsible for formatting reports in different formats, such as Markdown, HTML, or JSON. The following formatters are available:

- `MarkdownReportFormatter`: Formats reports as Markdown
- `HTMLReportFormatter`: Formats reports as HTML
- `JSONReportFormatter`: Formats reports as JSON

### ReportVisualizer

The `ReportVisualizer` classes are responsible for generating visualizations of analysis reports, such as charts or graphs. The following visualizers are available:

- `ChartVisualizer`: Generates pie chart data for reports
- `BarChartVisualizer`: Generates bar chart data for reports
- `FileIssueDistributionVisualizer`: Generates a visualization of issue distribution across files

### Integration

The `AnalysisReportIntegration` class provides integration with the core analysis engine and GitHub. It includes methods for generating reports from analysis results and posting reports to GitHub as comments on pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

