from mcp.server.fastmcp import FastMCP
import requests
import pymupdf as fitz

mcp = FastMCP("paper-fetch")

@mcp.tool()
def fetch_paper(paper_id: str, title: str = "", pdf_url: str = "") -> dict:
    """
    Download a paper's PDF directly from its open-access URL (provided by
    search_papers) and extract raw text. No arXiv/OpenAlex API call needed
    here at all — just a plain file download.
    """
    if not pdf_url:
        raise ValueError("No open-access PDF URL available for this paper.")

    response = requests.get(
    pdf_url,
    timeout=30,
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
    )
    response.raise_for_status()

    doc = fitz.open(stream=response.content, filetype="pdf")
    full_text = ""
    for page in doc:
        full_text += page.get_text("text") #type:ignore
    doc.close()

    return {
        "paper_id": paper_id,
        "title": title,
        "text": full_text,
    }

if __name__ == "__main__":
    mcp.run()