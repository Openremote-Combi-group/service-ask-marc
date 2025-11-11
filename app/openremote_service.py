import asyncio
from logging import getLogger

from openremote_client import OpenRemoteClient
from openremote_client.schemas import ExternalServiceSchema

from config import config

logger = getLogger('uvicorn.error')


class OpenRemoteService:
    client: OpenRemoteClient
    service_id: str = config.openremote_service_id
    instance_id: int

    @classmethod
    async def register(cls, openremote_client: OpenRemoteClient):
        try:
            service_registry = await openremote_client.services.register_service(
                ExternalServiceSchema(
                    serviceId=config.openremote_service_id,
                    label="Ask Marc MCP service",
                    icon='mdi-creation',
                    homepageUrl="http://localhost:3000",
                    status="AVAILABLE"
                )
            )

            return cls(
                openremote_client=openremote_client,
                instance_id=service_registry.content.instanceId
            )
        except Exception as e:
            logger.error("Failed to connect to OpenRemote")
            logger.debug(e)

            raise RuntimeError("Failed to connect to OpenRemote")


    async def __heartbeat_loop(self):
        while True:
            await asyncio.sleep(config.openremote_heartbeat_interval)
            await self.send_heartbeat()

    def __init__(self, openremote_client: OpenRemoteClient, instance_id: int):
        self.__openremote_client = openremote_client
        self.instance_id = instance_id

        asyncio.run_coroutine_threadsafe(self.__heartbeat_loop(), asyncio.get_event_loop())

        logger.info(f"Registered OpenRemote service with service_id '{self.service_id}' and instance_id '{self.instance_id}'")

    async def send_heartbeat(self):
        await self.__openremote_client.services.heartbeat(self.service_id, self.instance_id)
        logger.info("Sent heartbeat to OpenRemote")

    async def deregister(self):
        await self.__openremote_client.services.deregister_service(self.service_id, self.instance_id)
        logger.info("Deregistered OpenRemote service")
