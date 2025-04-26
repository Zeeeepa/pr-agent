from fastapi import APIRouter, Depends, HTTPException, Request, Response, BackgroundTasks
from typing import Dict, Any, List, Optional
import json
import uuid
import logging

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
from ..config import get_setting_or_env, set_settings_service

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Service instances
settings_service = SettingsService()
set_settings_service(settings_service)  # Set the global settings service
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
@router.post("/api/v1/validate_settings")
async def validate_settings(settings: Dict[str, str]):
    """
    Validate settings
    """
    try:
        # Validate the settings
        valid, error_message = await settings_service.validate_settings(settings)
        
        if not valid:
            return {"valid": False, "message": error_message, "code": "validation_error"}
        
        return {"valid": True, "message": "Settings validated successfully"}
    except Exception as e:
        logger.error(f"Error validating settings: {str(e)}")
        return {"valid": False, "message": str(e), "code": "validation_error"}

@router.post("/api/v1/settings")
async def save_settings(settings: Dict[str, str]):
    """
    Save settings
    """
    try:
        # Validate settings before saving
        valid, error_message = await settings_service.validate_settings(settings)
        
        if not valid:
            raise HTTPException(status_code=400, detail={"message": error_message, "code": "validation_error"})
        
        # Save the settings
        await settings_service.save_settings(settings)
        
        # Initialize database if Supabase settings are provided
        if 'SUPABASE_URL' in settings and 'SUPABASE_ANON_KEY' in settings:
            # Test database connection
            if not await db_service.test_connection():
                raise HTTPException(status_code=400, detail={"message": "Failed to connect to Supabase with the provided credentials", "code": "db_connection_error"})
        
        return {"status": "success", "message": "Settings saved successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving settings: {str(e)}")
        raise HTTPException(status_code=500, detail={"message": f"Failed to save settings: {str(e)}", "code": "server_error"})

@router.get("/api/v1/settings")
async def get_settings():
    """
    Get settings
    """
    try:
        # Get the settings
        settings = await settings_service.get_settings()
        
        # Mask sensitive values
        masked_settings = settings.copy()
        for key in masked_settings:
            if key.endswith('_KEY') or key.endswith('_TOKEN') or key.endswith('_SECRET'):
                if masked_settings[key]:
                    masked_settings[key] = '********'
        
        return masked_settings
    except Exception as e:
        logger.error(f"Error getting settings: {str(e)}")
        raise HTTPException(status_code=500, detail={"message": f"Failed to get settings: {str(e)}", "code": "server_error"})

# Database status endpoint
@router.get("/api/v1/database/status")
async def get_database_status():
    """
    Get database connection status
    """
    try:
        # Test database connection
        connection_ok = await db_service.test_connection()
        
        if connection_ok:
            return {"status": "connected"}
        else:
            return {"status": "disconnected"}
    except Exception as e:
        logger.error(f"Error checking database status: {str(e)}")
        return {"status": "error", "message": str(e)}

# Projects endpoints
@router.get("/api/v1/projects")
async def get_projects() -> List[Project]:
    """
    Get all projects
    """
    try:
        return await db_service.get_projects()
    except ValueError as e:
        if "Supabase is not initialized" in str(e):
            raise HTTPException(status_code=400, detail={"message": "Database connection not configured. Please set up Supabase URL and API key in settings.", "code": "db_not_configured"})
        raise HTTPException(status_code=500, detail={"message": str(e), "code": "server_error"})
    except Exception as e:
        logger.error(f"Error getting projects: {str(e)}")
        raise HTTPException(status_code=500, detail={"message": str(e), "code": "server_error"})

@router.get("/api/v1/projects/github")
async def get_github_projects() -> List[Project]:
    """
    Get all GitHub repositories
    """
    try:
        return await github_service.get_repositories()
    except ValueError as e:
        if "GitHub token" in str(e):
            raise HTTPException(status_code=400, detail={"message": "GitHub token not configured. Please set up GitHub token in settings.", "code": "github_not_configured"})
        raise HTTPException(status_code=500, detail={"message": str(e), "code": "server_error"})
    except Exception as e:
        logger.error(f"Error getting GitHub projects: {str(e)}")
        raise HTTPException(status_code=500, detail={"message": str(e), "code": "server_error"})

