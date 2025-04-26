# PR-Agent ExeServer

ExeServer is an extension to PR-Agent that provides a dashboard for managing GitHub events, workflows, and triggers. It allows you to create custom event triggers that can execute codefiles, GitHub Actions, or GitHub Workflows in response to GitHub events.

## Features

- **Event Triggers**: Create custom triggers that execute actions in response to GitHub events
- **GitHub Workflow Management**: View and manage GitHub workflows and workflow runs
- **Event Logging**: Log and view all GitHub events
- **AI Assistant**: Chat with an AI assistant to help with project management
- **Project Requirements**: Track project requirements and their status

## Integration with PR-Agent

ExeServer leverages existing PR-Agent components for better integration and reduced code duplication:

- **GitHub API Integration**: Uses `pr_agent.git_providers.github_provider.GithubProvider` for all GitHub API interactions
- **Webhook Handling**: Integrates with `pr_agent.servers.github_app` for processing GitHub events
- **GitHub Actions**: Uses `pr_agent.servers.github_action_runner` for running GitHub Actions
- **Configuration Management**: Leverages PR-Agent's configuration system for consistent settings

## Installation

### Prerequisites

- Python 3.8 or higher
- A Supabase account and project (for database storage)
- GitHub token or GitHub App credentials

### Step 1: Clone and Install the Repository

1. Clone the PR-Agent repository:
   ```bash
   git clone https://github.com/Zeeeepa/pr-agent.git
   cd pr-agent
   ```

2. Install the package in development mode:
   ```bash
   pip install -e .
   ```

   This is crucial as it makes the `pr_agent` package available to the Python interpreter, preventing the "ModuleNotFoundError: No module named 'pr_agent'" error.

3. Install additional dependencies:
   ```bash
   pip install supabase python-dotenv psycopg2
   ```

### Step 2: Configure Supabase

1. Create a Supabase project at https://supabase.com
2. Create the following tables in your Supabase database:
   - `events`
   - `projects`
   - `triggers`
   - `workflows`
   - `workflow_runs`

3. Get your Supabase URL and anon key from your Supabase project settings

### Step 3: Set Up Environment Variables

1. Create a `.env` file in the root directory:
   ```bash
   cp .env.example .env
   ```

2. Add your GitHub and Supabase credentials to the `.env` file:
   ```
   # GitHub credentials
   GITHUB_TOKEN=your_github_token
   
   # Supabase credentials
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

### Step 4: Run the Server

1. Make sure you're in the PR-Agent root directory (not inside the pr_agent directory)
2. Run the server:
   ```bash
   python -m pr_agent.execserver.app
   ```

3. Open the dashboard in your browser:
   ```
   http://localhost:8000
   ```

## Troubleshooting

### ModuleNotFoundError: No module named 'pr_agent'

This error occurs when Python cannot find the `pr_agent` package. To fix it:

1. Make sure you've installed the package in development mode:
   ```bash
   pip install -e .
   ```

2. Make sure you're running the server from the correct directory:
   ```bash
   # Run from the PR-Agent root directory, not from inside pr_agent/execserver
   python -m pr_agent.execserver.app
   ```

3. Check that your Python environment has the correct path:
   ```bash
   python -c "import sys; print(sys.path)"
   ```

### Supabase Connection Issues

If you're having trouble connecting to Supabase:

1. Verify your Supabase URL and anon key in the `.env` file
2. Make sure your Supabase project is active and the database is running
3. Check that you've created the required tables in your Supabase database
4. Ensure your IP address is allowed in Supabase's network restrictions

## Testing

To run the ExecServer tests:

```bash
# Run from the PR-Agent root directory
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
