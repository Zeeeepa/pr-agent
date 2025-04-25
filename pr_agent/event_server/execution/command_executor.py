"""
PR-Agent command execution module for the Event Server Executor.
"""

import asyncio
import time
import traceback
from typing import Any, Dict, Optional

from pr_agent.agent.pr_agent import PRAgent
from pr_agent.log import get_logger

from ..db.models import Event, Execution, ExecutionStatus, Trigger


class CommandExecutor:
    """Executor for running PR-Agent commands."""
    
    def __init__(self, timeout: int = 300):
        """Initialize the command executor.
        
        Args:
            timeout: Maximum execution time in seconds.
        """
        self.logger = get_logger()
        self.timeout = timeout
    
    async def execute_command(self, command: str, pr_url: str) -> Dict[str, Any]:
        """Execute a PR-Agent command.
        
        Args:
            command: PR-Agent command to execute.
            pr_url: URL of the PR to run the command on.
            
        Returns:
            Dictionary with execution results.
        """
        start_time = time.time()
        
        try:
            # Create a PR-Agent instance
            agent = PRAgent()
            
            # Execute the command
            result = await agent.handle_request(pr_url, command)
            
            duration = time.time() - start_time
            
            return {
                "success": True,
                "output": result,
                "duration": duration
            }
        except Exception as e:
            duration = time.time() - start_time
            
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
                "duration": duration
            }
    
    def execute_trigger(self, trigger: Trigger, event: Event) -> Execution:
        """Execute a trigger with an event.
        
        Args:
            trigger: Trigger to execute.
            event: Event that triggered the execution.
            
        Returns:
            Execution object with results.
        """
        execution = Execution(
            event_id=event.id,
            trigger_id=trigger.id,
            status=ExecutionStatus.RUNNING
        )
        
        start_time = time.time()
        
        try:
            # Get the command and PR URL from the trigger parameters and event data
            command = trigger.execution_params.get("command")
            if not command:
                raise ValueError("No command specified in trigger parameters")
            
            # Extract PR URL from the event data
            pr_url = self._extract_pr_url(event)
            if not pr_url:
                raise ValueError("Could not extract PR URL from event data")
            
            # Execute the command asynchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.execute_command(command, pr_url))
            loop.close()
            
            # Update the execution with the results
            execution.end_time = time.time()
            execution.duration = execution.end_time - start_time
            
            if result["success"]:
                execution.status = ExecutionStatus.SUCCESS
                execution.result = {"output": result.get("output", "")}
            else:
                execution.status = ExecutionStatus.FAILED
                execution.error = result.get("error", "Unknown error")
                execution.result = {"traceback": result.get("traceback", "")}
        
        except Exception as e:
            # Handle any exceptions during execution
            execution.end_time = time.time()
            execution.duration = execution.end_time - start_time
            execution.status = ExecutionStatus.FAILED
            execution.error = str(e)
            execution.result = {"traceback": traceback.format_exc()}
        
        return execution
    
    def _extract_pr_url(self, event: Event) -> Optional[str]:
        """Extract PR URL from event data.
        
        Args:
            event: Event to extract PR URL from.
            
        Returns:
            PR URL if found, None otherwise.
        """
        data = event.data
        
        # For pull_request events
        if event.type == "pull_request" and "pull_request" in data:
            return data["pull_request"].get("html_url") or data["pull_request"].get("url")
        
        # For issue_comment events on PRs
        if event.type == "issue_comment" and "issue" in data and "pull_request" in data["issue"]:
            return data["issue"]["pull_request"].get("html_url") or data["issue"]["pull_request"].get("url")
        
        # For pull_request_review events
        if event.type == "pull_request_review" and "pull_request" in data:
            return data["pull_request"].get("html_url") or data["pull_request"].get("url")
        
        # For pull_request_review_comment events
        if event.type == "pull_request_review_comment" and "pull_request" in data:
            return data["pull_request"].get("html_url") or data["pull_request"].get("url")
        
        return None