@router.get("/api/v1/projects/{project_id}")
async def get_project(project_id: str) -> Project:
    """
    Get a project by ID
    """
    try:
        project = await db_service.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail={"message": "Project not found", "code": "not_found"})
        return project
    except ValueError as e:
        if "Supabase is not initialized" in str(e):
            raise HTTPException(status_code=400, detail={"message": "Database connection not configured. Please set up Supabase URL and API key in settings.", "code": "db_not_configured"})
        raise HTTPException(status_code=500, detail={"message": str(e), "code": "server_error"})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project: {str(e)}")
        raise HTTPException(status_code=500, detail={"message": str(e), "code": "server_error"})

# Triggers endpoints
@router.get("/api/v1/triggers")
async def get_triggers(project_id: Optional[str] = None) -> List[Trigger]:
    """
    Get all triggers, optionally filtered by project
    """
    try:
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
    except ValueError as e:
        if "Supabase is not initialized" in str(e):
            raise HTTPException(status_code=400, detail={"message": "Database connection not configured. Please set up Supabase URL and API key in settings.", "code": "db_not_configured"})
        raise HTTPException(status_code=500, detail={"message": str(e), "code": "server_error"})
    except Exception as e:
        logger.error(f"Error getting triggers: {str(e)}")
        raise HTTPException(status_code=500, detail={"message": str(e), "code": "server_error"})

@router.post("/api/v1/triggers")
async def create_trigger(trigger: Trigger) -> Trigger:
    """
    Create a new trigger
    """
    try:
        # Validate project exists
        project = await db_service.get_project(trigger.project_id)
        if not project:
            raise HTTPException(status_code=404, detail={"message": "Project not found", "code": "not_found"})
        
        # Create the trigger
        return await db_service.create_trigger(trigger)
    except ValueError as e:
        if "Supabase is not initialized" in str(e):
            raise HTTPException(status_code=400, detail={"message": "Database connection not configured. Please set up Supabase URL and API key in settings.", "code": "db_not_configured"})
        raise HTTPException(status_code=500, detail={"message": str(e), "code": "server_error"})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating trigger: {str(e)}")
        raise HTTPException(status_code=500, detail={"message": str(e), "code": "server_error"})

@router.get("/api/v1/triggers/{trigger_id}")
async def get_trigger(trigger_id: str) -> Trigger:
    """
    Get a trigger by ID
    """
    try:
        trigger = await db_service.get_trigger(trigger_id)
        if not trigger:
            raise HTTPException(status_code=404, detail={"message": "Trigger not found", "code": "not_found"})
        return trigger
    except ValueError as e:
        if "Supabase is not initialized" in str(e):
            raise HTTPException(status_code=400, detail={"message": "Database connection not configured. Please set up Supabase URL and API key in settings.", "code": "db_not_configured"})
        raise HTTPException(status_code=500, detail={"message": str(e), "code": "server_error"})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trigger: {str(e)}")
        raise HTTPException(status_code=500, detail={"message": str(e), "code": "server_error"})

@router.patch("/api/v1/triggers/{trigger_id}")
async def update_trigger(trigger_id: str, data: Dict[str, Any]) -> Trigger:
    """
    Update a trigger
    """
    try:
        trigger = await db_service.update_trigger(trigger_id, data)
        if not trigger:
            raise HTTPException(status_code=404, detail={"message": "Trigger not found", "code": "not_found"})
        return trigger
    except ValueError as e:
        if "Supabase is not initialized" in str(e):
            raise HTTPException(status_code=400, detail={"message": "Database connection not configured. Please set up Supabase URL and API key in settings.", "code": "db_not_configured"})
        raise HTTPException(status_code=500, detail={"message": str(e), "code": "server_error"})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating trigger: {str(e)}")
        raise HTTPException(status_code=500, detail={"message": str(e), "code": "server_error"})

