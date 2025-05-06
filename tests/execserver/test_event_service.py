import asyncio
import json
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

from pr_agent.execserver.models.event import Event
from pr_agent.execserver.models.trigger import (EventType, Trigger,
                                                TriggerAction,
                                                TriggerCondition, TriggerType)
from pr_agent.execserver.services.db_service import DatabaseService
from pr_agent.execserver.services.event_service import EventService
from pr_agent.execserver.services.github_service import GitHubService
from pr_agent.execserver.services.workflow_service import WorkflowService


@pytest.fixture
def event_service():
    """Create a mock event service for testing."""
    db_service = MagicMock(spec=DatabaseService)
    github_service = MagicMock(spec=GitHubService)
    workflow_service = MagicMock(spec=WorkflowService)

    return EventService(db_service, github_service, workflow_service)

@pytest.mark.asyncio
async def test_process_webhook(event_service):
    """Test processing a webhook event."""
    # Mock the log_event method to return a test event
    event_service.db_service.log_event.return_value = Event(
        id="test-event-id",
        event_type="pull_request",
        repository="test/repo",
        payload={
            "action": "opened",
            "number": 1,
            "pull_request": {
                "title": "Test PR",
                "body": "This is a test PR"
            }
        },
        processed=False,
        processed_at=None
    )

    # Mock the process_event method
    event_service.process_event = MagicMock()

    # Process a webhook
    event_type = "pull_request"
    payload = {
        "action": "opened",
        "number": 1,
        "pull_request": {
            "title": "Test PR",
            "body": "This is a test PR"
        },
        "repository": {
            "full_name": "test/repo"
        }
    }

    success, error = await event_service.process_webhook(event_type, payload)

    # Verify the event was logged and processed
    assert success is True
    assert error is None
    event_service.db_service.log_event.assert_called_once_with(event_type, "test/repo", payload)
    event_service.process_event.assert_called_once()

@pytest.mark.asyncio
async def test_execute_trigger_actions(event_service):
    """Test executing trigger actions."""
    # Create a test trigger
    trigger = Trigger(
        id="test-trigger-id",
        name="Test Trigger",
        project_id="test-project-id",
        conditions=[
            TriggerCondition(
                event_type=EventType.PULL_REQUEST,
                filters={"action": "opened"}
            )
        ],
        actions=[
            TriggerAction(
                action_type=TriggerType.PR_COMMENT,
                action_data={"comment_text": "Thank you for your contribution!"}
            )
        ],
        enabled=True
    )

    # Create a test event
    event = Event(
        id="test-event-id",
        event_type="pull_request",
        repository="test/repo",
        payload={
            "action": "opened",
            "number": 1,
            "pull_request": {
                "title": "Test PR",
                "body": "This is a test PR"
            }
        },
        processed=False,
        processed_at=None
    )

    # Execute the trigger actions
    await event_service.execute_trigger_actions(trigger, event)

    # Verify the PR comment action was executed
    event_service.github_service.comment_on_pr.assert_called_once_with(
        "test", "repo", 1, "Thank you for your contribution!"
    )
