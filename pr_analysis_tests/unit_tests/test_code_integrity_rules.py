import unittest
from unittest.mock import Mock, patch
from pr_analysis.rules.code_integrity_rules import SyntaxErrorRule, UndefinedReferenceRule

class TestSyntaxErrorRule(unittest.TestCase):
    def setUp(self):
        self.rule = SyntaxErrorRule()
    
    def test_init(self):
        # Verify the rule was initialized correctly
        self.assertEqual(self.rule.rule_id, "CI001")
        self.assertEqual(self.rule.name, "Syntax Error Check")
        self.assertIn("syntax errors", self.rule.description.lower())
    
    def test_apply_no_changes(self):
        # Mock context with no file changes
        context = Mock()
        context.get_file_changes.return_value = {}
        
        # Call the method under test
        results = self.rule.apply(context)
        
        # Verify no results were returned
        self.assertEqual(results, [])
    
    def test_apply_with_changes_no_errors(self):
        # Mock context with file changes but no syntax errors
        context = Mock()
        context.get_file_changes.return_value = {
            "file1.py": "added",
            "file2.py": "modified"
        }
        context.head_context.get_file_content.return_value = "def valid_function():\n    return True"
        
        # Mock _check_syntax to return no errors
        with patch.object(self.rule, '_check_syntax', return_value=[]):
            # Call the method under test
            results = self.rule.apply(context)
            
            # Verify _check_syntax was called for each changed file
            self.assertEqual(self.rule._check_syntax.call_count, 2)
            
            # Verify no results were returned
            self.assertEqual(results, [])
    
    def test_apply_with_changes_with_errors(self):
        # Mock context with file changes and syntax errors
        context = Mock()
        context.get_file_changes.return_value = {
            "file1.py": "added",
            "file2.py": "modified"
        }
        context.head_context.get_file_content.return_value = "def invalid_function():\n    return True"
        
        # Mock _check_syntax to return errors for file1.py
        mock_error = Mock()
        with patch.object(self.rule, '_check_syntax', return_value=[mock_error]):
            # Call the method under test
            results = self.rule.apply(context)
            
            # Verify _check_syntax was called for each changed file
            self.assertEqual(self.rule._check_syntax.call_count, 2)
            
            # Verify the errors were returned
            self.assertEqual(results, [mock_error, mock_error])

class TestUndefinedReferenceRule(unittest.TestCase):
    def setUp(self):
        self.rule = UndefinedReferenceRule()
    
    def test_init(self):
        # Verify the rule was initialized correctly
        self.assertEqual(self.rule.rule_id, "CI002")
        self.assertEqual(self.rule.name, "Undefined Reference Check")
        self.assertIn("undefined references", self.rule.description.lower())
    
    def test_apply(self):
        # Mock context
        context = Mock()
        
        # Mock implementation of apply
        with patch.object(self.rule, 'apply', return_value=[]):
            # Call the method under test
            results = self.rule.apply(context)
            
            # Verify the results
            self.assertEqual(results, [])

if __name__ == "__main__":
    unittest.main()

