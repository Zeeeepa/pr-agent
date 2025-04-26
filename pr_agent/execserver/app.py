"""
Main application entry point for ExeServer.

This module initializes the FastAPI application with proper middleware,
routes, and error handling.
"""

import os
from pathlib import Path
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from pr_agent.execserver.api.routes import router as api_router
from pr_agent.execserver.config import get_cors_origins, get_log_level, get_log_format
from pr_agent.log import setup_logger, LoggingFormat
from pr_agent.error_handler import PRAgentError, handle_exceptions
from pr_agent.log.enhanced_logging import RequestContext, structured_log

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
        },
    )

# Include API routes
app.include_router(api_router, prefix="/api")

# Mount static files for UI
static_dir = Path(__file__).parent / "ui" / "static"
app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

# Health check endpoint
@app.get("/health")
@handle_exceptions(default_message="Health check failed")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "ok", "version": "0.1.0"}

# Main entry point
if __name__ == "__main__":
    import uvicorn
    from pr_agent.execserver.config import get_ui_port
    
    port = get_ui_port()
    uvicorn.run(app, host="0.0.0.0", port=port)
