"""
Report Generator Module

This module contains the ReportGenerator class for creating analysis reports
from static analysis results.
"""

from typing import Dict, List, Any, Optional
from .formatter import ReportFormatter, DefaultReportFormatter


class ReportGenerator:
    """
    Generates comprehensive analysis reports from static analysis results.
    
    The ReportGenerator aggregates results from different analysis rules and
    provides summary and detailed information about the analysis.
    
    Attributes:
        formatter (ReportFormatter): The formatter to use for formatting the report.
    """
    
    def __init__(self, formatter: Optional[ReportFormatter] = None):
        """
        Initialize a new ReportGenerator.
        
        Args:
            formatter (ReportFormatter, optional): The formatter to use for formatting the report.
                If not provided, a DefaultReportFormatter will be used.
        """
        self.formatter = formatter or DefaultReportFormatter()
    
    def generate_report(self, results: List[Dict[str, Any]]) -> Any:
        """
        Generate a report from the analysis results.
        
        Args:
            results (List[Dict[str, Any]]): The analysis results to include in the report.
                Each result should be a dictionary with at least a 'severity' key.
        
        Returns:
            Any: The formatted report, as returned by the formatter.
        """
        # Create report data structure
        report = {
            "summary": self._generate_summary(results),
            "details": self._generate_details(results),
            "recommendations": self._generate_recommendations(results),
        }
        
        # Format the report
        return self.formatter.format_report(report)
    
    def _generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary information from the analysis results.
        
        Args:
            results (List[Dict[str, Any]]): The analysis results.
        
        Returns:
            Dict[str, Any]: A dictionary containing summary information.
        """
        return {
            "total_issues": len(results),
            "error_count": len([r for r in results if r.get("severity") == "error"]),
            "warning_count": len([r for r in results if r.get("severity") == "warning"]),
            "info_count": len([r for r in results if r.get("severity") == "info"]),
            "is_valid": len([r for r in results if r.get("severity") == "error"]) == 0,
        }
    
    def _generate_details(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate detailed information from the analysis results.
        
        Args:
            results (List[Dict[str, Any]]): The analysis results.
        
        Returns:
            Dict[str, Any]: A dictionary containing detailed information.
        """
        return {
            "issues": results,
        }
    
    def _generate_recommendations(self, results: List[Dict[str, Any]]) -> List[str]:
        """
        Generate recommendations based on the analysis results.
        
        Args:
            results (List[Dict[str, Any]]): The analysis results.
        
        Returns:
            List[str]: A list of recommendations.
        """
        recommendations = []
        
        # Add recommendations based on issues
        for result in results:
            if result.get("recommendation"):
                recommendations.append(result["recommendation"])
        
        return recommendations

