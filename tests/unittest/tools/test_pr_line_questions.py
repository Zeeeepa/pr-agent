import unittest
from unittest.mock import patch, MagicMock

from pr_agent.tools.pr_line_questions import PR_LineQuestions
from pr_agent.algo.ai_handlers.base_ai_handler import BaseAiHandler


class TestPRLineQuestions(unittest.TestCase):
    """
    Test cases for the PR_LineQuestions class.
    """

    @patch('pr_agent.tools.pr_line_questions.get_git_provider')
    def setUp(self, mock_get_git_provider):
        """
        Set up the test environment.
        """
        self.mock_git_provider_class = MagicMock()
        self.mock_git_provider = MagicMock()
        self.mock_git_provider_class.return_value = self.mock_git_provider
        mock_get_git_provider.return_value = self.mock_git_provider_class
        
        # Mock PR object
        self.mock_git_provider.pr = MagicMock()
        self.mock_git_provider.pr.title = "Test PR"
        self.mock_git_provider.get_pr_branch.return_value = "feature-branch"
        self.mock_git_provider.get_languages.return_value = {"Python": 100}
        self.mock_git_provider.get_files.return_value = ["test.py"]
        
        # Mock AI handler
        self.mock_ai_handler = MagicMock(spec=BaseAiHandler)
        self.mock_ai_handler_class = MagicMock(return_value=self.mock_ai_handler)
        
        # Initialize PR_LineQuestions with a test question
        self.pr_line_questions = PR_LineQuestions(
            pr_url="https://github.com/test/repo/pull/1",
            args=["--file", "test.py", "--line", "10", "Why", "is", "this", "line", "needed?"],
            ai_handler=self.mock_ai_handler_class
        )
        
    def test_initialization(self):
        """
        Test that PR_LineQuestions initializes correctly.
        """
        self.assertEqual(self.pr_line_questions.git_provider, self.mock_git_provider)
        self.assertEqual(self.pr_line_questions.question_str, "Why is this line needed?")
        self.assertEqual(self.pr_line_questions.vars["title"], "Test PR")
        self.assertEqual(self.pr_line_questions.vars["branch"], "feature-branch")
        
    @patch('pr_agent.tools.pr_line_questions.get_pr_diff')
    @patch('pr_agent.tools.pr_line_questions.extract_hunk_lines_from_patch')
    @patch('pr_agent.tools.pr_line_questions.retry_with_fallback_models')
    def test_answer_line_question(self, mock_retry, mock_extract_hunk, mock_get_pr_diff):
        """
        Test the answer method for line-specific questions.
        """
        # Mock the PR diff
        mock_get_pr_diff.return_value = "test diff"
        
        # Mock the hunk extraction
        mock_extract_hunk.return_value = ("full hunk context", "selected line")
        
        # Mock the AI response
        mock_retry.return_value = "This line is needed for input validation."
        
        # Call the answer method
        with patch.object(self.pr_line_questions, 'publish_answer') as mock_publish:
            result = self.pr_line_questions.answer()
            
            # Verify that the answer was published
            mock_publish.assert_called_once()
            
            # Verify the result
            self.assertEqual(result, "This line is needed for input validation.")
            
    @patch('pr_agent.tools.pr_line_questions.get_pr_diff')
    @patch('pr_agent.tools.pr_line_questions.extract_hunk_lines_from_patch')
    def test_answer_with_different_ai_models(self, mock_extract_hunk, mock_get_pr_diff):
        """
        Test that PR_LineQuestions can work with different AI models.
        """
        # Mock the PR diff
        mock_get_pr_diff.return_value = "test diff"
        
        # Mock the hunk extraction
        mock_extract_hunk.return_value = ("full hunk context", "selected line")
        
        # Test with different AI handlers
        for handler_name in ["LiteLLMAIHandler", "OpenAIAIHandler", "LangchainAIHandler"]:
            with patch(f'pr_agent.tools.pr_line_questions.{handler_name}') as mock_handler:
                # Mock the handler instance
                mock_handler_instance = MagicMock()
                mock_handler.return_value = mock_handler_instance
                
                # Initialize PR_LineQuestions with the handler
                pr_line_questions = PR_LineQuestions(
                    pr_url="https://github.com/test/repo/pull/1",
                    args=["--file", "test.py", "--line", "10", "Why", "is", "this", "line", "needed?"],
                    ai_handler=mock_handler
                )
                
                # Verify that the handler was used
                self.assertEqual(pr_line_questions.ai_handler, mock_handler_instance)
                
    def test_parse_args(self):
        """
        Test the parse_args method.
        """
        # Test with file and line args
        args = ["--file", "test.py", "--line", "10", "Why", "is", "this", "line", "needed?"]
        result = self.pr_line_questions.parse_args(args)
        self.assertEqual(result, "Why is this line needed?")
        self.assertEqual(self.pr_line_questions.file, "test.py")
        self.assertEqual(self.pr_line_questions.line, 10)
        
        # Test without question
        args = ["--file", "test.py", "--line", "10"]
        pr_line_questions = PR_LineQuestions(
            pr_url="https://github.com/test/repo/pull/1",
            args=args,
            ai_handler=self.mock_ai_handler_class
        )
        self.assertEqual(pr_line_questions.question_str, "")
        self.assertEqual(pr_line_questions.file, "test.py")
        self.assertEqual(pr_line_questions.line, 10)


if __name__ == '__main__':
    unittest.main()

