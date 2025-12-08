import logging

from fastmcp import FastMCP
from fastmcp.tools import Tool
from fastmcp.tools.tool_transform import ArgTransform
from httpx import HTTPStatusError
from openremote_client.schemas import AssetQuerySchema, RealmPredicateSchema, AssetObjectSchema
from pydantic import Field, BaseModel
from ...app.utils import asset_attribute_model_factory

from shared.openremote_service import get_openremote_service


logger = logging.getLogger("uvicorn")

asset_mcp = FastMCP("Asset Service")


class AssetQuerySchemaDescription(AssetQuerySchema):
    types: list[str] | None = Field(default=None, description="Asset types to query, (Make sure to use the 'get_all_asset_types' tool to gather which types there are)")
    realm: RealmPredicateSchema | None = Field(default=None, description="Realm to query (Make sure to use the 'get_all_realms' tool to now which realms to query)")

@asset_mcp.tool
async def query(asset_query_schema: AssetQuerySchemaDescription):
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
async def get_by_id(asset_id: str):
    """Retrieve a single asset by ID."""
    openremote_service = get_openremote_service()

    return await openremote_service.client.asset.get_asset(asset_id)


class AssetAttributeSchema(BaseModel):
    name: str = Field(description="Name of the attribute, must match the dictionary key.")
    type: str = Field(description="Type of the attribute.")


@asset_mcp.tool
async def create(name: str, attributes: dict, type: str | None = None, parentId: str | None = None, realm: str | None = None):
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

   """
    openremote_service = get_openremote_service()

    # class AssetObjectSchemaDescription(AssetObjectSchema):
    #
    # attributes_convert = {key: AssetAttributeSchema(name=key) for key, attribute in attributes.values() }

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


async def init_asset_service(mcp: FastMCP):
    openremote_service = get_openremote_service()

    logger.debug("Compiling asset tools...")

    # Fetch all asset types and create specialized tools for each one
    asset_models = await openremote_service.client.asset_model.get_asset_infos()

    for asset_model in asset_models.content:
        asset_model_name = asset_model.assetDescriptor['name']

        asset_mcp.add_tool(Tool.from_tool(
            create,
            name=f"create_{asset_model_name}",
            description=f"Create a new '{asset_model_name}' in the OpenRemote platform.",
            transform_args={
                'attributes': ArgTransform(
                    name='attributes',
                    description='Attributes of the asset to create.',
                    type=asset_attribute_model_factory(asset_model_name, asset_model.attributeDescriptors),
                    required=True,
                )
            }
        ))
    logger.info(f"Compiled {len(asset_models.content)} asset tools.")

    await mcp.import_server(asset_mcp, prefix="asset")

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
