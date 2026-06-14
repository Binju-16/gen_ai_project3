import json
import os
from pathlib import Path

from dotenv import load_dotenv
import openai

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = BASE_DIR / "evaluation.md"

openai.api_key = os.getenv("OPENAI_API_KEY", "")
if not openai.api_key:
    raise RuntimeError("OPENAI_API_KEY is required to run evaluation.")

TOOL_DEFINITIONS = [
    {
        "name": "lookup_term",
        "description": "Fetch a definition, example usage, and explanation for a study term or concept.",
        "parameters": {
            "type": "object",
            "properties": {
                "term": {
                    "type": "string",
                    "description": "The term or concept to look up.",
                },
                "language": {
                    "type": "string",
                    "description": "The language of the lookup. Use English for this application.",
                    "default": "English",
                },
            },
            "required": ["term"],
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
    {
        "name": "build_study_plan",
        "description": "Create a study plan for the user based on topics, deadlines, and available time.",
        "parameters": {
            "type": "object",
            "properties": {
                "topics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Topics or concepts the student should study.",
                },
                "deadline": {
                    "type": "string",
                    "description": "The exam date or deadline for the study plan.",
                },
                "available_hours": {
                    "type": "integer",
                    "description": "Estimated study hours available per day.",
                    "default": 2,
                },
            },
            "required": ["topics", "deadline"],
        },
    },
]

PROMPT = [
    {
        "role": "system",
        "content": (
            "You are MentorMate, an AI study companion. Use tools only when they help you answer the student's question accurately with supporting definitions or course notes. "
            "If you use a tool, refer to the information it returns in your final answer."
        ),
    }
]

TEST_CASES = [
    {
        "name": "Concept comparison",
        "input": "What is the difference between prompt engineering and fine-tuning in generative AI?",
    },
    {
        "name": "Course concept explanation",
        "input": "Summarize how grounding helps make AI answers more reliable.",
    },
    {
        "name": "Exam preparation",
        "input": "How should I prepare for a generative AI exam using lecture notes and definitions?",
    },
]


def run_test_case(case):
    messages = PROMPT + [{"role": "user", "content": case["input"]}]
    response = openai.chat.completions.create(
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
        choice = response.choices[0].message
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
            handle.write("**Model response:**\n\n```")
            handle.write("\n")
            handle.write(json.dumps(result['message'].to_dict(), indent=2))
            handle.write("\n```")
            handle.write("\n\n")
    print(f"Evaluation results written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
