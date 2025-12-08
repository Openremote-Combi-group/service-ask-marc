# Copyright 2025, OpenRemote Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for MCP server health endpoint."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import HTTPStatusError, Response
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
            
            response = await health(None)
            
            assert isinstance(response, JSONResponse)
            assert response.status_code == 200
            
            # Parse response body
            import json
            body = json.loads(response.body.decode())
            assert body["status"] == "healthy"
            assert body["service"] == config.openremote_service_id

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_health_endpoint_unhealthy(self, mock_openremote_client):
        """Test health endpoint returns unhealthy when OpenRemote is down."""
        # Mock HTTPStatusError
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
            
            response = await health(None)
            
            assert isinstance(response, JSONResponse)
            assert response.status_code == 200
            
            # Parse response body
            import json
            body = json.loads(response.body.decode())
            assert body["status"] == "unhealthy"
            assert body["service"] == config.openremote_service_id
            assert "error" in body
