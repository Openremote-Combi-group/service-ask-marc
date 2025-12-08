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
Tests for Keycloak middleware and access control.
"""

import pytest
from middlewares.keycloak.models import UserContext, KeycloakTokenPayload


def test_user_context_realm_access():
    """Test that UserContext correctly determines realm accessibility."""
    # Create a token payload for a regular user in 'customer' realm
    payload = KeycloakTokenPayload(
        exp=9999999999,
        iss="http://localhost:8081/auth/realms/customer",
        azp="openremote",
        realm_access=KeycloakTokenPayload.RealmAccess(roles=["user"]),
        resource_access={"openremote": KeycloakTokenPayload.ResourceAccess(roles=["read:assets"])},
        preferred_username="testuser"
    )
    
    user_context = UserContext(payload)
    
    # User should have access to their own realm
    assert user_context.is_realm_accessible_by_user("customer") is True
    
    # User should NOT have access to other realms
    assert user_context.is_realm_accessible_by_user("master") is False
    assert user_context.is_realm_accessible_by_user("other") is False
    
    # User should not be a super user
    assert user_context.is_super_user() is False


def test_user_context_super_user():
    """Test that master realm admin is recognized as super user."""
    # Create a token payload for a master realm admin
    payload = KeycloakTokenPayload(
        exp=9999999999,
        iss="http://localhost:8081/auth/realms/master",
        azp="openremote",
        realm_access=KeycloakTokenPayload.RealmAccess(roles=["admin"]),
        resource_access={"openremote": KeycloakTokenPayload.ResourceAccess(roles=["read:assets", "write:assets"])},
        preferred_username="admin"
    )
    
    user_context = UserContext(payload)
    
    # Admin should be a super user
    assert user_context.is_super_user() is True
    
    # Super user should have access to all realms
    assert user_context.is_realm_accessible_by_user("master") is True
    assert user_context.is_realm_accessible_by_user("customer") is True
    assert user_context.is_realm_accessible_by_user("any_realm") is True


def test_user_context_resource_roles():
    """Test that resource roles are correctly checked."""
    payload = KeycloakTokenPayload(
        exp=9999999999,
        iss="http://localhost:8081/auth/realms/customer",
        azp="openremote",
        realm_access=KeycloakTokenPayload.RealmAccess(roles=["user"]),
        resource_access={
            "openremote": KeycloakTokenPayload.ResourceAccess(roles=["read:assets", "write:rules"])
        },
        preferred_username="testuser"
    )
    
    user_context = UserContext(payload)
    
    # Check individual roles
    assert user_context.has_resource_role("openremote", "read:assets") is True
    assert user_context.has_resource_role("openremote", "write:rules") is True
    assert user_context.has_resource_role("openremote", "delete:assets") is False
    
    # Check any of multiple roles
    assert user_context.has_any_resource_role("openremote", ["read:assets", "delete:assets"]) is True
    assert user_context.has_any_resource_role("openremote", ["delete:assets", "admin"]) is False
