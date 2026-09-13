import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
import streamlit as st
from agents.orchestrator import run_litreview
from report_formatter import format_report

st.set_page_config(page_title="LitReview", layout="wide")
st.title("📚 LitReview — Multi-Agent Literature Review Assistant")

topic = st.text_input("Enter a research topic", placeholder="e.g. lunar terrain segmentation")

if st.button("Generate Review") and topic:
    with st.spinner("Finding papers, extracting claims, synthesizing review..."):
        result = asyncio.run(run_litreview(topic))
        report = format_report(result)

    st.markdown(report)
    st.download_button("Download report as Markdown", report, file_name="litreview_report.md")