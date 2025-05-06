# PR Static Analysis System - Extension Guide

This guide explains how to extend the PR Static Analysis System with custom rules, report formatters, and visualization components.

## Adding New Analysis Rules

The PR Static Analysis System is designed to be easily extended with new analysis rules. This section explains how to create and add custom rules.

### Rule Structure

All rules must inherit from the `BaseRule` class and implement the `apply` method:

```python
from pr_analysis.rules.base_rule import BaseRule, AnalysisResult

class MyCustomRule(BaseRule):
    def __init__(self):
        super().__init__(
            rule_id="CUSTOM001",
            name="My Custom Rule",
            description="This rule checks for a custom condition"
        )
    
    def apply(self, context):
        results = []
        
        # Implement your rule logic here
        # ...
        
        # Add results for any issues found
        results.append(
            AnalysisResult(
                rule_id=self.rule_id,
                severity="warning",
                message="Custom issue found",
                file="path/to/file.py",
                line=10,
                column=5
            )
        )
        
        return results
```

### Rule Categories

Rules are typically organized into the following categories:

1. **Code Integrity Rules**: Check for syntax errors, undefined references, etc.
2. **Parameter Validation Rules**: Check for parameter type mismatches, missing parameters, etc.
3. **Implementation Validation Rules**: Check for feature completeness, test coverage, etc.

You can create a new rule in any of these categories or define your own category.

### Using the Analysis Context

The `context` parameter passed to the `apply` method provides access to the PR data and codebase. You can use it to:

- Get file content: `context.get_file_content(file_path)`
- Get all files: `context.get_files()`
- Get files by extension: `context.get_files_by_extension(".py")`
- Get symbols: `context.get_symbols()`
- Get symbol references: `context.get_symbol_references(symbol)`

For diff analysis, you can access the base and head contexts:

- Base context: `context.base_context`
- Head context: `context.head_context`
- Get file changes: `context.get_file_changes()`

### Example: Creating a Custom Rule

Here's an example of a custom rule that checks for TODO comments in the code:

```python
from pr_analysis.rules.base_rule import BaseRule, AnalysisResult
import re

class TodoCommentRule(BaseRule):
    def __init__(self):
        super().__init__(
            rule_id="CUSTOM001",
            name="TODO Comment Check",
            description="Checks for TODO comments in the code"
        )
        self.todo_pattern = re.compile(r'#\s*TODO', re.IGNORECASE)
    
    def apply(self, context):
        results = []
        
        # Get all files that were added or modified
        file_changes = context.get_file_changes()
        for file_path, change_type in file_changes.items():
            if change_type in ["added", "modified"] and file_path.endswith(".py"):
                # Get the file content
                try:
                    content = context.head_context.get_file_content(file_path)
                    
                    # Check for TODO comments
                    for i, line in enumerate(content.splitlines(), 1):
                        match = self.todo_pattern.search(line)
                        if match:
                            results.append(
                                AnalysisResult(
                                    rule_id=self.rule_id,
                                    severity="info",
                                    message=f"TODO comment found: {line.strip()}",
                                    file=file_path,
                                    line=i,
                                    column=match.start() + 1
                                )
                            )
                except Exception as e:
                    # Log the error and continue with other files
                    pass
        
        return results
```

### Registering a Custom Rule

To use your custom rule, you need to register it with the rule engine:

```python
from pr_analysis.core.rule_engine import RuleEngine
from pr_analysis.rules.code_integrity_rules import SyntaxErrorRule, UndefinedReferenceRule
from my_custom_rules import TodoCommentRule

# Create the rule engine with built-in and custom rules
rule_engine = RuleEngine([
    SyntaxErrorRule(),
    UndefinedReferenceRule(),
    TodoCommentRule()
])
```

## Adding New Report Formatters

You can extend the reporting system with custom formatters for different output formats.

### Formatter Structure

A report formatter is a class with a `format_report` method that takes a report dictionary and returns a formatted string:

```python
class MyCustomFormatter:
    def format_report(self, report):
        # Implement your formatting logic here
        # ...
        return formatted_report
```

### Example: Creating a Custom Formatter

Here's an example of a custom formatter that generates a CSV report:

```python
import csv
import io

class CSVReportFormatter:
    def format_report(self, report):
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(["Rule ID", "Severity", "Message", "File", "Line", "Column"])
        
        # Write results
        for result in report["results"]:
            writer.writerow([
                result["rule_id"],
                result["severity"],
                result["message"],
                result["file"],
                result["line"],
                result["column"]
            ])
        
        return output.getvalue()
```

### Registering a Custom Formatter

To use your custom formatter, you need to register it with the reporting system:

```python
from pr_analysis.reporting.report_generator import ReportGenerator
from my_custom_formatters import CSVReportFormatter

# Create the report generator
report_generator = ReportGenerator()

# Format a report using the custom formatter
report = report_generator.generate_report(results, pr_context)
csv_report = CSVReportFormatter().format_report(report)
```

## Adding New Visualization Components

You can extend the reporting system with custom visualization components for different types of data.

### Visualization Component Structure

A visualization component is a class with methods that generate visualizations for different aspects of the report:

