"""
API routes for the ExeServer.

This module defines the API routes for the ExeServer, including endpoints for
events, triggers, workflows, and other functionality.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import List, Optional, Dict, Any
import logging

from ..models.event import Event
from ..models.project import Project
from ..models.trigger import Trigger
from ..models.workflow import Workflow, WorkflowRun
from ..services.db_service import DatabaseService
from ..config import is_supabase_configured, get_supabase_url, get_supabase_anon_key, save_config

# Create router
router = APIRouter(prefix="/v1")

# Initialize services
db_service = DatabaseService()

logger = logging.getLogger(__name__)

# Settings endpoints
@router.get("/settings/supabase")
async def get_supabase_settings():
    """Get Supabase connection settings and status"""
    return {
        "is_configured": is_supabase_configured(),
        "connection_status": db_service.get_connection_status()
    }

@router.post("/settings/supabase/validate")
async def validate_supabase_settings(settings: Dict[str, str] = Body(...)):
    """Validate Supabase connection settings"""
    url = settings.get("url")
    key = settings.get("key")
    
    if not url or not key:
        raise HTTPException(status_code=400, detail="URL and key are required")
    
    result = db_service.validate_connection(url, key)
    return result

@router.post("/settings/supabase/save")
async def save_supabase_settings(settings: Dict[str, str] = Body(...)):
    """Save Supabase connection settings"""
    url = settings.get("url")
    key = settings.get("key")
    
    if not url or not key:
        raise HTTPException(status_code=400, detail="URL and key are required")
    
    # Save to environment
    save_config("SUPABASE_URL", url)
    save_config("SUPABASE_ANON_KEY", key)
    
    # Update database service
    result = db_service.update_credentials(url, key)
    
    return {
        "success": result["is_connected"],
        "message": "Settings saved successfully" if result["is_connected"] else f"Failed to connect: {result['error']}",
        "connection_status": result
    }

# Event endpoints
@router.get("/events", response_model=List[Event])
async def get_events(
    repository: Optional[str] = None,
    processed: Optional[bool] = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get events with optional filtering"""
    try:
        events = await db_service.get_events(repository, processed, limit, offset)
        return events
    except ValueError as e:
        if "Database not connected" in str(e):
            return []
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events/{event_id}", response_model=Event)
async def get_event(event_id: str):
    """Get an event by ID"""
    try:
        event = await db_service.get_event(event_id)
        if not event:
            raise HTTPException(status_code=404, detail=f"Event with ID {event_id} not found")
        return event
    except ValueError as e:
        if "Database not connected" in str(e):
            raise HTTPException(status_code=503, detail="Database not connected")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting event {event_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/events/{event_id}/process")
async def process_event(event_id: str):
    """Mark an event as processed"""
    try:
        event = await db_service.mark_event_processed(event_id)
        return {"success": True, "event": event}
    except ValueError as e:
        if "Database not connected" in str(e):
            raise HTTPException(status_code=503, detail="Database not connected")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing event {event_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Project endpoints
@router.get("/projects", response_model=List[Project])
async def get_projects():
    """Get all projects"""
    try:
        projects = await db_service.get_projects()
        return projects
    except ValueError as e:
        if "Database not connected" in str(e):
            return []
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str):
    """Get a project by ID"""
    try:
        project = await db_service.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")
        return project
    except ValueError as e:
        if "Database not connected" in str(e):
            raise HTTPException(status_code=503, detail="Database not connected")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/projects", response_model=Project)
async def create_project(project: Project):
    """Create a new project"""
    try:
        created_project = await db_service.create_project(project)
        return created_project
    except ValueError as e:
        if "Database not connected" in str(e):
            raise HTTPException(status_code=503, detail="Database not connected")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Trigger endpoints
@router.get("/triggers", response_model=List[Trigger])
async def get_triggers(project_id: Optional[str] = None):
    """Get triggers with optional filtering by project"""
    try:
        if project_id:
            triggers = await db_service.get_triggers_for_project(project_id)
        else:
            # This is a placeholder - we would need to implement a method to get all triggers
            triggers = []
        return triggers
    except ValueError as e:
        if "Database not connected" in str(e):
            return []
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting triggers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/triggers/{trigger_id}", response_model=Trigger)
async def get_trigger(trigger_id: str):
    """Get a trigger by ID"""
    try:
        trigger = await db_service.get_trigger(trigger_id)
        if not trigger:
            raise HTTPException(status_code=404, detail=f"Trigger with ID {trigger_id} not found")
        return trigger
    except ValueError as e:
        if "Database not connected" in str(e):
            raise HTTPException(status_code=503, detail="Database not connected")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting trigger {trigger_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/triggers", response_model=Trigger)
async def create_trigger(trigger: Trigger):
    """Create a new trigger"""
    try:
        created_trigger = await db_service.create_trigger(trigger)
        return created_trigger
    except ValueError as e:
        if "Database not connected" in str(e):
            raise HTTPException(status_code=503, detail="Database not connected")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating trigger: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/triggers/{trigger_id}", response_model=Trigger)
async def update_trigger(trigger_id: str, data: Dict[str, Any]):
    """Update a trigger"""
    try:
        updated_trigger = await db_service.update_trigger(trigger_id, data)
        if not updated_trigger:
            raise HTTPException(status_code=404, detail=f"Trigger with ID {trigger_id} not found")
        return updated_trigger
    except ValueError as e:
        if "Database not connected" in str(e):
            raise HTTPException(status_code=503, detail="Database not connected")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating trigger {trigger_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Workflow endpoints
@router.get("/workflows", response_model=List[Workflow])
async def get_workflows(repository: Optional[str] = None):
    """Get workflows with optional filtering by repository"""
    try:
        if repository:
            workflows = await db_service.get_workflows_for_repository(repository)
        else:
            # This is a placeholder - we would need to implement a method to get all workflows
            workflows = []
        return workflows
    except ValueError as e:
        if "Database not connected" in str(e):
            return []
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting workflows: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workflows/{workflow_id}", response_model=Workflow)
async def get_workflow(workflow_id: str):
    """Get a workflow by ID"""
    try:
        workflow = await db_service.get_workflow(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail=f"Workflow with ID {workflow_id} not found")
        return workflow
    except ValueError as e:
        if "Database not connected" in str(e):
            raise HTTPException(status_code=503, detail="Database not connected")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting workflow {workflow_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workflows", response_model=Workflow)
async def create_workflow(workflow: Workflow):
    """Create a new workflow"""
    try:
        created_workflow = await db_service.create_workflow(workflow)
        return created_workflow
    except ValueError as e:
        if "Database not connected" in str(e):
            raise HTTPException(status_code=503, detail="Database not connected")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workflow-runs", response_model=List[WorkflowRun])
async def get_workflow_runs(
    workflow_id: Optional[str] = None,
    repository: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get workflow runs with optional filtering"""
    try:
        runs = await db_service.get_workflow_runs(workflow_id, repository, limit, offset)
        return runs
    except ValueError as e:
        if "Database not connected" in str(e):
            return []
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting workflow runs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workflow-runs", response_model=WorkflowRun)
async def create_workflow_run(workflow_run: WorkflowRun):
    """Create a new workflow run"""
    try:
        created_run = await db_service.create_workflow_run(workflow_run)
        return created_run
    except ValueError as e:
        if "Database not connected" in str(e):
            raise HTTPException(status_code=503, detail="Database not connected")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating workflow run: {e}")
        raise HTTPException(status_code=500, detail=str(e))
