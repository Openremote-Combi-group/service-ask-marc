"""Tests for MCP server realm service."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestRealmService:
    """Test cases for realm service tools."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_all_realms_success(self, mock_openremote_client):
        """Test get all realms returns realm list."""
        realms = [
            {"name": "master", "displayName": "Master"},
            {"name": "test", "displayName": "Test Realm"}
        ]
        mock_openremote_client.realm.get_all_realms = AsyncMock(return_value=realms)
        
        with patch('src.services.mcp_server.app.services.realm.get_openremote_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.client = mock_openremote_client
            mock_get_service.return_value = mock_service
            
            from src.services.mcp_server.app.services.realm import get_all_realms
            
            result = await get_all_realms()
            
            assert isinstance(result, list)
            assert len(result) == 2
            assert result[0]["name"] == "master"
            mock_openremote_client.realm.get_all_realms.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_realm_success(self, mock_openremote_client):
        """Test get specific realm by name."""
        realm_data = {"name": "master", "displayName": "Master", "enabled": True}
        mock_openremote_client.realm.get_realm = AsyncMock(return_value=realm_data)
        
        with patch('src.services.mcp_server.app.services.realm.get_openremote_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.client = mock_openremote_client
            mock_get_service.return_value = mock_service
            
            from src.services.mcp_server.app.services.realm import get_realm
            
            result = await get_realm("master")
            
            assert result["name"] == "master"
            assert result["enabled"] is True
            mock_openremote_client.realm.get_realm.assert_called_once_with("master")
