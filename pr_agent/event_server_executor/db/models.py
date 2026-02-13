"""
Database models for Event Server Executor.
"""

import json
import os
import sqlite3
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

import supabase
from pydantic import BaseModel


class GitHubEvent(BaseModel):
    """GitHub event model."""
    id: str
    event_type: str
    action: Optional[str] = None
    repository: str
    sender: str
    payload: Dict[str, Any]
    timestamp: float
    processed: bool = False

    @property
    def formatted_timestamp(self) -> str:
        """Return a formatted timestamp."""
        return datetime.fromtimestamp(self.timestamp).strftime("%Y-%m-%d %H:%M:%S")


class EventTrigger(BaseModel):
    """Event trigger model."""
    id: str
    name: str
    repository: str
    event_type: str
    action: Optional[str] = None
    codefile_path: str
    enabled: bool = True
    notify: bool = True
    created_at: float
    last_triggered: Optional[float] = None

    @property
    def formatted_created_at(self) -> str:
        """Return a formatted created_at timestamp."""
        return datetime.fromtimestamp(self.created_at).strftime("%Y-%m-%d %H:%M:%S")

    @property
    def formatted_last_triggered(self) -> Optional[str]:
        """Return a formatted last_triggered timestamp."""
        if self.last_triggered:
            return datetime.fromtimestamp(self.last_triggered).strftime("%Y-%m-%d %H:%M:%S")
        return None


class EventExecution(BaseModel):
    """Event execution model."""
    id: str
    trigger_id: str
    event_id: str
    status: str  # "success", "failure", "pending"
    output: Optional[str] = None
    error: Optional[str] = None
    started_at: float
    completed_at: Optional[float] = None

    @property
    def formatted_started_at(self) -> str:
        """Return a formatted started_at timestamp."""
        return datetime.fromtimestamp(self.started_at).strftime("%Y-%m-%d %H:%M:%S")

    @property
    def formatted_completed_at(self) -> Optional[str]:
        """Return a formatted completed_at timestamp."""
        if self.completed_at:
            return datetime.fromtimestamp(self.completed_at).strftime("%Y-%m-%d %H:%M:%S")
        return None


class Notification(BaseModel):
    """Notification model."""
    id: str
    trigger_id: str
    event_id: str
    execution_id: Optional[str] = None
    title: str
    message: str
    timestamp: float
    read: bool = False

    @property
    def formatted_timestamp(self) -> str:
        """Return a formatted timestamp."""
        return datetime.fromtimestamp(self.timestamp).strftime("%Y-%m-%d %H:%M:%S")
