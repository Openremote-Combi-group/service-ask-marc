from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='allow',
    )

    app_debug: bool = False

    app_static_folder: str = 'static'

    app_homepage_url: str = '/'

    # database_url: PostgresDsn | MySQLDsn | MariaDBDsn
    # database_prefix: str | None = 'ask_marc_'

    openremote_url: HttpUrl
    openremote_client_id: str
    openremote_client_secret: str
    openremote_verify_ssl: bool = True
    openremote_service_id: str = 'MCP-Client-API'
    openremote_heartbeat_interval: int = 30

    mcp_config: dict | None = None
    mcp_config_file: str = 'mcp_config.json'

    openai_api_key: str | None = None
    anthropic_api_key: str | None = None

    base_url: str = '/'

    cors_allowed_domains: set[str] = set()


config = Config()
