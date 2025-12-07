"""MCP Server test configuration."""
import sys
from pathlib import Path

# Add mcp-server to path FIRST to ensure we import from it
server_path = Path(__file__).parent.parent.parent / "src" / "services" / "mcp-server"
sys.path.insert(0, str(server_path))
