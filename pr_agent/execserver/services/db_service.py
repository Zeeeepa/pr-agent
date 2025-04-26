import os
import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from supabase import create_client, Client

from ..models.event import Event
from ..models.project import Project
from ..models.trigger import Trigger
from ..models.workflow import Workflow, WorkflowRun
from ..config import get_supabase_url, get_supabase_anon_key
from .migration_service import MigrationService

logger = logging.getLogger(__name__)

class DatabaseService:
    """
    Service for interacting with the database
    """
    def __init__(self, settings_service=None):
        """Initialize the database service"""
        self.settings_service = settings_service
        self.supabase = None
        self.migration_service = None
        self._initialize_supabase()
        
    def _initialize_supabase(self):
        """Initialize the Supabase client"""
        try:
            # Try to get settings from settings service first
            if self.settings_service:
                supabase_url = self.settings_service.get_setting('SUPABASE_URL')
                supabase_anon_key = self.settings_service.get_setting('SUPABASE_ANON_KEY')
                
                if supabase_url and supabase_anon_key:
                    self.supabase = create_client(supabase_url, supabase_anon_key)
                    self.migration_service = MigrationService(self.supabase)
                    return
            
            # Fall back to config if settings service doesn't have the values
            supabase_url = get_supabase_url()
            supabase_anon_key = get_supabase_anon_key()
            
            if supabase_url and supabase_anon_key:
                self.supabase = create_client(supabase_url, supabase_anon_key)
                self.migration_service = MigrationService(self.supabase)
                
                # Apply migrations if Supabase is initialized
                if self.supabase:
                    self._apply_migrations()
        except Exception as e:
            # Log the error but don't raise it - we'll handle missing Supabase in each method
            logger.error(f"Failed to initialize Supabase: {str(e)}")
    
    def _apply_migrations(self):
        """Apply database migrations"""
        try:
            if self.migration_service:
                import asyncio
                asyncio.create_task(self.migration_service.apply_migrations())
        except Exception as e:
            logger.error(f"Failed to apply migrations: {str(e)}")
    
    def _ensure_supabase(self):
        """Ensure Supabase is initialized"""
        if not self.supabase:
            self._initialize_supabase()
            
        if not self.supabase:
            raise ValueError("Supabase is not initialized. Please provide Supabase URL and API key in settings.")
    
    async def test_connection(self) -> bool:
        """
        Test the Supabase connection
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            self._ensure_supabase()
            # Try a simple query to test the connection
            self.supabase.table("migrations").select("*").limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Supabase connection test failed: {str(e)}")
            return False
        
    # Event methods
    async def log_event(self, event_type: str, repository: str, payload: Dict[str, Any]) -> Event:
        """
        Log a GitHub event to the database
        
        Args:
            event_type: Type of GitHub event
            repository: Repository full name (owner/repo)
            payload: Event payload data
            
        Returns:
            The created Event object
        """
        self._ensure_supabase()
        
        event_id = str(uuid.uuid4())
        event = Event(
            id=event_id,
            event_type=event_type,
            repository=repository,
            payload=payload,
            created_at=datetime.utcnow(),
            processed=False,
            processed_at=None
        )
        
        try:
            # Insert into Supabase
            self.supabase.table("events").insert(event.dict()).execute()
            return event
        except Exception as e:
            logger.error(f"Failed to log event: {str(e)}")
            raise
    
    async def mark_event_processed(self, event_id: str) -> Event:
        """
        Mark an event as processed
        
        Args:
            event_id: ID of the event to mark as processed
            
        Returns:
            The updated Event object
        """
        self._ensure_supabase()
        
        now = datetime.utcnow()
        
        try:
            # Update in Supabase
            result = self.supabase.table("events").update({
                "processed": True,
                "processed_at": now.isoformat()
            }).eq("id", event_id).execute()
            
            # Get the updated event
            event_data = result.data[0] if result.data else None
            if not event_data:
                raise ValueError(f"Event with ID {event_id} not found")
            
            return Event(**event_data)
        except Exception as e:
            logger.error(f"Failed to mark event as processed: {str(e)}")
            raise
    
    async def get_event(self, event_id: str) -> Optional[Event]:
        """
        Get an event by ID
        
        Args:
            event_id: ID of the event to get
            
        Returns:
            The Event object or None if not found
        """
        self._ensure_supabase()
        
        try:
            result = self.supabase.table("events").select("*").eq("id", event_id).execute()
            event_data = result.data[0] if result.data else None
            
            if not event_data:
                return None
            
            return Event(**event_data)
        except Exception as e:
            logger.error(f"Failed to get event: {str(e)}")
            return None
    
    async def get_events(self, repository: Optional[str] = None, processed: Optional[bool] = None, 
                        limit: int = 100, offset: int = 0) -> List[Event]:
        """
        Get events with optional filtering
        
        Args:
            repository: Filter by repository
            processed: Filter by processed status
            limit: Maximum number of events to return
            offset: Offset for pagination
            
        Returns:
            List of Event objects
        """
        self._ensure_supabase()
        
        try:
            query = self.supabase.table("events").select("*")
            
            if repository:
                query = query.eq("repository", repository)
            
            if processed is not None:
                query = query.eq("processed", processed)
            
            result = query.order("created_at", desc=True).limit(limit).offset(offset).execute()
            
            return [Event(**event_data) for event_data in result.data]
        except Exception as e:
            logger.error(f"Failed to get events: {str(e)}")
            return []
    
    # Project methods
    async def create_project(self, project: Project) -> Project:
        """
        Create a new project
        
        Args:
            project: Project to create
            
        Returns:
            The created Project object
        """
        self._ensure_supabase()
        
        try:
            self.supabase.table("projects").insert(project.dict()).execute()
            return project
        except Exception as e:
            logger.error(f"Failed to create project: {str(e)}")
            raise
    
    async def get_project(self, project_id: str) -> Optional[Project]:
        """
        Get a project by ID
        
        Args:
            project_id: ID of the project to get
            
        Returns:
            The Project object or None if not found
        """
        self._ensure_supabase()
        
        try:
            result = self.supabase.table("projects").select("*").eq("id", project_id).execute()
            project_data = result.data[0] if result.data else None
            
            if not project_data:
                return None
            
            return Project(**project_data)
        except Exception as e:
            logger.error(f"Failed to get project: {str(e)}")
            return None
    
    async def get_projects(self) -> List[Project]:
        """
        Get all projects
        
        Returns:
            List of Project objects
        """
        self._ensure_supabase()
        
        try:
            result = self.supabase.table("projects").select("*").execute()
            return [Project(**project_data) for project_data in result.data]
        except Exception as e:
            logger.error(f"Failed to get projects: {str(e)}")
            return []
    
    # Trigger methods
    async def create_trigger(self, trigger: Trigger) -> Trigger:
        """
        Create a new trigger
        
        Args:
            trigger: Trigger to create
            
        Returns:
            The created Trigger object
        """
        self._ensure_supabase()
        
        try:
            self.supabase.table("triggers").insert(trigger.dict()).execute()
            return trigger
        except Exception as e:
            logger.error(f"Failed to create trigger: {str(e)}")
            raise
    
    async def get_trigger(self, trigger_id: str) -> Optional[Trigger]:
        """
        Get a trigger by ID
        
        Args:
            trigger_id: ID of the trigger to get
            
        Returns:
            The Trigger object or None if not found
        """
        self._ensure_supabase()
        
        try:
            result = self.supabase.table("triggers").select("*").eq("id", trigger_id).execute()
            trigger_data = result.data[0] if result.data else None
            
            if not trigger_data:
                return None
            
            return Trigger(**trigger_data)
        except Exception as e:
            logger.error(f"Failed to get trigger: {str(e)}")
            return None
    
    async def get_triggers_for_project(self, project_id: str) -> List[Trigger]:
        """
        Get all triggers for a project
        
        Args:
            project_id: ID of the project
            
        Returns:
            List of Trigger objects
        """
        self._ensure_supabase()
        
        try:
            result = self.supabase.table("triggers").select("*").eq("project_id", project_id).execute()
            return [Trigger(**trigger_data) for trigger_data in result.data]
        except Exception as e:
            logger.error(f"Failed to get triggers for project: {str(e)}")
            return []
    
    async def update_trigger(self, trigger_id: str, data: Dict[str, Any]) -> Optional[Trigger]:
        """
        Update a trigger
        
        Args:
            trigger_id: ID of the trigger to update
            data: Data to update
            
        Returns:
            The updated Trigger object or None if not found
        """
        self._ensure_supabase()
        
        try:
            result = self.supabase.table("triggers").update(data).eq("id", trigger_id).execute()
            trigger_data = result.data[0] if result.data else None
            
            if not trigger_data:
                return None
            
            return Trigger(**trigger_data)
        except Exception as e:
            logger.error(f"Failed to update trigger: {str(e)}")
            return None
    
    # Workflow methods
    async def create_workflow(self, workflow: Workflow) -> Workflow:
        """
        Create a new workflow
        
        Args:
            workflow: Workflow to create
            
        Returns:
            The created Workflow object
        """
        self._ensure_supabase()
        
        try:
            self.supabase.table("workflows").insert(workflow.dict()).execute()
            return workflow
        except Exception as e:
            logger.error(f"Failed to create workflow: {str(e)}")
            raise
    
    async def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """
        Get a workflow by ID
        
        Args:
            workflow_id: ID of the workflow to get
            
        Returns:
            The Workflow object or None if not found
        """
        self._ensure_supabase()
        
        try:
            result = self.supabase.table("workflows").select("*").eq("id", workflow_id).execute()
            workflow_data = result.data[0] if result.data else None
            
            if not workflow_data:
                return None
            
            return Workflow(**workflow_data)
        except Exception as e:
            logger.error(f"Failed to get workflow: {str(e)}")
            return None
    
    async def get_workflows_for_repository(self, repository: str) -> List[Workflow]:
        """
        Get all workflows for a repository
        
        Args:
            repository: Repository full name (owner/repo)
            
        Returns:
            List of Workflow objects
        """
        self._ensure_supabase()
        
        try:
            result = self.supabase.table("workflows").select("*").eq("repository", repository).execute()
            return [Workflow(**workflow_data) for workflow_data in result.data]
        except Exception as e:
            logger.error(f"Failed to get workflows for repository: {str(e)}")
            return []
    
    async def create_workflow_run(self, workflow_run: WorkflowRun) -> WorkflowRun:
        """
        Create a new workflow run
        
        Args:
            workflow_run: WorkflowRun to create
            
        Returns:
            The created WorkflowRun object
        """
        self._ensure_supabase()
        
        try:
            self.supabase.table("workflow_runs").insert(workflow_run.dict()).execute()
            return workflow_run
        except Exception as e:
            logger.error(f"Failed to create workflow run: {str(e)}")
            raise
    
    async def get_workflow_runs(self, workflow_id: Optional[str] = None, repository: Optional[str] = None,
                              limit: int = 10, offset: int = 0) -> List[WorkflowRun]:
        """
        Get workflow runs with optional filtering
        
        Args:
            workflow_id: Filter by workflow ID
            repository: Filter by repository
            limit: Maximum number of workflow runs to return
            offset: Offset for pagination
            
        Returns:
            List of WorkflowRun objects
        """
        self._ensure_supabase()
        
        try:
            query = self.supabase.table("workflow_runs").select("*")
            
            if workflow_id:
                query = query.eq("workflow_id", workflow_id)
            
            if repository:
                query = query.eq("repository", repository)
            
            result = query.order("created_at", desc=True).limit(limit).offset(offset).execute()
            
            return [WorkflowRun(**run_data) for run_data in result.data]
        except Exception as e:
            logger.error(f"Failed to get workflow runs: {str(e)}")
            return []
