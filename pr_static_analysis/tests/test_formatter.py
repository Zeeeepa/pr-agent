"""
Tests for the ReportFormatter classes.
"""

import unittest
import json
from pr_static_analysis.report.formatter import (
    ReportFormatter,
    DefaultReportFormatter,
    MarkdownReportFormatter,
    HTMLReportFormatter,
    JSONReportFormatter
)


class TestReportFormatter(unittest.TestCase):
    """
    Tests for the ReportFormatter classes.
    """
    
    def setUp(self):
        """
        Set up the test case.
        """
        self.sample_report = {
            "summary": {
                "total_issues": 3,
                "error_count": 1,
                "warning_count": 1,
                "info_count": 1,
                "is_valid": False
            },
            "details": {
                "issues": [
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
                        "file": "example.py",
                        "line": 20
                    }
                ]
            },
            "recommendations": [
                "Add a return type annotation to the function",
                "Remove the unused variable or use it"
            ]
        }
    
    def test_default_formatter(self):
        """
        Test the DefaultReportFormatter.
        """
        formatter = DefaultReportFormatter()
        report = formatter.format_report(self.sample_report)
        
        self.assertIsInstance(report, str)
        self.assertIn("# PR Static Analysis Report", report)
    
    def test_markdown_formatter(self):
        """
        Test the MarkdownReportFormatter.
        """
        formatter = MarkdownReportFormatter()
        report = formatter.format_report(self.sample_report)
        
        self.assertIsInstance(report, str)
        self.assertIn("# PR Static Analysis Report", report)
        self.assertIn("## Summary", report)
        self.assertIn("## Details", report)
        self.assertIn("## Recommendations", report)
        self.assertIn("Total issues: 3", report)
        self.assertIn("Errors: 1", report)
        self.assertIn("Warnings: 1", report)
        self.assertIn("Info: 1", report)
        self.assertIn("Valid implementation: No", report)
        self.assertIn("**ERROR**: Missing return type annotation in `example.py` at line 10", report)
        self.assertIn("**WARNING**: Unused variable in `example.py` at line 15", report)
        self.assertIn("**INFO**: Consider using a more descriptive variable name in `example.py` at line 20", report)
        self.assertIn("Add a return type annotation to the function", report)
        self.assertIn("Remove the unused variable or use it", report)
    
    def test_html_formatter(self):
        """
        Test the HTMLReportFormatter.
        """
        formatter = HTMLReportFormatter()
        report = formatter.format_report(self.sample_report)
        
        self.assertIsInstance(report, str)
        self.assertIn("<!DOCTYPE html>", report)
        self.assertIn("<title>PR Static Analysis Report</title>", report)
        self.assertIn("<h1>PR Static Analysis Report</h1>", report)
        self.assertIn("<h2>Summary</h2>", report)
        self.assertIn("<h2>Details</h2>", report)
        self.assertIn("<h2>Recommendations</h2>", report)
        self.assertIn("Total issues: 3", report)
        self.assertIn("Errors: 1", report)
        self.assertIn("Warnings: 1", report)
        self.assertIn("Info: 1", report)
        self.assertIn("Valid implementation: No", report)
        self.assertIn("<span class='error'><strong>ERROR</strong></span>: Missing return type annotation", report)
        self.assertIn("<span class='warning'><strong>WARNING</strong></span>: Unused variable", report)
        self.assertIn("<span class='info'><strong>INFO</strong></span>: Consider using a more descriptive variable name", report)
        self.assertIn("Add a return type annotation to the function", report)
        self.assertIn("Remove the unused variable or use it", report)
    
    def test_json_formatter(self):
        """
        Test the JSONReportFormatter.
        """
        formatter = JSONReportFormatter()
        report = formatter.format_report(self.sample_report)
        
        self.assertIsInstance(report, str)
        
        # Parse the JSON to verify it's valid
        parsed_report = json.loads(report)
        
        self.assertEqual(parsed_report, self.sample_report)


if __name__ == "__main__":
    unittest.main()

