"""
Unit tests for the analysis rules.
"""

import unittest
from unittest.mock import MagicMock
from pr_agent.analysis.rules.file_size_rule import FileSizeRule
from pr_agent.analysis.rules.naming_convention_rule import NamingConventionRule
from pr_agent.analysis.analysis_context import AnalysisContext
from pr_agent.algo.types import FilePatchInfo, EDIT_TYPE

class TestFileSizeRule(unittest.TestCase):
    """Test cases for the FileSizeRule."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.rule = FileSizeRule(max_file_size_kb=1)  # 1KB limit for testing
        
        # Create a mock context
        self.context = MagicMock(spec=AnalysisContext)
        
        # Create test files
        self.small_file = MagicMock(spec=FilePatchInfo)
        self.small_file.filename = 'small_file.py'
        self.small_file.head_file = 'a' * 500  # 500 bytes
        self.small_file.edit_type = EDIT_TYPE.MODIFIED
        
        self.large_file = MagicMock(spec=FilePatchInfo)
        self.large_file.filename = 'large_file.py'
        self.large_file.head_file = 'a' * 2000  # 2000 bytes (> 1KB)
        self.large_file.edit_type = EDIT_TYPE.MODIFIED
        
    def test_small_file_passes(self):
        """Test that a small file passes the rule."""
        self.context.get_changed_files.return_value = [self.small_file]
        
        result = self.rule.run(self.context)
        
        self.assertTrue(result['passed'])
        self.assertEqual(len(result['issues']), 0)
        
    def test_large_file_fails(self):
        """Test that a large file fails the rule."""
        self.context.get_changed_files.return_value = [self.large_file]
        
        result = self.rule.run(self.context)
        
        self.assertFalse(result['passed'])
        self.assertEqual(len(result['issues']), 1)
        self.assertEqual(result['issues'][0]['file'], 'large_file.py')
        self.assertEqual(result['issues'][0]['severity'], 'medium')
        
    def test_mixed_files(self):
        """Test with a mix of small and large files."""
        self.context.get_changed_files.return_value = [self.small_file, self.large_file]
        
        result = self.rule.run(self.context)
        
        self.assertFalse(result['passed'])
        self.assertEqual(len(result['issues']), 1)
        self.assertEqual(result['issues'][0]['file'], 'large_file.py')

class TestNamingConventionRule(unittest.TestCase):
    """Test cases for the NamingConventionRule."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.rule = NamingConventionRule()
        
        # Create a mock context
        self.context = MagicMock(spec=AnalysisContext)
        
    def test_python_file_naming(self):
        """Test Python file naming conventions."""
        # Good file name
        good_file = MagicMock(spec=FilePatchInfo)
        good_file.filename = 'good_file.py'
        good_file.head_file = ''
        
        # Bad file name
        bad_file = MagicMock(spec=FilePatchInfo)
        bad_file.filename = 'BadFile.py'
        bad_file.head_file = ''
        
        self.context.get_changed_files.return_value = [good_file, bad_file]
        
        result = self.rule.run(self.context)
        
        self.assertFalse(result['passed'])
        self.assertEqual(len(result['issues']), 1)
        self.assertEqual(result['issues'][0]['file'], 'BadFile.py')
        
    def test_js_file_naming(self):
        """Test JavaScript file naming conventions."""
        # Good file name
        good_file = MagicMock(spec=FilePatchInfo)
        good_file.filename = 'goodFile.js'
        good_file.head_file = ''
        
        # Bad file name
        bad_file = MagicMock(spec=FilePatchInfo)
        bad_file.filename = 'bad_file.js'
        bad_file.head_file = ''
        
        self.context.get_changed_files.return_value = [good_file, bad_file]
        
        result = self.rule.run(self.context)
        
        self.assertFalse(result['passed'])
        self.assertEqual(len(result['issues']), 1)
        self.assertEqual(result['issues'][0]['file'], 'bad_file.js')
        
    def test_python_function_naming(self):
        """Test Python function naming conventions."""
        file = MagicMock(spec=FilePatchInfo)
        file.filename = 'test.py'
        file.head_file = """
def good_function():
    pass
    
def BadFunction():
    pass
"""
        
        self.context.get_changed_files.return_value = [file]
        
        result = self.rule.run(self.context)
        
        self.assertFalse(result['passed'])
        self.assertEqual(len(result['issues']), 1)
        self.assertEqual(result['issues'][0]['message'], "Function name 'BadFunction' does not follow snake_case convention")
        
    def test_python_class_naming(self):
        """Test Python class naming conventions."""
        file = MagicMock(spec=FilePatchInfo)
        file.filename = 'test.py'
        file.head_file = """
class GoodClass:
    pass
    
class bad_class:
    pass
"""
        
        self.context.get_changed_files.return_value = [file]
        
        result = self.rule.run(self.context)
        
        self.assertFalse(result['passed'])
        self.assertEqual(len(result['issues']), 1)
        self.assertEqual(result['issues'][0]['message'], "Class name 'bad_class' does not follow PascalCase convention")
        
    def test_js_function_naming(self):
        """Test JavaScript function naming conventions."""
        file = MagicMock(spec=FilePatchInfo)
        file.filename = 'test.js'
        file.head_file = """
function goodFunction() {
    return true;
}
    
function Bad_Function() {
    return false;
}
"""
        
        self.context.get_changed_files.return_value = [file]
        
        result = self.rule.run(self.context)
        
        self.assertFalse(result['passed'])
        self.assertEqual(len(result['issues']), 1)
        self.assertEqual(result['issues'][0]['message'], "Function name 'Bad_Function' does not follow camelCase convention")

if __name__ == '__main__':
    unittest.main()

