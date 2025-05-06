# Webhook Setup and Real-time Notifications

This document provides information on setting up and using webhooks with PR-Agent to receive real-time notifications for repository events.

## Overview

PR-Agent uses webhooks to receive instant notifications when repository events occur, such as PR creation, updates, or merges. This allows PR-Agent to respond to these events in real-time, providing automated feedback and analysis.

## Supported Git Providers

PR-Agent supports webhooks from the following Git providers:

- GitHub (via GitHub Apps)
- GitLab
- Azure DevOps
- Bitbucket Server

## Webhook Setup

### GitHub App

1. Create a GitHub App with the following permissions:
   - Repository permissions:
     - Contents: Read
     - Issues: Read & Write
     - Pull requests: Read & Write
     - Metadata: Read
   - Subscribe to events:
     - Pull request
     - Pull request review
     - Pull request review comment
     - Issue comment

2. Generate a webhook secret and configure the webhook URL to point to your PR-Agent server:
   ```
   https://your-pr-agent-server.com/api/v1/github_webhooks
   ```

3. Install the GitHub App on your repositories.

### GitLab

1. Go to your GitLab project settings > Webhooks.

2. Add a new webhook with the following URL:
   ```
   https://your-pr-agent-server.com/webhook
   ```

3. Select the following events:
   - Merge request events
   - Comments

4. Add a secret token for security.

5. Save the webhook.

### Azure DevOps

1. Go to your Azure DevOps project settings > Service hooks.

2. Add a new webhook with the following URL:
   ```
   https://your-pr-agent-server.com/
   ```

3. Configure the webhook to trigger on:
   - Pull request created
   - Pull request updated
   - Pull request commented on

4. Configure basic authentication with your username and password.

### Bitbucket Server

1. Go to your Bitbucket Server repository settings > Webhooks.

2. Add a new webhook with the following URL:
   ```
   https://your-pr-agent-server.com/webhook
   ```

3. Configure the webhook to trigger on:
   - Pull request created
   - Pull request updated
   - Pull request commented on

4. Add a secret for security.

## Local Development with Tunneling

For local development, PR-Agent provides tunneling support to expose your local server to the internet, allowing you to receive webhook events from Git providers.

### Prerequisites

Install the required dependencies:

```bash
pip install pyngrok localtunnel
```

### Starting a Tunnel

PR-Agent supports two tunneling services:

1. **ngrok** (default): A secure tunneling service that exposes your local server to the internet.
2. **localtunnel**: An alternative tunneling service that can be used if ngrok is not available.

To start a tunnel, use the `--use-tunnel` flag when starting the server:

```bash
python -m pr_agent.servers.github_app --use-tunnel
```

This will automatically create a tunnel and display the public URL, which you can use to configure your webhook.

### Configuration Options

You can configure the tunneling service using environment variables:

- `TUNNEL_SERVICE`: The tunneling service to use (`ngrok` or `localtunnel`). Default: `ngrok`.
- `TUNNEL_AUTH_TOKEN`: Authentication token for ngrok (if required).
- `TUNNEL_REGION`: Region for localtunnel (if required).

Example:

```bash
export TUNNEL_SERVICE=ngrok
export TUNNEL_AUTH_TOKEN=your-ngrok-auth-token
python -m pr_agent.servers.github_app --use-tunnel
```

## Error Handling and Resilience

PR-Agent implements several patterns to ensure webhook reliability:

### Circuit Breaker Pattern

The circuit breaker pattern prevents cascading failures when Git provider APIs are unavailable. It monitors for failures and "trips" after a certain threshold, preventing further calls to the failing service until it recovers.

Configuration options:

- `CIRCUIT_BREAKER_FAILURE_THRESHOLD`: Number of failures before opening the circuit. Default: 5.
- `CIRCUIT_BREAKER_RECOVERY_TIMEOUT`: Seconds to wait before trying to recover. Default: 30.

### Standardized Error Handling

PR-Agent provides standardized error handling for webhook endpoints, ensuring consistent error responses and logging.

### Asynchronous Processing

Webhook events are processed asynchronously using background tasks, preventing webhook timeouts and ensuring that the server can handle multiple concurrent events.

## Troubleshooting

### Webhook Not Receiving Events

1. Check that the webhook URL is correctly configured in your Git provider.
2. Verify that the webhook secret is correct.
3. Check the PR-Agent logs for any errors.
4. Ensure that your server is accessible from the internet (if using a tunnel, check that the tunnel is active).

### Webhook Validation Failures

1. Verify that the webhook secret is correctly configured in both PR-Agent and your Git provider.
2. Check that the webhook payload is not being modified in transit (e.g., by a proxy).

### API Rate Limiting

If you encounter API rate limiting issues, consider:

1. Increasing the circuit breaker recovery timeout.
2. Implementing a queue for webhook events to process them at a controlled rate.
3. Using a personal access token with higher rate limits.

## Advanced Configuration

### Custom Webhook Handlers

You can create custom webhook handlers by extending the base webhook server classes:

```python
from pr_agent.servers.github_app import router as github_router
from fastapi import APIRouter, FastAPI

# Create a custom router
custom_router = APIRouter()

# Add custom endpoints
@custom_router.post("/custom_webhook")
async def handle_custom_webhook(request: Request):
    # Custom webhook handling logic
    pass

# Create a FastAPI app with both routers
app = FastAPI()
app.include_router(github_router)
app.include_router(custom_router)
```

### Webhook Event Filtering

You can configure PR-Agent to filter webhook events based on various criteria:

```python
# In your configuration file
CONFIG:
  IGNORE_PR_AUTHORS:
    - bot-user
    - another-bot
  IGNORE_PR_TITLE:
    - "\\[WIP\\].*"
    - "DO NOT MERGE"
  IGNORE_PR_LABELS:
    - wip
    - do-not-review
  IGNORE_PR_SOURCE_BRANCHES:
    - "dependabot/.*"
  IGNORE_PR_TARGET_BRANCHES:
    - "release/.*"
```

This configuration will ignore PRs from specific authors, with specific titles or labels, or from/to specific branches.

