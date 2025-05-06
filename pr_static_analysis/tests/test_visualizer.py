"""
Tests for the ReportVisualizer classes.
"""

import unittest
from pr_static_analysis.report.visualizer import (
    ChartVisualizer,
    BarChartVisualizer,
    FileIssueDistributionVisualizer
)


class TestReportVisualizer(unittest.TestCase):
    """
    Tests for the ReportVisualizer classes.
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
                        "file": "utils.py",
                        "line": 20
                    }
                ]
            },
            "recommendations": [
                "Add a return type annotation to the function",
                "Remove the unused variable or use it"
            ]
        }
    
    def test_chart_visualizer(self):
        """
        Test the ChartVisualizer.
        """
        visualizer = ChartVisualizer()
        visualization = visualizer.generate_visualization(self.sample_report)
        
        self.assertEqual(visualization["type"], "pie")
        self.assertEqual(visualization["data"]["labels"], ["Errors", "Warnings", "Info"])
        self.assertEqual(visualization["data"]["datasets"][0]["data"], [1, 1, 1])
        self.assertEqual(visualization["data"]["datasets"][0]["backgroundColor"], ["#ff6384", "#ffcd56", "#36a2eb"])
    
    def test_bar_chart_visualizer(self):
        """
        Test the BarChartVisualizer.
        """
        visualizer = BarChartVisualizer()
        visualization = visualizer.generate_visualization(self.sample_report)
        
        self.assertEqual(visualization["type"], "bar")
        self.assertEqual(visualization["data"]["labels"], ["Errors", "Warnings", "Info"])
        self.assertEqual(visualization["data"]["datasets"][0]["data"], [1, 1, 1])
        self.assertEqual(visualization["data"]["datasets"][0]["backgroundColor"], ["#ff6384", "#ffcd56", "#36a2eb"])
        self.assertTrue(visualization["options"]["scales"]["y"]["beginAtZero"])
    
    def test_file_issue_distribution_visualizer(self):
        """
        Test the FileIssueDistributionVisualizer.
        """
        visualizer = FileIssueDistributionVisualizer()
        visualization = visualizer.generate_visualization(self.sample_report)
        
        self.assertEqual(visualization["type"], "bar")
        self.assertIn("example.py", visualization["data"]["labels"])
        self.assertIn("utils.py", visualization["data"]["labels"])
        
        # Check that we have three datasets (error, warning, info)
        self.assertEqual(len(visualization["data"]["datasets"]), 3)
        self.assertEqual(visualization["data"]["datasets"][0]["label"], "Errors")
        self.assertEqual(visualization["data"]["datasets"][1]["label"], "Warnings")
        self.assertEqual(visualization["data"]["datasets"][2]["label"], "Info")
        
        # Check that the stacked option is enabled
        self.assertTrue(visualization["options"]["scales"]["x"]["stacked"])
        self.assertTrue(visualization["options"]["scales"]["y"]["stacked"])
        self.assertTrue(visualization["options"]["scales"]["y"]["beginAtZero"])


if __name__ == "__main__":
    unittest.main()

