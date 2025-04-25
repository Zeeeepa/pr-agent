"""
Database models for the Event Server Executor.
"""

import datetime
import enum
import json
import uuid
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class EventType(str, enum.Enum):
    """GitHub event types."""
    PULL_REQUEST = "pull_request"
    ISSUE = "issue"
    ISSUE_COMMENT = "issue_comment"
    PUSH = "push"
    PULL_REQUEST_REVIEW = "pull_request_review"
    PULL_REQUEST_REVIEW_COMMENT = "pull_request_review_comment"
    COMMIT_COMMENT = "commit_comment"
    CREATE = "create"
    DELETE = "delete"
    RELEASE = "release"
    WORKFLOW_RUN = "workflow_run"
    WORKFLOW_JOB = "workflow_job"
    CHECK_RUN = "check_run"
    CHECK_SUITE = "check_suite"
    OTHER = "other"


class ExecutionType(str, enum.Enum):
    """Types of execution that can be triggered."""
    CODEFILE = "codefile"
    GITHUB_ACTION = "github_action"
    PR_AGENT_COMMAND = "pr_agent_command"


class ExecutionStatus(str, enum.Enum):
    """Status of an execution."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"


class Event(BaseModel):
    """GitHub event model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: EventType
    action: Optional[str] = None
    repository: str
    sender: Optional[str] = None
    data: Dict[str, Any]
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)

    class Config:
        orm_mode = True


class Trigger(BaseModel):
    """Trigger configuration model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    repository: str
    event_type: EventType
    event_action: Optional[str] = None
    execution_type: ExecutionType
    execution_params: Dict[str, Any]
    notifications: Dict[str, bool] = Field(default_factory=lambda: {"windows": True})
    enabled: bool = True
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)

    class Config:
        orm_mode = True


class Execution(BaseModel):
    """Execution model for tracking triggered executions."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_id: str
    trigger_id: str
    status: ExecutionStatus = ExecutionStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    start_time: datetime.datetime = Field(default_factory=datetime.datetime.now)
    end_time: Optional[datetime.datetime] = None
    duration: Optional[float] = None

    class Config:
        orm_mode = True


class Notification(BaseModel):
    """Notification model for tracking sent notifications."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    execution_id: str
    type: str  # windows, email, etc.
    status: str  # success, failed
    message: str
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)

    class Config:
        orm_mode = True


# Database models for SQLite
class SQLModels:
    """SQL table definitions for SQLite."""
    
    EVENTS_TABLE = """
    CREATE TABLE IF NOT EXISTS events (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL,
        action TEXT,
        repository TEXT NOT NULL,
        sender TEXT,
        data TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
    """
    
    TRIGGERS_TABLE = """
    CREATE TABLE IF NOT EXISTS triggers (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        repository TEXT NOT NULL,
        event_type TEXT NOT NULL,
        event_action TEXT,
        execution_type TEXT NOT NULL,
        execution_params TEXT NOT NULL,
        notifications TEXT NOT NULL,
        enabled INTEGER NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """
    
    EXECUTIONS_TABLE = """
    CREATE TABLE IF NOT EXISTS executions (
        id TEXT PRIMARY KEY,
        event_id TEXT NOT NULL,
        trigger_id TEXT NOT NULL,
        status TEXT NOT NULL,
        result TEXT,
        error TEXT,
        start_time TEXT NOT NULL,
        end_time TEXT,
        duration REAL,
        FOREIGN KEY (event_id) REFERENCES events (id),
        FOREIGN KEY (trigger_id) REFERENCES triggers (id)
    )
    """
    
    NOTIFICATIONS_TABLE = """
    CREATE TABLE IF NOT EXISTS notifications (
        id TEXT PRIMARY KEY,
        execution_id TEXT NOT NULL,
        type TEXT NOT NULL,
        status TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (execution_id) REFERENCES executions (id)
    )
    """
    
    @classmethod
    def get_all_tables(cls) -> List[str]:
        """Get all table creation SQL statements."""
        return [
            cls.EVENTS_TABLE,
            cls.TRIGGERS_TABLE,
            cls.EXECUTIONS_TABLE,
            cls.NOTIFICATIONS_TABLE
        ]


def serialize_model(model: BaseModel) -> Dict[str, Any]:
    """Serialize a Pydantic model for database storage."""
    data = model.dict()
    for key, value in data.items():
        if isinstance(value, (datetime.datetime, datetime.date)):
            data[key] = value.isoformat()
        elif isinstance(value, enum.Enum):
            data[key] = value.value
        elif isinstance(value, dict):
            data[key] = json.dumps(value)
    return data


def deserialize_event(data: Dict[str, Any]) -> Event:
    """Deserialize an event from database storage."""
    if isinstance(data.get("data"), str):
        data["data"] = json.loads(data["data"])
    if isinstance(data.get("timestamp"), str):
        data["timestamp"] = datetime.datetime.fromisoformat(data["timestamp"])
    return Event(**data)


def deserialize_trigger(data: Dict[str, Any]) -> Trigger:
    """Deserialize a trigger from database storage."""
    if isinstance(data.get("execution_params"), str):
        data["execution_params"] = json.loads(data["execution_params"])
    if isinstance(data.get("notifications"), str):
        data["notifications"] = json.loads(data["notifications"])
    if isinstance(data.get("created_at"), str):
        data["created_at"] = datetime.datetime.fromisoformat(data["created_at"])
    if isinstance(data.get("updated_at"), str):
        data["updated_at"] = datetime.datetime.fromisoformat(data["updated_at"])
    return Trigger(**data)


def deserialize_execution(data: Dict[str, Any]) -> Execution:
    """Deserialize an execution from database storage."""
    if isinstance(data.get("result"), str) and data["result"]:
        data["result"] = json.loads(data["result"])
    if isinstance(data.get("start_time"), str):
        data["start_time"] = datetime.datetime.fromisoformat(data["start_time"])
    if isinstance(data.get("end_time"), str) and data["end_time"]:
        data["end_time"] = datetime.datetime.fromisoformat(data["end_time"])
    return Execution(**data)


def deserialize_notification(data: Dict[str, Any]) -> Notification:
    """Deserialize a notification from database storage."""
    if isinstance(data.get("timestamp"), str):
        data["timestamp"] = datetime.datetime.fromisoformat(data["timestamp"])
    return Notification(**data)
