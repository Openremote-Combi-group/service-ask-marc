from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, MySQLDsn, MariaDBDsn, HttpUrl


class Config(BaseSettings):
    app_debug: bool = False

    database_url: PostgresDsn | MySQLDsn | MariaDBDsn
    database_prefix: str | None = 'ask_marc_'

    openremote_url: HttpUrl = HttpUrl('http://localhost:8080')
    openremote_client_id: str
    openremote_client_secret: str
    openremote_verify_ssl: bool = True
    openremote_service_id: str = 'Ask-Marc'
    openremote_heartbeat_interval: int = 50

    base_url: str = '/'

    cors_allowed_domains: set[str] = set()


config = Config()
