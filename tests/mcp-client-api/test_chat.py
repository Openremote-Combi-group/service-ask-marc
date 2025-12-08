"""Tests for MCP client API chat functionality."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call
import json
from uuid import uuid4


class TestChatWebSocket:
    """Test cases for chat websocket functionality."""

    @pytest.mark.unit
    def test_model_mapping(self):
        """Test that MODEL_MAPPING contains expected models."""
        from app.chat import MODEL_MAPPING
        
        assert "gpt-4o" in MODEL_MAPPING
        assert "gpt-4o-mini" in MODEL_MAPPING
        assert "gpt-4-turbo" in MODEL_MAPPING
        assert "claude-3-5-sonnet-20241022" in MODEL_MAPPING
        
        assert MODEL_MAPPING["gpt-4o"]["model_provider"] == "openai"
        assert MODEL_MAPPING["claude-3-5-sonnet-20241022"]["model_provider"] == "anthropic"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_chat_invalid_model_selection(self, mock_mcp_client, mock_env_vars):
        """Test chat rejects invalid model selection."""
        mock_websocket = AsyncMock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.receive_json = AsyncMock(return_value={
            "type": "init",
            "model": "invalid-model"
        })
        mock_websocket.send_json = AsyncMock()
        mock_websocket.close = AsyncMock()
        
        with patch('app.chat.get_mcp_client_service', return_value=mock_mcp_client):
            from app.chat import chat
            
            await chat(mock_websocket)
            
            # Should send error and close
            mock_websocket.send_json.assert_called()
            error_call = mock_websocket.send_json.call_args[0][0]
            assert error_call["type"] == "error"
            assert "Invalid model" in error_call["content"]
            mock_websocket.close.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_chat_openai_missing_api_key(self, mock_mcp_client, mock_env_vars, monkeypatch):
        """Test chat rejects OpenAI model when API key is missing."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        
        # Reload config without API key
        import sys
        sys.path.insert(0, 'src/services/mcp-client-api')
        
        # Clear cached modules
        for key in list(sys.modules.keys()):
            if key.startswith('app'):
                del sys.modules[key]
        
        # Import and create fresh config without API key
        from app.config import Config
        fresh_config = Config()
        
        mock_websocket = AsyncMock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.receive_json = AsyncMock(return_value={
            "type": "init",
            "model": "gpt-4o"
        })
        mock_websocket.send_json = AsyncMock()
        mock_websocket.close = AsyncMock()
        
        with patch('app.chat.get_mcp_client_service', return_value=mock_mcp_client):
            with patch('app.chat.config', fresh_config):
                from app.chat import chat
                
                await chat(mock_websocket)
                
                sys.path.pop(0)
                
                # Should send error about missing API key
                error_call = mock_websocket.send_json.call_args[0][0]
                assert error_call["type"] == "error"
                # Check for either our custom message or the library's message
                assert ("OpenAI API key" in error_call["content"] or 
                        "api_key" in error_call["content"].lower())
                mock_websocket.close.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_chat_anthropic_missing_api_key(self, mock_mcp_client, mock_env_vars, monkeypatch):
        """Test chat rejects Anthropic model when API key is missing."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        
        import sys
        sys.path.insert(0, 'src/services/mcp-client-api')
        
        # Clear cached modules
        for key in list(sys.modules.keys()):
            if key.startswith('app'):
                del sys.modules[key]
        
        # Import and create fresh config without API key
        from app.config import Config
        fresh_config = Config()
        
        mock_websocket = AsyncMock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.receive_json = AsyncMock(return_value={
            "type": "init",
            "model": "claude-3-5-sonnet-20241022"
        })
        mock_websocket.send_json = AsyncMock()
        mock_websocket.close = AsyncMock()
        
        with patch('app.chat.get_mcp_client_service', return_value=mock_mcp_client):
            with patch('app.chat.config', fresh_config):
                from app.chat import chat
                
                await chat(mock_websocket)
                
                sys.path.pop(0)
                
                error_call = mock_websocket.send_json.call_args[0][0]
                assert error_call["type"] == "error"
                assert "Anthropic API key" in error_call["content"]
                mock_websocket.close.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_chat_invalid_init_message(self, mock_mcp_client, mock_env_vars):
        """Test chat rejects non-init initial message."""
        mock_websocket = AsyncMock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.receive_json = AsyncMock(return_value={
            "type": "message",
            "content": "Hello"
        })
        mock_websocket.send_json = AsyncMock()
        mock_websocket.close = AsyncMock()
        
        with patch('app.chat.get_mcp_client_service', return_value=mock_mcp_client):
            from app.chat import chat
            
            await chat(mock_websocket)
            
            error_call = mock_websocket.send_json.call_args[0][0]
            assert error_call["type"] == "error"
            assert "initialization message" in error_call["content"]
            mock_websocket.close.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_chat_json_decode_error(self, mock_mcp_client, mock_env_vars):
        """Test chat handles JSON decode errors."""
        mock_websocket = AsyncMock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.receive_json = AsyncMock(side_effect=json.JSONDecodeError("Invalid JSON", "", 0))
        mock_websocket.send_json = AsyncMock()
        mock_websocket.close = AsyncMock()
        
        with patch('app.chat.get_mcp_client_service', return_value=mock_mcp_client):
            from app.chat import chat
            
            await chat(mock_websocket)
            
            error_call = mock_websocket.send_json.call_args[0][0]
            assert error_call["type"] == "error"
            assert "Invalid message format" in error_call["content"]
            mock_websocket.close.assert_called_once()


class TestChatAPI:
    """Test cases for chat API initialization."""

    @pytest.mark.unit
    def test_init_chat_api(self):
        """Test chat API router initialization."""
        from fastapi import FastAPI
        from app.chat import init_chat_api
        
        app = FastAPI()
        init_chat_api(app)
        
        # Check that websocket route was added
        route_paths = [route.path for route in app.routes]
        assert "/api/chat" in route_paths
