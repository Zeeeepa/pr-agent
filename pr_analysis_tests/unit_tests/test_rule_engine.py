import unittest
from unittest.mock import Mock
from pr_analysis.core.rule_engine import RuleEngine

class TestRuleEngine(unittest.TestCase):
    def setUp(self):
        self.rule1 = Mock()
        self.rule1.apply.return_value = ["result1"]
        self.rule1.rule_id = "rule1"
        self.rule1.name = "Rule 1"
        
        self.rule2 = Mock()
        self.rule2.apply.return_value = ["result2", "result3"]
        self.rule2.rule_id = "rule2"
        self.rule2.name = "Rule 2"
        
        self.engine = RuleEngine([self.rule1, self.rule2])
        
    def test_apply_rules(self):
        # Mock context
        context = Mock()
        
        # Call the method under test
        results = self.engine.apply_rules(context)
        
        # Verify the results
        self.rule1.apply.assert_called_once_with(context)
        self.rule2.apply.assert_called_once_with(context)
        self.assertEqual(results, ["result1", "result2", "result3"])
    
    def test_apply_rules_with_no_rules(self):
        # Create engine with no rules
        engine = RuleEngine([])
        
        # Mock context
        context = Mock()
        
        # Call the method under test
        results = engine.apply_rules(context)
        
        # Verify the results
        self.assertEqual(results, [])
    
    def test_apply_rules_with_rule_error(self):
        # Mock rule that raises an exception
        error_rule = Mock()
        error_rule.apply.side_effect = Exception("Rule application failed")
        error_rule.rule_id = "error_rule"
        error_rule.name = "Error Rule"
        
        # Create engine with the error rule
        engine = RuleEngine([self.rule1, error_rule, self.rule2])
        
        # Mock context
        context = Mock()
        
        # Call the method under test
        results = engine.apply_rules(context)
        
        # Verify the results - should include results from rule1 and rule2, but not error_rule
        self.rule1.apply.assert_called_once_with(context)
        error_rule.apply.assert_called_once_with(context)
        self.rule2.apply.assert_called_once_with(context)
        self.assertEqual(results, ["result1", "result2", "result3"])
    
    def test_get_rules(self):
        # Call the method under test
        rules = self.engine.get_rules()
        
        # Verify the results
        self.assertEqual(rules, [self.rule1, self.rule2])
    
    def test_add_rule(self):
        # Mock new rule
        new_rule = Mock()
        new_rule.rule_id = "new_rule"
        new_rule.name = "New Rule"
        
        # Call the method under test
        self.engine.add_rule(new_rule)
        
        # Verify the rule was added
        self.assertEqual(self.engine.get_rules(), [self.rule1, self.rule2, new_rule])
    
    def test_remove_rule(self):
        # Call the method under test
        self.engine.remove_rule("rule1")
        
        # Verify the rule was removed
        self.assertEqual(self.engine.get_rules(), [self.rule2])
    
    def test_remove_nonexistent_rule(self):
        # Call the method under test
        self.engine.remove_rule("nonexistent_rule")
        
        # Verify no rules were removed
        self.assertEqual(self.engine.get_rules(), [self.rule1, self.rule2])

if __name__ == "__main__":
    unittest.main()

