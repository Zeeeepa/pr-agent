"""
Code execution module for the Event Server Executor.
"""

import importlib.util
import os
import subprocess
import sys
import tempfile
import time
import traceback
from typing import Any, Dict, Optional

from pr_agent.log import get_logger

from ..db.models import Event, Execution, ExecutionStatus, Trigger


class CodeExecutor:
    """Executor for running Python code files."""
    
    def __init__(self, timeout: int = 30):
        """Initialize the code executor.
        
        Args:
            timeout: Maximum execution time in seconds.
        """
        self.logger = get_logger()
        self.timeout = timeout
    
    def execute_code(self, code: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Python code with event data.
        
        Args:
            code: Python code to execute.
            event_data: Event data to pass to the code.
            
        Returns:
            Dictionary with execution results.
        """
        # Create a temporary file for the code
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as temp_file:
            temp_file_path = temp_file.name
            
            # Add event data to the code
            full_code = f"""
import json
import os
import sys
import traceback

# Event data from GitHub webhook
event_data = {event_data}

# Main code
try:
{self._indent_code(code, 4)}
except Exception as e:
    print(json.dumps({{"error": str(e), "traceback": traceback.format_exc()}}))
    sys.exit(1)
"""
            temp_file.write(full_code)
        
        try:
            # Execute the code in a separate process with timeout
            start_time = time.time()
            process = subprocess.Popen(
                [sys.executable, temp_file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            try:
                stdout, stderr = process.communicate(timeout=self.timeout)
                duration = time.time() - start_time
                
                if process.returncode != 0:
                    # Try to parse error from stdout (might be JSON)
                    try:
                        error_data = json.loads(stdout)
                        error_message = error_data.get("error", stderr)
                        error_traceback = error_data.get("traceback", "")
                    except:
                        error_message = stderr
                        error_traceback = ""
                    
                    return {
                        "success": False,
                        "error": error_message,
                        "traceback": error_traceback,
                        "duration": duration
                    }
                
                return {
                    "success": True,
                    "output": stdout,
                    "duration": duration
                }
            except subprocess.TimeoutExpired:
                process.kill()
                return {
                    "success": False,
                    "error": f"Execution timed out after {self.timeout} seconds",
                    "duration": self.timeout
                }
        finally:
            # Clean up the temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass
    
    def execute_file(self, file_path: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a Python file with event data.
        
        Args:
            file_path: Path to the Python file to execute.
            event_data: Event data to pass to the code.
            
        Returns:
            Dictionary with execution results.
        """
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        try:
            with open(file_path, "r") as f:
                code = f.read()
            
            return self.execute_code(code, event_data)
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
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
            # Get the code file path from the trigger parameters
            file_path = trigger.execution_params.get("file_path")
            if not file_path:
                raise ValueError("No file path specified in trigger parameters")
            
            # Execute the code file
            result = self.execute_file(file_path, event.data)
            
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
    
    def _indent_code(self, code: str, spaces: int) -> str:
        """Indent code by a specified number of spaces.
        
        Args:
            code: Code to indent.
            spaces: Number of spaces to indent by.
            
        Returns:
            Indented code.
        """
        indent = " " * spaces
        return "\n".join(indent + line for line in code.splitlines())
