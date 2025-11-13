from fastapi import FastAPI
from openremote_client import OpenRemoteClient
from openremote_client.schemas import ExternalServiceSchema

from services import OpenRemoteService
from .config import config

__openremote_service: OpenRemoteService | None = None


def get_openremote_service() -> OpenRemoteService:
    global __openremote_service

    if __openremote_service is None:
        raise RuntimeError("OpenRemote service not initialized")

    return __openremote_service


async def init_openremote(app: FastAPI):
    global __openremote_service

    openremote_client = OpenRemoteClient(
        host=str(config.openremote_url),
        client_id=config.openremote_client_id,
        client_secret=config.openremote_client_secret,
        verify_SSL=config.openremote_verify_ssl
    )

    __openremote_service = await OpenRemoteService.register(
        openremote_client,
        ExternalServiceSchema(
            serviceId=config.openremote_service_id,
            label="Ask Marc MCP Service",
            homepageUrl="http://localhost:3000/",
            status="AVAILABLE",
        )
    )

