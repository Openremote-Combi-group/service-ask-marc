import asyncio
from uuid import uuid4
import json

from fastapi import APIRouter, WebSocket, FastAPI
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from langchain_mcp_adapters.client import MultiServerMCPClient

from app.config import config

client = MultiServerMCPClient(
    {
        "openremote": {
            "transport": "streamable_http",
            "url": "http://localhost:8000/mcp"
        }
    }
)


router = APIRouter()

# Model mapping for langchain init_chat_model
MODEL_MAPPING = {
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
    
    tools = await client.get_tools()
    
    messages: list[BaseMessage] = [
        SystemMessage(
            id=str(uuid4()),
            content="You are an helpful assistant for the OpenRemote Platform. Markdown is supported so please render in Markdown."
        )
    ]
    
    # Wait for initial message with model selection
    try:
        initial_data = await websocket.receive_text()
        initial_message = json.loads(initial_data)
        
        if initial_message.get('type') == 'init':
            selected_model = initial_message.get('model', 'gpt-4o')
            
            # Validate model exists
            if selected_model not in MODEL_MAPPING:
                await websocket.send_json({
                    "type": "error",
                    "content": f"Invalid model selected: {selected_model}"
                })
                await websocket.close()
                return
            
            model_config = MODEL_MAPPING[selected_model]
            
            # Check if API key is configured
            if model_config['model_provider'] == 'openai' and not config.openai_api_key:
                await websocket.send_json({
                    "type": "error",
                    "content": "OpenAI API key is not configured. Please add OPENAI_API_KEY to your environment variables."
                })
                await websocket.close()
                return
            
            if model_config['model_provider'] == 'anthropic' and not config.anthropic_api_key:
                await websocket.send_json({
                    "type": "error",
                    "content": "Anthropic API key is not configured. Please add ANTHROPIC_API_KEY to your environment variables."
                })
                await websocket.close()
                return
            
            # Initialize model with proper configuration
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
                await websocket.close()
                return
            
            agent = create_agent(
                model,
                tools
            )
            
            # Send ready signal
            await websocket.send_json({"type": "ready"})
        else:
            await websocket.send_json({
                "type": "error",
                "content": "Expected initialization message"
            })
            await websocket.close()
            return
            
    except json.JSONDecodeError:
        await websocket.send_json({
            "type": "error",
            "content": "Invalid message format"
        })
        await websocket.close()
        return
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "content": f"Connection error: {str(e)}"
        })
        await websocket.close()
        return

    while True:
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
                "content": ai_message.content
            })




def init_chat_api(app: FastAPI):
    app.include_router(router)