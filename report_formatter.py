def format_report(state: dict) -> str:
    """
    Takes the final LangGraph state (topic, papers, extracted_claims, synthesis)
    and formats it into the 7-section Markdown report from the spec.
    """
    topic = state["topic"]
    papers = state["papers"]
    synthesis = state["synthesis"]

    md = f"# Literature Review: {topic}\n\n"

    md += "## 1. Research Landscape\n"
    md += synthesis.get("research_landscape", "N/A") + "\n\n"

    md += "## 2. Methodological Evolution\n"
    for point in synthesis.get("trend_timeline", []):
        md += f"- {point}\n"
    md += "\n"

    md += "## 3. Consensus\n"
    for point in synthesis.get("consensus", []):
        md += f"- {point}\n"
    md += "\n"

    md += "## 4. Contradictions\n"
    for c in synthesis.get("contradictions", []):
        papers_str = ", ".join(c.get("papers", []))
        md += f"- **{papers_str}**: {c.get('issue', '')} (Possible reason: {c.get('possible_reason', '')})\n"
    md += "\n"

    md += "## 5. Research Gaps\n"
    for gap in synthesis.get("research_gaps", []):
        md += f"- {gap}\n"
    md += "\n"

    md += "## 6. Comparison Table\n"
    md += "| Paper | Method | Dataset | Metric | Result |\n"
    md += "|---|---|---|---|---|\n"
    for row in synthesis.get("comparison_table", []):
        md += f"| {row.get('paper_id','')} | {row.get('method','')} | {row.get('dataset','')} | {row.get('metric','')} | {row.get('result','')} |\n"
    md += "\n"

    md += "## 7. References\n"
    for p in papers:
        link = p.get("pdf_url") or f"https://openalex.org/{p['id']}"
        md += f"- [{p['title']}]({link}) ({p.get('year', 'n.d.')})\n"

    return md