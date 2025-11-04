from fastapi import FastAPI
from contextlib import asynccontextmanager
#from .database import init_database
from .cors import init_cors
from .config import config


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
#     await init_database(str(config.database_url))
#
#     yield


app = FastAPI(
    title="OpenRemote Ask-Marc Service",
    description="A bridge for OpenRemote to communicate with AI models like ChatGPT or Claude. And provide configuration to connect them to tools using MCP.",
    lifespan=lifespan
)


# Init modules
init_cors(app, config.cors_allowed_domains)

