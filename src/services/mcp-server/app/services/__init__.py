from fastmcp import FastMCP

from .asset import init_asset_service
from .asset_model import asset_model_mcp
from .realm import realm_mcp
#from .rule import rule_mcp


async def init_services(mcp_app: FastMCP):
    await init_asset_service(mcp_app)
    await mcp_app.import_server(asset_model_mcp, prefix="asset_model")
    await mcp_app.import_server(realm_mcp, prefix="realm")
    #await mcp_app.import_server(rule_mcp, prefix="rule")
