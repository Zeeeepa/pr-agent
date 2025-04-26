"""
Migration Service

This module provides a service for managing database migrations
"""

import os
import logging
import glob
import re
from typing import List, Dict, Any, Optional, Tuple
import asyncio
import json
from datetime import datetime

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
        self.migration_history_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'migration_history.json')
        
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
            try:
                # Use raw SQL for better control over table creation
                self.supabase.rpc('exec_sql', {
                    'sql': """
                    CREATE TABLE IF NOT EXISTS migrations (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        applied_at TIMESTAMP WITH TIME ZONE NOT NULL,
                        success BOOLEAN NOT NULL DEFAULT TRUE,
                        error_message TEXT,
                        duration_ms INTEGER
                    )
                    """
                }).execute()
                logger.info("Migrations table created successfully")
            except Exception as e:
                logger.error(f"Failed to create migrations table: {str(e)}")
                raise
    
    async def _get_applied_migrations(self) -> List[Dict[str, Any]]:
        """
        Get list of applied migrations
        
        Returns:
            List of applied migration records
        """
        try:
            result = self.supabase.table('migrations').select('*').order('id').execute()
            return result.data
        except Exception as e:
            logger.error(f"Failed to get applied migrations: {str(e)}")
            
            # Try to read from local history file as fallback
            try:
                if os.path.exists(self.migration_history_file):
                    with open(self.migration_history_file, 'r') as f:
                        return json.load(f)
            except Exception as file_e:
                logger.error(f"Failed to read migration history file: {str(file_e)}")
            
            return []
    
    async def _mark_migration_applied(self, migration_id: str, migration_name: str, 
                                     success: bool = True, error_message: Optional[str] = None,
                                     duration_ms: Optional[int] = None):
        """
        Mark a migration as applied
        
        Args:
            migration_id: ID of the migration
            migration_name: Name of the migration
            success: Whether the migration was successful
            error_message: Error message if the migration failed
            duration_ms: Duration of the migration in milliseconds
        """
        try:
            # Record in database
            self.supabase.table('migrations').insert({
                'id': migration_id,
                'name': migration_name,
                'applied_at': datetime.utcnow().isoformat(),
                'success': success,
                'error_message': error_message,
                'duration_ms': duration_ms
            }).execute()
            logger.info(f"Marked migration {migration_id} as applied (success: {success})")
            
            # Also record in local history file as backup
            try:
                history = []
                if os.path.exists(self.migration_history_file):
                    with open(self.migration_history_file, 'r') as f:
                        history = json.load(f)
                
                history.append({
                    'id': migration_id,
                    'name': migration_name,
                    'applied_at': datetime.utcnow().isoformat(),
                    'success': success,
                    'error_message': error_message,
                    'duration_ms': duration_ms
                })
                
                with open(self.migration_history_file, 'w') as f:
                    json.dump(history, f, indent=2)
            except Exception as e:
                logger.error(f"Failed to update migration history file: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to mark migration {migration_id} as applied: {str(e)}")
            raise
    
    async def _get_pending_migrations(self) -> List[Tuple[str, str, str]]:
        """
        Get list of pending migrations
        
        Returns:
            List of tuples containing (migration_id, migration_name, migration_file_path)
        """
        # Get all migration files
        migration_files = glob.glob(os.path.join(self.migrations_dir, '*.sql'))
        migration_files.sort()
        
        # Get applied migrations
        applied_migrations = await self._get_applied_migrations()
        applied_ids = [m['id'] for m in applied_migrations]
        
        # Filter out applied migrations
        pending_migrations = []
        for migration_file in migration_files:
            # Extract migration ID and name from filename
            # Expected format: 001_initial_schema.sql, 002_add_users_table.sql, etc.
            filename = os.path.basename(migration_file)
            match = re.match(r'^(\d+)_(.+)\.sql$', filename)
            
            if match:
                migration_id = match.group(1)
                migration_name = match.group(2).replace('_', ' ')
                
                if migration_id not in applied_ids:
                    pending_migrations.append((migration_id, migration_name, migration_file))
            else:
                logger.warning(f"Ignoring migration file with invalid name format: {filename}")
        
        return pending_migrations
    
    async def _apply_migration(self, migration_id: str, migration_name: str, migration_file: str) -> bool:
        """
        Apply a migration
        
        Args:
            migration_id: ID of the migration
            migration_name: Name of the migration
            migration_file: Path to the migration file
            
        Returns:
            True if successful, False otherwise
        """
        start_time = datetime.utcnow()
        
        try:
            # Read migration file
            with open(migration_file, 'r') as f:
                sql = f.read()
            
            # Execute SQL
            logger.info(f"Applying migration {migration_id}: {migration_name}")
            self.supabase.rpc('exec_sql', {'sql': sql}).execute()
            
            # Calculate duration
            end_time = datetime.utcnow()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Mark migration as applied
            await self._mark_migration_applied(migration_id, migration_name, True, None, duration_ms)
            
            logger.info(f"Migration {migration_id} applied successfully in {duration_ms}ms")
            return True
        except Exception as e:
            error_message = str(e)
            logger.error(f"Failed to apply migration {migration_id}: {error_message}")
            
            # Calculate duration
            end_time = datetime.utcnow()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Mark migration as failed
            await self._mark_migration_applied(migration_id, migration_name, False, error_message, duration_ms)
            
            return False
    
    async def apply_migrations(self) -> Tuple[bool, List[str], List[str]]:
        """
        Apply pending migrations
        
        Returns:
            Tuple of (overall_success, applied_migrations, failed_migrations)
        """
        applied = []
        failed = []
        
        try:
            # Ensure migrations table exists
            await self._ensure_migrations_table()
            
            # Get pending migrations
            pending_migrations = await self._get_pending_migrations()
            
            if not pending_migrations:
                logger.info("No pending migrations")
                return True, [], []
            
            logger.info(f"Found {len(pending_migrations)} pending migrations")
            
            # Apply migrations
            for migration_id, migration_name, migration_file in pending_migrations:
                success = await self._apply_migration(migration_id, migration_name, migration_file)
                if success:
                    applied.append(f"{migration_id}: {migration_name}")
                else:
                    failed.append(f"{migration_id}: {migration_name}")
                    # Stop on first failure
                    break
            
            if failed:
                logger.error(f"Migration failed. Applied: {len(applied)}, Failed: {len(failed)}")
                return False, applied, failed
            else:
                logger.info(f"All migrations applied successfully: {len(applied)}")
                return True, applied, []
        except Exception as e:
            logger.error(f"Failed to apply migrations: {str(e)}")
            return False, applied, ["Error: " + str(e)]
    
    async def get_migration_status(self) -> Dict[str, Any]:
        """
        Get migration status
        
        Returns:
            Dictionary with migration status information
        """
        try:
            # Get applied migrations
            applied_migrations = await self._get_applied_migrations()
            
            # Get pending migrations
            pending_migrations = await self._get_pending_migrations()
            
            # Check for failed migrations
            failed_migrations = [m for m in applied_migrations if not m.get('success', True)]
            
            return {
                "applied_count": len(applied_migrations),
                "pending_count": len(pending_migrations),
                "failed_count": len(failed_migrations),
                "applied": applied_migrations,
                "pending": [{"id": m[0], "name": m[1]} for m in pending_migrations],
                "failed": failed_migrations
            }
        except Exception as e:
            logger.error(f"Failed to get migration status: {str(e)}")
            return {
                "error": str(e),
                "applied_count": 0,
                "pending_count": 0,
                "failed_count": 0,
                "applied": [],
                "pending": [],
                "failed": []
            }
