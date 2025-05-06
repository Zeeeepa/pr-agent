"""
Analysis Context for PR Static Analysis.

This module provides the AnalysisContext class for managing the state and data for the PR analysis process.
"""

from typing import Any, Dict, List, Optional

from pr_agent.algo.types import FilePatchInfo
from pr_agent.log import get_logger


class AnalysisContext:
    """
    Manages the state and data for the analysis process.

    Provides access to PR data, codebase, and analysis results.
    Integrates with existing components.
    """

    def __init__(self, pr_data: Dict[str, Any]):
        """
        Initialize the analysis context with PR data.

        Args:
            pr_data: Dictionary containing PR data from GitHub
        """
        self.pr_data = pr_data
        self.base_codebase = None
        self.head_codebase = None
        self.results = {}
        self.changed_files: List[FilePatchInfo] = []
        self.logger = get_logger()

    def load_codebases(self):
        """
        Load base and head codebases from the PR data.

        This method initializes the base and head codebase objects for analysis.
        """
        self.logger.info("Loading codebases for analysis")
        # Load base and head codebases
        self.base_codebase = self._load_codebase(self.pr_data['base_commit'])
        self.head_codebase = self._load_codebase(self.pr_data['head_commit'])

    def _load_codebase(self, commit_sha: str) -> Any:
        """
        Load a codebase from a specific commit.

        Args:
            commit_sha: The commit SHA to load

        Returns:
            The loaded codebase object
        """
        self.logger.info(f"Loading codebase for commit: {commit_sha}")
        # This would be implemented to load the codebase from the commit
        # For now, return a placeholder
        return {
            'commit_sha': commit_sha,
            'files': {}
        }

    def get_changed_files(self) -> List[FilePatchInfo]:
        """
        Get files changed in the PR.

        Returns:
            List of FilePatchInfo objects representing changed files
        """
        if not self.changed_files and 'changed_files' in self.pr_data:
            self.changed_files = self.pr_data['changed_files']
        return self.changed_files

    def set_changed_files(self, changed_files: List[FilePatchInfo]):
        """
        Set the list of changed files.

        Args:
            changed_files: List of FilePatchInfo objects representing changed files
        """
        self.changed_files = changed_files

    def add_result(self, rule_id: str, result: Any):
        """
        Add a rule result to the context.

        Args:
            rule_id: The ID of the rule that produced the result
            result: The result data
        """
        self.results[rule_id] = result

    def get_result(self, rule_id: str) -> Optional[Any]:
        """
        Get a rule result from the context.

        Args:
            rule_id: The ID of the rule

        Returns:
            The result data, or None if not found
        """
        return self.results.get(rule_id)

    def get_all_results(self) -> Dict[str, Any]:
        """
        Get all rule results.

        Returns:
            Dictionary of rule IDs to results
        """
        return self.results
