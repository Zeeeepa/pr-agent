import unittest
from unittest.mock import Mock, patch
import json
from datetime import datetime
from pr_analysis.reporting.report_generator import ReportGenerator

class TestReportGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = ReportGenerator()
    
    def test_generate_report(self):
        # Mock results and PR context
        results = [
            Mock(severity="error", to_dict=lambda: {"severity": "error"}),
            Mock(severity="warning", to_dict=lambda: {"severity": "warning"}),
            Mock(severity="info", to_dict=lambda: {"severity": "info"})
        ]
        pr_context = Mock(
            number=123,
            title="Test PR",
            html_url="https://github.com/test/repo/pull/123",
            base=Mock(ref="main"),
            head=Mock(ref="feature")
        )
        
        # Mock _generate_summary and _get_timestamp
        with patch.object(self.generator, '_generate_summary') as mock_generate_summary:
            with patch.object(self.generator, '_get_timestamp') as mock_get_timestamp:
                mock_generate_summary.return_value = {"summary": "data"}
                mock_get_timestamp.return_value = "2023-01-01T00:00:00"
                
                # Call the method under test
                report = self.generator.generate_report(results, pr_context)
                
                # Verify _generate_summary was called
                mock_generate_summary.assert_called_once_with(results)
                
                # Verify _get_timestamp was called
                mock_get_timestamp.assert_called_once()
                
                # Verify the report structure
                self.assertEqual(report["pr"]["number"], 123)
                self.assertEqual(report["pr"]["title"], "Test PR")
                self.assertEqual(report["pr"]["url"], "https://github.com/test/repo/pull/123")
                self.assertEqual(report["pr"]["base"], "main")
                self.assertEqual(report["pr"]["head"], "feature")
                self.assertEqual(report["summary"], {"summary": "data"})
                self.assertEqual(report["results"], [r.to_dict() for r in results])
                self.assertEqual(report["timestamp"], "2023-01-01T00:00:00")
    
    def test_generate_summary(self):
        # Mock results
        results = [
            Mock(severity="error"),
            Mock(severity="error"),
            Mock(severity="warning"),
            Mock(severity="info"),
            Mock(severity="info"),
            Mock(severity="info")
        ]
        
        # Call the method under test
        summary = self.generator._generate_summary(results)
        
        # Verify the summary
        self.assertEqual(summary["error_count"], 2)
        self.assertEqual(summary["warning_count"], 1)
        self.assertEqual(summary["info_count"], 3)
        self.assertEqual(summary["total_count"], 6)
        self.assertTrue(summary["has_errors"])
        self.assertTrue(summary["has_warnings"])
    
    def test_generate_summary_no_results(self):
        # Call the method under test with no results
        summary = self.generator._generate_summary([])
        
        # Verify the summary
        self.assertEqual(summary["error_count"], 0)
        self.assertEqual(summary["warning_count"], 0)
        self.assertEqual(summary["info_count"], 0)
        self.assertEqual(summary["total_count"], 0)
        self.assertFalse(summary["has_errors"])
        self.assertFalse(summary["has_warnings"])
    
    def test_get_timestamp(self):
        # Mock datetime.utcnow
        mock_now = datetime(2023, 1, 1, 0, 0, 0)
        with patch('pr_analysis.reporting.report_generator.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = mock_now
            
            # Call the method under test
            timestamp = self.generator._get_timestamp()
            
            # Verify datetime.utcnow was called
            mock_datetime.utcnow.assert_called_once()
            
            # Verify the timestamp
            self.assertEqual(timestamp, "2023-01-01T00:00:00")

if __name__ == "__main__":
    unittest.main()

