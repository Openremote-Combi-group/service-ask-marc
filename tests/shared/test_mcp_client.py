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

"""Tests for shared module - MCP client."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from shared.mcp_client import (
    get_mcp_client_service,
    init_mcp_client_service,
)


class TestMCPClient:
    """Test cases for MCP client functions."""

    @pytest.mark.unit
    def test_get_mcp_client_service_not_initialized(self):
        """Test get_mcp_client_service raises error when not initialized."""
        # The autouse fixture resets this, so it should be None
        with pytest.raises(RuntimeError, match="MCP service not initialized"):
            get_mcp_client_service()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_init_mcp_client_service(self, mock_mcp_client):
        """Test MCP client initialization."""
        mcp_config = {
            "openremote": {
                "transport": "streamable_http",
                "url": "http://localhost:8420/mcp"
            }
        }
        
        with patch('shared.mcp_client.MultiServerMCPClient', return_value=mock_mcp_client):
            await init_mcp_client_service(mcp_config)
            
            service = get_mcp_client_service()
            assert service is not None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_mcp_client_after_init(self, mock_mcp_client):
        """Test getting MCP client after initialization."""
        mcp_config = {
            "openremote": {
                "transport": "streamable_http",
                "url": "http://localhost:8420/mcp"
            }
        }
        
        with patch('shared.mcp_client.MultiServerMCPClient', return_value=mock_mcp_client):
            await init_mcp_client_service(mcp_config)
            
            service1 = get_mcp_client_service()
            service2 = get_mcp_client_service()
            
            assert service1 is service2  # Should return same instance
