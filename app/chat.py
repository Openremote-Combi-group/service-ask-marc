import asyncio

from langchain.agents import create_agent
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


if __name__ == "__main__":
    asyncio.run(run_langchain_agent())