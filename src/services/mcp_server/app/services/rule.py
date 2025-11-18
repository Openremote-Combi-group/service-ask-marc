from fastmcp import FastMCP
from openremote_client.schemas import GlobalRulesetSchema, RealmRulesetSchema, AssetRulesetSchema

from shared.openremote_service import get_openremote_service

rule_mcp = FastMCP("Rule Service")


# Global Rulesets
@rule_mcp.tool
async def get_global_rulesets():
    """Retrieve all global rulesets. Global rules apply across all realms."""
    openremote_service = get_openremote_service()

    return await openremote_service.client.rule.get_global_rulesets()


@rule_mcp.tool
async def get_global_ruleset(rule_id: int):
    """Retrieve a specific global ruleset by ID."""
    openremote_service = get_openremote_service()

    return await openremote_service.client.rule.get_global_ruleset(rule_id)


@rule_mcp.tool
async def create_global_ruleset(global_ruleset_schema: GlobalRulesetSchema):
    """Create a new global ruleset. Returns the ID of the created ruleset."""
    openremote_service = get_openremote_service()

    return await openremote_service.client.rule.create_global_ruleset(global_ruleset_schema)


@rule_mcp.tool
async def update_global_ruleset(rule_id: int, global_ruleset_schema: GlobalRulesetSchema):
    """Update an existing global ruleset. First retrieve it with 'get_global_ruleset', modify, then call this."""
    openremote_service = get_openremote_service()

    return await openremote_service.client.rule.update_global_ruleset(rule_id, global_ruleset_schema)


@rule_mcp.tool
async def delete_global_ruleset(rule_id: int):
    """Delete a global ruleset by ID. Use with caution - this action cannot be undone."""
    openremote_service = get_openremote_service()

    return await openremote_service.client.rule.delete_global_ruleset(rule_id)


# Realm Rulesets
@rule_mcp.tool
async def get_realm_rulesets(realm_name: str):
    """Retrieve all rulesets for a specific realm. Use 'get_all_realms' to see available realms."""
    openremote_service = get_openremote_service()

    return await openremote_service.client.rule.get_realm_rulesets(realm_name)


@rule_mcp.tool
async def get_realm_ruleset(rule_id: int):
    """Retrieve a specific realm ruleset by ID."""
    openremote_service = get_openremote_service()

    return await openremote_service.client.rule.get_realm_ruleset(rule_id)


@rule_mcp.tool
async def create_realm_ruleset(realm_ruleset_schema: RealmRulesetSchema):
    """Create a new realm ruleset. Returns the ID of the created ruleset."""
    openremote_service = get_openremote_service()

    return await openremote_service.client.rule.create_realm_ruleset(realm_ruleset_schema)


@rule_mcp.tool
async def update_realm_ruleset(rule_id: int, realm_ruleset_schema: RealmRulesetSchema):
    """Update an existing realm ruleset. First retrieve it with 'get_realm_ruleset', modify, then call this."""
    openremote_service = get_openremote_service()

    return await openremote_service.client.rule.update_realm_ruleset(rule_id, realm_ruleset_schema)


@rule_mcp.tool
async def delete_realm_ruleset(rule_id: int):
    """Delete a realm ruleset by ID. Use with caution - this action cannot be undone."""
    openremote_service = get_openremote_service()

    return await openremote_service.client.rule.delete_realm_ruleset(rule_id)


# Asset Rulesets
@rule_mcp.tool
async def get_asset_rulesets(asset_id: str):
    """Retrieve all rulesets for a specific asset."""
    openremote_service = get_openremote_service()

    return await openremote_service.client.rule.get_asset_rulesets(asset_id)


@rule_mcp.tool
async def get_asset_ruleset(rule_id: int):
    """Retrieve a specific asset ruleset by ID."""
    openremote_service = get_openremote_service()

    return await openremote_service.client.rule.get_asset_ruleset(rule_id)


@rule_mcp.tool
async def create_asset_ruleset(asset_ruleset_schema: AssetRulesetSchema):
    """Create a new asset ruleset. Returns the ID of the created ruleset."""
    openremote_service = get_openremote_service()

    return await openremote_service.client.rule.create_asset_ruleset(asset_ruleset_schema)


@rule_mcp.tool
async def update_asset_ruleset(rule_id: int, asset_ruleset_schema: AssetRulesetSchema):
    """Update an existing asset ruleset. First retrieve it with 'get_asset_ruleset', modify, then call this."""
    openremote_service = get_openremote_service()

    return await openremote_service.client.rule.update_asset_ruleset(rule_id, asset_ruleset_schema)


@rule_mcp.tool
async def delete_asset_ruleset(rule_id: int):
    """Delete an asset ruleset by ID. Use with caution - this action cannot be undone."""
    openremote_service = get_openremote_service()

    return await openremote_service.client.rule.delete_asset_ruleset(rule_id)


# Rules Engine Info
@rule_mcp.tool
async def get_global_engine_info():
    """Get information about the global rules engine status and configuration."""
    openremote_service = get_openremote_service()

    return await openremote_service.client.rule.get_global_engine_info()


@rule_mcp.tool
async def get_realm_engine_info(realm_name: str):
    """Get information about a realm's rules engine status and configuration."""
    openremote_service = get_openremote_service()

    return await openremote_service.client.rule.get_realm_engine_info(realm_name)


@rule_mcp.tool
async def get_asset_engine_info(asset_id: str):
    """Get information about an asset's rules engine status and configuration."""
    openremote_service = get_openremote_service()

    return await openremote_service.client.rule.get_asset_engine_info(asset_id)


@rule_mcp.tool
async def get_asset_geofences(asset_id: str):
    """Get the geofences configured for an asset."""
    openremote_service = get_openremote_service()

    return await openremote_service.client.rule.get_asset_geofences(asset_id)


def init_rule(mcp: FastMCP):
    mcp.mount(rule_mcp)
