# Asynchronous Webhook Processing

This document describes the asynchronous webhook processing system implemented in PR-Agent.

## Overview

The asynchronous webhook processing system is designed to handle webhook events from various sources (GitHub, GitLab, etc.) in a reliable and efficient manner. It provides the following features:

- **Quick Response**: Responds quickly to webhook sources to prevent timeouts
- **Background Processing**: Processes webhook events asynchronously in the background
- **Status Tracking**: Tracks the status of webhook processing tasks
- **Error Handling**: Provides robust error handling and retry mechanisms
- **Concurrency**: Handles multiple concurrent webhook events efficiently
- **Isolation**: Ensures isolation between different webhook processing tasks
- **Persistence**: Optionally persists webhook tasks across application restarts

## Architecture

The system consists of the following components:

### WebhookTask

Represents a webhook processing task with the following properties:

- `webhook_id`: Unique identifier for the webhook
- `source`: Source of the webhook (github, gitlab, etc.)
- `event_type`: Type of the webhook event
- `payload`: Webhook payload data
- `status`: Current status of the task (queued, processing, completed, failed, retrying)
- `created_at`: Timestamp when the task was created
- `updated_at`: Timestamp when the task was last updated
- `attempts`: Number of processing attempts
- `max_attempts`: Maximum number of retry attempts
- `error`: Error information if the task failed
- `result`: Result of the task processing

### WebhookQueue

Manages the queue of webhook tasks with the following functionality:

- `enqueue`: Add a webhook task to the queue
- `dequeue`: Get the next webhook task from the queue
- `get_task`: Get a webhook task by ID
- `update_task`: Update a webhook task in the queue
- `requeue`: Requeue a failed webhook task for retry
- `get_all_tasks`: Get all webhook tasks
- `cleanup_old_tasks`: Remove old completed or failed tasks

### WebhookProcessor

Processes webhook tasks with the following functionality:

- `register_handler`: Register a handler function for a specific webhook source and event type
- `process_webhook`: Process a webhook task
- `worker`: Worker task that processes webhooks from the queue
- `start`: Start the webhook processor
- `stop`: Stop the webhook processor
- `enqueue_webhook`: Enqueue a webhook for processing
- `get_webhook_status`: Get the status of a webhook task
- `get_all_webhook_statuses`: Get the status of all webhook tasks
- `cleanup`: Clean up old webhook tasks

## Configuration

The webhook processor can be configured using the following settings in `pr_agent/config/webhook_processor.yaml`:

```yaml
# Number of worker tasks to run concurrently
NUM_WORKERS: 5

# Maximum number of retry attempts for failed webhook processing
MAX_RETRY_ATTEMPTS: 3

# Maximum age (in seconds) of completed/failed webhook tasks to keep before cleanup (default: 24 hours)
CLEANUP_AGE: 86400

# Enable persistence of webhook tasks across application restarts
ENABLE_PERSISTENCE: true

# File path for persisting webhook tasks (relative to application root)
PERSISTENCE_FILE: "data/webhook_tasks.json"

# Interval (in seconds) for persisting webhook tasks to disk
PERSISTENCE_INTERVAL: 300

# Maximum number of webhook tasks to keep in memory
MAX_TASKS: 1000

# Enable detailed logging of webhook processing
DETAILED_LOGGING: true
```

## Usage

### Server Integration

The webhook processor is integrated with the following servers:

- GitHub App (`pr_agent/servers/github_app.py`)
- GitLab Webhook (`pr_agent/servers/gitlab_webhook.py`)
- Azure DevOps Server Webhook (`pr_agent/servers/azuredevops_server_webhook.py`)
- Bitbucket Server Webhook (`pr_agent/servers/bitbucket_server_webhook.py`)

Each server initializes the webhook processor on startup and registers handlers for different webhook event types.

### API Endpoints

The following API endpoints are available for monitoring webhook processing:

- `GET /api/v1/webhook_status/{webhook_id}`: Get the status of a webhook processing task
- `GET /api/v1/webhook_statuses`: List all webhook processing tasks

### Example Flow

1. A webhook is received by one of the server endpoints
2. The server validates the webhook and enqueues it for asynchronous processing
3. The server responds immediately to the webhook source to prevent timeouts
4. The webhook processor picks up the webhook from the queue and processes it
5. The webhook processor updates the status of the webhook task
6. If processing fails, the webhook processor retries the task up to the configured maximum number of attempts
7. The webhook processor cleans up old completed or failed tasks periodically

## Error Handling

The webhook processor provides robust error handling with the following features:

- **Retry Mechanism**: Failed webhook tasks are automatically retried up to the configured maximum number of attempts
- **Error Logging**: Errors during webhook processing are logged with detailed information
- **Status Tracking**: The status of webhook tasks is tracked and can be monitored through the API endpoints
- **Isolation**: Errors in one webhook task do not affect other tasks

## Concurrency and Resource Management

The webhook processor handles concurrency and resource management with the following features:

- **Worker Pool**: A configurable number of worker tasks process webhooks concurrently
- **Queue**: Webhooks are queued and processed in order
- **Isolation**: Each webhook task is processed independently
- **Resource Limits**: The number of webhook tasks kept in memory is limited

## Persistence

The webhook processor optionally persists webhook tasks across application restarts with the following features:

- **Task Serialization**: Webhook tasks are serialized to JSON format
- **Periodic Persistence**: Tasks are persisted to disk periodically
- **Atomic Updates**: Tasks are written to a temporary file first to avoid corruption
- **Recovery**: Tasks are recovered from disk on startup

## Monitoring and Debugging

The webhook processor provides the following features for monitoring and debugging:

- **Status API**: API endpoints for monitoring webhook processing status
- **Logging**: Detailed logging of webhook processing events
- **Metrics**: Metrics for queue size, processing time, etc.

## Testing

The webhook processor is tested with the following test cases:

- **Unit Tests**: Tests for individual components (WebhookTask, WebhookQueue, WebhookProcessor)
- **Integration Tests**: Tests for the integration between components
- **Concurrency Tests**: Tests for handling multiple concurrent webhook events
- **Error Handling Tests**: Tests for error handling and recovery mechanisms
- **Persistence Tests**: Tests for persistence across application restarts

