"""
Tests for the ReportGenerator class.
"""

import unittest
from pr_static_analysis.report.generator import ReportGenerator
from pr_static_analysis.report.formatter import MarkdownReportFormatter


class TestReportGenerator(unittest.TestCase):
    """
    Tests for the ReportGenerator class.
    """
    
    def setUp(self):
        """
        Set up the test case.
        """
        self.generator = ReportGenerator(formatter=MarkdownReportFormatter())
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
    
    def test_generate_summary(self):
        """
        Test the _generate_summary method.
        """
        summary = self.generator._generate_summary(self.sample_results)
        
        self.assertEqual(summary["total_issues"], 3)
        self.assertEqual(summary["error_count"], 1)
        self.assertEqual(summary["warning_count"], 1)
        self.assertEqual(summary["info_count"], 1)
        self.assertFalse(summary["is_valid"])
    
    def test_generate_details(self):
        """
        Test the _generate_details method.
        """
        details = self.generator._generate_details(self.sample_results)
        
        self.assertEqual(details["issues"], self.sample_results)
    
    def test_generate_recommendations(self):
        """
        Test the _generate_recommendations method.
        """
        recommendations = self.generator._generate_recommendations(self.sample_results)
        
        self.assertEqual(len(recommendations), 2)
        self.assertIn("Add a return type annotation to the function", recommendations)
        self.assertIn("Remove the unused variable or use it", recommendations)
    
    def test_generate_report(self):
        """
        Test the generate_report method.
        """
        report = self.generator.generate_report(self.sample_results)
        
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


if __name__ == "__main__":
    unittest.main()

