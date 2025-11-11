from contextlib import asynccontextmanager

from fastapi import FastAPI
from openremote_client import OpenRemoteClient

from config import config
from .chat import init_chat_api
from .cors import init_cors
from .mcp_api import mcp
from .openremote_service import OpenRemoteService


# FastAPI lifespan
@asynccontextmanager
async def app_lifespan(app: FastAPI):
    openremote_client = OpenRemoteClient(
        host=str(config.openremote_url),
        client_id=config.openremote_client_id,
        client_secret=config.openremote_client_secret,
        verify_SSL=config.openremote_verify_ssl
    )

    openremote_service = await OpenRemoteService.register(openremote_client)

    yield

    await openremote_service.deregister()

# Transform the MCP app into a Starlette app
mcp_app = mcp.http_app(
    path="/", transport="streamable-http", stateless_http=True
)

# Combine the FastAPI & FastMCP lifespans
@asynccontextmanager
async def combined_lifespan(app: FastAPI):
    # Run both lifespans
    async with app_lifespan(app):
        async with mcp_app.lifespan(app):
            yield

app = FastAPI(
    title="OpenRemote Ask-Marc Service",
    description="MCP client integrated with OpenRemote",
    lifespan=combined_lifespan
)

app.mount("/mcp", mcp_app, name="MCP")
init_cors(app)
init_chat_api(app)