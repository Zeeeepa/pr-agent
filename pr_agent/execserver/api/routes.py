from fastapi import APIRouter, Depends, HTTPException, Request, Response, BackgroundTasks
from typing import Dict, Any, List, Optional
import json
import uuid

from ..models.event import Event
from ..models.project import Project
from ..models.trigger import Trigger, TriggerCondition, TriggerAction, EventType, TriggerType
from ..models.workflow import Workflow, WorkflowRun
from ..services.db_service import DatabaseService
from ..services.github_service import GitHubService
from ..services.event_service import EventService
from ..services.workflow_service import WorkflowService
from ..services.settings_service import SettingsService
from pr_agent.servers.utils import verify_signature
from pr_agent.servers.github_app import handle_github_webhooks as pr_agent_handle_github_webhooks
from ..config import get_setting_or_env

# Create router
router = APIRouter()

# Service instances
settings_service = SettingsService()
db_service = DatabaseService(settings_service)
github_service = GitHubService()
workflow_service = WorkflowService()
event_service = EventService(db_service, github_service, workflow_service)

# GitHub webhook endpoint
@router.post("/api/v1/github_webhooks")
async def handle_github_webhooks(background_tasks: BackgroundTasks, request: Request, response: Response):
    """
    Handle GitHub webhook events
    """
    # Get the request body
    body = await request.json()
    
    # Verify the webhook signature
    github_secret = get_setting_or_env("GITHUB_WEBHOOK_SECRET")
    if github_secret:
        signature = request.headers.get("X-Hub-Signature-256")
        if not signature:
            raise HTTPException(status_code=401, detail="Missing signature header")
        
        if not verify_signature(await request.body(), signature, github_secret):
            raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Get the event type
    event_type = request.headers.get("X-GitHub-Event")
    if not event_type:
        raise HTTPException(status_code=400, detail="Missing event type header")
    
    # Process the webhook in the background using both PR-Agent's handler and our custom handler
    background_tasks.add_task(pr_agent_handle_github_webhooks, background_tasks, request, response)
    background_tasks.add_task(event_service.process_webhook, event_type, body)
    
    return {"status": "processing"}

# Settings endpoints
@router.post("/api/v1/settings/validate")
async def validate_settings(settings: Dict[str, str]):
    """
    Validate settings
    """
    try:
        # Validate the settings
        valid = await settings_service.validate_settings(settings)
        return {"valid": valid}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/api/v1/settings")
async def save_settings(settings: Dict[str, str]):
    """
    Save settings
    """
    try:
        # Save the settings
        await settings_service.save_settings(settings)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/api/v1/settings")
async def get_settings():
    """
    Get settings
    """
    try:
        # Get the settings
        settings = await settings_service.get_settings()
        return settings
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Projects endpoints
@router.get("/api/v1/projects")
async def get_projects() -> List[Project]:
    """
    Get all projects
    """
    return await db_service.get_projects()

@router.get("/api/v1/projects/github")
async def get_github_projects() -> List[Project]:
    """
    Get all GitHub repositories
    """
    return await github_service.get_repositories()

@router.get("/api/v1/projects/{project_id}")
async def get_project(project_id: str) -> Project:
    """
    Get a project by ID
    """
    project = await db_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

# Triggers endpoints
@router.get("/api/v1/triggers")
async def get_triggers(project_id: Optional[str] = None) -> List[Trigger]:
    """
    Get all triggers, optionally filtered by project
    """
    if project_id:
        return await db_service.get_triggers_for_project(project_id)
    
    # Get all projects
    projects = await db_service.get_projects()
    
    # Get triggers for each project
    all_triggers = []
    for project in projects:
        triggers = await db_service.get_triggers_for_project(project.id)
        all_triggers.extend(triggers)
    
    return all_triggers

@router.post("/api/v1/triggers")
async def create_trigger(trigger: Trigger) -> Trigger:
    """
    Create a new trigger
    """
    # Validate project exists
    project = await db_service.get_project(trigger.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create the trigger
    return await db_service.create_trigger(trigger)

@router.get("/api/v1/triggers/{trigger_id}")
async def get_trigger(trigger_id: str) -> Trigger:
    """
    Get a trigger by ID
    """
    trigger = await db_service.get_trigger(trigger_id)
    if not trigger:
        raise HTTPException(status_code=404, detail="Trigger not found")
    return trigger

@router.patch("/api/v1/triggers/{trigger_id}")
async def update_trigger(trigger_id: str, data: Dict[str, Any]) -> Trigger:
    """
    Update a trigger
    """
    trigger = await db_service.update_trigger(trigger_id, data)
    if not trigger:
        raise HTTPException(status_code=404, detail="Trigger not found")
    return trigger

# Workflows endpoints
@router.get("/api/v1/workflows")
async def get_workflows(repository: str) -> List[Workflow]:
    """
    Get all workflows for a repository
    """
    owner, repo = repository.split("/")
    return await github_service.get_workflows(owner, repo)

@router.get("/api/v1/workflow_runs")
async def get_workflow_runs(repository: str, workflow_id: Optional[str] = None, limit: int = 10) -> List[WorkflowRun]:
    """
    Get workflow runs for a repository
    """
    owner, repo = repository.split("/")
    return await github_service.get_workflow_runs(owner, repo, workflow_id, limit)

@router.post("/api/v1/workflows/{workflow_id}/dispatch")
async def trigger_workflow(workflow_id: str, repository: str, ref: Optional[str] = None, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Trigger a workflow
    """
    owner, repo = repository.split("/")
    success = await github_service.trigger_workflow(owner, repo, workflow_id, ref, inputs)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to trigger workflow")
    
    return {"status": "triggered"}

# Events endpoints
@router.get("/api/v1/events")
async def get_events(repository: Optional[str] = None, limit: int = 10) -> List[Event]:
    """
    Get recent events
    """
    return await event_service.get_recent_events(repository, limit)

# Execute code endpoint
@router.post("/api/v1/execute_code")
async def execute_code(code: str, repository: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute Python code
    """
    success = await workflow_service.execute_python_code(code, repository, event_data)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to execute code")
    
    return {"status": "executed"}
