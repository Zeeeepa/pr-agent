import os
import sys
import importlib.util
import subprocess
import tempfile
from typing import Dict, Any, Optional, List
import asyncio
import json

from ..config import ENABLE_NOTIFICATIONS


class WorkflowService:
    """
    Service for executing workflows and codefiles
    """
    def __init__(self):
        """Initialize the workflow service"""
        pass
    
    async def execute_codefile(self, filepath: str, repository: str, event_data: Dict[str, Any]) -> bool:
        """
        Execute a Python codefile
        
        Args:
            filepath: Path to the codefile
            repository: Repository full name (owner/repo)
            event_data: Event data to pass to the codefile
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(filepath):
                print(f"Codefile not found: {filepath}")
                return False
            
            # Create a temporary file with the event data
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                json.dump(event_data, temp_file)
                temp_file_path = temp_file.name
            
            try:
                # Execute the codefile with the event data as an argument
                result = subprocess.run(
                    [sys.executable, filepath, temp_file_path, repository],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                print(f"Codefile executed successfully: {result.stdout}")
                
                # Show notification if enabled
                if ENABLE_NOTIFICATIONS:
                    await self.show_notification(
                        title=f"Workflow Executed: {os.path.basename(filepath)}",
                        message=f"Repository: {repository}\nStatus: Success"
                    )
                
                return True
            finally:
                # Clean up the temporary file
                os.unlink(temp_file_path)
        except Exception as e:
            print(f"Error executing codefile: {e}")
            
            # Show notification if enabled
            if ENABLE_NOTIFICATIONS:
                await self.show_notification(
                    title=f"Workflow Failed: {os.path.basename(filepath)}",
                    message=f"Repository: {repository}\nError: {str(e)}"
                )
            
            return False
    
    async def execute_python_code(self, code: str, repository: str, event_data: Dict[str, Any]) -> bool:
        """
        Execute Python code directly
        
        Args:
            code: Python code to execute
            repository: Repository full name (owner/repo)
            event_data: Event data to pass to the code
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create a temporary file with the code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_code_file:
                temp_code_file.write(code)
                temp_code_path = temp_code_file.name
            
            # Create a temporary file with the event data
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_data_file:
                json.dump(event_data, temp_data_file)
                temp_data_path = temp_data_file.name
            
            try:
                # Execute the code with the event data as an argument
                result = subprocess.run(
                    [sys.executable, temp_code_path, temp_data_path, repository],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                print(f"Code executed successfully: {result.stdout}")
                
                # Show notification if enabled
                if ENABLE_NOTIFICATIONS:
                    await self.show_notification(
                        title=f"Code Executed Successfully",
                        message=f"Repository: {repository}\nStatus: Success"
                    )
                
                return True
            finally:
                # Clean up the temporary files
                os.unlink(temp_code_path)
                os.unlink(temp_data_path)
        except Exception as e:
            print(f"Error executing code: {e}")
            
            # Show notification if enabled
            if ENABLE_NOTIFICATIONS:
                await self.show_notification(
                    title=f"Code Execution Failed",
                    message=f"Repository: {repository}\nError: {str(e)}"
                )
            
            return False
    
    async def show_notification(self, title: str, message: str) -> None:
        """
        Show a desktop notification
        
        Args:
            title: Notification title
            message: Notification message
        """
        if sys.platform == 'win32':
            # Windows notification
            try:
                from win10toast import ToastNotifier
                toaster = ToastNotifier()
                toaster.show_toast(title, message, duration=5)
            except ImportError:
                print("win10toast not installed. Install with: pip install win10toast")
        elif sys.platform == 'darwin':
            # macOS notification
            try:
                subprocess.run(['osascript', '-e', f'display notification "{message}" with title "{title}"'])
            except Exception as e:
                print(f"Error showing macOS notification: {e}")
        else:
            # Linux notification
            try:
                subprocess.run(['notify-send', title, message])
            except Exception as e:
                print(f"Error showing Linux notification: {e}")
