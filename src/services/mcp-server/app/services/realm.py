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
from ..context import require_realm_access, get_user_context

realm_mcp = FastMCP("Realm Service")


@realm_mcp.tool
async def get_all_realms():
    """Retrieve all realms accessible by the authenticated user.
    
    Super users (master realm admins) can see all realms.
    Regular users can only see their authenticated realm.
    """
    openremote_service = get_openremote_service()
    user_context = get_user_context()
    
    all_realms = await openremote_service.client.realm.get_all_realms()
    
    # If no user context (middleware disabled), return all realms
    if user_context is None:
        return all_realms
    
    # If super user, return all realms
    if user_context.is_super_user():
        return all_realms
    
    # Filter to only the user's authenticated realm
    authenticated_realm = user_context.get_authenticated_realm_name()
    filtered_realms = [r for r in all_realms if r.name == authenticated_realm]
    
    return filtered_realms


@realm_mcp.tool
async def get_realm(realm_name: str):
    """Retrieve details about a specific realm.
    
    Users can only access realms they have permission for:
    - Their authenticated realm
    - Master realm (if they are a super user)
    
    Args:
        realm_name: The name of the realm to retrieve.
        
    Raises:
        PermissionError: If the user does not have access to the specified realm.
    """
    # Check realm access
    require_realm_access(realm_name)
    
    openremote_service = get_openremote_service()
    return await openremote_service.client.realm.get_realm(realm_name)