"""
API endpoints for managing executions.
"""

import os
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from pr_agent.log import get_logger

from ..db.models import Execution, ExecutionStatus, Notification
from ..db.sqlite import SQLiteDB
from .events import get_db

router = APIRouter()
logger = get_logger()


class ExecutionResponse(BaseModel):
    """Response model for execution endpoints."""
    success: bool
    message: str
    execution_id: Optional[str] = None


@router.get("/api/v1/executions", response_model=List[Execution])
async def get_executions(
    event_id: Optional[str] = None,
    trigger_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: SQLiteDB = Depends(get_db)
):
    """Get executions with optional filtering.
    
    Args:
        event_id: Filter by event ID.
        trigger_id: Filter by trigger ID.
        status: Filter by status.
        limit: Maximum number of executions to return.
        offset: Offset for pagination.
        db: Database connection.
        
    Returns:
        List of executions.
    """
    try:
        return db.get_executions(event_id, trigger_id, status, limit, offset)
    except Exception as e:
        logger.error(f"Error getting executions: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting executions: {str(e)}")


@router.get("/api/v1/executions/{execution_id}", response_model=Execution)
async def get_execution(
    execution_id: str,
    db: SQLiteDB = Depends(get_db)
):
    """Get an execution by ID.
    
    Args:
        execution_id: ID of the execution to get.
        db: Database connection.
        
    Returns:
        Execution if found.
    """
    try:
        execution = db.get_execution(execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail=f"Execution {execution_id} not found")
        return execution
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting execution {execution_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting execution: {str(e)}")


@router.post("/api/v1/executions/{execution_id}/retry", response_model=ExecutionResponse)
async def retry_execution(
    execution_id: str,
    db: SQLiteDB = Depends(get_db)
):
    """Retry a failed execution.
    
    Args:
        execution_id: ID of the execution to retry.
        db: Database connection.
        
    Returns:
        Response with new execution ID.
    """
    try:
        # Get the execution
        execution = db.get_execution(execution_id)
        if not execution:
            return ExecutionResponse(
                success=False,
                message=f"Execution {execution_id} not found"
            )
        
        # Check if the execution is failed
        if execution.status != ExecutionStatus.FAILED:
            return ExecutionResponse(
                success=False,
                message=f"Execution {execution_id} is not failed (status: {execution.status.value})"
            )
        
        # Get the event and trigger
        event = db.get_event(execution.event_id)
        trigger = db.get_trigger(execution.trigger_id)
        
        if not event or not trigger:
            return ExecutionResponse(
                success=False,
                message="Event or trigger not found"
            )
        
        # Execute the trigger
        from ..execution.action_executor import ActionExecutor
        from ..execution.code_executor import CodeExecutor
        from ..execution.command_executor import CommandExecutor
        
        # Initialize the appropriate executor
        if trigger.execution_type == "codefile":
            executor = CodeExecutor()
        elif trigger.execution_type == "github_action":
            executor = ActionExecutor()
        elif trigger.execution_type == "pr_agent_command":
            executor = CommandExecutor()
        else:
            return ExecutionResponse(
                success=False,
                message=f"Unknown execution type: {trigger.execution_type}"
            )
        
        # Execute the trigger
        new_execution = executor.execute_trigger(trigger, event)
        
        # Store the execution in the database
        new_execution_id = db.create_execution(new_execution)
        
        # Send notification if enabled
        if trigger.notifications.get("windows", False):
            from ..notification.windows import WindowsNotifier
            notifier = WindowsNotifier()
            notifier.send_trigger_notification(
                trigger.name,
                event.type.value,
                event.repository,
                new_execution.status.value
            )
        
        return ExecutionResponse(
            success=True,
            message="Execution retried successfully",
            execution_id=new_execution_id
        )
    except Exception as e:
        logger.error(f"Error retrying execution {execution_id}: {e}")
        return ExecutionResponse(
            success=False,
            message=f"Error retrying execution: {str(e)}"
        )


@router.get("/api/v1/executions/{execution_id}/notifications", response_model=List[Notification])
async def get_execution_notifications(
    execution_id: str,
    db: SQLiteDB = Depends(get_db)
):
    """Get notifications for an execution.
    
    Args:
        execution_id: ID of the execution to get notifications for.
        db: Database connection.
        
    Returns:
        List of notifications.
    """
    try:
        return db.get_notifications(execution_id)
    except Exception as e:
        logger.error(f"Error getting notifications for execution {execution_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting notifications: {str(e)}")


@router.get("/api/v1/execution-statuses", response_model=List[str])
async def get_execution_statuses():
    """Get all available execution statuses.
    
    Returns:
        List of execution statuses.
    """
    return [status.value for status in ExecutionStatus]
