"""
Database utility functions for ExeServer.

This module provides utility functions for database operations.
"""

import os
import logging
from typing import Tuple, List
from pathlib import Path

from supabase import Client

logger = logging.getLogger(__name__)

async def create_required_sql_functions(supabase: Client) -> Tuple[bool, List[str]]:
    """
    Create the required SQL functions directly using raw SQL

    Args:
        supabase: Supabase client

    Returns:
        Tuple of (success, error_messages)
    """
    try:
        # Get the SQL file path
        sql_file_path = Path(__file__).parent / "sql" / "functions.sql"
        
        if not os.path.exists(sql_file_path):
            logger.error(f"SQL functions file not found: {sql_file_path}")
            return False, [f"SQL functions file not found: {sql_file_path}"]
        
        # Read the SQL file
        with open(sql_file_path, 'r') as f:
            sql = f.read()
        
        # Execute the SQL directly using the REST API
        # This bypasses the need for the functions to already exist
        response = supabase.postgrest.rpc('exec_sql', {'sql': sql}).execute()
        
        if hasattr(response, 'error') and response.error:
            # If exec_sql function doesn't exist, we need to create it first using raw SQL
            # This is a special case since we can't use exec_sql to create itself
            try:
                # Create the exec_sql function first using raw SQL via the REST API
                exec_sql_function = """
                CREATE OR REPLACE FUNCTION public.exec_sql(sql text)
                RETURNS SETOF json AS $$
                BEGIN
                    RETURN QUERY EXECUTE sql;
                EXCEPTION WHEN OTHERS THEN
                    RAISE EXCEPTION '%', SQLERRM;
                END;
                $$ LANGUAGE plpgsql SECURITY DEFINER;
                """
                
                # Use direct SQL execution via the REST API
                # We need to use the SQL API directly to create the function
                import requests
                
                # Get the base URL and auth headers from the Supabase client
                base_url = supabase.base_url
                auth_key = supabase.supabase_key
                
                # Construct the URL for the SQL endpoint
                sql_url = f"{base_url}/rest/v1/sql"
                
                # Set up headers for authentication
                headers = {
                    "apikey": auth_key,
                    "Authorization": f"Bearer {auth_key}",
                    "Content-Type": "application/json"
                }
                
                # Make the request to create the exec_sql function
                response = requests.post(
                    sql_url,
                    headers=headers,
                    json={"query": exec_sql_function}
                )
                
                if response.status_code >= 400:
                    logger.error(f"Failed to create exec_sql function: Status code {response.status_code}")
                    if response.status_code < 500:  # Don't log potentially sensitive response for server errors
                        logger.error(f"Response: {response.text}")
                    return False, [f"Failed to create exec_sql function: Status code {response.status_code}"]
                
                logger.info("exec_sql function created successfully")
                
                # Now that we have exec_sql, we can use it to create the other functions
                response = supabase.postgrest.rpc('exec_sql', {'sql': sql}).execute()
                
                if hasattr(response, 'error') and response.error:
                    logger.error(f"Failed to create SQL functions: {response.error}")
                    return False, [f"Failed to create SQL functions: {response.error}"]
                
                logger.info("SQL functions created successfully")
                return True, []
            except Exception as e:
                logger.error(f"Failed to create exec_sql function: {str(e)}")
                return False, [f"Failed to create exec_sql function: {str(e)}"]
        
        logger.info("SQL functions created successfully")
        return True, []
    except Exception as e:
        logger.error(f"Failed to create SQL functions: {str(e)}")
        return False, [f"Failed to create SQL functions: {str(e)}"]

async def create_tables_directly(supabase: Client) -> Tuple[bool, List[str]]:
    """
    Create the required tables directly using raw SQL
    This is a fallback when the create_table_if_not_exists function doesn't exist

    Args:
        supabase: Supabase client

    Returns:
        Tuple of (success, error_messages)
    """
    try:
        # Create events table
        events_table_sql = """
        CREATE TABLE IF NOT EXISTS events (
            id uuid PRIMARY KEY,
            event_type text NOT NULL,
            repository text NOT NULL,
            payload jsonb NOT NULL,
            created_at timestamp NOT NULL,
            processed boolean NOT NULL DEFAULT false,
            processed_at timestamp
        )
        """
        
        # Create projects table
        projects_table_sql = """
        CREATE TABLE IF NOT EXISTS projects (
            id uuid PRIMARY KEY,
            name text NOT NULL,
            full_name text NOT NULL,
            description text,
            created_at timestamp NOT NULL
        )
        """
        
        # Create triggers table
        triggers_table_sql = """
        CREATE TABLE IF NOT EXISTS triggers (
            id uuid PRIMARY KEY,
            project_id uuid NOT NULL REFERENCES projects(id),
            name text NOT NULL,
            description text,
            conditions jsonb NOT NULL,
            actions jsonb NOT NULL,
            enabled boolean NOT NULL DEFAULT true,
            created_at timestamp NOT NULL
        )
        """
        
        # Create workflows table
        workflows_table_sql = """
        CREATE TABLE IF NOT EXISTS workflows (
            id uuid PRIMARY KEY,
            repository text NOT NULL,
            name text NOT NULL,
            description text,
            created_at timestamp NOT NULL
        )
        """
        
        # Create workflow_runs table
        workflow_runs_table_sql = """
        CREATE TABLE IF NOT EXISTS workflow_runs (
            id uuid PRIMARY KEY,
            workflow_id uuid NOT NULL REFERENCES workflows(id),
            repository text NOT NULL,
            status text NOT NULL,
            created_at timestamp NOT NULL,
            completed_at timestamp
        )
        """
        
        # Create migrations table
        migrations_table_sql = """
        CREATE TABLE IF NOT EXISTS migrations (
            id serial PRIMARY KEY,
            version integer NOT NULL,
            description text NOT NULL,
            applied_at timestamp NOT NULL
        )
        """
        
        # Execute all SQL statements
        tables_sql = [
            events_table_sql,
            projects_table_sql,
            triggers_table_sql,
            workflows_table_sql,
            workflow_runs_table_sql,
            migrations_table_sql
        ]
        
        errors = []
        for sql in tables_sql:
            try:
                # Try to use exec_sql if it exists
                response = supabase.postgrest.rpc('exec_sql', {'sql': sql}).execute()
                
                if hasattr(response, 'error') and response.error:
                    logger.error(f"Failed to create table: {response.error}")
                    errors.append(f"Failed to create table: {response.error}")
            except Exception as e:
                logger.error(f"Failed to create table: {str(e)}")
                errors.append(f"Failed to create table: {str(e)}")
        
        if errors:
            return False, errors
        
        logger.info("Tables created successfully")
        return True, []
    except Exception as e:
        logger.error(f"Failed to create tables: {str(e)}")
        return False, [f"Failed to create tables: {str(e)}"]
