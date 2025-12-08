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

from langchain_mcp_adapters.client import MultiServerMCPClient

__mcp_service: MultiServerMCPClient | None = None


def get_mcp_client_service() -> MultiServerMCPClient:
    global __mcp_service

    if __mcp_service is None:
        raise RuntimeError("MCP service not initialized")

    return __mcp_service


async def init_mcp_client_service(mcp_config: dict):
    global __mcp_service

    __mcp_service = MultiServerMCPClient(mcp_config)
