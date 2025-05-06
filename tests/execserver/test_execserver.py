import asyncio
import json
import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from pr_agent.execserver.app import app
from pr_agent.execserver.models.event import Event
from pr_agent.execserver.models.project import Project
from pr_agent.execserver.models.trigger import (EventType, Trigger,
                                                TriggerAction,
                                                TriggerCondition, TriggerType)
from pr_agent.execserver.models.workflow import (Workflow, WorkflowRun,
                                                 WorkflowStatus,
                                                 WorkflowTrigger)


class TestExeServer(unittest.TestCase):
    """Test cases for the ExeServer module"""

    def setUp(self):
        """Set up the test client"""
        self.client = TestClient(app)

    def test_health_check(self):
        """Test the health check endpoint"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy"})

    @patch('pr_agent.execserver.api.routes.event_service')
    @patch('pr_agent.execserver.api.routes.pr_agent_handle_github_webhooks')
    def test_github_webhooks(self, mock_pr_agent_handler, mock_event_service):
        """Test the GitHub webhooks endpoint"""
        # Mock the process_webhook method
        mock_event_service.process_webhook = AsyncMock(return_value=(True, None))
        mock_pr_agent_handler.return_value = {}

        # Test payload
        payload = {
            "repository": {
                "full_name": "owner/repo"
            },
            "action": "opened",
            "pull_request": {
                "number": 123,
                "title": "Test PR"
            }
        }

        # Send a request to the webhook endpoint
        response = self.client.post(
            "/api/v1/github_webhooks",
            json=payload,
            headers={"X-GitHub-Event": "pull_request"}
        )

        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "processing"})

        # Check that the process_webhook method was called with the correct arguments
        mock_event_service.process_webhook.assert_called_once()
        args, kwargs = mock_event_service.process_webhook.call_args
        self.assertEqual(args[0], "pull_request")
        self.assertEqual(args[1], payload)

    @patch('pr_agent.execserver.api.routes.db_service')
    def test_get_projects(self, mock_db_service):
        """Test the get_projects endpoint"""
        # Mock the get_projects method
        mock_project = Project(
            id="123",
            name="test-project",
            full_name="owner/test-project",
            description="Test project",
            html_url="https://github.com/owner/test-project",
            api_url="https://api.github.com/repos/owner/test-project",
            default_branch="main"
        )
        mock_db_service.get_projects = AsyncMock(return_value=[mock_project])

        # Send a request to the get_projects endpoint
        response = self.client.get("/api/v1/projects")

        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["id"], "123")
        self.assertEqual(response.json()[0]["name"], "test-project")

    @patch('pr_agent.execserver.api.routes.github_service')
    def test_get_workflows(self, mock_github_service):
        """Test the get_workflows endpoint"""
        # Mock the get_workflows method
        mock_workflow = Workflow(
            id="123",
            name="CI/CD Pipeline",
            repository="owner/repo",
            path=".github/workflows/ci-cd.yml",
            status=WorkflowStatus.ACTIVE,
            trigger=WorkflowTrigger.PUSH,
            html_url="https://github.com/owner/repo/actions/workflows/ci-cd.yml",
            api_url="https://api.github.com/repos/owner/repo/actions/workflows/123"
        )
        mock_github_service.get_workflows = AsyncMock(return_value=[mock_workflow])

        # Send a request to the get_workflows endpoint
        response = self.client.get("/api/v1/workflows?repository=owner/repo")

        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["id"], "123")
        self.assertEqual(response.json()[0]["name"], "CI/CD Pipeline")

    @patch('pr_agent.execserver.api.routes.event_service')
    def test_get_events(self, mock_event_service):
        """Test the get_events endpoint"""
        # Mock the get_recent_events method
        mock_event = Event(
            id="123",
            event_type="pull_request",
            repository="owner/repo",
            payload={
                "action": "opened",
                "pull_request": {
                    "number": 123,
                    "title": "Test PR"
                }
            },
            created_at="2023-01-01T00:00:00Z",
            processed=True,
            processed_at="2023-01-01T00:01:00Z"
        )
        mock_event_service.get_recent_events = AsyncMock(return_value=[mock_event])

        # Send a request to the get_events endpoint
        response = self.client.get("/api/v1/events?repository=owner/repo")

        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["id"], "123")
        self.assertEqual(response.json()[0]["event_type"], "pull_request")

    @patch('pr_agent.execserver.api.routes.workflow_service')
    def test_execute_code(self, mock_workflow_service):
        """Test the execute_code endpoint"""
        # Mock the execute_python_code method
        mock_workflow_service.execute_python_code = AsyncMock(return_value=True)

        # Test payload
        payload = {
            "code": "print('Hello, World!')",
            "repository": "owner/repo",
            "event_data": {
                "action": "opened",
                "pull_request": {
                    "number": 123,
                    "title": "Test PR"
                }
            }
        }

        # Send a request to the execute_code endpoint
        response = self.client.post("/api/v1/execute_code", json=payload)

        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "executed"})

        # Check that the execute_python_code method was called with the correct arguments
        mock_workflow_service.execute_python_code.assert_called_once()
        args, kwargs = mock_workflow_service.execute_python_code.call_args
        self.assertEqual(args[0], "print('Hello, World!')")
        self.assertEqual(args[1], "owner/repo")
        self.assertEqual(args[2], payload["event_data"])

    @patch('pr_agent.execserver.services.workflow_service.run_action')
    def test_execute_github_action(self, mock_run_action):
        """Test the execute_github_action method"""
        from pr_agent.execserver.services.workflow_service import \
            WorkflowService

        # Mock the run_action function
        mock_run_action.return_value = None

        # Create a workflow service instance
        workflow_service = WorkflowService()

        # Test inputs
        repository = "owner/repo"
        action_name = "test-action"
        inputs = {"param1": "value1", "param2": "value2"}

        # Call the method
        result = asyncio.run(workflow_service.execute_github_action(repository, action_name, inputs))

        # Check the result
        self.assertTrue(result)

        # Check that run_action was called
        mock_run_action.assert_called_once()

        # Check that environment variables were set correctly
        self.assertEqual(os.environ["GITHUB_REPOSITORY"], repository)
        self.assertEqual(os.environ["GITHUB_EVENT_NAME"], "workflow_dispatch")
        self.assertTrue("GITHUB_EVENT_PATH" in os.environ)


if __name__ == '__main__':
    unittest.main()
