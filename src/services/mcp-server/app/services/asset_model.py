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

from shared.openremote_service import get_openremote_service

asset_model_mcp = FastMCP("Asset Model Service")


@asset_model_mcp.tool
async def get_all_asset_types():
    """Retrieve the asset type information of each available asset type"""
    openremote_service = get_openremote_service()

    return await openremote_service.client.asset_model.get_asset_infos()


@asset_model_mcp.tool
async def get_asset_type(asset_type: str):
    """Retrieve the asset type information of an asset type"""
    openremote_service = get_openremote_service()

    return await openremote_service.client.asset_model.get_asset_info(asset_type)