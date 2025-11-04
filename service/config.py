from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, MySQLDsn, MariaDBDsn


class Config(BaseSettings):
    app_debug: bool = False

    database_url: PostgresDsn | MySQLDsn | MariaDBDsn
    database_prefix: str | None = 'ask_marc_'

    base_url: str = '/'

    cors_allowed_domains: set[str] = set()


config = Config()
