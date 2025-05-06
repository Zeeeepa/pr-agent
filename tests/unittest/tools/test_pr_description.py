import unittest
from unittest.mock import patch, MagicMock

from pr_agent.tools.pr_description import PRDescription
from pr_agent.algo.ai_handlers.base_ai_handler import BaseAiHandler


class TestPRDescription(unittest.TestCase):
    """
    Test cases for the PRDescription class.
    """

    @patch('pr_agent.tools.pr_description.get_git_provider_with_context')
    def setUp(self, mock_get_git_provider):
        """
        Set up the test environment.
        """
        self.mock_git_provider = MagicMock()
        mock_get_git_provider.return_value = self.mock_git_provider
        
        # Mock PR object
        self.mock_git_provider.pr = MagicMock()
        self.mock_git_provider.pr.title = "Test PR"
        self.mock_git_provider.get_pr_branch.return_value = "feature-branch"
        self.mock_git_provider.get_pr_description.return_value = "Test PR description"
        self.mock_git_provider.get_languages.return_value = {"Python": 100}
        self.mock_git_provider.get_files.return_value = ["test.py"]
        self.mock_git_provider.get_pr_id.return_value = "123"
        
        # Mock AI handler
        self.mock_ai_handler = MagicMock(spec=BaseAiHandler)
        self.mock_ai_handler_class = MagicMock(return_value=self.mock_ai_handler)
        
        # Initialize PRDescription
        self.pr_description = PRDescription(
            pr_url="https://github.com/test/repo/pull/1",
            ai_handler=self.mock_ai_handler_class
        )
        
    def test_initialization(self):
        """
        Test that PRDescription initializes correctly.
        """
        self.assertEqual(self.pr_description.git_provider, self.mock_git_provider)
        self.assertEqual(self.pr_description.pr_id, "123")
        
    @patch('pr_agent.tools.pr_description.get_pr_diff')
    @patch('pr_agent.tools.pr_description.retry_with_fallback_models')
    def test_generate_description(self, mock_retry, mock_get_pr_diff):
        """
        Test the describe method.
        """
        # Mock the PR diff
        mock_get_pr_diff.return_value = "test diff"
        
        # Mock the AI response
        mock_retry.return_value = """
        title: Improved Feature
        description: This PR improves the feature by adding input validation.
        """
        
        # Call the describe method
        with patch.object(self.pr_description, 'publish_description') as mock_publish:
            result = self.pr_description.describe()
            
            # Verify that the description was published
            mock_publish.assert_called_once()
            
            # Verify the result
            self.assertIn("title: Improved Feature", result)
            self.assertIn("description: This PR improves the feature by adding input validation.", result)
            
    @patch('pr_agent.tools.pr_description.get_pr_diff')
    def test_describe_with_different_ai_models(self, mock_get_pr_diff):
        """
        Test that PRDescription can work with different AI models.
        """
        # Mock the PR diff
        mock_get_pr_diff.return_value = "test diff"
        
        # Test with different AI handlers
        for handler_name in ["LiteLLMAIHandler", "OpenAIAIHandler", "LangchainAIHandler"]:
            with patch(f'pr_agent.tools.pr_description.{handler_name}') as mock_handler:
                # Mock the handler instance
                mock_handler_instance = MagicMock()
                mock_handler.return_value = mock_handler_instance
                
                # Initialize PRDescription with the handler
                pr_description = PRDescription(
                    pr_url="https://github.com/test/repo/pull/1",
                    ai_handler=mock_handler
                )
                
                # Verify that the handler was used
                self.assertEqual(pr_description.ai_handler, mock_handler_instance)
                
    @patch('pr_agent.tools.pr_description.get_pr_diff')
    @patch('pr_agent.tools.pr_description.retry_with_fallback_models')
    @patch('pr_agent.tools.pr_description.get_user_labels')
    def test_generate_labels(self, mock_get_user_labels, mock_retry, mock_get_pr_diff):
        """
        Test that PRDescription can generate labels.
        """
        # Mock the PR diff
        mock_get_pr_diff.return_value = "test diff"
        
        # Mock the AI response
        mock_retry.return_value = """
        title: Improved Feature
        description: This PR improves the feature by adding input validation.
        labels: bug, enhancement
        """
        
        # Mock user labels
        mock_get_user_labels.return_value = ["bug", "enhancement", "documentation"]
        
        # Call the describe method
        with patch.object(self.pr_description, 'publish_description') as mock_publish:
            result = self.pr_description.describe()
            
            # Verify that the description was published
            mock_publish.assert_called_once()
            
            # Verify the result
            self.assertIn("labels: bug, enhancement", result)


if __name__ == '__main__':
    unittest.main()

