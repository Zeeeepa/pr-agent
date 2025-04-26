# PR-Agent ExeServer

ExeServer is an extension to PR-Agent that provides a dashboard for managing GitHub events, workflows, and triggers. It allows you to create custom event triggers that can execute codefiles, GitHub Actions, or GitHub Workflows in response to GitHub events.

## Features

- **Event Triggers**: Create custom triggers that execute actions in response to GitHub events
- **GitHub Workflow Management**: View and manage GitHub workflows and workflow runs
- **Event Logging**: Log and view all GitHub events
- **AI Assistant**: Chat with an AI assistant to help with project management
- **Project Requirements**: Track project requirements and their status

## Integration with PR-Agent

ExecServer leverages existing PR-Agent components for better integration and reduced code duplication:

- **GitHub Provider**: Uses `pr_agent.git_providers.github_provider.GithubProvider` for all GitHub API interactions
- **Webhook Handling**: Integrates with `pr_agent.servers.github_app` for processing GitHub events
- **GitHub Actions**: Uses `pr_agent.servers.github_action_runner` for executing GitHub Actions

This integration ensures that ExecServer benefits from improvements made to the core PR-Agent components and maintains consistent behavior across the application.

## Architecture

ExecServer is built on top of PR-Agent and leverages its existing functionality for GitHub integration. The main components are:

- **API Server**: FastAPI server that provides REST endpoints for the dashboard
- **Database**: Supabase database for storing events, triggers, and other data
- **UI**: Web-based dashboard for managing triggers, workflows, and events

## Installation

1. Clone the PR-Agent repository:
   ```bash
   git clone https://github.com/Zeeeepa/pr-agent.git
   cd pr-agent
   ```

2. Install the package in development mode:
   ```bash
   pip install -e .
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file to add your GitHub token, Supabase URL, and Supabase anonymous key.

5. Run the server from the project root directory:
   ```bash
   python -m pr_agent.execserver.app
   ```

6. Open the dashboard in your browser:
   ```
   http://localhost:8000
   ```

## Troubleshooting

### ModuleNotFoundError: No module named 'pr_agent'

If you encounter this error when running the application:

```
ModuleNotFoundError: No module named 'pr_agent'
```

This typically means the package is not installed in your Python environment. To fix this:

1. Make sure you're in the root directory of the PR-Agent project (not in the pr_agent subdirectory)
2. Install the package in development mode:
   ```bash
   pip install -e .
   ```
3. Try running the application again

### Dependency Conflicts

If you encounter dependency conflicts when installing requirements, make sure you're using the latest version of the requirements.txt file. The project requires specific versions of packages to work correctly:

- FastAPI 0.100.0+ (for Pydantic 2.x compatibility)
- Pydantic 2.x
- LiteLLM (compatible version)

## Testing

To run the ExecServer tests:

```bash
pytest tests/execserver/test_execserver.py -v
```

## Configuration

The following environment variables can be set in the `.env` file:

- `GITHUB_TOKEN`: GitHub personal access token
- `GITHUB_APP_ID`: GitHub App ID (if using GitHub App authentication)
- `GITHUB_APP_PRIVATE_KEY`: GitHub App private key (if using GitHub App authentication)
- `GITHUB_APP_INSTALLATION_ID`: GitHub App installation ID (if using GitHub App authentication)
- `GITHUB_WEBHOOK_SECRET`: Secret for verifying GitHub webhook signatures
- `SUPABASE_URL`: URL of your Supabase instance
- `SUPABASE_ANON_KEY`: Anonymous key for your Supabase instance
- `UI_PORT`: Port for the UI server (default: 8000)
- `API_PORT`: Port for the API server (default: 8001)
- `ENABLE_NOTIFICATIONS`: Enable desktop notifications (default: False)

## Usage

### Creating a Trigger

1. Go to the "Event Triggers" tab
2. Click "Create New Trigger"
3. Select a project, event type, and action
4. Configure the trigger conditions and action parameters
5. Click "Save"

### Viewing Workflows

1. Go to the "GitHub Workflows" tab
2. Select a repository
3. View active workflows and recent workflow runs
4. Click "Run" to manually trigger a workflow

### Viewing Events

1. Go to the "Recent Events" tab
2. View all GitHub events that have been received
3. Click "View Details" to see the full event payload

## Development

### Project Structure

```
pr_agent/execserver/
├── __init__.py
├── app.py                # Main application entry point
├── config.py             # Configuration settings
├── models/               # Data models
│   ├── __init__.py
│   ├── event.py          # Event data models
│   ├── project.py        # Project data models
│   ├── trigger.py        # Trigger data models
│   └── workflow.py       # Workflow data models
├── services/             # Business logic services
│   ├── __init__.py
│   ├── db_service.py     # Database interaction service
│   ├── event_service.py  # Event handling service
│   ├── github_service.py # GitHub API interaction service
│   └── workflow_service.py # Workflow execution service
├── api/                  # API routes and handlers
│   ├── __init__.py
│   └── routes.py         # API routes
└── ui/                   # UI components
    ├── __init__.py
    └── static/           # Static UI files
        └── index.html    # Main UI page
```

### Adding a New Feature

1. Define the data model in the `models/` directory
2. Add the business logic in the `services/` directory
3. Add API endpoints in the `api/routes.py` file
4. Add UI components in the `ui/static/` directory

## License

This project is licensed under the same license as PR-Agent.
