import unittest
from unittest.mock import Mock, patch
from pr_analysis.core.pr_analyzer import PRAnalyzer

class TestPRAnalyzer(unittest.TestCase):
    def setUp(self):
        self.github_client = Mock()
        self.rule_engine = Mock()
        self.analyzer = PRAnalyzer(self.github_client, self.rule_engine)
        
    def test_analyze_pr(self):
        # Mock PR data
        pr_data = Mock()
        pr_data.base = "base"
        pr_data.head = "head"
        
        # Mock GitHub client
        self.github_client.get_pr.return_value = pr_data
        
        # Mock rule engine
        self.rule_engine.apply_rules.return_value = ["result1", "result2"]
        
        # Call the method under test
        results = self.analyzer.analyze_pr(123, "repo")
        
        # Verify the results
        self.github_client.get_pr.assert_called_once_with(123, "repo")
        self.rule_engine.apply_rules.assert_called_once()
        self.assertEqual(results, self.analyzer._generate_report(["result1", "result2"], pr_data))
    
    def test_analyze_pr_with_no_results(self):
        # Mock PR data
        pr_data = Mock()
        pr_data.base = "base"
        pr_data.head = "head"
        
        # Mock GitHub client
        self.github_client.get_pr.return_value = pr_data
        
        # Mock rule engine with no results
        self.rule_engine.apply_rules.return_value = []
        
        # Call the method under test
        results = self.analyzer.analyze_pr(123, "repo")
        
        # Verify the results
        self.github_client.get_pr.assert_called_once_with(123, "repo")
        self.rule_engine.apply_rules.assert_called_once()
        self.assertEqual(results, self.analyzer._generate_report([], pr_data))
    
    def test_analyze_pr_with_error(self):
        # Mock GitHub client to raise an exception
        self.github_client.get_pr.side_effect = Exception("Failed to get PR")
        
        # Call the method under test and verify it raises an exception
        with self.assertRaises(Exception):
            self.analyzer.analyze_pr(123, "repo")
    
    def test_create_analysis_context(self):
        # Mock PR part data
        pr_part = Mock()
        pr_part.ref = "ref"
        pr_part.sha = "sha"
        pr_part.repo_name = "repo_name"
        
        # Call the method under test
        context = self.analyzer._create_analysis_context(pr_part)
        
        # Verify the context was created correctly
        # This will depend on the actual implementation of _create_analysis_context
        # For now, we'll just assert that it was called
        self.assertIsNotNone(context)
    
    def test_create_diff_context(self):
        # Mock base and head contexts
        base_context = Mock()
        head_context = Mock()
        
        # Call the method under test
        diff_context = self.analyzer._create_diff_context(base_context, head_context)
        
        # Verify the diff context was created correctly
        # This will depend on the actual implementation of _create_diff_context
        # For now, we'll just assert that it was called
        self.assertIsNotNone(diff_context)
    
    def test_generate_report(self):
        # Mock results and PR data
        results = ["result1", "result2"]
        pr_data = Mock()
        pr_data.number = 123
        pr_data.title = "Test PR"
        pr_data.html_url = "https://github.com/repo/pull/123"
        
        # Call the method under test
        report = self.analyzer._generate_report(results, pr_data)
        
        # Verify the report was generated correctly
        self.assertEqual(report["pr"]["number"], 123)
        self.assertEqual(report["pr"]["title"], "Test PR")
        self.assertEqual(report["pr"]["url"], "https://github.com/repo/pull/123")
        self.assertEqual(report["results"], results)
        self.assertIn("timestamp", report)

if __name__ == "__main__":
    unittest.main()

