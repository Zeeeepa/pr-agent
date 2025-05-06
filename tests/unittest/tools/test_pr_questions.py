import unittest
from unittest.mock import MagicMock, patch

from pr_agent.algo.ai_handlers.base_ai_handler import BaseAiHandler
from pr_agent.tools.pr_questions import PRQuestions


class TestPRQuestions(unittest.TestCase):
    """
    Test cases for the PRQuestions class.
    """

    @patch('pr_agent.tools.pr_questions.get_git_provider')
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
        self.mock_git_provider.get_pr_description.return_value = "Test PR description"
        self.mock_git_provider.get_languages.return_value = {"Python": 100}
        self.mock_git_provider.get_files.return_value = ["test.py"]
        self.mock_git_provider.get_commit_messages.return_value = "Test commit message"

        # Mock AI handler
        self.mock_ai_handler = MagicMock(spec=BaseAiHandler)
        self.mock_ai_handler_class = MagicMock(return_value=self.mock_ai_handler)

        # Initialize PRQuestions with a test question
        self.pr_questions = PRQuestions(
            pr_url="https://github.com/test/repo/pull/1",
            args=["What", "is", "this", "PR", "doing?"],
            ai_handler=self.mock_ai_handler_class
        )

    def test_initialization(self):
        """
        Test that PRQuestions initializes correctly.
        """
        self.assertEqual(self.pr_questions.git_provider, self.mock_git_provider)
        self.assertEqual(self.pr_questions.question_str, "What is this PR doing?")
        self.assertEqual(self.pr_questions.vars["title"], "Test PR")
        self.assertEqual(self.pr_questions.vars["branch"], "feature-branch")
        self.assertEqual(self.pr_questions.vars["description"], "Test PR description")
        self.assertEqual(self.pr_questions.vars["questions"], "What is this PR doing?")

    @patch('pr_agent.tools.pr_questions.get_pr_diff')
    @patch('pr_agent.tools.pr_questions.retry_with_fallback_models')
    def test_answer_question(self, mock_retry, mock_get_pr_diff):
        """
        Test the answer method.
        """
        # Mock the PR diff
        mock_get_pr_diff.return_value = "test diff"

        # Mock the AI response
        mock_retry.return_value = "This PR is implementing a new feature."

        # Call the answer method
        with patch.object(self.pr_questions, 'publish_answer') as mock_publish:
            result = self.pr_questions.answer()

            # Verify that the answer was published
            mock_publish.assert_called_once()

            # Verify the result
            self.assertEqual(result, "This PR is implementing a new feature.")

    @patch('pr_agent.tools.pr_questions.get_pr_diff')
    def test_answer_with_different_ai_models(self, mock_get_pr_diff):
        """
        Test that PRQuestions can work with different AI models.
        """
        # Mock the PR diff
        mock_get_pr_diff.return_value = "test diff"

        # Test with different AI handlers
        for handler_name in ["LiteLLMAIHandler", "OpenAIAIHandler", "LangchainAIHandler"]:
            with patch(f'pr_agent.tools.pr_questions.{handler_name}') as mock_handler:
                # Mock the handler instance
                mock_handler_instance = MagicMock()
                mock_handler.return_value = mock_handler_instance

                # Initialize PRQuestions with the handler
                pr_questions = PRQuestions(
                    pr_url="https://github.com/test/repo/pull/1",
                    args=["What", "is", "this", "PR", "doing?"],
                    ai_handler=mock_handler
                )

                # Verify that the handler was used
                self.assertEqual(pr_questions.ai_handler, mock_handler_instance)

    def test_parse_args(self):
        """
        Test the parse_args method.
        """
        # Test with args
        args = ["What", "is", "this", "PR", "doing?"]
        result = self.pr_questions.parse_args(args)
        self.assertEqual(result, "What is this PR doing?")

        # Test without args
        result = self.pr_questions.parse_args(None)
        self.assertEqual(result, "")

        # Test with empty args
        result = self.pr_questions.parse_args([])
        self.assertEqual(result, "")


if __name__ == '__main__':
    unittest.main()

-e

