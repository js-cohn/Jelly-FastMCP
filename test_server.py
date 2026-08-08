import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from jelly_mcp.server import mcp


async def test_mcp_initialization():
    """Verify that FastMCP is initialized and the core Jelly tools are registered."""
    print("Verifying FastMCP server registration...")

    assert mcp.name == "Jelly", f"Expected server name 'Jelly', got '{mcp.name}'"

    tools = await mcp.list_tools()
    tool_names = [tool.name for tool in tools]
    print(f"Registered tools: {tool_names}")

    expected_tools = [
        "list_conversations",
        "search_conversations",
        "get_conversation",
        "list_conversation_messages",
        "list_labels",
        "create_label",
        "archive_conversation",
        "assign_conversation",
        "create_draft_reply",
        "upsert_contact",
    ]

    for tool in expected_tools:
        assert tool in tool_names, f"Expected tool '{tool}' to be registered"

    resources = await mcp.list_resources()
    resource_uris = [res.uri for res in resources]
    print("Registered resources:")
    print(resource_uris)

    templates = await mcp.list_resource_templates()
    template_uris = [template.uri_template for template in templates]
    print("Registered resource templates:")
    print(template_uris)

    assert any(
        "jelly://conversations/{conversation_id}/markdown" == uri for uri in template_uris
    ), "Expected the Jelly markdown resource template to be registered"

    print("All registration checks passed successfully!")


if __name__ == "__main__":
    asyncio.run(test_mcp_initialization())
