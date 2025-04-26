# Supabase Integration for PR-Agent

This document provides information about the Supabase integration in PR-Agent's ExeServer module.

## Overview

PR-Agent uses Supabase as its database backend for storing events, projects, triggers, workflows, and other data. The integration includes:

1. Database connection management
2. Automatic database migrations
3. Validation of Supabase credentials
4. Error handling and logging

## Setup

### Prerequisites

- A Supabase account and project
- Supabase URL and API key

### Configuration

You can configure Supabase in two ways:

1. **Through the UI**: Use the Settings dialog in the PR-Agent dashboard to enter your Supabase URL and API key.
2. **Environment Variables**: Set the following environment variables:
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_ANON_KEY`: Your Supabase anonymous key

## Database Schema

The database schema is managed through migrations. The initial schema creates the following tables:

- `events`: Stores GitHub webhook events
- `projects`: Stores information about GitHub repositories
- `triggers`: Stores event triggers and actions
- `workflows`: Stores GitHub workflow information
- `workflow_runs`: Stores GitHub workflow run information
- `migrations`: Tracks applied database migrations

## Migrations

Migrations are automatically applied when the application starts or when new Supabase credentials are provided. The migration system:

1. Checks for a `migrations` table
2. Creates it if it doesn't exist
3. Applies any pending migrations in order

Migration files are located in the `pr_agent/execserver/migrations` directory and are named with a numeric prefix (e.g., `001_initial_schema.sql`).

## Validation

The application validates Supabase credentials by:

1. Attempting to connect to the Supabase instance
2. Checking for the existence of required tables
3. Providing detailed error messages for common issues

## Error Handling

The Supabase integration includes comprehensive error handling:

- Connection errors are logged and reported to the user
- Database operation errors are caught and logged
- Validation errors provide specific feedback about what went wrong

## Troubleshooting

Common issues and solutions:

### Connection Issues

- Verify that your Supabase URL and API key are correct
- Check that your Supabase project is active
- Ensure your IP address is not blocked by Supabase

### Missing Tables

If you see errors about missing tables, the migrations may not have been applied. You can:

1. Check the application logs for migration errors
2. Manually apply the migrations from the `migrations` directory
3. Reset your Supabase database and let the application apply migrations from scratch

### Performance Issues

If you experience slow performance:

- Check your Supabase plan limits
- Consider adding indexes for frequently queried fields
- Optimize your queries in the `db_service.py` file

## Extending the Schema

To extend the database schema:

1. Create a new migration file in the `migrations` directory with a higher number prefix
2. Add your schema changes to the migration file
3. Restart the application or save new settings to apply the migration

## Security Considerations

- The Supabase anonymous key has limited permissions
- Sensitive data should be encrypted before storage
- Consider using row-level security in Supabase for multi-tenant deployments
