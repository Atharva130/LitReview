# LitReview — Multi-Agent Literature Review Assistant

LitReview takes a research topic, finds relevant papers, extracts each paper's
claims into a structured schema, and synthesizes those claims into a literature
review — surfacing consensus, contradictions, and methodological trends across
papers, instead of just summarizing each paper individually.

## Why this exists

Reviewing a body of research means tracking which papers agree, which conflict,
and how the field has moved over time. Most "AI paper summarizer" tools stop at
describing each paper on its own — the real work is *comparing across* papers.
This project automates that comparison step, motivated by a real bottleneck
encountered while comparing methods across papers for a lunar terrain
segmentation project.

## Architecture

```
                    Orchestrator (LangGraph)
                    state: { topic, papers, extracted_claims, synthesis }
                                │
                                ▼
                    Paper Finder Agent
                    → MCP tool: search_papers(topic)
                                │
                          [papers list]
                                ▼
                    Extraction Agent
                    → MCP tool: fetch_paper(id)
                    → extracts structured schema per paper:
                        problem, method, dataset, metric,
                        result, limitation, section
                                │
                        [structured claims]
                                ▼
                    Synthesis Agent
                    → consensus, contradictions, trend timeline,
                      comparison table
                                │
                                ▼
                    Final structured Markdown report
```

Two standalone MCP servers expose the external-data tools (`search_papers`,
`fetch_paper`), called over the Model Context Protocol via a generic MCP
client rather than as in-process function calls — keeping agent reasoning
cleanly separated from external data access.

## Tech stack

| Layer | Tool |
|---|---|
| Orchestration | LangGraph |
| Tool protocol | MCP (2 servers: paper search, paper fetch) |
| Paper search | arXiv (`arxiv` Python library) |
| PDF fetch & parsing | Direct download from `arxiv.org/pdf/{id}`, text extraction via PyMuPDF |
| LLM | Groq (`openai/gpt-oss-20b`) |
| Backend/UI | Streamlit |
| Deployment | Docker → HuggingFace Spaces |

## Resilience by design

External research APIs (arXiv, Semantic Scholar) are frequently rate-limited
in practice. LitReview is built to degrade gracefully rather than fail:

- If live paper search fails, the system falls back to a small cached set of
  real papers so the rest of the pipeline can still run — and the final
  report **honestly flags** when this fallback was used, rather than silently
  presenting unrelated cached results as if they answered the query.
- If full-text fetch fails for a given paper, extraction falls back to that
  paper's abstract instead of failing the whole run.
- LLM calls retry with backoff on malformed output before failing.

## Project structure

```
LitReview/
├── mcp_servers/
│   ├── arxiv_search/server.py   # search_papers MCP tool
│   └── paper_fetch/server.py    # fetch_paper MCP tool
├── agents/
│   ├── finder_agent.py          # Paper Finder Agent
│   ├── extraction_agent.py      # Extraction Agent
│   ├── synthesis_agent.py       # Synthesis Agent
│   └── orchestrator.py          # LangGraph orchestrator
├── eval/
│   ├── queries.json             # Curated eval query set
│   └── run_eval.py              # Eval harness
├── data/
│   └── sample_papers.json       # Cached fallback fixture
├── mcp_client.py                 # Generic MCP client wiring
├── report_formatter.py           # Markdown report formatter
├── app.py                        # Streamlit UI
└── requirements.txt
```

## Setup

```bash
python -m venv litenv
litenv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Create a `.env` file:
```
GROQ_API_KEY=your-key-here
```

## Running

Streamlit UI:
```bash
streamlit run app.py
```

Evaluation:
```bash
python eval/run_eval.py
```

## Evaluation

A curated set of topic queries in a known domain (lunar terrain/crater
research), each with an expected consensus/contradiction relationship
verified by hand. The system's synthesis output is scored against that
expectation as a single pass/fail per query.

## Status

Core pipeline (Finder → Extraction → Synthesis → Report) working end-to-end
with Streamlit UI. Docker + HuggingFace Spaces deployment in progress.