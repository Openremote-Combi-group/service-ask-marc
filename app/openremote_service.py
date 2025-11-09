import asyncio
import time

from fastapi import FastAPI, BackgroundTasks
from openremote_client import OpenRemoteClient
from openremote_client.schemas import ExternalServiceSchema

from config import config
from logging import getLogger


class OpenRemoteService:
    __openremote_client: OpenRemoteClient
    service_id: str = config.openremote_service_id
    instance_id: int

    def __init__(self, openremote_client: OpenRemoteClient, instance_id: int):
        self.__openremote_client = openremote_client
        self.instance_id = instance_id

    async def send_heartbeat(self):
        await self.__openremote_client.services.heartbeat(self.service_id, self.instance_id)


openremote_service: OpenRemoteService


async def init_openremote_service(app: FastAPI):
    global openremote_service

    openremote_client = OpenRemoteClient(
        host=str(config.openremote_url),
        client_id=config.openremote_client_id,
        client_secret=config.openremote_client_secret,
        verify_SSL=config.openremote_verify_ssl
    )

    logger = getLogger("uvicorn.error")

    try:
        await openremote_client.status.get_health_status()
        logger.info("OpenRemote service is up and running")

        service_registry = await openremote_client.services.register_service(
            ExternalServiceSchema(
                serviceId=config.openremote_service_id,
                label="Ask Marc service",
                icon='mdi-creation',
                homepageUrl="http://localhost:8000",
                status="AVAILABLE"
            )
        )

        openremote_service = OpenRemoteService(
            openremote_client=openremote_client,
            instance_id=service_registry.content.instanceId
        )

        logger.info(f"Registered {service_registry.content.serviceId} service with ID {service_registry.content.serviceId}")

        async def heartbeat(or_service: OpenRemoteService):
            while True:
                await or_service.send_heartbeat()
                await asyncio.sleep(config.openremote_heartbeat_interval)
                logger.info("Sent heartbeat to OpenRemote")

        asyncio.run_coroutine_threadsafe(heartbeat(openremote_service), asyncio.get_event_loop())


    except Exception as e:
        logger.error("Failed to connect to OpenRemote")
        logger.debug(e)

        raise RuntimeError("Failed to connect to OpenRemote")
