# Access Control Implementation

## Overview

The MCP Server now includes Keycloak-based access control to ensure users can only access resources within their authorized realms. This prevents low-permission users from accessing sensitive data like the master realm when they shouldn't have access.

## How It Works

### 1. Keycloak Middleware

The `KeycloakMiddleware` validates JWT tokens from OpenRemote's Keycloak instance:

- Extracts Bearer token from Authorization header
- Validates token signature using Keycloak's JWKS endpoint
- Creates a `UserContext` with user's realm, roles, and permissions
- Stores context for access by MCP tools

### 2. User Context

The `UserContext` provides methods to check:

- **Authenticated Realm**: Which realm the user logged into
- **Super User Status**: Is the user a master realm admin?
- **Realm Access**: Can the user access a specific realm?
- **Resource Roles**: Does the user have specific permissions?

### 3. Realm Access Rules

```python
# Regular users can ONLY access their authenticated realm
user.is_realm_accessible_by_user("customer")  # True if user is in customer realm
user.is_realm_accessible_by_user("master")    # False for non-admin users

# Master realm admins can access ALL realms
admin.is_realm_accessible_by_user("any_realm")  # True for master admins
```

### 4. MCP Tool Protection

Tools that access realm-specific data check permissions:

```python
from app.context import require_realm_access

@asset_mcp.tool
async def get_realm(realm_name: str):
    # Raises PermissionError if user lacks access
    require_realm_access(realm_name)
    
    # Tool implementation...
```

## Protected Tools

The following MCP tools enforce realm access control:

- `get_realm(realm_name)` - Retrieve realm details
- `get_all_realms()` - Filters to user's accessible realms
- `asset_query(...)` - Validates realm in query
- `create_asset(...)` - Validates target realm

## Configuration

### Environment Variables

```bash
# Keycloak settings
OPENREMOTE_KEYCLOAK_URL=http://localhost:8081/auth
OPENREMOTE_REALM=master
KEYCLOAK_MIDDLEWARE_ENABLED=1  # Set to 0 to disable

# OpenRemote connection
OPENREMOTE_URL=http://localhost:8080
OPENREMOTE_CLIENT_ID=serviceuser
OPENREMOTE_CLIENT_SECRET=<secret>
```

### Excluded Routes

These routes bypass authentication:
- `/api/health` - Health check endpoint
- `/health` - Alternative health endpoint
- `/docs` - API documentation
- `/redoc` - Alternative docs
- `/openapi.json` - OpenAPI spec

## Service User vs. AI User

**Important**: The MCP server uses a **service user** to connect to OpenRemote. This service user needs full permissions to perform operations on behalf of users.

The **AI user's token** is validated by the middleware. The AI can only request actions for realms the AI user has access to, even though the service user could technically access more.

This two-tier system ensures:
1. Service operations work without restriction
2. User-initiated AI requests are properly scoped

## Disabling Access Control

For development or testing, disable the middleware:

```bash
KEYCLOAK_MIDDLEWARE_ENABLED=0
```

When disabled, all tools work without authentication.

## Error Messages

When access is denied:

```json
{
  "error": "Permission denied",
  "detail": "User 'alice' does not have access to realm 'master'. You can only access your authenticated realm or the master realm as an admin."
}
```

## Testing

Run access control tests:

```bash
pytest tests/mcp-server/test_access_control.py
```

## Architecture

```
┌─────────────────┐
│  AI Client      │
│  (with token)   │
└────────┬────────┘
         │ HTTP Request + Bearer Token
         ▼
┌─────────────────────────────┐
│  KeycloakMiddleware         │
│  - Validates JWT            │
│  - Creates UserContext      │
│  - Sets context variable    │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  MCP Tools                  │
│  - Check require_realm_     │
│    access(realm)            │
│  - Return filtered results  │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  OpenRemote API             │
│  (via service user)         │
└─────────────────────────────┘
```

## Implementation Details

Key files:
- `middlewares/keycloak/middleware.py` - JWT validation
- `middlewares/keycloak/models.py` - UserContext
- `app/context.py` - Context variable management
- `app/dependencies.py` - Issuer provider
- `app/config.py` - Configuration settings
