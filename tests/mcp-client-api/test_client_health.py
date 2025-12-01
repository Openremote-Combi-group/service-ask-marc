"""Tests for MCP client API health endpoint."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import HTTPStatusError
from starlette.responses import JSONResponse


class TestHealth:
    """Test cases for health endpoint."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_health_endpoint_healthy(self, mock_openremote_client):
        """Test health endpoint returns healthy status."""
        with patch('app.health.get_openremote_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.client = mock_openremote_client
            mock_get_service.return_value = mock_service
            
            from app.health import health
            from app.config import config
            
            response = await health()
            
            assert isinstance(response, JSONResponse)
            assert response.status_code == 200
            
            import json
            body = json.loads(response.body.decode())
            assert body["status"] == "healthy"
            assert body["service"] == config.openremote_service_id

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_health_endpoint_unhealthy(self, mock_openremote_client):
        """Test health endpoint returns unhealthy when OpenRemote is down."""
        mock_response = MagicMock()
        mock_response.status_code = 503
        mock_openremote_client.status.get_health_status = AsyncMock(
            side_effect=HTTPStatusError("Service unavailable", request=MagicMock(), response=mock_response)
        )
        
        with patch('app.health.get_openremote_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.client = mock_openremote_client
            mock_get_service.return_value = mock_service
            
            from app.health import health
            from app.config import config
            
            response = await health()
            
            assert isinstance(response, JSONResponse)
            assert response.status_code == 200
            
            import json
            body = json.loads(response.body.decode())
            assert body["status"] == "unhealthy"
            assert body["service"] == config.openremote_service_id
            assert "error" in body
