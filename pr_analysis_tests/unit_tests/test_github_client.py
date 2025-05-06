import unittest
from unittest.mock import Mock, patch
from pr_analysis.github.pr_client import GitHubClient

class TestGitHubClient(unittest.TestCase):
    def setUp(self):
        self.token = "test_token"
        with patch('pr_analysis.github.pr_client.Github'):
            self.client = GitHubClient(self.token)
    
    @patch('pr_analysis.github.pr_client.Github')
    def test_init(self, mock_github):
        # Create a new client to test initialization
        client = GitHubClient(self.token)
        
        # Verify Github was initialized with the token
        mock_github.assert_called_once_with(self.token)
        
        # Verify the client attribute was set
        self.assertEqual(client.client, mock_github.return_value)
    
    def test_get_pr(self):
        # Mock repository and PR
        mock_repo = Mock()
        mock_pr = Mock()
        self.client.client.get_repo.return_value = mock_repo
        mock_repo.get_pull.return_value = mock_pr
        
        # Call the method under test
        pr = self.client.get_pr(123, "test/repo")
        
        # Verify the client methods were called
        self.client.client.get_repo.assert_called_once_with("test/repo")
        mock_repo.get_pull.assert_called_once_with(123)
        
        # Verify the PR was returned
        self.assertEqual(pr, mock_pr)
    
    def test_get_pr_files(self):
        # Mock PR and files
        mock_pr = Mock()
        mock_files = [Mock(), Mock(), Mock()]
        mock_pr.get_files.return_value = mock_files
        
        # Call the method under test
        files = self.client.get_pr_files(mock_pr)
        
        # Verify the PR method was called
        mock_pr.get_files.assert_called_once()
        
        # Verify the files were returned
        self.assertEqual(files, mock_files)
    
    def test_get_pr_commits(self):
        # Mock PR and commits
        mock_pr = Mock()
        mock_commits = [Mock(), Mock(), Mock()]
        mock_pr.get_commits.return_value = mock_commits
        
        # Call the method under test
        commits = self.client.get_pr_commits(mock_pr)
        
        # Verify the PR method was called
        mock_pr.get_commits.assert_called_once()
        
        # Verify the commits were returned
        self.assertEqual(commits, mock_commits)
    
    def test_post_comment(self):
        # Mock PR
        mock_pr = Mock()
        
        # Call the method under test
        self.client.post_comment(mock_pr, "Test comment")
        
        # Verify the PR method was called
        mock_pr.create_issue_comment.assert_called_once_with("Test comment")
    
    def test_post_review_comment(self):
        # Mock PR
        mock_pr = Mock()
        
        # Call the method under test
        self.client.post_review_comment(
            mock_pr, "Test comment", "commit123", "file.py", 10
        )
        
        # Verify the PR method was called
        mock_pr.create_review_comment.assert_called_once_with(
            "Test comment", "commit123", "file.py", 10
        )

if __name__ == "__main__":
    unittest.main()

