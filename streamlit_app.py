import asyncio
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import process_user_message

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


HELP_MODES = {
    "Explain": "Explain the following topic clearly for a student:",
    "Summarize": "Summarize the following study material or topic for a student:",
    "Study Plan": "Create a practical study plan for the following topic or exam goal:",
    "Quiz Me": "Generate a useful practice quiz for the following topic:",
    "Study Mode": (
        "Create a complete study guide for the following topic. Include an explanation, "
        "key points, examples, practice questions, and a quick revision checklist:"
    ),
    "Compare": "Compare the following concept with related concepts and explain the differences:",
}


def tool_display_name(tool_name: str) -> str:
    names = {
        "lookup_term": "Dictionary / Term Lookup",
        "search_course_notes": "Course Notes Search",
        "build_study_plan": "Study Plan Builder",
        "generate_practice_quiz": "Practice Quiz Generator",
    }
    return names.get(tool_name, tool_name)


def tool_purpose(tool_name: str) -> str:
    purposes = {
        "lookup_term": "Used to define or clarify a study concept.",
        "search_course_notes": "Used to ground the answer in available course notes.",
        "build_study_plan": "Used to create a structured review plan.",
        "generate_practice_quiz": "Used to create topic-specific practice questions.",
    }
    return purposes.get(tool_name, "Used as supporting information for the answer.")


def extract_sources(tool_trace: List[Dict[str, Any]]) -> List[str]:
    sources = []

    for item in tool_trace:
        tool_name = item.get("tool", "")
        result = item.get("result", {})

        if tool_name == "lookup_term":
            source = result.get("source", "")
            if source and source != "none":
                sources.append(f"Dictionary source: {source}")

        elif tool_name == "search_course_notes":
            matches = result.get("matches", [])
            if matches:
                topics = [note.get("topic", "Course note") for note in matches]
                sources.append("Course notes: " + ", ".join(topics))

        elif tool_name == "build_study_plan":
            topics = result.get("topics", [])
            if topics:
                sources.append("Study plan generated for: " + ", ".join(topics))

        elif tool_name == "generate_practice_quiz":
            topic = result.get("topic", "selected topic")
            sources.append(f"Practice quiz generated for: {topic}")

    return sources


def get_quiz_result(tool_trace: List[Dict[str, Any]]) -> Dict[str, Any] | None:
    for item in tool_trace:
        if item.get("tool") == "generate_practice_quiz":
            return item.get("result", {})
    return None


