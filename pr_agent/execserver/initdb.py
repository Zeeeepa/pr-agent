#!/usr/bin/env python3
"""
Database initialization script for PR-Agent ExecServer.

This script creates the necessary SQL functions in Supabase for the ExecServer to work properly.
"""

import argparse
import logging
import sys
import requests
import json
import asyncio
from supabase import create_client, Client

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("initdb")

# SQL functions to create
SQL_FUNCTIONS = [
    """
    CREATE OR REPLACE FUNCTION public.create_table_if_not_exists(
        table_name text,
        columns text
    ) RETURNS void AS $$
    BEGIN
        EXECUTE format('
            CREATE TABLE IF NOT EXISTS %I (
                %s
            );
        ', table_name, columns);
    END;
    $$ LANGUAGE plpgsql SECURITY DEFINER;
    """,
    """
    CREATE OR REPLACE FUNCTION public.exec_sql(
        sql text,
        params jsonb DEFAULT NULL
    ) RETURNS jsonb AS $$
    DECLARE
        result jsonb;
    BEGIN
        IF params IS NULL THEN
            EXECUTE sql INTO result;
        ELSE
            EXECUTE sql USING params INTO result;
        END IF;
        RETURN result;
    EXCEPTION WHEN OTHERS THEN
        RETURN jsonb_build_object('error', SQLERRM);
    END;
    $$ LANGUAGE plpgsql SECURITY DEFINER;
    """,
    """
    CREATE OR REPLACE FUNCTION public.drop_table_if_exists(
        table_name text
    ) RETURNS void AS $$
    BEGIN
        EXECUTE format('DROP TABLE IF EXISTS %I;', table_name);
    END;
    $$ LANGUAGE plpgsql SECURITY DEFINER;
    """
]

async def create_sql_functions(supabase_url: str, supabase_key: str) -> bool:
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
        
        # First create the exec_sql function, then use it for the others
        if not await create_exec_sql_function(supabase_url, supabase_key):
            return False
            
        # Now create the remaining functions
        return await create_remaining_functions(supabase)
    except Exception as e:
        logger.error("Failed to create SQL functions", exc_info=True)
        return False

async def create_exec_sql_function(supabase_url: str, supabase_key: str) -> bool:
    """
    Create the exec_sql function which is needed for other operations
    
    Args:
        supabase_url: Supabase URL
        supabase_key: Supabase anonymous key
        
    Returns:
        True if successful, False otherwise
    """
    # Direct REST API call to create the exec_sql function
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    
    # Extract the REST API URL from the Supabase URL
    rest_url = supabase_url.replace("supabase.co", "supabase.co/rest/v1")
    
    # Get the exec_sql function definition
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
            return True
        elif response.status_code == 404:
            # If exec_sql doesn't exist yet, we need to use a different approach
            logger.info("exec_sql function doesn't exist yet, using direct SQL execution")
            
            # Use the Supabase SQL API to execute the SQL directly
            sql_url = f"{supabase_url.replace('supabase.co', 'supabase.co/rest/v1/sql')}"
            
            response = requests.post(
                sql_url,
                headers=headers,
                json={"query": exec_sql_function}
            )
            
            if response.status_code >= 400:
                logger.error("Failed to create exec_sql function")
                if response.status_code < 500:  # Don't log potentially sensitive SQL for server errors
                    logger.error(f"Status code: {response.status_code}")
                return False
            
            logger.info("Successfully created exec_sql function using direct SQL execution")
            return True
        else:
            logger.error(f"Failed to create exec_sql function: Status code {response.status_code}")
            return False
    except Exception as e:
        logger.error("Error creating exec_sql function", exc_info=True)
        return False

async def create_remaining_functions(supabase: Client) -> bool:
    """
    Create the remaining SQL functions using the exec_sql function
    
    Args:
        supabase: Supabase client
        
    Returns:
        True if successful, False otherwise
    """
    try:
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
                logger.error("Error creating SQL function", exc_info=True)
                return False
        
        logger.info("All SQL functions created successfully")
        return True
    except Exception as e:
        logger.error("Failed to create remaining SQL functions", exc_info=True)
        return False

async def main_async():
    """Async main function"""
    parser = argparse.ArgumentParser(description="Initialize PR-Agent ExecServer database")
    parser.add_argument("--url", required=True, help="Supabase URL")
    parser.add_argument("--key", required=True, help="Supabase anonymous key")
    
    args = parser.parse_args()
    
    try:
        logger.info(f"Connecting to Supabase at {args.url}")
        
        # Create SQL functions
        if await create_sql_functions(args.url, args.key):
            logger.info("Database initialization completed successfully")
            return 0
        else:
            logger.error("Database initialization failed")
            return 1
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        return 1

def main():
    """Main entry point"""
    return asyncio.run(main_async())

if __name__ == "__main__":
    sys.exit(main())
