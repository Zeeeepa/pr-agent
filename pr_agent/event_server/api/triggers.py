"""
API endpoints for managing triggers.
"""

import os
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from pr_agent.log import get_logger

from ..db.models import EventType, ExecutionType, Trigger
from ..db.sqlite import SQLiteDB
from .events import get_db

router = APIRouter()
logger = get_logger()


class TriggerResponse(BaseModel):
    """Response model for trigger endpoints."""
    success: bool
    message: str
    trigger_id: Optional[str] = None


@router.post("/api/v1/triggers", response_model=TriggerResponse)
async def create_trigger(
    trigger: Trigger,
    db: SQLiteDB = Depends(get_db)
):
    """Create a new trigger.
    
    Args:
        trigger: Trigger to create.
        db: Database connection.
        
    Returns:
        Response with trigger ID.
    """
    try:
        # Update timestamps
        trigger.created_at = datetime.now()
        trigger.updated_at = datetime.now()
        
        # Create the trigger
        trigger_id = db.create_trigger(trigger)
        
        return TriggerResponse(
            success=True,
            message="Trigger created successfully",
            trigger_id=trigger_id
        )
    except Exception as e:
        logger.error(f"Error creating trigger: {e}")
        return TriggerResponse(
            success=False,
            message=f"Error creating trigger: {str(e)}"
        )


@router.put("/api/v1/triggers/{trigger_id}", response_model=TriggerResponse)
async def update_trigger(
    trigger_id: str,
    trigger_update: Trigger,
    db: SQLiteDB = Depends(get_db)
):
    """Update an existing trigger.
    
    Args:
        trigger_id: ID of the trigger to update.
        trigger_update: Updated trigger data.
        db: Database connection.
        
    Returns:
        Response with trigger ID.
    """
    try:
        # Check if the trigger exists
        existing_trigger = db.get_trigger(trigger_id)
        if not existing_trigger:
            return TriggerResponse(
                success=False,
                message=f"Trigger {trigger_id} not found"
            )
        
        # Update the trigger ID and timestamps
        trigger_update.id = trigger_id
        trigger_update.created_at = existing_trigger.created_at
        trigger_update.updated_at = datetime.now()
        
        # Update the trigger
        db.update_trigger(trigger_update)
        
        return TriggerResponse(
            success=True,
            message="Trigger updated successfully",
            trigger_id=trigger_id
        )
    except Exception as e:
        logger.error(f"Error updating trigger {trigger_id}: {e}")
        return TriggerResponse(
            success=False,
            message=f"Error updating trigger: {str(e)}"
        )


@router.delete("/api/v1/triggers/{trigger_id}", response_model=TriggerResponse)
async def delete_trigger(
    trigger_id: str,
    db: SQLiteDB = Depends(get_db)
):
    """Delete a trigger.
    
    Args:
        trigger_id: ID of the trigger to delete.
        db: Database connection.
        
    Returns:
        Response with success status.
    """
    try:
        # Check if the trigger exists
        existing_trigger = db.get_trigger(trigger_id)
        if not existing_trigger:
            return TriggerResponse(
                success=False,
                message=f"Trigger {trigger_id} not found"
            )
        
        # Delete the trigger
        db.delete_trigger(trigger_id)
        
        return TriggerResponse(
            success=True,
            message="Trigger deleted successfully",
            trigger_id=trigger_id
        )
    except Exception as e:
        logger.error(f"Error deleting trigger {trigger_id}: {e}")
        return TriggerResponse(
            success=False,
            message=f"Error deleting trigger: {str(e)}"
        )


@router.get("/api/v1/triggers", response_model=List[Trigger])
async def get_triggers(
    repository: Optional[str] = None,
    event_type: Optional[str] = None,
    enabled: Optional[bool] = None,
    db: SQLiteDB = Depends(get_db)
):
    """Get triggers with optional filtering.
    
    Args:
        repository: Filter by repository.
        event_type: Filter by event type.
        enabled: Filter by enabled status.
        db: Database connection.
        
    Returns:
        List of triggers.
    """
    try:
        return db.get_triggers(repository, event_type, enabled)
    except Exception as e:
        logger.error(f"Error getting triggers: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting triggers: {str(e)}")


@router.get("/api/v1/triggers/{trigger_id}", response_model=Trigger)
async def get_trigger(
    trigger_id: str,
    db: SQLiteDB = Depends(get_db)
):
    """Get a trigger by ID.
    
    Args:
        trigger_id: ID of the trigger to get.
        db: Database connection.
        
    Returns:
        Trigger if found.
    """
    try:
        trigger = db.get_trigger(trigger_id)
        if not trigger:
            raise HTTPException(status_code=404, detail=f"Trigger {trigger_id} not found")
        return trigger
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trigger {trigger_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting trigger: {str(e)}")


@router.get("/api/v1/event-types", response_model=List[str])
async def get_event_types():
    """Get all available event types.
    
    Returns:
        List of event types.
    """
    return [event_type.value for event_type in EventType]


@router.get("/api/v1/execution-types", response_model=List[str])
async def get_execution_types():
    """Get all available execution types.
    
    Returns:
        List of execution types.
    """
    return [execution_type.value for execution_type in ExecutionType]
