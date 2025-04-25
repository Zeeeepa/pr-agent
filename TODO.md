# Event Server Executor Extension for PR-Agent

This document outlines the requirements and implementation plan for the Event Server Executor extension for PR-Agent. The extension will leverage existing PR-Agent functionality to capture GitHub events, store them in a database, and execute custom code based on configured triggers.

## Core Components

### 1. Event DB Server
- **Purpose**: Capture and store GitHub events in a database
- **Requirements**:
  - Use environment variables for configuration (GitHub token, Supabase URL, anon key)
  - Store all GitHub webhook events with metadata
  - Support both SQLite (local development) and Supabase (production)
  - Run serverless alongside the existing PR-Agent application
  - Properly use GitHub API for event retrieval and processing

### 2. Event-Triggers Dashboard
- **Purpose**: Web interface for configuring event triggers and viewing stored events
- **Requirements**:
  - Select GitHub projects to monitor
  - Configure triggers based on GitHub event types
  - Link triggers to code execution
  - View event history and execution logs
  - Support hundreds of trigger-action configurations

### 3. Codefile Execution Engine
- **Purpose**: Execute custom code when triggered by GitHub events
- **Requirements**:
  - Support execution of Python code files
  - Pass event data to executed code
  - Secure execution environment
  - Support for GitHub Actions execution
  - Support for PR-Agent actions (comment on PR, etc.)

### 4. Notification System
- **Purpose**: Send notifications when actions are triggered
- **Requirements**:
  - Windows notification pop-ups
  - Configurable notification content
  - Support for success/failure notifications

## Implementation Plan

### Phase 1: Core Infrastructure
1. Create database models for events, triggers, executions, and notifications
2. Implement database connection module with support for SQLite and Supabase
3. Extend webhook handler to store events in the database
4. Set up basic FastAPI endpoints for the dashboard

### Phase 2: Event Storage and Retrieval
1. Implement event categorization by project
2. Create event filtering and search functionality
3. Add event retention policies
4. Implement event replay for testing

### Phase 3: Trigger Configuration
1. Design trigger configuration format
2. Create trigger management API
3. Implement trigger matching logic
4. Add trigger testing capabilities

### Phase 4: Execution Engine
1. Implement secure code execution environment
2. Add support for GitHub Actions execution
3. Create execution logging and monitoring
4. Implement error handling and retry logic

### Phase 5: Dashboard and Notifications
1. Develop web-based dashboard UI
2. Implement Windows notification system
3. Add user authentication and authorization
4. Create comprehensive monitoring and alerting

## Technical Requirements

### API Endpoints
- `POST /api/v1/events`: Webhook endpoint for receiving GitHub events
- `GET /api/v1/events`: List stored events with filtering
- `POST /api/v1/triggers`: Create a new trigger
- `GET /api/v1/triggers`: List configured triggers
- `POST /api/v1/execute`: Manually execute a trigger
- `GET /api/v1/executions`: List execution history

### Database Schema
- **Events**: Store raw event data and metadata
- **Triggers**: Store trigger configurations
- **Executions**: Track execution history and results
- **Notifications**: Store notification configurations and history

