import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.mcp_client_manager import mcp_manager


from unittest.mock import patch

@patch("services.mcp_client_manager.mcp_manager.list_tools")
async def test_mcp_connection(mock_list_tools):
    print("--- Testing MCP Client Connection ---")
    mock_list_tools.return_value = [{"name": "test_tool"}]
    
    tools = await mcp_manager.list_tools(
        server_name="context7",
        container_name="openclaw-mcp-context7",
        command="node",
        args=["build/index.js"]
    )
    
    assert len(tools) == 1
    assert tools[0]["name"] == "test_tool"
    mock_list_tools.assert_called_once()
    
    print("\n✔ All tests passed.")

if __name__ == "__main__":
    asyncio.run(test_mcp_connection())
