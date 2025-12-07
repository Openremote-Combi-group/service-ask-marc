import json
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


async def invoke_ollama_chat(base_url: str, model_name: str, messages: list[BaseMessage]) -> str:
    """Call the Ollama chat endpoint and return the assistant content."""

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

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{base_url.rstrip('/')}/api/chat",
            json=payload,
        )

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            f"Ollama call failed with status code {exc.response.status_code}: {exc.response.text}"
        ) from exc

    data = response.json()

    if isinstance(data, dict):
        if "message" in data and isinstance(data["message"], dict):
            return data["message"].get("content", "") or ""

        if "response" in data:
            return data.get("response") or ""

    return ""


@router.websocket('/chat')
async def chat(websocket: WebSocket):
    await websocket.accept()

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

        if initial_message.get('type') == 'init':
            selected_model = initial_message.get('model', 'gpt-4o')

            # Validate model exists
            if selected_model not in MODEL_MAPPING:
                await websocket.send_json({
                    "type": "error",
                    "content": f"Invalid model selected: {selected_model}"
                })
                print("Client error (Invalid model selected)")
                await websocket.close()
                return

            model_config = MODEL_MAPPING[selected_model]

            # Check if API key is configured or required
            if model_config['model_provider'] == 'openai' and not config.openai_api_key:
                await websocket.send_json({
                    "type": "error",
                    "content": "OpenAI API key is not configured. Please add OPENAI_API_KEY to your environment variables."
                })
                print("Client error (OpenAI API key not configured)")
                await websocket.close()
                return

            if model_config['model_provider'] == 'anthropic' and not config.anthropic_api_key:
                await websocket.send_json({
                    "type": "error",
                    "content": "Anthropic API key is not configured. Please add ANTHROPIC_API_KEY to your environment variables."
                })
                print("Client error (Anthropic API key not configured)")
                await websocket.close()
                return

            # Initialize model with proper configuration
            tools: list = []
            agent = None
            supports_streaming = model_config['model_provider'] != 'ollama'

            if model_config['model_provider'] == 'ollama':
                if not config.ollama_base_url:
                    await websocket.send_json({
                        "type": "error",
                        "content": "Ollama base URL is not configured. Please add OLLAMA_BASE_URL to your environment variables or .env file."
                    })
                    print("Client error (Ollama base URL not configured)")
                    await websocket.close()
                    return

                ollama_config = {
                    "model": model_config['model'],
                    "base_url": str(config.ollama_base_url),
                    "temperature": 0.1,
                }

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
                    print("Failed to initialize AI model: ", e)
                    await websocket.close()
                    return

                try:
                    tools = await mcp_service.get_tools()
                except Exception as load_error:
                    await websocket.send_json({
                        "type": "error",
                        "content": f"Failed to load MCP tools: {load_error}",
                    })
                    print("Failed to load MCP tools: ", load_error)
                    await websocket.close()
                    return

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
                    print("Selected model does not support tool usage; continuing without tools.")
        else:
            await websocket.send_json({
                "type": "error",
                "content": "Expected initialization message"
            })
            print("Web socket error (Invalid json): ")
            await websocket.close()
            return

    except json.JSONDecodeError as e:
        await websocket.send_json({
            "type": "error",
            "content": "Invalid message format"
        })
        print("Web socket error (Invalid json): ", e)
        await websocket.close()
        return
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "content": f"Connection error: {str(e)}"
        })
        await websocket.close()
        print("Web socket error: ", e)
        return

    while True:
        try:
            await websocket.send_json({"type": "ready"})
            human_prompt = await websocket.receive_text()
        except WebSocketDisconnect:
            print("Client disconnected from chat websocket")
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
            try:
                fallback_content = await invoke_ollama_chat(
                    ollama_config["base_url"],
                    ollama_config["model"],
                    messages,
                )
            except Exception as ollama_error:
                await websocket.send_json({
                    "type": "error",
                    "content": f"Local model invocation failed: {ollama_error}",
                })
                print("Local model invocation failed: ", ollama_error)
                continue

            accumulated_content = fallback_content or ""

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
                    print("Model streaming unavailable, falling back to ainvoke: ", stream_error)
                    supports_streaming = False
                except Exception as stream_error:
                    await websocket.send_json({
                        "type": "error",
                        "content": f"Model streaming failed: {stream_error}"
                    })
                    print("Model streaming failed: ", stream_error)
                    continue

            if not done_sent:
                try:
                    fallback_response = await model.ainvoke(messages)
                except Exception as invoke_error:
                    await websocket.send_json({
                        "type": "error",
                        "content": f"Model invocation failed: {invoke_error}"
                    })
                    print("Model invocation failed: ", invoke_error)
                    continue

                fallback_content = getattr(fallback_response, "content", str(fallback_response)) or ""
                accumulated_content = fallback_content

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