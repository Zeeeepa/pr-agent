"""
Integration example for the PR Static Analysis Reporting System.

This example demonstrates how to integrate the reporting system with a hypothetical
analysis engine.
"""

from typing import Dict, Any, List
from pr_static_analysis.report import (
    create_markdown_report_integration,
    create_html_report_integration,
    create_json_report_integration
)


class HypotheticalAnalysisEngine:
    """
    A hypothetical analysis engine that performs static analysis on code.
    
    This is just a mock class for demonstration purposes.
    """
    
    def analyze_pr(self, pr_url: str) -> List[Dict[str, Any]]:
        """
        Analyze a pull request and return the analysis results.
        
        Args:
            pr_url (str): The URL of the pull request to analyze.
        
        Returns:
            List[Dict[str, Any]]: The analysis results.
        """
        # In a real implementation, this would actually analyze the PR
        # For this example, we'll just return some mock results
        return [
            {
                "severity": "error",
                "message": "Missing return type annotation",
                "file": "example.py",
                "line": 10,
                "recommendation": "Add a return type annotation to the function"
            },
            {
                "severity": "warning",
                "message": "Unused variable",
                "file": "example.py",
                "line": 15,
                "recommendation": "Remove the unused variable or use it"
            },
            {
                "severity": "info",
                "message": "Consider using a more descriptive variable name",
                "file": "utils.py",
                "line": 20
            }
        ]


class HypotheticalGitHubClient:
    """
    A hypothetical GitHub client that can post comments on pull requests.
    
    This is just a mock class for demonstration purposes.
    """
    
    def post_comment(self, repo_owner: str, repo_name: str, pr_number: int, body: str) -> Dict[str, Any]:
        """
        Post a comment on a pull request.
        
        Args:
            repo_owner (str): The owner of the repository.
            repo_name (str): The name of the repository.
            pr_number (int): The number of the pull request.
            body (str): The body of the comment.
        
        Returns:
            Dict[str, Any]: The response from the GitHub API.
        """
        # In a real implementation, this would actually post a comment to GitHub
        # For this example, we'll just print the comment and return a mock response
        print(f"Posting comment to {repo_owner}/{repo_name}#{pr_number}:")
        print("-" * 80)
        print(body[:200] + "..." if len(body) > 200 else body)
        print("-" * 80)
        return {"id": 12345}


def github_api_callback(url: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    A callback function that makes API calls to GitHub.
    
    Args:
        url (str): The URL to make the API call to.
        data (Dict[str, Any]): The data to include in the API call.
    
    Returns:
        Dict[str, Any]: The response from the GitHub API.
    """
    # Extract the repository owner, name, and PR number from the URL
    # URL format: https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments
    parts = url.split("/")
    repo_owner = parts[4]
    repo_name = parts[5]
    pr_number = int(parts[7])
    
    # Create a GitHub client and post the comment
    github_client = HypotheticalGitHubClient()
    return github_client.post_comment(repo_owner, repo_name, pr_number, data["body"])


def main():
    """
    Main function that demonstrates the integration.
    """
    # Create an analysis engine
    engine = HypotheticalAnalysisEngine()
    
    # Analyze a pull request
    pr_url = "https://github.com/owner/repo/pull/123"
    results = engine.analyze_pr(pr_url)
    
    # Create an integration with a Markdown formatter
    integration = create_markdown_report_integration()
    
    # Generate a report from the analysis results
    report = integration.generate_report(results)
    
    # Post the report to GitHub
    integration.post_report_to_github(
        report=report,
        pr_number=123,
        repo_owner="owner",
        repo_name="repo",
        github_api_callback=github_api_callback
    )


if __name__ == "__main__":
    main()

