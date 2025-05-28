from fastapi import APIRouter, Depends, HTTPException, Request, Response, BackgroundTasks
from typing import Dict, Any, List, Optional
import json
import uuid
import logging
from functools import lru_cache

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
from pr_agent.log.enhanced_logging import structured_log

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1")

# Service dependency functions
@lru_cache()
def get_settings_service():
    """Get the settings service instance"""
    from pr_agent.execserver.app import settings_service
    return settings_service

@lru_cache()
def get_db_service():
    """Get the database service instance"""
    from pr_agent.execserver.app import db_service
    return db_service

@lru_cache()
def get_github_service():
    """Get the GitHub service instance"""
    from pr_agent.execserver.app import github_service
    return github_service

@lru_cache()
def get_workflow_service():
    """Get the workflow service instance"""
    from pr_agent.execserver.app import workflow_service
    return workflow_service

@lru_cache()
def get_event_service():
    """Get the event service instance"""
    from pr_agent.execserver.app import event_service
    return event_service

# Standard error response function
def create_error_response(status_code: int, message: str, code: str = None, details: Dict = None):
    """Create a standardized error response"""
    error_response = {
        "message": message,
    }
    
    if code:
        error_response["code"] = code
    
    if details:
        error_response["details"] = details
    
    # Log the error
    structured_log(
        f"API Error: {message}",
        level="error",
        status_code=status_code,
        error_code=code,
        details=details
    )
    
    raise HTTPException(status_code=status_code, detail=error_response)

