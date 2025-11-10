import random

from fastapi import FastAPI
from fastmcp import FastMCP

mcp = FastMCP("OpenRemote Tools")


@mcp.tool
def ask_marc() -> str:
    """
    Ask marc any yes or no question and he shall answer!

    :return: str
    """
    return random.Random().choice(['Yes', 'No'])



def init_mcp(app: FastAPI):
    mcp_app = mcp.http_app(
        path="/", transport="streamable-http", stateless_http=True
    )
    app.router.lifespan_context = mcp_app.router.lifespan_context
    app.mount("/mcp", mcp_app, name="mcp")
