import json
import logging
from urllib.parse import urlparse
from uuid import uuid4

import httpx
from fastapi import APIRouter, WebSocket, FastAPI
from starlette.websockets import WebSocketDisconnect
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage

from shared.mcp_client import get_mcp_client_service
from .config import config

router = APIRouter()
logger = logging.getLogger("mcp_client_api.chat")

# Model mapping for langchain init_chat_model
MODEL_MAPPING = {
    'ollama-llama3': {'model': 'llama3', 'model_provider': 'ollama'},
    'gpt-4o': {'model': 'gpt-4o', 'model_provider': 'openai'},
    'gpt-4o-mini': {'model': 'gpt-4o-mini', 'model_provider': 'openai'},
    'gpt-4-turbo': {'model': 'gpt-4-turbo', 'model_provider': 'openai'},
    'gpt-4': {'model': 'gpt-4', 'model_provider': 'openai'},
    'gpt-3.5-turbo': {'model': 'gpt-3.5-turbo', 'model_provider': 'openai'},
    'claude-3-5-sonnet-20241022': {'model': 'claude-3-5-sonnet-20241022', 'model_provider': 'anthropic'},
    'claude-3-5-haiku-20241022': {'model': 'claude-3-5-haiku-20241022', 'model_provider': 'anthropic'},
    'claude-3-opus-20240229': {'model': 'claude-3-opus-20240229', 'model_provider': 'anthropic'},
}


async def invoke_ollama_chat(base_urls: list[str], model_name: str, messages: list[BaseMessage]) -> str:
    """Call the Ollama chat endpoint and return the assistant content."""

    if not base_urls:
        raise RuntimeError("No Ollama hosts configured")

    role_map = {
        "human": "user",
        "ai": "assistant",
    }

    payload = {
        "model": model_name,
        "messages": [
            {
                "role": role_map.get(message.type, message.type),
                "content": message.content if isinstance(message.content, str) else str(message.content),
            }
            for message in messages
        ],
        "stream": False,
    }

    last_error: Exception | None = None

    logger.debug(
        "Preparing Ollama request",
        extra={
            "model": model_name,
            "base_urls": base_urls,
            "message_types": [message.type for message in messages],
        }
    )

    async with httpx.AsyncClient(timeout=60.0) as client:
        for base_url in base_urls:
            target_url = f"{base_url.rstrip('/')}/api/chat"
            try:
                logger.debug("Calling Ollama", extra={"target_url": target_url})
                response = await client.post(target_url, json=payload)
                response.raise_for_status()
                data = response.json()

                if isinstance(data, dict):
                    if "message" in data and isinstance(data["message"], dict):
                        return data["message"].get("content", "") or ""

                    if "response" in data:
                        return data.get("response") or ""

                return ""
            except httpx.HTTPStatusError as exc:
                logger.warning(
                    "Ollama responded with HTTP error",
                    extra={
                        "target_url": target_url,
                        "status_code": exc.response.status_code,
                        "response_text": exc.response.text,
                    }
                )
                if exc.response.status_code == 404 and "not found" in exc.response.text.lower():
                    raise RuntimeError(
                        f"Ollama model '{model_name}' is not available. Run `ollama pull {model_name}` on the host serving {target_url} and try again."
                    ) from exc
                raise RuntimeError(
                    f"Ollama responded with status code {exc.response.status_code}: {exc.response.text}"
                ) from exc
            except httpx.RequestError as exc:
                last_error = exc
                logger.warning(
                    "Failed to reach Ollama host",
                    extra={"target_url": target_url, "error": str(exc)}
                )
                continue

    if last_error:
        logger.error(
            "Unable to reach Ollama hosts",
            extra={"base_urls": base_urls, "last_error": str(last_error)}
        )
        raise RuntimeError(
            "Unable to reach Ollama host(s): " + ", ".join(base_urls)
            + f". Last error: {last_error}"
        )

    logger.error(
        "Ollama hosts exhausted without specific error",
        extra={"base_urls": base_urls}
    )
    raise RuntimeError("Unable to reach Ollama host without specific error")


