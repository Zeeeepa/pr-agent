"""
Migration service for ExeServer.

This module provides a service for managing database migrations.
"""

import os
import re
import logging
from typing import List, Optional
from supabase import Client

logger = logging.getLogger(__name__)

class MigrationService:
    """
    Service for managing database migrations
    """
    def __init__(self, supabase_client: Client):
        """
        Initialize the migration service
        
        Args:
            supabase_client: Initialized Supabase client
        """
        self.supabase = supabase_client
        self.migrations_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'migrations')
        
    async def initialize_migrations_table(self) -> None:
        """
        Initialize the migrations table if it doesn't exist
        """
        try:
            # Create migrations table if it doesn't exist
            query = """
            CREATE TABLE IF NOT EXISTS migrations (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                applied_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            )
            """
            
            # Execute the query using Supabase's raw SQL execution
            self.supabase.table("migrations").select("*").limit(1).execute()
        except Exception:
            # Table doesn't exist, create it
            self.supabase.postgrest.rpc("exec", {"query": query}).execute()
    
    async def get_applied_migrations(self) -> List[str]:
        """
        Get a list of migrations that have already been applied
        
        Returns:
            List of migration names
        """
        try:
            result = self.supabase.table("migrations").select("name").execute()
            return [row["name"] for row in result.data]
        except Exception as e:
            logger.error(f"Error getting applied migrations: {str(e)}")
            return []
    
    async def apply_migrations(self) -> bool:
        """
        Apply all pending migrations
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Initialize migrations table
            await self.initialize_migrations_table()
            
            # Get applied migrations
            applied_migrations = await self.get_applied_migrations()
            
            # Get all migration files
            migration_files = self._get_migration_files()
            
            # Apply pending migrations
            for migration_file in migration_files:
                migration_name = os.path.basename(migration_file)
                
                if migration_name in applied_migrations:
                    logger.info(f"Migration {migration_name} already applied, skipping")
                    continue
                
                logger.info(f"Applying migration: {migration_name}")
                
                # Read migration file
                with open(migration_file, 'r') as f:
                    migration_sql = f.read()
                
                # Execute migration
                self.supabase.postgrest.rpc("exec", {"query": migration_sql}).execute()
                
                # Record migration as applied
                self.supabase.table("migrations").insert({"name": migration_name}).execute()
                
                logger.info(f"Migration {migration_name} applied successfully")
            
            return True
        except Exception as e:
            logger.error(f"Error applying migrations: {str(e)}")
            return False
    
    def _get_migration_files(self) -> List[str]:
        """
        Get a sorted list of migration files
        
        Returns:
            List of migration file paths
        """
        if not os.path.exists(self.migrations_dir):
            return []
        
        # Get all SQL files in the migrations directory
        migration_files = [
            os.path.join(self.migrations_dir, f)
            for f in os.listdir(self.migrations_dir)
            if f.endswith('.sql')
        ]
        
        # Sort by migration number
        migration_files.sort(key=lambda f: int(re.search(r'^(\d+)', os.path.basename(f)).group(1)))
        
        return migration_files
