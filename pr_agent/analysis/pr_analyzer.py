"""
PR Analyzer for Static Analysis.

This module provides the PRAnalyzer class for orchestrating the PR analysis process.
"""

from typing import Dict, List, Any, Optional
from pr_agent.analysis.analysis_context import AnalysisContext
from pr_agent.analysis.rule_engine import RuleEngine
from pr_agent.git_providers.git_provider import GitProvider
from pr_agent.log import get_logger

class PRAnalyzer:
    """
    Main orchestrator for the PR analysis process.
    
    Coordinates the analysis of PRs using the rule engine.
    Manages the analysis context and results.
    Interfaces with GitHub components for PR data.
    """
    
    def __init__(self, rule_engine: RuleEngine, github_client: Any):
        """
        Initialize the PR analyzer.
        
        Args:
            rule_engine: The rule engine to use for analysis
            github_client: The GitHub client for fetching PR data
        """
        self.rule_engine = rule_engine
        self.github_client = github_client
        self.logger = get_logger()
        
    def analyze_pr(self, repo: str, pr_number: int) -> Dict[str, Any]:
        """
        Analyze a pull request.
        
        Args:
            repo: The repository name (owner/repo)
            pr_number: The PR number
            
        Returns:
            Analysis report
        """
        self.logger.info(f"Analyzing PR {repo}#{pr_number}")
        
        # Get PR data from GitHub
        pr_data = self._get_pr_data(repo, pr_number)
        
        # Create analysis context
        context = AnalysisContext(pr_data)
        
        # Load codebases
        context.load_codebases()
        
        # Run analysis rules
        results = self.rule_engine.run_rules(context)
        
        # Generate report
        report = self._generate_report(results, context)
        
        return report
    
    def _get_pr_data(self, repo: str, pr_number: int) -> Dict[str, Any]:
        """
        Get PR data from GitHub.
        
        Args:
            repo: The repository name (owner/repo)
            pr_number: The PR number
            
        Returns:
            Dictionary containing PR data
        """
        self.logger.info(f"Fetching PR data for {repo}#{pr_number}")
        
        # Get the repository object
        repo_obj = self.github_client.get_repo(repo)
        
        # Get the PR object
        pr = repo_obj.get_pull(pr_number)
        
        # Get the base and head commits
        base_commit = pr.base.sha
        head_commit = pr.head.sha
        
        # Get the changed files
        changed_files = list(pr.get_files())
        
        # Construct PR data dictionary
        pr_data = {
            'repo': repo,
            'pr_number': pr_number,
            'title': pr.title,
            'body': pr.body,
            'base_commit': base_commit,
            'head_commit': head_commit,
            'changed_files': changed_files,
            'user': pr.user.login,
            'created_at': pr.created_at,
            'updated_at': pr.updated_at,
            'state': pr.state,
            'labels': [label.name for label in pr.labels],
        }
        
        return pr_data
    
    def _generate_report(self, results: Dict[str, Any], context: AnalysisContext) -> Dict[str, Any]:
        """
        Generate an analysis report from rule results.
        
        Args:
            results: Dictionary mapping rule IDs to results
            context: The analysis context
            
        Returns:
            Analysis report
        """
        self.logger.info("Generating analysis report")
        
        # Construct the report
        report = {
            'pr_info': {
                'repo': context.pr_data['repo'],
                'pr_number': context.pr_data['pr_number'],
                'title': context.pr_data['title'],
            },
            'analysis_results': results,
            'summary': self._generate_summary(results, context),
        }
        
        return report
    
    def _generate_summary(self, results: Dict[str, Any], context: AnalysisContext) -> Dict[str, Any]:
        """
        Generate a summary of the analysis results.
        
        Args:
            results: Dictionary mapping rule IDs to results
            context: The analysis context
            
        Returns:
            Summary dictionary
        """
        # Count issues by severity
        severity_counts = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'info': 0,
        }
        
        # Process results to count issues by severity
        for rule_id, result in results.items():
            if 'issues' in result:
                for issue in result['issues']:
                    severity = issue.get('severity', 'info').lower()
                    if severity in severity_counts:
                        severity_counts[severity] += 1
        
        # Generate summary
        summary = {
            'total_rules_run': len(results),
            'issue_counts': severity_counts,
            'total_issues': sum(severity_counts.values()),
        }
        
        return summary
    
    def analyze_pr_with_git_provider(self, git_provider: GitProvider) -> Dict[str, Any]:
        """
        Analyze a pull request using a GitProvider.
        
        This method is an alternative to analyze_pr that uses a GitProvider
        instead of directly accessing the GitHub API.
        
        Args:
            git_provider: The GitProvider instance
            
        Returns:
            Analysis report
        """
        self.logger.info(f"Analyzing PR with GitProvider")
        
        # Get PR data
        pr_data = self._get_pr_data_from_git_provider(git_provider)
        
        # Create analysis context
        context = AnalysisContext(pr_data)
        
        # Get changed files
        changed_files = git_provider.get_diff_files()
        context.set_changed_files(changed_files)
        
        # Run analysis rules
        results = self.rule_engine.run_rules(context)
        
        # Generate report
        report = self._generate_report(results, context)
        
        return report
    
    def _get_pr_data_from_git_provider(self, git_provider: GitProvider) -> Dict[str, Any]:
        """
        Get PR data from a GitProvider.
        
        Args:
            git_provider: The GitProvider instance
            
        Returns:
            Dictionary containing PR data
        """
        self.logger.info("Fetching PR data from GitProvider")
        
        # Get PR metadata
        pr_metadata = git_provider.get_pr_metadata()
        
        # Construct PR data dictionary
        pr_data = {
            'repo': git_provider.repo,
            'pr_number': git_provider.pr_num,
            'title': pr_metadata.get('title', ''),
            'body': pr_metadata.get('body', ''),
            'base_commit': pr_metadata.get('base_commit', ''),
            'head_commit': pr_metadata.get('head_commit', ''),
            'changed_files': [],  # Will be set separately
            'user': pr_metadata.get('user', ''),
            'created_at': pr_metadata.get('created_at', None),
            'updated_at': pr_metadata.get('updated_at', None),
            'state': pr_metadata.get('state', ''),
            'labels': pr_metadata.get('labels', []),
        }
        
        return pr_data

