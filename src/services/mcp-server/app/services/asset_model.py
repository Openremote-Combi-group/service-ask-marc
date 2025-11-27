from fastmcp import FastMCP

from shared.openremote_service import get_openremote_service

asset_model_mcp = FastMCP("Asset Model Service")


@asset_model_mcp.tool
async def get_all_types():
    """Retrieve the asset type information of each available asset type"""
    openremote_service = get_openremote_service()

    return await openremote_service.client.asset_model.get_asset_infos()


@asset_model_mcp.tool
async def get_type(asset_type: str):
    """Retrieve the asset type information of an asset type"""
    openremote_service = get_openremote_service()

    return await openremote_service.client.asset_model.get_asset_info(asset_type)