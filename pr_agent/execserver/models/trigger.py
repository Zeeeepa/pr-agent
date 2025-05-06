from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class TriggerType(str, Enum):
    """
    Types of triggers that can be configured
    """
    CODEFILE = "codefile"
    GITHUB_ACTION = "github_action"
    GITHUB_WORKFLOW = "github_workflow"
    PR_COMMENT = "pr_comment"


class EventType(str, Enum):
    """
    GitHub event types that can trigger actions
    """
    PUSH = "push"
    PULL_REQUEST = "pull_request"
    PULL_REQUEST_REVIEW = "pull_request_review"
    PULL_REQUEST_REVIEW_COMMENT = "pull_request_review_comment"
    ISSUES = "issues"
    ISSUE_COMMENT = "issue_comment"
    CREATE = "create"
    DELETE = "delete"
    RELEASE = "release"
    WORKFLOW_RUN = "workflow_run"


class TriggerCondition(BaseModel):
    """
    Conditions for when a trigger should fire
    """
    event_type: EventType = Field(..., description="Type of GitHub event to listen for")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Filters to apply to the event")


class TriggerAction(BaseModel):
    """
    Action to take when a trigger fires
    """
    action_type: TriggerType = Field(..., description="Type of action to take")
    action_data: Dict[str, Any] = Field(..., description="Data needed to execute the action")


class Trigger(BaseModel):
    """
    Model representing a trigger configuration
    """
    id: str = Field(..., description="Unique identifier for the trigger")
    name: str = Field(..., description="Name of the trigger")
    project_id: str = Field(..., description="ID of the project this trigger is associated with")
    conditions: List[TriggerCondition] = Field(..., description="Conditions that will fire this trigger")
    actions: List[TriggerAction] = Field(..., description="Actions to take when the trigger fires")
    enabled: bool = Field(default=True, description="Whether this trigger is enabled")

    class Config:
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "PR Comment Trigger",
                "project_id": "123456789",
                "conditions": [
                    {
                        "event_type": "pull_request",
                        "filters": {
                            "action": "opened"
                        }
                    }
                ],
                "actions": [
                    {
                        "action_type": "pr_comment",
                        "action_data": {
                            "comment_text": "Thank you for your contribution! Our team will review this PR soon."
                        }
                    }
                ],
                "enabled": True
            }
        }
