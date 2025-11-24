from fastapi import FastAPI, APIRouter
from httpx import HTTPStatusError
from starlette.responses import JSONResponse

from shared.openremote_service import get_openremote_service
from .config import config

health_router = APIRouter()


@health_router.get("/health")
async def health():
    openremote_service = get_openremote_service()

    try:
        await openremote_service.client.status.get_health_status()
    except HTTPStatusError:
        return JSONResponse({"status": "unhealthy", "service": config.openremote_service_id, "error": "Failed to connect to OpenRemote"}, status_code=200)

    return JSONResponse({"status": "healthy", "service": config.openremote_service_id}, status_code=200)


def init_health(app: FastAPI):
    app.include_router(health_router, prefix='/api')