@router.websocket('/chat')
async def chat(websocket: WebSocket):
    await websocket.accept()
    logger.info(
        "WebSocket connection accepted",
        extra={
            "client": getattr(websocket, "client", None),
        }
    )

    mcp_service = get_mcp_client_service()

    ollama_config: dict | None = None

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
                await websocket.send_json({
                    "type": "error",
                    "content": f"Invalid model selected: {selected_model}"
                })
                logger.error(
                    "Client selected invalid model",
                    extra={"model_id": selected_model}
                )
                await websocket.close()
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
                await websocket.send_json({
                    "type": "error",
                    "content": "OpenAI API key is not configured. Please add OPENAI_API_KEY to your environment variables."
                })
                logger.error("OpenAI API key not configured")
                await websocket.close()
                return

            if model_config['model_provider'] == 'anthropic' and not config.anthropic_api_key:
                await websocket.send_json({
                    "type": "error",
                    "content": "Anthropic API key is not configured. Please add ANTHROPIC_API_KEY to your environment variables."
                })
                logger.error("Anthropic API key not configured")
                await websocket.close()
                return

            # Initialize model with proper configuration
            tools: list = []
            agent = None
            supports_streaming = model_config['model_provider'] != 'ollama'
            logger.debug(
                "Preparing model pipeline",
                extra={
                    "supports_streaming": supports_streaming,
                    "provider": model_config['model_provider'],
                }
            )

            if model_config['model_provider'] == 'ollama':
                if not config.ollama_base_url:
                    await websocket.send_json({
                        "type": "error",
                        "content": "Ollama base URL is not configured. Please add OLLAMA_BASE_URL to your environment variables or .env file."
                    })
                    logger.error("Ollama base URL not configured")
                    await websocket.close()
                    return

                ollama_config = {
                    "model": model_config['model'],
                    "base_url": str(config.ollama_base_url),
                }
                logger.info(
                    "Configured Ollama model",
                    extra={
                        "model": ollama_config['model'],
                        "base_url": ollama_config['base_url'],
                    }
                )

                model = None
            else:
                try:
                    model = init_chat_model(
                        model=model_config['model'],
                        model_provider=model_config['model_provider'],
                        temperature=0.1
                    )
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "content": f"Failed to initialize AI model: {str(e)}"
                    })
                    logger.exception("Failed to initialize AI model")
                    await websocket.close()
                    return

                try:
                    logger.debug("Loading MCP tools")
                    tools = await mcp_service.get_tools()
                    logger.debug(
                        "Loaded MCP tools",
                        extra={"tool_count": len(tools)}
                    )
                except Exception as load_error:
                    await websocket.send_json({
                        "type": "warning",
                        "content": "Failed to load MCP tools; continuing without tool support.",
                    })
                    logger.warning(
                        "Failed to load MCP tools; continuing without tools",
                        extra={"error": str(load_error)}
                    )
                    logger.debug(
                        "MCP tool loading stack trace",
                        exc_info=load_error
                    )
                    tools = []

            if tools:
                try:
                    agent = create_agent(
                        model,
                        tools
                    )
                except NotImplementedError:
                    await websocket.send_json({
                        "type": "warning",
                        "content": "Selected model does not support tool usage. Continuing without MCP tools.",
                    })
                    logger.warning("Selected model does not support tool usage; continuing without tools")
        else:
            await websocket.send_json({
                "type": "error",
                "content": "Expected initialization message"
            })
            logger.error("Initialization message invalid or missing")
            await websocket.close()
            return

    except json.JSONDecodeError as e:
        await websocket.send_json({
            "type": "error",
            "content": "Invalid message format"
        })
        logger.exception("Invalid JSON received during initialization")
        await websocket.close()
        return
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "content": f"Connection error: {str(e)}"
        })
        await websocket.close()
        logger.exception("Unexpected error during initialization")
        return

    while True:
        try:
            await websocket.send_json({"type": "ready"})
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

        await websocket.send_json(
            {
                "id": human_message.id,
                "type": "human",
                "content": human_message.content
            }
        )

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

                if kind == "on_chat_model_stream":
                    chunk = event["data"]["chunk"]
                    if hasattr(chunk, "content") and chunk.content:
                        accumulated_content += chunk.content
                        await websocket.send_json({
                            "id": message_id,
                            "type": "token",
                            "content": chunk.content
                        })

                elif kind == "on_tool_start":
                    await websocket.send_json({
                        "id": message_id,
                        "tool_id": event["run_id"],
                        "type": "tool_start",
                        "name": event["name"],
                        "input": event["data"].get("input")
                    })

                elif kind == "on_tool_end":
                    await websocket.send_json({
                        "id": message_id,
                        "type": "tool_end",
                        "tool_id": event["run_id"],
                        "name": event["name"],
                        "output": event["data"].get("output").content
                    })

            await websocket.send_json({
                "id": message_id,
                "type": "done",
                "content": accumulated_content
            })
            done_sent = True

            ai_message = AIMessage(
                id=message_id,
                content=accumulated_content
            )
            messages.append(ai_message)

        elif ollama_config:
            base_urls = [ollama_config["base_url"]]
            parsed_url = urlparse(ollama_config["base_url"])

            if parsed_url.hostname in {"127.0.0.1", "localhost"}:
                for fallback_url in ("http://host.docker.internal:11434", "http://ollama:11434"):
                    if fallback_url not in base_urls:
                        base_urls.append(fallback_url)

            try:
                logger.info(
                    "Invoking Ollama model",
                    extra={
                        "model": ollama_config["model"],
                        "base_urls": base_urls,
                        "message_count": len(messages),
                    }
                )
                fallback_content = await invoke_ollama_chat(
                    base_urls,
                    ollama_config["model"],
                    messages,
                )
            except Exception as ollama_error:
                await websocket.send_json({
                    "type": "error",
                    "content": f"Local model invocation failed: {ollama_error}",
                })
                logger.exception("Local model invocation failed")
                continue

            accumulated_content = fallback_content or ""
            response_preview = accumulated_content[:200] + ('...' if len(accumulated_content) > 200 else '')
            logger.debug("Ollama response received", extra={"preview": response_preview})

            if accumulated_content:
                await websocket.send_json({
                    "id": message_id,
                    "type": "token",
                    "content": accumulated_content,
                })

            await websocket.send_json({
                "id": message_id,
                "type": "done",
                "content": accumulated_content,
            })
            done_sent = True

            ai_message = AIMessage(
                id=message_id,
                content=accumulated_content,
            )
            messages.append(ai_message)

        else:
            if supports_streaming:
                try:
                    logger.debug("Streaming response via remote model")
                    async for chunk in model.astream(messages):
                        if hasattr(chunk, "content") and chunk.content:
                            accumulated_content += chunk.content
                            await websocket.send_json({
                                "id": message_id,
                                "type": "token",
                                "content": chunk.content
                            })
                    await websocket.send_json({
                        "id": message_id,
                        "type": "done",
                        "content": accumulated_content
                    })
                    done_sent = True
                except (NotImplementedError, ValueError) as stream_error:
                    logger.warning(
                        "Model streaming unavailable, falling back to ainvoke",
                        extra={"error": str(stream_error)},
                        exc_info=True
                    )
                    supports_streaming = False
                except Exception as stream_error:
                    await websocket.send_json({
                        "type": "error",
                        "content": f"Model streaming failed: {stream_error}"
                    })
                    logger.exception("Model streaming failed")
                    continue

            if not done_sent:
                try:
                    logger.debug("Invoking remote model without streaming")
                    fallback_response = await model.ainvoke(messages)
                except Exception as invoke_error:
                    await websocket.send_json({
                        "type": "error",
                        "content": f"Model invocation failed: {invoke_error}"
                    })
                    logger.exception("Model invocation failed")
                    continue

                fallback_content = getattr(fallback_response, "content", str(fallback_response)) or ""
                accumulated_content = fallback_content
                response_preview = accumulated_content[:200] + ('...' if len(accumulated_content) > 200 else '')
                logger.debug("Remote model response received", extra={"preview": response_preview})

                if fallback_content:
                    await websocket.send_json({
                        "id": message_id,
                        "type": "token",
                        "content": fallback_content
                    })

                await websocket.send_json({
                    "id": message_id,
                    "type": "done",
                    "content": accumulated_content
                })
                done_sent = True

            if done_sent:
                ai_message = AIMessage(
                    id=message_id,
                    content=accumulated_content
                )
                messages.append(ai_message)

def init_chat_api(app: FastAPI):
    app.include_router(router, prefix='/api')