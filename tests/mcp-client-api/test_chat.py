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
        
        assert "ollama-llama3" in MODEL_MAPPING
        assert "gpt-4o" in MODEL_MAPPING
        assert "gpt-4o-mini" in MODEL_MAPPING
        assert "gpt-4-turbo" in MODEL_MAPPING
        assert "claude-3-5-sonnet-20241022" in MODEL_MAPPING
        
        assert MODEL_MAPPING["ollama-llama3"]["model_provider"] == "ollama"
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
        fresh_config.openai_api_key = None
        
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
                assert "OpenAI API key" in error_call["content"]
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
        fresh_config.anthropic_api_key = None
        
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

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_chat_fallback_without_agent_tools(self, mock_mcp_client, mock_env_vars, monkeypatch):
        """Test chat continues without tools when agent creation is unsupported."""

        class FakeChunk:
            def __init__(self, content: str):
                self.content = content

        class FakeModel:
            def __init__(self, *args, **kwargs):
                pass

            async def astream(self, messages):
                yield FakeChunk("test response")

        mock_mcp_client.get_tools.return_value = [MagicMock()]

        mock_websocket = AsyncMock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.receive_json = AsyncMock(return_value={
            "type": "init",
            "model": "gpt-4o"
        })
        mock_websocket.receive_text = AsyncMock(side_effect=[
            "Hello there",
            RuntimeError("stop")
        ])
        mock_websocket.send_json = AsyncMock()
        mock_websocket.close = AsyncMock()

        with patch('app.chat.get_mcp_client_service', return_value=mock_mcp_client), \
                patch('app.chat.create_agent', side_effect=NotImplementedError()), \
                patch('app.chat.init_chat_model', return_value=FakeModel()):
            from app.chat import chat

            with pytest.raises(RuntimeError):
                await chat(mock_websocket)

        sent_messages = [args[0] for args, _ in mock_websocket.send_json.call_args_list]

        warning_messages = [msg for msg in sent_messages if msg.get("type") == "warning"]
        assert warning_messages, "Expected warning message when tools unsupported"

        token_messages = [msg for msg in sent_messages if msg.get("type") == "token"]
        assert token_messages and token_messages[0]["content"] == "test response"

        done_messages = [msg for msg in sent_messages if msg.get("type") == "done"]
        assert done_messages and done_messages[0]["content"] == "test response"

        mock_websocket.close.assert_not_called()
        assert mock_mcp_client.get_tools.await_count == 1

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_chat_ollama_skips_tool_loading(self, mock_mcp_client, mock_env_vars):
        """Test Ollama model avoids loading MCP tools and uses direct invocation."""

        mock_websocket = AsyncMock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.receive_json = AsyncMock(return_value={
            "type": "init",
            "model": "ollama-llama3"
        })
        mock_websocket.receive_text = AsyncMock(side_effect=[
            "Use local model",
            RuntimeError("stop")
        ])
        mock_websocket.send_json = AsyncMock()
        mock_websocket.close = AsyncMock()

        with patch('app.chat.get_mcp_client_service', return_value=mock_mcp_client), \
            patch('app.chat.init_chat_model') as mock_init_model, \
            patch('app.chat.invoke_ollama_chat', new_callable=AsyncMock) as mock_ollama_call:
            mock_ollama_call.return_value = "ollama response"

            from app.chat import chat

            with pytest.raises(RuntimeError):
                await chat(mock_websocket)

        mock_init_model.assert_not_called()
        mock_ollama_call.assert_awaited_once()
        first_call_args = mock_ollama_call.await_args.args
        assert isinstance(first_call_args[0], list)
        assert first_call_args[0], "Expected at least one Ollama base URL"
        mock_mcp_client.get_tools.assert_not_awaited()

        sent_messages = [args[0] for args, _ in mock_websocket.send_json.call_args_list]
        token_messages = [msg for msg in sent_messages if msg.get("type") == "token"]
        assert token_messages and token_messages[0]["content"] == "ollama response"
        done_messages = [msg for msg in sent_messages if msg.get("type") == "done"]
        assert done_messages and done_messages[0]["content"] == "ollama response"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_chat_streaming_failure_fallbacks_to_ainvoke(self, mock_mcp_client, mock_env_vars):
        """Test fallback to ainvoke when streaming fails for a remote model."""

        class FakeModel:
            async def astream(self, messages):
                if False:  # pragma: no cover - ensure async generator type
                    yield None
                raise ValueError("stream unsupported")

            async def ainvoke(self, messages):
                class Response:
                    content = "fallback content"

                return Response()

        mock_websocket = AsyncMock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.receive_json = AsyncMock(return_value={
            "type": "init",
            "model": "gpt-4o"
        })
        mock_websocket.receive_text = AsyncMock(side_effect=[
            "Trigger fallback",
            RuntimeError("stop")
        ])
        mock_websocket.send_json = AsyncMock()
        mock_websocket.close = AsyncMock()

        mock_mcp_client.get_tools.return_value = []

        with patch('app.chat.get_mcp_client_service', return_value=mock_mcp_client), \
                patch('app.chat.init_chat_model', return_value=FakeModel()):
            from app.chat import chat

            with pytest.raises(RuntimeError):
                await chat(mock_websocket)

        sent_messages = [args[0] for args, _ in mock_websocket.send_json.call_args_list]

        error_messages = [msg for msg in sent_messages if msg.get("type") == "error"]
        assert not error_messages, "No error messages expected when fallback succeeds"

        token_messages = [msg for msg in sent_messages if msg.get("type") == "token"]
        assert token_messages and token_messages[0]["content"] == "fallback content"

        done_messages = [msg for msg in sent_messages if msg.get("type") == "done"]
        assert done_messages and done_messages[0]["content"] == "fallback content"

        mock_websocket.close.assert_not_called()


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
