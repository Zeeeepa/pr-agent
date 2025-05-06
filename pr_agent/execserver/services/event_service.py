import asyncio
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from ..models.event import Event
from ..models.trigger import EventType, Trigger, TriggerType
from .db_service import DatabaseService
from .github_service import GitHubService
from .workflow_service import WorkflowService


class EventService:
    """
    Service for handling GitHub events and triggering actions
    """
    def __init__(self, db_service: DatabaseService, github_service: GitHubService, workflow_service: WorkflowService):
        """
        Initialize the event service

        Args:
            db_service: Database service
            github_service: GitHub service
            workflow_service: Workflow service
        """
        self.db_service = db_service
        self.github_service = github_service
        self.workflow_service = workflow_service

    async def process_webhook(self, event_type: str, payload: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Process a GitHub webhook event

        Args:
            event_type: Type of GitHub event
            payload: Event payload data

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Extract repository information
            repository = payload.get("repository", {}).get("full_name")
            if not repository:
                return False, "Repository information not found in payload"

            # Log the event to the database
            event = await self.db_service.log_event(event_type, repository, payload)

            # Process the event
            await self.process_event(event)

            return True, None
        except Exception as e:
            return False, str(e)

    async def process_event(self, event: Event) -> None:
        """
        Process an event and trigger any matching actions

        Args:
            event: Event to process
        """
        try:
            # Get repository owner and name
            owner, repo = event.repository.split("/")

            # Get project from database
            project = None
            projects = await self.db_service.get_projects()
            for p in projects:
                if p.full_name == event.repository:
                    project = p
                    break

            if not project:
                # Project not found in database, try to get it from GitHub
                project_from_github = await self.github_service.get_repository(owner, repo)
                if project_from_github:
                    # Save to database
                    project = await self.db_service.create_project(project_from_github)

            if not project:
                print(f"Project not found for repository: {event.repository}")
                return

            # Get triggers for this project
            triggers = await self.db_service.get_triggers_for_project(project.id)

            # Find matching triggers
            matching_triggers = []
            for trigger in triggers:
                if not trigger.enabled:
                    continue

                for condition in trigger.conditions:
                    if condition.event_type == event.event_type:
                        # Check filters
                        matches = True
                        for key, value in condition.filters.items():
                            # Handle nested keys with dot notation (e.g., "pull_request.action")
                            if "." in key:
                                parts = key.split(".")
                                payload_value = event.payload
                                for part in parts:
                                    if part in payload_value:
                                        payload_value = payload_value[part]
                                    else:
                                        matches = False
                                        break

                                if matches and payload_value != value:
                                    matches = False
                            else:
                                if key in event.payload and event.payload[key] != value:
                                    matches = False

                        if matches:
                            matching_triggers.append(trigger)
                            break

            # Execute actions for matching triggers
            for trigger in matching_triggers:
                await self.execute_trigger_actions(trigger, event)

            # Mark event as processed
            await self.db_service.mark_event_processed(event.id)
        except Exception as e:
            print(f"Error processing event: {e}")

    async def execute_trigger_actions(self, trigger: Trigger, event: Event) -> None:
        """
        Execute actions for a trigger

        Args:
            trigger: Trigger to execute
            event: Event that triggered the action
        """
        for action in trigger.actions:
            try:
                if action.action_type == TriggerType.CODEFILE:
                    # Execute codefile
                    await self.workflow_service.execute_codefile(
                        action.action_data.get("filepath"),
                        event.repository,
                        event.payload
                    )

                elif action.action_type == TriggerType.GITHUB_ACTION:
                    # Trigger GitHub Action
                    owner, repo = event.repository.split("/")
                    await self.github_service.trigger_workflow(
                        owner,
                        repo,
                        action.action_data.get("workflow_id"),
                        action.action_data.get("ref"),
                        action.action_data.get("inputs")
                    )

                elif action.action_type == TriggerType.GITHUB_WORKFLOW:
                    # Trigger GitHub Workflow
                    owner, repo = event.repository.split("/")
                    await self.github_service.trigger_workflow(
                        owner,
                        repo,
                        action.action_data.get("workflow_id"),
                        action.action_data.get("ref"),
                        action.action_data.get("inputs")
                    )

                elif action.action_type == TriggerType.PR_COMMENT:
                    # Add comment to PR
                    if event.event_type == EventType.PULL_REQUEST:
                        owner, repo = event.repository.split("/")
                        pr_number = event.payload.get("pull_request", {}).get("number")
                        if pr_number:
                            await self.github_service.comment_on_pr(
                                owner,
                                repo,
                                pr_number,
                                action.action_data.get("comment_text", "")
                            )
            except Exception as e:
                print(f"Error executing action: {e}")

    async def get_recent_events(self, repository: Optional[str] = None, limit: int = 10) -> List[Event]:
        """
        Get recent events

        Args:
            repository: Optional repository to filter by
            limit: Maximum number of events to return

        Returns:
            List of Event objects
        """
        return await self.db_service.get_events(repository=repository, limit=limit)
