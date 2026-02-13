"""
Example event handler for PR comments.

This module provides an example of how to handle PR comment events.
"""

import os
import requests
from typing import Any, Dict, Optional


def handle_event(payload: Dict[str, Any], event_type: str, action: Optional[str] = None) -> str:
    """Handle a GitHub event.
    
    Args:
        payload: The event payload.
        event_type: The type of event.
        action: The action of the event.
        
    Returns:
        A message indicating the result of the event handling.
    """
    # Check if this is a PR comment event
    if event_type != "issue_comment" or action != "created":
        return f"Ignoring event of type {event_type} with action {action}"
    
    # Check if the comment is on a PR
    if "pull_request" not in payload.get("issue", {}):
        return "Ignoring comment on an issue (not a PR)"
    
    # Get the comment body
    comment_body = payload.get("comment", {}).get("body", "")
    
    # Check if the comment contains a trigger phrase
    if not comment_body.startswith("/hello"):
        return "Ignoring comment that doesn't start with /hello"
    
    # Get PR information
    repo_full_name = payload.get("repository", {}).get("full_name", "")
    pr_number = payload.get("issue", {}).get("number")
    comment_id = payload.get("comment", {}).get("id")
    
    if not repo_full_name or not pr_number or not comment_id:
        return "Missing required information from payload"
    
    # Post a reply comment
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        return "GITHUB_TOKEN environment variable not set"
    
    api_url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "body": "👋 Hello! I received your command."
    }
    
    response = requests.post(api_url, headers=headers, json=data)
    
    if response.status_code == 201:
        return f"Successfully posted reply to PR #{pr_number}"
    else:
        return f"Failed to post reply: {response.status_code} - {response.text}"
