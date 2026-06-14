import json
import os
import sys
from pathlib import Path
import asyncio

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import app
import openai
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
    messages = [app.SYSTEM_PROMPT, {"role": "user", "content": case["input"]}]
    tool_trace = []

    for _ in range(5):
        response = asyncio.run(app.call_openai_chat(messages))
        choice = response.choices[0]
        message = choice.message

        function_call = message.function_call
        if function_call:
            tool_name = function_call.name
            raw_args = function_call.arguments or "{}"
            try:
                args = json.loads(raw_args)
            except json.JSONDecodeError:
                args = {}

            if tool_name == "lookup_dictionary_entry":
                tool_result = asyncio.run(
                    app.lookup_dictionary_entry(word=args.get("word", ""), language=args.get("language", "English"))
                )
            elif tool_name == "search_course_notes":
                tool_result = asyncio.run(
                    app.search_course_notes(query=args.get("query", ""), max_results=int(args.get("max_results", 3)))
                )
            else:
                tool_result = {"error": f"Unknown tool: {tool_name}"}

            tool_trace.append({"tool": tool_name, "args": args, "result": tool_result})
            messages.append({"role": "assistant", "content": None, "function_call": {"name": tool_name, "arguments": json.dumps(args)}})
            # Insert the tool result as an assistant content message so we avoid
            # role='tool' compatibility issues with the OpenAI client.
            messages.append({"role": "assistant", "content": json.dumps({"tool": tool_name, "result": tool_result})})

            # Call the model again WITHOUT the `functions` parameter so the API
            # accepts the `tool` role messages and returns a final grounded answer.
            second_resp = openai.chat.completions.create(
                model="gpt-4-0613",
                messages=messages,
                temperature=0.2,
            )
            second_choice = second_resp.choices[0].message
            assistant_content = second_choice.content or ""
            return assistant_content, tool_trace, second_choice

        assistant_content = message.content or ""
        return assistant_content, tool_trace, message

    raise RuntimeError("Tool loop exceeded the maximum number of iterations.")


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
            if hasattr(raw_message, "to_dict"):
                raw_message = raw_message.to_dict()
            handle.write(json.dumps({"tool_trace": r["tool_trace"], "final_answer": r["answer"], "raw": raw_message}, indent=2))
            handle.write("\n```")
            handle.write("\n\n")

    print(f"Full evaluation written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
