"""Tests for MCP client API configuration."""
import pytest
from pydantic import ValidationError


class TestConfig:
    """Test cases for MCP client API config."""

    @pytest.mark.unit
    def test_config_loads_from_env(self, mock_env_vars):
        """Test configuration loads from environment variables."""
        from src.services.mcp_client_api.app.config import Config
        
        config = Config()
        
        assert config.openremote_url == "http://localhost:8080"
        assert config.openremote_client_id == "test-client"
        assert config.openremote_client_secret == "test-secret"
        assert config.openremote_verify_ssl is False
        assert config.openai_api_key == "test-openai-key"
        assert config.anthropic_api_key == "test-anthropic-key"
        assert config.openremote_service_id == "MCP-Client-API"
        assert config.openremote_heartbeat_interval == 30

    @pytest.mark.unit
    def test_config_defaults(self, mock_env_vars):
        """Test configuration defaults."""
        from src.services.mcp_client_api.app.config import Config
        
        config = Config()
        
        assert config.app_debug is False
        assert config.app_static_folder == "static"
        assert config.app_homepage_url == "/"
        assert config.base_url == "/"
        assert config.cors_allowed_domains == set()
        assert config.mcp_config is None
        assert config.mcp_config_file == "mcp_config.json"

    @pytest.mark.unit
    def test_config_missing_required_fields(self, monkeypatch):
        """Test configuration validation with missing required fields."""
        monkeypatch.delenv("OPENREMOTE_URL", raising=False)
        monkeypatch.delenv("OPENREMOTE_CLIENT_ID", raising=False)
        monkeypatch.delenv("OPENREMOTE_CLIENT_SECRET", raising=False)
        
        from src.services.mcp_client_api.app.config import Config
        
        with pytest.raises(ValidationError):
            Config()

    @pytest.mark.unit
    def test_config_optional_api_keys(self, mock_env_vars, monkeypatch):
        """Test that API keys are optional."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        
        from src.services.mcp_client_api.app.config import Config
        
        config = Config()
        
        assert config.openai_api_key is None
        assert config.anthropic_api_key is None
