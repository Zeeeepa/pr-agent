import asyncio
from typing import Any, Dict

import httpx
import pytest

# Base URL for the API
BASE_URL = "http://localhost:8000"

@pytest.mark.asyncio
async def test_health_endpoint():
    """Test the health check endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data

@pytest.mark.asyncio
async def test_events_endpoint():
    """Test the events endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/v1/events")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

@pytest.mark.asyncio
async def test_github_webhook_endpoint():
    """Test the GitHub webhook endpoint."""
    # Create a test event payload
    payload = {
        "action": "opened",
        "number": 1,
        "pull_request": {
            "title": "Test PR",
            "body": "This is a test PR",
            "html_url": "https://github.com/test/repo/pull/1"
        },
        "repository": {
            "full_name": "test/repo"
        }
    }

    # Send the event to the webhook endpoint
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/github_webhooks",
            json=payload,
            headers={"X-GitHub-Event": "pull_request"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processing"

@pytest.mark.asyncio
async def test_ui_static_files():
    """Test that the UI static files are being served."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
