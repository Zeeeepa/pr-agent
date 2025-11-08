"""
Notification manager for Event Server Executor.

This module provides functionality to manage notifications.
"""

import os
from typing import Optional

from pr_agent.log import get_logger
from pr_agent.event_server_executor.db.manager import DatabaseManager
from pr_agent.event_server_executor.notifications.windows import WindowsNotifier


class NotificationManager:
    """Notification manager for Event Server Executor."""

    def __init__(self, db_manager: DatabaseManager):
        """Initialize the notification manager.
        
        Args:
            db_manager: The database manager to use.
        """
        self.logger = get_logger()
        self.db_manager = db_manager
        self.windows_notifier = WindowsNotifier()
        self.enable_windows_notifications = os.environ.get("ENABLE_WINDOWS_NOTIFICATIONS", "true").lower() == "true"

    def send_notification(self, trigger_id: str, event_id: str, title: str, message: str, 
                         execution_id: Optional[str] = None) -> str:
        """Send a notification.
        
        Args:
            trigger_id: The ID of the trigger.
            event_id: The ID of the event.
            title: The title of the notification.
            message: The message of the notification.
            execution_id: The ID of the execution.
            
        Returns:
            The ID of the new notification.
        """
        # Add the notification to the database
        notification_id = self.db_manager.add_notification(
            trigger_id=trigger_id,
            event_id=event_id,
            execution_id=execution_id,
            title=title,
            message=message
        )
        
        # Send Windows notification if enabled
        if self.enable_windows_notifications:
            self.windows_notifier.send_notification(title, message)
        
        return notification_id
