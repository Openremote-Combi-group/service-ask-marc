import json
import logging
from uuid import uuid4

from fastapi import APIRouter, WebSocket, FastAPI
from starlette.websockets import WebSocketDisconnect
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage

try:  # pragma: no cover - optional dependency
    from langchain_ollama import ChatOllama  # type: ignore
except ImportError:  # pragma: no cover - backwards compatibility
    try:
        from langchain_community.chat_models import ChatOllama  # type: ignore
    except ImportError:
        ChatOllama = None

from shared.mcp_client import get_mcp_client_service
from .config import config

router = APIRouter()
logger = logging.getLogger("mcp_client_api.chat")

# Model mapping for langchain init_chat_model
MODEL_MAPPING = {
    'ollama-llama3': {'model': 'llama3.1:8b', 'model_provider': 'ollama'},  # Changed!
    'gpt-4o': {'model': 'gpt-4o', 'model_provider': 'openai'},
    'gpt-4o-mini': {'model': 'gpt-4o-mini', 'model_provider': 'openai'},
    'gpt-4-turbo': {'model': 'gpt-4-turbo', 'model_provider': 'openai'},
    'gpt-4': {'model': 'gpt-4', 'model_provider': 'openai'},
    'gpt-3.5-turbo': {'model': 'gpt-3.5-turbo', 'model_provider': 'openai'},
    'claude-3-5-sonnet-20241022': {'model': 'claude-3-5-sonnet-20241022', 'model_provider': 'anthropic'},
    'claude-3-5-haiku-20241022': {'model': 'claude-3-5-haiku-20241022', 'model_provider': 'anthropic'},
    'claude-3-opus-20240229': {'model': 'claude-3-opus-20240229', 'model_provider': 'anthropic'},
}


