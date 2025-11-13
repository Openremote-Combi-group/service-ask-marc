from contextlib import asynccontextmanager

from fastapi import FastAPI

from .mcp_api import mcp
from .openremote_service import init_openremote


# FastAPI lifespan
@asynccontextmanager
async def app_lifespan(app: FastAPI):

    yield
    # print("Deregerring OpenRemote service...")
    # await openremote_service.deregister()

# Transform the MCP app into a Starlette app
mcp_app = mcp.http_app(
    path="/", transport="streamable-http", stateless_http=True
)

# Combine the FastAPI & FastMCP lifespans
@asynccontextmanager
async def combined_lifespan(app: FastAPI):
    await init_openremote(app)

    # Run both lifespans
    async with app_lifespan(app):
        async with mcp_app.lifespan(app):
            yield

app = FastAPI(
    title="OpenRemote Ask-Marc Service",
    description="MCP client integrated with OpenRemote",
    lifespan=combined_lifespan
)

# Import these AFTER creating the app
from .cors import init_cors
from .chat import init_chat_api


app.mount("/mcp", mcp_app, name="MCP")
init_cors(app)
init_chat_api(app)