from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class WorkflowStatus(str, Enum):
    """
    Status of a GitHub workflow
    """
    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPLETED = "completed"
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowTrigger(str, Enum):
    """
    Types of workflow triggers
    """
    PUSH = "push"
    PULL_REQUEST = "pull_request"
    SCHEDULE = "schedule"
    WORKFLOW_DISPATCH = "workflow_dispatch"
    REPOSITORY_DISPATCH = "repository_dispatch"
    ON_DEMAND = "on_demand"
    CONTINUOUS = "continuous"


class Workflow(BaseModel):
    """
    Model representing a GitHub workflow
    """
    id: str = Field(..., description="Unique identifier for the workflow")
    name: str = Field(..., description="Name of the workflow")
    repository: str = Field(..., description="Repository full name (owner/repo)")
    path: str = Field(..., description="Path to the workflow file in the repository")
    status: WorkflowStatus = Field(..., description="Current status of the workflow")
    trigger: WorkflowTrigger = Field(..., description="Trigger type for the workflow")
    html_url: str = Field(..., description="URL to the workflow on GitHub")
    api_url: str = Field(..., description="GitHub API URL for the workflow")

    class Config:
        schema_extra = {
            "example": {
                "id": "123456789",
                "name": "CI/CD Pipeline",
                "repository": "owner/repo",
                "path": ".github/workflows/ci-cd.yml",
                "status": "active",
                "trigger": "push",
                "html_url": "https://github.com/owner/repo/actions/workflows/ci-cd.yml",
                "api_url": "https://api.github.com/repos/owner/repo/actions/workflows/123456789"
            }
        }


class WorkflowRun(BaseModel):
    """
    Model representing a GitHub workflow run
    """
    id: str = Field(..., description="Unique identifier for the workflow run")
    workflow_id: str = Field(..., description="ID of the workflow")
    repository: str = Field(..., description="Repository full name (owner/repo)")
    trigger: str = Field(..., description="What triggered this workflow run")
    status: WorkflowStatus = Field(..., description="Status of the workflow run")
    conclusion: Optional[str] = Field(None, description="Conclusion of the workflow run")
    created_at: datetime = Field(..., description="When the workflow run was created")
    updated_at: datetime = Field(..., description="When the workflow run was last updated")
    html_url: str = Field(..., description="URL to the workflow run on GitHub")
    api_url: str = Field(..., description="GitHub API URL for the workflow run")

    class Config:
        schema_extra = {
            "example": {
                "id": "987654321",
                "workflow_id": "123456789",
                "repository": "owner/repo",
                "trigger": "Push to main",
                "status": "completed",
                "conclusion": "success",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:05:00Z",
                "html_url": "https://github.com/owner/repo/actions/runs/987654321",
                "api_url": "https://api.github.com/repos/owner/repo/actions/runs/987654321"
            }
        }