@router.websocket('/chat')
async def chat(websocket: WebSocket):
    await websocket.accept()
    logger.info(
        "WebSocket connection accepted",
        extra={
            "client": getattr(websocket, "client", None),
        }
    )

    connection_closed = False

    async def safe_send(payload: dict) -> bool:
        nonlocal connection_closed
        if connection_closed:
            return False
        try:
            await websocket.send_json(payload)
            return True
        except WebSocketDisconnect:
            connection_closed = True
            logger.info("Client disconnected while sending message")
            return False
        except RuntimeError as send_error:
            connection_closed = True
            logger.info(
                "Attempted to send on closed websocket",
                extra={"error": str(send_error)},
            )
            return False

    async def safe_close(code: int | None = None) -> None:
        nonlocal connection_closed
        if connection_closed:
            return
        try:
            if code is None:
                await websocket.close()
            else:
                await websocket.close(code=code)
        except WebSocketDisconnect:
            pass
        finally:
            connection_closed = True

    mcp_service = get_mcp_client_service()

    # Try to load MCP tools, but continue without them if they fail
    tools: list = []
    try:
        tools = await mcp_service.get_tools()
        logger.info(f"Loaded {len(tools)} MCP tools")
    except Exception as e:
        logger.warning(f"MCP tools unavailable, continuing without them: {e}")
        tools = []

    messages: list[BaseMessage] = [
        SystemMessage(
            id=str(uuid4()),
            content="You are an helpful assistant for the OpenRemote Platform. Markdown is supported so please render in Markdown."
        )
    ]

    # Wait for an initial message with model selection
    try:
        initial_message = await websocket.receive_json()
        logger.debug("Initial websocket message received", extra={"message_type": initial_message.get('type')})

        if initial_message.get('type') == 'init':
            selected_model = initial_message.get('model', 'gpt-4o')
            logger.debug("Client selected model", extra={"model_id": selected_model})

            # Validate model exists
            if selected_model not in MODEL_MAPPING:
                if not await safe_send({
                    "type": "error",
                    "content": f"Invalid model selected: {selected_model}"
                }):
                    return
                logger.error(
                    "Client selected invalid model",
                    extra={"model_id": selected_model}
                )
                await safe_close()
                return

            model_config = MODEL_MAPPING[selected_model]
            logger.debug(
                "Resolved model configuration",
                extra={
                    "model_provider": model_config['model_provider'],
                    "model": model_config['model'],
                }
            )

            # Check if API key is configured or required
            if model_config['model_provider'] == 'openai' and not config.openai_api_key:
                if not await safe_send({
                    "type": "error",
                    "content": "OpenAI API key is not configured. Please add OPENAI_API_KEY to your environment variables."
                }):
                    return
                logger.error("OpenAI API key not configured")
                await safe_close()
                return

            if model_config['model_provider'] == 'anthropic' and not config.anthropic_api_key:
                if not await safe_send({
                    "type": "error",
                    "content": "Anthropic API key is not configured. Please add ANTHROPIC_API_KEY to your environment variables."
                }):
                    return
                logger.error("Anthropic API key not configured")
                await safe_close()
                return

            # Initialize model with proper configuration
            agent = None
            model = None
            supports_streaming = True
            provider = model_config['model_provider']

            if provider == 'ollama':
                if ChatOllama is None:
                    if not await safe_send({
                        "type": "error",
                        "content": "Local model support requires langchain-community to be installed in the service image.",
                    }):
                        return
                    logger.error("ChatOllama dependency missing; install langchain-community for local models")
                    await safe_close()
                    return

                if not config.ollama_base_url:
                    if not await safe_send({
                        "type": "error",
                        "content": "Ollama base URL is not configured. Please add OLLAMA_BASE_URL to your environment variables or .env file."
                    }):
                        return
                    logger.error("Ollama base URL not configured")
                    await safe_close()
                    return

                try:
                    model = ChatOllama(
                        model=model_config['model'],
                        base_url=str(config.ollama_base_url),
                        temperature=0.1,
                    )
                    logger.info(
                        "Configured Ollama Chat model",
                        extra={
                            "model": model_config['model'],
                            "base_url": str(config.ollama_base_url),
                        },
                    )
                except Exception as model_error:
                    if not await safe_send({
                        "type": "error",
                        "content": f"Failed to initialize local model: {model_error}",
                    }):
                        return
                    logger.exception("Failed to initialize ChatOllama model")
                    await safe_close()
                    return
            else:
                try:
                    model = init_chat_model(
                        model=model_config['model'],
                        model_provider=provider,
                        temperature=0.1
                    )
                except Exception as e:
                    if not await safe_send({
                        "type": "error",
                        "content": f"Failed to initialize AI model: {str(e)}"
                    }):
                        return
                    logger.exception("Failed to initialize AI model")
                    await safe_close()
                    return

            logger.debug(
                "Preparing model pipeline",
                extra={
                    "supports_streaming": supports_streaming,
                    "provider": provider,
                }
            )

            if tools:
                try:
                    agent = create_agent(
                        model,
                        tools
                    )
                except NotImplementedError:
                    if not await safe_send({
                        "type": "warning",
                        "content": "Selected model does not support tool usage. Continuing without MCP tools.",
                    }):
                        return
                    logger.warning("Selected model does not support tool usage; continuing without tools")
        else:
            if not await safe_send({
                "type": "error",
                "content": "Expected initialization message"
            }):
                return
            logger.error("Initialization message invalid or missing")
            await safe_close()
            return

    except json.JSONDecodeError as e:
        await safe_send({
            "type": "error",
            "content": "Invalid message format"
        })
        logger.exception("Invalid JSON received during initialization")
        await safe_close()
        return
    except Exception as e:
        await safe_send({
            "type": "error",
            "content": f"Connection error: {str(e)}"
        })
        await safe_close()
        logger.exception("Unexpected error during initialization")
        return

    while True:
        try:
            if not await safe_send({"type": "ready"}):
                break
            human_prompt = await websocket.receive_text()
            prompt_preview = human_prompt[:200] + ('...' if len(human_prompt) > 200 else '')
            logger.debug("Received human prompt", extra={"preview": prompt_preview})
        except WebSocketDisconnect:
            logger.info("Client disconnected from chat websocket")
            break

        human_message = HumanMessage(
            id=str(uuid4()),
            content=human_prompt
        )

        messages.append(human_message)

        if not await safe_send(
            {
                "id": human_message.id,
                "type": "human",
                "content": human_message.content
            }
        ):
            break

        message_id = str(uuid4())
        accumulated_content = ""
        done_sent = False

        if agent:
            logger.debug("Streaming response via agent")
            async for event in agent.astream_events(
                {"messages": messages},
                version="v2"
            ):
                kind = event["event"]

                # Stream token chunks from the LLM
                if kind == "on_chat_model_stream":
                    chunk = event["data"]["chunk"]
                    if hasattr(chunk, "content") and chunk.content:
                        accumulated_content += chunk.content
                        if not await safe_send({
                            "id": message_id,
                            "type": "token",
                            "content": chunk.content
                        }):
                            break

                # Stream tool calls and results
                elif kind == "on_tool_start":
                    if not await safe_send({
                        "id": message_id,
                        "tool_id": event["run_id"],
                        "type": "tool_start",
                        "name": event["name"],
                        "input": event["data"].get("input")
                    }):
                        break

                elif kind == "on_tool_end":
                    if not await safe_send({
                        "id": message_id,
                        "type": "tool_end",
                        "tool_id": event["run_id"],
                        "name": event["name"],
                        "output": event["data"].get("output").content
                    }):
                        break

            if connection_closed:
                break

            if not await safe_send({
                "id": message_id,
                "type": "done",
                "content": accumulated_content
            }):
                break
            done_sent = True

            # Add the AI's response to the messages list
            ai_message = AIMessage(
                id=message_id,
                content=accumulated_content
            )
            messages.append(ai_message)

        else:
            if supports_streaming:
                try:
                    logger.debug("Streaming response via remote model")
                    async for chunk in model.astream(messages):
                        if hasattr(chunk, "content") and chunk.content:
                            accumulated_content += chunk.content
                            if not await safe_send({
                                "id": message_id,
                                "type": "token",
                                "content": chunk.content
                            }):
                                break
                    if connection_closed:
                        break
                    if not await safe_send({
                        "id": message_id,
                        "type": "done",
                        "content": accumulated_content
                    }):
                        break
                    done_sent = True
                except (NotImplementedError, ValueError) as stream_error:
                    logger.warning(
                        "Model streaming unavailable, falling back to ainvoke",
                        extra={"error": str(stream_error)},
                        exc_info=True
                    )
                    supports_streaming = False
                except Exception as stream_error:
                    if not await safe_send({
                        "type": "error",
                        "content": f"Model streaming failed: {stream_error}"
                    }):
                        break
                    logger.exception("Model streaming failed")
                    continue

            if not done_sent:
                try:
                    logger.debug("Invoking remote model without streaming")
                    fallback_response = await model.ainvoke(messages)
                except Exception as invoke_error:
                    if not await safe_send({
                        "type": "error",
                        "content": f"Model invocation failed: {invoke_error}"
                    }):
                        break
                    logger.exception("Model invocation failed")
                    continue

                fallback_content = getattr(fallback_response, "content", str(fallback_response)) or ""
                accumulated_content = fallback_content
                response_preview = accumulated_content[:200] + ('...' if len(accumulated_content) > 200 else '')
                logger.debug("Remote model response received", extra={"preview": response_preview})

                if fallback_content:
                    if not await safe_send({
                        "id": message_id,
                        "type": "token",
                        "content": fallback_content
                    }):
                        break

                if not await safe_send({
                    "id": message_id,
                    "type": "done",
                    "content": accumulated_content
                }):
                    break
                done_sent = True

            if done_sent:
                ai_message = AIMessage(
                    id=message_id,
                    content=accumulated_content
                )
                messages.append(ai_message)

        if connection_closed:
            break

def init_chat_api(app: FastAPI):
    app.include_router(router, prefix='/api')