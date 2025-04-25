"""
SQLite database implementation for the Event Server Executor.
"""

import os
import sqlite3
from typing import Any, Dict, List, Optional, Tuple, Union

from pr_agent.log import get_logger

from .models import (Event, Execution, Notification, SQLModels, Trigger,
                    deserialize_event, deserialize_execution,
                    deserialize_notification, deserialize_trigger,
                    serialize_model)


class SQLiteDB:
    """SQLite database implementation."""

    def __init__(self, db_path: str):
        """Initialize the SQLite database.
        
        Args:
            db_path: Path to the SQLite database file.
        """
        self.logger = get_logger()
        self.db_path = db_path
        
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize the database
        self._init_db()

    def _init_db(self):
        """Initialize the database by creating tables if they don't exist."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables
            for table_sql in SQLModels.get_all_tables():
                cursor.execute(table_sql)
            
            conn.commit()
            conn.close()
            self.logger.info(f"Initialized SQLite database at {self.db_path}")
        except Exception as e:
            self.logger.error(f"Error initializing SQLite database: {e}")
            raise

    def _execute_query(self, query: str, params: Tuple = (), fetch: bool = False, 
                      fetch_all: bool = False) -> Union[List[Dict[str, Any]], Dict[str, Any], None]:
        """Execute a SQL query and optionally fetch results.
        
        Args:
            query: SQL query to execute.
            params: Parameters for the query.
            fetch: Whether to fetch a single result.
            fetch_all: Whether to fetch all results.
            
        Returns:
            Query results if fetch or fetch_all is True, None otherwise.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            cursor = conn.cursor()
            
            cursor.execute(query, params)
            
            result = None
            if fetch_all:
                result = [dict(row) for row in cursor.fetchall()]
            elif fetch:
                row = cursor.fetchone()
                result = dict(row) if row else None
            
            conn.commit()
            conn.close()
            return result
        except Exception as e:
            self.logger.error(f"Error executing query: {e}")
            raise

    # Event methods
    def create_event(self, event: Event) -> str:
        """Create a new event in the database.
        
        Args:
            event: Event to create.
            
        Returns:
            ID of the created event.
        """
        data = serialize_model(event)
        query = """
        INSERT INTO events (id, type, action, repository, sender, data, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            data["id"],
            data["type"],
            data["action"],
            data["repository"],
            data["sender"],
            data["data"],
            data["timestamp"]
        )
        self._execute_query(query, params)
        return event.id

    def get_event(self, event_id: str) -> Optional[Event]:
        """Get an event by ID.
        
        Args:
            event_id: ID of the event to get.
            
        Returns:
            Event if found, None otherwise.
        """
        query = "SELECT * FROM events WHERE id = ?"
        result = self._execute_query(query, (event_id,), fetch=True)
        if result:
            return deserialize_event(result)
        return None

    def get_events(self, repository: Optional[str] = None, 
                  event_type: Optional[str] = None,
                  limit: int = 100, offset: int = 0) -> List[Event]:
        """Get events with optional filtering.
        
        Args:
            repository: Filter by repository.
            event_type: Filter by event type.
            limit: Maximum number of events to return.
            offset: Offset for pagination.
            
        Returns:
            List of events.
        """
        query = "SELECT * FROM events"
        params = []
        
        # Add filters
        filters = []
        if repository:
            filters.append("repository = ?")
            params.append(repository)
        if event_type:
            filters.append("type = ?")
            params.append(event_type)
        
        if filters:
            query += " WHERE " + " AND ".join(filters)
        
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        results = self._execute_query(query, tuple(params), fetch_all=True)
        return [deserialize_event(result) for result in results]

    # Trigger methods
    def create_trigger(self, trigger: Trigger) -> str:
        """Create a new trigger in the database.
        
        Args:
            trigger: Trigger to create.
            
        Returns:
            ID of the created trigger.
        """
        data = serialize_model(trigger)
        query = """
        INSERT INTO triggers (id, name, repository, event_type, event_action, 
                            execution_type, execution_params, notifications, 
                            enabled, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            data["id"],
            data["name"],
            data["repository"],
            data["event_type"],
            data["event_action"],
            data["execution_type"],
            data["execution_params"],
            data["notifications"],
            1 if data["enabled"] else 0,
            data["created_at"],
            data["updated_at"]
        )
        self._execute_query(query, params)
        return trigger.id

    def update_trigger(self, trigger: Trigger) -> bool:
        """Update an existing trigger in the database.
        
        Args:
            trigger: Trigger to update.
            
        Returns:
            True if the trigger was updated, False otherwise.
        """
        data = serialize_model(trigger)
        query = """
        UPDATE triggers
        SET name = ?, repository = ?, event_type = ?, event_action = ?,
            execution_type = ?, execution_params = ?, notifications = ?,
            enabled = ?, updated_at = ?
        WHERE id = ?
        """
        params = (
            data["name"],
            data["repository"],
            data["event_type"],
            data["event_action"],
            data["execution_type"],
            data["execution_params"],
            data["notifications"],
            1 if data["enabled"] else 0,
            data["updated_at"],
            data["id"]
        )
        self._execute_query(query, params)
        return True

    def get_trigger(self, trigger_id: str) -> Optional[Trigger]:
        """Get a trigger by ID.
        
        Args:
            trigger_id: ID of the trigger to get.
            
        Returns:
            Trigger if found, None otherwise.
        """
        query = "SELECT * FROM triggers WHERE id = ?"
        result = self._execute_query(query, (trigger_id,), fetch=True)
        if result:
            return deserialize_trigger(result)
        return None

    def get_triggers(self, repository: Optional[str] = None,
                    event_type: Optional[str] = None,
                    enabled: Optional[bool] = None) -> List[Trigger]:
        """Get triggers with optional filtering.
        
        Args:
            repository: Filter by repository.
            event_type: Filter by event type.
            enabled: Filter by enabled status.
            
        Returns:
            List of triggers.
        """
        query = "SELECT * FROM triggers"
        params = []
        
        # Add filters
        filters = []
        if repository:
            filters.append("repository = ?")
            params.append(repository)
        if event_type:
            filters.append("event_type = ?")
            params.append(event_type)
        if enabled is not None:
            filters.append("enabled = ?")
            params.append(1 if enabled else 0)
        
        if filters:
            query += " WHERE " + " AND ".join(filters)
        
        query += " ORDER BY created_at DESC"
        
        results = self._execute_query(query, tuple(params), fetch_all=True)
        return [deserialize_trigger(result) for result in results]

    def delete_trigger(self, trigger_id: str) -> bool:
        """Delete a trigger by ID.
        
        Args:
            trigger_id: ID of the trigger to delete.
            
        Returns:
            True if the trigger was deleted, False otherwise.
        """
        query = "DELETE FROM triggers WHERE id = ?"
        self._execute_query(query, (trigger_id,))
        return True

    def get_matching_triggers(self, event: Event) -> List[Trigger]:
        """Get triggers that match an event.
        
        Args:
            event: Event to match triggers against.
            
        Returns:
            List of matching triggers.
        """
        query = """
        SELECT * FROM triggers 
        WHERE enabled = 1 
        AND event_type = ? 
        AND repository = ?
        """
        params = [event.type.value, event.repository]
        
        # Add action filter if present
        if event.action:
            query += " AND (event_action IS NULL OR event_action = ?)"
            params.append(event.action)
        else:
            query += " AND event_action IS NULL"
        
        results = self._execute_query(query, tuple(params), fetch_all=True)
        return [deserialize_trigger(result) for result in results]

    # Execution methods
    def create_execution(self, execution: Execution) -> str:
        """Create a new execution in the database.
        
        Args:
            execution: Execution to create.
            
        Returns:
            ID of the created execution.
        """
        data = serialize_model(execution)
        query = """
        INSERT INTO executions (id, event_id, trigger_id, status, result, error,
                              start_time, end_time, duration)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            data["id"],
            data["event_id"],
            data["trigger_id"],
            data["status"],
            data.get("result"),
            data.get("error"),
            data["start_time"],
            data.get("end_time"),
            data.get("duration")
        )
        self._execute_query(query, params)
        return execution.id

    def update_execution(self, execution: Execution) -> bool:
        """Update an existing execution in the database.
        
        Args:
            execution: Execution to update.
            
        Returns:
            True if the execution was updated, False otherwise.
        """
        data = serialize_model(execution)
        query = """
        UPDATE executions
        SET status = ?, result = ?, error = ?, end_time = ?, duration = ?
        WHERE id = ?
        """
        params = (
            data["status"],
            data.get("result"),
            data.get("error"),
            data.get("end_time"),
            data.get("duration"),
            data["id"]
        )
        self._execute_query(query, params)
        return True

    def get_execution(self, execution_id: str) -> Optional[Execution]:
        """Get an execution by ID.
        
        Args:
            execution_id: ID of the execution to get.
            
        Returns:
            Execution if found, None otherwise.
        """
        query = "SELECT * FROM executions WHERE id = ?"
        result = self._execute_query(query, (execution_id,), fetch=True)
        if result:
            return deserialize_execution(result)
        return None

    def get_executions(self, event_id: Optional[str] = None,
                      trigger_id: Optional[str] = None,
                      status: Optional[str] = None,
                      limit: int = 100, offset: int = 0) -> List[Execution]:
        """Get executions with optional filtering.
        
        Args:
            event_id: Filter by event ID.
            trigger_id: Filter by trigger ID.
            status: Filter by status.
            limit: Maximum number of executions to return.
            offset: Offset for pagination.
            
        Returns:
            List of executions.
        """
        query = "SELECT * FROM executions"
        params = []
        
        # Add filters
        filters = []
        if event_id:
            filters.append("event_id = ?")
            params.append(event_id)
        if trigger_id:
            filters.append("trigger_id = ?")
            params.append(trigger_id)
        if status:
            filters.append("status = ?")
            params.append(status)
        
        if filters:
            query += " WHERE " + " AND ".join(filters)
        
        query += " ORDER BY start_time DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        results = self._execute_query(query, tuple(params), fetch_all=True)
        return [deserialize_execution(result) for result in results]

    # Notification methods
    def create_notification(self, notification: Notification) -> str:
        """Create a new notification in the database.
        
        Args:
            notification: Notification to create.
            
        Returns:
            ID of the created notification.
        """
        data = serialize_model(notification)
        query = """
        INSERT INTO notifications (id, execution_id, type, status, message, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (
            data["id"],
            data["execution_id"],
            data["type"],
            data["status"],
            data["message"],
            data["timestamp"]
        )
        self._execute_query(query, params)
        return notification.id

    def get_notifications(self, execution_id: Optional[str] = None,
                         limit: int = 100, offset: int = 0) -> List[Notification]:
        """Get notifications with optional filtering.
        
        Args:
            execution_id: Filter by execution ID.
            limit: Maximum number of notifications to return.
            offset: Offset for pagination.
            
        Returns:
            List of notifications.
        """
        query = "SELECT * FROM notifications"
        params = []
        
        # Add filters
        if execution_id:
            query += " WHERE execution_id = ?"
            params.append(execution_id)
        
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        results = self._execute_query(query, tuple(params), fetch_all=True)
        return [deserialize_notification(result) for result in results]
