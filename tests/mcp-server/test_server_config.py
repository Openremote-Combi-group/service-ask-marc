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

"""Tests for MCP server configuration."""
import pytest
from pydantic import ValidationError


class TestConfig:
    """Test cases for MCP server config."""

    @pytest.mark.unit
    def test_config_loads_from_env(self, mock_env_vars):
        """Test configuration loads from environment variables."""
        # Import after setting env vars
        import sys
        # Clear any cached app modules
        for key in list(sys.modules.keys()):
            if key.startswith('app'):
                del sys.modules[key]
        
        sys.path.insert(0, 'src/services/mcp-server')
        from app.config import Config
        sys.path.pop(0)
        
        config = Config()
        
        # HttpUrl returns Pydantic object, convert to string
        assert str(config.openremote_url) == "http://localhost:8080/"
        assert config.openremote_client_id == "test-client"
        assert config.openremote_client_secret == "test-secret"
        assert config.openremote_verify_ssl is False
        assert config.openremote_service_id == "MCP-Server"
        assert config.openremote_heartbeat_interval == 30

    @pytest.mark.unit
    def test_config_defaults(self, mock_env_vars):
        """Test configuration defaults."""
        import sys
        # Clear any cached app modules
        for key in list(sys.modules.keys()):
            if key.startswith('app'):
                del sys.modules[key]
        
        sys.path.insert(0, 'src/services/mcp-server')
        from app.config import Config
        sys.path.pop(0)
        
        config = Config()
        
        assert config.app_debug is False
        assert config.base_url == "/"
        assert config.cors_allowed_domains == set()
