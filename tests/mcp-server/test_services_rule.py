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

"""Tests for MCP server rule service."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from openremote_client.schemas import GlobalRulesetSchema, RealmRulesetSchema, AssetRulesetSchema


class TestRuleService:
    """Test cases for rule service tools."""

    # Global Ruleset Tests
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_global_rulesets_success(self, mock_openremote_client, sample_ruleset):
        """Test get all global rulesets."""
        mock_openremote_client.rule.get_global_rulesets = AsyncMock(return_value=[sample_ruleset])
        
        with patch('app.services.rule.get_openremote_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.client = mock_openremote_client
            mock_get_service.return_value = mock_service
            
            import sys

            
            sys.path.insert(0, 'src/services/mcp-server')

            
            from app.services.rule import get_global_rulesets

            
            sys.path.pop(0)
            
            result = await get_global_rulesets.fn()
            
            assert isinstance(result, list)
            assert len(result) == 1
            mock_openremote_client.rule.get_global_rulesets.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_global_ruleset_success(self, mock_openremote_client, sample_ruleset):
        """Test get specific global ruleset by ID."""
        mock_openremote_client.rule.get_global_ruleset = AsyncMock(return_value=sample_ruleset)
        
        with patch('app.services.rule.get_openremote_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.client = mock_openremote_client
            mock_get_service.return_value = mock_service
            
            import sys

            
            sys.path.insert(0, 'src/services/mcp-server')

            
            from app.services.rule import get_global_ruleset

            
            sys.path.pop(0)
            
            result = await get_global_ruleset.fn(1)
            
            assert result["id"] == 1
            mock_openremote_client.rule.get_global_ruleset.assert_called_once_with(1)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_global_ruleset_success(self, mock_openremote_client):
        """Test create global ruleset."""
        created_ruleset = {"id": 2, "name": "New Rule"}
        mock_openremote_client.rule.create_global_ruleset = AsyncMock(return_value=created_ruleset)
        
        with patch('app.services.rule.get_openremote_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.client = mock_openremote_client
            mock_get_service.return_value = mock_service
            
            import sys

            
            sys.path.insert(0, 'src/services/mcp-server')

            
            from app.services.rule import create_global_ruleset

            
            sys.path.pop(0)
            
            ruleset_schema = GlobalRulesetSchema(name="New Rule", rules="test", lang="GROOVY")
            result = await create_global_ruleset.fn(ruleset_schema)
            
            assert result["id"] == 2
            mock_openremote_client.rule.create_global_ruleset.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_global_ruleset_success(self, mock_openremote_client, sample_ruleset):
        """Test update global ruleset."""
        updated_ruleset = {**sample_ruleset, "name": "Updated Rule"}
        mock_openremote_client.rule.update_global_ruleset = AsyncMock(return_value=updated_ruleset)
        
        with patch('app.services.rule.get_openremote_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.client = mock_openremote_client
            mock_get_service.return_value = mock_service
            
            import sys

            
            sys.path.insert(0, 'src/services/mcp-server')

            
            from app.services.rule import update_global_ruleset

            
            sys.path.pop(0)
            
            ruleset_schema = GlobalRulesetSchema(name="Updated Rule", rules="test", lang="GROOVY")
            result = await update_global_ruleset.fn(1, ruleset_schema)
            
            assert result["name"] == "Updated Rule"
            mock_openremote_client.rule.update_global_ruleset.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_global_ruleset_success(self, mock_openremote_client):
        """Test delete global ruleset."""
        mock_openremote_client.rule.delete_global_ruleset = AsyncMock(return_value=None)
        
        with patch('app.services.rule.get_openremote_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.client = mock_openremote_client
            mock_get_service.return_value = mock_service
            
            import sys

            
            sys.path.insert(0, 'src/services/mcp-server')

            
            from app.services.rule import delete_global_ruleset

            
            sys.path.pop(0)
            
            result = await delete_global_ruleset.fn(1)
            
            assert result is None
            mock_openremote_client.rule.delete_global_ruleset.assert_called_once_with(1)

    # Realm Ruleset Tests
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_realm_rulesets_success(self, mock_openremote_client, sample_ruleset):
        """Test get realm rulesets."""
        mock_openremote_client.rule.get_realm_rulesets = AsyncMock(return_value=[sample_ruleset])
        
        with patch('app.services.rule.get_openremote_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.client = mock_openremote_client
            mock_get_service.return_value = mock_service
            
            import sys

            
            sys.path.insert(0, 'src/services/mcp-server')

            
            from app.services.rule import get_realm_rulesets

            
            sys.path.pop(0)
            
            result = await get_realm_rulesets.fn("master")
            
            assert isinstance(result, list)
            mock_openremote_client.rule.get_realm_rulesets.assert_called_once_with("master")

    # Asset Ruleset Tests
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_asset_rulesets_success(self, mock_openremote_client, sample_ruleset):
        """Test get asset rulesets."""
        mock_openremote_client.rule.get_asset_rulesets = AsyncMock(return_value=[sample_ruleset])
        
        with patch('app.services.rule.get_openremote_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.client = mock_openremote_client
            mock_get_service.return_value = mock_service
            
            import sys

            
            sys.path.insert(0, 'src/services/mcp-server')

            
            from app.services.rule import get_asset_rulesets

            
            sys.path.pop(0)
            
            result = await get_asset_rulesets.fn("asset-123")
            
            assert isinstance(result, list)
            mock_openremote_client.rule.get_asset_rulesets.assert_called_once_with("asset-123")

    # Engine Info Tests
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_global_engine_info_success(self, mock_openremote_client):
        """Test get global engine info."""
        engine_info = {"status": "RUNNING", "version": "1.0"}
        mock_openremote_client.rule.get_global_engine_info = AsyncMock(return_value=engine_info)
        
        with patch('app.services.rule.get_openremote_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.client = mock_openremote_client
            mock_get_service.return_value = mock_service
            
            import sys

            
            sys.path.insert(0, 'src/services/mcp-server')

            
            from app.services.rule import get_global_engine_info

            
            sys.path.pop(0)
            
            result = await get_global_engine_info.fn()
            
            assert result["status"] == "RUNNING"
            mock_openremote_client.rule.get_global_engine_info.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_asset_geofences_success(self, mock_openremote_client):
        """Test get asset geofences."""
        geofences = [{"id": "geo-1", "coordinates": []}]
        mock_openremote_client.rule.get_asset_geofences = AsyncMock(return_value=geofences)
        
        with patch('app.services.rule.get_openremote_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.client = mock_openremote_client
            mock_get_service.return_value = mock_service
            
            import sys

            
            sys.path.insert(0, 'src/services/mcp-server')

            
            from app.services.rule import get_asset_geofences

            
            sys.path.pop(0)
            
            result = await get_asset_geofences.fn("asset-123")
            
            assert isinstance(result, list)
            assert len(result) == 1
            mock_openremote_client.rule.get_asset_geofences.assert_called_once_with("asset-123")

    # Additional Realm Ruleset Tests
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_realm_ruleset_success(self, mock_openremote_client, sample_ruleset):
        """Test get specific realm ruleset by ID."""
        mock_openremote_client.rule.get_realm_ruleset = AsyncMock(return_value=sample_ruleset)
        
        with patch('app.services.rule.get_openremote_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.client = mock_openremote_client
            mock_get_service.return_value = mock_service
            
            import sys
            sys.path.insert(0, 'src/services/mcp-server')
            from app.services.rule import get_realm_ruleset
            sys.path.pop(0)
            
            result = await get_realm_ruleset.fn(1)
            
            assert result["id"] == 1
            mock_openremote_client.rule.get_realm_ruleset.assert_called_once_with(1)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_realm_ruleset_success(self, mock_openremote_client):
        """Test create realm ruleset."""
        created_ruleset = {"id": 2, "name": "New Realm Rule"}
        mock_openremote_client.rule.create_realm_ruleset = AsyncMock(return_value=created_ruleset)
        
        with patch('app.services.rule.get_openremote_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.client = mock_openremote_client
            mock_get_service.return_value = mock_service
            
            import sys
            sys.path.insert(0, 'src/services/mcp-server')
            from app.services.rule import create_realm_ruleset
            sys.path.pop(0)
            
            ruleset_schema = RealmRulesetSchema(name="New Realm Rule", rules="test", lang="GROOVY", realm="master")
            result = await create_realm_ruleset.fn(ruleset_schema)
            
            assert result["id"] == 2
            mock_openremote_client.rule.create_realm_ruleset.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_realm_ruleset_success(self, mock_openremote_client, sample_ruleset):
        """Test update realm ruleset."""
        updated_ruleset = {**sample_ruleset, "name": "Updated Realm Rule"}
        mock_openremote_client.rule.update_realm_ruleset = AsyncMock(return_value=updated_ruleset)
        
        with patch('app.services.rule.get_openremote_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.client = mock_openremote_client
            mock_get_service.return_value = mock_service
            
            import sys
            sys.path.insert(0, 'src/services/mcp-server')
            from app.services.rule import update_realm_ruleset
            sys.path.pop(0)
            
            ruleset_schema = RealmRulesetSchema(name="Updated Realm Rule", rules="test", lang="GROOVY", realm="master")
            result = await update_realm_ruleset.fn(1, ruleset_schema)
            
            assert result["name"] == "Updated Realm Rule"
            mock_openremote_client.rule.update_realm_ruleset.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_realm_ruleset_success(self, mock_openremote_client):
        """Test delete realm ruleset."""
        mock_openremote_client.rule.delete_realm_ruleset = AsyncMock(return_value=None)
        
        with patch('app.services.rule.get_openremote_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.client = mock_openremote_client
            mock_get_service.return_value = mock_service
            
            import sys
            sys.path.insert(0, 'src/services/mcp-server')
            from app.services.rule import delete_realm_ruleset
            sys.path.pop(0)
            
            result = await delete_realm_ruleset.fn(1)
            
            assert result is None
            mock_openremote_client.rule.delete_realm_ruleset.assert_called_once_with(1)

    # Additional Asset Ruleset Tests
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_asset_ruleset_success(self, mock_openremote_client, sample_ruleset):
        """Test get specific asset ruleset by ID."""
        mock_openremote_client.rule.get_asset_ruleset = AsyncMock(return_value=sample_ruleset)
        
        with patch('app.services.rule.get_openremote_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.client = mock_openremote_client
            mock_get_service.return_value = mock_service
            
            import sys
            sys.path.insert(0, 'src/services/mcp-server')
            from app.services.rule import get_asset_ruleset
            sys.path.pop(0)
            
            result = await get_asset_ruleset.fn(1)
            
            assert result["id"] == 1
            mock_openremote_client.rule.get_asset_ruleset.assert_called_once_with(1)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_asset_ruleset_success(self, mock_openremote_client):
        """Test create asset ruleset."""
        created_ruleset = {"id": 2, "name": "New Asset Rule"}
        mock_openremote_client.rule.create_asset_ruleset = AsyncMock(return_value=created_ruleset)
        
        with patch('app.services.rule.get_openremote_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.client = mock_openremote_client
            mock_get_service.return_value = mock_service
            
            import sys
            sys.path.insert(0, 'src/services/mcp-server')
            from app.services.rule import create_asset_ruleset
            sys.path.pop(0)
            
            ruleset_schema = AssetRulesetSchema(name="New Asset Rule", rules="test", lang="GROOVY", assetId="asset-123")
            result = await create_asset_ruleset.fn(ruleset_schema)
            
            assert result["id"] == 2
            mock_openremote_client.rule.create_asset_ruleset.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_asset_ruleset_success(self, mock_openremote_client, sample_ruleset):
        """Test update asset ruleset."""
        updated_ruleset = {**sample_ruleset, "name": "Updated Asset Rule"}
        mock_openremote_client.rule.update_asset_ruleset = AsyncMock(return_value=updated_ruleset)
        
        with patch('app.services.rule.get_openremote_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.client = mock_openremote_client
            mock_get_service.return_value = mock_service
            
            import sys
            sys.path.insert(0, 'src/services/mcp-server')
            from app.services.rule import update_asset_ruleset
            sys.path.pop(0)
            
            ruleset_schema = AssetRulesetSchema(name="Updated Asset Rule", rules="test", lang="GROOVY", assetId="asset-123")
            result = await update_asset_ruleset.fn(1, ruleset_schema)
            
            assert result["name"] == "Updated Asset Rule"
            mock_openremote_client.rule.update_asset_ruleset.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_asset_ruleset_success(self, mock_openremote_client):
        """Test delete asset ruleset."""
        mock_openremote_client.rule.delete_asset_ruleset = AsyncMock(return_value=None)
        
        with patch('app.services.rule.get_openremote_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.client = mock_openremote_client
            mock_get_service.return_value = mock_service
            
            import sys
            sys.path.insert(0, 'src/services/mcp-server')
            from app.services.rule import delete_asset_ruleset
            sys.path.pop(0)
            
            result = await delete_asset_ruleset.fn(1)
            
            assert result is None
            mock_openremote_client.rule.delete_asset_ruleset.assert_called_once_with(1)

    # Additional Engine Info Tests
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_realm_engine_info_success(self, mock_openremote_client):
        """Test get realm engine info."""
        engine_info = {"status": "RUNNING", "realm": "master"}
        mock_openremote_client.rule.get_realm_engine_info = AsyncMock(return_value=engine_info)
        
        with patch('app.services.rule.get_openremote_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.client = mock_openremote_client
            mock_get_service.return_value = mock_service
            
            import sys
            sys.path.insert(0, 'src/services/mcp-server')
            from app.services.rule import get_realm_engine_info
            sys.path.pop(0)
            
            result = await get_realm_engine_info.fn("master")
            
            assert result["status"] == "RUNNING"
            mock_openremote_client.rule.get_realm_engine_info.assert_called_once_with("master")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_asset_engine_info_success(self, mock_openremote_client):
        """Test get asset engine info."""
        engine_info = {"status": "RUNNING", "assetId": "asset-123"}
        mock_openremote_client.rule.get_asset_engine_info = AsyncMock(return_value=engine_info)
        
        with patch('app.services.rule.get_openremote_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.client = mock_openremote_client
            mock_get_service.return_value = mock_service
            
            import sys
            sys.path.insert(0, 'src/services/mcp-server')
            from app.services.rule import get_asset_engine_info
            sys.path.pop(0)
            
            result = await get_asset_engine_info.fn("asset-123")
            
            assert result["status"] == "RUNNING"
            mock_openremote_client.rule.get_asset_engine_info.assert_called_once_with("asset-123")
