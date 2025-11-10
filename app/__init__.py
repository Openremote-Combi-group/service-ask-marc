from contextlib import asynccontextmanager

from fastapi import FastAPI

from .cors import init_cors
from .mcp_api import init_mcp
from .openremote_service import init_openremote_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_openremote_service(app)

    yield


app = FastAPI(
    title="OpenRemote Ask-Marc Service",
    description="MCP client integrated with OpenRemote",
    lifespan=lifespan
)

#app.mount("/", StaticFiles(directory="static", html=True), name="static")

init_cors(app)
init_mcp(app)
