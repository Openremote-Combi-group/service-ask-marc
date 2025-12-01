"""Tests for CORS middleware configuration."""
import pytest
from unittest.mock import MagicMock, patch
from fastapi import FastAPI


class TestCORS:
    """Test cases for CORS middleware."""

    @pytest.mark.unit
    def test_cors_initialization(self, mock_env_vars):
        """Test CORS middleware is properly initialized."""
        from src.services.mcp_client_api.app.cors import init_cors
        
        app = FastAPI()
        init_cors(app)
        
        # Check that CORS middleware was added
        middleware_classes = [m.cls.__name__ for m in app.user_middleware]
        assert "CORSMiddleware" in middleware_classes

    @pytest.mark.unit
    def test_cors_with_allowed_domains(self, mock_env_vars, monkeypatch):
        """Test CORS with specific allowed domains."""
        monkeypatch.setenv("CORS_ALLOWED_DOMAINS", "http://localhost:3000,http://example.com")
        
        from src.services.mcp_client_api.app.config import Config
        from src.services.mcp_client_api.app.cors import init_cors
        
        # Need to reload config with new env var
        config = Config()
        config.cors_allowed_domains = {"http://localhost:3000", "http://example.com"}
        
        app = FastAPI()
        
        with patch('src.services.mcp_client_api.app.cors.config', config):
            init_cors(app)
        
        # Verify middleware was added
        middleware_classes = [m.cls.__name__ for m in app.user_middleware]
        assert "CORSMiddleware" in middleware_classes
