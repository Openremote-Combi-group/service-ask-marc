import json
import logging
import traceback
from uuid import uuid4

from fastapi import APIRouter, WebSocket, FastAPI
from starlette.websockets import WebSocketDisconnect
from langchain.agents import create_agent, AgentType
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage, BaseMessage

try:
    from langchain_ollama import ChatOllama
except ImportError:
    from langchain_community.chat_models import ChatOllama
    ChatOllama = ChatOllama if ChatOllama else None

from langchain.chat_models import init_chat_model

from shared.mcp_client import get_mcp_client_service
from .config import config

router = APIRouter()
logger = logging.getLogger("mcp_client_api.chat")

# ✅ FIXED: Proper model mapping for frontend selector
MODEL_MAPPING = {
    # LOCAL Ollama (tool support)
    'llama3.1:8b': {
        'model': 'llama3.1:8b', 
        'model_provider': 'ollama',
        'base_url': str(config.ollama_base_url or config.local_llm_base_url),
        'temperature': 0.1,
        'is_local': True
    },
    'llama3.2': {
        'model': 'llama3.2', 
        'model_provider': 'ollama',
        'base_url': str(config.ollama_base_url or config.local_llm_base_url),
        'temperature': 0.1,
        'is_local': True
    },
    
    # REMOTE Cloud providers (tool support)
    'gpt-4o': {'model': 'gpt-4o', 'model_provider': 'openai', 'temperature': 0.1, 'is_local': False},
    'gpt-4o-mini': {'model': 'gpt-4o-mini', 'model_provider': 'openai', 'temperature': 0.1, 'is_local': False},
    'gpt-4-turbo': {'model': 'gpt-4-turbo', 'model_provider': 'openai', 'temperature': 0.1, 'is_local': False},
    'gpt-3.5-turbo': {'model': 'gpt-3.5-turbo', 'model_provider': 'openai', 'temperature': 0.1, 'is_local': False},
    
    'claude-3-5-sonnet-20241022': {'model': 'claude-3-5-sonnet-20241022', 'model_provider': 'anthropic', 'temperature': 0.1, 'is_local': False},
    'claude-3-5-haiku-20241022': {'model': 'claude-3-5-haiku-20241022', 'model_provider': 'anthropic', 'temperature': 0.1, 'is_local': False},
}

