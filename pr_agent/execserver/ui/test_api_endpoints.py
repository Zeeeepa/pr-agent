import pytest
import httpx

@pytest.mark.asyncio
async def test_api_endpoints():
    """Test that the API endpoints return successful responses."""
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.get("/api/v1/events")
        assert response.status_code == 200

