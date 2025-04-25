"""
Simple web dashboard for the Event Server Executor.
"""

import os
from typing import List, Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pr_agent.log import get_logger

from ..db.models import Event, Execution, Trigger
from ..db.sqlite import SQLiteDB
from ..api.events import get_db

router = APIRouter()
logger = get_logger()

# Set up templates
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)

# Set up static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
router.mount("/static", StaticFiles(directory=static_dir), name="static")


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: SQLiteDB = Depends(get_db)
):
    """Dashboard home page.
    
    Args:
        request: FastAPI request.
        db: Database connection.
        
    Returns:
        HTML response.
    """
    # Get recent events
    events = db.get_events(limit=10)
    
    # Get active triggers
    triggers = db.get_triggers(enabled=True)
    
    # Get recent executions
    executions = db.get_executions(limit=10)
    
    # Render template
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "events": events,
            "triggers": triggers,
            "executions": executions
        }
    )


@router.get("/dashboard/events", response_class=HTMLResponse)
async def events_page(
    request: Request,
    repository: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: SQLiteDB = Depends(get_db)
):
    """Events page.
    
    Args:
        request: FastAPI request.
        repository: Filter by repository.
        event_type: Filter by event type.
        limit: Maximum number of events to return.
        offset: Offset for pagination.
        db: Database connection.
        
    Returns:
        HTML response.
    """
    # Get events
    events = db.get_events(repository, event_type, limit, offset)
    
    # Render template
    return templates.TemplateResponse(
        "events.html",
        {
            "request": request,
            "events": events,
            "repository": repository,
            "event_type": event_type,
            "limit": limit,
            "offset": offset
        }
    )


@router.get("/dashboard/triggers", response_class=HTMLResponse)
async def triggers_page(
    request: Request,
    repository: Optional[str] = None,
    event_type: Optional[str] = None,
    enabled: Optional[bool] = None,
    db: SQLiteDB = Depends(get_db)
):
    """Triggers page.
    
    Args:
        request: FastAPI request.
        repository: Filter by repository.
        event_type: Filter by event type.
        enabled: Filter by enabled status.
        db: Database connection.
        
    Returns:
        HTML response.
    """
    # Get triggers
    triggers = db.get_triggers(repository, event_type, enabled)
    
    # Render template
    return templates.TemplateResponse(
        "triggers.html",
        {
            "request": request,
            "triggers": triggers,
            "repository": repository,
            "event_type": event_type,
            "enabled": enabled
        }
    )


@router.get("/dashboard/executions", response_class=HTMLResponse)
async def executions_page(
    request: Request,
    event_id: Optional[str] = None,
    trigger_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: SQLiteDB = Depends(get_db)
):
    """Executions page.
    
    Args:
        request: FastAPI request.
        event_id: Filter by event ID.
        trigger_id: Filter by trigger ID.
        status: Filter by status.
        limit: Maximum number of executions to return.
        offset: Offset for pagination.
        db: Database connection.
        
    Returns:
        HTML response.
    """
    # Get executions
    executions = db.get_executions(event_id, trigger_id, status, limit, offset)
    
    # Render template
    return templates.TemplateResponse(
        "executions.html",
        {
            "request": request,
            "executions": executions,
            "event_id": event_id,
            "trigger_id": trigger_id,
            "status": status,
            "limit": limit,
            "offset": offset
        }
    )


@router.get("/dashboard/event/{event_id}", response_class=HTMLResponse)
async def event_detail(
    request: Request,
    event_id: str,
    db: SQLiteDB = Depends(get_db)
):
    """Event detail page.
    
    Args:
        request: FastAPI request.
        event_id: ID of the event to view.
        db: Database connection.
        
    Returns:
        HTML response.
    """
    # Get event
    event = db.get_event(event_id)
    if not event:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "message": f"Event {event_id} not found"
            }
        )
    
    # Get executions for this event
    executions = db.get_executions(event_id=event_id)
    
    # Render template
    return templates.TemplateResponse(
        "event_detail.html",
        {
            "request": request,
            "event": event,
            "executions": executions
        }
    )


@router.get("/dashboard/trigger/{trigger_id}", response_class=HTMLResponse)
async def trigger_detail(
    request: Request,
    trigger_id: str,
    db: SQLiteDB = Depends(get_db)
):
    """Trigger detail page.
    
    Args:
        request: FastAPI request.
        trigger_id: ID of the trigger to view.
        db: Database connection.
        
    Returns:
        HTML response.
    """
    # Get trigger
    trigger = db.get_trigger(trigger_id)
    if not trigger:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "message": f"Trigger {trigger_id} not found"
            }
        )
    
    # Get executions for this trigger
    executions = db.get_executions(trigger_id=trigger_id)
    
    # Render template
    return templates.TemplateResponse(
        "trigger_detail.html",
        {
            "request": request,
            "trigger": trigger,
            "executions": executions
        }
    )


@router.get("/dashboard/execution/{execution_id}", response_class=HTMLResponse)
async def execution_detail(
    request: Request,
    execution_id: str,
    db: SQLiteDB = Depends(get_db)
):
    """Execution detail page.
    
    Args:
        request: FastAPI request.
        execution_id: ID of the execution to view.
        db: Database connection.
        
    Returns:
        HTML response.
    """
    # Get execution
    execution = db.get_execution(execution_id)
    if not execution:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "message": f"Execution {execution_id} not found"
            }
        )
    
    # Get event and trigger
    event = db.get_event(execution.event_id)
    trigger = db.get_trigger(execution.trigger_id)
    
    # Get notifications for this execution
    notifications = db.get_notifications(execution_id=execution_id)
    
    # Render template
    return templates.TemplateResponse(
        "execution_detail.html",
        {
            "request": request,
            "execution": execution,
            "event": event,
            "trigger": trigger,
            "notifications": notifications
        }
    )
