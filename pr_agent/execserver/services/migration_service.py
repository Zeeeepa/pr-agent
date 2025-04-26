"""
Migration Service

This module provides a service for managing database migrations
"""

import os
import logging
import glob
from typing import List, Dict, Any
import asyncio

from supabase import Client

logger = logging.getLogger(__name__)

class MigrationService:
    """
    Service for managing database migrations
    """
    
    def __init__(self, supabase: Client):
        """
        Initialize the migration service
        
        Args:
            supabase: Supabase client
        """
        self.supabase = supabase
        self.migrations_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'migrations')
        
    async def _ensure_migrations_table(self):
        """
        Ensure the migrations table exists
        """
        try:
            # Check if migrations table exists
            self.supabase.table('migrations').select('*').limit(1).execute()
            logger.info("Migrations table exists")
        except Exception:
            # Create migrations table
            logger.info("Creating migrations table")
            self.supabase.table('migrations').create({
                'id': 'text primary key',
                'applied_at': 'timestamp with time zone not null'
            }).execute()
    
    async def _get_applied_migrations(self) -> List[str]:
        """
        Get list of applied migrations
        
        Returns:
            List of applied migration IDs
        """
        try:
            result = self.supabase.table('migrations').select('id').order('id').execute()
            return [migration['id'] for migration in result.data]
        except Exception as e:
            logger.error(f"Failed to get applied migrations: {str(e)}")
            return []
    
    async def _mark_migration_applied(self, migration_id: str):
        """
        Mark a migration as applied
        
        Args:
            migration_id: ID of the migration
        """
        try:
            self.supabase.table('migrations').insert({
                'id': migration_id,
                'applied_at': 'now()'
            }).execute()
            logger.info(f"Marked migration {migration_id} as applied")
        except Exception as e:
            logger.error(f"Failed to mark migration {migration_id} as applied: {str(e)}")
            raise
    
    async def _get_pending_migrations(self) -> List[str]:
        """
        Get list of pending migrations
        
        Returns:
            List of pending migration file paths
        """
        # Get all migration files
        migration_files = glob.glob(os.path.join(self.migrations_dir, '*.sql'))
        migration_files.sort()
        
        # Get applied migrations
        applied_migrations = await self._get_applied_migrations()
        
        # Filter out applied migrations
        pending_migrations = []
        for migration_file in migration_files:
            migration_id = os.path.basename(migration_file).split('_')[0]
            if migration_id not in applied_migrations:
                pending_migrations.append(migration_file)
        
        return pending_migrations
    
    async def _apply_migration(self, migration_file: str):
        """
        Apply a migration
        
        Args:
            migration_file: Path to the migration file
        """
        migration_id = os.path.basename(migration_file).split('_')[0]
        
        try:
            # Read migration file
            with open(migration_file, 'r') as f:
                sql = f.read()
            
            # Execute SQL
            logger.info(f"Applying migration {migration_id}")
            self.supabase.rpc('exec_sql', {'sql': sql}).execute()
            
            # Mark migration as applied
            await self._mark_migration_applied(migration_id)
            
            logger.info(f"Migration {migration_id} applied successfully")
        except Exception as e:
            logger.error(f"Failed to apply migration {migration_id}: {str(e)}")
            raise
    
    async def apply_migrations(self):
        """
        Apply pending migrations
        """
        try:
            # Ensure migrations table exists
            await self._ensure_migrations_table()
            
            # Get pending migrations
            pending_migrations = await self._get_pending_migrations()
            
            if not pending_migrations:
                logger.info("No pending migrations")
                return
            
            logger.info(f"Found {len(pending_migrations)} pending migrations")
            
            # Apply migrations
            for migration_file in pending_migrations:
                await self._apply_migration(migration_file)
            
            logger.info("All migrations applied successfully")
        except Exception as e:
            logger.error(f"Failed to apply migrations: {str(e)}")
            raise
