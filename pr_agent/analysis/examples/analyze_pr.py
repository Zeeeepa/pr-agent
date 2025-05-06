"""
Example script for analyzing a PR using the PR static analysis engine.
"""

import argparse
import json
import sys
from github import Github

from pr_agent.analysis.pr_analyzer import PRAnalyzer
from pr_agent.analysis.rule_engine import RuleEngine
from pr_agent.analysis.rules import FileSizeRule, NamingConventionRule
from pr_agent.git_providers.github_provider import GithubProvider
from pr_agent.log import get_logger

def main():
    """Main function for the PR analysis example."""
    parser = argparse.ArgumentParser(description='Analyze a GitHub PR')
    parser.add_argument('--repo', required=True, help='Repository name (owner/repo)')
    parser.add_argument('--pr', type=int, required=True, help='PR number')
    parser.add_argument('--token', required=True, help='GitHub token')
    parser.add_argument('--output', default='analysis_report.json', help='Output file for the analysis report')
    parser.add_argument('--use-git-provider', action='store_true', help='Use GitProvider instead of direct GitHub API')
    args = parser.parse_args()
    
    logger = get_logger()
    logger.info(f"Analyzing PR {args.repo}#{args.pr}")
    
    # Initialize GitHub client
    github_client = Github(args.token)
    
    # Initialize rule engine
    rule_engine = RuleEngine()
    
    # Register rules
    rule_engine.register_rule(FileSizeRule(max_file_size_kb=500))
    rule_engine.register_rule(NamingConventionRule())
    
    # Initialize PR analyzer
    analyzer = PRAnalyzer(rule_engine, github_client)
    
    # Analyze PR
    if args.use_git_provider:
        # Use GitProvider
        pr_url = f"https://github.com/{args.repo}/pull/{args.pr}"
        git_provider = GithubProvider(pr_url)
        report = analyzer.analyze_pr_with_git_provider(git_provider)
    else:
        # Use direct GitHub API
        report = analyzer.analyze_pr(args.repo, args.pr)
    
    # Print summary
    print(f"Analysis complete for PR {args.repo}#{args.pr}")
    print(f"Total rules run: {report['summary']['total_rules_run']}")
    print(f"Total issues found: {report['summary']['total_issues']}")
    
    # Print issues by severity
    for severity, count in report['summary']['issue_counts'].items():
        if count > 0:
            print(f"  {severity.capitalize()}: {count}")
    
    # Write report to file
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Analysis report written to {args.output}")
    
    # Return non-zero exit code if issues were found
    if report['summary']['total_issues'] > 0:
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())

