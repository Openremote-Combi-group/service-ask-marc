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

"""
This module contains the dependency injectors for the MCP server.
"""

import logging

from shared.openremote_service import get_openremote_service
from .config import config

logger = logging.getLogger(__name__)


def get_openremote_issuers() -> list[str] | None:
    """Get valid issuers from OpenRemote realms.

    Returns:
        List of valid issuer URLs or None if realms cannot be retrieved.
    """
    try:
        openremote_service = get_openremote_service()
        
        # Use the OpenRemote client to get accessible realms
        # This is a synchronous call wrapped in async context
        import asyncio
        
        # Create async wrapper for the sync realm call
        async def get_realms():
            return await openremote_service.client.realm.get_all_realms()
        
        # Run in event loop if available, otherwise create new one
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're in an async context, but can't await here
                # Return a default issuer based on config
                return [f"{config.openremote_url}/auth/realms/{config.openremote_realm}"]
            else:
                realms = loop.run_until_complete(get_realms())
        except RuntimeError:
            # No event loop, return default
            return [f"{config.openremote_url}/auth/realms/{config.openremote_realm}"]

        if realms is None:
            return None

        urls = []
        for realm in realms:
            urls.append(f"{config.openremote_url}/auth/realms/{realm.name}")
        return urls
    except Exception as e:
        logger.error(f"Error getting issuers from OpenRemote: {e}", exc_info=True)
        # Return default issuer as fallback
        return [f"{config.openremote_url}/auth/realms/{config.openremote_realm}"]


# Constants
OPENREMOTE_KC_RESOURCE = "openremote"
OPENREMOTE_CLIENT_ID = "openremote"