# Workflows endpoints
@router.get("/api/v1/workflows")
async def get_workflows(repository: str) -> List[Workflow]:
    """
    Get all workflows for a repository
    """
    try:
        owner, repo = repository.split("/")
        return await github_service.get_workflows(owner, repo)
    except ValueError as e:
        if "GitHub token" in str(e):
            raise HTTPException(status_code=400, detail={"message": "GitHub token not configured. Please set up GitHub token in settings.", "code": "github_not_configured"})
        raise HTTPException(status_code=500, detail={"message": str(e), "code": "server_error"})
    except Exception as e:
        logger.error(f"Error getting workflows: {str(e)}")
        raise HTTPException(status_code=500, detail={"message": str(e), "code": "server_error"})

@router.get("/api/v1/workflow_runs")
async def get_workflow_runs(repository: str, workflow_id: Optional[str] = None, limit: int = 10) -> List[WorkflowRun]:
    """
    Get workflow runs for a repository
    """
    try:
        owner, repo = repository.split("/")
        return await github_service.get_workflow_runs(owner, repo, workflow_id, limit)
    except ValueError as e:
        if "GitHub token" in str(e):
            raise HTTPException(status_code=400, detail={"message": "GitHub token not configured. Please set up GitHub token in settings.", "code": "github_not_configured"})
        raise HTTPException(status_code=500, detail={"message": str(e), "code": "server_error"})
    except Exception as e:
        logger.error(f"Error getting workflow runs: {str(e)}")
        raise HTTPException(status_code=500, detail={"message": str(e), "code": "server_error"})

@router.post("/api/v1/workflows/{workflow_id}/dispatch")
async def trigger_workflow(workflow_id: str, repository: str, ref: Optional[str] = None, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Trigger a workflow
    """
    try:
        owner, repo = repository.split("/")
        success = await github_service.trigger_workflow(owner, repo, workflow_id, ref, inputs)
        
        if not success:
            raise HTTPException(status_code=500, detail={"message": "Failed to trigger workflow", "code": "workflow_error"})
        
        return {"status": "triggered"}
    except ValueError as e:
        if "GitHub token" in str(e):
            raise HTTPException(status_code=400, detail={"message": "GitHub token not configured. Please set up GitHub token in settings.", "code": "github_not_configured"})
        raise HTTPException(status_code=500, detail={"message": str(e), "code": "server_error"})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering workflow: {str(e)}")
        raise HTTPException(status_code=500, detail={"message": str(e), "code": "server_error"})

# Events endpoints
@router.get("/api/v1/events")
async def get_events(repository: Optional[str] = None, limit: int = 10) -> List[Event]:
    """
    Get recent events
    """
    try:
        return await event_service.get_recent_events(repository, limit)
    except ValueError as e:
        if "Supabase is not initialized" in str(e):
            raise HTTPException(status_code=400, detail={"message": "Database connection not configured. Please set up Supabase URL and API key in settings.", "code": "db_not_configured"})
        raise HTTPException(status_code=500, detail={"message": str(e), "code": "server_error"})
    except Exception as e:
        logger.error(f"Error getting events: {str(e)}")
        raise HTTPException(status_code=500, detail={"message": str(e), "code": "server_error"})

# Execute code endpoint
@router.post("/api/v1/execute_code")
async def execute_code(code: str, repository: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute Python code
    """
    try:
        success = await workflow_service.execute_python_code(code, repository, event_data)
        
        if not success:
            raise HTTPException(status_code=500, detail={"message": "Failed to execute code", "code": "execution_error"})
        
        return {"status": "executed"}
    except Exception as e:
        logger.error(f"Error executing code: {str(e)}")
        raise HTTPException(status_code=500, detail={"message": str(e), "code": "server_error"})
