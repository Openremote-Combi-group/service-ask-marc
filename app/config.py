from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, MySQLDsn, MariaDBDsn, HttpUrl


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False
    )

    app_debug: bool = False

    database_url: PostgresDsn | MySQLDsn | MariaDBDsn
    database_prefix: str | None = 'ask_marc_'

    openremote_url: HttpUrl
    openremote_client_id: str
    openremote_client_secret: str
    openremote_verify_ssl: bool = True
    openremote_service_id: str = 'Ask-Marc'
    openremote_heartbeat_interval: int = 45


    openai_api_key: str | None = None

    base_url: str = '/'

    cors_allowed_domains: set[str] = set()


config = Config()
