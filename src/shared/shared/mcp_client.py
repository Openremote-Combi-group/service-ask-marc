from langchain_mcp_adapters.client import MultiServerMCPClient

__mcp_service: MultiServerMCPClient | None = None


def get_mcp_client_service() -> MultiServerMCPClient:
    global __mcp_service

    if __mcp_service is None:
        raise RuntimeError("MCP service not initialized")

    return __mcp_service


async def init_mcp_client_service(mcp_config: dict):
    global __mcp_service

    __mcp_service = MultiServerMCPClient(mcp_config)
