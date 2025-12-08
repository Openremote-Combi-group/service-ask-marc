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
        
        with patch('app.services.asset_model.get_openremote_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.client = mock_openremote_client
            mock_get_service.return_value = mock_service
            
            import sys

            
            sys.path.insert(0, 'src/services/mcp-server')

            
            from app.services.asset_model import get_all_asset_types

            
            sys.path.pop(0)
            
            result = await get_all_asset_types.fn()
            
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
        
        with patch('app.services.asset_model.get_openremote_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.client = mock_openremote_client
            mock_get_service.return_value = mock_service
            
            import sys

            
            sys.path.insert(0, 'src/services/mcp-server')

            
            from app.services.asset_model import get_asset_type

            
            sys.path.pop(0)
            
            result = await get_asset_type.fn("ThingAsset")
            
            assert result["assetType"] == "ThingAsset"
            assert "attributeDescriptors" in result
            mock_openremote_client.asset_model.get_asset_info.assert_called_once_with("ThingAsset")
