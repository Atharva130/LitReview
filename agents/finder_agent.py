import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from mcp_client import call_mcp_tool

async def find_papers(topic: str, max_results: int = 5) -> dict:
    """
    Calls the arxiv_search MCP server's search_papers tool.
    Falls back to the cached fixture if arXiv is unreachable/rate-limited.
    Returns {"papers": [...], "used_fallback": bool} so callers can be
    honest with the user about which data they're actually looking at.
    """
    try:
        result = await call_mcp_tool(
            "mcp_servers/arxiv_search/server.py",
            "search_papers",
            {"topic": topic, "max_results": max_results},
        )
        if result.isError:
            raise RuntimeError(result.content[0].text)
        papers = result.structuredContent["result"] if result.structuredContent else []
        return {"papers": papers, "used_fallback": False}
    except Exception as e:
        print(f"[finder_agent] Live search failed ({e}), using cached fixture.")
        with open("data/sample_papers.json") as f:
            papers = json.load(f)
        return {"papers": papers, "used_fallback": True}