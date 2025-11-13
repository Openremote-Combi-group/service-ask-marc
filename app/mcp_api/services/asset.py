from fastmcp import FastMCP
from openremote_client.schemas import AssetQuerySchema, RealmPredicateSchema
from pydantic import Field

from app.openremote_service import get_openremote_service

asset_mcp = FastMCP("Asset Service")


class AssetQuerySchemaDescription(AssetQuerySchema):
    types: list[str] | None = Field(default=None, description="Asset types to query, (Make sure to use the 'get_all_asset_types' tool to gather which types there are)")
    realm: RealmPredicateSchema | None = Field(default=None, description="Realm to query (Use the 'get_all_realms' tool to now which realms to query)")

@asset_mcp.tool
async def asset_query(asset_query_schema: AssetQuerySchemaDescription):
    """Lists all assets available."""
    openremote_service = get_openremote_service()

    return await openremote_service.client.asset.query_assets(asset_query_schema)


@asset_mcp.tool
async def get_asset(asset_id: str):
    """Retrieve an asset."""
    openremote_service = get_openremote_service()

    return await openremote_service.client.asset.get_asset(asset_id)


def init_asset(mcp: FastMCP):
    mcp.mount(asset_mcp)