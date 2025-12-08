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
        
        with patch('app.services.realm.get_openremote_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.client = mock_openremote_client
            mock_get_service.return_value = mock_service
            
            import sys

            
            sys.path.insert(0, 'src/services/mcp-server')

            
            from app.services.realm import get_all_realms

            
            sys.path.pop(0)
            
            result = await get_all_realms.fn()
            
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
        
        with patch('app.services.realm.get_openremote_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.client = mock_openremote_client
            mock_get_service.return_value = mock_service
            
            import sys

            
            sys.path.insert(0, 'src/services/mcp-server')

            
            from app.services.realm import get_realm

            
            sys.path.pop(0)
            
            result = await get_realm.fn("master")
            
            assert result["name"] == "master"
            assert result["enabled"] is True
            mock_openremote_client.realm.get_realm.assert_called_once_with("master")
