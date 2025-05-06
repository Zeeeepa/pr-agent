import unittest
from unittest.mock import patch, MagicMock

from pr_agent.tools.pr_code_suggestions import PRCodeSuggestions
from pr_agent.algo.ai_handlers.base_ai_handler import BaseAiHandler


class TestPRCodeSuggestions(unittest.TestCase):
    """
    Test cases for the PRCodeSuggestions class.
    """

    @patch('pr_agent.tools.pr_code_suggestions.get_git_provider_with_context')
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
        
        # Mock AI handler
        self.mock_ai_handler = MagicMock(spec=BaseAiHandler)
        self.mock_ai_handler_class = MagicMock(return_value=self.mock_ai_handler)
        
        # Initialize PRCodeSuggestions
        self.pr_code_suggestions = PRCodeSuggestions(
            pr_url="https://github.com/test/repo/pull/1",
            ai_handler=self.mock_ai_handler_class
        )
        
    def test_initialization(self):
        """
        Test that PRCodeSuggestions initializes correctly.
        """
        self.assertEqual(self.pr_code_suggestions.git_provider, self.mock_git_provider)
        self.assertEqual(self.pr_code_suggestions.main_language, "Python")
        
    @patch('pr_agent.tools.pr_code_suggestions.get_pr_diff')
    @patch('pr_agent.tools.pr_code_suggestions.retry_with_fallback_models')
    def test_improve_standard_mode(self, mock_retry, mock_get_pr_diff):
        """
        Test the improve method in standard mode.
        """
        # Mock the PR diff
        mock_get_pr_diff.return_value = "test diff"
        
        # Mock the AI response
        mock_retry.return_value = "AI code suggestions response"
        
        # Call the improve method
        with patch.object(self.pr_code_suggestions, 'publish_suggestions') as mock_publish:
            result = self.pr_code_suggestions.improve()
            
            # Verify that the suggestions were published
            mock_publish.assert_called_once()
            
            # Verify the result
            self.assertEqual(result, "AI code suggestions response")
            
    @patch('pr_agent.tools.pr_code_suggestions.get_pr_diff')
    @patch('pr_agent.tools.pr_code_suggestions.retry_with_fallback_models')
    def test_improve_extended_mode(self, mock_retry, mock_get_pr_diff):
        """
        Test the improve method in extended mode.
        """
        # Set extended mode
        self.pr_code_suggestions.extended = True
        
        # Mock the PR diff
        mock_get_pr_diff.return_value = "test diff"
        
        # Mock the AI response
        mock_retry.return_value = "AI extended code suggestions response"
        
        # Call the improve method
        with patch.object(self.pr_code_suggestions, 'publish_suggestions') as mock_publish:
            result = self.pr_code_suggestions.improve()
            
            # Verify that the suggestions were published
            mock_publish.assert_called_once()
            
            # Verify the result
            self.assertEqual(result, "AI extended code suggestions response")
            
    @patch('pr_agent.tools.pr_code_suggestions.get_pr_multi_diffs')
    @patch('pr_agent.tools.pr_code_suggestions.retry_with_fallback_models')
    def test_improve_with_multiple_diffs(self, mock_retry, mock_get_pr_multi_diffs):
        """
        Test the improve method with multiple diffs.
        """
        # Set extended mode
        self.pr_code_suggestions.extended = True
        
        # Mock multiple PR diffs
        mock_get_pr_multi_diffs.return_value = ["diff1", "diff2"]
        
        # Mock the AI responses
        mock_retry.side_effect = ["AI response 1", "AI response 2"]
        
        # Call the improve method
        with patch.object(self.pr_code_suggestions, 'publish_suggestions') as mock_publish:
            result = self.pr_code_suggestions.improve()
            
            # Verify that the suggestions were published
            mock_publish.assert_called_once()
            
            # Verify the result (should be the last response)
            self.assertEqual(result, "AI response 2")
            
    @patch('pr_agent.tools.pr_code_suggestions.get_pr_diff')
    def test_improve_with_different_ai_models(self, mock_get_pr_diff):
        """
        Test that PRCodeSuggestions can work with different AI models.
        """
        # Mock the PR diff
        mock_get_pr_diff.return_value = "test diff"
        
        # Test with different AI handlers
        for handler_name in ["LiteLLMAIHandler", "OpenAIAIHandler", "LangchainAIHandler"]:
            with patch(f'pr_agent.tools.pr_code_suggestions.{handler_name}') as mock_handler:
                # Mock the handler instance
                mock_handler_instance = MagicMock()
                mock_handler.return_value = mock_handler_instance
                
                # Initialize PRCodeSuggestions with the handler
                pr_code_suggestions = PRCodeSuggestions(
                    pr_url="https://github.com/test/repo/pull/1",
                    ai_handler=mock_handler
                )
                
                # Verify that the handler was used
                self.assertEqual(pr_code_suggestions.ai_handler, mock_handler_instance)
                
    @patch('pr_agent.tools.pr_code_suggestions.get_pr_diff')
    @patch('pr_agent.tools.pr_code_suggestions.retry_with_fallback_models')
    def test_suggestion_formatting(self, mock_retry, mock_get_pr_diff):
        """
        Test that code suggestions are properly formatted.
        """
        # Mock the PR diff
        mock_get_pr_diff.return_value = "test diff"
        
        # Mock the AI response with a code suggestion
        mock_retry.return_value = """
        Here are some code suggestions:
        
        ```suggestion
        def improved_function():
            # This is an improved function
            return "improved"
        ```
        
        This suggestion improves the function.
        """
        
        # Call the improve method
        with patch.object(self.pr_code_suggestions, 'publish_suggestions') as mock_publish:
            result = self.pr_code_suggestions.improve()
            
            # Verify that the suggestions were published
            mock_publish.assert_called_once()
            
            # Verify the result contains the code suggestion
            self.assertIn("```suggestion", result)
            self.assertIn("def improved_function():", result)


if __name__ == '__main__':
    unittest.main()

