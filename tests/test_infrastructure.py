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

"""Quick validation test to ensure test infrastructure works."""
import pytest


class TestInfrastructure:
    """Basic tests to validate test setup."""

    @pytest.mark.unit
    def test_pytest_works(self):
        """Verify pytest is working."""
        assert True

    @pytest.mark.unit
    def test_fixtures_available(self, mock_openremote_client, mock_mcp_client):
        """Verify fixtures are available."""
        assert mock_openremote_client is not None
        assert mock_mcp_client is not None

    @pytest.mark.unit
    def test_sample_data_fixtures(self, sample_asset, sample_ruleset):
        """Verify sample data fixtures work."""
        assert sample_asset["id"] == "test-asset-123"
        assert sample_ruleset["id"] == 1

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_async_works(self):
        """Verify async tests work."""
        async def dummy_async():
            return "success"
        
        result = await dummy_async()
        assert result == "success"
