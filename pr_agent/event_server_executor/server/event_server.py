"""
Event server for Event Server Executor.

This module provides a server that captures GitHub events and stores them in a database.
"""

import json
import os
from typing import Any, Dict, List, Optional, Tuple, Union

import uvicorn
from fastapi import APIRouter, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.background import BackgroundTasks

from pr_agent.log import get_logger
from pr_agent.event_server_executor.db.manager import DatabaseManager
from pr_agent.event_server_executor.server.executor import CodeExecutor


class EventServer:
    """Event server for Event Server Executor."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """Initialize the event server.
        
        Args:
            db_manager: The database manager to use. If None, a new one will be created.
        """
        self.logger = get_logger()
        self.db_manager = db_manager or DatabaseManager(
            db_type=os.environ.get("EVENT_DB_TYPE", "sqlite")
        )
        self.executor = CodeExecutor(self.db_manager)
        
        self.app = FastAPI(title="Event Server Executor")
        self.router = APIRouter()
        
        # Set up CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Set up routes
        self.setup_routes()
        
        # Include router
        self.app.include_router(self.router)

    def setup_routes(self):
        """Set up the routes for the server."""
        @self.router.post("/api/webhooks/github")
        async def handle_github_webhook(background_tasks: BackgroundTasks, request: Request):
            """Handle GitHub webhook events."""
            self.logger.debug("Received GitHub webhook event")
            
            # Get the event type from the headers
            event_type = request.headers.get("X-GitHub-Event")
            if not event_type:
                self.logger.warning("No event type in headers")
                raise HTTPException(status_code=400, detail="No event type in headers")
            
            # Parse the request body
            try:
                body = await request.json()
            except json.JSONDecodeError:
                self.logger.warning("Invalid JSON in request body")
                raise HTTPException(status_code=400, detail="Invalid JSON in request body")
            
            # Extract information from the body
            action = body.get("action")
            repository = body.get("repository", {}).get("full_name")
            sender = body.get("sender", {}).get("login")
            
            if not repository:
                self.logger.warning("No repository in request body")
                raise HTTPException(status_code=400, detail="No repository in request body")
            
            if not sender:
                self.logger.warning("No sender in request body")
                raise HTTPException(status_code=400, detail="No sender in request body")
            
            # Add the event to the database
            event_id = self.db_manager.add_event(
                event_type=event_type,
                action=action,
                repository=repository,
                sender=sender,
                payload=body
            )
            
            # Process the event in the background
            background_tasks.add_task(self.process_event, event_id)
            
            return {"status": "success", "event_id": event_id}
        
        @self.router.get("/api/events")
        async def get_events(limit: int = 100, offset: int = 0):
            """Get a list of events."""
            events = self.db_manager.get_events(limit=limit, offset=offset)
            return {"events": [event.dict() for event in events]}
        
        @self.router.get("/api/events/{event_id}")
        async def get_event(event_id: str):
            """Get an event by ID."""
            event = self.db_manager.get_event(event_id)
            if not event:
                raise HTTPException(status_code=404, detail="Event not found")
            return event.dict()
        
        @self.router.get("/api/triggers")
        async def get_triggers(
            repository: Optional[str] = None,
            event_type: Optional[str] = None,
            action: Optional[str] = None,
            enabled: Optional[bool] = None
        ):
            """Get a list of triggers."""
            triggers = self.db_manager.get_triggers(
                repository=repository,
                event_type=event_type,
                action=action,
                enabled=enabled
            )
            return {"triggers": [trigger.dict() for trigger in triggers]}
        
        @self.router.post("/api/triggers")
        async def add_trigger(trigger: Dict[str, Any]):
            """Add a new trigger."""
            trigger_id = self.db_manager.add_trigger(
                name=trigger.get("name"),
                repository=trigger.get("repository"),
                event_type=trigger.get("event_type"),
                action=trigger.get("action"),
                codefile_path=trigger.get("codefile_path"),
                enabled=trigger.get("enabled", True),
                notify=trigger.get("notify", True)
            )
            return {"status": "success", "trigger_id": trigger_id}
        
        @self.router.get("/api/triggers/{trigger_id}")
        async def get_trigger(trigger_id: str):
            """Get a trigger by ID."""
            trigger = self.db_manager.get_trigger(trigger_id)
            if not trigger:
                raise HTTPException(status_code=404, detail="Trigger not found")
            return trigger.dict()
        
        @self.router.put("/api/triggers/{trigger_id}")
        async def update_trigger(trigger_id: str, trigger: Dict[str, Any]):
            """Update a trigger."""
            self.db_manager.update_trigger(trigger_id, **trigger)
            return {"status": "success"}
        
        @self.router.delete("/api/triggers/{trigger_id}")
        async def delete_trigger(trigger_id: str):
            """Delete a trigger."""
            self.db_manager.delete_trigger(trigger_id)
            return {"status": "success"}
        
        @self.router.get("/api/executions")
        async def get_executions(
            trigger_id: Optional[str] = None,
            event_id: Optional[str] = None,
            status: Optional[str] = None,
            limit: int = 100,
            offset: int = 0
        ):
            """Get a list of executions."""
            executions = self.db_manager.get_executions(
                trigger_id=trigger_id,
                event_id=event_id,
                status=status,
                limit=limit,
                offset=offset
            )
            return {"executions": [execution.dict() for execution in executions]}
        
        @self.router.get("/api/executions/{execution_id}")
        async def get_execution(execution_id: str):
            """Get an execution by ID."""
            execution = self.db_manager.get_execution(execution_id)
            if not execution:
                raise HTTPException(status_code=404, detail="Execution not found")
            return execution.dict()
        
        @self.router.get("/api/notifications")
        async def get_notifications(read: Optional[bool] = None, limit: int = 100, offset: int = 0):
            """Get a list of notifications."""
            notifications = self.db_manager.get_notifications(
                read=read,
                limit=limit,
                offset=offset
            )
            return {"notifications": [notification.dict() for notification in notifications]}
        
        @self.router.get("/api/notifications/{notification_id}")
        async def get_notification(notification_id: str):
            """Get a notification by ID."""
            notification = self.db_manager.get_notification(notification_id)
            if not notification:
                raise HTTPException(status_code=404, detail="Notification not found")
            return notification.dict()
        
        @self.router.put("/api/notifications/{notification_id}/read")
        async def mark_notification_read(notification_id: str):
            """Mark a notification as read."""
            self.db_manager.mark_notification_read(notification_id)
            return {"status": "success"}

    async def process_event(self, event_id: str):
        """Process an event.
        
        Args:
            event_id: The ID of the event to process.
        """
        event = self.db_manager.get_event(event_id)
        if not event:
            self.logger.warning(f"Event {event_id} not found")
            return
        
        # Get matching triggers
        triggers = self.db_manager.get_triggers(
            repository=event.repository,
            event_type=event.event_type,
            action=event.action,
            enabled=True
        )
        
        if not triggers:
            self.logger.debug(f"No matching triggers for event {event_id}")
            self.db_manager.mark_event_processed(event_id)
            return
        
        # Execute each matching trigger
        for trigger in triggers:
            self.logger.info(f"Executing trigger {trigger.id} for event {event_id}")
            
            # Update the last_triggered timestamp
            self.db_manager.update_trigger_last_triggered(trigger.id)
            
            # Add an execution record
            execution_id = self.db_manager.add_execution(trigger.id, event_id)
            
            try:
                # Execute the code
                output = await self.executor.execute(trigger, event)
                
                # Update the execution record
                self.db_manager.update_execution(execution_id, "success", output=output)
                
                # Add a notification if enabled
                if trigger.notify:
                    self.db_manager.add_notification(
                        trigger_id=trigger.id,
                        event_id=event_id,
                        execution_id=execution_id,
                        title=f"Trigger '{trigger.name}' executed successfully",
                        message=f"Event: {event.event_type}\nRepository: {event.repository}\nSender: {event.sender}"
                    )
            except Exception as e:
                self.logger.error(f"Error executing trigger {trigger.id}: {str(e)}")
                
                # Update the execution record
                self.db_manager.update_execution(execution_id, "failure", error=str(e))
                
                # Add a notification if enabled
                if trigger.notify:
                    self.db_manager.add_notification(
                        trigger_id=trigger.id,
                        event_id=event_id,
                        execution_id=execution_id,
                        title=f"Trigger '{trigger.name}' execution failed",
                        message=f"Event: {event.event_type}\nRepository: {event.repository}\nSender: {event.sender}\nError: {str(e)}"
                    )
        
        # Mark the event as processed
        self.db_manager.mark_event_processed(event_id)

    def run(self, host: str = "0.0.0.0", port: int = 3000):
        """Run the server.
        
        Args:
            host: The host to bind to.
            port: The port to bind to.
        """
        uvicorn.run(self.app, host=host, port=port)


def create_server():
    """Create and return a new event server."""
    return EventServer()


def run_server():
    """Run the event server."""
    port = int(os.environ.get("PORT", "3000"))
    server = create_server()
    server.run(port=port)
