"""
Code executor for Event Server Executor.

This module provides functionality to execute code when events are triggered.
"""

import asyncio
import importlib.util
import os
import sys
import tempfile
import traceback
from typing import Any, Dict, Optional

from pr_agent.log import get_logger
from pr_agent.event_server_executor.db.manager import DatabaseManager
from pr_agent.event_server_executor.db.models import EventTrigger, GitHubEvent


class CodeExecutor:
    """Code executor for Event Server Executor."""

    def __init__(self, db_manager: DatabaseManager):
        """Initialize the code executor.
        
        Args:
            db_manager: The database manager to use.
        """
        self.logger = get_logger()
        self.db_manager = db_manager

    async def execute(self, trigger: EventTrigger, event: GitHubEvent) -> str:
        """Execute code for a trigger.
        
        Args:
            trigger: The trigger to execute.
            event: The event that triggered the execution.
            
        Returns:
            The output of the execution.
        """
        self.logger.info(f"Executing code for trigger {trigger.id} ({trigger.name})")
        
        # Check if the code file exists
        if not os.path.exists(trigger.codefile_path):
            raise FileNotFoundError(f"Code file not found: {trigger.codefile_path}")
        
        # Create a temporary directory for execution
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy the code file to the temporary directory
            temp_file_path = os.path.join(temp_dir, os.path.basename(trigger.codefile_path))
            with open(trigger.codefile_path, "r") as src_file:
                code = src_file.read()
            
            with open(temp_file_path, "w") as dst_file:
                dst_file.write(code)
            
            # Load the module
            module_name = os.path.splitext(os.path.basename(trigger.codefile_path))[0]
            spec = importlib.util.spec_from_file_location(module_name, temp_file_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not load module from {temp_file_path}")
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Check if the module has a handle_event function
            if not hasattr(module, "handle_event"):
                raise AttributeError(f"Module {module_name} does not have a handle_event function")
            
            # Execute the handle_event function
            try:
                # Check if the function is async
                if asyncio.iscoroutinefunction(module.handle_event):
                    output = await module.handle_event(event.payload, event.event_type, event.action)
                else:
                    output = module.handle_event(event.payload, event.event_type, event.action)
                
                return str(output) if output is not None else "No output"
            except Exception as e:
                self.logger.error(f"Error executing handle_event function: {str(e)}")
                self.logger.error(traceback.format_exc())
                raise
