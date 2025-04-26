import os
import uuid
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json

from supabase import create_client, Client

from ..models.event import Event
from ..models.project import Project
from ..models.trigger import Trigger
from ..models.workflow import Workflow, WorkflowRun
from ..config import get_supabase_url, get_supabase_anon_key
from .migration_service import MigrationService
from pr_agent.error_handler import ConfigurationError

# Set up logging
logger = logging.getLogger(__name__)

class DatabaseService:
    """
    Service for managing database operations
    """
    
    def __init__(self, settings_service=None):
        """Initialize the database service"""
        self.settings_service = settings_service
        self.supabase: Optional[Client] = None
        self.migration_service = None
        self._initialize_supabase()
        
    def _initialize_supabase(self):
        """Initialize the Supabase client with improved error handling"""
        try:
            # Try to get Supabase URL and API key from settings service
            if self.settings_service:
                supabase_url = self.settings_service.get_setting('SUPABASE_URL')
                supabase_anon_key = self.settings_service.get_setting('SUPABASE_ANON_KEY')
                
                if supabase_url and supabase_anon_key:
                    logger.info("Initializing Supabase from settings service")
                    try:
                        self.supabase = create_client(supabase_url, supabase_anon_key)
                        self.migration_service = MigrationService(self.supabase)
                        # Test connection with a simple query
                        self._test_connection_internal()
                        logger.info("Supabase initialized successfully from settings service")
                        return
                    except Exception as e:
                        logger.error(f"Failed to initialize Supabase from settings service: {str(e)}")
                        # Don't raise here, try the fallback method
            
            # Fall back to config if settings service doesn't have the values
            try:
                supabase_url = get_supabase_url()
                supabase_anon_key = get_supabase_anon_key()
                
                if supabase_url and supabase_anon_key:
                    logger.info("Initializing Supabase from environment/config")
                    self.supabase = create_client(supabase_url, supabase_anon_key)
                    self.migration_service = MigrationService(self.supabase)
                    # Test connection with a simple query
                    self._test_connection_internal()
                    logger.info("Supabase initialized successfully from environment/config")
                else:
                    logger.warning("Supabase URL or API key not found in environment/config")
            except ConfigurationError:
                logger.warning("Supabase configuration not found in environment/config")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase from environment/config: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error initializing Supabase: {str(e)}")
    
    def _test_connection_internal(self):
        """Internal method to test Supabase connection"""
        if not self.supabase:
            return False
        
        try:
            # Try to query the migrations table
            self.supabase.table('migrations').select('*').limit(1).execute()
            return True
        except Exception as e:
            # Check if this is a "table doesn't exist" error, which is okay
            # as migrations will create it
            error_str = str(e).lower()
            if "not found" in error_str and "relation" in error_str:
                # This is expected for a new database
                logger.info("Migrations table not found, will be created during migration")
                return True
            else:
                logger.error(f"Failed to connect to Supabase: {str(e)}")
                raise

    async def test_connection(self) -> Tuple[bool, Optional[str]]:
        """
        Test connection to Supabase
        
        Returns:
            Tuple of (success, error_message)
        """
        if not self.supabase:
            return False, "Supabase is not initialized. Please provide Supabase URL and API key in settings."
        
        try:
            # Try to query the migrations table
            self.supabase.table('migrations').select('*').limit(1).execute()
            
            # If we get here, connection is successful
            # Now check if migrations need to be applied
            if self.migration_service:
                try:
                    await self.migration_service.apply_migrations()
                except Exception as e:
                    logger.error(f"Failed to apply migrations: {str(e)}")
                    return False, f"Connected to Supabase, but failed to apply migrations: {str(e)}"
            
            return True, None
        except Exception as e:
            error_str = str(e).lower()
            
            # Provide more specific error messages based on the exception
            if "not found" in error_str and "relation" in error_str:
                # This is expected for a new database, try to apply migrations
                if self.migration_service:
                    try:
                        await self.migration_service.apply_migrations()
                        return True, None
                    except Exception as migration_error:
                        logger.error(f"Failed to apply migrations: {str(migration_error)}")
                        return False, f"Failed to apply database migrations: {str(migration_error)}"
                else:
                    return False, "Migration service not initialized"
            elif "unauthorized" in error_str or "authentication" in error_str:
                return False, "Invalid Supabase API key or unauthorized access"
            elif "network" in error_str or "connection" in error_str:
                return False, "Network or connection error when connecting to Supabase"
            else:
                return False, f"Failed to connect to Supabase: {str(e)}"

    # Event methods
    async def log_event(self, event_type: str, repository: str, payload: Dict[str, Any]) -> Event:
        """
        Log an event
        
        Args:
            event_type: Type of event
            repository: Repository name
            payload: Event payload
            
        Returns:
            Event object
        """
        self._ensure_supabase()
        
        # Create event
        event = Event(
            id=str(uuid.uuid4()),
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
            Updated event
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
            Event object or None if not found
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
        Get events
        
        Args:
            repository: Repository to filter by
            processed: Whether to filter by processed status
            limit: Maximum number of events to return
            offset: Offset for pagination
            
        Returns:
            List of events
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
        Create a project
        
        Args:
            project: Project to create
            
        Returns:
            Created project
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
            Project object or None if not found
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
            List of projects
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
        Create a trigger
        
        Args:
            trigger: Trigger to create
            
        Returns:
            Created trigger
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
            Trigger object or None if not found
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
            project_id: ID of the project to get triggers for
            
        Returns:
            List of triggers
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
            Updated trigger or None if not found
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
        Create a workflow
        
        Args:
            workflow: Workflow to create
            
        Returns:
            Created workflow
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
            Workflow object or None if not found
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
    
    async def get_workflows(self, repository: Optional[str] = None) -> List[Workflow]:
        """
        Get workflows
        
        Args:
            repository: Repository to filter by
            
        Returns:
            List of workflows
        """
        self._ensure_supabase()
        
        try:
            query = self.supabase.table("workflows").select("*")
            
            if repository:
                query = query.eq("repository", repository)
            
            result = query.execute()
            
            return [Workflow(**workflow_data) for workflow_data in result.data]
        except Exception as e:
            logger.error(f"Failed to get workflows: {str(e)}")
            return []
    
    # Workflow run methods
    async def create_workflow_run(self, workflow_run: WorkflowRun) -> WorkflowRun:
        """
        Create a workflow run
        
        Args:
            workflow_run: Workflow run to create
            
        Returns:
            Created workflow run
        """
        self._ensure_supabase()
        
        try:
            self.supabase.table("workflow_runs").insert(workflow_run.dict()).execute()
            return workflow_run
        except Exception as e:
            logger.error(f"Failed to create workflow run: {str(e)}")
            raise
    
    async def get_workflow_run(self, run_id: str) -> Optional[WorkflowRun]:
        """
        Get a workflow run by ID
        
        Args:
            run_id: ID of the workflow run to get
            
        Returns:
            Workflow run object or None if not found
        """
        self._ensure_supabase()
        
        try:
            result = self.supabase.table("workflow_runs").select("*").eq("id", run_id).execute()
            run_data = result.data[0] if result.data else None
            
            if not run_data:
                return None
            
            return WorkflowRun(**run_data)
        except Exception as e:
            logger.error(f"Failed to get workflow run: {str(e)}")
            return None
    
    async def get_workflow_runs(self, workflow_id: Optional[str] = None, repository: Optional[str] = None, 
                               limit: int = 10, offset: int = 0) -> List[WorkflowRun]:
        """
        Get workflow runs
        
        Args:
            workflow_id: Workflow ID to filter by
            repository: Repository to filter by
            limit: Maximum number of runs to return
            offset: Offset for pagination
            
        Returns:
            List of workflow runs
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
    
    async def update_workflow_run(self, run_id: str, data: Dict[str, Any]) -> Optional[WorkflowRun]:
        """
        Update a workflow run
        
        Args:
            run_id: ID of the workflow run to update
            data: Data to update
            
        Returns:
            Updated workflow run or None if not found
        """
        self._ensure_supabase()
        
        try:
            result = self.supabase.table("workflow_runs").update(data).eq("id", run_id).execute()
            run_data = result.data[0] if result.data else None
            
            if not run_data:
                return None
            
            return WorkflowRun(**run_data)
        except Exception as e:
            logger.error(f"Failed to update workflow run: {str(e)}")
            return None
    
    def _ensure_supabase(self):
        """
        Ensure Supabase is initialized
        
        Raises:
            ValueError: If Supabase is not initialized
        """
        if not self.supabase:
            # Try to initialize again in case settings were updated
            self._initialize_supabase()
            
        if not self.supabase:
            raise ValueError("Supabase is not initialized. Please provide Supabase URL and API key in settings.")
