from typing import List, Optional

from pydantic import BaseModel, Field


class Project(BaseModel):
    """
    Model representing a GitHub project
    """
    id: str = Field(..., description="Unique identifier for the project")
    name: str = Field(..., description="Project name")
    full_name: str = Field(..., description="Full name of the repository (owner/repo)")
    description: Optional[str] = Field(None, description="Project description")
    html_url: str = Field(..., description="URL to the project on GitHub")
    api_url: str = Field(..., description="GitHub API URL for the project")
    default_branch: str = Field(..., description="Default branch of the repository")

    class Config:
        schema_extra = {
            "example": {
                "id": "123456789",
                "name": "my-project",
                "full_name": "owner/my-project",
                "description": "A sample project",
                "html_url": "https://github.com/owner/my-project",
                "api_url": "https://api.github.com/repos/owner/my-project",
                "default_branch": "main"
            }
        }
