import os
from typing import Dict, Any, List, Optional, Union
import asyncio
import json
import time
from datetime import datetime

from github.Repository import Repository
from github.Workflow import Workflow as GithubWorkflow
from github.WorkflowRun import WorkflowRun as GithubWorkflowRun

from ..models.workflow import Workflow, WorkflowRun, WorkflowStatus, WorkflowTrigger
from ..config import get_enable_notifications
from .github_service import GitHubService
from .notification_service import NotificationService

class WorkflowService:
    """
    Service for managing GitHub Actions workflows
    """
    def __init__(self):
        """Initialize the workflow service"""
        self.github_service = GitHubService()
        self.notification_service = NotificationService()
    
    async def get_workflows(self, owner: str, name: str) -> List[Workflow]:
        """
        Get all workflows for a repository
        
        Args:
            owner: Repository owner
            name: Repository name
            
        Returns:
            List of Workflow objects
        """
        return await self.github_service.get_workflows(owner, name)
    
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
        return await self.github_service.get_workflow_runs(owner, name, workflow_id, limit)
    
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
        result = await self.github_service.trigger_workflow(owner, name, workflow_id, ref, inputs)
        
        if result:
            # Send notification if enabled
            if get_enable_notifications():
                await self.notification_service.send_workflow_triggered_notification(
                    owner, name, workflow_id, ref, inputs
                )
        
        return result
    
    async def monitor_workflow_run(self, owner: str, name: str, run_id: str, 
                                 timeout: int = 600, check_interval: int = 10) -> Dict[str, Any]:
        """
        Monitor a workflow run until completion or timeout
        
        Args:
            owner: Repository owner
            name: Repository name
            run_id: Workflow run ID
            timeout: Maximum time to wait in seconds
            check_interval: Time between checks in seconds
            
        Returns:
            Dictionary with status information
        """
        start_time = time.time()
        elapsed_time = 0
        
        while elapsed_time < timeout:
            # Get the latest run status
            runs = await self.github_service.get_workflow_runs(owner, name)
            current_run = next((run for run in runs if str(run.id) == run_id), None)
            
            if not current_run:
                return {"status": "error", "message": f"Run {run_id} not found"}
            
            # Check if the run has completed
            if current_run.status == WorkflowStatus.COMPLETED:
                # Send notification if enabled
                if get_enable_notifications():
                    await self.notification_service.send_workflow_completed_notification(
                        owner, name, run_id, current_run.conclusion
                    )
                
                return {
                    "status": "completed",
                    "conclusion": current_run.conclusion,
                    "html_url": current_run.html_url,
                    "elapsed_time": elapsed_time
                }
            
            # Wait before checking again
            await asyncio.sleep(check_interval)
            elapsed_time = time.time() - start_time
        
        # If we've reached here, the workflow has timed out
        if get_enable_notifications():
            await self.notification_service.send_workflow_timeout_notification(
                owner, name, run_id
            )
        
        return {"status": "timeout", "message": f"Workflow run did not complete within {timeout} seconds"}
    
    async def cancel_workflow_run(self, owner: str, name: str, run_id: str) -> bool:
        """
        Cancel a workflow run
        
        Args:
            owner: Repository owner
            name: Repository name
            run_id: Workflow run ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            repo = self.github_service.github.get_repo(f"{owner}/{name}")
            run = repo.get_workflow_run(int(run_id))
            result = run.cancel()
            
            if result:
                # Send notification if enabled
                if get_enable_notifications():
                    await self.notification_service.send_workflow_cancelled_notification(
                        owner, name, run_id
                    )
            
            return result
        except Exception as e:
            print(f"Error cancelling workflow run: {e}")
            return False
    
    async def rerun_workflow_run(self, owner: str, name: str, run_id: str) -> bool:
        """
        Rerun a workflow run
        
        Args:
            owner: Repository owner
            name: Repository name
            run_id: Workflow run ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            repo = self.github_service.github.get_repo(f"{owner}/{name}")
            run = repo.get_workflow_run(int(run_id))
            result = run.rerun()
            
            if result:
                # Send notification if enabled
                if get_enable_notifications():
                    await self.notification_service.send_workflow_rerun_notification(
                        owner, name, run_id
                    )
            
            return result
        except Exception as e:
            print(f"Error rerunning workflow run: {e}")
            return False
