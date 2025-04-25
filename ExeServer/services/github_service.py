import os
from typing import Dict, Any, List, Optional, Union
import asyncio
import json

from github import Github, GithubIntegration, Auth
from github.Repository import Repository
from github.Workflow import Workflow as GithubWorkflow
from github.WorkflowRun import WorkflowRun as GithubWorkflowRun

from pr_agent.git_providers.github_provider import GithubProvider
from pr_agent.git_providers.git_provider import GitProvider

from ..models.project import Project
from ..models.workflow import Workflow, WorkflowRun, WorkflowStatus, WorkflowTrigger
from ..config import GITHUB_TOKEN, GITHUB_APP_ID, GITHUB_APP_PRIVATE_KEY, GITHUB_APP_INSTALLATION_ID


class GitHubService:
    """
    Service for interacting with GitHub API
    """
    def __init__(self):
        """Initialize the GitHub service"""
        if GITHUB_APP_ID and GITHUB_APP_PRIVATE_KEY and GITHUB_APP_INSTALLATION_ID:
            # Use GitHub App authentication
            auth = Auth.AppAuth(GITHUB_APP_ID, GITHUB_APP_PRIVATE_KEY)
            integration = GithubIntegration(auth=auth)
            auth = Auth.AppInstallationAuth(
                GITHUB_APP_INSTALLATION_ID, 
                integration.get_access_token(GITHUB_APP_INSTALLATION_ID).token
            )
            self.github = Github(auth=auth)
        elif GITHUB_TOKEN:
            # Use personal access token
            self.github = Github(GITHUB_TOKEN)
        else:
            raise ValueError("GitHub authentication credentials not provided")
        
        # Initialize PR-Agent's GitHub provider
        self.pr_agent_github_provider = None
    
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
        repos = []
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
        try:
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
            repo = self.github.get_repo(f"{owner}/{name}")
            pr = repo.get_pull(pr_number)
            
            files = []
            for file in pr.get_files():
                files.append({
                    "filename": file.filename,
                    "status": file.status,
                    "additions": file.additions,
                    "deletions": file.deletions,
                    "changes": file.changes,
                    "blob_url": file.blob_url,
                    "raw_url": file.raw_url,
                    "contents_url": file.contents_url
                })
            
            return files
        except Exception as e:
            print(f"Error getting PR files: {e}")
            return []
