from fastmcp import FastMCP

asset_mcp = FastMCP("Asset Service")

@asset_mcp.tool
async def get_all_assets():
    """Lists all assets available."""
    return ["building_asset", "lamp_asset", "vehicle_asset"]



@asset_mcp.tool
async def get_asset_by_id(asset_id: str):
    """Get asset by id."""




def init_asset(mcp: FastMCP):
    mcp.mount(asset_mcp)