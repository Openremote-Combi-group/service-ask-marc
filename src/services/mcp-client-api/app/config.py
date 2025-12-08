# Copyright 2025, OpenRemote Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

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
