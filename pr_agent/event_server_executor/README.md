# Event Server Executor

Event Server Executor is an extension for PR-agent that provides functionality to:

1. Capture and store GitHub events in a database
2. Configure event triggers for specific GitHub events
3. Execute custom code when events are triggered
4. Send notifications when actions are performed

## Features

- **Event Logging**: Capture and store all GitHub webhook events in a database
- **Event Triggers**: Configure triggers for specific GitHub events
- **Code Execution**: Execute custom Python code when events are triggered
- **Notifications**: Send notifications when actions are performed
- **Dashboard**: Web-based dashboard for managing triggers and viewing events

## Installation

1. Clone the PR-agent repository:
   ```bash
   git clone https://github.com/Zeeeepa/pr-agent.git
   cd pr-agent
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   pip install gradio supabase
   ```

3. Set up environment variables:
   ```bash
   # GitHub token for API access
   export GITHUB_TOKEN=your_github_token
   
   # Database configuration (optional, defaults to SQLite)
   export EVENT_DB_TYPE=sqlite  # or "supabase"
   export EVENT_DB_PATH=events.db
   
   # Supabase configuration (only if using Supabase)
   export SUPABASE_URL=your_supabase_url
   export SUPABASE_ANON_KEY=your_supabase_anon_key
   
   # Notification configuration (optional)
   export ENABLE_WINDOWS_NOTIFICATIONS=true
   ```

## Usage

### Running the Server

To run the event server:

```bash
python -m pr_agent.event_server_executor.main --server-only
```

This will start the server on port 3000 by default. You can specify a different port with the `--server-port` option.

### Running the Dashboard

To run the dashboard:

```bash
python -m pr_agent.event_server_executor.main --dashboard-only
```

This will start the dashboard on port 7860 by default. You can specify a different port with the `--dashboard-port` option.

### Running Both

To run both the server and dashboard:

```bash
python -m pr_agent.event_server_executor.main
```

### Setting Up GitHub Webhooks

1. Go to your GitHub repository settings
2. Click on "Webhooks" and then "Add webhook"
3. Set the Payload URL to `http://your-server-url:3000/api/webhooks/github`
4. Set the Content type to `application/json`
5. Select the events you want to receive
6. Click "Add webhook"

### Creating Event Handlers

Event handlers are Python modules that define a `handle_event` function. The function takes three arguments:

- `payload`: The event payload
- `event_type`: The type of event
- `action`: The action of the event

Example:

```python
def handle_event(payload, event_type, action):
    if event_type == "issue_comment" and action == "created":
        # Do something with the comment
        return "Processed comment"
    return "Ignored event"
```

Save your event handler as a Python file, then create a trigger in the dashboard that points to this file.

## API Endpoints

The server provides the following API endpoints:

- `POST /api/webhooks/github`: Receive GitHub webhook events
- `GET /api/events`: Get a list of events
- `GET /api/events/{event_id}`: Get an event by ID
- `GET /api/triggers`: Get a list of triggers
- `POST /api/triggers`: Add a new trigger
- `GET /api/triggers/{trigger_id}`: Get a trigger by ID
- `PUT /api/triggers/{trigger_id}`: Update a trigger
- `DELETE /api/triggers/{trigger_id}`: Delete a trigger
- `GET /api/executions`: Get a list of executions
- `GET /api/executions/{execution_id}`: Get an execution by ID
- `GET /api/notifications`: Get a list of notifications
- `GET /api/notifications/{notification_id}`: Get a notification by ID
- `PUT /api/notifications/{notification_id}/read`: Mark a notification as read

## Examples

See the `examples` directory for example event handlers:

- `pr_comment_handler.py`: Responds to PR comments that start with "/hello"

## License

This project is licensed under the same license as PR-agent.
