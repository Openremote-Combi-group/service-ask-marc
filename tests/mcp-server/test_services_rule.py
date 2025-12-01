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
