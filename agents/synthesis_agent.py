import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYNTHESIS_PROMPT = """You are synthesizing a literature review from structured claims extracted
from multiple papers. Each claim follows this schema: paper_id, problem, method, dataset,
metric, result, limitation, section.

Given the list of claims below, output ONLY a JSON object with these fields:

{{
  "research_landscape": "...",
  "consensus": ["..."],
  "contradictions": [
    {{"papers": ["id1", "id2"], "issue": "...", "possible_reason": "..."}}
  ],
  "trend_timeline": ["..."],
  "research_gaps": ["..."],
  "comparison_table": [
    {{"paper_id": "...", "method": "...", "dataset": "...", "metric": "...", "result": "..."}}
  ]
}}

Rules:
- "research_landscape": 2-3 sentence framing of what this set of papers collectively addresses.
- "consensus": points where multiple papers agree on method or result.
- "contradictions": conflicting results, methods, or claims between papers, with a stated
  possible reason (e.g. different dataset/protocol/metric). Include meaningful differences
  in reported performance (e.g. one paper reporting notably higher/lower accuracy than another
  on a similar task), not just direct logical opposites.
- "trend_timeline": how methods evolved, ordered chronologically if year data allows.
- "research_gaps": open questions or under-explored areas visible from these claims.
- "comparison_table": one row per paper.
- Output ONLY the JSON object, no preamble, no markdown fences.

Claims:
{claims}
"""

def synthesize(claims: list[dict], max_attempts: int = 3) -> dict:
    prompt = SYNTHESIS_PROMPT.format(claims=json.dumps(claims, indent=2))

    last_error = None
    for attempt in range(max_attempts):
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000,
                temperature=0,
                response_format={"type": "json_object"},
            )
            raw = response.choices[0].message.content.strip() #type:ignore
            raw = raw.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(raw)
            print(f"[DEBUG] finish_reason={response.choices[0].finish_reason}, "
                  f"consensus={len(parsed.get('consensus', []))}, "
                  f"contradictions={len(parsed.get('contradictions', []))}, "
                  f"gaps={len(parsed.get('research_gaps', []))}, "
                  f"table_rows={len(parsed.get('comparison_table', []))}")
            return parsed
        except Exception as e:
            last_error = e
            print(f"[synthesis_agent] Attempt {attempt + 1} failed ({e}), retrying...")

    raise RuntimeError(f"Synthesis failed after {max_attempts} attempts: {last_error}")