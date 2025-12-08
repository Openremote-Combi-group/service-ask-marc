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
Context utilities for accessing user information in MCP tools.
"""

from contextvars import ContextVar
from typing import Optional

from middlewares.keycloak.models import UserContext

# Context variable to store the current user context
_user_context: ContextVar[Optional[UserContext]] = ContextVar('user_context', default=None)


def get_user_context() -> Optional[UserContext]:
    """Get the current user context from the context variable.
    
    Returns:
        UserContext if available, None otherwise.
    """
    return _user_context.get()


def set_user_context(user: Optional[UserContext]) -> None:
    """Set the user context in the context variable.
    
    Args:
        user: The UserContext to set.
    """
    _user_context.set(user)


def check_realm_access(realm: str) -> bool:
    """Check if the current user has access to the specified realm.
    
    Args:
        realm: The realm name to check access for.
        
    Returns:
        True if user has access or if middleware is disabled, False otherwise.
    """
    user_context = get_user_context()
    
    # If no user context (middleware disabled), allow access
    if user_context is None:
        return True
    
    # Check realm access
    return user_context.is_realm_accessible_by_user(realm)


def require_realm_access(realm: str) -> None:
    """Require that the current user has access to the specified realm.
    
    Args:
        realm: The realm name to check access for.
        
    Raises:
        PermissionError: If the user does not have access to the realm.
    """
    if not check_realm_access(realm):
        user_context = get_user_context()
        username = user_context.get_username() if user_context else "unknown"
        raise PermissionError(
            f"User '{username}' does not have access to realm '{realm}'. "
            f"You can only access your authenticated realm or the master realm as an admin."
        )
