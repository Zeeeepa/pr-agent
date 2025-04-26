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
import requests
import json
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

def create_sql_functions(supabase_url: str, supabase_key: str) -> bool:
    """
    Create the necessary SQL functions in Supabase
    
    Args:
        supabase_url: Supabase URL
        supabase_key: Supabase anonymous key
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create Supabase client
        supabase = create_client(supabase_url, supabase_key)
        
        # First, try to use the REST API directly for the first function (exec_sql)
        # since we can't use exec_sql if it doesn't exist yet
        logger.info("Creating exec_sql function...")
        
        # Direct REST API call to create the exec_sql function
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        
        # Extract the REST API URL from the Supabase client
        rest_url = supabase.postgrest_url
        
        # Create the exec_sql function first
        exec_sql_function = SQL_FUNCTIONS[1]
        
        try:
            # Try direct SQL execution via the REST API
            response = requests.post(
                f"{rest_url}/rpc/exec_sql",
                headers=headers,
                json={"sql": exec_sql_function}
            )
            
            if response.status_code == 200:
                logger.info("Successfully created exec_sql function")
            elif response.status_code == 404:
                # If exec_sql doesn't exist yet, we need to use a different approach
                logger.info("exec_sql function doesn't exist yet, using direct SQL execution")
                
                # Use the Supabase SQL API to execute the SQL directly
                # This is a more direct approach that doesn't rely on the exec_sql function
                sql_url = supabase_url.replace("supabase.co", "supabase.co/rest/v1/sql")
                
                response = requests.post(
                    sql_url,
                    headers=headers,
                    json={"query": exec_sql_function}
                )
                
                if response.status_code >= 400:
                    logger.error(f"Failed to create exec_sql function: {response.text}")
                    return False
                
                logger.info("Successfully created exec_sql function using direct SQL execution")
            else:
                logger.error(f"Failed to create exec_sql function: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error creating exec_sql function: {str(e)}")
            return False
        
        # Now that exec_sql exists, use it to create the other functions
        for i, sql in enumerate(SQL_FUNCTIONS):
            # Skip the exec_sql function since we already created it
            if i == 1:
                continue
                
            logger.info(f"Creating SQL function {i+1}/{len(SQL_FUNCTIONS)}...")
            
            try:
                # Use the exec_sql function to create the other functions
                response = supabase.rpc('exec_sql', {'sql': sql}).execute()
                
                if hasattr(response, 'error') and response.error:
                    logger.error(f"Error creating SQL function: {response.error}")
                    return False
            except Exception as e:
                logger.error(f"Error creating SQL function: {str(e)}")
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
        logger.info(f"Connecting to Supabase at {args.url}")
        
        # Create SQL functions
        if create_sql_functions(args.url, args.key):
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
