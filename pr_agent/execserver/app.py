import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse

from pr_agent.execserver.api.routes import router
from pr_agent.execserver.config import UI_PORT, API_PORT

# Create FastAPI app
app = FastAPI(
    title="PR-Agent ExeServer",
    description="GitHub Workflow and Action Integration for PR-Agent",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

# Serve static files for UI
ui_dir = os.path.join(os.path.dirname(__file__), "ui", "static")
if os.path.exists(ui_dir):
    app.mount("/static", StaticFiles(directory=ui_dir), name="static")

# Serve UI index page
@app.get("/")
async def serve_ui():
    index_path = os.path.join(os.path.dirname(__file__), "ui", "static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "UI not built yet. Please build the UI first."}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

def start_api():
    """Start the API server"""
    uvicorn.run(app, host="0.0.0.0", port=API_PORT)

if __name__ == "__main__":
    start_api()
