from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class Event(BaseModel):
    """
    Model representing a GitHub event
    """
    id: str = Field(..., description="Unique identifier for the event")
    event_type: str = Field(..., description="Type of GitHub event (e.g., push, pull_request)")
    repository: str = Field(..., description="Repository full name (e.g., owner/repo)")
    payload: Dict[str, Any] = Field(..., description="Event payload data")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Event creation timestamp")
    processed: bool = Field(default=False, description="Whether the event has been processed")
    processed_at: Optional[datetime] = Field(default=None, description="When the event was processed")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "event_type": "pull_request",
                "repository": "owner/repo",
                "payload": {
                    "action": "opened",
                    "number": 123,
                    "pull_request": {
                        "title": "Fix bug in login component",
                        "body": "This PR fixes a bug in the login component"
                    }
                },
                "created_at": "2023-01-01T00:00:00Z",
                "processed": False,
                "processed_at": None
            }
        }
