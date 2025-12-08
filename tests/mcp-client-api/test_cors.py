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
