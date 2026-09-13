import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agents.orchestrator import run_litreview
from report_formatter import format_report

app = FastAPI(title="LitReview API")


class ReviewRequest(BaseModel):
    topic: str


class ReviewResponse(BaseModel):
    report_markdown: str
    used_fallback: bool


@app.post("/api/generate-review", response_model=ReviewResponse)
async def generate_review(req: ReviewRequest):
    result = await run_litreview(req.topic)
    report = format_report(result)
    return ReviewResponse(
        report_markdown=report,
        used_fallback=result.get("used_fallback", False),
    )


app.mount("/", StaticFiles(directory="static", html=True), name="static")