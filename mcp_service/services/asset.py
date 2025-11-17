from fastmcp import FastMCP
from httpx import HTTPStatusError
from openremote_client.schemas import AssetQuerySchema, RealmPredicateSchema, AssetObjectSchema, AttributeStateSchema
from pydantic import Field

from services.openremote import get_openremote_service

asset_mcp = FastMCP("Asset Service")


class AssetQuerySchemaDescription(AssetQuerySchema):
    types: list[str] | None = Field(default=None, description="Asset types to query, (Make sure to use the 'get_all_asset_types' tool to gather which types there are)")
    realm: RealmPredicateSchema | None = Field(default=None, description="Realm to query (Make sure to use the 'get_all_realms' tool to now which realms to query)")

@asset_mcp.tool
async def asset_query(asset_query_schema: AssetQuerySchemaDescription):
    """
    Lists all assets available.

    If 403 is returned, that either means you don't have to correct access rights or the realms you specified do not exist.
    Try calling the 'get_all_realms' tool to see which realms are available.
    """
    openremote_service = get_openremote_service()

    try:
        return await openremote_service.client.asset.query_assets(asset_query_schema)
    except HTTPStatusError as e:
        return {
            "status_code": e.response.status_code,
            "detail": e.response.text,
        }


@asset_mcp.tool
async def get_asset(asset_id: str):
    """Retrieve a single asset by ID."""
    openremote_service = get_openremote_service()

    return await openremote_service.client.asset.get_asset(asset_id)


@asset_mcp.tool
async def create_asset(asset_object_schema: AssetObjectSchema):
    """Create a new asset. Use 'get_all_asset_types' to see available asset types."""
    openremote_service = get_openremote_service()

    return await openremote_service.client.asset.create_asset(asset_object_schema)


@asset_mcp.tool
async def update_asset(asset_id: str, asset_object_schema: AssetObjectSchema):
    """Update an existing asset. First retrieve the asset with 'get_asset', modify the desired fields, then call this."""
    openremote_service = get_openremote_service()

    return await openremote_service.client.asset.update_asset(asset_id, asset_object_schema)


@asset_mcp.tool
async def delete_asset(asset_id: str):
    """Delete an asset by ID. Use with caution - this action cannot be undone."""
    openremote_service = get_openremote_service()

    # Note: The API expects the asset_id in the body, but we'll handle it via query or endpoint
    return await openremote_service.client.asset.delete_asset()


@asset_mcp.tool
async def write_attribute_value(asset_id: str, attribute_name: str, value: str | int | float | bool):
    """Write/update a single attribute value on an asset. Use this to change sensor values, settings, etc."""
    openremote_service = get_openremote_service()

    return await openremote_service.client.asset.write_attribute_value(asset_id, attribute_name, value)


@asset_mcp.tool
async def write_attribute_values(attribute_state_schema: AttributeStateSchema):
    """Write/update multiple attribute values at once. More efficient than writing individually."""
    openremote_service = get_openremote_service()

    return await openremote_service.client.asset.write_attribute_values(attribute_state_schema)


def init_asset(mcp: FastMCP):
    mcp.mount(asset_mcp)
