import unittest
from unittest.mock import Mock, patch
import os
import tempfile
import json

# Import the main components
from pr_analysis.core.pr_analyzer import PRAnalyzer
from pr_analysis.core.rule_engine import RuleEngine
from pr_analysis.github.pr_client import GitHubClient
from pr_analysis.reporting.report_generator import ReportGenerator
from pr_analysis.reporting.report_formatter import MarkdownReportFormatter

class TestEndToEnd(unittest.TestCase):
    def setUp(self):
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock GitHub token
        self.github_token = "test_token"
        
        # Create real components with mocked dependencies
        with patch('pr_analysis.github.pr_client.Github'):
            self.github_client = GitHubClient(self.github_token)
        
        self.rule_engine = RuleEngine([])
        self.report_generator = ReportGenerator()
        self.report_formatter = MarkdownReportFormatter()
        
        self.pr_analyzer = PRAnalyzer(self.github_client, self.rule_engine)
    
    def tearDown(self):
        # Clean up temporary directory
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.temp_dir)
    
    @patch('pr_analysis.github.pr_client.GitHubClient.get_pr')
    @patch('pr_analysis.core.pr_analyzer.PRAnalyzer._create_analysis_context')
    @patch('pr_analysis.core.pr_analyzer.PRAnalyzer._create_diff_context')
    @patch('pr_analysis.core.rule_engine.RuleEngine.apply_rules')
    def test_analyze_pr_end_to_end(self, mock_apply_rules, mock_create_diff_context, 
                                  mock_create_analysis_context, mock_get_pr):
        # Mock PR data
        mock_pr = Mock()
        mock_pr.number = 123
        mock_pr.title = "Test PR"
        mock_pr.html_url = "https://github.com/test/repo/pull/123"
        mock_pr.base = Mock(ref="main")
        mock_pr.head = Mock(ref="feature")
        
        # Mock get_pr
        mock_get_pr.return_value = mock_pr
        
        # Mock contexts
        mock_base_context = Mock()
        mock_head_context = Mock()
        mock_diff_context = Mock()
        
        # Mock _create_analysis_context
        mock_create_analysis_context.side_effect = [mock_base_context, mock_head_context]
        
        # Mock _create_diff_context
        mock_create_diff_context.return_value = mock_diff_context
        
        # Mock apply_rules
        mock_result = Mock()
        mock_result.rule_id = "CI001"
        mock_result.severity = "error"
        mock_result.message = "Syntax error"
        mock_result.file = "file1.py"
        mock_result.line = 10
        mock_result.column = 5
        mock_result.to_dict.return_value = {
            "rule_id": "CI001",
            "severity": "error",
            "message": "Syntax error",
            "file": "file1.py",
            "line": 10,
            "column": 5
        }
        mock_apply_rules.return_value = [mock_result]
        
        # Call the method under test
        results = self.pr_analyzer.analyze_pr(123, "test/repo")
        
        # Verify get_pr was called
        mock_get_pr.assert_called_once_with(123, "test/repo")
        
        # Verify _create_analysis_context was called twice
        self.assertEqual(mock_create_analysis_context.call_count, 2)
        mock_create_analysis_context.assert_any_call(mock_pr.base)
        mock_create_analysis_context.assert_any_call(mock_pr.head)
        
        # Verify _create_diff_context was called
        mock_create_diff_context.assert_called_once_with(mock_base_context, mock_head_context)
        
        # Verify apply_rules was called
        mock_apply_rules.assert_called_once_with(mock_diff_context)
        
        # Verify the results structure
        self.assertIn("pr", results)
        self.assertEqual(results["pr"]["number"], 123)
        self.assertEqual(results["pr"]["title"], "Test PR")
        self.assertEqual(results["pr"]["url"], "https://github.com/test/repo/pull/123")
        self.assertEqual(results["pr"]["base"], "main")
        self.assertEqual(results["pr"]["head"], "feature")
        
        self.assertIn("summary", results)
        self.assertEqual(results["summary"]["error_count"], 1)
        self.assertEqual(results["summary"]["warning_count"], 0)
        self.assertEqual(results["summary"]["info_count"], 0)
        self.assertEqual(results["summary"]["total_count"], 1)
        self.assertTrue(results["summary"]["has_errors"])
        self.assertFalse(results["summary"]["has_warnings"])
        
        self.assertIn("results", results)
        self.assertEqual(len(results["results"]), 1)
        self.assertEqual(results["results"][0]["rule_id"], "CI001")
        self.assertEqual(results["results"][0]["severity"], "error")
        self.assertEqual(results["results"][0]["message"], "Syntax error")
        self.assertEqual(results["results"][0]["file"], "file1.py")
        self.assertEqual(results["results"][0]["line"], 10)
        self.assertEqual(results["results"][0]["column"], 5)
        
        self.assertIn("timestamp", results)
    
    @patch('pr_analysis.github.pr_client.GitHubClient.get_pr')
    @patch('pr_analysis.core.pr_analyzer.PRAnalyzer._create_analysis_context')
    @patch('pr_analysis.core.pr_analyzer.PRAnalyzer._create_diff_context')
    @patch('pr_analysis.core.rule_engine.RuleEngine.apply_rules')
    @patch('pr_analysis.github.pr_client.GitHubClient.post_comment')
    def test_analyze_and_post_results(self, mock_post_comment, mock_apply_rules, 
                                     mock_create_diff_context, mock_create_analysis_context, 
                                     mock_get_pr):
        # Mock PR data
        mock_pr = Mock()
        mock_pr.number = 123
        mock_pr.title = "Test PR"
        mock_pr.html_url = "https://github.com/test/repo/pull/123"
        mock_pr.base = Mock(ref="main")
        mock_pr.head = Mock(ref="feature")
        
        # Mock get_pr
        mock_get_pr.return_value = mock_pr
        
        # Mock contexts
        mock_base_context = Mock()
        mock_head_context = Mock()
        mock_diff_context = Mock()
        
        # Mock _create_analysis_context
        mock_create_analysis_context.side_effect = [mock_base_context, mock_head_context]
        
        # Mock _create_diff_context
        mock_create_diff_context.return_value = mock_diff_context
        
        # Mock apply_rules
        mock_result = Mock()
        mock_result.rule_id = "CI001"
        mock_result.severity = "error"
        mock_result.message = "Syntax error"
        mock_result.file = "file1.py"
        mock_result.line = 10
        mock_result.column = 5
        mock_result.to_dict.return_value = {
            "rule_id": "CI001",
            "severity": "error",
            "message": "Syntax error",
            "file": "file1.py",
            "line": 10,
            "column": 5
        }
        mock_apply_rules.return_value = [mock_result]
        
        # Analyze the PR
        results = self.pr_analyzer.analyze_pr(123, "test/repo")
        
        # Format the results as Markdown
        markdown = self.report_formatter.format_report(results)
        
        # Post the results as a comment
        self.github_client.post_comment(mock_pr, markdown)
        
        # Verify post_comment was called with the formatted results
        mock_post_comment.assert_called_once()
        self.assertIn("# PR Analysis Report for #123", mock_post_comment.call_args[0][1])

if __name__ == "__main__":
    unittest.main()

