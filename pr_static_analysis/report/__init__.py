"""
Report Module

This module provides tools for generating, formatting, and visualizing
static analysis reports.
"""

from .generator import ReportGenerator
from .formatter import (
    ReportFormatter,
    DefaultReportFormatter,
    MarkdownReportFormatter,
    HTMLReportFormatter,
    JSONReportFormatter
)
from .visualizer import (
    ReportVisualizer,
    ChartVisualizer,
    BarChartVisualizer,
    FileIssueDistributionVisualizer
)
from .integration import (
    AnalysisReportIntegration,
    create_markdown_report_integration,
    create_html_report_integration,
    create_json_report_integration
)

__all__ = [
    'ReportGenerator',
    'ReportFormatter',
    'DefaultReportFormatter',
    'MarkdownReportFormatter',
    'HTMLReportFormatter',
    'JSONReportFormatter',
    'ReportVisualizer',
    'ChartVisualizer',
    'BarChartVisualizer',
    'FileIssueDistributionVisualizer',
    'AnalysisReportIntegration',
    'create_markdown_report_integration',
    'create_html_report_integration',
    'create_json_report_integration'
]

