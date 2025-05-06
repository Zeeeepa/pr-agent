import unittest
from unittest.mock import Mock
from pr_analysis.rules.base_rule import BaseRule, AnalysisResult

class ConcreteRule(BaseRule):
    """Concrete implementation of BaseRule for testing."""
    
    def __init__(self):
        super().__init__(
            rule_id="test_rule",
            name="Test Rule",
            description="A rule for testing"
        )
    
    def apply(self, context):
        # Simple implementation that returns a single result
        return [
            AnalysisResult(
                rule_id=self.rule_id,
                severity="warning",
                message="Test message",
                file="test_file.py",
                line=10,
                column=5
            )
        ]

class TestBaseRule(unittest.TestCase):
    def setUp(self):
        self.rule = ConcreteRule()
    
    def test_init(self):
        # Verify the rule was initialized correctly
        self.assertEqual(self.rule.rule_id, "test_rule")
        self.assertEqual(self.rule.name, "Test Rule")
        self.assertEqual(self.rule.description, "A rule for testing")
    
    def test_apply(self):
        # Mock context
        context = Mock()
        
        # Call the method under test
        results = self.rule.apply(context)
        
        # Verify the results
        self.assertEqual(len(results), 1)
        result = results[0]
        self.assertEqual(result.rule_id, "test_rule")
        self.assertEqual(result.severity, "warning")
        self.assertEqual(result.message, "Test message")
        self.assertEqual(result.file, "test_file.py")
        self.assertEqual(result.line, 10)
        self.assertEqual(result.column, 5)

class TestAnalysisResult(unittest.TestCase):
    def setUp(self):
        self.result = AnalysisResult(
            rule_id="test_rule",
            severity="error",
            message="Test error message",
            file="test_file.py",
            line=15,
            column=10
        )
    
    def test_init(self):
        # Verify the result was initialized correctly
        self.assertEqual(self.result.rule_id, "test_rule")
        self.assertEqual(self.result.severity, "error")
        self.assertEqual(self.result.message, "Test error message")
        self.assertEqual(self.result.file, "test_file.py")
        self.assertEqual(self.result.line, 15)
        self.assertEqual(self.result.column, 10)
    
    def test_to_dict(self):
        # Call the method under test
        result_dict = self.result.to_dict()
        
        # Verify the dictionary representation
        self.assertEqual(result_dict["rule_id"], "test_rule")
        self.assertEqual(result_dict["severity"], "error")
        self.assertEqual(result_dict["message"], "Test error message")
        self.assertEqual(result_dict["file"], "test_file.py")
        self.assertEqual(result_dict["line"], 15)
        self.assertEqual(result_dict["column"], 10)

if __name__ == "__main__":
    unittest.main()

