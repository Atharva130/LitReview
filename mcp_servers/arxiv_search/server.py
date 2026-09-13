from mcp.server.fastmcp import FastMCP
import requests
import os
from dotenv import load_dotenv

load_dotenv()
mcp = FastMCP("paper-search")

API_KEY = os.getenv("OPENALEX_API_KEY")


def _reconstruct_abstract(inverted_index: dict) -> str:
    """OpenAlex stores abstracts as an inverted index (word -> positions)
    for copyright reasons; rebuild the plain text from it."""
    if not inverted_index:
        return ""
    max_pos = max(pos for positions in inverted_index.values() for pos in positions)
    words = [""] * (max_pos + 1)
    for word, positions in inverted_index.items():
        for pos in positions:
            words[pos] = word
    return " ".join(words)


@mcp.tool()
def search_papers(topic: str, max_results: int = 5) -> list[dict]:
    """
    Search OpenAlex for papers relevant to a topic. Returns id, title,
    abstract, year, authors, and a pdf_url when the paper is open access
    (used later for full-text fetch, no arXiv dependency needed).
    """
    url = "https://api.openalex.org/works"
    params = {
        "search": topic,
        "per_page": max_results,
        "filter": "has_abstract:true",
    }
    if API_KEY:
        params["api_key"] = API_KEY

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    results = []
    for work in data.get("results", []):
        best_oa = work.get("best_oa_location") or {}
        results.append({
            "id": work.get("id", "").replace("https://openalex.org/", ""),
            "title": work.get("title", ""),
            "abstract": _reconstruct_abstract(work.get("abstract_inverted_index")),
            "year": work.get("publication_year"),
            "authors": [a["author"]["display_name"] for a in work.get("authorships", [])],
            "pdf_url": best_oa.get("pdf_url"),
        })
    return results

if __name__ == "__main__":
    mcp.run()