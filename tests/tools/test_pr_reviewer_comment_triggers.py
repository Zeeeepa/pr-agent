import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from pr_agent.config_loader import get_settings
from pr_agent.tools.comment_tracker import CommentTracker
from pr_agent.tools.pr_reviewer import PRReviewer


class TestPRReviewerCommentTriggers(unittest.TestCase):
    def setUp(self):
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        
        # Create a patch for the comment_tracker module
        self.tracker_patch = patch('pr_agent.tools.pr_reviewer.comment_tracker')
        self.mock_tracker = self.tracker_patch.start()
        
        # Create a mock for the git provider
        self.mock_git_provider = MagicMock()
        self.mock_git_provider.get_repo_name.return_value = "test-repo"
        self.mock_git_provider.pr = MagicMock()
        self.mock_git_provider.pr.number = 123
        self.mock_git_provider.get_latest_commit_sha.return_value = "abc123"
        self.mock_git_provider.get_files.return_value = ["file1.py"]
        
        # Create a patch for get_git_provider_with_context
        self.git_provider_patch = patch('pr_agent.tools.pr_reviewer.get_git_provider_with_context')
        self.mock_get_git_provider = self.git_provider_patch.start()
        self.mock_get_git_provider.return_value = self.mock_git_provider
        
        # Create a patch for the settings
        self.settings_patch = patch('pr_agent.tools.pr_reviewer.get_settings')
        self.mock_settings = self.settings_patch.start()
        self.mock_settings.return_value.pr_reviewer = {
            'comment_trigger': 'ALWAYS',
            'persistent_comment': True,
            'final_update_message': True,
            'require_score_review': False,
            'require_tests_review': True,
            'require_estimate_effort_to_review': True,
            'require_can_be_split_review': False,
            'require_security_review': True,
            'require_ticket_analysis_review': True,
        }
        self.mock_settings.return_value.config = {
            'publish_output': True,
        }
        self.mock_settings.return_value.get.return_value = False
        
    def tearDown(self):
        # Clean up the temporary file
        os.unlink(self.temp_file.name)
        
        # Stop the patches
        self.tracker_patch.stop()
        self.git_provider_patch.stop()
        self.settings_patch.stop()
        
    @patch('pr_agent.tools.pr_reviewer.retry_with_fallback_models')
    async def test_always_trigger(self, mock_retry):
        # Configure the mock tracker
        self.mock_tracker.should_comment.return_value = True
        
        # Create a PR reviewer
        reviewer = PRReviewer("https://github.com/test-repo/pull/123")
        reviewer.prediction = "test prediction"
        reviewer._prepare_pr_review = MagicMock(return_value="test review")
        
        # Run the reviewer
        await reviewer.run()
        
        # Check that should_comment was called with the correct arguments
        self.mock_tracker.should_comment.assert_called_once_with(
            repo="test-repo",
            pr_id="123",
            trigger="ALWAYS",
            latest_commit_sha="abc123"
        )
        
        # Check that the comment was published
        self.mock_git_provider.publish_persistent_comment.assert_called_once()
        
        # Check that record_comment was called
        self.mock_tracker.record_comment.assert_called_once_with(
            repo="test-repo",
            pr_id="123",
            commit_sha="abc123"
        )
        
    @patch('pr_agent.tools.pr_reviewer.retry_with_fallback_models')
    async def test_skip_comment(self, mock_retry):
        # Configure the mock tracker to skip the comment
        self.mock_tracker.should_comment.return_value = False
        
        # Create a PR reviewer
        reviewer = PRReviewer("https://github.com/test-repo/pull/123")
        
        # Run the reviewer
        await reviewer.run()
        
        # Check that should_comment was called with the correct arguments
        self.mock_tracker.should_comment.assert_called_once_with(
            repo="test-repo",
            pr_id="123",
            trigger="ALWAYS",
            latest_commit_sha="abc123"
        )
        
        # Check that the comment was not published
        self.mock_git_provider.publish_persistent_comment.assert_not_called()
        self.mock_git_provider.publish_comment.assert_not_called()
        
        # Check that record_comment was not called
        self.mock_tracker.record_comment.assert_not_called()
        
    @patch('pr_agent.tools.pr_reviewer.retry_with_fallback_models')
    async def test_once_per_pr_trigger(self, mock_retry):
        # Configure the settings
        self.mock_settings.return_value.pr_reviewer['comment_trigger'] = 'ONCE_PER_PR'
        
        # Configure the mock tracker
        self.mock_tracker.should_comment.return_value = True
        
        # Create a PR reviewer
        reviewer = PRReviewer("https://github.com/test-repo/pull/123")
        reviewer.prediction = "test prediction"
        reviewer._prepare_pr_review = MagicMock(return_value="test review")
        
        # Run the reviewer
        await reviewer.run()
        
        # Check that should_comment was called with the correct arguments
        self.mock_tracker.should_comment.assert_called_once_with(
            repo="test-repo",
            pr_id="123",
            trigger="ONCE_PER_PR",
            latest_commit_sha="abc123"
        )
        
        # Check that the comment was published
        self.mock_git_provider.publish_persistent_comment.assert_called_once()
        
        # Check that record_comment was called
        self.mock_tracker.record_comment.assert_called_once_with(
            repo="test-repo",
            pr_id="123",
            commit_sha="abc123"
        )
        
    @patch('pr_agent.tools.pr_reviewer.retry_with_fallback_models')
    async def test_after_changes_trigger(self, mock_retry):
        # Configure the settings
        self.mock_settings.return_value.pr_reviewer['comment_trigger'] = 'AFTER_CHANGES'
        
        # Configure the mock tracker
        self.mock_tracker.should_comment.return_value = True
        
        # Create a PR reviewer
        reviewer = PRReviewer("https://github.com/test-repo/pull/123")
        reviewer.prediction = "test prediction"
        reviewer._prepare_pr_review = MagicMock(return_value="test review")
        
        # Run the reviewer
        await reviewer.run()
        
        # Check that should_comment was called with the correct arguments
        self.mock_tracker.should_comment.assert_called_once_with(
            repo="test-repo",
            pr_id="123",
            trigger="AFTER_CHANGES",
            latest_commit_sha="abc123"
        )
        
        # Check that the comment was published
        self.mock_git_provider.publish_persistent_comment.assert_called_once()
        
        # Check that record_comment was called
        self.mock_tracker.record_comment.assert_called_once_with(
            repo="test-repo",
            pr_id="123",
            commit_sha="abc123"
        )


if __name__ == "__main__":
    unittest.main()

