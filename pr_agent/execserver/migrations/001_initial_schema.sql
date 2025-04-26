-- Initial database schema for PR-Agent ExeServer
-- This migration creates the basic tables needed for the application

-- Migrations table (if not exists)
CREATE TABLE IF NOT EXISTS migrations (
    id TEXT PRIMARY KEY,
    applied_at TIMESTAMP WITH TIME ZONE NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'success'
);

-- Events table
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY,
    event_type TEXT NOT NULL,
    repository TEXT NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    processed BOOLEAN NOT NULL DEFAULT FALSE,
    processed_at TIMESTAMP WITH TIME ZONE
);

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    full_name TEXT NOT NULL UNIQUE,
    description TEXT,
    html_url TEXT NOT NULL,
    api_url TEXT NOT NULL,
    default_branch TEXT NOT NULL
);

-- Triggers table
CREATE TABLE IF NOT EXISTS triggers (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    conditions JSONB NOT NULL,
    actions JSONB NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT TRUE
);

-- Workflows table
CREATE TABLE IF NOT EXISTS workflows (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    repository TEXT NOT NULL,
    path TEXT NOT NULL,
    status TEXT NOT NULL,
    trigger TEXT NOT NULL,
    html_url TEXT NOT NULL,
    api_url TEXT NOT NULL
);

-- Workflow runs table
CREATE TABLE IF NOT EXISTS workflow_runs (
    id TEXT PRIMARY KEY,
    workflow_id TEXT NOT NULL,
    repository TEXT NOT NULL,
    trigger TEXT NOT NULL,
    status TEXT NOT NULL,
    conclusion TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    html_url TEXT NOT NULL,
    api_url TEXT NOT NULL
);

-- Settings table for storing application settings
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_events_repository ON events(repository);
CREATE INDEX IF NOT EXISTS idx_events_event_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_processed ON events(processed);
CREATE INDEX IF NOT EXISTS idx_events_created_at ON events(created_at);

CREATE INDEX IF NOT EXISTS idx_triggers_project_id ON triggers(project_id);
CREATE INDEX IF NOT EXISTS idx_triggers_enabled ON triggers(enabled);

CREATE INDEX IF NOT EXISTS idx_workflow_runs_workflow_id ON workflow_runs(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_runs_repository ON workflow_runs(repository);
CREATE INDEX IF NOT EXISTS idx_workflow_runs_created_at ON workflow_runs(created_at);
