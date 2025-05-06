import unittest
from unittest.mock import Mock, patch
import json
from pr_analysis.reporting.report_formatter import MarkdownReportFormatter, HTMLReportFormatter, JSONReportFormatter

class TestMarkdownReportFormatter(unittest.TestCase):
    def setUp(self):
        self.formatter = MarkdownReportFormatter()
    
    def test_format_report_with_results(self):
        # Mock report with results
        report = {
            "pr": {
                "number": 123,
                "title": "Test PR",
                "url": "https://github.com/test/repo/pull/123",
                "base": "main",
                "head": "feature"
            },
            "summary": {
                "error_count": 1,
                "warning_count": 2,
                "info_count": 3,
                "total_count": 6,
                "has_errors": True,
                "has_warnings": True
            },
            "results": [
                {
                    "rule_id": "CI001",
                    "severity": "error",
                    "message": "Syntax error",
                    "file": "file1.py",
                    "line": 10,
                    "column": 5
                },
                {
                    "rule_id": "CI002",
                    "severity": "warning",
                    "message": "Undefined reference",
                    "file": "file2.py",
                    "line": 20,
                    "column": 10
                }
            ],
            "timestamp": "2023-01-01T00:00:00"
        }
        
        # Mock _get_severity_icon
        with patch.object(self.formatter, '_get_severity_icon') as mock_get_severity_icon:
            mock_get_severity_icon.side_effect = lambda s: ":x:" if s == "error" else ":warning:"
            
            # Call the method under test
            markdown = self.formatter.format_report(report)
            
            # Verify _get_severity_icon was called
            self.assertEqual(mock_get_severity_icon.call_count, 2)
            
            # Verify the markdown contains expected elements
            self.assertIn("# PR Analysis Report for #123", markdown)
            self.assertIn("**PR:** [Test PR](https://github.com/test/repo/pull/123)", markdown)
            self.assertIn("**Base:** `main`", markdown)
            self.assertIn("**Head:** `feature`", markdown)
            self.assertIn("## Summary", markdown)
            self.assertIn("**Errors:** 1", markdown)
            self.assertIn("**Warnings:** 2", markdown)
            self.assertIn("**Info:** 3", markdown)
            self.assertIn("**Total:** 6", markdown)
            self.assertIn("## Issues", markdown)
            self.assertIn(":x: CI001: Syntax error", markdown)
            self.assertIn("**File:** `file1.py`", markdown)
            self.assertIn("**Line:** 10", markdown)
            self.assertIn(":warning: CI002: Undefined reference", markdown)
            self.assertIn("**File:** `file2.py`", markdown)
            self.assertIn("**Line:** 20", markdown)
    
    def test_format_report_no_results(self):
        # Mock report with no results
        report = {
            "pr": {
                "number": 123,
                "title": "Test PR",
                "url": "https://github.com/test/repo/pull/123",
                "base": "main",
                "head": "feature"
            },
            "summary": {
                "error_count": 0,
                "warning_count": 0,
                "info_count": 0,
                "total_count": 0,
                "has_errors": False,
                "has_warnings": False
            },
            "results": [],
            "timestamp": "2023-01-01T00:00:00"
        }
        
        # Call the method under test
        markdown = self.formatter.format_report(report)
        
        # Verify the markdown contains expected elements
        self.assertIn("# PR Analysis Report for #123", markdown)
        self.assertIn("**PR:** [Test PR](https://github.com/test/repo/pull/123)", markdown)
        self.assertIn("**Base:** `main`", markdown)
        self.assertIn("**Head:** `feature`", markdown)
        self.assertIn("## Summary", markdown)
        self.assertIn("**Errors:** 0", markdown)
        self.assertIn("**Warnings:** 0", markdown)
        self.assertIn("**Info:** 0", markdown)
        self.assertIn("**Total:** 0", markdown)
        self.assertIn("No issues found! :white_check_mark:", markdown)
    
    def test_get_severity_icon(self):
        # Call the method under test for different severities
        error_icon = self.formatter._get_severity_icon("error")
        warning_icon = self.formatter._get_severity_icon("warning")
        info_icon = self.formatter._get_severity_icon("info")
        
        # Verify the icons
        self.assertEqual(error_icon, ":x:")
        self.assertEqual(warning_icon, ":warning:")
        self.assertEqual(info_icon, ":information_source:")

class TestJSONReportFormatter(unittest.TestCase):
    def setUp(self):
        self.formatter = JSONReportFormatter()
    
    def test_format_report(self):
        # Mock report
        report = {
            "pr": {
                "number": 123,
                "title": "Test PR",
                "url": "https://github.com/test/repo/pull/123",
                "base": "main",
                "head": "feature"
            },
            "summary": {
                "error_count": 1,
                "warning_count": 2,
                "info_count": 3,
                "total_count": 6,
                "has_errors": True,
                "has_warnings": True
            },
            "results": [
                {
                    "rule_id": "CI001",
                    "severity": "error",
                    "message": "Syntax error",
                    "file": "file1.py",
                    "line": 10,
                    "column": 5
                }
            ],
            "timestamp": "2023-01-01T00:00:00"
        }
        
        # Call the method under test
        json_str = self.formatter.format_report(report)
        
        # Parse the JSON string
        parsed_json = json.loads(json_str)
        
        # Verify the JSON structure
        self.assertEqual(parsed_json, report)

if __name__ == "__main__":
    unittest.main()

