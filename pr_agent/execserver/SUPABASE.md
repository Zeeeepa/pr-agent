# Supabase Integration for PR-Agent ExeServer

This document provides detailed information about the Supabase integration in PR-Agent's ExeServer module.

## Overview

PR-Agent ExeServer uses Supabase as its database backend for storing events, projects, triggers, workflows, and settings. The integration includes:

1. **Robust Connection Management**: Handles connection errors gracefully with detailed error messages
2. **Automatic Database Migrations**: Applies database schema migrations automatically
3. **Comprehensive Validation**: Validates Supabase credentials before use
4. **Error Handling**: Provides detailed error messages for common issues

## Setup

### Prerequisites

- A Supabase account
- A Supabase project
- Supabase URL and API key

### Configuration

You can configure Supabase in several ways:

1. **Environment Variables**:
   ```bash
   export SUPABASE_URL=your_supabase_url
   export SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

2. **Configuration File** (`pr_agent.toml`):
   ```toml
   [execserver]
   supabase_url = "your_supabase_url"
   supabase_anon_key = "your_supabase_anon_key"
   ```

3. **Web UI**:
   - Navigate to the Settings page in the ExeServer UI
   - Enter your Supabase URL and API key
   - Click "Save"

## Database Schema

The database schema is managed through migrations. The initial schema creates the following tables:

- `migrations`: Tracks applied database migrations
- `events`: Stores GitHub webhook events
- `projects`: Stores information about GitHub repositories
- `triggers`: Stores event triggers and actions
- `workflows`: Stores GitHub workflow information
- `workflow_runs`: Stores GitHub workflow run information
- `settings`: Stores application settings

## Migration System

The migration system automatically applies database migrations when the application starts or when new Supabase credentials are provided. The system:

1. Checks for a `migrations` table
2. Creates it if it doesn't exist
3. Applies any pending migrations in order
4. Tracks migration status (success/failure)

Migration files are located in the `pr_agent/execserver/migrations` directory and follow a naming convention:

- `001_initial_schema.sql`: Initial database schema
- `002_add_indexes_and_constraints.sql`: Additional indexes and constraints

### Adding a New Migration

To add a new migration:

1. Create a new SQL file in the `migrations` directory with a higher number prefix
2. Add your schema changes to the migration file
3. Restart the application or save new settings to apply the migration

## Validation

The application validates Supabase credentials by:

1. Checking the URL format (must start with http:// or https://)
2. Verifying the API key format (must be at least 10 characters and start with "eyJ")
3. Attempting to connect to the Supabase instance
4. Checking for the existence of required tables

## Error Handling

The Supabase integration includes comprehensive error handling:

- **Connection Errors**: Detailed error messages for connection issues
- **Authentication Errors**: Clear messages for invalid credentials
- **Migration Errors**: Specific error messages for migration failures
- **Query Errors**: Detailed error messages for database operation failures

## Troubleshooting

### Common Issues and Solutions

#### Connection Issues

- **Invalid URL Format**: Ensure your Supabase URL starts with `https://`
- **Invalid API Key**: Verify your Supabase API key is correct
- **Network Issues**: Check your network connection and firewall settings

#### Migration Issues

- **Failed Migrations**: Check the application logs for specific error messages
- **Missing Tables**: The migration system will attempt to create missing tables
- **Permission Issues**: Ensure your Supabase API key has the necessary permissions

#### Performance Issues

- **Slow Queries**: Consider adding indexes for frequently queried fields
- **Rate Limiting**: Check your Supabase plan limits
- **Large Data Sets**: Implement pagination for large data sets

## Security Considerations

- **API Key Security**: The Supabase API key is stored securely and masked in the UI
- **Data Encryption**: Consider encrypting sensitive data before storing it
- **Row-Level Security**: Use Supabase's row-level security for multi-tenant deployments

## Advanced Configuration

### Custom SQL Functions

You can create custom SQL functions in Supabase to optimize complex queries:

1. Go to the SQL Editor in your Supabase dashboard
2. Create a new function:
   ```sql
   CREATE OR REPLACE FUNCTION get_recent_events(repo TEXT, limit_count INT)
   RETURNS SETOF events AS $$
   BEGIN
     RETURN QUERY
     SELECT * FROM events
     WHERE repository = repo
     ORDER BY created_at DESC
     LIMIT limit_count;
   END;
   $$ LANGUAGE plpgsql;
   ```

3. Call the function from your code:
   ```python
   result = supabase.rpc('get_recent_events', {'repo': 'owner/repo', 'limit_count': 10}).execute()
   ```

### Backup and Restore

To backup your Supabase database:

1. Go to the Supabase dashboard
2. Navigate to the SQL Editor
3. Run:
   ```sql
   SELECT * FROM events;
   SELECT * FROM projects;
   SELECT * FROM triggers;
   SELECT * FROM workflows;
   SELECT * FROM workflow_runs;
   SELECT * FROM migrations;
   SELECT * FROM settings;
   ```
4. Export the results as JSON or CSV

## API Reference

### Database Service

The `DatabaseService` class provides methods for interacting with the Supabase database:

- `test_connection()`: Test the connection to Supabase
- `get_events()`: Get events from the database
- `log_event()`: Log a new event
- `get_projects()`: Get all projects
- `create_project()`: Create a new project
- `get_triggers_for_project()`: Get triggers for a project
- `create_trigger()`: Create a new trigger
- `update_trigger()`: Update a trigger

### Migration Service

The `MigrationService` class manages database migrations:

- `apply_migrations()`: Apply pending migrations
- `get_migration_status()`: Get the status of all migrations

### Settings Service

The `SettingsService` class manages application settings:

- `validate_settings()`: Validate settings
- `validate_supabase_credentials()`: Validate Supabase credentials
- `save_settings()`: Save settings
- `get_settings()`: Get all settings
