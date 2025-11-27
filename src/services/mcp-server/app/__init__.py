from contextlib import asynccontextmanager

from fastmcp import FastMCP
from openremote_client.schemas import ExternalServiceSchema

from shared.openremote_service import init_openremote_service
from .config import config
from .health import init_health
from .services import init_services

mcp = FastMCP("OpenRemote Tools")


init_health(mcp)

app = mcp.http_app()


def extend_lifespan(original_lifespan):
    """
    Wraps FastMCP's existing lifespan to add custom background tasks.
    Preserves the session manager lifespan while adding custom logic.
    """
    @asynccontextmanager
    async def combined_lifespan(app):
        # Run FastMCP's original lifespan (manages session manager)
        async with original_lifespan(app):
            # Init OpenRemote service
            await init_openremote_service(
                host=str(config.openremote_url),
                client_id=config.openremote_client_id,
                client_secret=config.openremote_client_secret,
                verify_SSL=config.openremote_verify_ssl,
                service_schema=ExternalServiceSchema(
                    serviceId=config.openremote_service_id,
                    label="MCP Server",
                    homepageUrl="http://localhost:8420",
                    status="AVAILABLE",
                )
            )

            await init_services(mcp)

            yield

    return combined_lifespan

app.router.lifespan_context = extend_lifespan(app.router.lifespan_context)

