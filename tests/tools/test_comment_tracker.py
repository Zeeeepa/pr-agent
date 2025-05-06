import json
import os
import tempfile
import unittest
from datetime import datetime

from pr_agent.tools.comment_tracker import CommentTracker


class TestCommentTracker(unittest.TestCase):
    def setUp(self):
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        self.tracker = CommentTracker(self.temp_file.name)
        
    def tearDown(self):
        # Clean up the temporary file
        os.unlink(self.temp_file.name)
        
    def test_record_comment(self):
        # Test recording a comment
        self.tracker.record_comment("test-repo", "123", "abc123")
        
        # Check that the comment was recorded
        self.assertIn("test-repo/123", self.tracker.comment_history)
        self.assertEqual(len(self.tracker.comment_history["test-repo/123"]["comments"]), 1)
        self.assertEqual(self.tracker.comment_history["test-repo/123"]["comments"][0]["commit_sha"], "abc123")
        
    def test_should_comment_always(self):
        # Test ALWAYS trigger
        # Should always return True
        self.tracker.record_comment("test-repo", "123", "abc123")
        
        # Even with existing comments, should return True
        self.assertTrue(self.tracker.should_comment("test-repo", "123", "ALWAYS", "abc123"))
        self.assertTrue(self.tracker.should_comment("test-repo", "123", "ALWAYS", "def456"))
        
    def test_should_comment_once_per_pr(self):
        # Test ONCE_PER_PR trigger
        # First comment should be allowed
        self.assertTrue(self.tracker.should_comment("test-repo", "123", "ONCE_PER_PR", "abc123"))
        
        # Record the comment
        self.tracker.record_comment("test-repo", "123", "abc123")
        
        # Subsequent comments should not be allowed
        self.assertFalse(self.tracker.should_comment("test-repo", "123", "ONCE_PER_PR", "abc123"))
        self.assertFalse(self.tracker.should_comment("test-repo", "123", "ONCE_PER_PR", "def456"))
        
    def test_should_comment_after_changes(self):
        # Test AFTER_CHANGES trigger
        # First comment should be allowed
        self.assertTrue(self.tracker.should_comment("test-repo", "123", "AFTER_CHANGES", "abc123"))
        
        # Record the comment
        self.tracker.record_comment("test-repo", "123", "abc123")
        
        # Same commit SHA should not allow a new comment
        self.assertFalse(self.tracker.should_comment("test-repo", "123", "AFTER_CHANGES", "abc123"))
        
        # Different commit SHA should allow a new comment
        self.assertTrue(self.tracker.should_comment("test-repo", "123", "AFTER_CHANGES", "def456"))
        
    def test_get_comment_history(self):
        # Test getting comment history
        self.tracker.record_comment("test-repo", "123", "abc123")
        self.tracker.record_comment("test-repo", "123", "def456")
        
        history = self.tracker.get_comment_history("test-repo", "123")
        
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["commit_sha"], "abc123")
        self.assertEqual(history[1]["commit_sha"], "def456")
        
    def test_persistence(self):
        # Test that comment history is persisted to disk
        self.tracker.record_comment("test-repo", "123", "abc123")
        
        # Create a new tracker with the same storage path
        new_tracker = CommentTracker(self.temp_file.name)
        
        # Check that the comment history was loaded
        self.assertIn("test-repo/123", new_tracker.comment_history)
        self.assertEqual(len(new_tracker.comment_history["test-repo/123"]["comments"]), 1)
        self.assertEqual(new_tracker.comment_history["test-repo/123"]["comments"][0]["commit_sha"], "abc123")
        
    def test_different_repos_and_prs(self):
        # Test that different repos and PRs are tracked separately
        self.tracker.record_comment("repo1", "123", "abc123")
        self.tracker.record_comment("repo2", "123", "def456")
        self.tracker.record_comment("repo1", "456", "ghi789")
        
        # Check that all comments were recorded correctly
        self.assertIn("repo1/123", self.tracker.comment_history)
        self.assertIn("repo2/123", self.tracker.comment_history)
        self.assertIn("repo1/456", self.tracker.comment_history)
        
        # Check that the correct commit SHAs were recorded
        self.assertEqual(self.tracker.comment_history["repo1/123"]["comments"][0]["commit_sha"], "abc123")
        self.assertEqual(self.tracker.comment_history["repo2/123"]["comments"][0]["commit_sha"], "def456")
        self.assertEqual(self.tracker.comment_history["repo1/456"]["comments"][0]["commit_sha"], "ghi789")


if __name__ == "__main__":
    unittest.main()

