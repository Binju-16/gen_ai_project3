import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import app
from app import process_user_message

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


SAMPLE_PROMPTS = [
    (
        "Exam study plan",
        "I have an exam in three days covering prompt engineering, grounding, and agentic behavior. Create a practical study plan with focused review sessions.",
    ),
    (
        "Note summary",
        "Summarize the course note on grounding and explain why it matters for my study strategy.",
    ),
    (
        "Concept comparison",
        "Compare prompt engineering and fine-tuning, and explain when each concept matters in practice.",
    ),
]


def render_tool_results(tool_trace):
    for index, item in enumerate(tool_trace, start=1):
        st.markdown(f"**Source {index}:** {item['tool']}")
        st.write(item['result'])


def main():
    st.set_page_config(page_title="MentorMate AI Companion", page_icon="📚")
    st.title("MentorMate — Study Companion")
    st.write(
        "Ask MentorMate for course explanations, note summaries, or a study plan based on your upcoming deadlines."
    )
    st.markdown("---")

    st.sidebar.header("How to use")
    st.sidebar.write(
        "Ask about course concepts, request a summary of your notes, or get a study schedule for an assignment or exam."
    )
    if not os.getenv("OPENAI_API_KEY"):
        st.sidebar.warning("OPENAI_API_KEY is not set. Set it before running this app.")

    user_input = st.text_area("Describe your study question or request", height=160)
    submit = st.button("Ask MentorMate")

    if submit:
        if not user_input.strip():
            st.warning("Please type a question or concept to proceed.")
            return

        with st.spinner("MentorMate is preparing your response..."):
            try:
                result = run_async(process_user_message(user_input))
                st.markdown("### Answer")
                st.write(result.get("answer", ""))

                tool_trace = result.get("tool_trace", [])
                if tool_trace:
                    with st.expander("Sources and supporting information"):
                        render_tool_results(tool_trace)
            except Exception as exc:
                st.error(str(exc))

    st.markdown("---")
    st.subheader("Example study tasks")

    with st.expander("Try these realistic requests"):
        st.write("Support requests related to studying, planning, or summarizing your course material.")
        if st.button("Run example questions"):
            for title, prompt in SAMPLE_PROMPTS:
                st.markdown(f"**{title}**")
                st.write(f"Question: {prompt}")
                try:
                    result = run_async(process_user_message(prompt))
                    st.markdown("**Answer**")
                    st.write(result.get("answer", ""))
                    trace = result.get("tool_trace", [])
                    if trace:
                        st.write("**Supporting data for this answer**")
                        render_tool_results(trace)
                    st.markdown("---")
                except Exception as e:
                    st.error(f"{title} failed: {e}")


if __name__ == "__main__":
    main()
