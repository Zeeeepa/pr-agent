import os
from typing import Dict, Any, List, Optional, Union
import asyncio
import json

from github import Github, GithubIntegration, GithubException, BadCredentialsException, RateLimitExceededException
from github.Repository import Repository
from github.Workflow import Workflow as GithubWorkflow
from github.WorkflowRun import WorkflowRun as GithubWorkflowRun

from pr_agent.git_providers.github_provider import GithubProvider
from pr_agent.git_providers.git_provider import GitProvider
from pr_agent.servers.github_action_runner import get_setting_or_env

from ..models.project import Project
from ..models.workflow import Workflow, WorkflowRun, WorkflowStatus, WorkflowTrigger
from ..config import get_github_token, get_github_app_id, get_github_app_private_key, get_github_app_installation_id


class GitHubService:
    """
    Service for interacting with GitHub API
    """
    def __init__(self):
        """Initialize the GitHub service"""
        # Initialize PR-Agent's GitHub provider
        self.pr_agent_github_provider = None
        self.github = None
        
        # Initialize PyGithub client
        try:
            github_app_id = get_github_app_id()
            github_app_private_key = get_github_app_private_key()
            github_app_installation_id = get_github_app_installation_id()
            github_token = get_github_token()
            
            if github_app_id and github_app_private_key and github_app_installation_id:
                # Use GitHub App authentication (PyGithub 1.58.1 compatible)
                integration = GithubIntegration(
                    github_app_id,
                    github_app_private_key
                )
                # Get an access token for the installation
                access_token = integration.get_access_token(github_app_installation_id).token
                self.github = Github(access_token)
                
                # Verify the token works by making a simple API call
                self.github.get_rate_limit()
            elif github_token:
                # Use personal access token
                self.github = Github(github_token)
                
                # Verify the token works by making a simple API call
                self.github.get_rate_limit()
            else:
                # No authentication provided, but don't raise an error yet
                # We'll check for self.github before making API calls
                pass
        except BadCredentialsException:
            print("GitHub authentication failed: Invalid credentials")
            self.github = None
        except RateLimitExceededException:
            print("GitHub authentication failed: Rate limit exceeded")
            self.github = None
        except GithubException as e:
            print(f"GitHub authentication failed: {e.data.get('message', str(e))}")
            self.github = None
        except Exception as e:
            print(f"GitHub authentication failed: {str(e)}")
            self.github = None
    
    def _ensure_github_client(self):
        """
        Ensure GitHub client is initialized
        
        Raises:
            ValueError: If GitHub client is not initialized
        """
        if not self.github:
            github_token = get_github_token()
            if github_token:
                try:
                    self.github = Github(github_token)
                    # Test the connection
                    self.github.get_rate_limit()
                except Exception as e:
                    raise ValueError(f"Failed to initialize GitHub client: {str(e)}")
            else:
                raise ValueError("GitHub authentication credentials not provided. Please set a valid GitHub token in settings.")
    
    def get_pr_agent_github_provider(self, pr_url: Optional[str] = None) -> GithubProvider:
        """
        Get PR-Agent's GitHub provider
        
        Args:
            pr_url: Optional PR URL to initialize the provider with
            
        Returns:
            GithubProvider instance
        """
        if not self.pr_agent_github_provider or pr_url:
            self.pr_agent_github_provider = GithubProvider(pr_url)
        return self.pr_agent_github_provider
    
    async def get_repositories(self) -> List[Project]:
        """
        Get all repositories the authenticated user has access to
        
        Returns:
            List of Project objects
        """
        self._ensure_github_client()
        
        repos = []
        try:
            for repo in self.github.get_user().get_repos():
                project = Project(
                    id=str(repo.id),
                    name=repo.name,
                    full_name=repo.full_name,
                    description=repo.description,
                    html_url=repo.html_url,
                    api_url=repo.url,
                    default_branch=repo.default_branch
                )
                repos.append(project)
        except Exception as e:
            print(f"Error getting repositories: {e}")
        
        return repos
    
    async def get_repository(self, owner: str, name: str) -> Optional[Project]:
        """
        Get a repository by owner and name
        
        Args:
            owner: Repository owner
            name: Repository name
            
        Returns:
            Project object or None if not found
        """
        self._ensure_github_client()
        
        try:
            repo = self.github.get_repo(f"{owner}/{name}")
            return Project(
                id=str(repo.id),
                name=repo.name,
                full_name=repo.full_name,
                description=repo.description,
                html_url=repo.html_url,
                api_url=repo.url,
                default_branch=repo.default_branch
            )
        except Exception as e:
            print(f"Error getting repository: {e}")
            return None
    
    async def get_workflows(self, owner: str, name: str) -> List[Workflow]:
        """
        Get all workflows for a repository
        
        Args:
            owner: Repository owner
            name: Repository name
            
        Returns:
            List of Workflow objects
        """
        self._ensure_github_client()
        
        try:
            repo = self.github.get_repo(f"{owner}/{name}")
            workflows = []
            
            for workflow in repo.get_workflows():
                # Map GitHub workflow state to our WorkflowStatus enum
                status = WorkflowStatus.ACTIVE if workflow.state == "active" else WorkflowStatus.INACTIVE
                
                # Try to determine the trigger type from the workflow file
                trigger = WorkflowTrigger.PUSH  # Default
                try:
                    workflow_content = repo.get_contents(workflow.path).decoded_content.decode('utf-8')
                    if "pull_request" in workflow_content:
                        trigger = WorkflowTrigger.PULL_REQUEST
                    elif "schedule" in workflow_content:
                        trigger = WorkflowTrigger.SCHEDULE
                    elif "workflow_dispatch" in workflow_content:
                        trigger = WorkflowTrigger.WORKFLOW_DISPATCH
                    elif "repository_dispatch" in workflow_content:
                        trigger = WorkflowTrigger.REPOSITORY_DISPATCH
                except:
                    pass
                
                workflows.append(Workflow(
                    id=str(workflow.id),
                    name=workflow.name,
                    repository=repo.full_name,
                    path=workflow.path,
                    status=status,
                    trigger=trigger,
                    html_url=workflow.html_url,
                    api_url=workflow.url
                ))
            
            return workflows
        except Exception as e:
            print(f"Error getting workflows: {e}")
            return []
    
    async def get_workflow_runs(self, owner: str, name: str, workflow_id: Optional[str] = None, 
                              limit: int = 10) -> List[WorkflowRun]:
        """
        Get workflow runs for a repository
        
        Args:
            owner: Repository owner
            name: Repository name
            workflow_id: Optional workflow ID to filter by
            limit: Maximum number of runs to return
            
        Returns:
            List of WorkflowRun objects
        """
        self._ensure_github_client()
        
        try:
            repo = self.github.get_repo(f"{owner}/{name}")
            runs = []
            
            if workflow_id:
                workflow = repo.get_workflow(int(workflow_id))
                workflow_runs = workflow.get_runs()
            else:
                workflow_runs = repo.get_workflow_runs()
            
            count = 0
            for run in workflow_runs:
                if count >= limit:
                    break
                
                # Map GitHub workflow run status to our WorkflowStatus enum
                if run.status == "completed":
                    status = WorkflowStatus.COMPLETED
                elif run.status == "in_progress":
                    status = WorkflowStatus.IN_PROGRESS
                elif run.status == "queued":
                    status = WorkflowStatus.QUEUED
                else:
                    status = WorkflowStatus.ACTIVE
                
                runs.append(WorkflowRun(
                    id=str(run.id),
                    workflow_id=str(run.workflow_id),
                    repository=repo.full_name,
                    trigger=run.event,
                    status=status,
                    conclusion=run.conclusion,
                    created_at=run.created_at,
                    updated_at=run.updated_at,
                    html_url=run.html_url,
                    api_url=run.url
                ))
                count += 1
            
            return runs
        except Exception as e:
            print(f"Error getting workflow runs: {e}")
            return []
    
    async def trigger_workflow(self, owner: str, name: str, workflow_id: str, 
                             ref: Optional[str] = None, inputs: Optional[Dict[str, Any]] = None) -> bool:
        """
        Trigger a workflow
        
        Args:
            owner: Repository owner
            name: Repository name
            workflow_id: Workflow ID
            ref: Git reference (branch, tag, commit)
            inputs: Workflow inputs
            
        Returns:
            True if successful, False otherwise
        """
        self._ensure_github_client()
        
        try:
            # Use PR-Agent's github_action_runner functionality
            repo = self.github.get_repo(f"{owner}/{name}")
            workflow = repo.get_workflow(int(workflow_id))
            
            if not ref:
                ref = repo.default_branch
            
            workflow.create_dispatch(ref, inputs or {})
            return True
        except Exception as e:
            print(f"Error triggering workflow: {e}")
            return False
    
    async def comment_on_pr(self, owner: str, name: str, pr_number: int, comment: str) -> bool:
        """
        Add a comment to a pull request
        
        Args:
            owner: Repository owner
            name: Repository name
            pr_number: Pull request number
            comment: Comment text
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Use PR-Agent's GitHub provider to comment
            pr_url = f"https://github.com/{owner}/{name}/pull/{pr_number}"
            github_provider = self.get_pr_agent_github_provider(pr_url)
            github_provider.add_comment(comment)
            return True
        except Exception as e:
            print(f"Error commenting on PR: {e}")
            return False
    
    async def get_pr_files(self, owner: str, name: str, pr_number: int) -> List[Dict[str, Any]]:
        """
        Get files changed in a pull request
        
        Args:
            owner: Repository owner
            name: Repository name
            pr_number: Pull request number
            
        Returns:
            List of file information dictionaries
        """
        try:
            # Use PR-Agent's GitHub provider to get PR files
            pr_url = f"https://github.com/{owner}/{name}/pull/{pr_number}"
            github_provider = self.get_pr_agent_github_provider(pr_url)
            files = github_provider.get_files()
            
            result = []
            for file in files:
                result.append({
                    "filename": file.filename,
                    "status": file.status,
                    "additions": file.additions,
                    "deletions": file.deletions,
                    "changes": file.changes,
                    "blob_url": file.blob_url,
                    "raw_url": file.raw_url,
                    "contents_url": file.contents_url
                })
            
            return result
        except Exception as e:
            print(f"Error getting PR files: {e}")
            return []
