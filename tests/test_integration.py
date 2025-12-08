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

"""Integration tests for Ask-Marc services."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient
from fastapi import FastAPI


class TestMCPServerIntegration:
    """Integration tests for MCP Server."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_server_health_endpoint(self, mock_openremote_client):
        """Test MCP server health endpoint integration."""
        with patch('shared.openremote_service.OpenRemoteClient', return_value=mock_openremote_client):
            with patch('shared.openremote_service.get_openremote_service') as mock_get_service:
                mock_service = MagicMock()
                mock_service.client = mock_openremote_client
                mock_get_service.return_value = mock_service
                
                import sys
                sys.path.insert(0, 'src/services/mcp-server')
                from app import app
                sys.path.pop(0)
                
                from httpx import ASGITransport
                async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                    response = await client.get("/api/health")
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert "status" in data


class TestMCPClientAPIIntegration:
    """Integration tests for MCP Client API."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_client_health_endpoint(self, mock_openremote_client):
        """Test MCP client API health endpoint integration."""
        with patch('shared.openremote_service.OpenRemoteClient', return_value=mock_openremote_client):
            with patch('shared.openremote_service.get_openremote_service') as mock_get_service:
                mock_service = MagicMock()
                mock_service.client = mock_openremote_client
                mock_get_service.return_value = mock_service
                
                import sys
                sys.path.insert(0, 'src/services/mcp-client-api')
                from app import app
                sys.path.pop(0)
                
                from httpx import ASGITransport
                async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                    response = await client.get("/api/health")
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert "status" in data


class TestEndToEndFlow:
    """End-to-end integration tests."""

    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_asset_query_flow(self, mock_openremote_client, sample_asset):
        """Test complete flow: query assets through MCP server."""
        mock_openremote_client.asset.query_assets = AsyncMock(return_value=[sample_asset])
        
        with patch('app.services.asset.get_openremote_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.client = mock_openremote_client
            mock_get_service.return_value = mock_service
            
            import sys
            sys.path.insert(0, 'src/services/mcp-server')
            from app.services.asset import asset_query, AssetQuerySchemaDescription
            sys.path.pop(0)
            
            # Execute the query - use .fn for FunctionTool
            query = AssetQuerySchemaDescription(types=["ThingAsset"])
            result = await asset_query.fn(query)
            
            # Verify results
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0]["id"] == sample_asset["id"]
            
            # Verify the mock was called correctly
            mock_openremote_client.asset.query_assets.assert_called_once()
