import random

from fastmcp import FastMCP

from .services import init_services

mcp = FastMCP("OpenRemote Tools")


@mcp.tool
def ask_marc() -> str:
    """
    Ask marc any yes or no question and he shall answer!

    :return: str
    """
    return random.Random().choice(['Yes', 'No'])

init_services(mcp)