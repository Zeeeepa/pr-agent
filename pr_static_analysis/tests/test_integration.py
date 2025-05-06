"""
Tests for the integration module.
"""

import unittest
from unittest.mock import MagicMock
from pr_static_analysis.report.integration import (
    AnalysisReportIntegration,
    create_markdown_report_integration,
    create_html_report_integration,
    create_json_report_integration
)
from pr_static_analysis.report.formatter import (
    MarkdownReportFormatter,
    HTMLReportFormatter,
    JSONReportFormatter
)
from pr_static_analysis.report.visualizer import ChartVisualizer


class TestAnalysisReportIntegration(unittest.TestCase):
    """
    Tests for the AnalysisReportIntegration class.
    """
    
    def setUp(self):
        """
        Set up the test case.
        """
        self.integration = AnalysisReportIntegration(
            formatter=MarkdownReportFormatter(),
            visualizer=ChartVisualizer()
        )
        self.sample_results = [
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
    
    def test_generate_report(self):
        """
        Test the generate_report method.
        """
        report = self.integration.generate_report(self.sample_results)
        
        self.assertIn("report", report)
        self.assertIn("visualization", report)
        
        self.assertIsInstance(report["report"], str)
        self.assertIn("# PR Static Analysis Report", report["report"])
        
        self.assertEqual(report["visualization"]["type"], "pie")
        self.assertEqual(report["visualization"]["data"]["labels"], ["Errors", "Warnings", "Info"])
        self.assertEqual(report["visualization"]["data"]["datasets"][0]["data"], [1, 1, 1])
    
    def test_post_report_to_github(self):
        """
        Test the post_report_to_github method.
        """
        # Create a mock for the GitHub API callback
        mock_callback = MagicMock()
        mock_callback.return_value = {"id": 12345}
        
        # Generate a report
        report = self.integration.generate_report(self.sample_results)
        
        # Post the report to GitHub
        result = self.integration.post_report_to_github(
            report=report,
            pr_number=123,
            repo_owner="owner",
            repo_name="repo",
            github_api_callback=mock_callback
        )
        
        # Check that the callback was called with the correct arguments
        mock_callback.assert_called_once_with(
            "https://api.github.com/repos/owner/repo/issues/123/comments",
            {"body": report["report"]}
        )
        
        # Check that the result is correct
        self.assertEqual(result, {"id": 12345})
    
    def test_create_markdown_report_integration(self):
        """
        Test the create_markdown_report_integration function.
        """
        integration = create_markdown_report_integration()
        
        self.assertIsInstance(integration, AnalysisReportIntegration)
        self.assertIsInstance(integration.generator.formatter, MarkdownReportFormatter)
        self.assertIsInstance(integration.visualizer, ChartVisualizer)
    
    def test_create_html_report_integration(self):
        """
        Test the create_html_report_integration function.
        """
        integration = create_html_report_integration()
        
        self.assertIsInstance(integration, AnalysisReportIntegration)
        self.assertIsInstance(integration.generator.formatter, HTMLReportFormatter)
        self.assertIsInstance(integration.visualizer, ChartVisualizer)
    
    def test_create_json_report_integration(self):
        """
        Test the create_json_report_integration function.
        """
        integration = create_json_report_integration()
        
        self.assertIsInstance(integration, AnalysisReportIntegration)
        self.assertIsInstance(integration.generator.formatter, JSONReportFormatter)
        self.assertIsInstance(integration.visualizer, ChartVisualizer)


if __name__ == "__main__":
    unittest.main()

