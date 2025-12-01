"""Tests for CORS middleware configuration."""
import pytest
from unittest.mock import MagicMock, patch
from fastapi import FastAPI


class TestCORS:
    """Test cases for CORS middleware."""

    @pytest.mark.unit
    def test_cors_initialization(self, mock_env_vars):
        """Test CORS middleware is properly initialized."""
        from app.cors import init_cors
        
        app = FastAPI()
        init_cors(app)
        
        # Check that CORS middleware was added
        middleware_classes = [m.cls.__name__ for m in app.user_middleware]
        assert "CORSMiddleware" in middleware_classes

    @pytest.mark.unit
    def test_cors_with_allowed_domains(self, mock_env_vars):
        """Test CORS with specific allowed domains."""
        from app.cors import init_cors
        from app.config import Config
        
        # Create a config with allowed domains
        # Don't use env var since cors_allowed_domains is a set type and pydantic 
        # doesn't parse comma-separated strings to sets automatically
        
        # Create mock config with domains
        mock_config = MagicMock(spec=Config)
        mock_config.cors_allowed_domains = {"http://localhost:3000", "http://example.com"}
        
        app = FastAPI()
        
        with patch('app.cors.config', mock_config):
            init_cors(app)
        
        # Verify middleware was added
        middleware_classes = [m.cls.__name__ for m in app.user_middleware]
        assert "CORSMiddleware" in middleware_classes
