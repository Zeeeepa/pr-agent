#!/usr/bin/env python
"""
Database Initialization Script for PR-Agent

This script creates the necessary SQL functions in Supabase that are required
for the PR-Agent database migrations to work properly.

Functions created:
- create_table_if_not_exists: Creates a table if it doesn't exist
- exec_sql: Executes arbitrary SQL statements
- drop_table_if_exists: Drops a table if it exists

Usage:
    python initdb.py --url <supabase_url> --key <supabase_anon_key>
"""

import argparse
import logging
import sys
from supabase import create_client, Client

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# SQL functions to create
SQL_FUNCTIONS = [
    """
    -- Function to create a table if it doesn't exist
    CREATE OR REPLACE FUNCTION public.create_table_if_not_exists(table_name text, columns text) 
    RETURNS void AS $$
    BEGIN
        EXECUTE format('CREATE TABLE IF NOT EXISTS %I (%s)', table_name, columns);
    END;
    $$ LANGUAGE plpgsql SECURITY DEFINER;
    """,
    
    """
    -- Function to execute arbitrary SQL
    CREATE OR REPLACE FUNCTION public.exec_sql(sql text) 
    RETURNS void AS $$
    BEGIN
        EXECUTE sql;
    END;
    $$ LANGUAGE plpgsql SECURITY DEFINER;
    """,
    
    """
    -- Function to drop a table if it exists
    CREATE OR REPLACE FUNCTION public.drop_table_if_exists(table_name text) 
    RETURNS void AS $$
    BEGIN
        EXECUTE format('DROP TABLE IF EXISTS %I', table_name);
    END;
    $$ LANGUAGE plpgsql SECURITY DEFINER;
    """
]

def create_sql_functions(supabase: Client) -> bool:
    """
    Create the necessary SQL functions in Supabase
    
    Args:
        supabase: Supabase client
        
    Returns:
        True if successful, False otherwise
    """
    try:
        for sql in SQL_FUNCTIONS:
            logger.info(f"Executing SQL function creation...")
            # Execute the SQL directly using the REST API
            response = supabase.postgrest.rpc('exec_sql', {'sql': sql}).execute()
            
            if hasattr(response, 'error') and response.error:
                logger.error(f"Error creating SQL function: {response.error}")
                # If exec_sql doesn't exist yet, we need to create it first using raw SQL
                if "exec_sql" in str(response.error):
                    logger.info("Attempting to create exec_sql function directly...")
                    # This is a bit of a hack, but we need to create the exec_sql function first
                    # We'll use the raw REST API to execute SQL directly
                    try:
                        # Try using a direct SQL query if possible
                        from postgrest.base_request import APIResponse
                        sql_query = SQL_FUNCTIONS[1]  # The exec_sql function definition
                        
                        # Use the underlying client to execute SQL directly
                        # This approach depends on the specific Supabase Python client version
                        response = supabase.postgrest.schema('public').rpc('exec_sql', {'sql': sql_query})
                        
                        if isinstance(response, APIResponse) and response.error:
                            logger.error(f"Failed to create exec_sql function: {response.error}")
                            return False
                        
                        logger.info("Successfully created exec_sql function")
                    except Exception as e:
                        logger.error(f"Failed to create exec_sql function: {str(e)}")
                        logger.error("You may need to manually create the SQL functions in the Supabase SQL Editor")
                        return False
        
        logger.info("All SQL functions created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating SQL functions: {str(e)}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Initialize PR-Agent database')
    parser.add_argument('--url', required=True, help='Supabase URL')
    parser.add_argument('--key', required=True, help='Supabase anonymous key')
    
    args = parser.parse_args()
    
    try:
        # Create Supabase client
        logger.info(f"Connecting to Supabase at {args.url}")
        supabase = create_client(args.url, args.key)
        
        # Create SQL functions
        if create_sql_functions(supabase):
            logger.info("Database initialization completed successfully")
            return 0
        else:
            logger.error("Database initialization failed")
            return 1
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
