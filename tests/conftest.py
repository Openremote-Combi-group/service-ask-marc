"""Shared pytest fixtures for all tests."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import Response
import json


@pytest.fixture
def mock_openremote_client():
    """Mock OpenRemote client for testing."""
    client = MagicMock()
    
    # Mock status endpoint
    client.status.get_health_status = AsyncMock(return_value={"status": "healthy"})
    
    # Mock services endpoint
    mock_service_response = MagicMock()
    mock_service_response.content = {
        "serviceId": "test-service",
        "instanceId": 123,
        "label": "Test Service",
        "homepageUrl": "http://test",
        "status": "AVAILABLE"
    }
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


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables."""
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
