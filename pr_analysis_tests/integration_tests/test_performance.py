import unittest
from unittest.mock import Mock, patch
import time
import os
import tempfile
import random
import string

# Import the main components
from pr_analysis.core.pr_analyzer import PRAnalyzer
from pr_analysis.core.rule_engine import RuleEngine
from pr_analysis.github.pr_client import GitHubClient

class TestPerformance(unittest.TestCase):
    def setUp(self):
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock GitHub token
        self.github_token = "test_token"
        
        # Create real components with mocked dependencies
        with patch('pr_analysis.github.pr_client.Github'):
            self.github_client = GitHubClient(self.github_token)
        
        self.rule_engine = RuleEngine([])
        self.pr_analyzer = PRAnalyzer(self.github_client, self.rule_engine)
    
    def tearDown(self):
        # Clean up temporary directory
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.temp_dir)
    
    def _generate_random_file_content(self, size_kb):
        """Generate random file content of the specified size in KB."""
        chars = string.ascii_letters + string.digits + string.punctuation + ' \n\t'
        return ''.join(random.choice(chars) for _ in range(size_kb * 1024))
    
    def _create_test_file(self, filename, size_kb):
        """Create a test file with random content of the specified size in KB."""
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w') as f:
            f.write(self._generate_random_file_content(size_kb))
        return filepath
    
    @patch('pr_analysis.github.pr_client.GitHubClient.get_pr')
    @patch('pr_analysis.core.pr_analyzer.PRAnalyzer._create_analysis_context')
    @patch('pr_analysis.core.pr_analyzer.PRAnalyzer._create_diff_context')
    @patch('pr_analysis.core.rule_engine.RuleEngine.apply_rules')
    def test_analyze_large_pr(self, mock_apply_rules, mock_create_diff_context, 
                             mock_create_analysis_context, mock_get_pr):
        # Create a large PR with many files
        num_files = 100
        file_size_kb = 10
        
        # Create test files
        for i in range(num_files):
            self._create_test_file(f"file{i}.py", file_size_kb)
        
        # Mock PR data
        mock_pr = Mock()
        mock_pr.number = 123
        mock_pr.title = "Large Test PR"
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
        
        # Mock apply_rules to return a result for each file
        mock_results = []
        for i in range(num_files):
            mock_result = Mock()
            mock_result.rule_id = f"CI{i:03d}"
            mock_result.severity = random.choice(["error", "warning", "info"])
            mock_result.message = f"Test message {i}"
            mock_result.file = f"file{i}.py"
            mock_result.line = random.randint(1, 100)
            mock_result.column = random.randint(1, 80)
            mock_result.to_dict.return_value = {
                "rule_id": mock_result.rule_id,
                "severity": mock_result.severity,
                "message": mock_result.message,
                "file": mock_result.file,
                "line": mock_result.line,
                "column": mock_result.column
            }
            mock_results.append(mock_result)
        
        mock_apply_rules.return_value = mock_results
        
        # Measure the time it takes to analyze the PR
        start_time = time.time()
        results = self.pr_analyzer.analyze_pr(123, "test/repo")
        end_time = time.time()
        
        # Calculate the elapsed time
        elapsed_time = end_time - start_time
        
        # Print the performance metrics
        print(f"Analyzed {num_files} files ({num_files * file_size_kb} KB total) in {elapsed_time:.2f} seconds")
        print(f"Average time per file: {(elapsed_time / num_files) * 1000:.2f} ms")
        print(f"Average time per KB: {(elapsed_time / (num_files * file_size_kb)) * 1000:.2f} ms")
        
        # Verify the results
        self.assertEqual(len(results["results"]), num_files)
    
    @patch('pr_analysis.github.pr_client.GitHubClient.get_pr')
    @patch('pr_analysis.core.pr_analyzer.PRAnalyzer._create_analysis_context')
    @patch('pr_analysis.core.pr_analyzer.PRAnalyzer._create_diff_context')
    @patch('pr_analysis.core.rule_engine.RuleEngine.apply_rules')
    def test_analyze_complex_pr(self, mock_apply_rules, mock_create_diff_context, 
                               mock_create_analysis_context, mock_get_pr):
        # Create a complex PR with different file types and sizes
        file_specs = [
            ("small.py", 1),      # Small Python file (1 KB)
            ("medium.py", 10),    # Medium Python file (10 KB)
            ("large.py", 100),    # Large Python file (100 KB)
            ("small.js", 1),      # Small JavaScript file (1 KB)
            ("medium.js", 10),    # Medium JavaScript file (10 KB)
            ("large.js", 100),    # Large JavaScript file (100 KB)
            ("small.html", 1),    # Small HTML file (1 KB)
            ("medium.html", 10),  # Medium HTML file (10 KB)
            ("large.html", 100)   # Large HTML file (100 KB)
        ]
        
        # Create test files
        for filename, size_kb in file_specs:
            self._create_test_file(filename, size_kb)
        
        # Mock PR data
        mock_pr = Mock()
        mock_pr.number = 123
        mock_pr.title = "Complex Test PR"
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
        
        # Mock apply_rules to return a result for each file
        mock_results = []
        for filename, size_kb in file_specs:
            # Generate more results for larger files
            num_results = max(1, size_kb // 10)
            for i in range(num_results):
                mock_result = Mock()
                mock_result.rule_id = f"CI{len(mock_results):03d}"
                mock_result.severity = random.choice(["error", "warning", "info"])
                mock_result.message = f"Test message for {filename} #{i}"
                mock_result.file = filename
                mock_result.line = random.randint(1, size_kb * 10)
                mock_result.column = random.randint(1, 80)
                mock_result.to_dict.return_value = {
                    "rule_id": mock_result.rule_id,
                    "severity": mock_result.severity,
                    "message": mock_result.message,
                    "file": mock_result.file,
                    "line": mock_result.line,
                    "column": mock_result.column
                }
                mock_results.append(mock_result)
        
        mock_apply_rules.return_value = mock_results
        
        # Measure the time it takes to analyze the PR
        start_time = time.time()
        results = self.pr_analyzer.analyze_pr(123, "test/repo")
        end_time = time.time()
        
        # Calculate the elapsed time
        elapsed_time = end_time - start_time
        
        # Calculate total size
        total_size_kb = sum(size_kb for _, size_kb in file_specs)
        
        # Print the performance metrics
        print(f"Analyzed {len(file_specs)} files ({total_size_kb} KB total) in {elapsed_time:.2f} seconds")
        print(f"Average time per file: {(elapsed_time / len(file_specs)) * 1000:.2f} ms")
        print(f"Average time per KB: {(elapsed_time / total_size_kb) * 1000:.2f} ms")
        
        # Verify the results
        self.assertEqual(len(results["results"]), len(mock_results))

if __name__ == "__main__":
    unittest.main()