# GitHub webhook endpoint
@router.post("/github_webhooks")
async def handle_github_webhooks(
    background_tasks: BackgroundTasks, 
    request: Request, 
    response: Response,
    event_service: EventService = Depends(get_event_service)
):
    """
    Handle GitHub webhook events
    """
    try:
        # Get the request body
        body = await request.json()
        
        # Verify the webhook signature
        github_secret = get_setting_or_env("GITHUB_WEBHOOK_SECRET")
        if github_secret:
            signature = request.headers.get("X-Hub-Signature-256")
            if not signature:
                return create_error_response(401, "Missing signature header", "missing_signature")
            
            if not verify_signature(await request.body(), signature, github_secret):
                return create_error_response(401, "Invalid signature", "invalid_signature")
        
        # Get the event type
        event_type = request.headers.get("X-GitHub-Event")
        if not event_type:
            return create_error_response(400, "Missing event type header", "missing_event_type")
        
        # Process the webhook in the background using both PR-Agent's handler and our custom handler
        background_tasks.add_task(pr_agent_handle_github_webhooks, background_tasks, request, response)
        background_tasks.add_task(event_service.process_webhook, event_type, body)
        
        return {"status": "processing"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling GitHub webhook: {str(e)}")
        return create_error_response(500, f"Failed to process webhook: {str(e)}", "server_error")

# Settings endpoints
@router.post("/settings/validate")
async def validate_settings(
    settings: Dict[str, str],
    settings_service: SettingsService = Depends(get_settings_service)
):
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

@router.post("/settings")
async def save_settings(
    settings: Dict[str, str],
    settings_service: SettingsService = Depends(get_settings_service),
    db_service: DatabaseService = Depends(get_db_service)
):
    """
    Save settings
    """
    try:
        # Validate settings before saving
        valid, error_message = await settings_service.validate_settings(settings)
        
        if not valid:
            return create_error_response(400, error_message, "validation_error")
        
        # Save the settings
        await settings_service.save_settings(settings)
        
        # Initialize database if Supabase settings are provided
        if 'SUPABASE_URL' in settings and 'SUPABASE_ANON_KEY' in settings:
            # Test database connection
            if not await db_service.test_connection():
                return create_error_response(
                    400, 
                    "Failed to connect to Supabase with the provided credentials", 
                    "db_connection_error"
                )
            
            # Get connection status for detailed error message
            connection_status = await db_service.get_connection_status()
            if not connection_status["connected"] and connection_status["error"]:
                return create_error_response(
                    400, 
                    connection_status["error"], 
                    "db_connection_error"
                )
        
        return {"status": "success", "message": "Settings saved successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving settings: {str(e)}")
        return create_error_response(500, f"Failed to save settings: {str(e)}", "server_error")

@router.get("/settings")
async def get_settings(
    settings_service: SettingsService = Depends(get_settings_service)
):
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
        return create_error_response(500, f"Failed to get settings: {str(e)}", "server_error")

# Database status endpoint
@router.get("/database/status")
async def get_database_status(
    db_service: DatabaseService = Depends(get_db_service)
):
    """
    Get database connection status
    """
    try:
        # Get detailed connection status
        connection_status = await db_service.get_connection_status()
        
        if connection_status["connected"]:
            return {"status": "connected"}
        else:
            return {
                "status": "disconnected", 
                "error": connection_status["error"] or "Unknown error"
            }
    except Exception as e:
        logger.error(f"Error checking database status: {str(e)}")
        return {"status": "error", "message": str(e)}

# Database migration status endpoint
@router.get("/database/migrations")
async def get_migration_status(
    db_service: DatabaseService = Depends(get_db_service)
):
    """
    Get database migration status
    """
    try:
        # Check if database is connected
        connection_status = await db_service.get_connection_status()
        if not connection_status["connected"]:
            return {
                "status": "error",
                "message": "Database not connected",
                "error": connection_status["error"] or "Unknown error"
            }
        
        # Get migration status
        if db_service.migration_service:
            migration_status = await db_service.migration_service.get_migration_status()
            return {
                "status": "success",
                "migrations": migration_status
            }
        else:
            return {
                "status": "error",
                "message": "Migration service not initialized"
            }
    except Exception as e:
        logger.error(f"Error checking migration status: {str(e)}")
        return {"status": "error", "message": str(e)}

# Apply migrations endpoint
@router.post("/database/migrations/apply")
async def apply_migrations(
    db_service: DatabaseService = Depends(get_db_service)
):
    """
    Apply pending database migrations
    """
    try:
        # Check if database is connected
        connection_status = await db_service.get_connection_status()
        if not connection_status["connected"]:
            return create_error_response(
                400, 
                "Database not connected", 
                "db_connection_error",
                {"error": connection_status["error"] or "Unknown error"}
            )
        
        # Apply migrations
        if db_service.migration_service:
            success, applied, failed = await db_service.migration_service.apply_migrations()
            
            if success:
                return {
                    "status": "success",
                    "message": f"Successfully applied {len(applied)} migrations",
                    "applied": applied,
                    "failed": failed
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to apply migrations. Applied: {len(applied)}, Failed: {len(failed)}",
                    "applied": applied,
                    "failed": failed
                }
        else:
            return create_error_response(400, "Migration service not initialized", "migration_service_error")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error applying migrations: {str(e)}")
        return create_error_response(500, f"Failed to apply migrations: {str(e)}", "server_error")

# Projects endpoints
@router.get("/projects")
async def get_projects(
    db_service: DatabaseService = Depends(get_db_service)
) -> List[Project]:
    """
    Get all projects
    """
    try:
        return await db_service.get_projects()
    except ValueError as e:
        if "Supabase is not initialized" in str(e):
            return create_error_response(
                400, 
                "Database connection not configured. Please set up Supabase URL and API key in settings.", 
                "db_not_configured"
            )
        return create_error_response(500, str(e), "server_error")
    except Exception as e:
        logger.error(f"Error getting projects: {str(e)}")
        return create_error_response(500, str(e), "server_error")

@router.get("/projects/github")
async def get_github_projects(
    github_service: GitHubService = Depends(get_github_service)
) -> List[Project]:
    """
    Get all GitHub repositories
    """
    try:
        return await github_service.get_repositories()
    except ValueError as e:
        if "GitHub token" in str(e):
            return create_error_response(
                400, 
                "GitHub token not configured. Please set up GitHub token in settings.", 
                "github_not_configured"
            )
        return create_error_response(500, str(e), "server_error")
    except Exception as e:
        logger.error(f"Error getting GitHub projects: {str(e)}")
        return create_error_response(500, str(e), "server_error")

@router.get("/projects/{project_id}")
async def get_project(
    project_id: str,
    db_service: DatabaseService = Depends(get_db_service)
) -> Project:
    """
    Get a project by ID
    """
    try:
        project = await db_service.get_project(project_id)
        if not project:
            return create_error_response(404, "Project not found", "not_found")
        return project
    except ValueError as e:
        if "Supabase is not initialized" in str(e):
            return create_error_response(
                400, 
                "Database connection not configured. Please set up Supabase URL and API key in settings.", 
                "db_not_configured"
            )
        return create_error_response(500, str(e), "server_error")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project: {str(e)}")
        return create_error_response(500, str(e), "server_error")

# Triggers endpoints
@router.get("/triggers")
async def get_triggers(
    project_id: Optional[str] = None,
    db_service: DatabaseService = Depends(get_db_service)
) -> List[Trigger]:
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
            return create_error_response(
                400, 
                "Database connection not configured. Please set up Supabase URL and API key in settings.", 
                "db_not_configured"
            )
        return create_error_response(500, str(e), "server_error")
    except Exception as e:
        logger.error(f"Error getting triggers: {str(e)}")
        return create_error_response(500, str(e), "server_error")

@router.post("/triggers")
async def create_trigger(
    trigger: Trigger,
    db_service: DatabaseService = Depends(get_db_service)
) -> Trigger:
    """
    Create a new trigger
    """
    try:
        # Validate project exists
        project = await db_service.get_project(trigger.project_id)
        if not project:
            return create_error_response(404, "Project not found", "not_found")
        
        # Create the trigger
        return await db_service.create_trigger(trigger)
    except ValueError as e:
        if "Supabase is not initialized" in str(e):
            return create_error_response(
                400, 
                "Database connection not configured. Please set up Supabase URL and API key in settings.", 
                "db_not_configured"
            )
        return create_error_response(500, str(e), "server_error")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating trigger: {str(e)}")
        return create_error_response(500, str(e), "server_error")

@router.get("/triggers/{trigger_id}")
async def get_trigger(
    trigger_id: str,
    db_service: DatabaseService = Depends(get_db_service)
) -> Trigger:
    """
    Get a trigger by ID
    """
    try:
        trigger = await db_service.get_trigger(trigger_id)
        if not trigger:
            return create_error_response(404, "Trigger not found", "not_found")
        return trigger
    except ValueError as e:
        if "Supabase is not initialized" in str(e):
            return create_error_response(
                400, 
                "Database connection not configured. Please set up Supabase URL and API key in settings.", 
                "db_not_configured"
            )
        return create_error_response(500, str(e), "server_error")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trigger: {str(e)}")
        return create_error_response(500, str(e), "server_error")

@router.patch("/triggers/{trigger_id}")
async def update_trigger(
    trigger_id: str, 
    data: Dict[str, Any],
    db_service: DatabaseService = Depends(get_db_service)
) -> Trigger:
    """
    Update a trigger
    """
    try:
        trigger = await db_service.update_trigger(trigger_id, data)
        if not trigger:
            return create_error_response(404, "Trigger not found", "not_found")
        return trigger
    except ValueError as e:
        if "Supabase is not initialized" in str(e):
            return create_error_response(
                400, 
                "Database connection not configured. Please set up Supabase URL and API key in settings.", 
                "db_not_configured"
            )
        return create_error_response(500, str(e), "server_error")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating trigger: {str(e)}")
        return create_error_response(500, str(e), "server_error")

# Workflows endpoints
@router.get("/workflows")
async def get_workflows(
    repository: str,
    github_service: GitHubService = Depends(get_github_service)
) -> List[Workflow]:
    """
    Get all workflows for a repository
    """
    try:
        owner, repo = repository.split("/")
        return await github_service.get_workflows(owner, repo)
    except ValueError as e:
        if "GitHub token" in str(e):
            return create_error_response(
                400, 
                "GitHub token not configured. Please set up GitHub token in settings.", 
                "github_not_configured"
            )
        return create_error_response(500, str(e), "server_error")
    except Exception as e:
        logger.error(f"Error getting workflows: {str(e)}")
        return create_error_response(500, str(e), "server_error")

@router.get("/workflow_runs")
async def get_workflow_runs(
    repository: str, 
    workflow_id: Optional[str] = None, 
    limit: int = 10,
    github_service: GitHubService = Depends(get_github_service)
) -> List[WorkflowRun]:
    """
    Get workflow runs for a repository
    """
    try:
        owner, repo = repository.split("/")
        return await github_service.get_workflow_runs(owner, repo, workflow_id, limit)
    except ValueError as e:
        if "GitHub token" in str(e):
            return create_error_response(
                400, 
                "GitHub token not configured. Please set up GitHub token in settings.", 
                "github_not_configured"
            )
        return create_error_response(500, str(e), "server_error")
    except Exception as e:
        logger.error(f"Error getting workflow runs: {str(e)}")
        return create_error_response(500, str(e), "server_error")

@router.post("/workflows/{workflow_id}/dispatch")
async def trigger_workflow(
    workflow_id: str, 
    repository: str, 
    ref: Optional[str] = None, 
    inputs: Optional[Dict[str, Any]] = None,
    github_service: GitHubService = Depends(get_github_service)
) -> Dict[str, Any]:
    """
    Trigger a workflow
    """
    try:
        owner, repo = repository.split("/")
        success = await github_service.trigger_workflow(owner, repo, workflow_id, ref, inputs)
        
        if not success:
            return create_error_response(500, "Failed to trigger workflow", "workflow_error")
        
        return {"status": "triggered"}
    except ValueError as e:
        if "GitHub token" in str(e):
            return create_error_response(
                400, 
                "GitHub token not configured. Please set up GitHub token in settings.", 
                "github_not_configured"
            )
        return create_error_response(500, str(e), "server_error")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering workflow: {str(e)}")
        return create_error_response(500, str(e), "server_error")

# Events endpoints
@router.get("/events")
async def get_events(
    repository: Optional[str] = None, 
    limit: int = 10,
    event_service: EventService = Depends(get_event_service)
) -> List[Event]:
    """
    Get recent events
    """
    try:
        return await event_service.get_recent_events(repository, limit)
    except ValueError as e:
        if "Supabase is not initialized" in str(e):
            return create_error_response(
                400, 
                "Database connection not configured. Please set up Supabase URL and API key in settings.", 
                "db_not_configured"
            )
        return create_error_response(500, str(e), "server_error")
    except Exception as e:
        logger.error(f"Error getting events: {str(e)}")
        return create_error_response(500, str(e), "server_error")

# Execute code endpoint
@router.post("/execute_code")
async def execute_code(
    code: str, 
    repository: str, 
    event_data: Dict[str, Any],
    workflow_service: WorkflowService = Depends(get_workflow_service)
) -> Dict[str, Any]:
    """
    Execute Python code
    """
    try:
        success = await workflow_service.execute_python_code(code, repository, event_data)
        
        if not success:
            return create_error_response(500, "Failed to execute code", "execution_error")
        
        return {"status": "executed"}
    except Exception as e:
        logger.error(f"Error executing code: {str(e)}")
        return create_error_response(500, str(e), "server_error")

