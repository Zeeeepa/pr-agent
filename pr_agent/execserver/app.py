"""
Main application entry point for ExeServer.

This module initializes the FastAPI application with proper middleware,
routes, and error handling.
"""

import os
import asyncio
from pathlib import Path
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from pr_agent.execserver.api.routes import router as api_router
from pr_agent.execserver.config import (
    get_cors_origins, get_log_level, get_log_format, 
    set_settings_service, get_supabase_url, get_supabase_anon_key
)
from pr_agent.execserver.services.settings_service import SettingsService
from pr_agent.execserver.db import initialize_database
from pr_agent.log import setup_logger, LoggingFormat
from pr_agent.error_handler import PRAgentError, handle_exceptions
from pr_agent.log.enhanced_logging import RequestContext, structured_log

# Initialize settings service
settings_service = SettingsService()
set_settings_service(settings_service)

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
app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

# Health check endpoint
@app.get("/health")
@handle_exceptions(default_message="Health check failed")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "ok", "version": "0.1.0"}

# Database initialization
@app.on_event("startup")
async def startup_db_client():
    """Initialize database on startup."""
    try:
        # Try to get Supabase credentials from settings service first
        supabase_url = settings_service.get_setting('SUPABASE_URL')
        supabase_anon_key = settings_service.get_setting('SUPABASE_ANON_KEY')
        
        # If not found in settings service, try config
        if not supabase_url or not supabase_anon_key:
            supabase_url = get_supabase_url()
            supabase_anon_key = get_supabase_anon_key()
        
        # Initialize database if credentials are available
        if supabase_url and supabase_anon_key:
            logger.info("Initializing database...")
            
            # Create a temporary database service to check for required SQL functions
            from pr_agent.execserver.services.db_service import DatabaseService
            db_service = DatabaseService()
            
            # Check if required SQL functions exist
            functions_exist, missing_functions = await db_service.check_required_sql_functions()
            
            if not functions_exist:
                # Get the path to the initdb.py script
                initdb_path = await db_service.get_initdb_script_path()
                
                # Log a warning with instructions on how to fix the issue
                logger.warning(f"Required SQL functions are missing: {', '.join(missing_functions)}")
                logger.warning(f"Please run the database initialization script to create these functions:")
                logger.warning(f"cd {os.path.dirname(initdb_path)}")
                logger.warning(f"python initdb.py --url \"{supabase_url}\" --key \"{supabase_anon_key}\"")
                logger.warning("Then restart the application.")
                
                # Continue with initialization, but it will likely fail
                logger.warning("Attempting to initialize database anyway, but it may fail...")
            
            # Try to initialize the database
            success = await initialize_database(supabase_url, supabase_anon_key)
            if success:
                logger.info("Database initialized successfully")
            else:
                logger.warning("Database initialization failed")
        else:
            logger.warning("Supabase credentials not found, skipping database initialization")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")

# Main entry point
if __name__ == "__main__":
    import uvicorn
    from pr_agent.execserver.config import get_ui_port
    
    port = get_ui_port()
    uvicorn.run(app, host="0.0.0.0", port=port)
