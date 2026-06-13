import asyncio
import json
import os
from typing import Any, Dict

import streamlit as st

from app import SYSTEM_PROMPT, call_openai_chat, lookup_dictionary_entry, search_course_notes


def run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        new_loop = asyncio.new_event_loop()
        try:
            return new_loop.run_until_complete(coro)
        finally:
            new_loop.close()

    return asyncio.run(coro)


def run_study_sense(user_message: str):
    if not user_message.strip():
        raise ValueError("Please enter a study question or term.")

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set. Set it before running the app.")

    messages = [SYSTEM_PROMPT, {"role": "user", "content": user_message}]
    tool_trace = []

    for _ in range(3):
        response = run_async(call_openai_chat(messages))
        choice = response["choices"][0]
        message = choice["message"]
        function_call = message.get("function_call")

        if function_call:
            tool_name = function_call["name"]
            raw_args = function_call.get("arguments", "{}")
            try:
                args = json.loads(raw_args)
            except json.JSONDecodeError:
                args = {}

            if tool_name == "lookup_dictionary_entry":
                tool_result = run_async(
                    lookup_dictionary_entry(
                        word=args.get("word", ""),
                        language=args.get("language", "English"),
                    )
                )
            elif tool_name == "search_course_notes":
                tool_result = run_async(
                    search_course_notes(
                        query=args.get("query", ""),
                        max_results=int(args.get("max_results", 3)),
                    )
                )
            else:
                tool_result = {"error": f"Unknown tool: {tool_name}"}

            tool_trace.append({"tool": tool_name, "args": args, "result": tool_result})
            messages.append(
                {
                    "role": "assistant",
                    "content": None,
                    "function_call": {"name": tool_name, "arguments": json.dumps(args)},
                }
            )
            messages.append(
                {
                    "role": "tool",
                    "name": tool_name,
                    "content": json.dumps(tool_result),
                }
            )
            continue

        return message.get("content", ""), tool_trace, choice

    raise RuntimeError("Tool loop exceeded the maximum number of iterations.")


def display_tool_trace(tool_trace):
    if not tool_trace:
        return

    for index, item in enumerate(tool_trace, start=1):
        st.markdown(f"**Tool call {index}:** `{item['tool']}`")
        st.json(item)


def main():
    st.set_page_config(page_title="StudySense AI Companion", page_icon="📚")
    st.title("StudySense — Streamlit AI Study Companion")
    st.write(
        "Ask a study question about generative AI, coursework concepts, or definitions, and StudySense will decide whether to use a grounded tool to answer it."
    )
    st.markdown("---")

    st.sidebar.header("How to use")
    st.sidebar.write(
        "Enter a question or concept and click **Ask**. The app can call a definition tool or a course notes search tool when appropriate."
    )
    st.sidebar.write("Ensure `OPENAI_API_KEY` is set in your environment before running this app.")

    user_input = st.text_area("Your study question", height=160)
    submit = st.button("Ask StudySense")

    if submit:
        if not user_input.strip():
            st.warning("Please type a question or concept to proceed.")
            return

        with st.spinner("Asking the model and checking whether a tool is needed..."):
            try:
                answer, tool_trace, choice = run_study_sense(user_input)
                st.markdown("### Answer")
                st.write(answer)

                if tool_trace:
                    st.markdown("### Tool trace")
                    display_tool_trace(tool_trace)

                if choice.get("function_call"):
                    st.markdown("### Final decision")
                    st.json(choice["function_call"])
            except Exception as exc:
                st.error(str(exc))


if __name__ == "__main__":
    main()
