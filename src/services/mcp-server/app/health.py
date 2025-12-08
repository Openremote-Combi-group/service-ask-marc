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

from fastmcp import FastMCP
from httpx import HTTPStatusError
from starlette.responses import JSONResponse

from shared.openremote_service import get_openremote_service
from .config import config

mcp_health = FastMCP("Health Check")


@mcp_health.custom_route("/api/health", methods=['GET'])
async def health(request):
    openremote_service = get_openremote_service()

    try:
        await openremote_service.client.status.get_health_status()
    except HTTPStatusError:
        return JSONResponse({"status": "unhealthy", "service": config.openremote_service_id, "error": "Failed to connect to OpenRemote"}, status_code=200)

    return JSONResponse({"status": "healthy", "service": config.openremote_service_id}, status_code=200)


def init_health(mcp: FastMCP):
    mcp.mount(mcp_health)