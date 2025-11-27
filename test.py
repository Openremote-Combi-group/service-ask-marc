import asyncio
import json

from fastmcp import Client


async def main():
    print("creating connection")

    client = Client("http://localhost:8420/mcp")
    async with client:
        # List available operations
        for tool in await client.list_tools():
            if tool.name == 'asset_create_LightAsset':
                print(json.dumps(tool.inputSchema, indent=4))

asyncio.run(main())