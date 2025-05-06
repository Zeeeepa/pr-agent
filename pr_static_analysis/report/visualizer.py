"""
Report Visualizer Module

This module contains the ReportVisualizer classes for generating visualizations
of analysis reports.
"""

from typing import Dict, Any, List, Optional
import json


class ReportVisualizer:
    """
    Base class for report visualizers.
    
    Report visualizers are responsible for generating visualizations of analysis reports,
    such as charts or graphs.
    """
    
    def generate_visualization(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a visualization of the report.
        
        Args:
            report (Dict[str, Any]): The report to visualize.
        
        Returns:
            Dict[str, Any]: The visualization data.
        
        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement generate_visualization()")


class ChartVisualizer(ReportVisualizer):
    """
    Report visualizer that generates chart data for reports.
    """
    
    def generate_visualization(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate chart data for the report.
        
        Args:
            report (Dict[str, Any]): The report to visualize.
        
        Returns:
            Dict[str, Any]: The chart data.
        """
        # Generate chart data for the report
        chart_data = {
            "type": "pie",
            "data": {
                "labels": ["Errors", "Warnings", "Info"],
                "datasets": [{
                    "data": [
                        report["summary"]["error_count"],
                        report["summary"]["warning_count"],
                        report["summary"]["info_count"],
                    ],
                    "backgroundColor": ["#ff6384", "#ffcd56", "#36a2eb"],
                }]
            }
        }
        
        return chart_data


class BarChartVisualizer(ReportVisualizer):
    """
    Report visualizer that generates bar chart data for reports.
    """
    
    def generate_visualization(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate bar chart data for the report.
        
        Args:
            report (Dict[str, Any]): The report to visualize.
        
        Returns:
            Dict[str, Any]: The bar chart data.
        """
        # Generate bar chart data for the report
        chart_data = {
            "type": "bar",
            "data": {
                "labels": ["Errors", "Warnings", "Info"],
                "datasets": [{
                    "label": "Issue Count",
                    "data": [
                        report["summary"]["error_count"],
                        report["summary"]["warning_count"],
                        report["summary"]["info_count"],
                    ],
                    "backgroundColor": ["#ff6384", "#ffcd56", "#36a2eb"],
                }]
            },
            "options": {
                "scales": {
                    "y": {
                        "beginAtZero": True
                    }
                }
            }
        }
        
        return chart_data


class FileIssueDistributionVisualizer(ReportVisualizer):
    """
    Report visualizer that generates a visualization of issue distribution across files.
    """
    
    def generate_visualization(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a visualization of issue distribution across files.
        
        Args:
            report (Dict[str, Any]): The report to visualize.
        
        Returns:
            Dict[str, Any]: The visualization data.
        """
        # Count issues per file
        file_counts = {}
        for issue in report["details"]["issues"]:
            file = issue.get("file", "Unknown")
            if file not in file_counts:
                file_counts[file] = {"error": 0, "warning": 0, "info": 0}
            
            severity = issue.get("severity", "info")
            file_counts[file][severity] += 1
        
        # Convert to chart data
        files = list(file_counts.keys())
        error_counts = [file_counts[file]["error"] for file in files]
        warning_counts = [file_counts[file]["warning"] for file in files]
        info_counts = [file_counts[file]["info"] for file in files]
        
        chart_data = {
            "type": "bar",
            "data": {
                "labels": files,
                "datasets": [
                    {
                        "label": "Errors",
                        "data": error_counts,
                        "backgroundColor": "#ff6384",
                    },
                    {
                        "label": "Warnings",
                        "data": warning_counts,
                        "backgroundColor": "#ffcd56",
                    },
                    {
                        "label": "Info",
                        "data": info_counts,
                        "backgroundColor": "#36a2eb",
                    }
                ]
            },
            "options": {
                "scales": {
                    "x": {
                        "stacked": True
                    },
                    "y": {
                        "stacked": True,
                        "beginAtZero": True
                    }
                }
            }
        }
        
        return chart_data

