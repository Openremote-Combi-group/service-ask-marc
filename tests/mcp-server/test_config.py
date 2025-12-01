"""Tests for MCP server configuration."""
import pytest
from pydantic import ValidationError


class TestConfig:
    """Test cases for MCP server config."""

    @pytest.mark.unit
    def test_config_loads_from_env(self, mock_env_vars):
        """Test configuration loads from environment variables."""
        # Import after setting env vars
        from src.services.mcp_server.app.config import Config
        
        config = Config()
        
        assert config.openremote_url == "http://localhost:8080"
        assert config.openremote_client_id == "test-client"
        assert config.openremote_client_secret == "test-secret"
        assert config.openremote_verify_ssl is False
        assert config.openremote_service_id == "MCP-Server"
        assert config.openremote_heartbeat_interval == 30

    @pytest.mark.unit
    def test_config_defaults(self, mock_env_vars):
        """Test configuration defaults."""
        from src.services.mcp_server.app.config import Config
        
        config = Config()
        
        assert config.app_debug is False
        assert config.base_url == "/"
        assert config.cors_allowed_domains == set()

    @pytest.mark.unit
    def test_config_missing_required_fields(self, monkeypatch):
        """Test configuration validation with missing required fields."""
        # Clear all environment variables
        monkeypatch.delenv("OPENREMOTE_URL", raising=False)
        monkeypatch.delenv("OPENREMOTE_CLIENT_ID", raising=False)
        monkeypatch.delenv("OPENREMOTE_CLIENT_SECRET", raising=False)
        
        from src.services.mcp_server.app.config import Config
        
        with pytest.raises(ValidationError):
            Config()
