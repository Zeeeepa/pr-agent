"""
File Size Rule for PR Static Analysis.

This rule checks if files in the PR exceed a certain size threshold.
"""

from typing import Any, Dict, List

from pr_agent.algo.types import FilePatchInfo
from pr_agent.analysis.analysis_context import AnalysisContext
from pr_agent.analysis.rule_engine import Rule


class FileSizeRule(Rule):
    """
    Rule that checks if files in the PR exceed a certain size threshold.
    """

    def __init__(self, max_file_size_kb: int = 500):
        """
        Initialize the file size rule.

        Args:
            max_file_size_kb: Maximum file size in KB
        """
        super().__init__(
            rule_id="file_size",
            description=f"Checks if files exceed {max_file_size_kb}KB in size",
            priority=10  # Higher priority rules run first
        )
        self.max_file_size_kb = max_file_size_kb

    def run(self, context: AnalysisContext) -> Dict[str, Any]:
        """
        Run the rule on the given context.

        Args:
            context: The analysis context

        Returns:
            Dictionary containing the rule results
        """
        self.logger.info(f"Running {self.rule_id} rule")

        # Get changed files
        changed_files = context.get_changed_files()

        # Check file sizes
        issues = []
        for file in changed_files:
            if self._is_file_too_large(file):
                issues.append({
                    'file': file.filename,
                    'message': f"File exceeds the maximum size of {self.max_file_size_kb}KB",
                    'severity': 'medium',
                    'line': None,
                })

        # Return results
        return {
            'rule_id': self.rule_id,
            'description': self.description,
            'issues': issues,
            'passed': len(issues) == 0,
        }

    def _is_file_too_large(self, file: FilePatchInfo) -> bool:
        """
        Check if a file is too large.

        Args:
            file: The file to check

        Returns:
            True if the file is too large, False otherwise
        """
        # Calculate file size in KB
        file_size_kb = 0

        if file.head_file:
            file_size_kb = len(file.head_file) / 1024

        return file_size_kb > self.max_file_size_kb