def render_answer_card(answer: str):
    st.markdown("### MentorMate Response")
    st.markdown(
        f"""
        <div style="
            padding: 1.25rem;
            border-radius: 14px;
            border: 1px solid rgba(120, 120, 120, 0.25);
            background-color: rgba(250, 250, 250, 0.04);
            line-height: 1.6;
            font-size: 1rem;
        ">
            {answer}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_quiz_cards(quiz_result: Dict[str, Any]):
    questions = quiz_result.get("questions", [])
    topic = quiz_result.get("topic", "this topic")

    if not questions:
        return

    st.markdown("### Practice Quiz")
    st.caption(f"Use these questions to test your understanding of **{topic}**.")

    for q in questions:
        q_num = q.get("question_number", "")
        q_type = q.get("type", "Practice")
        question = q.get("question", "")
        answer = q.get("answer", "")
        explanation = q.get("explanation", "")

        with st.container(border=True):
            st.markdown(f"**Question {q_num}: {q_type}**")
            st.write(question)

            with st.expander("Show answer and explanation"):
                st.markdown("**Answer**")
                st.write(answer)

                st.markdown("**Why this helps**")
                st.write(explanation)


def render_sources(tool_trace: List[Dict[str, Any]]):
    if not tool_trace:
        return

    sources = extract_sources(tool_trace)

    if sources:
        st.markdown("### Learning Resources Used")
        for source in sources:
            st.success(source)

    st.markdown("### How MentorMate Built This Answer")
    for index, item in enumerate(tool_trace, start=1):
        tool_name = item.get("tool", "")
        st.markdown(f"**{index}. {tool_display_name(tool_name)}**")
        st.caption(tool_purpose(tool_name))


def render_debug_trace(tool_trace: List[Dict[str, Any]]):
    if not tool_trace:
        return

    show_debug = st.checkbox("Show developer tool trace")
    if show_debug:
        st.json(tool_trace)


def build_mode_prompt(mode: str, user_input: str) -> str:
    instruction = HELP_MODES.get(mode, "Help the student with the following request:")
    return f"{instruction}\n\n{user_input.strip()}"


def run_prompt(prompt: str):
    with st.spinner("MentorMate is preparing your study support..."):
        result = run_async(process_user_message(prompt))

    answer = result.get("answer", "")
    tool_trace = result.get("tool_trace", [])
    quiz_result = get_quiz_result(tool_trace)

    render_answer_card(answer)

    if quiz_result:
        st.markdown("")
        render_quiz_cards(quiz_result)

    st.markdown("")
    render_sources(tool_trace)
    render_debug_trace(tool_trace)


def main():
    st.set_page_config(
        page_title="MentorMate AI Study Companion",
        page_icon="📚",
        layout="wide",
    )

    st.markdown(
        """
        <div style="padding: 1rem 0 0.5rem 0;">
            <h1 style="margin-bottom: 0;">📚 MentorMate</h1>
            <p style="font-size: 1.1rem; color: #666;">
                An AI study companion for explanations, summaries, quizzes, study guides, and exam planning.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not os.getenv("OPENAI_API_KEY"):
        st.warning("OPENAI_API_KEY is not set. The app needs an API key to answer questions.")

    with st.sidebar:
        st.header("How MentorMate helps")
        st.write(
            "MentorMate helps students understand academic topics, prepare for exams, and turn study questions into useful learning materials."
        )

        st.markdown("**It can:**")
        st.markdown(
            """
            - Explain academic concepts
            - Summarize study material
            - Build study plans
            - Generate practice quizzes
            - Create complete study guides
            - Show supporting tools when used
            """
        )

        st.markdown("---")
        st.markdown("**Best for:**")
        st.caption(
            "Biology, chemistry, math, computer science, history, business, exam prep, study guides, and study planning."
        )

    st.markdown("### Choose what kind of help you want")

    if "selected_mode" not in st.session_state:
        st.session_state.selected_mode = "Explain"

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        if st.button("Explain", use_container_width=True):
            st.session_state.selected_mode = "Explain"

    with col2:
        if st.button("Summarize", use_container_width=True):
            st.session_state.selected_mode = "Summarize"

    with col3:
        if st.button("Study Plan", use_container_width=True):
            st.session_state.selected_mode = "Study Plan"

    with col4:
        if st.button("Quiz Me", use_container_width=True):
            st.session_state.selected_mode = "Quiz Me"

    with col5:
        if st.button("Study Mode", use_container_width=True):
            st.session_state.selected_mode = "Study Mode"

    with col6:
        if st.button("Compare", use_container_width=True):
            st.session_state.selected_mode = "Compare"

    st.info(f"Selected mode: **{st.session_state.selected_mode}**")

    user_input = st.text_area(
        "Type your own topic, question, notes, or exam goal",
        height=160,
        placeholder=(
            "Example: anatomy of frog\n"
            "Example: photosynthesis\n"
            "Example: I have a biology exam in 3 days on frog anatomy and respiration."
        ),
    )

    ask_button = st.button("Get Study Support", type="primary", use_container_width=True)

    if ask_button:
        if not user_input.strip():
            st.warning("Please type a topic, question, notes, or exam goal.")
            return

        final_prompt = build_mode_prompt(st.session_state.selected_mode, user_input)
        run_prompt(final_prompt)

    st.markdown("---")

    with st.expander("How to use MentorMate"):
        st.markdown(
            """
            1. Choose the type of help you want.
            2. Type any academic topic or study question.
            3. MentorMate will decide whether it can answer directly or whether a tool is useful.
            4. If a tool is used, you can see how the response was supported.
            """
        )

    with st.expander("How MentorMate works"):
        st.markdown(
            """
            MentorMate uses an agentic workflow. The model decides whether it needs a tool,
            chooses the best tool, reads the result, and then creates a student-friendly response.

            For simple explanations, it may answer directly. For quizzes, study plans, definitions,
            or grounded course material, it can use supporting tools behind the scenes.
            """
        )


if __name__ == "__main__":
    main()