import asyncio
from uuid import uuid4

from fastapi import APIRouter, WebSocket, FastAPI
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient(
    {
        "openremote": {
            "transport": "streamable_http",
            "url": "http://localhost:8000/mcp"
        }
    }
)


async def run_langchain_agent():
    """Main logic: Connect to MCP + Run LangChain agent loop."""
    tools = await client.get_tools()

    agent = create_agent(
        "openai:gpt-4.1",
        tools
    )

    response = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Can you Ask Marc if life has any meaning?"
                }
            ]
        }
    )

    print(response)

router = APIRouter()


@router.websocket('/chat')
async def chat(websocket: WebSocket):
    tools = await client.get_tools()

    model = init_chat_model(
        model="gpt-4.1",
        temperature=0.1
    )

    agent = create_agent(
        model,
        tools
    )

    await websocket.accept()

    messages: list[BaseMessage] = [
        SystemMessage(
            id=str(uuid4()),
            content="You are an helpful assistant for the OpenRemote Platform."
        )
    ]

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




def init_chat_api(app: FastAPI):
    app.include_router(router)


if __name__ == "__main__":
    asyncio.run(run_langchain_agent())