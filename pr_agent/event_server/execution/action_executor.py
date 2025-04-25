"""
GitHub Action execution module for the Event Server Executor.
"""

import asyncio
import json
import os
import time
import traceback
from typing import Any, Dict, Optional

from pr_agent.log import get_logger
from pr_agent.servers.github_action_runner import get_setting_or_env, run_action

from ..db.models import Event, Execution, ExecutionStatus, Trigger


class ActionExecutor:
    """Executor for running GitHub Actions."""
    
    def __init__(self, timeout: int = 300):
        """Initialize the action executor.
        
        Args:
            timeout: Maximum execution time in seconds.
        """
        self.logger = get_logger()
        self.timeout = timeout
    
    async def execute_action(self, action_params: Dict[str, Any], event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a GitHub Action.
        
        Args:
            action_params: Parameters for the GitHub Action.
            event_data: Event data to pass to the action.
            
        Returns:
            Dictionary with execution results.
        """
        start_time = time.time()
        
        try:
            # Set environment variables for the action
            self._set_environment_variables(action_params, event_data)
            
            # Run the action
            await run_action()
            
            duration = time.time() - start_time
            
            return {
                "success": True,
                "output": "GitHub Action executed successfully",
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
        finally:
            # Clean up environment variables
            self._clean_environment_variables(action_params)
    
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
            # Get the action parameters from the trigger
            action_params = trigger.execution_params
            if not action_params:
                raise ValueError("No action parameters specified in trigger")
            
            # Execute the action asynchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.execute_action(action_params, event.data))
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
    
    def _set_environment_variables(self, action_params: Dict[str, Any], event_data: Dict[str, Any]):
        """Set environment variables for the GitHub Action.
        
        Args:
            action_params: Parameters for the GitHub Action.
            event_data: Event data to pass to the action.
        """
        # Set GitHub token
        os.environ["GITHUB_TOKEN"] = os.environ.get("GITHUB_TOKEN") or action_params.get("github_token", "")
        
        # Set GitHub event name and path
        os.environ["GITHUB_EVENT_NAME"] = action_params.get("event_name", event_data.get("event", ""))
        
        # Create a temporary file for the event payload
        event_path = os.path.join(os.getcwd(), "event.json")
        with open(event_path, "w") as f:
            json.dump(event_data, f)
        os.environ["GITHUB_EVENT_PATH"] = event_path
        
        # Set OpenAI key and org if provided
        if "openai_key" in action_params:
            os.environ["OPENAI_KEY"] = action_params["openai_key"]
        if "openai_org" in action_params:
            os.environ["OPENAI_ORG"] = action_params["openai_org"]
        
        # Set additional environment variables
        for key, value in action_params.get("env", {}).items():
            os.environ[key] = str(value)
    
    def _clean_environment_variables(self, action_params: Dict[str, Any]):
        """Clean up environment variables after the GitHub Action.
        
        Args:
            action_params: Parameters for the GitHub Action.
        """
        # Remove GitHub event path file
        event_path = os.environ.get("GITHUB_EVENT_PATH")
        if event_path and os.path.exists(event_path):
            try:
                os.unlink(event_path)
            except:
                pass
        
        # Remove environment variables
        for key in ["GITHUB_TOKEN", "GITHUB_EVENT_NAME", "GITHUB_EVENT_PATH", "OPENAI_KEY", "OPENAI_ORG"]:
            if key in os.environ:
                del os.environ[key]
        
        # Remove additional environment variables
        for key in action_params.get("env", {}).keys():
            if key in os.environ:
                del os.environ[key]
