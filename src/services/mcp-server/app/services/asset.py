from fastmcp import FastMCP
from httpx import HTTPStatusError
from openremote_client.schemas import AssetQuerySchema, RealmPredicateSchema, AssetObjectSchema
from pydantic import Field, BaseModel

from shared.openremote_service import get_openremote_service
from ..context import require_realm_access

asset_mcp = FastMCP("Asset Service")


class AssetQuerySchemaDescription(AssetQuerySchema):
    types: list[str] | None = Field(default=None, description="Asset types to query, (Make sure to use the 'get_all_asset_types' tool to gather which types there are)")
    realm: RealmPredicateSchema | None = Field(default=None, description="Realm to query (Make sure to use the 'get_all_realms' tool to now which realms to query)")

@asset_mcp.tool
async def asset_query(asset_query_schema: AssetQuerySchemaDescription):
    """
    Lists all assets available.

    If 403 is returned, that either means you don't have the correct access rights or the realms you specified do not exist.
    Try calling the 'get_all_realms' tool to see which realms are available.
    
    Access control: Users can only query assets in realms they have access to.
    """
    # Check realm access if realm is specified
    if asset_query_schema.realm and asset_query_schema.realm.name:
        try:
            require_realm_access(asset_query_schema.realm.name)
        except PermissionError as e:
            return {
                "error": "Permission denied",
                "detail": str(e),
                "status_code": 403,
            }
    
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


class AssetAttributeSchema(BaseModel):
    name: str = Field(description="Name of the attribute, must match the dictionary key.")
    type: str = Field(description="Type of the attribute.")

class AssetObjectSchemaDescription(BaseModel):
    name: str
    type: str | None = Field(
        default=None,
        description="Asset type definition. Use get_all_asset_types to see valid types."
    )
    parentId: str | None = Field(default=None, description="Optional parent asset ID")
    realm: str | None = Field(default=None, description="Optional realm")

    # IMPORTANT: dynamic key → attribute object
    asset_properties: dict[str, AssetAttributeSchema] = Field(
        description=(
            "REQUIRED. A dictionary where each key is an attribute name. "
            "Each value is an object describing that attribute (name + type). "
            "The key MUST match the AssetAttributeSchema.name."
        )
    )

@asset_mcp.tool
async def create_asset(name: str, attributes: dict[str, AssetAttributeSchema], type: str | None = None, parentId: str | None = None, realm: str | None = None):
    """
   Create a new asset in the OpenRemote platform.

   IMPORTANT RULES FOR THE AI (DO NOT IGNORE):

   1. The field "attributes" is REQUIRED.
      You MUST ALWAYS include it when calling this tool.

   2. "attributes" must be an object where:
         - Each key = attribute name
         - Each value = { "name": key, "type": "<attribute-type>" }
      Example:
        "attributes": {
            "temperature": {"name": "temperature", "type": "number"},
            "status": {"name": "status", "type": "string"}
        }

   3. If the user does not provide asset_properties:
        - First call get_all_asset_types
        - Find the selected type
        - Look at the required attributes
        - Fill in attributes automatically with logical placeholder types

   4. If OpenRemote returns 400:
        - It means the schema is wrong or missing required attribute fields.
        - You must ask the user for missing information or generate logical defaults.
        
   Access control: Users can only create assets in realms they have access to.
   """
    # Check realm access if realm is specified
    if realm:
        try:
            require_realm_access(realm)
        except PermissionError as e:
            return {
                "error": "Permission denied",
                "detail": str(e),
            }
    
    openremote_service = get_openremote_service()

    try:
        return await openremote_service.client.asset.create_asset(AssetObjectSchema(name=name, type=type, parentId=parentId, realm=realm, attributes=attributes))
    except HTTPStatusError as e:
        return {
            "status_code": e.response.status_code,
            "detail": e.response.text,
        }
    except Exception as e:
        return {
            "detail": str(e)
        }

#
# @asset_mcp.tool
# async def update_asset(asset_id: str, asset_object_schema: AssetObjectSchema):
#     """Update an existing asset. First retrieve the asset with 'get_asset', modify the desired fields, then call this."""
#     openremote_service = get_openremote_service()
#
#     return await openremote_service.client.asset.update_asset(asset_id, asset_object_schema)
#
#
# @asset_mcp.tool
# async def delete_asset(asset_id: str):
#     """Delete an asset by ID. Use with caution - this action cannot be undone."""
#     openremote_service = get_openremote_service()
#
#     # Note: The API expects the asset_id in the body, but we'll handle it via query or endpoint
#     return await openremote_service.client.asset.delete_asset()
#
#
# @asset_mcp.tool
# async def write_attribute_value(asset_id: str, attribute_name: str, value: str | int | float | bool):
#     """Write/update a single attribute value on an asset. Use this to change sensor values, settings, etc."""
#     openremote_service = get_openremote_service()
#
#     return await openremote_service.client.asset.write_attribute_value(asset_id, attribute_name, value)
#
#
# @asset_mcp.tool
# async def write_attribute_values(attribute_state_schema: AttributeStateSchema):
#     """Write/update multiple attribute values at once. More efficient than writing individually."""
#     openremote_service = get_openremote_service()
#
#     return await openremote_service.client.asset.write_attribute_values(attribute_state_schema)


def init_asset(mcp: FastMCP):
    mcp.mount(asset_mcp)
