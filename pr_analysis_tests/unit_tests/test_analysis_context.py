import unittest
from unittest.mock import Mock, patch
from pr_analysis.core.analysis_context import AnalysisContext

class TestAnalysisContext(unittest.TestCase):
    def setUp(self):
        # Mock repository data
        self.repo_name = "test/repo"
        self.ref = "main"
        self.sha = "abc123"
        
        # Create the context
        self.context = AnalysisContext(self.repo_name, self.ref, self.sha)
    
    def test_init(self):
        # Verify the context was initialized correctly
        self.assertEqual(self.context.repo_name, self.repo_name)
        self.assertEqual(self.context.ref, self.ref)
        self.assertEqual(self.context.sha, self.sha)
    
    @patch('pr_analysis.core.analysis_context.AnalysisContext._load_codebase')
    def test_load_codebase(self, mock_load_codebase):
        # Mock the _load_codebase method
        mock_codebase = Mock()
        mock_load_codebase.return_value = mock_codebase
        
        # Create a new context to trigger _load_codebase
        context = AnalysisContext(self.repo_name, self.ref, self.sha)
        
        # Verify _load_codebase was called
        mock_load_codebase.assert_called_once_with(self.repo_name, self.ref, self.sha)
        
        # Verify the codebase was set
        self.assertEqual(context.codebase, mock_codebase)
    
    def test_get_file_content(self):
        # Mock the codebase
        self.context.codebase = Mock()
        mock_content = "file content"
        self.context.codebase.get_file_content.return_value = mock_content
        
        # Call the method under test
        content = self.context.get_file_content("path/to/file.py")
        
        # Verify the codebase method was called
        self.context.codebase.get_file_content.assert_called_once_with("path/to/file.py")
        
        # Verify the content was returned
        self.assertEqual(content, mock_content)
    
    def test_get_file_content_nonexistent_file(self):
        # Mock the codebase to raise an exception for nonexistent file
        self.context.codebase = Mock()
        self.context.codebase.get_file_content.side_effect = FileNotFoundError("File not found")
        
        # Call the method under test and verify it raises an exception
        with self.assertRaises(FileNotFoundError):
            self.context.get_file_content("nonexistent/file.py")
    
    def test_get_files(self):
        # Mock the codebase
        self.context.codebase = Mock()
        mock_files = ["file1.py", "file2.py", "file3.py"]
        self.context.codebase.get_files.return_value = mock_files
        
        # Call the method under test
        files = self.context.get_files()
        
        # Verify the codebase method was called
        self.context.codebase.get_files.assert_called_once()
        
        # Verify the files were returned
        self.assertEqual(files, mock_files)
    
    def test_get_files_by_extension(self):
        # Mock the codebase
        self.context.codebase = Mock()
        mock_files = ["file1.py", "file2.py"]
        self.context.codebase.get_files_by_extension.return_value = mock_files
        
        # Call the method under test
        files = self.context.get_files_by_extension(".py")
        
        # Verify the codebase method was called
        self.context.codebase.get_files_by_extension.assert_called_once_with(".py")
        
        # Verify the files were returned
        self.assertEqual(files, mock_files)
    
    def test_get_symbols(self):
        # Mock the codebase
        self.context.codebase = Mock()
        mock_symbols = ["symbol1", "symbol2", "symbol3"]
        self.context.codebase.get_symbols.return_value = mock_symbols
        
        # Call the method under test
        symbols = self.context.get_symbols()
        
        # Verify the codebase method was called
        self.context.codebase.get_symbols.assert_called_once()
        
        # Verify the symbols were returned
        self.assertEqual(symbols, mock_symbols)
    
    def test_get_symbol_references(self):
        # Mock the codebase
        self.context.codebase = Mock()
        mock_references = ["ref1", "ref2", "ref3"]
        self.context.codebase.get_symbol_references.return_value = mock_references
        
        # Call the method under test
        references = self.context.get_symbol_references("symbol")
        
        # Verify the codebase method was called
        self.context.codebase.get_symbol_references.assert_called_once_with("symbol")
        
        # Verify the references were returned
        self.assertEqual(references, mock_references)

if __name__ == "__main__":
    unittest.main()

