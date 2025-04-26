"""
Database migration module for ExeServer.

This module provides functionality for managing database schema migrations.
"""

import logging
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from supabase import create_client, Client

from .utils import create_required_sql_functions, create_tables_directly

logger = logging.getLogger(__name__)

# Migration schema version
CURRENT_SCHEMA_VERSION = 1

class Migration:
    """
    Base class for database migrations
    """
    def __init__(self, version: int, description: str):
        self.version = version
        self.description = description
    
    async def up(self, supabase: Client) -> bool:
        """
        Apply the migration
        
        Args:
            supabase: Supabase client
            
        Returns:
            True if successful
        """
        raise NotImplementedError("Subclasses must implement up()")
    
    async def down(self, supabase: Client) -> bool:
        """
        Revert the migration
        
        Args:
            supabase: Supabase client
            
        Returns:
            True if successful
        """
        raise NotImplementedError("Subclasses must implement down()")


class InitialMigration(Migration):
    """
    Initial database migration to create the schema
    """
    def __init__(self):
        super().__init__(1, "Initial schema creation")
    
    async def up(self, supabase: Client) -> bool:
        """
        Create the initial schema
        
        Args:
            supabase: Supabase client
            
        Returns:
            True if successful
        """
        try:
            # First try using the standard approach with SQL functions
            try:
                # Create events table
                supabase.table("events").select("*").limit(1).execute()
                logger.info("Events table already exists")
            except Exception:
                logger.info("Creating events table")
                try:
                    supabase.rpc("create_table_if_not_exists", {
                        "table_name": "events",
                        "columns": """
                            id uuid PRIMARY KEY,
                            event_type text NOT NULL,
                            repository text NOT NULL,
                            payload jsonb NOT NULL,
                            created_at timestamp NOT NULL,
                            processed boolean NOT NULL DEFAULT false,
                            processed_at timestamp
                        """
                    }).execute()
                except Exception as e:
                    logger.warning(f"Failed to create events table using SQL function: {str(e)}")
                    # We'll handle this in the fallback below
            
            try:
                # Create projects table
                supabase.table("projects").select("*").limit(1).execute()
                logger.info("Projects table already exists")
            except Exception:
                logger.info("Creating projects table")
                try:
                    supabase.rpc("create_table_if_not_exists", {
                        "table_name": "projects",
                        "columns": """
                            id uuid PRIMARY KEY,
                            name text NOT NULL,
                            full_name text NOT NULL,
                            description text,
                            created_at timestamp NOT NULL
                        """
                    }).execute()
                except Exception as e:
                    logger.warning(f"Failed to create projects table using SQL function: {str(e)}")
                    # We'll handle this in the fallback below
            
            try:
                # Create triggers table
                supabase.table("triggers").select("*").limit(1).execute()
                logger.info("Triggers table already exists")
            except Exception:
                logger.info("Creating triggers table")
                try:
                    supabase.rpc("create_table_if_not_exists", {
                        "table_name": "triggers",
                        "columns": """
                            id uuid PRIMARY KEY,
                            project_id uuid NOT NULL REFERENCES projects(id),
                            name text NOT NULL,
                            description text,
                            conditions jsonb NOT NULL,
                            actions jsonb NOT NULL,
                            enabled boolean NOT NULL DEFAULT true,
                            created_at timestamp NOT NULL
                        """
                    }).execute()
                except Exception as e:
                    logger.warning(f"Failed to create triggers table using SQL function: {str(e)}")
                    # We'll handle this in the fallback below
            
            try:
                # Create workflows table
                supabase.table("workflows").select("*").limit(1).execute()
                logger.info("Workflows table already exists")
            except Exception:
                logger.info("Creating workflows table")
                try:
                    supabase.rpc("create_table_if_not_exists", {
                        "table_name": "workflows",
                        "columns": """
                            id uuid PRIMARY KEY,
                            repository text NOT NULL,
                            name text NOT NULL,
                            description text,
                            created_at timestamp NOT NULL
                        """
                    }).execute()
                except Exception as e:
                    logger.warning(f"Failed to create workflows table using SQL function: {str(e)}")
                    # We'll handle this in the fallback below
            
            try:
                # Create workflow_runs table
                supabase.table("workflow_runs").select("*").limit(1).execute()
                logger.info("Workflow runs table already exists")
            except Exception:
                logger.info("Creating workflow_runs table")
                try:
                    supabase.rpc("create_table_if_not_exists", {
                        "table_name": "workflow_runs",
                        "columns": """
                            id uuid PRIMARY KEY,
                            workflow_id uuid NOT NULL REFERENCES workflows(id),
                            repository text NOT NULL,
                            status text NOT NULL,
                            created_at timestamp NOT NULL,
                            completed_at timestamp
                        """
                    }).execute()
                except Exception as e:
                    logger.warning(f"Failed to create workflow_runs table using SQL function: {str(e)}")
                    # We'll handle this in the fallback below
            
            try:
                # Create migrations table
                supabase.table("migrations").select("*").limit(1).execute()
                logger.info("Migrations table already exists")
            except Exception:
                logger.info("Creating migrations table")
                try:
                    supabase.rpc("create_table_if_not_exists", {
                        "table_name": "migrations",
                        "columns": """
                            id serial PRIMARY KEY,
                            version integer NOT NULL,
                            description text NOT NULL,
                            applied_at timestamp NOT NULL
                        """
                    }).execute()
                    
                    # Insert this migration
                    supabase.table("migrations").insert({
                        "version": self.version,
                        "description": self.description,
                        "applied_at": datetime.utcnow().isoformat()
                    }).execute()
                except Exception as e:
                    logger.warning(f"Failed to create migrations table using SQL function: {str(e)}")
                    # We'll handle this in the fallback below
            
            # Check if all tables exist
            try:
                # Try to query each table to see if they exist
                tables = ["events", "projects", "triggers", "workflows", "workflow_runs", "migrations"]
                missing_tables = []
                
                for table in tables:
                    try:
                        supabase.table(table).select("*").limit(1).execute()
                    except Exception:
                        missing_tables.append(table)
                
                if missing_tables:
                    logger.warning(f"Some tables are still missing: {', '.join(missing_tables)}")
                    logger.info("Attempting to create tables directly as fallback")
                    
                    # Use the fallback method to create tables directly
                    success, errors = await create_tables_directly(supabase)
                    
                    if not success:
                        logger.error(f"Failed to create tables directly: {errors}")
                        return False
            except Exception as e:
                logger.error(f"Error checking tables: {str(e)}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error in initial migration: {str(e)}")
            return False
    
    async def down(self, supabase: Client) -> bool:
        """
        Revert the initial schema
        
        Args:
            supabase: Supabase client
            
        Returns:
            True if successful
        """
        try:
            # Drop tables in reverse order
            try:
                supabase.rpc("drop_table_if_exists", {"table_name": "workflow_runs"}).execute()
                supabase.rpc("drop_table_if_exists", {"table_name": "workflows"}).execute()
                supabase.rpc("drop_table_if_exists", {"table_name": "triggers"}).execute()
                supabase.rpc("drop_table_if_exists", {"table_name": "projects"}).execute()
                supabase.rpc("drop_table_if_exists", {"table_name": "events"}).execute()
                supabase.rpc("drop_table_if_exists", {"table_name": "migrations"}).execute()
            except Exception as e:
                logger.warning(f"Failed to drop tables using SQL function: {str(e)}")
                
                # Fallback to direct SQL
                try:
                    # Use exec_sql if available
                    drop_tables_sql = """
                    DROP TABLE IF EXISTS workflow_runs CASCADE;
                    DROP TABLE IF EXISTS workflows CASCADE;
                    DROP TABLE IF EXISTS triggers CASCADE;
                    DROP TABLE IF EXISTS projects CASCADE;
                    DROP TABLE IF EXISTS events CASCADE;
                    DROP TABLE IF EXISTS migrations CASCADE;
                    """
                    
                    supabase.rpc("exec_sql", {"sql": drop_tables_sql}).execute()
                except Exception as e2:
                    logger.error(f"Failed to drop tables directly: {str(e2)}")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Error reverting migration: {str(e)}")
            return False


