from fastmcp import FastMCP

from mcp_service.services.asset import asset_mcp
from mcp_service.services.asset_model import asset_model_mcp
from mcp_service.services.realm import realm_mcp
from mcp_service.services.rule import rule_mcp


def init_services(mcp_app: FastMCP):
    mcp_app.mount(asset_mcp)
    mcp_app.mount(asset_model_mcp)
    mcp_app.mount(realm_mcp)
    mcp_app.mount(rule_mcp)
