import json
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from openremote_client.schemas import ExternalServiceSchema

from shared.mcp_client import init_mcp_client_service
from shared.openremote_service import init_openremote_service
from .chat import init_chat_api
from .config import config
from .cors import init_cors
from .health import init_health


# FastAPI lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Init OpenRemote service
    await init_openremote_service(
        host=str(config.openremote_url),
        client_id=config.openremote_client_id,
        client_secret=config.openremote_client_secret,
        verify_SSL=config.openremote_verify_ssl,
        service_schema=ExternalServiceSchema(
            serviceId=config.openremote_service_id,
            label="Ask-Marc (MCP-Client)",
            homepageUrl="http://localhost:3000/",
            status="AVAILABLE",
        )
    )

    # Init MCP client
    mcp_config_json: dict

    if config.mcp_config is not None:
        mcp_config_json = config.mcp_config
    elif Path(config.mcp_config_file).is_file():
        with open(config.mcp_config_file, "r") as file:
            file_text = file.read()
            mcp_config_json = json.loads(file_text)
    else:
        raise RuntimeError("No MCP configuration provided.")

    await init_mcp_client_service(mcp_config_json)

    yield

app = FastAPI(
    title="OpenRemote Ask-Marc Service",
    description="MCP client integrated with OpenRemote",
    lifespan=lifespan
)


init_cors(app)
init_chat_api(app)
init_health(app)
