"""
Main application entry point for ExeServer.

This module initializes the FastAPI application with proper middleware,
routes, and error handling.
"""

import os
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from pr_agent.execserver.api.routes import router as api_router
from pr_agent.execserver.config import (
    get_cors_origins, get_log_level, get_log_format, 
    set_settings_service, get_supabase_url, get_supabase_anon_key
)
from pr_agent.execserver.services.settings_service import SettingsService
from pr_agent.execserver.services.db_service import DatabaseService
from pr_agent.execserver.services.github_service import GitHubService
from pr_agent.execserver.services.workflow_service import WorkflowService
from pr_agent.execserver.services.event_service import EventService
from pr_agent.execserver.db import initialize_database
from pr_agent.execserver.db.utils import create_required_sql_functions, create_tables_directly
from pr_agent.log import setup_logger, LoggingFormat
from pr_agent.error_handler import PRAgentError, handle_exceptions
from pr_agent.log.enhanced_logging import RequestContext, structured_log

# Initialize settings service
settings_service = SettingsService()
set_settings_service(settings_service)

# Initialize service variables at module level
db_service = None
github_service = None
workflow_service = None
event_service = None

# Setup logging
log_level = get_log_level()
log_format = LoggingFormat(get_log_format())
logger = setup_logger(level=log_level, fmt=log_format)

# Create FastAPI app
app = FastAPI(title="ExeServer", description="GitHub Workflow Execution Server")

# Configure CORS
cors_origins = get_cors_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add correlation ID middleware
@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    """Add correlation ID to each request for tracing."""
    # Generate a new correlation ID for this request
    correlation_id = RequestContext.get_correlation_id()
    
    # Log the request
    structured_log(
        f"Request: {request.method} {request.url.path}",
        level="info",
        correlation_id=correlation_id,
        method=request.method,
        path=request.url.path,
        query_params=dict(request.query_params),
        client_host=request.client.host if request.client else None,
    )
    
    # Process the request
    try:
        response = await call_next(request)
        
        # Log the response
        structured_log(
            f"Response: {response.status_code}",
            level="info" if response.status_code < 400 else "error",
            correlation_id=correlation_id,
            status_code=response.status_code,
        )
        
        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id
        return response
    finally:
        # Clear the request context
        RequestContext.clear()

