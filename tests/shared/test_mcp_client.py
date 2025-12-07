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
