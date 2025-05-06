"""
Integration Module

This module provides integration with the core analysis engine.
"""

from typing import Dict, Any, List, Optional, Callable
from .generator import ReportGenerator
from .formatter import ReportFormatter, MarkdownReportFormatter, HTMLReportFormatter, JSONReportFormatter
from .visualizer import ReportVisualizer, ChartVisualizer


class AnalysisReportIntegration:
    """
    Integration with the core analysis engine.
    
    This class provides methods for generating reports from analysis results
    and integrating with the core analysis engine.
    
    Attributes:
        generator (ReportGenerator): The report generator to use.
        visualizer (Optional[ReportVisualizer]): The report visualizer to use, if any.
    """
    
    def __init__(
        self,
        formatter: Optional[ReportFormatter] = None,
        visualizer: Optional[ReportVisualizer] = None
    ):
        """
        Initialize a new AnalysisReportIntegration.
        
        Args:
            formatter (Optional[ReportFormatter]): The report formatter to use.
                If not provided, a MarkdownReportFormatter will be used.
            visualizer (Optional[ReportVisualizer]): The report visualizer to use.
                If not provided, no visualization will be generated.
        """
        self.generator = ReportGenerator(formatter=formatter or MarkdownReportFormatter())
        self.visualizer = visualizer
    
    def generate_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a report from analysis results.
        
        Args:
            results (List[Dict[str, Any]]): The analysis results.
        
        Returns:
            Dict[str, Any]: A dictionary containing the report and visualization data.
        """
        report_content = self.generator.generate_report(results)
        
        response = {
            "report": report_content
        }
        
        # Add visualization if a visualizer is available
        if self.visualizer:
            # We need to get the raw report data before formatting
            raw_report = {
                "summary": self.generator._generate_summary(results),
                "details": self.generator._generate_details(results),
                "recommendations": self.generator._generate_recommendations(results),
            }
            visualization = self.visualizer.generate_visualization(raw_report)
            response["visualization"] = visualization
        
        return response
    
    def post_report_to_github(
        self,
        report: Dict[str, Any],
        pr_number: int,
        repo_owner: str,
        repo_name: str,
        github_api_callback: Callable[[str, Dict[str, Any]], Any]
    ) -> Any:
        """
        Post a report to GitHub as a comment on a pull request.
        
        Args:
            report (Dict[str, Any]): The report to post.
            pr_number (int): The number of the pull request.
            repo_owner (str): The owner of the repository.
            repo_name (str): The name of the repository.
            github_api_callback (Callable[[str, Dict[str, Any]], Any]): A callback function
                that makes API calls to GitHub. It should take a URL and a data dictionary.
        
        Returns:
            Any: The result of the GitHub API call.
        """
        # Construct the API URL for posting a comment
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{pr_number}/comments"
        
        # Prepare the comment data
        data = {
            "body": report["report"]
        }
        
        # Make the API call
        return github_api_callback(url, data)


def create_markdown_report_integration() -> AnalysisReportIntegration:
    """
    Create an AnalysisReportIntegration with a MarkdownReportFormatter.
    
    Returns:
        AnalysisReportIntegration: The created integration.
    """
    return AnalysisReportIntegration(
        formatter=MarkdownReportFormatter(),
        visualizer=ChartVisualizer()
    )


def create_html_report_integration() -> AnalysisReportIntegration:
    """
    Create an AnalysisReportIntegration with an HTMLReportFormatter.
    
    Returns:
        AnalysisReportIntegration: The created integration.
    """
    return AnalysisReportIntegration(
        formatter=HTMLReportFormatter(),
        visualizer=ChartVisualizer()
    )


def create_json_report_integration() -> AnalysisReportIntegration:
    """
    Create an AnalysisReportIntegration with a JSONReportFormatter.
    
    Returns:
        AnalysisReportIntegration: The created integration.
    """
    return AnalysisReportIntegration(
        formatter=JSONReportFormatter(),
        visualizer=ChartVisualizer()
    )

