import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def call_mcp_tool(server_script: str, tool_name: str, arguments: dict):
    """
    Launch an MCP server (given its script path) as a subprocess,
    call one of its tools, and return the result.
    """
    server_params = StdioServerParameters(
        command="python",
        args=[server_script],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            return result
        
if __name__ == "__main__":
    result = asyncio.run(
        call_mcp_tool(
            "mcp_servers/arxiv_search/server.py",
            "search_papers",
            {"topic": "lunar terrain segmentation", "max_results": 2},
        )
    )
    print(result)