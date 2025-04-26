# PR-Agent ExecServer

ExecServer is an extension to PR-Agent that provides a dashboard for managing GitHub events, workflows, and triggers. It allows you to create custom event triggers that can execute codefiles, GitHub Actions, or GitHub Workflows in response to GitHub events.

## Features

- **Event Triggers**: Create custom triggers that execute actions in response to GitHub events
- **GitHub Workflow Management**: View and manage GitHub workflows and workflow runs
- **Event Logging**: Log and view all GitHub events
- **AI Assistant**: Chat with an AI assistant to help with project management

## Architecture

ExecServer is built on top of PR-Agent and leverages its existing functionality for GitHub integration. The main components are:

- **API Server**: FastAPI server that provides REST endpoints for the dashboard
- **Database**: Supabase database for storing events, triggers, and other data
- **UI**: Web-based dashboard for managing triggers, workflows, and events

## Integration with PR-Agent

ExecServer is fully integrated with PR-Agent's existing components:

- Uses `pr_agent.git_providers.github_provider.GithubProvider` for all GitHub API interactions
- Uses `pr_agent.servers.github_app` for webhook handling
- Uses `pr_agent.servers.github_action_runner` for running GitHub Actions
- Uses PR-Agent's error handling and logging infrastructure

## Installation

### Prerequisites

- Python 3.12 or higher
- Git
- A GitHub account with access to repositories you want to monitor
- Supabase account (for database storage)

### Installation Steps

1. Clone the PR-Agent repository:
   ```bash
   git clone https://github.com/Zeeeepa/pr-agent.git
   cd pr-agent
   ```

2. Install the package in development mode:
   ```bash
   pip install -e .
   ```

   This installs the package in editable mode, which means changes to the code will be reflected immediately without reinstalling.

3. Install additional dependencies:
   ```bash
   pip install fastapi uvicorn supabase
   ```

   For Windows users who want desktop notifications:
   ```bash
   pip install win10toast
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file to add your GitHub token, Supabase URL, and Supabase anonymous key.

5. Run the server:
   ```bash
   # From the project root directory
   python -m pr_agent.execserver.app
   ```

   If you're inside the execserver directory, make sure to run:
   ```bash
   # From the pr_agent/execserver directory
   cd ../..  # Go back to project root
   python -m pr_agent.execserver.app
   ```

6. Open the dashboard in your browser:
   ```
   http://localhost:8000
   ```

## Troubleshooting

### ModuleNotFoundError: No module named 'pr_agent'

This error occurs when Python cannot find the pr_agent package. This typically happens when:

1. You're running the app from inside the pr_agent directory structure
2. The package is not installed

Solutions:
- Make sure you're running the app from the project root directory
- Install the package in development mode: `pip install -e .` from the project root
- Add the project root to your PYTHONPATH: `export PYTHONPATH=$PYTHONPATH:/path/to/pr-agent`

### Other Common Issues

- **GitHub Authentication Errors**: Make sure your GitHub token has the necessary permissions
- **Supabase Connection Errors**: Verify your Supabase URL and anonymous key
- **Port Already in Use**: Change the port in the .env file if 8000 is already in use

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

## Testing

ExecServer includes a comprehensive test suite in `tests/execserver/test_execserver.py`. To run the tests:

```bash
# From the project root
pytest tests/execserver/test_execserver.py
```

## License

This project is licensed under the same license as PR-Agent.
