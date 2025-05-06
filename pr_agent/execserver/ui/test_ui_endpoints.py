import pytest
import httpx

@pytest.mark.asyncio
async def test_ui_endpoints():
    """Test that the UI endpoints return successful responses."""
    async with httpx.AsyncClient(base_url="http://localhost:8080") as client:
        response = await client.get("/")
        assert response.status_code == 200