# List of all migrations in order
MIGRATIONS = [
    InitialMigration(),
    # Add new migrations here
]


async def get_current_db_version(supabase: Client) -> int:
    """
    Get the current database schema version
    
    Args:
        supabase: Supabase client
        
    Returns:
        Current schema version
    """
    try:
        result = supabase.table("migrations").select("version").order("version", desc=True).limit(1).execute()
        if result.data:
            return result.data[0]["version"]
        return 0
    except Exception:
        return 0


async def run_migrations(supabase: Client) -> bool:
    """
    Run all pending migrations
    
    Args:
        supabase: Supabase client
        
    Returns:
        True if all migrations were successful
    """
    try:
        # First, ensure required SQL functions exist
        functions_exist = False
        try:
            # Check if we can use the exec_sql function
            supabase.rpc("exec_sql", {"sql": "SELECT 1"}).execute()
            functions_exist = True
        except Exception:
            logger.warning("Required SQL functions don't exist, attempting to create them")
            
            # Try to create the required SQL functions
            success, errors = await create_required_sql_functions(supabase)
            
            if success:
                functions_exist = True
                logger.info("Successfully created required SQL functions")
            else:
                logger.warning(f"Failed to create SQL functions: {errors}")
                logger.warning("Will attempt to proceed with migrations anyway")
        
        # Get current version
        current_version = await get_current_db_version(supabase)
        logger.info(f"Current database schema version: {current_version}")
        
        # Apply pending migrations
        for migration in MIGRATIONS:
            if migration.version > current_version:
                logger.info(f"Applying migration {migration.version}: {migration.description}")
                success = await migration.up(supabase)
                
                if not success:
                    logger.error(f"Migration {migration.version} failed")
                    return False
                
                # Record the migration
                if migration.version > 1:  # Skip for initial migration (it records itself)
                    try:
                        supabase.table("migrations").insert({
                            "version": migration.version,
                            "description": migration.description,
                            "applied_at": datetime.utcnow().isoformat()
                        }).execute()
                    except Exception as e:
                        logger.error(f"Failed to record migration: {str(e)}")
                        # Continue anyway since the migration itself was successful
                
                logger.info(f"Migration {migration.version} applied successfully")
        
        return True
    except Exception as e:
        logger.error(f"Error running migrations: {str(e)}")
        return False


async def initialize_database(supabase_url: str, supabase_anon_key: str) -> bool:
    """
    Initialize the database and run migrations
    
    Args:
        supabase_url: Supabase URL
        supabase_anon_key: Supabase anonymous key
        
    Returns:
        True if initialization was successful
    """
    try:
        # Create Supabase client
        supabase = create_client(supabase_url, supabase_anon_key)
        
        # Run migrations
        success = await run_migrations(supabase)
        
        return success
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        return False
