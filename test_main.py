from httpx import AsyncClient
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
import httpx
from datetime import datetime
import asyncio

from main import app, fetch_cat_fact

client = TestClient(app)

class TestHealthEndpoint:
    """Test cases for the health check endpoint."""
    
    def test_health_endpoint(self):
        """Test that health endpoint returns correct response."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert data["status"] == "healthy"
        
        # Verify timestamp format
        timestamp = data["timestamp"]
        assert timestamp.endswith("Z")
        # Should be able to parse as ISO format
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))


class TestMeEndpoint:
    """Test cases for the /me endpoint."""
    
    @patch('main.fetch_cat_fact')
    def test_me_endpoint_success(self, mock_fetch_cat_fact):
        """Test successful response from /me endpoint."""
        # Mock the cat fact function
        mock_fetch_cat_fact.return_value = "Cats are amazing creatures!"
        
        response = client.get("/me")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        
        assert "status" in data
        assert "user" in data
        assert "timestamp" in data
        assert "fact" in data
        
        assert data["status"] == "success"
        
        user = data["user"]
        assert "email" in user
        assert "name" in user
        assert "stack" in user
        assert isinstance(user["email"], str)
        assert isinstance(user["name"], str)
        assert isinstance(user["stack"], str)
    
        assert data["fact"] == "Cats are amazing creatures!"
    
    @patch('main.fetch_cat_fact')
    def test_me_endpoint_cat_api_failure(self, mock_fetch_cat_fact):
        """Test /me endpoint when cat API fails."""
        
        from fastapi import HTTPException
        mock_fetch_cat_fact.side_effect = HTTPException(
            status_code=502, detail="Cat Facts API unavailable"
        )
        
        response = client.get("/me")
        assert response.status_code == 502
        
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Cat Facts API unavailable"
    
    @pytest.mark.asyncio
    async def test_rate_limit_resets_after_window():
            for _ in range(5):
                await client.get("/me")
            response = await client.get("/me")
            assert response.status_code == 429

            await asyncio.sleep(61)
            response = await client.get("/me")
            assert response.status_code == 200


class TestFetchCatFact:
    """Test cases for the fetch_cat_fact function."""
    
    @pytest.mark.asyncio
    async def test_fetch_cat_fact_success(self):
        """Test successful cat fact retrieval."""
        mock_response_data = {"fact": "Cats can rotate their ears 180 degrees.", "length": 42}
        
        with patch('httpx.AsyncClient') as mock_client:
            # Setup mock
            mock_context_manager = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_context_manager
            
            mock_response = AsyncMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_context_manager.get.return_value = mock_response
            
            # Test the function
            result = await fetch_cat_fact()
            assert result == "Cats can rotate their ears 180 degrees."
            
            # Verify the call
            mock_context_manager.get.assert_called_once_with("https://catfact.ninja/fact")
    
    @pytest.mark.asyncio
    async def test_fetch_cat_fact_timeout(self):
        """Test timeout handling in fetch_cat_fact."""
        with patch('httpx.AsyncClient') as mock_client:
            # Setup mock to raise timeout
            mock_context_manager = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_context_manager
            mock_context_manager.get.side_effect = httpx.TimeoutException("Request timed out")
            
            from fastapi import HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await fetch_cat_fact()
            
            assert exc_info.value.status_code == 504
            assert "timed out" in exc_info.value.detail.lower()
    
    @pytest.mark.asyncio
    async def test_fetch_cat_fact_http_error(self):
        """Test HTTP error handling in fetch_cat_fact."""
        with patch('httpx.AsyncClient') as mock_client:
            # Setup mock to raise HTTP error
            mock_context_manager = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_context_manager
            
            mock_response = AsyncMock()
            mock_response.status_code = 500
            
            http_error = httpx.HTTPStatusError(
                "Server Error", request=AsyncMock(), response=mock_response
            )
            mock_context_manager.get.side_effect = http_error
            
            from fastapi import HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await fetch_cat_fact()
            
            assert exc_info.value.status_code == 502
            assert "unavailable" in exc_info.value.detail.lower()
    
    @pytest.mark.asyncio
    async def test_fetch_cat_fact_empty_response(self):
        """Test handling of empty fact in response."""
        mock_response_data = {"fact": "", "length": 0}
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_context_manager = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_context_manager
            
            mock_response = AsyncMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_context_manager.get.return_value = mock_response
            
            from fastapi import HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await fetch_cat_fact()
            
            assert exc_info.value.status_code == 502
            assert "empty fact" in exc_info.value.detail.lower()
