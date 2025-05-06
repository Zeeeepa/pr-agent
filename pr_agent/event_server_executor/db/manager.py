"""
Database manager for Event Server Executor.
"""

import json
import os
import sqlite3
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union

import supabase
from pr_agent.log import get_logger

from pr_agent.event_server_executor.db.models import (
    EventExecution,
    EventTrigger,
    GitHubEvent,
    Notification,
)


class DatabaseManager:
    """Database manager for Event Server Executor."""

    def __init__(self, db_type: str = "sqlite"):
        """Initialize the database manager.
        
        Args:
            db_type: The type of database to use. Can be "sqlite" or "supabase".
        """
        self.logger = get_logger()
        self.db_type = db_type
        
        if db_type == "sqlite":
            self._init_sqlite()
        elif db_type == "supabase":
            self._init_supabase()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    def _init_sqlite(self):
        """Initialize SQLite database."""
        db_path = os.environ.get("EVENT_DB_PATH", "events.db")
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables_sqlite()
        self.logger.info(f"Initialized SQLite database at {db_path}")

    def _init_supabase(self):
        """Initialize Supabase database."""
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY environment variables must be set")
        
        self.supabase_client = supabase.create_client(supabase_url, supabase_key)
        self.logger.info(f"Initialized Supabase client with URL {supabase_url}")

    def _create_tables_sqlite(self):
        """Create tables in SQLite database."""
        cursor = self.conn.cursor()
        
        # Create events table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY,
            event_type TEXT NOT NULL,
            action TEXT,
            repository TEXT NOT NULL,
            sender TEXT NOT NULL,
            payload TEXT NOT NULL,
            timestamp REAL NOT NULL,
            processed INTEGER NOT NULL DEFAULT 0
        )
        ''')
        
        # Create triggers table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS triggers (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            repository TEXT NOT NULL,
            event_type TEXT NOT NULL,
            action TEXT,
            codefile_path TEXT NOT NULL,
            enabled INTEGER NOT NULL DEFAULT 1,
            notify INTEGER NOT NULL DEFAULT 1,
            created_at REAL NOT NULL,
            last_triggered REAL
        )
        ''')
        
        # Create executions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS executions (
            id TEXT PRIMARY KEY,
            trigger_id TEXT NOT NULL,
            event_id TEXT NOT NULL,
            status TEXT NOT NULL,
            output TEXT,
            error TEXT,
            started_at REAL NOT NULL,
            completed_at REAL,
            FOREIGN KEY (trigger_id) REFERENCES triggers (id),
            FOREIGN KEY (event_id) REFERENCES events (id)
        )
        ''')
        
        # Create notifications table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id TEXT PRIMARY KEY,
            trigger_id TEXT NOT NULL,
            event_id TEXT NOT NULL,
            execution_id TEXT,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp REAL NOT NULL,
            read INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (trigger_id) REFERENCES triggers (id),
            FOREIGN KEY (event_id) REFERENCES events (id),
            FOREIGN KEY (execution_id) REFERENCES executions (id)
        )
        ''')
        
        self.conn.commit()

    # Event methods
    def add_event(self, event_type: str, action: Optional[str], repository: str, 
                 sender: str, payload: Dict[str, Any]) -> str:
        """Add a new event to the database.
        
        Args:
            event_type: The type of event.
            action: The action of the event.
            repository: The repository of the event.
            sender: The sender of the event.
            payload: The payload of the event.
            
        Returns:
            The ID of the new event.
        """
        event_id = str(uuid.uuid4())
        timestamp = time.time()
        
        if self.db_type == "sqlite":
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO events (id, event_type, action, repository, sender, payload, timestamp) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (event_id, event_type, action, repository, sender, json.dumps(payload), timestamp)
            )
            self.conn.commit()
        elif self.db_type == "supabase":
            self.supabase_client.table("events").insert({
                "id": event_id,
                "event_type": event_type,
                "action": action,
                "repository": repository,
                "sender": sender,
                "payload": payload,
                "timestamp": timestamp,
                "processed": False
            }).execute()
        
        self.logger.info(f"Added event {event_id} of type {event_type} for repository {repository}")
        return event_id

    def get_event(self, event_id: str) -> Optional[GitHubEvent]:
        """Get an event by ID.
        
        Args:
            event_id: The ID of the event.
            
        Returns:
            The event, or None if not found.
        """
        if self.db_type == "sqlite":
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
            row = cursor.fetchone()
            
            if row:
                return GitHubEvent(
                    id=row["id"],
                    event_type=row["event_type"],
                    action=row["action"],
                    repository=row["repository"],
                    sender=row["sender"],
                    payload=json.loads(row["payload"]),
                    timestamp=row["timestamp"],
                    processed=bool(row["processed"])
                )
        elif self.db_type == "supabase":
            response = self.supabase_client.table("events").select("*").eq("id", event_id).execute()
            if response.data:
                event = response.data[0]
                return GitHubEvent(**event)
        
        return None

    def get_events(self, limit: int = 100, offset: int = 0) -> List[GitHubEvent]:
        """Get a list of events.
        
        Args:
            limit: The maximum number of events to return.
            offset: The offset to start from.
            
        Returns:
            A list of events.
        """
        events = []
        
        if self.db_type == "sqlite":
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM events ORDER BY timestamp DESC LIMIT ? OFFSET ?",
                (limit, offset)
            )
            
            for row in cursor.fetchall():
                events.append(GitHubEvent(
                    id=row["id"],
                    event_type=row["event_type"],
                    action=row["action"],
                    repository=row["repository"],
                    sender=row["sender"],
                    payload=json.loads(row["payload"]),
                    timestamp=row["timestamp"],
                    processed=bool(row["processed"])
                ))
        elif self.db_type == "supabase":
            response = self.supabase_client.table("events").select("*").order("timestamp", desc=True).range(offset, offset + limit - 1).execute()
            for event in response.data:
                events.append(GitHubEvent(**event))
        
        return events

    def mark_event_processed(self, event_id: str):
        """Mark an event as processed.
        
        Args:
            event_id: The ID of the event.
        """
        if self.db_type == "sqlite":
            cursor = self.conn.cursor()
            cursor.execute("UPDATE events SET processed = 1 WHERE id = ?", (event_id,))
            self.conn.commit()
        elif self.db_type == "supabase":
            self.supabase_client.table("events").update({"processed": True}).eq("id", event_id).execute()
        
        self.logger.debug(f"Marked event {event_id} as processed")

    # Trigger methods
    def add_trigger(self, name: str, repository: str, event_type: str, 
                   action: Optional[str], codefile_path: str, 
                   enabled: bool = True, notify: bool = True) -> str:
        """Add a new trigger to the database.
        
        Args:
            name: The name of the trigger.
            repository: The repository of the trigger.
            event_type: The event type of the trigger.
            action: The action of the trigger.
            codefile_path: The path to the code file to execute.
            enabled: Whether the trigger is enabled.
            notify: Whether to send notifications for this trigger.
            
        Returns:
            The ID of the new trigger.
        """
        trigger_id = str(uuid.uuid4())
        created_at = time.time()
        
        if self.db_type == "sqlite":
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO triggers (id, name, repository, event_type, action, codefile_path, enabled, notify, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (trigger_id, name, repository, event_type, action, codefile_path, int(enabled), int(notify), created_at)
            )
            self.conn.commit()
        elif self.db_type == "supabase":
            self.supabase_client.table("triggers").insert({
                "id": trigger_id,
                "name": name,
                "repository": repository,
                "event_type": event_type,
                "action": action,
                "codefile_path": codefile_path,
                "enabled": enabled,
                "notify": notify,
                "created_at": created_at
            }).execute()
        
        self.logger.info(f"Added trigger {trigger_id} ({name}) for repository {repository}, event type {event_type}")
        return trigger_id

    def get_trigger(self, trigger_id: str) -> Optional[EventTrigger]:
        """Get a trigger by ID.
        
        Args:
            trigger_id: The ID of the trigger.
            
        Returns:
            The trigger, or None if not found.
        """
        if self.db_type == "sqlite":
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM triggers WHERE id = ?", (trigger_id,))
            row = cursor.fetchone()
            
            if row:
                return EventTrigger(
                    id=row["id"],
                    name=row["name"],
                    repository=row["repository"],
                    event_type=row["event_type"],
                    action=row["action"],
                    codefile_path=row["codefile_path"],
                    enabled=bool(row["enabled"]),
                    notify=bool(row["notify"]),
                    created_at=row["created_at"],
                    last_triggered=row["last_triggered"]
                )
        elif self.db_type == "supabase":
            response = self.supabase_client.table("triggers").select("*").eq("id", trigger_id).execute()
            if response.data:
                trigger = response.data[0]
                return EventTrigger(**trigger)
        
        return None

    def get_triggers(self, repository: Optional[str] = None, 
                    event_type: Optional[str] = None, 
                    action: Optional[str] = None,
                    enabled: Optional[bool] = None) -> List[EventTrigger]:
        """Get a list of triggers.
        
        Args:
            repository: Filter by repository.
            event_type: Filter by event type.
            action: Filter by action.
            enabled: Filter by enabled status.
            
        Returns:
            A list of triggers.
        """
        triggers = []
        
        if self.db_type == "sqlite":
            cursor = self.conn.cursor()
            query = "SELECT * FROM triggers"
            params = []
            conditions = []
            
            if repository:
                conditions.append("repository = ?")
                params.append(repository)
            
            if event_type:
                conditions.append("event_type = ?")
                params.append(event_type)
            
            if action:
                conditions.append("action = ?")
                params.append(action)
            
            if enabled is not None:
                conditions.append("enabled = ?")
                params.append(int(enabled))
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY created_at DESC"
            
            cursor.execute(query, params)
            
            for row in cursor.fetchall():
                triggers.append(EventTrigger(
                    id=row["id"],
                    name=row["name"],
                    repository=row["repository"],
                    event_type=row["event_type"],
                    action=row["action"],
                    codefile_path=row["codefile_path"],
                    enabled=bool(row["enabled"]),
                    notify=bool(row["notify"]),
                    created_at=row["created_at"],
                    last_triggered=row["last_triggered"]
                ))
        elif self.db_type == "supabase":
            query = self.supabase_client.table("triggers").select("*")
            
            if repository:
                query = query.eq("repository", repository)
            
            if event_type:
                query = query.eq("event_type", event_type)
            
            if action:
                query = query.eq("action", action)
            
            if enabled is not None:
                query = query.eq("enabled", enabled)
            
            response = query.order("created_at", desc=True).execute()
            
            for trigger in response.data:
                triggers.append(EventTrigger(**trigger))
        
        return triggers

    def update_trigger_last_triggered(self, trigger_id: str):
        """Update the last_triggered timestamp of a trigger.
        
        Args:
            trigger_id: The ID of the trigger.
        """
        timestamp = time.time()
        
        if self.db_type == "sqlite":
            cursor = self.conn.cursor()
            cursor.execute("UPDATE triggers SET last_triggered = ? WHERE id = ?", (timestamp, trigger_id))
            self.conn.commit()
        elif self.db_type == "supabase":
            self.supabase_client.table("triggers").update({"last_triggered": timestamp}).eq("id", trigger_id).execute()
        
        self.logger.debug(f"Updated last_triggered for trigger {trigger_id}")

    def update_trigger(self, trigger_id: str, **kwargs):
        """Update a trigger.
        
        Args:
            trigger_id: The ID of the trigger.
            **kwargs: The fields to update.
        """
        if self.db_type == "sqlite":
            cursor = self.conn.cursor()
            
            set_clause = []
            params = []
            
            for key, value in kwargs.items():
                if key in ["enabled", "notify"]:
                    value = int(value)
                
                set_clause.append(f"{key} = ?")
                params.append(value)
            
            if not set_clause:
                return
            
            params.append(trigger_id)
            
            cursor.execute(
                f"UPDATE triggers SET {', '.join(set_clause)} WHERE id = ?",
                params
            )
            self.conn.commit()
        elif self.db_type == "supabase":
            update_data = {}
            
            for key, value in kwargs.items():
                update_data[key] = value
            
            if not update_data:
                return
            
            self.supabase_client.table("triggers").update(update_data).eq("id", trigger_id).execute()
        
        self.logger.info(f"Updated trigger {trigger_id}")

    def delete_trigger(self, trigger_id: str):
        """Delete a trigger.
        
        Args:
            trigger_id: The ID of the trigger.
        """
        if self.db_type == "sqlite":
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM triggers WHERE id = ?", (trigger_id,))
            self.conn.commit()
        elif self.db_type == "supabase":
            self.supabase_client.table("triggers").delete().eq("id", trigger_id).execute()
        
        self.logger.info(f"Deleted trigger {trigger_id}")

    # Execution methods
    def add_execution(self, trigger_id: str, event_id: str) -> str:
        """Add a new execution to the database.
        
        Args:
            trigger_id: The ID of the trigger.
            event_id: The ID of the event.
            
        Returns:
            The ID of the new execution.
        """
        execution_id = str(uuid.uuid4())
        started_at = time.time()
        
        if self.db_type == "sqlite":
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO executions (id, trigger_id, event_id, status, started_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (execution_id, trigger_id, event_id, "pending", started_at)
            )
            self.conn.commit()
        elif self.db_type == "supabase":
            self.supabase_client.table("executions").insert({
                "id": execution_id,
                "trigger_id": trigger_id,
                "event_id": event_id,
                "status": "pending",
                "started_at": started_at
            }).execute()
        
        self.logger.info(f"Added execution {execution_id} for trigger {trigger_id}, event {event_id}")
        return execution_id

    def update_execution(self, execution_id: str, status: str, 
                        output: Optional[str] = None, 
                        error: Optional[str] = None):
        """Update an execution.
        
        Args:
            execution_id: The ID of the execution.
            status: The status of the execution.
            output: The output of the execution.
            error: The error of the execution.
        """
        completed_at = time.time() if status != "pending" else None
        
        if self.db_type == "sqlite":
            cursor = self.conn.cursor()
            
            set_clause = ["status = ?"]
            params = [status]
            
            if output is not None:
                set_clause.append("output = ?")
                params.append(output)
            
            if error is not None:
                set_clause.append("error = ?")
                params.append(error)
            
            if completed_at is not None:
                set_clause.append("completed_at = ?")
                params.append(completed_at)
            
            params.append(execution_id)
            
            cursor.execute(
                f"UPDATE executions SET {', '.join(set_clause)} WHERE id = ?",
                params
            )
            self.conn.commit()
        elif self.db_type == "supabase":
            update_data = {"status": status}
            
            if output is not None:
                update_data["output"] = output
            
            if error is not None:
                update_data["error"] = error
            
            if completed_at is not None:
                update_data["completed_at"] = completed_at
            
            self.supabase_client.table("executions").update(update_data).eq("id", execution_id).execute()
        
        self.logger.info(f"Updated execution {execution_id} with status {status}")

    def get_execution(self, execution_id: str) -> Optional[EventExecution]:
        """Get an execution by ID.
        
        Args:
            execution_id: The ID of the execution.
            
        Returns:
            The execution, or None if not found.
        """
        if self.db_type == "sqlite":
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM executions WHERE id = ?", (execution_id,))
            row = cursor.fetchone()
            
            if row:
                return EventExecution(
                    id=row["id"],
                    trigger_id=row["trigger_id"],
                    event_id=row["event_id"],
                    status=row["status"],
                    output=row["output"],
                    error=row["error"],
                    started_at=row["started_at"],
                    completed_at=row["completed_at"]
                )
        elif self.db_type == "supabase":
            response = self.supabase_client.table("executions").select("*").eq("id", execution_id).execute()
            if response.data:
                execution = response.data[0]
                return EventExecution(**execution)
        
        return None

    def get_executions(self, trigger_id: Optional[str] = None, 
                      event_id: Optional[str] = None, 
                      status: Optional[str] = None,
                      limit: int = 100, offset: int = 0) -> List[EventExecution]:
        """Get a list of executions.
        
        Args:
            trigger_id: Filter by trigger ID.
            event_id: Filter by event ID.
            status: Filter by status.
            limit: The maximum number of executions to return.
            offset: The offset to start from.
            
        Returns:
            A list of executions.
        """
        executions = []
        
        if self.db_type == "sqlite":
            cursor = self.conn.cursor()
            query = "SELECT * FROM executions"
            params = []
            conditions = []
            
            if trigger_id:
                conditions.append("trigger_id = ?")
                params.append(trigger_id)
            
            if event_id:
                conditions.append("event_id = ?")
                params.append(event_id)
            
            if status:
                conditions.append("status = ?")
                params.append(status)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY started_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            
            for row in cursor.fetchall():
                executions.append(EventExecution(
                    id=row["id"],
                    trigger_id=row["trigger_id"],
                    event_id=row["event_id"],
                    status=row["status"],
                    output=row["output"],
                    error=row["error"],
                    started_at=row["started_at"],
                    completed_at=row["completed_at"]
                ))
        elif self.db_type == "supabase":
            query = self.supabase_client.table("executions").select("*")
            
            if trigger_id:
                query = query.eq("trigger_id", trigger_id)
            
            if event_id:
                query = query.eq("event_id", event_id)
            
            if status:
                query = query.eq("status", status)
            
            response = query.order("started_at", desc=True).range(offset, offset + limit - 1).execute()
            
            for execution in response.data:
                executions.append(EventExecution(**execution))
        
        return executions

    # Notification methods
    def add_notification(self, trigger_id: str, event_id: str, 
                        title: str, message: str, 
                        execution_id: Optional[str] = None) -> str:
        """Add a new notification to the database.
        
        Args:
            trigger_id: The ID of the trigger.
            event_id: The ID of the event.
            title: The title of the notification.
            message: The message of the notification.
            execution_id: The ID of the execution.
            
        Returns:
            The ID of the new notification.
        """
        notification_id = str(uuid.uuid4())
        timestamp = time.time()
        
        if self.db_type == "sqlite":
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO notifications (id, trigger_id, event_id, execution_id, title, message, timestamp) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (notification_id, trigger_id, event_id, execution_id, title, message, timestamp)
            )
            self.conn.commit()
        elif self.db_type == "supabase":
            self.supabase_client.table("notifications").insert({
                "id": notification_id,
                "trigger_id": trigger_id,
                "event_id": event_id,
                "execution_id": execution_id,
                "title": title,
                "message": message,
                "timestamp": timestamp,
                "read": False
            }).execute()
        
        self.logger.info(f"Added notification {notification_id} for trigger {trigger_id}, event {event_id}")
        return notification_id

    def mark_notification_read(self, notification_id: str):
        """Mark a notification as read.
        
        Args:
            notification_id: The ID of the notification.
        """
        if self.db_type == "sqlite":
            cursor = self.conn.cursor()
            cursor.execute("UPDATE notifications SET read = 1 WHERE id = ?", (notification_id,))
            self.conn.commit()
        elif self.db_type == "supabase":
            self.supabase_client.table("notifications").update({"read": True}).eq("id", notification_id).execute()
        
        self.logger.debug(f"Marked notification {notification_id} as read")

    def get_notification(self, notification_id: str) -> Optional[Notification]:
        """Get a notification by ID.
        
        Args:
            notification_id: The ID of the notification.
            
        Returns:
            The notification, or None if not found.
        """
        if self.db_type == "sqlite":
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM notifications WHERE id = ?", (notification_id,))
            row = cursor.fetchone()
            
            if row:
                return Notification(
                    id=row["id"],
                    trigger_id=row["trigger_id"],
                    event_id=row["event_id"],
                    execution_id=row["execution_id"],
                    title=row["title"],
                    message=row["message"],
                    timestamp=row["timestamp"],
                    read=bool(row["read"])
                )
        elif self.db_type == "supabase":
            response = self.supabase_client.table("notifications").select("*").eq("id", notification_id).execute()
            if response.data:
                notification = response.data[0]
                return Notification(**notification)
        
        return None

    def get_notifications(self, read: Optional[bool] = None, 
                         limit: int = 100, offset: int = 0) -> List[Notification]:
        """Get a list of notifications.
        
        Args:
            read: Filter by read status.
            limit: The maximum number of notifications to return.
            offset: The offset to start from.
            
        Returns:
            A list of notifications.
        """
        notifications = []
        
        if self.db_type == "sqlite":
            cursor = self.conn.cursor()
            query = "SELECT * FROM notifications"
            params = []
            
            if read is not None:
                query += " WHERE read = ?"
                params.append(int(read))
            
            query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            
            for row in cursor.fetchall():
                notifications.append(Notification(
                    id=row["id"],
                    trigger_id=row["trigger_id"],
                    event_id=row["event_id"],
                    execution_id=row["execution_id"],
                    title=row["title"],
                    message=row["message"],
                    timestamp=row["timestamp"],
                    read=bool(row["read"])
                ))
        elif self.db_type == "supabase":
            query = self.supabase_client.table("notifications").select("*")
            
            if read is not None:
                query = query.eq("read", read)
            
            response = query.order("timestamp", desc=True).range(offset, offset + limit - 1).execute()
            
            for notification in response.data:
                notifications.append(Notification(**notification))
        
        return notifications

    def close(self):
        """Close the database connection."""
        if self.db_type == "sqlite" and hasattr(self, "conn"):
            self.conn.close()
            self.logger.debug("Closed SQLite database connection")
