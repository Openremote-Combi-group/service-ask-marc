from fastmcp import FastMCP

from .asset import asset_mcp
from .asset_model import asset_model_mcp
from .realm import realm_mcp
from .rule import rule_mcp


def init_services(mcp_app: FastMCP):
    mcp_app.mount(asset_mcp)
    mcp_app.mount(asset_model_mcp)
    mcp_app.mount(realm_mcp)
    mcp_app.mount(rule_mcp)
