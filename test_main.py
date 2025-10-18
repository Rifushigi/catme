import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from main import app, fetch_cat_fact

client = TestClient(app)


class TestHealthEndpoint:
    def test_health_endpoint(self):
        """Checks that /health returns a healthy status and timestamp."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        assert "timestamp" in data
        assert data["timestamp"].endswith("+00:00")



class TestMeEndpoint:
    @pytest.mark.asyncio
    @patch("main.fetch_cat_fact", new_callable=AsyncMock)
    async def test_me_endpoint(self, mock_fetch_cat_fact):
        """Checks that /me returns expected keys and successful response."""
        mock_fetch_cat_fact.return_value = "Cats are wonderful!"
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/me")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "fact" in data
        assert "user" in data


class TestFetchCatFact:
    @pytest.mark.asyncio
    async def test_fetch_cat_fact_success(self):
        """Checks that fetch_cat_fact returns a valid fact string."""
        mock_response_data = {"fact": "Cats sleep 70% of their lives.", "length": 30}

        with patch("httpx.AsyncClient") as mock_client:
            mock_context = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_context

            mock_response = AsyncMock()
            mock_response.json = lambda: mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_context.get.return_value = mock_response

            result = await fetch_cat_fact()
            assert isinstance(result, str)
            assert "Cats sleep" in result
