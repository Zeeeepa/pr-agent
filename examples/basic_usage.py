"""
Basic usage example for the PR Static Analysis Reporting System.
"""

from pr_static_analysis.report import (
    ReportGenerator,
    MarkdownReportFormatter,
    HTMLReportFormatter,
    JSONReportFormatter,
    ChartVisualizer,
    BarChartVisualizer,
    FileIssueDistributionVisualizer,
    create_markdown_report_integration,
    create_html_report_integration,
    create_json_report_integration
)

# Sample analysis results
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
    },
    {
        "severity": "info",
        "message": "Consider using a more descriptive variable name",
        "file": "utils.py",
        "line": 20
    }
]

# Example 1: Using ReportGenerator with different formatters
print("Example 1: Using ReportGenerator with different formatters")
print("-" * 80)

# Markdown formatter
markdown_generator = ReportGenerator(formatter=MarkdownReportFormatter())
markdown_report = markdown_generator.generate_report(results)
print("Markdown Report:")
print(markdown_report)
print()

# HTML formatter
html_generator = ReportGenerator(formatter=HTMLReportFormatter())
html_report = html_generator.generate_report(results)
print("HTML Report (first 200 characters):")
print(html_report[:200] + "...")
print()

# JSON formatter
json_generator = ReportGenerator(formatter=JSONReportFormatter())
json_report = json_generator.generate_report(results)
print("JSON Report (first 200 characters):")
print(json_report[:200] + "...")
print()

# Example 2: Using the integration
print("Example 2: Using the integration")
print("-" * 80)

# Create an integration with a Markdown formatter and chart visualizer
integration = create_markdown_report_integration()

# Generate a report from analysis results
report = integration.generate_report(results)

print("Report:")
print(report["report"])
print()

print("Visualization:")
print(report["visualization"])
print()

# Example 3: Posting a report to GitHub
print("Example 3: Posting a report to GitHub")
print("-" * 80)

# Define a mock GitHub API callback
def mock_github_api_callback(url, data):
    print(f"Making API call to: {url}")
    print(f"With data: {data.keys()}")
    return {"id": 12345}

# Post the report to GitHub
result = integration.post_report_to_github(
    report=report,
    pr_number=123,
    repo_owner="owner",
    repo_name="repo",
    github_api_callback=mock_github_api_callback
)

print("Result:", result)