```python
class MyCustomVisualizer:
    def generate_visualization(self, report):
        # Implement your visualization logic here
        # ...
        return visualization_html
```

### Example: Creating a Custom Visualizer

Here's an example of a custom visualizer that generates a heatmap of issues by file:

```python
import plotly.graph_objects as go
import plotly.io as pio
from collections import defaultdict

class IssueHeatmapVisualizer:
    def generate_heatmap(self, report):
        # Count issues by file and severity
        file_severity_counts = defaultdict(lambda: defaultdict(int))
        for result in report["results"]:
            file_path = result["file"]
            severity = result["severity"]
            file_severity_counts[file_path][severity] += 1
        
        # Prepare data for heatmap
        files = list(file_severity_counts.keys())
        severities = ["error", "warning", "info"]
        z_values = []
        
        for file_path in files:
            row = []
            for severity in severities:
                row.append(file_severity_counts[file_path][severity])
            z_values.append(row)
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=z_values,
            x=severities,
            y=files,
            colorscale="Reds",
            hoverongaps=False
        ))
        
        fig.update_layout(
            title="Issues by File and Severity",
            xaxis_title="Severity",
            yaxis_title="File"
        )
        
        # Convert to HTML
        return pio.to_html(fig, full_html=False)
```

### Registering a Custom Visualizer

To use your custom visualizer, you need to integrate it with your reporting system:

```python
from pr_analysis.reporting.report_generator import ReportGenerator
from my_custom_visualizers import IssueHeatmapVisualizer

# Create the report generator
report_generator = ReportGenerator()

# Generate a report
report = report_generator.generate_report(results, pr_context)

# Generate a visualization
visualizer = IssueHeatmapVisualizer()
heatmap_html = visualizer.generate_heatmap(report)

# Include the visualization in your HTML report
html_report = f"""
<html>
<head>
    <title>PR Analysis Report</title>
</head>
<body>
    <h1>PR Analysis Report for #{report["pr"]["number"]}</h1>
    
    <h2>Summary</h2>
    <p>Errors: {report["summary"]["error_count"]}</p>
    <p>Warnings: {report["summary"]["warning_count"]}</p>
    <p>Info: {report["summary"]["info_count"]}</p>
    
    <h2>Issue Heatmap</h2>
    {heatmap_html}
    
    <h2>Issues</h2>
    <!-- Issue details here -->
</body>
</html>
"""
```

## Creating a Plugin System

For more advanced extensions, you can create a plugin system that allows users to add custom rules, formatters, and visualizers without modifying the core code.

### Plugin Structure

A plugin is a Python package that defines custom rules, formatters, or visualizers and registers them with the system.

Here's an example plugin structure:

```
my_plugin/
├── __init__.py
├── rules/
│   ├── __init__.py
│   └── custom_rules.py
├── formatters/
│   ├── __init__.py
│   └── custom_formatters.py
└── visualizers/
    ├── __init__.py
    └── custom_visualizers.py
```

### Plugin Registration

In the plugin's `__init__.py`, you can define a function to register the plugin with the system:

```python
def register_plugin(system):
    # Register custom rules
    from .rules.custom_rules import TodoCommentRule
    system.rule_engine.add_rule(TodoCommentRule())
    
    # Register custom formatters
    from .formatters.custom_formatters import CSVReportFormatter
    system.register_formatter("csv", CSVReportFormatter())
    
    # Register custom visualizers
    from .visualizers.custom_visualizers import IssueHeatmapVisualizer
    system.register_visualizer("heatmap", IssueHeatmapVisualizer())
```

### Plugin Discovery

The system can discover and load plugins using entry points:

```python
# In setup.py
setup(
    name="my_plugin",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "pr_analysis.plugins": [
            "my_plugin = my_plugin:register_plugin",
        ],
    },
)
```

The system can then load all registered plugins:

```python
import pkg_resources

def load_plugins(system):
    for entry_point in pkg_resources.iter_entry_points("pr_analysis.plugins"):
        try:
            register_func = entry_point.load()
            register_func(system)
        except Exception as e:
            # Log the error and continue with other plugins
            pass
```

## Best Practices

When extending the PR Static Analysis System, follow these best practices:

1. **Keep rules focused**: Each rule should check for a specific issue.
2. **Use appropriate severity levels**: Use "error" for critical issues, "warning" for potential issues, and "info" for informational messages.
3. **Provide clear messages**: Rule messages should clearly explain the issue and how to fix it.
4. **Handle exceptions gracefully**: Rules should catch and handle exceptions to avoid crashing the entire analysis.
5. **Write tests**: Write unit tests for your custom rules, formatters, and visualizers.
6. **Document your extensions**: Provide clear documentation for your extensions, including examples and usage instructions.
7. **Follow the existing patterns**: Follow the patterns and conventions used in the core system.
8. **Consider performance**: Be mindful of performance, especially for rules that analyze large files or complex code structures.

## Next Steps

Now that you know how to extend the PR Static Analysis System, you can:

- [Explore the API Reference](../api_docs/index.md) for detailed information about the system's classes and methods
- [Contribute to the project](contributing.md) by submitting your extensions as pull requests
- [Join the community](community.md) to discuss ideas and get help with your extensions

