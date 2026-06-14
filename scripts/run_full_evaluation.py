import json
import os
import sys
from pathlib import Path
import asyncio

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import app
OUTPUT_FILE = BASE_DIR / "evaluation.md"

TEST_CASES = [
    {
        "name": "Definition comparison",
        "input": "What is the difference between prompt engineering and fine-tuning in generative AI?",
    },
    {
        "name": "Grounded study explanation",
        "input": "Explain how grounding improves the reliability of AI study answers.",
    },
    {
        "name": "Study preparation guidance",
        "input": "How should I prepare for a generative AI exam using lecture notes and definitions?",
    },
]


def run_case(case):
    result = asyncio.run(app.process_user_message(case["input"]))
    return result.get("answer", ""), result.get("tool_trace", []), result


def main():
    results = []
    for case in TEST_CASES:
        ans, trace, raw_message = run_case(case)
        results.append({"name": case["name"], "input": case["input"], "answer": ans, "tool_trace": trace, "raw_message": raw_message})

    with open(OUTPUT_FILE, "w", encoding="utf-8") as handle:
        handle.write("# Full Evaluation Results\n\n")
        for r in results:
            handle.write(f"## {r['name']}\n\n")
            handle.write(f"**Input:** {r['input']}\n\n")
            handle.write("**Tool trace and final answer:**\n\n")
            handle.write("```")
            handle.write("\n")
            raw_message = r["raw_message"]
            handle.write(json.dumps({"tool_trace": r["tool_trace"], "final_answer": r["answer"], "raw": raw_message}, indent=2))
            handle.write("\n```")
            handle.write("\n\n")

    print(f"Full evaluation written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
