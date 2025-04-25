"""
Main entry point for the Event Server Executor.
"""

import os
import sys
from typing import Optional

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pyngrok import conf, ngrok

from pr_agent.log import get_logger

from .api.events import router as events_router
from .api.executions import router as executions_router
from .api.triggers import router as triggers_router

# Configure logger
logger = get_logger()

# Create FastAPI app
app = FastAPI(title="Event Server Executor", version="0.1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(events_router)
app.include_router(triggers_router)
app.include_router(executions_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"status": "ok", "message": "Event Server Executor is running"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


def start_ngrok(port: int) -> Optional[str]:
    """Start ngrok tunnel to expose the server.
    
    Args:
        port: Port to expose.
        
    Returns:
        Public URL of the ngrok tunnel.
    """
    # Check if ngrok is enabled
    if os.environ.get("NGROK_ENABLED", "false").lower() != "true":
        logger.info("Ngrok is disabled")
        return None
    
    # Get ngrok auth token
    ngrok_auth_token = os.environ.get("NGROK_AUTH_TOKEN")
    if not ngrok_auth_token:
        logger.warning("Ngrok auth token not found, skipping ngrok setup")
        return None
    
    try:
        # Configure ngrok
        conf.get_default().auth_token = ngrok_auth_token
        
        # Start ngrok tunnel
        public_url = ngrok.connect(port)
        logger.info(f"Ngrok tunnel established at {public_url}")
        
        return public_url
    except Exception as e:
        logger.error(f"Error starting ngrok: {e}")
        return None


def main():
    """Main entry point."""
    # Get port from environment
    port = int(os.environ.get("PORT", "3000"))
    host = os.environ.get("HOST", "0.0.0.0")
    
    # Start ngrok if enabled
    public_url = start_ngrok(port)
    if public_url:
        logger.info(f"Server is publicly accessible at {public_url}")
    
    # Start server
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
