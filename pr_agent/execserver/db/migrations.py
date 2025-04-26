"""
Database migration module for ExeServer.

This module provides functionality for managing database schema migrations.
"""

import logging
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

from supabase import create_client, Client

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
            # Create events table
            supabase.table("events").select("*").limit(1).execute()
            logger.info("Events table already exists")
        except Exception:
            logger.info("Creating events table")
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
        
        try:
            # Create projects table
            supabase.table("projects").select("*").limit(1).execute()
            logger.info("Projects table already exists")
        except Exception:
            logger.info("Creating projects table")
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
        
        try:
            # Create triggers table
            supabase.table("triggers").select("*").limit(1).execute()
            logger.info("Triggers table already exists")
        except Exception:
            logger.info("Creating triggers table")
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
        
        try:
            # Create workflows table
            supabase.table("workflows").select("*").limit(1).execute()
            logger.info("Workflows table already exists")
        except Exception:
            logger.info("Creating workflows table")
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
        
        try:
            # Create workflow_runs table
            supabase.table("workflow_runs").select("*").limit(1).execute()
            logger.info("Workflow runs table already exists")
        except Exception:
            logger.info("Creating workflow_runs table")
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
        
        try:
            # Create migrations table
            supabase.table("migrations").select("*").limit(1).execute()
            logger.info("Migrations table already exists")
        except Exception:
            logger.info("Creating migrations table")
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
        
        return True
    
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
            supabase.rpc("drop_table_if_exists", {"table_name": "workflow_runs"}).execute()
            supabase.rpc("drop_table_if_exists", {"table_name": "workflows"}).execute()
            supabase.rpc("drop_table_if_exists", {"table_name": "triggers"}).execute()
            supabase.rpc("drop_table_if_exists", {"table_name": "projects"}).execute()
            supabase.rpc("drop_table_if_exists", {"table_name": "events"}).execute()
            supabase.rpc("drop_table_if_exists", {"table_name": "migrations"}).execute()
            
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
                    supabase.table("migrations").insert({
                        "version": migration.version,
                        "description": migration.description,
                        "applied_at": datetime.utcnow().isoformat()
                    }).execute()
                
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
