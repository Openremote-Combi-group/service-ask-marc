"""MCP Client API test configuration."""
import sys
from pathlib import Path

# Add mcp-client-api to path FIRST to ensure we import from it
client_api_path = Path(__file__).parent.parent.parent / "src" / "services" / "mcp-client-api"
sys.path.insert(0, str(client_api_path))
