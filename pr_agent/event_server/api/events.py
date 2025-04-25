"""
API endpoints for handling GitHub events.
"""

import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response
from pydantic import BaseModel

from pr_agent.log import get_logger

from ..db.models import Event, EventType
from ..db.sqlite import SQLiteDB

router = APIRouter()
logger = get_logger()


class EventResponse(BaseModel):
    """Response model for event endpoints."""
    success: bool
    message: str
    event_id: Optional[str] = None


async def get_db():
    """Get database connection."""
    db_path = os.environ.get("SQLITE_PATH", "./data/events.db")
    return SQLiteDB(db_path)


@router.post("/api/v1/events", response_model=EventResponse)
async def handle_github_webhook(
    background_tasks: BackgroundTasks,
    request: Request,
    db: SQLiteDB = Depends(get_db)
):
    """Handle GitHub webhook events.
    
    Args:
        background_tasks: FastAPI background tasks.
        request: FastAPI request.
        db: Database connection.
        
    Returns:
        Response with event ID.
    """
    try:
        # Parse the request body
        body = await request.json()
        
        # Get the event type from the headers
        event_type = request.headers.get("X-GitHub-Event", "unknown")
        
        # Process the event
        return await process_github_event(background_tasks, event_type, body, db)
    except Exception as e:
        logger.error(f"Error handling GitHub webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Error handling webhook: {str(e)}")


@router.post("/api/v1/events/manual", response_model=EventResponse)
async def handle_manual_event(
    background_tasks: BackgroundTasks,
    event_type: str,
    event_data: Dict[str, Any],
    db: SQLiteDB = Depends(get_db)
):
    """Handle manually triggered events.
    
    Args:
        background_tasks: FastAPI background tasks.
        event_type: Type of the event.
        event_data: Event data.
        db: Database connection.
        
    Returns:
        Response with event ID.
    """
    try:
        # Process the event
        return await process_github_event(background_tasks, event_type, event_data, db)
    except Exception as e:
        logger.error(f"Error handling manual event: {e}")
        raise HTTPException(status_code=500, detail=f"Error handling event: {str(e)}")


@router.get("/api/v1/events", response_model=List[Event])
async def get_events(
    repository: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: SQLiteDB = Depends(get_db)
):
    """Get events with optional filtering.
    
    Args:
        repository: Filter by repository.
        event_type: Filter by event type.
        limit: Maximum number of events to return.
        offset: Offset for pagination.
        db: Database connection.
        
    Returns:
        List of events.
    """
    try:
        return db.get_events(repository, event_type, limit, offset)
    except Exception as e:
        logger.error(f"Error getting events: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting events: {str(e)}")


@router.get("/api/v1/events/{event_id}", response_model=Event)
async def get_event(
    event_id: str,
    db: SQLiteDB = Depends(get_db)
):
    """Get an event by ID.
    
    Args:
        event_id: ID of the event to get.
        db: Database connection.
        
    Returns:
        Event if found.
    """
    try:
        event = db.get_event(event_id)
        if not event:
            raise HTTPException(status_code=404, detail=f"Event {event_id} not found")
        return event
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting event {event_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting event: {str(e)}")


async def process_github_event(
    background_tasks: BackgroundTasks,
    event_type: str,
    event_data: Dict[str, Any],
    db: SQLiteDB
) -> EventResponse:
    """Process a GitHub event.
    
    Args:
        background_tasks: FastAPI background tasks.
        event_type: Type of the event.
        event_data: Event data.
        db: Database connection.
        
    Returns:
        Response with event ID.
    """
    try:
        # Map GitHub event type to our EventType enum
        try:
            mapped_event_type = EventType(event_type)
        except ValueError:
            mapped_event_type = EventType.OTHER
        
        # Extract repository name
        repository = extract_repository_name(event_data)
        
        # Extract action
        action = event_data.get("action")
        
        # Extract sender
        sender = extract_sender_name(event_data)
        
        # Create event object
        event = Event(
            type=mapped_event_type,
            action=action,
            repository=repository,
            sender=sender,
            data=event_data
        )
        
        # Store the event in the database
        event_id = db.create_event(event)
        
        # Process triggers in the background
        background_tasks.add_task(process_event_triggers, event, db)
        
        return EventResponse(
            success=True,
            message=f"Event {event_type} processed successfully",
            event_id=event_id
        )
    except Exception as e:
        logger.error(f"Error processing GitHub event: {e}")
        return EventResponse(
            success=False,
            message=f"Error processing event: {str(e)}"
        )


def extract_repository_name(event_data: Dict[str, Any]) -> str:
    """Extract repository name from event data.
    
    Args:
        event_data: Event data.
        
    Returns:
        Repository name.
    """
    if "repository" in event_data and "full_name" in event_data["repository"]:
        return event_data["repository"]["full_name"]
    return "unknown"


def extract_sender_name(event_data: Dict[str, Any]) -> Optional[str]:
    """Extract sender name from event data.
    
    Args:
        event_data: Event data.
        
    Returns:
        Sender name if available.
    """
    if "sender" in event_data and "login" in event_data["sender"]:
        return event_data["sender"]["login"]
    return None


async def process_event_triggers(event: Event, db: SQLiteDB):
    """Process triggers for an event.
    
    Args:
        event: Event to process triggers for.
        db: Database connection.
    """
    from ..execution.action_executor import ActionExecutor
    from ..execution.code_executor import CodeExecutor
    from ..execution.command_executor import CommandExecutor
    from ..notification.windows import WindowsNotifier
    
    try:
        # Get matching triggers
        triggers = db.get_matching_triggers(event)
        
        if not triggers:
            logger.info(f"No matching triggers found for event {event.id}")
            return
        
        logger.info(f"Found {len(triggers)} matching triggers for event {event.id}")
        
        # Initialize executors
        code_executor = CodeExecutor()
        command_executor = CommandExecutor()
        action_executor = ActionExecutor()
        
        # Initialize notifier
        notifier = WindowsNotifier()
        
        # Process each trigger
        for trigger in triggers:
            try:
                # Execute the trigger based on its type
                if trigger.execution_type == "codefile":
                    execution = code_executor.execute_trigger(trigger, event)
                elif trigger.execution_type == "github_action":
                    execution = action_executor.execute_trigger(trigger, event)
                elif trigger.execution_type == "pr_agent_command":
                    execution = command_executor.execute_trigger(trigger, event)
                else:
                    logger.error(f"Unknown execution type: {trigger.execution_type}")
                    continue
                
                # Store the execution in the database
                db.create_execution(execution)
                
                # Send notification if enabled
                if trigger.notifications.get("windows", False):
                    notifier.send_trigger_notification(
                        trigger.name,
                        event.type.value,
                        event.repository,
                        execution.status.value
                    )
            except Exception as e:
                logger.error(f"Error executing trigger {trigger.id}: {e}")
    except Exception as e:
        logger.error(f"Error processing triggers for event {event.id}: {e}")
