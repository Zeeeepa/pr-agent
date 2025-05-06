import unittest
from unittest.mock import MagicMock, patch

from pr_agent.algo.ai_handlers.base_ai_handler import BaseAiHandler
from pr_agent.tools.pr_update_changelog import PRUpdateChangelog


class TestPRUpdateChangelog(unittest.TestCase):
    """
    Test cases for the PRUpdateChangelog class.
    """

    @patch('pr_agent.tools.pr_update_changelog.get_git_provider')
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

        # Mock changelog file
        self.mock_git_provider.get_file_content.return_value = "# Changelog\n\n## [Unreleased]\n\n### Added\n\n- Feature A\n\n### Fixed\n\n- Bug X\n"

        # Mock AI handler
        self.mock_ai_handler = MagicMock(spec=BaseAiHandler)
        self.mock_ai_handler_class = MagicMock(return_value=self.mock_ai_handler)

        # Initialize PRUpdateChangelog
        with patch.object(PRUpdateChangelog, '_get_changelog_file'):
            self.pr_update_changelog = PRUpdateChangelog(
                pr_url="https://github.com/test/repo/pull/1",
                ai_handler=self.mock_ai_handler_class
            )
            self.pr_update_changelog.changelog_file_str = "# Changelog\n\n## [Unreleased]\n\n### Added\n\n- Feature A\n\n### Fixed\n\n- Bug X\n"

    def test_initialization(self):
        """
        Test that PRUpdateChangelog initializes correctly.
        """
        self.assertEqual(self.pr_update_changelog.git_provider, self.mock_git_provider)
        self.assertEqual(self.pr_update_changelog.main_language, "Python")
        self.assertEqual(self.pr_update_changelog.changelog_file_str, "# Changelog\n\n## [Unreleased]\n\n### Added\n\n- Feature A\n\n### Fixed\n\n- Bug X\n")

    @patch('pr_agent.tools.pr_update_changelog.get_pr_diff')
    @patch('pr_agent.tools.pr_update_changelog.retry_with_fallback_models')
    def test_update_changelog(self, mock_retry, mock_get_pr_diff):
        """
        Test the update_changelog method.
        """
        # Mock the PR diff
        mock_get_pr_diff.return_value = "test diff"

        # Mock the AI response
        mock_retry.return_value = """
        # Changelog

        ## [Unreleased]

        ### Added

        - Feature A
        - New Feature B from PR

        ### Fixed

        - Bug X
        """

        # Call the update_changelog method
        with patch.object(self.pr_update_changelog, 'publish_changelog') as mock_publish:
            result = self.pr_update_changelog.update_changelog()

            # Verify that the changelog was published
            mock_publish.assert_called_once()

            # Verify the result
            self.assertIn("New Feature B from PR", result)

    @patch('pr_agent.tools.pr_update_changelog.get_pr_diff')
    def test_update_changelog_with_different_ai_models(self, mock_get_pr_diff):
        """
        Test that PRUpdateChangelog can work with different AI models.
        """
        # Mock the PR diff
        mock_get_pr_diff.return_value = "test diff"

        # Test with different AI handlers
        for handler_name in ["LiteLLMAIHandler", "OpenAIAIHandler", "LangchainAIHandler"]:
            with patch(f'pr_agent.tools.pr_update_changelog.{handler_name}') as mock_handler:
                # Mock the handler instance
                mock_handler_instance = MagicMock()
                mock_handler.return_value = mock_handler_instance

                # Initialize PRUpdateChangelog with the handler
                with patch.object(PRUpdateChangelog, '_get_changelog_file'):
                    pr_update_changelog = PRUpdateChangelog(
                        pr_url="https://github.com/test/repo/pull/1",
                        ai_handler=mock_handler
                    )
                    pr_update_changelog.changelog_file_str = "# Changelog\n\n## [Unreleased]\n\n### Added\n\n- Feature A\n\n### Fixed\n\n- Bug X\n"

                # Verify that the handler was used
                self.assertEqual(pr_update_changelog.ai_handler, mock_handler_instance)

    @patch('pr_agent.tools.pr_update_changelog.get_pr_diff')
    @patch('pr_agent.tools.pr_update_changelog.retry_with_fallback_models')
    def test_changelog_formatting(self, mock_retry, mock_get_pr_diff):
        """
        Test that the changelog is properly formatted.
        """
        # Mock the PR diff
        mock_get_pr_diff.return_value = "test diff"

        # Mock the AI response with different changelog sections
        mock_retry.return_value = """
        # Changelog

        ## [Unreleased]

        ### Added

        - Feature A
        - New Feature B from PR

        ### Fixed

        - Bug X
        - Fixed issue Y from PR

        ### Changed

        - Updated dependency Z
        """

        # Call the update_changelog method
        with patch.object(self.pr_update_changelog, 'publish_changelog') as mock_publish:
            result = self.pr_update_changelog.update_changelog()

            # Verify that the changelog was published
            mock_publish.assert_called_once()

            # Verify the result contains all sections
            self.assertIn("### Added", result)
            self.assertIn("New Feature B from PR", result)
            self.assertIn("### Fixed", result)
            self.assertIn("Fixed issue Y from PR", result)
            self.assertIn("### Changed", result)
            self.assertIn("Updated dependency Z", result)


if __name__ == '__main__':
    unittest.main()

-e

