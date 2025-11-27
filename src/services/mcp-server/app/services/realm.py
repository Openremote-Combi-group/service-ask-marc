from fastmcp import FastMCP

from shared.openremote_service import get_openremote_service

realm_mcp = FastMCP("Realm Service")


@realm_mcp.tool
async def get_all():
    """Retrieve all realms."""
    openremote_service = get_openremote_service()

    return await openremote_service.client.realm.get_all_realms()


@realm_mcp.tool
async def get_by_name(realm_name: str):
    """Retrieve details about the currently authenticated and active realm."""
    openremote_service = get_openremote_service()

    return await openremote_service.client.realm.get_realm(realm_name)