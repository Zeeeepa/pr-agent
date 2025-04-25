import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys
from fastapi.testclient import TestClient

# Import the modules to test
from pr_agent.execserver.app import app
from pr_agent.execserver.models.event import Event
from pr_agent.execserver.models.project import Project
from pr_agent.execserver.models.trigger import Trigger, TriggerCondition, TriggerAction, EventType, TriggerType
from pr_agent.execserver.models.workflow import Workflow, WorkflowRun
from pr_agent.execserver.services.db_service import DatabaseService
from pr_agent.execserver.services.github_service import GitHubService
from pr_agent.execserver.services.event_service import EventService
from pr_agent.execserver.services.workflow_service import WorkflowService


class TestExecServer(unittest.TestCase):
    """Test cases for the ExecServer module"""

    def setUp(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
        
        # Mock the services
        self.mock_db_service = MagicMock(spec=DatabaseService)
        self.mock_github_service = MagicMock(spec=GitHubService)
        self.mock_workflow_service = MagicMock(spec=WorkflowService)
        self.mock_event_service = MagicMock(spec=EventService)

    def test_health_check(self):
        """Test the health check endpoint"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy"})

    @patch('pr_agent.execserver.api.routes.db_service')
    def test_get_projects(self, mock_db_service):
        """Test getting all projects"""
        # Setup mock
        mock_projects = [
            Project(
                id="123456789",
                name="my-project",
                full_name="owner/my-project",
                description="A sample project",
                html_url="https://github.com/owner/my-project",
                api_url="https://api.github.com/repos/owner/my-project",
                default_branch="main"
            )
        ]
        mock_db_service.get_projects.return_value = mock_projects
        
        # Make request
        response = self.client.get("/api/v1/projects")
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["name"], "my-project")

    @patch('pr_agent.execserver.api.routes.github_service')
    def test_get_workflows(self, mock_github_service):
        """Test getting workflows for a repository"""
        # Setup mock
        mock_workflows = [
            Workflow(
                id="123456789",
                name="CI/CD Pipeline",
                path=".github/workflows/ci-cd.yml",
                state="active",
                created_at="2023-01-01T00:00:00Z",
                updated_at="2023-01-01T00:00:00Z",
                url="https://api.github.com/repos/owner/repo/actions/workflows/123456789",
                html_url="https://github.com/owner/repo/actions/workflows/ci-cd.yml",
                badge_url="https://github.com/owner/repo/workflows/CI%2FCD%20Pipeline/badge.svg"
            )
        ]
        mock_github_service.get_workflows.return_value = mock_workflows
        
        # Make request
        response = self.client.get("/api/v1/workflows?repository=owner/repo")
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["name"], "CI/CD Pipeline")

    @patch('pr_agent.execserver.api.routes.event_service')
    def test_get_events(self, mock_event_service):
        """Test getting recent events"""
        # Setup mock
        mock_events = [
            Event(
                id="123e4567-e89b-12d3-a456-426614174000",
                event_type="pull_request",
                repository="owner/repo",
                payload={
                    "action": "opened",
                    "number": 123,
                    "pull_request": {
                        "title": "Fix bug in login component",
                        "body": "This PR fixes a bug in the login component"
                    }
                },
                created_at="2023-01-01T00:00:00Z",
                processed=False,
                processed_at=None
            )
        ]
        mock_event_service.get_recent_events.return_value = mock_events
        
        # Make request
        response = self.client.get("/api/v1/events")
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["event_type"], "pull_request")


if __name__ == '__main__':
    unittest.main()
