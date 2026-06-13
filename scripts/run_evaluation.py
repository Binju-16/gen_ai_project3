import json
import os
from pathlib import Path

import openai

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = BASE_DIR / "evaluation.md"

openai.api_key = os.getenv("OPENAI_API_KEY", "")
if not openai.api_key:
    raise RuntimeError("OPENAI_API_KEY is required to run evaluation.")

TOOL_DEFINITIONS = [
    {
        "name": "lookup_dictionary_entry",
        "description": "Fetch a definition, example usage, and explanation for a study term or concept.",
        "parameters": {
            "type": "object",
            "properties": {
                "word": {
                    "type": "string",
                    "description": "The word or concept to look up.",
                },
                "language": {
                    "type": "string",
                    "description": "The language of the lookup. Use English for this application.",
                    "default": "English",
                },
            },
            "required": ["word"],
        },
    },
    {
        "name": "search_course_notes",
        "description": "Search local course notes and study guidance for generative AI topics and coursework concepts.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The course concept, topic, or study guidance to search for.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "The maximum number of matching notes to return.",
                    "default": 3,
                },
            },
            "required": ["query"],
        },
    },
]

PROMPT = [
    {
        "role": "system",
        "content": (
            "You are StudySense, an autonomous study assistant. You may use the available tools when the user needs a definition, concept explanation, or course-specific grounding. "
            "Return tool calls only when appropriate."
        ),
    }
]

TEST_CASES = [
    {
        "name": "Definition request",
        "input": "Explain agentic behavior in AI and when I should use a tool.",
    },
    {
        "name": "Course grounding request",
        "input": "What is grounding and why does it matter for this project?",
    },
    {
        "name": "Combined study question",
        "input": "Define mocking in testing and find course guidance on evaluation.",
    },
]


def run_test_case(case):
    messages = PROMPT + [{"role": "user", "content": case["input"]}]
    response = openai.ChatCompletion.create(
        model="gpt-4-0613",
        messages=messages,
        functions=TOOL_DEFINITIONS,
        function_call="auto",
        temperature=0.2,
    )
    return response


def main():
    results = []
    for case in TEST_CASES:
        response = run_test_case(case)
        choice = response["choices"][0]["message"]
        results.append({
            "name": case["name"],
            "input": case["input"],
            "message": choice,
            "response": response,
        })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as handle:
        handle.write("# Evaluation Results\n\n")
        for result in results:
            handle.write(f"## {result['name']}\n\n")
            handle.write(f"**Input:** {result['input']}\n\n")
            handle.write("**Model response:**\n\n```
")
            handle.write(json.dumps(result['message'], indent=2))
            handle.write("\n```
\n\n")
    print(f"Evaluation results written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