# Add error handling middleware
@app.exception_handler(PRAgentError)
async def pr_agent_error_handler(request: Request, exc: PRAgentError):
    """Handle PR-Agent specific errors."""
    status_code = exc.status_code or 500
    
    structured_log(
        f"Error: {exc.message}",
        level="error",
        error_type=type(exc).__name__,
        status_code=status_code,
        details=exc.details,
    )
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": type(exc).__name__,
            "message": exc.message,
            "details": exc.details,
        },
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions."""
    structured_log(
        f"Unhandled error: {str(exc)}",
        level="error",
        error_type=type(exc).__name__,
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "code": "server_error"
        },
    )

# Include API routes
app.include_router(api_router)

# Mount static files for UI
static_dir = Path(__file__).parent / "ui" / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Add route for serving the React app
@app.get("/{full_path:path}", response_class=HTMLResponse)
async def serve_react_app(request: Request, full_path: str):
    """Serve the React app for any path not matched by other routes."""
    # Only serve the React app if the path doesn't start with /api
    if full_path.startswith("api/"):
        return Response(status_code=404)
    
    # Log the request to serve the React app
    structured_log(
        f"Serving React app for path: {full_path}",
        level="info",
        path=full_path,
        correlation_id=RequestContext.get_correlation_id(),
    )
    
    try:
        # Return the index.html file
        with open(static_dir / "index.html", "r") as f:
            html_content = f.read()
        
        return HTMLResponse(content=html_content)
    except Exception as e:
        # Log the error
        structured_log(
            f"Error serving React app: {str(e)}",
            level="error",
            path=full_path,
            error=str(e),
            correlation_id=RequestContext.get_correlation_id(),
        )
        return HTMLResponse(
            content=f"""
            <html>
                <head>
                    <title>PR-Agent Dashboard - Error</title>
                </head>
                <body>
                    <h1>Error Loading UI</h1>
                    <p>The UI could not be loaded. Please check the server logs for more information.</p>
                    <p>Error: {str(e)}</p>
                    <p>
                        <a href="/health">Check server health</a>
                    </p>
                </body>
            </html>
            """,
            status_code=500
        )

# Health check endpoint
@app.get("/health")
@handle_exceptions(default_message="Health check failed")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "ok", "version": "0.1.0"}

async def check_and_init_database(supabase_url: str, supabase_anon_key: str) -> bool:
    """
    Check for required SQL functions and initialize the database
    
    Args:
        supabase_url: Supabase URL
        supabase_anon_key: Supabase anonymous key
        
    Returns:
        True if database initialization was successful, False otherwise
    """
    from pr_agent.execserver.services.db_service import DatabaseService
    from supabase import create_client
    
    try:
        # Create a direct Supabase client for initialization
        supabase = create_client(supabase_url, supabase_anon_key)
        
        # First, try to create the required SQL functions if they don't exist
        try:
            # Check if we can use the exec_sql function
            supabase.rpc("exec_sql", {"sql": "SELECT 1"}).execute()
            logger.info("Required SQL functions already exist")
        except Exception:
            logger.warning("Required SQL functions don't exist, attempting to create them")
            
            # Try to create the required SQL functions
            success, errors = await create_required_sql_functions(supabase)
            
            if success:
                logger.info("Successfully created required SQL functions")
            else:
                logger.warning(f"Failed to create SQL functions: {errors}")
                logger.warning("Will attempt to proceed with database initialization anyway")
        
        # Now initialize the database using the standard method
        db_service = DatabaseService()
        
        # Check if required SQL functions exist
        functions_exist, missing_functions = await db_service.check_required_sql_functions()
        
        if not functions_exist:
            # Get the path to the initdb.py script
            initdb_path = await db_service.get_initdb_script_path()
            log_missing_functions_warning(missing_functions, initdb_path, supabase_url, supabase_anon_key)
        
        try:
            # Set a timeout for database initialization to prevent hanging
            # Use asyncio.wait_for for compatibility with Python < 3.11
            try:
                success = await asyncio.wait_for(
                    initialize_database(supabase_url, supabase_anon_key),
                    timeout=30  # 30 seconds timeout
                )
                
                if not success:
                    # If standard initialization fails, try direct table creation as a fallback
                    logger.warning("Standard database initialization failed, attempting direct table creation")
                    success, errors = await create_tables_directly(supabase)
                    
                    if success:
                        logger.info("Successfully created tables directly")
                    else:
                        logger.error(f"Failed to create tables directly: {errors}")
                
                return success
            except asyncio.TimeoutError:
                logger.error("Database initialization timed out")
                return False
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            return False
    except Exception as e:
        logger.error(f"Error in check_and_init_database: {str(e)}")
        return False

def log_missing_functions_warning(missing_functions: list, initdb_path: str, supabase_url: str, supabase_anon_key: str):
    """
    Log warnings about missing SQL functions with instructions on how to fix
    
    Args:
        missing_functions: List of missing SQL function names
        initdb_path: Path to the initdb.py script
        supabase_url: Supabase URL
        supabase_anon_key: Supabase anonymous key
    """
    # Mask sensitive credentials for logging
    masked_url = supabase_url
    masked_key = "****" if supabase_anon_key else None
    
    logger.warning(f"Required SQL functions are missing: {', '.join(missing_functions)}")
    logger.warning(f"Please run the database initialization script to create these functions:")
    logger.warning(f"cd {os.path.dirname(initdb_path)}")
    logger.warning(f"python initdb.py --url \"{masked_url}\" --key \"your-supabase-anon-key\"")
    logger.warning("Then restart the application.")
    logger.warning("Attempting to initialize database anyway, but it may fail...")

@app.on_event("startup")
async def startup_db_client():
    """Initialize the database client on startup"""
    global db_service, github_service, workflow_service, event_service
    
    try:
        # Get Supabase credentials from environment variables
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_anon_key = os.environ.get("SUPABASE_ANON_KEY")
        
        # Initialize database if credentials are available
        if supabase_url and supabase_anon_key:
            logger.info("Initializing database...")
            
            # Check for required SQL functions and initialize the database
            success = await check_and_init_database(supabase_url, supabase_anon_key)
            
            if success:
                logger.info("Database initialized successfully")
            else:
                logger.warning("Database initialization failed")
        else:
            logger.warning("Supabase credentials not found in environment variables")
            
        # Initialize services
        db_service = DatabaseService()
        github_service = GitHubService()
        workflow_service = WorkflowService()
        event_service = EventService(db_service, github_service, workflow_service)
        
        logger.info("Services initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing services: {str(e)}")

# Main entry point
if __name__ == "__main__":
    import uvicorn
    from pr_agent.execserver.config import get_ui_port
    
    port = get_ui_port()
    uvicorn.run(app, host="0.0.0.0", port=port)
