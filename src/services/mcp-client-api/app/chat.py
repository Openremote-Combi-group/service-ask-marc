import json
from uuid import uuid4

from fastapi import APIRouter, WebSocket, FastAPI
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage

from shared.mcp_client import get_mcp_client_service
from .config import config

router = APIRouter()

# Model mapping for langchain init_chat_model
MODEL_MAPPING = {
    'llama3.1:8b': {'model': 'llama-3.1-8b-instruct', 'model_provider': 'openai', 'is_local': True},
    'gpt-4o': {'model': 'gpt-4o', 'model_provider': 'openai', 'is_local': False},
    'gpt-4o-mini': {'model': 'gpt-4o-mini', 'model_provider': 'openai', 'is_local': False},
    'gpt-4-turbo': {'model': 'gpt-4-turbo', 'model_provider': 'openai', 'is_local': False},
    'gpt-4': {'model': 'gpt-4', 'model_provider': 'openai', 'is_local': False},
    'gpt-3.5-turbo': {'model': 'gpt-3.5-turbo', 'model_provider': 'openai', 'is_local': False},
    'claude-3-5-sonnet-20241022': {'model': 'claude-3-5-sonnet-20241022', 'model_provider': 'anthropic', 'is_local': False},
    'claude-3-5-haiku-20241022': {'model': 'claude-3-5-haiku-20241022', 'model_provider': 'anthropic', 'is_local': False},
    'claude-3-opus-20240229': {'model': 'claude-3-opus-20240229', 'model_provider': 'anthropic', 'is_local': False},
}


@router.websocket('/chat')
async def chat(websocket: WebSocket):
    await websocket.accept()

    mcp_service = get_mcp_client_service()

    # Try to load MCP tools, but continue without them if unavailable
    tools: list = []
    try:
        tools = await mcp_service.get_tools()
        print(f"Loaded {len(tools)} MCP tools")
    except Exception as e:
        print(f"MCP tools unavailable, continuing without them: {e}")
        import traceback
        traceback.print_exc()
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
        print(f"Received init message: {initial_message}")

        if initial_message.get('type') == 'init':
            selected_model = initial_message.get('model', 'gpt-4o')
            print(f"Selected model: {selected_model}")

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

            # Check if API key or local LLM is configured
            is_local = model_config.get('is_local', False)
            
            if model_config['model_provider'] == 'openai' and not is_local and not config.openai_api_key:
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

            if is_local and not config.local_llm_base_url:
                await websocket.send_json({
                    "type": "error",
                    "content": "Local LLM base URL is not configured. Please add LOCAL_LLM_BASE_URL to your environment variables."
                })
                print("Client error (Local LLM base URL not configured)")
                await websocket.close()
                return

            # Initialize model with proper configuration
            try:
                if is_local:
                    # Use local LLM via OpenAI-compatible API (llama.cpp)
                    model = init_chat_model(
                        model=model_config['model'],
                        model_provider=model_config['model_provider'],
                        base_url=str(config.local_llm_base_url),
                        api_key="not-needed",  # llama.cpp doesn't require API key
                        temperature=0.1
                    )
                else:
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

            # Create agent - let create_agent handle tool binding for all providers
            try:
                agent = create_agent(
                    model,
                    tools
                )
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "content": f"Failed to create agent: {str(e)}"
                })
                print("Failed to create agent: ", e)
                import traceback
                traceback.print_exc()
                await websocket.close()
                return
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
        await websocket.send_json({"type": "ready"})
        human_prompt = await websocket.receive_text()

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

        # Stream the agent response
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
                    await websocket.send_json({
                        "id": message_id,
                        "type": "token",
                        "content": chunk.content
                    })

            # Stream tool calls and results
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

            # Add the AI's response to the messages list
            ai_message = AIMessage(
                id=message_id,
                content=accumulated_content
            )
            messages.append(ai_message)

        await websocket.send_json({
            "id": message_id,
            "type": "done",
            "content": accumulated_content
        })

def init_chat_api(app: FastAPI):
    app.include_router(router, prefix='/api')