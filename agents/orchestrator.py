import sys, os
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(THIS_DIR)
sys.path.append(PROJECT_ROOT)   # so `import mcp_client` (in root) works
sys.path.append(THIS_DIR)       # so `import finder_agent` etc. (siblings) work

import asyncio
import json
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END

from finder_agent import find_papers
from extraction_agent import extract_claims
from synthesis_agent import synthesize
from mcp_client import call_mcp_tool


class LitReviewState(TypedDict):
    topic: str
    papers: List[Dict[str, Any]]
    used_fallback: bool
    extracted_claims: List[Dict[str, Any]]
    synthesis: Dict[str, Any]


async def finder_node(state: LitReviewState) -> dict:
    result = await find_papers(state["topic"], max_results=5)
    return {"papers": result["papers"], "used_fallback": result["used_fallback"]}


async def get_paper_text(paper: dict) -> str:
    try:
        result = await call_mcp_tool(
            "mcp_servers/paper_fetch/server.py",
            "fetch_paper",
            {
                "paper_id": paper["id"],
                "title": paper.get("title", ""),
                "pdf_url": paper.get("pdf_url", "") or "",
            },
        )
        if result.isError:
            raise RuntimeError(result.content[0].text)
        if result.structuredContent:
            return result.structuredContent["result"]["text"]
        parsed = json.loads(result.content[0].text)
        return parsed["text"]
    except Exception as e:
        print(f"[orchestrator] fetch_paper failed for {paper['id']} ({e}), using abstract instead.")
        return paper.get("abstract", "")


async def extraction_node(state: LitReviewState) -> dict:
    claims = []
    for paper in state["papers"]:
        text = await get_paper_text(paper)
        claim = extract_claims(paper["id"], text)
        claims.append(claim)
    return {"extracted_claims": claims}


async def synthesis_node(state: LitReviewState) -> dict:
    synthesis = synthesize(state["extracted_claims"])
    return {"synthesis": synthesis}


def build_graph():
    graph = StateGraph(LitReviewState)
    graph.add_node("finder", finder_node)
    graph.add_node("extraction", extraction_node)
    graph.add_node("synthesis", synthesis_node)

    graph.set_entry_point("finder")
    graph.add_edge("finder", "extraction")
    graph.add_edge("extraction", "synthesis")
    graph.add_edge("synthesis", END)

    return graph.compile()


async def run_litreview(topic: str) -> dict:
    app = build_graph()
    return await app.ainvoke({"topic": topic})


if __name__ == "__main__":
    from report_formatter import format_report

    result = asyncio.run(run_litreview("lunar terrain segmentation"))
    report = format_report(result)

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sample_report.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print("Report written to sample_report.md")