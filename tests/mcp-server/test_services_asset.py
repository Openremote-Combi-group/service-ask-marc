"""Tests for MCP server asset service."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import HTTPStatusError, Response
from openremote_client.schemas import AssetQuerySchema, AssetObjectSchema


class TestAssetService:
    """Test cases for asset service tools."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_asset_query_success(self, mock_openremote_client, sample_asset):
        """Test asset query returns assets."""
        mock_openremote_client.asset.query_assets = AsyncMock(return_value=[sample_asset])
        
        with patch('src.services.mcp_server.app.services.asset.get_openremote_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.client = mock_openremote_client
            mock_get_service.return_value = mock_service
            
            from src.services.mcp_server.app.services.asset import asset_query, AssetQuerySchemaDescription
            
            query = AssetQuerySchemaDescription(types=["ThingAsset"])
            result = await asset_query(query)
            
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0]["id"] == "test-asset-123"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_asset_query_http_error(self, mock_openremote_client):
        """Test asset query handles HTTP errors."""
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        
        mock_openremote_client.asset.query_assets = AsyncMock(
            side_effect=HTTPStatusError("Forbidden", request=MagicMock(), response=mock_response)
        )
        
        with patch('src.services.mcp_server.app.services.asset.get_openremote_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.client = mock_openremote_client
            mock_get_service.return_value = mock_service
            
            from src.services.mcp_server.app.services.asset import asset_query, AssetQuerySchemaDescription
            
            query = AssetQuerySchemaDescription(types=["ThingAsset"])
            result = await asset_query(query)
            
            assert isinstance(result, dict)
            assert result["status_code"] == 403
            assert "detail" in result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_asset_success(self, mock_openremote_client, sample_asset):
        """Test get single asset by ID."""
        mock_openremote_client.asset.get_asset = AsyncMock(return_value=sample_asset)
        
        with patch('src.services.mcp_server.app.services.asset.get_openremote_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.client = mock_openremote_client
            mock_get_service.return_value = mock_service
            
            from src.services.mcp_server.app.services.asset import get_asset
            
            result = await get_asset("test-asset-123")
            
            assert result["id"] == "test-asset-123"
            assert result["name"] == "Test Asset"
            mock_openremote_client.asset.get_asset.assert_called_once_with("test-asset-123")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_asset_success(self, mock_openremote_client):
        """Test creating a new asset."""
        created_asset = {"id": "new-asset-456", "name": "New Asset"}
        mock_openremote_client.asset.create_asset = AsyncMock(return_value=created_asset)
        
        with patch('src.services.mcp_server.app.services.asset.get_openremote_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.client = mock_openremote_client
            mock_get_service.return_value = mock_service
            
            from src.services.mcp_server.app.services.asset import create_asset, AssetAttributeSchema
            
            attributes = {
                "temperature": AssetAttributeSchema(name="temperature", type="number")
            }
            
            result = await create_asset(
                name="New Asset",
                attributes=attributes,
                type="ThingAsset",
                realm="master"
            )
            
            assert result["id"] == "new-asset-456"
            mock_openremote_client.asset.create_asset.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_asset_error(self, mock_openremote_client):
        """Test create asset handles errors."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        
        mock_openremote_client.asset.create_asset = AsyncMock(
            side_effect=HTTPStatusError("Bad Request", request=MagicMock(), response=mock_response)
        )
        
        with patch('src.services.mcp_server.app.services.asset.get_openremote_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.client = mock_openremote_client
            mock_get_service.return_value = mock_service
            
            from src.services.mcp_server.app.services.asset import create_asset, AssetAttributeSchema
            
            attributes = {
                "temperature": AssetAttributeSchema(name="temperature", type="number")
            }
            
            result = await create_asset(
                name="New Asset",
                attributes=attributes,
                type="InvalidType"
            )
            
            assert isinstance(result, dict)
            assert result["status_code"] == 400
