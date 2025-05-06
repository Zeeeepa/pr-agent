"""
Report Formatter Module

This module contains the ReportFormatter classes for formatting analysis reports
in different formats.
"""

from typing import Dict, Any, List
import json


class ReportFormatter:
    """
    Base class for report formatters.
    
    Report formatters are responsible for formatting reports in different formats,
    such as Markdown, HTML, or JSON.
    """
    
    def format_report(self, report: Dict[str, Any]) -> str:
        """
        Format the report.
        
        Args:
            report (Dict[str, Any]): The report to format.
        
        Returns:
            str: The formatted report.
        
        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement format_report()")


class DefaultReportFormatter(ReportFormatter):
    """
    Default report formatter that formats reports as Markdown.
    
    This formatter is used when no specific formatter is provided.
    """
    
    def format_report(self, report: Dict[str, Any]) -> str:
        """
        Format the report as Markdown.
        
        Args:
            report (Dict[str, Any]): The report to format.
        
        Returns:
            str: The formatted report as Markdown.
        """
        return MarkdownReportFormatter().format_report(report)


class MarkdownReportFormatter(ReportFormatter):
    """
    Report formatter that formats reports as Markdown.
    """
    
    def format_report(self, report: Dict[str, Any]) -> str:
        """
        Format the report as Markdown.
        
        Args:
            report (Dict[str, Any]): The report to format.
        
        Returns:
            str: The formatted report as Markdown.
        """
        markdown = "# PR Static Analysis Report\n\n"
        
        # Add summary
        markdown += "## Summary\n"
        summary = report["summary"]
        markdown += f"- Total issues: {summary['total_issues']}\n"
        markdown += f"- Errors: {summary['error_count']}\n"
        markdown += f"- Warnings: {summary['warning_count']}\n"
        markdown += f"- Info: {summary['info_count']}\n"
        markdown += f"- Valid implementation: {'Yes' if summary['is_valid'] else 'No'}\n\n"
        
        # Add details
        markdown += "## Details\n"
        for issue in report["details"]["issues"]:
            markdown += f"- **{issue['severity'].upper()}**: {issue['message']}"
            if issue.get("file"):
                markdown += f" in `{issue['file']}`"
                if issue.get("line"):
                    markdown += f" at line {issue['line']}"
            markdown += "\n"
        
        # Add recommendations
        if report["recommendations"]:
            markdown += "\n## Recommendations\n"
            for rec in report["recommendations"]:
                markdown += f"- {rec}\n"
        
        return markdown


class HTMLReportFormatter(ReportFormatter):
    """
    Report formatter that formats reports as HTML.
    """
    
    def format_report(self, report: Dict[str, Any]) -> str:
        """
        Format the report as HTML.
        
        Args:
            report (Dict[str, Any]): The report to format.
        
        Returns:
            str: The formatted report as HTML.
        """
        html = "<!DOCTYPE html>\n<html>\n<head>\n"
        html += "<title>PR Static Analysis Report</title>\n"
        html += "<style>\n"
        html += "body { font-family: Arial, sans-serif; margin: 20px; }\n"
        html += "h1 { color: #333; }\n"
        html += "h2 { color: #666; margin-top: 20px; }\n"
        html += ".error { color: #d9534f; }\n"
        html += ".warning { color: #f0ad4e; }\n"
        html += ".info { color: #5bc0de; }\n"
        html += ".summary { background-color: #f8f9fa; padding: 15px; border-radius: 5px; }\n"
        html += ".details { margin-top: 20px; }\n"
        html += ".recommendations { margin-top: 20px; }\n"
        html += "</style>\n"
        html += "</head>\n<body>\n"
        
        # Add title
        html += "<h1>PR Static Analysis Report</h1>\n"
        
        # Add summary
        html += "<div class='summary'>\n"
        html += "<h2>Summary</h2>\n"
        html += "<ul>\n"
        summary = report["summary"]
        html += f"<li>Total issues: {summary['total_issues']}</li>\n"
        html += f"<li>Errors: {summary['error_count']}</li>\n"
        html += f"<li>Warnings: {summary['warning_count']}</li>\n"
        html += f"<li>Info: {summary['info_count']}</li>\n"
        html += f"<li>Valid implementation: {'Yes' if summary['is_valid'] else 'No'}</li>\n"
        html += "</ul>\n"
        html += "</div>\n"
        
        # Add details
        html += "<div class='details'>\n"
        html += "<h2>Details</h2>\n"
        html += "<ul>\n"
        for issue in report["details"]["issues"]:
            severity_class = issue['severity'].lower()
            html += f"<li><span class='{severity_class}'><strong>{issue['severity'].upper()}</strong></span>: {issue['message']}"
            if issue.get("file"):
                html += f" in <code>{issue['file']}</code>"
                if issue.get("line"):
                    html += f" at line {issue['line']}"
            html += "</li>\n"
        html += "</ul>\n"
        html += "</div>\n"
        
        # Add recommendations
        if report["recommendations"]:
            html += "<div class='recommendations'>\n"
            html += "<h2>Recommendations</h2>\n"
            html += "<ul>\n"
            for rec in report["recommendations"]:
                html += f"<li>{rec}</li>\n"
            html += "</ul>\n"
            html += "</div>\n"
        
        html += "</body>\n</html>"
        return html


class JSONReportFormatter(ReportFormatter):
    """
    Report formatter that formats reports as JSON.
    """
    
    def format_report(self, report: Dict[str, Any]) -> str:
        """
        Format the report as JSON.
        
        Args:
            report (Dict[str, Any]): The report to format.
        
        Returns:
            str: The formatted report as JSON.
        """
        return json.dumps(report, indent=2)

