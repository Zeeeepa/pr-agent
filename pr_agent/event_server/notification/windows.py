"""
Windows notification module for the Event Server Executor.
"""

import os
import platform
import subprocess
from typing import Optional

from pr_agent.log import get_logger


class WindowsNotifier:
    """Windows notification handler."""
    
    def __init__(self):
        """Initialize the Windows notifier."""
        self.logger = get_logger()
        self.enabled = self._is_windows() and self._check_notification_enabled()
    
    def _is_windows(self) -> bool:
        """Check if the current platform is Windows."""
        return platform.system() == "Windows"
    
    def _check_notification_enabled(self) -> bool:
        """Check if notifications are enabled in the environment."""
        return os.environ.get("NOTIFICATION_ENABLED", "true").lower() == "true"
    
    def send_notification(self, title: str, message: str, icon: Optional[str] = None) -> bool:
        """Send a Windows notification.
        
        Args:
            title: Notification title.
            message: Notification message.
            icon: Optional path to an icon file.
            
        Returns:
            True if the notification was sent successfully, False otherwise.
        """
        if not self.enabled:
            self.logger.info("Windows notifications are disabled or not supported on this platform")
            return False
        
        try:
            # Use PowerShell to send a Windows notification
            powershell_script = f"""
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

            $APP_ID = "Event Server Executor"

            $template = @"
            <toast>
                <visual>
                    <binding template="ToastGeneric">
                        <text>{title}</text>
                        <text>{message}</text>
                    </binding>
                </visual>
            </toast>
            "@

            $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
            $xml.LoadXml($template)
            $toast = New-Object Windows.UI.Notifications.ToastNotification $xml
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($APP_ID).Show($toast)
            """
            
            # Execute the PowerShell script
            subprocess.run(["powershell", "-Command", powershell_script], 
                          capture_output=True, text=True, check=True)
            
            self.logger.info(f"Sent Windows notification: {title}")
            return True
        except Exception as e:
            self.logger.error(f"Error sending Windows notification: {e}")
            return False
    
    def send_trigger_notification(self, trigger_name: str, event_type: str, 
                                 repository: str, status: str) -> bool:
        """Send a notification for a trigger execution.
        
        Args:
            trigger_name: Name of the trigger.
            event_type: Type of the event.
            repository: Repository name.
            status: Execution status.
            
        Returns:
            True if the notification was sent successfully, False otherwise.
        """
        title = f"Trigger '{trigger_name}' {status.capitalize()}"
        message = f"Event: {event_type}\nRepository: {repository}"
        
        # Choose icon based on status
        icon = None
        if status.lower() == "success":
            icon = "✅"
        elif status.lower() == "failed":
            icon = "❌"
        
        return self.send_notification(title, message, icon)
    
    def send_event_notification(self, event_type: str, repository: str, 
                               action: Optional[str] = None) -> bool:
        """Send a notification for a new event.
        
        Args:
            event_type: Type of the event.
            repository: Repository name.
            action: Optional event action.
            
        Returns:
            True if the notification was sent successfully, False otherwise.
        """
        action_str = f" ({action})" if action else ""
        title = f"New {event_type}{action_str} Event"
        message = f"Repository: {repository}"
        
        return self.send_notification(title, message)
