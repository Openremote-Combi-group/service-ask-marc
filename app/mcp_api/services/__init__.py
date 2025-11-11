from fastmcp import FastMCP

from .asset import asset_mcp


def init_services(mcp_app: FastMCP):
    mcp_app.mount(asset_mcp)