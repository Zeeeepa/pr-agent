"""
Unit tests for the PR Analyzer.
"""

import unittest
from unittest.mock import MagicMock, patch
from pr_agent.analysis.pr_analyzer import PRAnalyzer
from pr_agent.analysis.rule_engine import RuleEngine, Rule
from pr_agent.analysis.analysis_context import AnalysisContext

class TestRule(Rule):
    """Test rule implementation."""
    
    def __init__(self, rule_id, description, priority=0, should_pass=True):
        super().__init__(rule_id, description, priority)
        self.should_pass = should_pass
        
    def run(self, context):
        if self.should_pass:
            return {
                'rule_id': self.rule_id,
                'description': self.description,
                'issues': [],
                'passed': True,
            }
        else:
            return {
                'rule_id': self.rule_id,
                'description': self.description,
                'issues': [{
                    'file': 'test.py',
                    'message': 'Test issue',
                    'severity': 'medium',
                    'line': 1,
                }],
                'passed': False,
            }

class TestPRAnalyzer(unittest.TestCase):
    """Test cases for the PR Analyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.rule_engine = RuleEngine()
        self.github_client = MagicMock()
        self.analyzer = PRAnalyzer(self.rule_engine, self.github_client)
        
        # Add test rules
        self.rule_engine.register_rule(TestRule('test_rule_1', 'Test rule 1', 10, True))
        self.rule_engine.register_rule(TestRule('test_rule_2', 'Test rule 2', 5, False))
        
        # Mock GitHub client
        repo_mock = MagicMock()
        pr_mock = MagicMock()
        pr_mock.title = 'Test PR'
        pr_mock.body = 'Test PR body'
        pr_mock.base.sha = 'base_sha'
        pr_mock.head.sha = 'head_sha'
        pr_mock.get_files.return_value = []
        pr_mock.user.login = 'test_user'
        pr_mock.created_at = '2023-01-01T00:00:00Z'
        pr_mock.updated_at = '2023-01-02T00:00:00Z'
        pr_mock.state = 'open'
        pr_mock.labels = []
        
        repo_mock.get_pull.return_value = pr_mock
        self.github_client.get_repo.return_value = repo_mock
        
    def test_analyze_pr(self):
        """Test analyzing a PR."""
        report = self.analyzer.analyze_pr('test/repo', 123)
        
        # Verify GitHub client was called correctly
        self.github_client.get_repo.assert_called_once_with('test/repo')
        self.github_client.get_repo().get_pull.assert_called_once_with(123)
        
        # Verify report structure
        self.assertIn('pr_info', report)
        self.assertIn('analysis_results', report)
        self.assertIn('summary', report)
        
        # Verify PR info
        self.assertEqual(report['pr_info']['repo'], 'test/repo')
        self.assertEqual(report['pr_info']['pr_number'], 123)
        self.assertEqual(report['pr_info']['title'], 'Test PR')
        
        # Verify analysis results
        self.assertIn('test_rule_1', report['analysis_results'])
        self.assertIn('test_rule_2', report['analysis_results'])
        self.assertTrue(report['analysis_results']['test_rule_1']['passed'])
        self.assertFalse(report['analysis_results']['test_rule_2']['passed'])
        
        # Verify summary
        self.assertEqual(report['summary']['total_rules_run'], 2)
        self.assertEqual(report['summary']['total_issues'], 1)
        self.assertEqual(report['summary']['issue_counts']['medium'], 1)
        
    def test_rule_dependencies(self):
        """Test rule dependencies."""
        # Create rules with dependencies
        rule1 = TestRule('dep_rule_1', 'Dependency rule 1', 10, True)
        rule2 = TestRule('dep_rule_2', 'Dependency rule 2', 5, True)
        rule2.add_dependency('dep_rule_1')
        
        # Register rules
        engine = RuleEngine()
        engine.register_rule(rule1)
        engine.register_rule(rule2)
        
        # Create analyzer with the new engine
        analyzer = PRAnalyzer(engine, self.github_client)
        
        # Analyze PR
        report = analyzer.analyze_pr('test/repo', 123)
        
        # Verify both rules ran
        self.assertIn('dep_rule_1', report['analysis_results'])
        self.assertIn('dep_rule_2', report['analysis_results'])
        
    def test_rule_priority(self):
        """Test rule priority ordering."""
        # Create a list to track execution order
        execution_order = []
        
        # Create a rule class that records execution order
        class OrderedRule(Rule):
            def __init__(self, rule_id, priority):
                super().__init__(rule_id, f"Rule {rule_id}", priority)
                
            def run(self, context):
                execution_order.append(self.rule_id)
                return {'rule_id': self.rule_id, 'passed': True}
        
        # Create rules with different priorities
        rule1 = OrderedRule('priority_rule_1', 10)
        rule2 = OrderedRule('priority_rule_2', 20)
        rule3 = OrderedRule('priority_rule_3', 5)
        
        # Register rules
        engine = RuleEngine()
        engine.register_rule(rule1)
        engine.register_rule(rule2)
        engine.register_rule(rule3)
        
        # Create analyzer with the new engine
        analyzer = PRAnalyzer(engine, self.github_client)
        
        # Analyze PR
        analyzer.analyze_pr('test/repo', 123)
        
        # Verify execution order (highest priority first)
        self.assertEqual(execution_order, ['priority_rule_2', 'priority_rule_1', 'priority_rule_3'])

if __name__ == '__main__':
    unittest.main()

