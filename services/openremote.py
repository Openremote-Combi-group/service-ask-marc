import asyncio
import logging

from openremote_client import OpenRemoteClient
from openremote_client.schemas import ExternalServiceSchema

logger = logging.getLogger("uvicorn")


class OpenRemoteService:
    __heartbeat_interval: int
    client: OpenRemoteClient
    service_id: str
    instance_id: int

    @classmethod
    async def register(cls, openremote_client: OpenRemoteClient, external_service_schema: ExternalServiceSchema, heartbeat_interval: int = 45):
        try:
            service_registry = await openremote_client.services.register_service(
                external_service_schema
            )

            return cls(
                client=openremote_client,
                external_service_schema=service_registry.content,
                heartbeat_interval=heartbeat_interval
            )
        except Exception as e:
            print("ERROR OPENREMOTE ERROR")
            print(e)
            logger.error("Failed to connect to OpenRemote")
            logger.debug(e)

            raise RuntimeError("Failed to connect to OpenRemote")


    async def __heartbeat_loop(self):
        while True:
            await asyncio.sleep(self.__heartbeat_interval)
            await self.send_heartbeat()

    def __init__(self, client: OpenRemoteClient, external_service_schema: ExternalServiceSchema, heartbeat_interval: int = 45):
        self.client = client
        self.service_id = external_service_schema.serviceId
        self.instance_id = external_service_schema.instanceId
        self.__heartbeat_interval = heartbeat_interval

        asyncio.run_coroutine_threadsafe(self.__heartbeat_loop(), asyncio.get_event_loop())

        logger.info(f"Registered OpenRemote service with service_id '{self.service_id}' and instance_id '{self.instance_id}'")

    async def send_heartbeat(self):
        await self.client.services.heartbeat(self.service_id, self.instance_id)
        logger.info("Sent heartbeat to OpenRemote")

    async def deregister(self):
        await self.client.services.deregister_service(self.service_id, self.instance_id)
        logger.info("Deregistered OpenRemote service")