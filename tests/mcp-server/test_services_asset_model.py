"""Tests for MCP server asset model service."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestAssetModelService:
    """Test cases for asset model service tools."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_all_asset_types_success(self, mock_openremote_client):
        """Test get all asset types returns type list."""
        asset_types = [
            {"assetType": "ThingAsset", "descriptorType": "asset"},
            {"assetType": "BuildingAsset", "descriptorType": "asset"}
        ]
        mock_openremote_client.asset_model.get_asset_infos = AsyncMock(return_value=asset_types)
        
        with patch('src.services.mcp_server.app.services.asset_model.get_openremote_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.client = mock_openremote_client
            mock_get_service.return_value = mock_service
            
            from src.services.mcp_server.app.services.asset_model import get_all_asset_types
            
            result = await get_all_asset_types()
            
            assert isinstance(result, list)
            assert len(result) == 2
            assert result[0]["assetType"] == "ThingAsset"
            mock_openremote_client.asset_model.get_asset_infos.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_asset_type_success(self, mock_openremote_client):
        """Test get specific asset type information."""
        asset_type_info = {
            "assetType": "ThingAsset",
            "descriptorType": "asset",
            "attributeDescriptors": []
        }
        mock_openremote_client.asset_model.get_asset_info = AsyncMock(return_value=asset_type_info)
        
        with patch('src.services.mcp_server.app.services.asset_model.get_openremote_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.client = mock_openremote_client
            mock_get_service.return_value = mock_service
            
            from src.services.mcp_server.app.services.asset_model import get_asset_type
            
            result = await get_asset_type("ThingAsset")
            
            assert result["assetType"] == "ThingAsset"
            assert "attributeDescriptors" in result
            mock_openremote_client.asset_model.get_asset_info.assert_called_once_with("ThingAsset")
