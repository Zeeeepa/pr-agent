import unittest
from unittest.mock import patch, MagicMock

from pr_agent.tools.pr_reviewer import PRReviewer
from pr_agent.algo.ai_handlers.base_ai_handler import BaseAiHandler


class TestPRReviewer(unittest.TestCase):
    """
    Test cases for the PRReviewer class.
    """

    @patch('pr_agent.tools.pr_reviewer.get_git_provider_with_context')
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
        self.mock_git_provider.get_commit_messages.return_value = "Test commit message"
        
        # Mock AI handler
        self.mock_ai_handler = MagicMock(spec=BaseAiHandler)
        self.mock_ai_handler_class = MagicMock(return_value=self.mock_ai_handler)
        
        # Initialize PRReviewer
        self.pr_reviewer = PRReviewer(
            pr_url="https://github.com/test/repo/pull/1",
            ai_handler=self.mock_ai_handler_class
        )
        
    def test_initialization(self):
        """
        Test that PRReviewer initializes correctly.
        """
        self.assertEqual(self.pr_reviewer.git_provider, self.mock_git_provider)
        self.assertFalse(self.pr_reviewer.is_answer)
        self.assertFalse(self.pr_reviewer.is_auto)
        
    @patch('pr_agent.tools.pr_reviewer.get_pr_diff')
    @patch('pr_agent.tools.pr_reviewer.retry_with_fallback_models')
    def test_review_standard_mode(self, mock_retry, mock_get_pr_diff):
        """
        Test the review method in standard mode.
        """
        # Mock the PR diff
        mock_get_pr_diff.return_value = "test diff"
        
        # Mock the AI response
        mock_retry.return_value = "AI review response"
        
        # Call the review method
        with patch.object(self.pr_reviewer, 'publish_review') as mock_publish:
            result = self.pr_reviewer.review()
            
            # Verify that the review was published
            mock_publish.assert_called_once()
            
            # Verify the result
            self.assertEqual(result, "AI review response")
            
    @patch('pr_agent.tools.pr_reviewer.get_pr_diff')
    @patch('pr_agent.tools.pr_reviewer.retry_with_fallback_models')
    def test_review_answer_mode(self, mock_retry, mock_get_pr_diff):
        """
        Test the review method in answer mode.
        """
        # Set answer mode
        self.pr_reviewer.is_answer = True
        
        # Mock the PR diff
        mock_get_pr_diff.return_value = "test diff"
        
        # Mock the AI response
        mock_retry.return_value = "AI answer response"
        
        # Call the review method
        with patch.object(self.pr_reviewer, 'publish_review') as mock_publish:
            result = self.pr_reviewer.review()
            
            # Verify that the review was published
            mock_publish.assert_called_once()
            
            # Verify the result
            self.assertEqual(result, "AI answer response")
            
    @patch('pr_agent.tools.pr_reviewer.get_pr_diff')
    @patch('pr_agent.tools.pr_reviewer.retry_with_fallback_models')
    def test_review_auto_mode(self, mock_retry, mock_get_pr_diff):
        """
        Test the review method in auto mode.
        """
        # Set auto mode
        self.pr_reviewer.is_auto = True
        
        # Mock the PR diff
        mock_get_pr_diff.return_value = "test diff"
        
        # Mock the AI response
        mock_retry.return_value = "AI auto response"
        
        # Call the review method
        with patch.object(self.pr_reviewer, 'publish_review') as mock_publish:
            result = self.pr_reviewer.review()
            
            # Verify that the review was published
            mock_publish.assert_called_once()
            
            # Verify the result
            self.assertEqual(result, "AI auto response")
            
    @patch('pr_agent.tools.pr_reviewer.get_pr_diff')
    def test_review_with_different_ai_models(self, mock_get_pr_diff):
        """
        Test that PRReviewer can work with different AI models.
        """
        # Mock the PR diff
        mock_get_pr_diff.return_value = "test diff"
        
        # Test with different AI handlers
        for handler_name in ["LiteLLMAIHandler", "OpenAIAIHandler", "LangchainAIHandler"]:
            with patch(f'pr_agent.tools.pr_reviewer.{handler_name}') as mock_handler:
                # Mock the handler instance
                mock_handler_instance = MagicMock()
                mock_handler.return_value = mock_handler_instance
                
                # Initialize PRReviewer with the handler
                pr_reviewer = PRReviewer(
                    pr_url="https://github.com/test/repo/pull/1",
                    ai_handler=mock_handler
                )
                
                # Verify that the handler was used
                self.assertEqual(pr_reviewer.ai_handler, mock_handler_instance)


if __name__ == '__main__':
    unittest.main()

