import unittest
from unittest.mock import MagicMock, patch

from pr_agent.algo.token_handler import TokenEncoder, TokenHandler


class TestTokenHandler(unittest.TestCase):
    """
    Test cases for the TokenHandler class.
    """

    @patch('pr_agent.algo.token_handler.get_settings')
    def setUp(self, mock_get_settings):
        """
        Set up the test environment.
        """
        # Mock settings
        mock_settings = MagicMock()
        mock_settings.config.model = "gpt-4"
        mock_get_settings.return_value = mock_settings

        # Mock PR object
        self.mock_pr = MagicMock()
        self.mock_pr.title = "Test PR"

        # Mock variables
        self.vars = {
            "title": "Test PR",
            "branch": "feature-branch",
            "description": "Test PR description",
            "language": "Python",
            "diff": "test diff"
        }

        # Mock system and user prompts
        self.system = "You are a helpful assistant."
        self.user = "Review this PR: {{title}}, {{branch}}, {{description}}, {{language}}, {{diff}}"

        # Initialize TokenHandler
        self.token_handler = TokenHandler(
            pr=self.mock_pr,
            vars=self.vars,
            system=self.system,
            user=self.user
        )

    @patch('pr_agent.algo.token_handler.TokenEncoder.get_token_encoder')
    def test_initialization(self, mock_get_token_encoder):
        """
        Test that TokenHandler initializes correctly.
        """
        # Mock encoder
        mock_encoder = MagicMock()
        mock_encoder.encode.return_value = [1, 2, 3, 4, 5]  # 5 tokens
        mock_get_token_encoder.return_value = mock_encoder

        # Initialize TokenHandler
        token_handler = TokenHandler(
            pr=self.mock_pr,
            vars=self.vars,
            system=self.system,
            user=self.user
        )

        # Verify initialization
        self.assertEqual(token_handler.pr, self.mock_pr)
        self.assertEqual(token_handler.vars, self.vars)
        self.assertEqual(token_handler.system, self.system)
        self.assertEqual(token_handler.user, self.user)

    @patch('pr_agent.algo.token_handler.TokenEncoder.get_token_encoder')
    def test_get_system_user_tokens(self, mock_get_token_encoder):
        """
        Test the _get_system_user_tokens method.
        """
        # Mock encoder
        mock_encoder = MagicMock()
        mock_encoder.encode.side_effect = lambda x: [i for i in range(len(x))]  # 1 token per character
        mock_get_token_encoder.return_value = mock_encoder

        # Call _get_system_user_tokens
        system_tokens, user_tokens = self.token_handler._get_system_user_tokens()

        # Verify result
        self.assertEqual(system_tokens, len(self.system))
        self.assertEqual(user_tokens, len("Review this PR: Test PR, feature-branch, Test PR description, Python, test diff"))

    @patch('pr_agent.algo.token_handler.TokenEncoder.get_token_encoder')
    def test_get_completion_tokens(self, mock_get_token_encoder):
        """
        Test the get_completion_tokens method.
        """
        # Mock encoder
        mock_encoder = MagicMock()
        mock_encoder.encode.side_effect = lambda x: [i for i in range(len(x))]  # 1 token per character
        mock_get_token_encoder.return_value = mock_encoder

        # Call get_completion_tokens
        completion_tokens = self.token_handler.get_completion_tokens()

        # Verify result
        self.assertEqual(completion_tokens, 8000)  # Default completion tokens

    @patch('pr_agent.algo.token_handler.TokenEncoder.get_token_encoder')
    def test_get_available_tokens(self, mock_get_token_encoder):
        """
        Test the get_available_tokens method.
        """
        # Mock encoder
        mock_encoder = MagicMock()
        mock_encoder.encode.side_effect = lambda x: [i for i in range(len(x))]  # 1 token per character
        mock_get_token_encoder.return_value = mock_encoder

        # Set limit
        self.token_handler.limit = 4000

        # Call get_available_tokens
        available_tokens = self.token_handler.get_available_tokens()

        # Calculate expected available tokens
        system_tokens = len(self.system)
        user_tokens = len("Review this PR: Test PR, feature-branch, Test PR description, Python, test diff")
        expected_available_tokens = 4000 - system_tokens - user_tokens

        # Verify result
        self.assertEqual(available_tokens, expected_available_tokens)

    @patch('pr_agent.algo.token_handler.TokenEncoder.get_token_encoder')
    def test_get_token_count(self, mock_get_token_encoder):
        """
        Test the get_token_count method.
        """
        # Mock encoder
        mock_encoder = MagicMock()
        mock_encoder.encode.return_value = [1, 2, 3, 4, 5]  # 5 tokens
        mock_get_token_encoder.return_value = mock_encoder

        # Call get_token_count
        token_count = self.token_handler.get_token_count("test text")

        # Verify result
        self.assertEqual(token_count, 5)

    @patch('pr_agent.algo.token_handler.TokenEncoder.get_token_encoder')
    def test_update_var_keep_tokens_under_limit(self, mock_get_token_encoder):
        """
        Test the update_var_keep_tokens_under_limit method.
        """
        # Mock encoder
        mock_encoder = MagicMock()
        mock_encoder.encode.side_effect = lambda x: [i for i in range(min(len(x), 100))]  # Up to 100 tokens
        mock_get_token_encoder.return_value = mock_encoder

        # Set limit
        self.token_handler.limit = 200

        # Set prompt tokens
        self.token_handler.prompt_tokens = 150

        # Call update_var_keep_tokens_under_limit
        self.token_handler.update_var_keep_tokens_under_limit("diff", "a" * 100)

        # Verify result
        self.assertEqual(self.token_handler.vars["diff"], "a" * 50)  # Should be truncated to 50 tokens

    @patch('pr_agent.algo.token_handler.get_settings')
    def test_token_encoder_get_token_encoder(self, mock_get_settings):
        """
        Test the TokenEncoder.get_token_encoder method.
        """
        # Mock settings
        mock_settings = MagicMock()
        mock_settings.config.model = "gpt-4"
        mock_get_settings.return_value = mock_settings

        # Reset TokenEncoder singleton
        TokenEncoder._encoder_instance = None
        TokenEncoder._model = None

        # Call get_token_encoder with patch for encoding_for_model
        with patch('pr_agent.algo.token_handler.encoding_for_model') as mock_encoding_for_model:
            mock_encoder = MagicMock()
            mock_encoding_for_model.return_value = mock_encoder

            encoder = TokenEncoder.get_token_encoder()

            # Verify result
            self.assertEqual(encoder, mock_encoder)
            mock_encoding_for_model.assert_called_once_with("gpt-4")


if __name__ == '__main__':
    unittest.main()

-e

