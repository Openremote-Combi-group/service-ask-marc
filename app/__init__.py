from fastapi import FastAPI
from contextlib import asynccontextmanager
#from .database import init_database
from .cors import init_cors
from .openremote_service import init_openremote_service
from .config import config


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_openremote_service(app)

    yield
#     await init_database(str(config.database_url))
#
#     yield


app = FastAPI(
    title="OpenRemote Ask-Marc Service",
    description="A bridge for OpenRemote to communicate with AI models like ChatGPT or Claude. And provide configuration to connect them to tools using MCP.",
    lifespan=lifespan
)


@app.get("/")
def home_page():
    return {"message": "Welcome to OpenRemote Ask-Marc Service"}

init_cors(app)