"""
Migration Service

This module provides a service for managing database migrations
"""

import os
import logging
import glob
from typing import List, Dict, Any, Optional, Tuple
import asyncio
import json

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
        self.migration_lock = asyncio.Lock()
        
    async def _ensure_migrations_table(self) -> Tuple[bool, Optional[str]]:
        """
        Ensure the migrations table exists
        
        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Check if migrations table exists
            self.supabase.table('migrations').select('*').limit(1).execute()
            logger.info("Migrations table exists")
            return True, None
        except Exception as e:
            error_str = str(e).lower()
            # Check if this is a "table doesn't exist" error
            if "not found" in error_str and "relation" in error_str:
                try:
                    # Create migrations table
                    logger.info("Creating migrations table")
                    self.supabase.rpc('exec_sql', {
                        'sql': """
                        CREATE TABLE IF NOT EXISTS migrations (
                            id TEXT PRIMARY KEY,
                            applied_at TIMESTAMP WITH TIME ZONE NOT NULL,
                            description TEXT,
                            status TEXT NOT NULL DEFAULT 'success'
                        );
                        """
                    }).execute()
                    return True, None
                except Exception as create_error:
                    error_message = f"Failed to create migrations table: {str(create_error)}"
                    logger.error(error_message)
                    return False, error_message
            else:
                error_message = f"Failed to check migrations table: {str(e)}"
                logger.error(error_message)
                return False, error_message
    
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
    
    async def _mark_migration_applied(self, migration_id: str, description: str = ""):
        """
        Mark a migration as applied
        
        Args:
            migration_id: ID of the migration
            description: Optional description of the migration
        """
        try:
            self.supabase.table('migrations').insert({
                'id': migration_id,
                'applied_at': 'now()',
                'description': description,
                'status': 'success'
            }).execute()
            logger.info(f"Marked migration {migration_id} as applied")
        except Exception as e:
            logger.error(f"Failed to mark migration {migration_id} as applied: {str(e)}")
            raise
    
    async def _mark_migration_failed(self, migration_id: str, error: str):
        """
        Mark a migration as failed
        
        Args:
            migration_id: ID of the migration
            error: Error message
        """
        try:
            # Check if migration entry exists
            result = self.supabase.table('migrations').select('*').eq('id', migration_id).execute()
            if result.data:
                # Update existing entry
                self.supabase.table('migrations').update({
                    'status': 'failed',
                    'description': f"Error: {error}"
                }).eq('id', migration_id).execute()
            else:
                # Create new entry
                self.supabase.table('migrations').insert({
                    'id': migration_id,
                    'applied_at': 'now()',
                    'description': f"Error: {error}",
                    'status': 'failed'
                }).execute()
            logger.error(f"Marked migration {migration_id} as failed: {error}")
        except Exception as e:
            logger.error(f"Failed to mark migration {migration_id} as failed: {str(e)}")
    
    async def _get_pending_migrations(self) -> List[Dict[str, Any]]:
        """
        Get list of pending migrations
        
        Returns:
            List of pending migration details (id, path, description)
        """
        # Get all migration files
        migration_files = glob.glob(os.path.join(self.migrations_dir, '*.sql'))
        migration_files.sort()
        
        # Get applied migrations
        applied_migrations = await self._get_applied_migrations()
        
        # Filter out applied migrations
        pending_migrations = []
        for migration_file in migration_files:
            filename = os.path.basename(migration_file)
            migration_id = filename.split('_')[0]
            
            # Extract description from filename
            description = ' '.join(filename.split('_')[1:]).replace('.sql', '').replace('_', ' ')
            
            if migration_id not in applied_migrations:
                pending_migrations.append({
                    'id': migration_id,
                    'path': migration_file,
                    'description': description
                })
        
        return pending_migrations
    
    async def _apply_migration(self, migration: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Apply a migration
        
        Args:
            migration: Migration details (id, path, description)
            
        Returns:
            Tuple of (success, error_message)
        """
        migration_id = migration['id']
        migration_file = migration['path']
        description = migration['description']
        
        try:
            # Read migration file
            with open(migration_file, 'r') as f:
                sql = f.read()
            
            # Execute SQL
            logger.info(f"Applying migration {migration_id}: {description}")
            self.supabase.rpc('exec_sql', {'sql': sql}).execute()
            
            # Mark migration as applied
            await self._mark_migration_applied(migration_id, description)
            
            logger.info(f"Migration {migration_id} applied successfully")
            return True, None
        except Exception as e:
            error_message = f"Failed to apply migration {migration_id}: {str(e)}"
            logger.error(error_message)
            await self._mark_migration_failed(migration_id, str(e))
            return False, error_message
    
    async def apply_migrations(self) -> Tuple[bool, Optional[str]]:
        """
        Apply pending migrations
        
        Returns:
            Tuple of (success, error_message)
        """
        # Use a lock to prevent concurrent migrations
        async with self.migration_lock:
            try:
                # Ensure migrations table exists
                table_success, table_error = await self._ensure_migrations_table()
                if not table_success:
                    return False, table_error
                
                # Get pending migrations
                pending_migrations = await self._get_pending_migrations()
                
                if not pending_migrations:
                    logger.info("No pending migrations")
                    return True, None
                
                logger.info(f"Found {len(pending_migrations)} pending migrations")
                
                # Apply migrations
                for migration in pending_migrations:
                    success, error = await self._apply_migration(migration)
                    if not success:
                        return False, error
                
                logger.info("All migrations applied successfully")
                return True, None
            except Exception as e:
                error_message = f"Failed to apply migrations: {str(e)}"
                logger.error(error_message)
                return False, error_message
                
    async def get_migration_status(self) -> Dict[str, Any]:
        """
        Get migration status
        
        Returns:
            Dictionary with migration status information
        """
        try:
            # Ensure migrations table exists
            table_success, _ = await self._ensure_migrations_table()
            if not table_success:
                return {
                    'status': 'error',
                    'message': 'Failed to check migrations table',
                    'applied': [],
                    'pending': []
                }
            
            # Get applied migrations
            result = self.supabase.table('migrations').select('*').order('applied_at').execute()
            applied_migrations = result.data
            
            # Get pending migrations
            pending_migrations = await self._get_pending_migrations()
            
            return {
                'status': 'success',
                'applied': applied_migrations,
                'pending': pending_migrations
            }
        except Exception as e:
            logger.error(f"Failed to get migration status: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'applied': [],
                'pending': []
            }
