import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List

from pr_agent.log import get_logger


class CommentTracker:
    """
    Tracks comment history for PRs to implement different comment trigger strategies.
    
    This class provides functionality to:
    1. Track which PRs have received comments
    2. Determine if a PR should receive a comment based on the trigger strategy
    3. Persist comment history across application restarts
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the CommentTracker with a storage path.
        
        Args:
            storage_path: Path to the JSON file for storing comment history.
                          If None, uses a default path in the user's home directory.
        """
        if storage_path is None:
            home_dir = str(Path.home())
            self.storage_dir = os.path.join(home_dir, '.pr_agent')
            os.makedirs(self.storage_dir, exist_ok=True)
            self.storage_path = os.path.join(self.storage_dir, 'comment_history.json')
        else:
            self.storage_path = storage_path
            
        self.comment_history = self._load_history()
    
    def _load_history(self) -> Dict:
        """
        Load comment history from the storage file.
        
        Returns:
            Dict containing comment history data.
        """
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            get_logger().error(f"Failed to load comment history: {e}")
            return {}
    
    def _save_history(self) -> None:
        """Save comment history to the storage file."""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.comment_history, f, indent=2)
        except Exception as e:
            get_logger().error(f"Failed to save comment history: {e}")
    
    def record_comment(self, repo: str, pr_id: str, commit_sha: Optional[str] = None) -> None:
        """
        Record that a comment was posted to a PR.
        
        Args:
            repo: Repository identifier (e.g., 'owner/repo')
            pr_id: Pull request identifier
            commit_sha: SHA of the latest commit at the time of commenting
        """
        pr_key = f"{repo}/{pr_id}"
        
        if pr_key not in self.comment_history:
            self.comment_history[pr_key] = {
                "comments": []
            }
        
        self.comment_history[pr_key]["comments"].append({
            "timestamp": datetime.now().isoformat(),
            "commit_sha": commit_sha
        })
        
        self._save_history()
    
    def should_comment(self, repo: str, pr_id: str, trigger: str, latest_commit_sha: Optional[str] = None) -> bool:
        """
        Determine if a comment should be posted based on the trigger strategy.
        
        Args:
            repo: Repository identifier (e.g., 'owner/repo')
            pr_id: Pull request identifier
            trigger: Comment trigger strategy ('ALWAYS', 'ONCE_PER_PR', or 'AFTER_CHANGES')
            latest_commit_sha: SHA of the latest commit in the PR
            
        Returns:
            True if a comment should be posted, False otherwise
        """
        pr_key = f"{repo}/{pr_id}"
        
        # If trigger is ALWAYS, always post a comment
        if trigger == "ALWAYS":
            return True
        
        # If PR has never been commented on, always post a comment
        if pr_key not in self.comment_history or not self.comment_history[pr_key]["comments"]:
            return True
        
        # If trigger is ONCE_PER_PR and PR has been commented on, don't post a comment
        if trigger == "ONCE_PER_PR":
            return False
        
        # If trigger is AFTER_CHANGES, check if the latest commit is different from the last commented commit
        if trigger == "AFTER_CHANGES" and latest_commit_sha:
            last_comment = self.comment_history[pr_key]["comments"][-1]
            last_commit_sha = last_comment.get("commit_sha")
            
            # If we don't have the last commit SHA or it's different from the latest, post a comment
            return not last_commit_sha or last_commit_sha != latest_commit_sha
        
        # Default to posting a comment if we can't determine
        return True
    
    def get_comment_history(self, repo: str, pr_id: str) -> List[Dict]:
        """
        Get the comment history for a PR.
        
        Args:
            repo: Repository identifier (e.g., 'owner/repo')
            pr_id: Pull request identifier
            
        Returns:
            List of comment records for the PR
        """
        pr_key = f"{repo}/{pr_id}"
        
        if pr_key in self.comment_history:
            return self.comment_history[pr_key]["comments"]
        
        return []


# Create a singleton instance
comment_tracker = CommentTracker()

