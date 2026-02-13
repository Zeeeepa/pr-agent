"""
Windows notifications for Event Server Executor.

This module provides functionality to send Windows notifications.
"""

import os
import platform
import subprocess
from typing import Optional

from pr_agent.log import get_logger


class WindowsNotifier:
    """Windows notifier for Event Server Executor."""

    def __init__(self):
        """Initialize the Windows notifier."""
        self.logger = get_logger()
        self.enabled = platform.system() == "Windows"
        
        if not self.enabled:
            self.logger.warning("Windows notifications are only available on Windows")

    def send_notification(self, title: str, message: str, icon: Optional[str] = None) -> bool:
        """Send a Windows notification.
        
        Args:
            title: The title of the notification.
            message: The message of the notification.
            icon: The path to the icon to use. If None, the default icon will be used.
            
        Returns:
            True if the notification was sent successfully, False otherwise.
        """
        if not self.enabled:
            self.logger.warning("Windows notifications are only available on Windows")
            return False
        
        try:
            # Use PowerShell to send a notification
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
            subprocess.run(["powershell", "-Command", powershell_script], check=True)
            
            self.logger.info(f"Sent Windows notification: {title}")
            return True
        except Exception as e:
            self.logger.error(f"Error sending Windows notification: {str(e)}")
            return False