@router.websocket('/chat')
async def chat(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection accepted")

    # Load MCP tools (works - you confirmed this)
    mcp_service = get_mcp_client_service()
    tools = []
    try:
        tools = await mcp_service.get_tools()
        logger.info(f"✅ Loaded {len(tools)} MCP tools")
    except Exception as e:
        logger.warning(f"MCP tools unavailable: {e}")
        tools = []

    messages: list[BaseMessage] = [
        SystemMessage(
            id=str(uuid4()),
            content="You are a helpful assistant for the OpenRemote Platform. Markdown is supported. "
                   "Use MCP tools when needed for OpenRemote operations."
        )
    ]

    connection_closed = False

    async def safe_send(payload: dict) -> bool:
        nonlocal connection_closed
        if connection_closed:
            return False
        try:
            await websocket.send_json(payload)
            return True
        except (WebSocketDisconnect, RuntimeError):
            connection_closed = True
            return False

    # Wait for frontend model selection
    try:
        initial_message = await websocket.receive_json()
        logger.debug(f"Initial message: {initial_message}")

        if initial_message.get('type') != 'init':
            await safe_send({"type": "error", "content": "Expected init message with model selection"})
            return

        selected_model = initial_message.get('model', 'gpt-4o')
        if selected_model not in MODEL_MAPPING:
            await safe_send({"type": "error", "content": f"Model '{selected_model}' not supported"})
            return

        model_config = MODEL_MAPPING[selected_model]
        logger.info(f"Selected model: {selected_model} ({model_config['model_provider']})")

        # ✅ FLEXIBLE MODEL INITIALIZATION
        model = None
        if model_config['model_provider'] == 'ollama':
            if ChatOllama is None:
                await safe_send({"type": "error", "content": "Ollama support requires langchain-ollama"})
                return
            if not model_config.get('base_url'):
                await safe_send({"type": "error", "content": "OLLAMA_BASE_URL not configured"})
                return
            model = ChatOllama(
                model=model_config['model'],
                base_url=model_config['base_url'],
                temperature=model_config['temperature']
            )
            logger.info(f"✅ Initialized Ollama: {model_config['model']} @ {model_config['base_url']}")

        else:  # Cloud providers
            if model_config['model_provider'] == 'openai' and not config.openai_api_key:
                await safe_send({"type": "error", "content": "OPENAI_API_KEY required"})
                return
            if model_config['model_provider'] == 'anthropic' and not config.anthropic_api_key:
                await safe_send({"type": "error", "content": "ANTHROPIC_API_KEY required"})
                return

            model = init_chat_model(
                model=model_config['model'],
                model_provider=model_config['model_provider'],
                temperature=model_config['temperature'],
                openai_api_key=config.openai_api_key if model_config['model_provider'] == 'openai' else None,
                anthropic_api_key=config.anthropic_api_key if model_config['model_provider'] == 'anthropic' else None
            )
            logger.info(f"✅ Initialized cloud model: {model_config['model']}")

        # ✅ AGENT CREATION (handles tools automatically)
        agent = None
        if tools:
            try:
                agent_type = AgentType.OPENAI_FUNCTIONS if model_config['model_provider'] != 'ollama' else AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION
                agent = create_agent(model, tools, agent=agent_type)
                logger.info(f"✅ Agent created with {len(tools)} tools")
            except Exception as e:
                logger.warning(f"Agent creation failed (using plain model): {e}")
                agent = None
        else:
            logger.info("No tools available - using plain model")

        await safe_send({"type": "ready", "tools_available": len(tools) > 0})

    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        await safe_send({"type": "error", "content": f"Setup failed: {str(e)}"})
        return

    # Main chat loop
    while True:
        try:
            if not await safe_send({"type": "ready"}):
                break

            human_prompt = await websocket.receive_text()
            human_message = HumanMessage(id=str(uuid4()), content=human_prompt)
            messages.append(human_message)

            await safe_send({
                "id": human_message.id,
                "type": "human",
                "content": human_message.content
            })

            message_id = str(uuid4())
            accumulated_content = ""

            if agent:
                # ✅ AGENT STREAMING (tools work here)
                async for event in agent.astream_events(
                    {"messages": messages},
                    version="v2"
                ):
                    kind = event["event"]

                    if kind == "on_chat_model_stream":
                        chunk = event["data"]["chunk"]
                        if hasattr(chunk, "content") and chunk.content:
                            accumulated_content += chunk.content
                            await safe_send({
                                "id": message_id,
                                "type": "token",
                                "content": chunk.content
                            })

                    elif kind == "on_tool_start":
                        await safe_send({
                            "id": message_id,
                            "tool_id": event["run_id"],
                            "type": "tool_start",
                            "name": event["name"],
                            "input": event["data"].get("input")
                        })

                    elif kind == "on_tool_end":
                        await safe_send({
                            "id": message_id,
                            "type": "tool_end",
                            "tool_id": event["run_id"],
                            "name": event["name"],
                            "output": event["data"].get("output", {}).get("content", "")
                        })

            else:
                # Plain model streaming fallback
                async for chunk in model.astream(messages):
                    if hasattr(chunk, "content") and chunk.content:
                        accumulated_content += chunk.content
                        await safe_send({
                            "id": message_id,
                            "type": "token",
                            "content": chunk.content
                        })

            # Final message
            await safe_send({
                "id": message_id,
                "type": "done",
                "content": accumulated_content
            })

            ai_message = AIMessage(id=message_id, content=accumulated_content)
            messages.append(ai_message)

        except WebSocketDisconnect:
            logger.info("Client disconnected")
            break
        except Exception as e:
            logger.error(f"Chat error: {e}")
            await safe_send({"type": "error", "content": f"Chat error: {str(e)}"})
            break

def init_chat_api(app: FastAPI):
    app.include_router(router, prefix='/api')
