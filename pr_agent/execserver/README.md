# PR-Agent ExeServer

PR-Agent ExeServer is a server component for PR-Agent that provides a web UI and API for managing GitHub repositories, events, and workflows.

## Features

- Web UI for managing PR-Agent settings and workflows
- API for integrating with GitHub and other services
- Event-driven architecture for handling GitHub webhooks
- Database storage for events, projects, triggers, and workflows
- Automatic database migrations

## Installation

### Prerequisites

- Python 3.9 or higher
- Supabase account and project (for database storage)
- GitHub account and personal access token

### Setup

1. Install PR-Agent with the execserver extra:

```bash
pip install "pr-agent[execserver]"
```

2. Set up environment variables:

```bash
# GitHub configuration
export GITHUB_TOKEN=your_github_token

# Supabase configuration
export SUPABASE_URL=your_supabase_url
export SUPABASE_ANON_KEY=your_supabase_anon_key
```

3. Run the server:

```bash
pr-agent-server
```

## Configuration

### Environment Variables

- `GITHUB_TOKEN`: GitHub personal access token
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_ANON_KEY`: Supabase anonymous key
- `UI_PORT`: Port for the web UI (default: 8000)
- `API_PORT`: Port for the API (default: 8001)

### Configuration File

You can also use a configuration file (`pr_agent.toml`) to set these values:

```toml
[execserver]
github_token = "your_github_token"
supabase_url = "your_supabase_url"
supabase_anon_key = "your_supabase_anon_key"
ui_port = 8000
api_port = 8001
```

## Database Setup

PR-Agent ExeServer uses Supabase as its database backend. The database schema is automatically created and migrated when the server starts.

### Manual Database Setup

If you prefer to set up the database manually, you can find the SQL migration files in the `pr_agent/execserver/migrations` directory.

### Database Schema

The database schema includes the following tables:

- `migrations`: Tracks applied database migrations
- `events`: Stores GitHub webhook events
- `projects`: Stores information about GitHub repositories
- `triggers`: Stores event triggers and actions
- `workflows`: Stores GitHub workflow information
- `workflow_runs`: Stores GitHub workflow run information
- `settings`: Stores application settings

## API Endpoints

### Settings

- `GET /api/v1/settings`: Get all settings
- `POST /api/v1/settings`: Save settings
- `POST /api/v1/settings/validate`: Validate settings

### Projects

- `GET /api/v1/projects`: Get all projects
- `GET /api/v1/projects/github`: Get all GitHub repositories
- `GET /api/v1/projects/{project_id}`: Get a project by ID

### Triggers

- `GET /api/v1/triggers`: Get all triggers
- `POST /api/v1/triggers`: Create a new trigger
- `GET /api/v1/triggers/{trigger_id}`: Get a trigger by ID
- `PATCH /api/v1/triggers/{trigger_id}`: Update a trigger

### Workflows

- `GET /api/v1/workflows`: Get all workflows for a repository
- `GET /api/v1/workflow_runs`: Get workflow runs for a repository
- `POST /api/v1/workflows/{workflow_id}/dispatch`: Trigger a workflow

### Events

- `GET /api/v1/events`: Get recent events

### GitHub Webhooks

- `POST /api/v1/github_webhooks`: Handle GitHub webhook events

## Troubleshooting

### Database Connection Issues

If you encounter database connection issues:

1. Verify that your Supabase URL and API key are correct
2. Check that your Supabase project is active
3. Ensure your IP address is not blocked by Supabase

### GitHub API Issues

If you encounter GitHub API issues:

1. Verify that your GitHub token is correct and has the necessary permissions
2. Check that your GitHub token has not expired
3. Ensure you are not hitting GitHub API rate limits

## Development

### Running in Development Mode

```bash
cd pr_agent/execserver
python app.py
```

### Running Tests

```bash
pytest tests/execserver
```

## License

PR-Agent is licensed under the Apache License 2.0. See the LICENSE file for details.