### Environment Variables
- `GITHUB_TOKEN`: GitHub API token
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_ANON_KEY`: Supabase anonymous key
- `SQLITE_PATH`: Path to SQLite database file (for local development)
- `EXECUTION_TIMEOUT`: Maximum execution time for triggered code
- `NOTIFICATION_ENABLED`: Enable/disable notifications

## Leveraged PR-Agent Components

The Event Server Executor will leverage the following existing PR-Agent components:

### From `pr_agent.servers.github_app`:
- `handle_github_webhooks`: For receiving and processing GitHub webhook events
- `handle_request`: For processing different types of GitHub events
- Event handling functions for different event types

### From `pr_agent.servers.github_action_runner`:
- `get_setting_or_env`: For retrieving configuration from environment variables
- `run_action`: For executing GitHub Actions

### From `pr_agent.git_providers.github_provider`:
- `GithubProvider`: For interacting with the GitHub API
- Methods for retrieving repository and PR information

### From `pr_agent.git_providers.git_provider`:
- `GitProvider`: Base class for Git provider implementations

## UI Mockups

### Dashboard Main View
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Event Server Executor                                      [Settings] [Logs] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ Projects                    Events                      Triggers            │
│ ┌───────────────────┐      ┌───────────────────┐      ┌───────────────────┐ │
│ │ ● repo1           │      │ PR Created        │      │ + New Trigger     │ │
│ │ ○ repo2           │      │ Issue Comment     │      │                   │ │
│ │ ○ repo3           │      │ Push              │      │ PR Created        │ │
│ │                   │      │ PR Review         │      │ ↳ comment.py      │ │
│ │ [+ Add Project]   │      │                   │      │                   │ │
│ │                   │      │ [View All Events] │      │ Issue Comment     │ │
│ └───────────────────┘      └───────────────────┘      │ ↳ notify.py       │ │
│                                                       │                   │ │
│ Recent Executions                                     │ [View All]        │ │
│ ┌─────────────────────────────────────────────────────┴───────────────────┐ │
│ │ Timestamp    Project    Event          Trigger       Status     Actions  │ │
│ ├─────────────────────────────────────────────────────────────────────────┤ │
│ │ 12:34:56     repo1      PR Created     comment.py    Success    [View]   │ │
│ │ 12:30:45     repo2      Issue Comment  notify.py     Success    [View]   │ │
│ │ 12:15:32     repo1      Push           test.py       Failed     [Retry]  │ │
│ │                                                                         │ │
│ │ [View All Executions]                                                   │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Trigger Configuration
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Configure Trigger                                         [Save] [Cancel]   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ Project:    [repo1 ▼]                                                       │
│                                                                             │
│ Event Type: [Pull Request ▼]                                                │
│                                                                             │
│ Event Action: [Created ▼]                                                   │
│                                                                             │
│ Execution Type:                                                             │
│ ○ Codefile    ● GitHub Action    ○ PR-Agent Command                         │
│                                                                             │
│ GitHub Action: [pr-review ▼]                                                │
│                                                                             │
│ Parameters:                                                                 │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ {                                                                       │ │
│ │   "comment": "Thanks for your PR! I'll review it shortly.",            │ │
│ │   "labels": ["needs-review"]                                           │ │
│ │ }                                                                       │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│ Notifications:                                                              │
│ ☑ Enable Windows notifications                                              │
│ ☐ Send email notifications                                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Event Details View
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Event Details                                           [Back] [Execute]    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ Event ID:      e12345-67890                                                 │
│ Project:       repo1                                                        │
│ Type:          Pull Request                                                 │
│ Action:        Created                                                      │
│ Timestamp:     2023-06-15 12:34:56                                          │
│                                                                             │
│ Event Data:                                                                 │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ {                                                                       │ │
│ │   "action": "opened",                                                   │ │
│ │   "number": 123,                                                        │ │
│ │   "pull_request": {                                                     │ │
│ │     "title": "Add new feature",                                         │ │
│ │     "body": "This PR adds a new feature...",                            │ │
│ │     "user": {                                                           │ │
│ │       "login": "username"                                               │ │
│ │     }                                                                   │ │
│ │   }                                                                     │ │
│ │ }                                                                       │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│ Triggered Executions:                                                       │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ Timestamp    Trigger       Status     Duration    Actions               │ │
│ ├─────────────────────────────────────────────────────────────────────────┤ │
│ │ 12:34:58     comment.py    Success    2.3s        [View Logs]           │ │
│ │ 12:35:01     label.py      Success    1.1s        [View Logs]           │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Security Considerations

1. **Authentication and Authorization**:
   - Secure access to the dashboard and API endpoints
   - Role-based access control for trigger management
   - API key authentication for webhook endpoints

2. **Code Execution Security**:
   - Sandboxed execution environment for custom code
   - Resource limits (CPU, memory, execution time)
   - Input validation and sanitization

3. **Data Security**:
   - Encryption of sensitive data in the database
   - Secure handling of GitHub tokens and credentials
   - Proper error handling to prevent information leakage

## Deployment Options

1. **Standalone Server**:
   - Run as a separate service from PR-Agent
   - Deploy to cloud platforms (AWS, Azure, GCP)
   - Use container orchestration (Kubernetes, Docker Swarm)

2. **Integrated with PR-Agent**:
   - Run as part of the PR-Agent application
   - Share resources and configuration
   - Simplified deployment and management

3. **Serverless Deployment**:
   - Deploy webhook handler as serverless function
   - Use managed database services
   - Scale automatically based on demand
