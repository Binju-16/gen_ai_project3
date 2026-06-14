import asyncio
import json
import os
from typing import Any, Dict

from dotenv import load_dotenv
import streamlit as st

from app import SYSTEM_PROMPT, call_openai_chat, lookup_dictionary_entry, search_course_notes

# Load environment variables from .env file
load_dotenv()


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
            # Append tool result as assistant content to avoid role='tool' compatibility issues
            messages.append(
                {
                    "role": "assistant",
                    "content": json.dumps({"tool": tool_name, "result": tool_result}),
                }
            )
            
            # Call the model WITHOUT the `functions` parameter to get final grounded answer
            import openai
            second_resp = openai.chat.completions.create(
                model="gpt-4-0613",
                messages=messages,
                temperature=0.2,
            )
            second_choice = second_resp.choices[0].message
            final_answer = second_choice.content or ""
            return final_answer, tool_trace, second_choice

        return message.content or "", tool_trace, choice

    raise RuntimeError("Tool loop exceeded the maximum number of iterations.")


# Predefined test prompts useful for quick local evaluation and debugging
SAMPLE_PROMPTS = [
    ("Definition lookup", "What is the difference between prompt engineering and fine-tuning in generative AI?"),
    ("Course concept explanation", "Explain how grounding improves the reliability of AI study answers."),
    ("Study planning", "How should I prepare for a generative AI exam using lecture notes and definitions?"),
]


def display_tool_trace(tool_trace):
    if not tool_trace:
        return

    for index, item in enumerate(tool_trace, start=1):
        st.markdown(f"**Tool call {index}:** `{item['tool']}`")
        st.json(item)


def main():
    st.set_page_config(page_title="MentorMate AI Companion", page_icon="📚")
    st.title("MentorMate — AI Study Companion")
    st.write(
        "Get fast, grounded answers to your course questions using lecture notes and reliable definitions. Ask about a concept, assignment topic, or study plan and MentorMate will use supporting data to answer clearly."
    )
    st.markdown("---")

    st.sidebar.header("How to use")
    st.sidebar.write(
        "Ask a course-related question, request a summary, or look up a term. MentorMate will decide whether it needs supporting data from notes or a definition source."
    )
    api_key_set = bool(os.getenv("OPENAI_API_KEY"))
    if api_key_set:
        st.sidebar.success("OPENAI_API_KEY is configured. The app is ready to answer questions.")
    else:
        st.sidebar.warning("OPENAI_API_KEY is not set. Set it before running this app.")

    user_input = st.text_area("Your question", height=160)
    submit = st.button("Ask MentorMate")

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
                    with st.expander("Supporting data used for this response"):
                        display_tool_trace(tool_trace)
            except Exception as exc:
                st.error(str(exc))

    st.markdown("---")
    st.subheader("Quick tests")

    with st.expander("Example study questions"):
        st.write("Try these real course questions to see how MentorMate uses notes and definitions.")
        if st.button("Run example questions"):
            for title, prompt in SAMPLE_PROMPTS:
                st.markdown(f"**{title}**")
                st.write(f"Question: {prompt}")
                try:
                    ans, trace, choice = run_study_sense(prompt)
                    st.markdown("**Answer**")
                    st.write(ans)
                    if trace:
                        with st.expander("Supporting data for this answer"):
                            display_tool_trace(trace)
                    st.markdown("---")
                except Exception as e:
                    st.error(f"{title} failed: {e}")


if __name__ == "__main__":
    main()
