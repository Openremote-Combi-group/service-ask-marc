"""Tests for MCP client API configuration."""

import pytest
from pydantic import ValidationError


class TestConfig:
    """Test cases for MCP client API config."""

    @pytest.mark.unit
    def test_config_loads_from_env(self, mock_env_vars):
        """Test configuration loads from environment variables."""
        import sys
        # Clear any cached app modules
        for key in list(sys.modules.keys()):
            if key.startswith('app'):
                del sys.modules[key]
        
        sys.path.insert(0, 'src/services/mcp-client-api')
        from app.config import Config
        sys.path.pop(0)
        
        config = Config(_env_file=None)
        
        # HttpUrl returns a Pydantic HttpUrl object, convert to string for comparison
        assert str(config.openremote_url) == "http://localhost:8080/"
        assert config.openremote_client_id == "test-client"
        assert config.openremote_client_secret == "test-secret"
        assert config.openremote_verify_ssl is False
        assert config.openai_api_key == "test-openai-key"
        assert config.anthropic_api_key == "test-anthropic-key"
        assert str(config.ollama_base_url).rstrip('/') == "http://127.0.0.1:11434"

    @pytest.mark.unit
    def test_config_defaults(self, mock_env_vars):
        """Test configuration defaults."""
        import sys
        # Clear any cached app modules
        for key in list(sys.modules.keys()):
            if key.startswith('app'):
                del sys.modules[key]
        
        sys.path.insert(0, 'src/services/mcp-client-api')
        from app.config import Config
        sys.path.pop(0)
        
        config = Config(_env_file=None)
        
        assert config.app_debug is False
        assert config.app_static_folder == "static"
        assert config.app_homepage_url == "/"
        assert config.base_url == "/"
        assert config.cors_allowed_domains == set()
        assert config.mcp_config is None
        assert config.mcp_config_file == "mcp_config.json"
        assert config.openremote_service_id == "MCP-Client-API"
        assert config.openremote_heartbeat_interval == 30
        assert str(config.ollama_base_url).rstrip('/') == "http://127.0.0.1:11434"

    @pytest.mark.unit
    def test_config_optional_api_keys(self, mock_env_vars, monkeypatch):
        """Test that API keys are optional."""
        # Clear API keys from environment
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        
        # Need to reimport to get fresh config without the keys
        import sys
        # Clear any cached app modules
        for key in list(sys.modules.keys()):
            if key.startswith('app'):
                del sys.modules[key]
        
        sys.path.insert(0, 'src/services/mcp-client-api')
        from app.config import Config
        sys.path.pop(0)
        
        config = Config(_env_file=None)
        
        # Check that the attributes exist and are None or empty string
        assert hasattr(config, 'openai_api_key')
        assert hasattr(config, 'anthropic_api_key')
        assert hasattr(config, 'ollama_base_url')
        # Pydantic may return '' for empty env vars, which is falsy
        assert not config.openai_api_key or config.openai_api_key is None
        assert not config.anthropic_api_key or config.anthropic_api_key is None
