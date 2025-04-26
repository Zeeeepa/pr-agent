# Database Module

This module provides database functionality for the ExeServer, including:

- Database initialization
- Schema migrations
- SQL function management
- Table creation and management

## Fallback Mechanism

The database initialization process includes a fallback mechanism to handle cases where the required SQL functions don't exist in the database. This is particularly useful for fresh installations or when connecting to a new Supabase instance.

### How it works:

1. First, the system checks if the required SQL functions exist:
   - `exec_sql`: For executing arbitrary SQL
   - `create_table_if_not_exists`: For creating tables if they don't exist
   - `drop_table_if_exists`: For dropping tables if they exist

2. If these functions don't exist, the system attempts to create them directly using raw SQL.

3. Once the functions are created (or if they already exist), the system proceeds with the standard database initialization process.

4. If the standard initialization fails, the system falls back to creating tables directly using raw SQL.

This approach ensures that the application can initialize its database even when connecting to a fresh Supabase instance without the required SQL functions.

## SQL Functions

The required SQL functions are defined in `sql/functions.sql`:

- `exec_sql`: Executes arbitrary SQL statements
- `create_table_if_not_exists`: Creates a table if it doesn't exist
- `drop_table_if_exists`: Drops a table if it exists

## Utility Functions

The `utils.py` file provides utility functions for database operations:

- `create_required_sql_functions`: Creates the required SQL functions
- `create_tables_directly`: Creates tables directly using raw SQL

## Migrations

The `migrations.py` file provides functionality for managing database schema migrations:

- `initialize_database`: Initializes the database and runs migrations
- `run_migrations`: Runs all pending migrations
- `get_current_db_version`: Gets the current database schema version

## Tables

The system creates the following tables:

- `events`: For storing events
- `projects`: For storing projects
- `triggers`: For storing triggers
- `workflows`: For storing workflows
- `workflow_runs`: For storing workflow runs
- `migrations`: For tracking migrations
