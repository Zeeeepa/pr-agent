# PR-Agent Extension: GitHub Workflow and Action Integration

## Overview
This project extends the PR-Agent functionality to create a dashboard that allows:
1. Creation of trigger events on selected projects
2. Execution of selected codefiles or GitHub Actions
3. Triggering GitHub Workflows after event triggers
4. Viewing workflows of selected GitHub repositories
5. Adding pre-set comments on PRs

## Existing PR-Agent Components to Leverage

### GitHub Integration
- `pr_agent.servers.github_app`: 
  - `handle_github_webhooks` - Process incoming GitHub webhook events
  - `handle_marketplace_webhooks` - Handle marketplace events
  - `handle_comments_on_pr` - Process comments on PRs
  
- `pr_agent.servers.github_action_runner`:
  - `get_setting_or_env` - Get settings from environment variables
  - `run_action` - Run GitHub actions

- `pr_agent.servers.github_polling`:
  - Notification handling and polling functionality

- `pr_agent.git_providers.github_provider`:
  - `GithubProvider` class - Interface with GitHub API
  
- `pr_agent.git_providers.git_provider`:
  - `GitProvider` class - Base class for Git providers

## New Components to Implement

### ExeServer Directory Structure
```
ExeServer/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── event.py           # Event data models
│   ├── project.py         # Project data models
│   ├── trigger.py         # Trigger data models
│   └── workflow.py        # Workflow data models
├── services/
│   ├── __init__.py
│   ├── db_service.py      # Database interaction service
│   ├── event_service.py   # Event handling service
│   ├── github_service.py  # GitHub API interaction service
│   └── workflow_service.py # Workflow execution service
├── api/
│   ├── __init__.py
│   ├── routes.py          # API routes
│   └── handlers.py        # API request handlers
├── ui/
│   ├── __init__.py
│   ├── components/        # UI components
│   ├── pages/             # UI pages
│   └── assets/            # UI assets
└── config.py              # Configuration settings
```

## Implementation Plan

### 1. Event DB
- Create a database service that logs every GitHub action
- Use environment variables for GitHub token, Supabase URL, and anonymous key
- Implement serverless functionality similar to PR-Agent

### 2. Dashboard Components
- **Event Trigger**: 
  - Select project from user's GitHub repositories
  - Select event type from GitHub events list
  - Configure trigger conditions

- **Codefile Execution**:
  - Select codefile to execute when trigger conditions are met
  - Option to execute GitHub Actions instead of codefiles

- **GitHub Workflow Management**:
  - View active workflows
  - View recent workflow runs
  - Configure workflows
  - View GitHub Actions

### 3. UI Components to Implement
- [ ] Chat Interface with AI Human Agent
  - [ ] Minimize button
  - [ ] Clear conversation option
  - [ ] AI/User message differentiation
  - [ ] Structured information display

- [ ] GitHub Workflow Management
  - [ ] Active Workflows table
  - [ ] Recent Workflow Runs table
  - [ ] Configure Workflows button
  - [ ] View GitHub Actions button
  - [ ] Refresh button
  - [ ] Workflow status indicators

## Integration Points
1. Use `GithubProvider` for GitHub API interactions
2. Extend `handle_github_webhooks` to trigger custom actions
3. Implement custom event handlers based on `github_app.py` patterns
4. Use `get_setting_or_env` for configuration management
5. Implement notification system for Windows pop-ups

## Next Steps
1. Set up the ExeServer directory structure
2. Implement database models and services
3. Create API endpoints for dashboard functionality
4. Develop UI components
5. Integrate with existing PR-Agent functionality
