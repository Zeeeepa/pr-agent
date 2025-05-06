"""
PR Static Analysis Tool.

This tool analyzes a PR using the static analysis engine and provides feedback.
"""

import json
from typing import Any, Dict, List, Optional

from github import Github

from pr_agent.algo.ai_handlers.base_ai_handler import BaseAiHandler
from pr_agent.analysis.pr_analyzer import PRAnalyzer
from pr_agent.analysis.rule_engine import RuleEngine
from pr_agent.analysis.rules import FileSizeRule, NamingConventionRule
from pr_agent.git_providers.git_provider import GitProvider
from pr_agent.log import get_logger


class PRStaticAnalysis:
    """
    Tool for performing static analysis on PRs.

    This tool uses the PR static analysis engine to analyze PRs and provide feedback.
    """

    def __init__(self, git_provider: GitProvider, ai_handler: BaseAiHandler = None):
        """
        Initialize the PR static analysis tool.

        Args:
            git_provider: The git provider to use
            ai_handler: The AI handler to use for generating summaries
        """
        self.git_provider = git_provider
        self.ai_handler = ai_handler
        self.logger = get_logger()

        # Initialize rule engine
        self.rule_engine = RuleEngine()

        # Register default rules
        self._register_default_rules()

    def _register_default_rules(self):
        """Register default analysis rules."""
        self.rule_engine.register_rule(FileSizeRule(max_file_size_kb=500))
        self.rule_engine.register_rule(NamingConventionRule())

    def analyze(self) -> Dict[str, Any]:
        """
        Analyze the PR and generate a report.

        Returns:
            Analysis report
        """
        self.logger.info("Starting PR static analysis")

        # Initialize PR analyzer
        analyzer = PRAnalyzer(self.rule_engine, None)  # No GitHub client needed when using git_provider

        # Analyze PR
        report = analyzer.analyze_pr_with_git_provider(self.git_provider)

        # Generate summary with AI if available
        if self.ai_handler and report['summary']['total_issues'] > 0:
            report['ai_summary'] = self._generate_ai_summary(report)

        return report

    def _generate_ai_summary(self, report: Dict[str, Any]) -> str:
        """
        Generate an AI summary of the analysis report.

        Args:
            report: The analysis report

        Returns:
            AI-generated summary
        """
        self.logger.info("Generating AI summary of analysis report")

        # Prepare prompt for AI
        prompt = self._prepare_ai_prompt(report)

        # Generate summary
        try:
            response = self.ai_handler.chat_completion(
                prompt,
                temperature=0.2,
                model_type="reasoning"
            )
            return response
        except Exception as e:
            self.logger.error(f"Error generating AI summary: {str(e)}")
            return "Failed to generate AI summary."

    def _prepare_ai_prompt(self, report: Dict[str, Any]) -> str:
        """
        Prepare a prompt for the AI to summarize the analysis report.

        Args:
            report: The analysis report

        Returns:
            Prompt for the AI
        """
        # Extract issues from the report
        issues = []
        for rule_id, result in report['analysis_results'].items():
            if 'issues' in result:
                for issue in result['issues']:
                    issues.append({
                        'rule': rule_id,
                        'file': issue.get('file', 'Unknown'),
                        'message': issue.get('message', 'Unknown issue'),
                        'severity': issue.get('severity', 'info'),
                        'line': issue.get('line', None),
                    })

        # Format issues for the prompt
        issues_text = ""
        for i, issue in enumerate(issues, 1):
            line_info = f" (line {issue['line']})" if issue['line'] else ""
            issues_text += f"{i}. [{issue['severity'].upper()}] {issue['file']}{line_info}: {issue['message']} (Rule: {issue['rule']})\n"

        # Create the prompt
        prompt = f"""
You are a code review assistant. Please analyze the following static analysis report for a pull request and provide a concise, helpful summary.

PR Information:
- Repository: {report['pr_info']['repo']}
- PR Number: {report['pr_info']['pr_number']}
- Title: {report['pr_info']['title']}

Analysis Summary:
- Total rules run: {report['summary']['total_rules_run']}
- Total issues found: {report['summary']['total_issues']}
- Issues by severity:
  - Critical: {report['summary']['issue_counts']['critical']}
  - High: {report['summary']['issue_counts']['high']}
  - Medium: {report['summary']['issue_counts']['medium']}
  - Low: {report['summary']['issue_counts']['low']}
  - Info: {report['summary']['issue_counts']['info']}

Issues:
{issues_text}

Please provide:
1. A brief summary of the analysis results
2. The most important issues to address, prioritized by severity and impact
3. Actionable recommendations for the PR author

Your response should be concise, constructive, and focused on helping the developer improve the code quality.
"""
        return prompt

    def get_comment_markdown(self, report: Dict[str, Any]) -> str:
        """
        Generate a markdown comment for the analysis report.

        Args:
            report: The analysis report

        Returns:
            Markdown comment
        """
        # Start with a header
        markdown = "## 🔍 PR Static Analysis Results\n\n"

        # Add summary
        markdown += "### Summary\n\n"
        markdown += f"- **Total issues found:** {report['summary']['total_issues']}\n"

        # Add issues by severity
        markdown += "- **Issues by severity:**\n"
        for severity, count in report['summary']['issue_counts'].items():
            if count > 0:
                emoji = self._get_severity_emoji(severity)
                markdown += f"  - {emoji} **{severity.capitalize()}:** {count}\n"

        # Add AI summary if available
        if 'ai_summary' in report:
            markdown += "\n### AI Summary\n\n"
            markdown += report['ai_summary']

        # Add issues
        if report['summary']['total_issues'] > 0:
            markdown += "\n### Issues\n\n"

            # Group issues by file
            issues_by_file = {}
            for rule_id, result in report['analysis_results'].items():
                if 'issues' in result:
                    for issue in result['issues']:
                        file = issue.get('file', 'Unknown')
                        if file not in issues_by_file:
                            issues_by_file[file] = []
                        issues_by_file[file].append({
                            'rule': rule_id,
                            'message': issue.get('message', 'Unknown issue'),
                            'severity': issue.get('severity', 'info'),
                            'line': issue.get('line', None),
                        })

            # Add issues by file
            for file, issues in issues_by_file.items():
                markdown += f"#### {file}\n\n"
                for issue in issues:
                    emoji = self._get_severity_emoji(issue['severity'])
                    line_info = f" (line {issue['line']})" if issue['line'] else ""
                    markdown += f"- {emoji} **{issue['severity'].capitalize()}:** {issue['message']}{line_info}\n"
                markdown += "\n"

        return markdown

    def _get_severity_emoji(self, severity: str) -> str:
        """
        Get an emoji for a severity level.

        Args:
            severity: The severity level

        Returns:
            Emoji for the severity
        """
        severity = severity.lower()
        if severity == 'critical':
            return "🚨"
        elif severity == 'high':
            return "❗"
        elif severity == 'medium':
            return "⚠️"
        elif severity == 'low':
            return "ℹ️"
        else:
            return "📝"

    def run(self) -> str:
        """
        Run the PR static analysis and return a markdown comment.

        Returns:
            Markdown comment with analysis results
        """
        # Analyze PR
        report = self.analyze()

        # Generate markdown comment
        markdown = self.get_comment_markdown(report)

        # Post comment to PR
        if report['summary']['total_issues'] > 0:
            self.git_provider.publish_comment(markdown)

        return markdown
