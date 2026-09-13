import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

CACHE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "claims_cache.json")

def _load_cache() -> dict:
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH) as f:
            return json.load(f)
    return {}

def _save_cache(cache: dict):
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2)

EXTRACTION_SCHEMA_PROMPT = """You are extracting structured information from a research paper.
Given the paper's text below, output ONLY a JSON object with exactly these fields:

{{
  "paper_id": "...",
  "problem": "...",
  "method": "...",
  "dataset": "...",
  "metric": "...",
  "result": "...",
  "limitation": "...",
  "section": "..."
}}

Rules:
- "section" should be a coarse label like "Abstract", "Methods", or "Experiments" — wherever this information was primarily drawn from.
- Be concise: 1-2 sentences per field.
- Output ONLY the JSON object, no preamble, no markdown fences.

Paper ID: {paper_id}
Paper text:
{text}
"""

def extract_claims(paper_id: str, text: str, max_attempts: int = 3) -> dict:
    cache = _load_cache()
    if paper_id in cache:
        return cache[paper_id]

    prompt = EXTRACTION_SCHEMA_PROMPT.format(paper_id=paper_id, text=text[:8000])

    last_error = None
    for attempt in range(max_attempts):
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0,
                response_format={"type": "json_object"},
            )
            raw = response.choices[0].message.content.strip() #type:ignore
            raw = raw.replace("```json", "").replace("```", "").strip()
            claim = json.loads(raw)
            cache[paper_id] = claim
            _save_cache(cache)
            return claim
        except Exception as e:
            last_error = e
            print(f"[extraction_agent] Attempt {attempt + 1} failed ({e}), retrying...")

    raise RuntimeError(f"Extraction failed for {paper_id} after {max_attempts} attempts: {last_error}")