"""
MCP Client Example: Invoking LocalCompute Tools via Python MCP SDK
"""
import asyncio
from services.mcp_server.server import call_tool, list_tools

async def main():
    print("1. Discovering available MCP Tools...")
    tools = await list_tools()
    print(f"✓ Discovered {len(tools)} official MCP tools:")
    for t in tools:
        print(f"  - {t.name}: {t.description}")

    print("\n2. Executing 'generate_capacity_report' tool...")
    res = await call_tool("generate_capacity_report", {"include_offline": False})
    print("✓ Tool Output:\n", res[0].text)

    print("\n3. Executing 'list_available_nodes' tool...")
    res_nodes = await call_tool("list_available_nodes", {"status_filter": "online"})
    print("✓ Tool Output:\n", res_nodes[0].text[:300] + "...")

if __name__ == "__main__":
    asyncio.run(main())
