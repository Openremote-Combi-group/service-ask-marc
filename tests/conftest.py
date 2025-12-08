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

"""Shared pytest fixtures for all tests."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import Response
import json


@pytest.fixture
def mock_openremote_client():
    """Mock OpenRemote client for testing."""
    from openremote_client.schemas import ExternalServiceSchema
    
    client = MagicMock()
    
    # Mock status endpoint
    client.status.get_health_status = AsyncMock(return_value={"status": "healthy"})
    
    # Mock services endpoint - return proper schema object, not dict
    mock_service_schema = ExternalServiceSchema(
        serviceId="test-service",
        instanceId=123,
        label="Test Service",
        homepageUrl="http://test",
        status="AVAILABLE"
    )
    mock_service_response = MagicMock()
    mock_service_response.content = mock_service_schema
    client.services.register_service = AsyncMock(return_value=mock_service_response)
    client.services.heartbeat = AsyncMock(return_value=None)
    client.services.deregister_service = AsyncMock(return_value=None)
    
    # Mock asset endpoints
    client.asset.query_assets = AsyncMock(return_value=[])
    client.asset.get_asset = AsyncMock(return_value={})
    client.asset.create_asset = AsyncMock(return_value={"id": "test-asset-123"})
    client.asset.update_asset = AsyncMock(return_value={})
    client.asset.delete_asset = AsyncMock(return_value=None)
    
    # Mock realm endpoints
    client.realm.get_all_realms = AsyncMock(return_value=[{"name": "master"}])
    client.realm.get_realm = AsyncMock(return_value={"name": "master"})
    
    # Mock asset_model endpoints
    client.asset_model.get_asset_infos = AsyncMock(return_value=[])
    client.asset_model.get_asset_info = AsyncMock(return_value={})
    
    # Mock rule endpoints
    client.rule.get_global_rulesets = AsyncMock(return_value=[])
    client.rule.get_global_ruleset = AsyncMock(return_value={})
    client.rule.create_global_ruleset = AsyncMock(return_value={"id": 1})
    client.rule.update_global_ruleset = AsyncMock(return_value={})
    client.rule.delete_global_ruleset = AsyncMock(return_value=None)
    
    client.rule.get_realm_rulesets = AsyncMock(return_value=[])
    client.rule.get_realm_ruleset = AsyncMock(return_value={})
    client.rule.create_realm_ruleset = AsyncMock(return_value={"id": 1})
    client.rule.update_realm_ruleset = AsyncMock(return_value={})
    client.rule.delete_realm_ruleset = AsyncMock(return_value=None)
    
    client.rule.get_asset_rulesets = AsyncMock(return_value=[])
    client.rule.get_asset_ruleset = AsyncMock(return_value={})
    client.rule.create_asset_ruleset = AsyncMock(return_value={"id": 1})
    client.rule.update_asset_ruleset = AsyncMock(return_value={})
    client.rule.delete_asset_ruleset = AsyncMock(return_value=None)
    
    client.rule.get_global_engine_info = AsyncMock(return_value={})
    client.rule.get_realm_engine_info = AsyncMock(return_value={})
    client.rule.get_asset_engine_info = AsyncMock(return_value={})
    client.rule.get_asset_geofences = AsyncMock(return_value=[])
    
    return client


@pytest.fixture
def mock_mcp_client():
    """Mock MCP client for testing."""
    client = AsyncMock()
    client.get_tools = AsyncMock(return_value=[])
    return client


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset global singletons between tests to avoid state leakage."""
    yield
    # Reset shared module globals
    import shared.openremote_service as or_service
    import shared.mcp_client as mcp_client
    or_service._OpenRemoteService__openremote_service = None
    mcp_client._mcp_client__mcp_service = None


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables for testing."""
    # Clear any existing env vars first
    env_to_clear = [
        "OPENREMOTE_URL",
        "OPENREMOTE_CLIENT_ID", 
        "OPENREMOTE_CLIENT_SECRET",
        "OPENREMOTE_VERIFY_SSL",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "CORS_ALLOWED_DOMAINS",
        "MCP_CONFIG",
        "APP_STATIC_FOLDER",
        "APP_HOMEPAGE_URL",
        "APP_DEBUG",
        "BASE_URL",
    ]
    
    for key in env_to_clear:
        monkeypatch.delenv(key, raising=False)
    
    # Set test environment variables
    env_vars = {
        "OPENREMOTE_URL": "http://localhost:8080",
        "OPENREMOTE_CLIENT_ID": "test-client",
        "OPENREMOTE_CLIENT_SECRET": "test-secret",
        "OPENREMOTE_VERIFY_SSL": "0",
        "OPENAI_API_KEY": "test-openai-key",
        "ANTHROPIC_API_KEY": "test-anthropic-key",
    }
    
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    
    return env_vars


@pytest.fixture
def sample_asset():
    """Sample asset data for testing."""
    return {
        "id": "test-asset-123",
        "name": "Test Asset",
        "type": "ThingAsset",
        "realm": "master",
        "attributes": {
            "temperature": {
                "name": "temperature",
                "type": "number",
                "value": 22.5
            }
        }
    }


@pytest.fixture
def sample_ruleset():
    """Sample ruleset data for testing."""
    return {
        "id": 1,
        "name": "Test Rule",
        "type": "global",
        "rules": "when temperature > 25 then send_notification()"
    }
