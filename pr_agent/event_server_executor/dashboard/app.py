"""
Dashboard app for Event Server Executor.

This module provides a dashboard for configuring event triggers and code execution.
"""

import os
from typing import Dict, List, Optional

import gradio as gr

from pr_agent.log import get_logger
from pr_agent.event_server_executor.db.manager import DatabaseManager
from pr_agent.event_server_executor.db.models import EventTrigger, GitHubEvent


class Dashboard:
    """Dashboard for Event Server Executor."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """Initialize the dashboard.
        
        Args:
            db_manager: The database manager to use. If None, a new one will be created.
        """
        self.logger = get_logger()
        self.db_manager = db_manager or DatabaseManager(
            db_type=os.environ.get("EVENT_DB_TYPE", "sqlite")
        )

    def build_ui(self):
        """Build the dashboard UI."""
        with gr.Blocks(title="Event Server Executor Dashboard") as app:
            gr.Markdown("# Event Server Executor Dashboard")
            
            with gr.Tabs():
                with gr.TabItem("Events"):
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("## Events")
                            events_table = gr.Dataframe(
                                headers=["ID", "Type", "Action", "Repository", "Sender", "Timestamp", "Processed"],
                                datatype=["str", "str", "str", "str", "str", "str", "bool"],
                                row_count=10,
                                col_count=(7, "fixed"),
                            )
                            refresh_events_btn = gr.Button("Refresh Events")
                        
                        with gr.Column():
                            gr.Markdown("## Event Details")
                            event_id_input = gr.Textbox(label="Event ID")
                            event_details = gr.JSON(label="Event Payload")
                            get_event_btn = gr.Button("Get Event Details")
                
                with gr.TabItem("Triggers"):
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("## Triggers")
                            triggers_table = gr.Dataframe(
                                headers=["ID", "Name", "Repository", "Event Type", "Action", "Codefile Path", "Enabled", "Notify", "Created At", "Last Triggered"],
                                datatype=["str", "str", "str", "str", "str", "str", "bool", "bool", "str", "str"],
                                row_count=10,
                                col_count=(10, "fixed"),
                            )
                            refresh_triggers_btn = gr.Button("Refresh Triggers")
                        
                        with gr.Column():
                            gr.Markdown("## Add Trigger")
                            trigger_name = gr.Textbox(label="Name")
                            trigger_repository = gr.Textbox(label="Repository")
                            trigger_event_type = gr.Dropdown(
                                label="Event Type",
                                choices=[
                                    "push",
                                    "pull_request",
                                    "issues",
                                    "issue_comment",
                                    "pull_request_review",
                                    "pull_request_review_comment",
                                    "create",
                                    "delete",
                                    "release",
                                    "fork",
                                    "watch",
                                    "star",
                                    "workflow_run",
                                    "workflow_job",
                                    "check_run",
                                    "check_suite",
                                    "status",
                                    "deployment",
                                    "deployment_status",
                                    "gollum",
                                    "label",
                                    "member",
                                    "milestone",
                                    "package",
                                    "page_build",
                                    "project",
                                    "project_card",
                                    "project_column",
                                    "public",
                                    "pull_request_target",
                                    "repository",
                                    "repository_dispatch",
                                    "team",
                                    "team_add",
                                    "workflow_dispatch",
                                ],
                            )
                            trigger_action = gr.Textbox(label="Action (optional)")
                            trigger_codefile_path = gr.Textbox(label="Codefile Path")
                            trigger_enabled = gr.Checkbox(label="Enabled", value=True)
                            trigger_notify = gr.Checkbox(label="Notify", value=True)
                            add_trigger_btn = gr.Button("Add Trigger")
                            add_trigger_result = gr.Textbox(label="Result")
                
                with gr.TabItem("Executions"):
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("## Executions")
                            executions_table = gr.Dataframe(
                                headers=["ID", "Trigger ID", "Event ID", "Status", "Started At", "Completed At"],
                                datatype=["str", "str", "str", "str", "str", "str"],
                                row_count=10,
                                col_count=(6, "fixed"),
                            )
                            refresh_executions_btn = gr.Button("Refresh Executions")
                        
                        with gr.Column():
                            gr.Markdown("## Execution Details")
                            execution_id_input = gr.Textbox(label="Execution ID")
                            execution_output = gr.Textbox(label="Output", lines=10)
                            execution_error = gr.Textbox(label="Error", lines=5)
                            get_execution_btn = gr.Button("Get Execution Details")
                
                with gr.TabItem("Notifications"):
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("## Notifications")
                            notifications_table = gr.Dataframe(
                                headers=["ID", "Trigger ID", "Event ID", "Execution ID", "Title", "Timestamp", "Read"],
                                datatype=["str", "str", "str", "str", "str", "str", "bool"],
                                row_count=10,
                                col_count=(7, "fixed"),
                            )
                            refresh_notifications_btn = gr.Button("Refresh Notifications")
                            mark_all_read_btn = gr.Button("Mark All as Read")
                        
                        with gr.Column():
                            gr.Markdown("## Notification Details")
                            notification_id_input = gr.Textbox(label="Notification ID")
                            notification_title = gr.Textbox(label="Title")
                            notification_message = gr.Textbox(label="Message", lines=5)
                            get_notification_btn = gr.Button("Get Notification Details")
                            mark_read_btn = gr.Button("Mark as Read")
            
            # Events tab functions
            def refresh_events():
                events = self.db_manager.get_events(limit=100)
                return [[
                    event.id,
                    event.event_type,
                    event.action or "",
                    event.repository,
                    event.sender,
                    event.formatted_timestamp,
                    event.processed
                ] for event in events]
            
            def get_event_details(event_id):
                event = self.db_manager.get_event(event_id)
                if event:
                    return event.payload
                return {}
            
            # Triggers tab functions
            def refresh_triggers():
                triggers = self.db_manager.get_triggers()
                return [[
                    trigger.id,
                    trigger.name,
                    trigger.repository,
                    trigger.event_type,
                    trigger.action or "",
                    trigger.codefile_path,
                    trigger.enabled,
                    trigger.notify,
                    trigger.formatted_created_at,
                    trigger.formatted_last_triggered or ""
                ] for trigger in triggers]
            
            def add_trigger(name, repository, event_type, action, codefile_path, enabled, notify):
                if not name or not repository or not event_type or not codefile_path:
                    return "Error: All fields except Action are required"
                
                try:
                    trigger_id = self.db_manager.add_trigger(
                        name=name,
                        repository=repository,
                        event_type=event_type,
                        action=action if action else None,
                        codefile_path=codefile_path,
                        enabled=enabled,
                        notify=notify
                    )
                    return f"Success: Added trigger {trigger_id}"
                except Exception as e:
                    return f"Error: {str(e)}"
            
            # Executions tab functions
            def refresh_executions():
                executions = self.db_manager.get_executions(limit=100)
                return [[
                    execution.id,
                    execution.trigger_id,
                    execution.event_id,
                    execution.status,
                    execution.formatted_started_at,
                    execution.formatted_completed_at or ""
                ] for execution in executions]
            
            def get_execution_details(execution_id):
                execution = self.db_manager.get_execution(execution_id)
                if execution:
                    return execution.output or "", execution.error or ""
                return "", ""
            
            # Notifications tab functions
            def refresh_notifications():
                notifications = self.db_manager.get_notifications(limit=100)
                return [[
                    notification.id,
                    notification.trigger_id,
                    notification.event_id,
                    notification.execution_id or "",
                    notification.title,
                    notification.formatted_timestamp,
                    notification.read
                ] for notification in notifications]
            
            def get_notification_details(notification_id):
                notification = self.db_manager.get_notification(notification_id)
                if notification:
                    return notification.title, notification.message
                return "", ""
            
            def mark_notification_read(notification_id):
                self.db_manager.mark_notification_read(notification_id)
                return refresh_notifications()
            
            def mark_all_notifications_read():
                notifications = self.db_manager.get_notifications(read=False)
                for notification in notifications:
                    self.db_manager.mark_notification_read(notification.id)
                return refresh_notifications()
            
            # Connect functions to UI elements
            refresh_events_btn.click(refresh_events, outputs=[events_table])
            get_event_btn.click(get_event_details, inputs=[event_id_input], outputs=[event_details])
            
            refresh_triggers_btn.click(refresh_triggers, outputs=[triggers_table])
            add_trigger_btn.click(
                add_trigger,
                inputs=[trigger_name, trigger_repository, trigger_event_type, trigger_action, trigger_codefile_path, trigger_enabled, trigger_notify],
                outputs=[add_trigger_result]
            )
            
            refresh_executions_btn.click(refresh_executions, outputs=[executions_table])
            get_execution_btn.click(get_execution_details, inputs=[execution_id_input], outputs=[execution_output, execution_error])
            
            refresh_notifications_btn.click(refresh_notifications, outputs=[notifications_table])
            get_notification_btn.click(get_notification_details, inputs=[notification_id_input], outputs=[notification_title, notification_message])
            mark_read_btn.click(mark_notification_read, inputs=[notification_id_input], outputs=[notifications_table])
            mark_all_read_btn.click(mark_all_notifications_read, outputs=[notifications_table])
            
            # Initialize tables
            app.load(refresh_events, outputs=[events_table])
            app.load(refresh_triggers, outputs=[triggers_table])
            app.load(refresh_executions, outputs=[executions_table])
            app.load(refresh_notifications, outputs=[notifications_table])
        
        return app

    def run(self, host: str = "0.0.0.0", port: int = 7860):
        """Run the dashboard.
        
        Args:
            host: The host to bind to.
            port: The port to bind to.
        """
        app = self.build_ui()
        app.launch(server_name=host, server_port=port)


def create_dashboard():
    """Create and return a new dashboard."""
    return Dashboard()


def run_dashboard():
    """Run the dashboard."""
    port = int(os.environ.get("DASHBOARD_PORT", "7860"))
    dashboard = create_dashboard()
    dashboard.run(port=port)
