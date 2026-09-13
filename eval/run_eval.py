import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import asyncio
from agents.orchestrator import run_litreview

def load_queries():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "queries.json")
    with open(path) as f:
        return json.load(f)

async def run_all():
    queries = load_queries()
    results = []

    for q in queries:
        print(f"Running: {q['topic']}")
        state = await run_litreview(q["topic"])
        synthesis = state.get("synthesis", {})

        has_consensus = len(synthesis.get("consensus", [])) > 0
        has_contradiction = len(synthesis.get("contradictions", [])) > 0

        if q["expected_relationship"] == "consensus":
            correct = has_consensus
        else:
            correct = has_contradiction

        results.append({
            "topic": q["topic"],
            "expected": q["expected_relationship"],
            "correct": correct,
        })

    total = len(results)
    correct_count = sum(1 for r in results if r["correct"])

    print("\n--- Eval Results ---")
    for r in results:
        status = "✓" if r["correct"] else "✗"
        print(f"{status} {r['topic']} (expected: {r['expected']})")

    print(f"\nScore: {correct_count}/{total} correctly identified known consensus/contradiction relationships.")

if __name__ == "__main__":
    asyncio.run(run_all())