import json
import os
import sys
from pathlib import Path
import asyncio
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import app
OUTPUT_FILE = BASE_DIR / "evaluation.md"

TEST_CASES = [
    {
        "name": "Define grounding",
        "input": "Define grounding for my course study and explain why it matters.",
        "expected_tool": "lookup_term",
    },
    {
        "name": "Define agentic behavior",
        "input": "What does agentic behavior mean in the context of an AI study assistant?",
        "expected_tool": "lookup_term",
    },
    {
        "name": "Summarize grounding note",
        "input": "Summarize the course note on grounding and explain how it improves study answers.",
        "expected_tool": "search_course_notes",
    },
    {
        "name": "Agentic behavior note",
        "input": "Use the course notes to explain why agentic behavior helps a study assistant.",
        "expected_tool": "search_course_notes",
    },
    {
        "name": "Prompt engineering definition",
        "input": "Give a precise definition of prompt engineering for my notes.",
        "expected_tool": "lookup_term",
    },
    {
        "name": "Exam study plan",
        "input": "I have an exam in three days on prompt engineering, grounding, and agentic behavior. Create a study plan with focused review sessions.",
        "expected_tool": "build_study_plan",
    },
    {
        "name": "Assignment review plan",
        "input": "I need a review schedule for a homework assignment covering prompt engineering and grounding in two days with 4 hours available.",
        "expected_tool": "build_study_plan",
    },
    {
        "name": "General grounding comparison",
        "input": "Compare grounding and prompt engineering using your course notes.",
        "expected_tool": "search_course_notes",
    },
]


def run_case(case):
    result = asyncio.run(app.process_user_message(case["input"]))
    return result.get("answer", ""), result.get("tool_trace", []), result


def summarize_case(case, result):
    actual_tool = result["tool_trace"][-1]["tool"] if result["tool_trace"] else "none"
    expected_tool = case.get("expected_tool", "none")
    grounded = "yes" if result["tool_trace"] else "no"
    passed = "yes" if expected_tool == actual_tool else "no"
    notes = []
    if expected_tool == "none" and actual_tool != "none":
        notes.append("Model used a tool when direct answer was expected.")
    if expected_tool != "none" and actual_tool == "none":
        notes.append("Model did not call the expected tool.")
    if expected_tool != "none" and actual_tool != expected_tool:
        notes.append(f"Model called {actual_tool} instead of {expected_tool}.")
    if grounded == "yes" and not result["tool_trace"]:
        notes.append("Tool trace is missing despite expected grounding.")
    return {
        "test": case["name"],
        "expected_tool": expected_tool,
        "actual_tool": actual_tool,
        "grounded": grounded,
        "passed": passed,
        "notes": " ".join(notes) if notes else "OK",
    }


def main():
    results = []
    summaries = []
    for case in TEST_CASES:
        ans, trace, raw_message = run_case(case)
        result = {"name": case["name"], "input": case["input"], "answer": ans, "tool_trace": trace, "raw_message": raw_message}
        results.append(result)
        summaries.append(summarize_case(case, result))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as handle:
        timestamp = datetime.now(timezone.utc).isoformat()
        handle.write("# Full Evaluation Results\n\n")
        handle.write(f"*Generated on: {timestamp}*\n\n")
        handle.write("*Last updated: this file is regenerated from the current app state and tool outputs.*\n\n")
        handle.write("## Evaluated questions\n\n")
        for case in TEST_CASES:
            handle.write(f"- {case['name']}: {case['input']}\n")
        handle.write("\n---\n\n")
        handle.write("## Evaluation summary\n\n")
        handle.write("| Test | Expected Tool | Actual Tool | Grounded? | Passed? | Notes |\n")
        handle.write("| --- | --- | --- | --- | --- | --- |\n")
        for summary in summaries:
            handle.write(
                f"| {summary['test']} | {summary['expected_tool']} | {summary['actual_tool']} | {summary['grounded']} | {summary['passed']} | {summary['notes']} |\n"
            )
        handle.write("\n---\n\n")

        for r in results:
            handle.write(f"## {r['name']}\n\n")
            handle.write(f"**Input:** {r['input']}\n\n")
            handle.write(f"**Expected tool:** {next(c['expected_tool'] for c in TEST_CASES if c['name'] == r['name'])}\n\n")
            actual_tool = r['tool_trace'][-1]['tool'] if r['tool_trace'] else 'none'
            handle.write(f"**Actual tool:** {actual_tool}\n\n")
            handle.write("**Tool trace:**\n\n")
            handle.write("```")
            handle.write("\n")
            raw_message = r["raw_message"]
            handle.write(json.dumps({"tool_trace": r["tool_trace"], "final_answer": r["answer"], "raw": raw_message}, indent=2))
            handle.write("\n```")
            handle.write("\n\n")

    print(f"Full evaluation written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
