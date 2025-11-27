from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

import logging


logger = logging.getLogger("uvicorn")

class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='allow'
    )

    app_debug: bool = False

    openremote_url: HttpUrl
    openremote_client_id: str
    openremote_client_secret: str
    openremote_verify_ssl: bool = True
    openremote_service_id: str = 'MCP-Server'
    openremote_heartbeat_interval: int = 30

    base_url: str = '/'

    cors_allowed_domains: set[str] = set()


config = Config()

if config.app_debug:
    logging.basicConfig(level=logging.DEBUG)