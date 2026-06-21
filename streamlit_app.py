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


SAMPLE_PROMPTS = {
    "Explain Concept": "Explain grounding in generative AI using a student-friendly example.",
    "Summarize Notes": "Summarize the course notes on prompt engineering and explain why they matter.",
    "Make Study Plan": "I have an exam in three days on prompt engineering, grounding, and agentic behavior. Create a focused study plan.",
    "Practice Quiz": "Generate a practice quiz on grounding in generative AI.",
    "Compare Concepts": "Compare prompt engineering and fine-tuning, and explain when each is useful.",
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
        "search_course_notes": "Used to ground the answer in course-specific notes.",
        "build_study_plan": "Used to create a structured review plan.",
        "generate_practice_quiz": "Used to create practice questions for active recall.",
    }
    return purposes.get(tool_name, "Used as supporting information for the answer.")


def extract_sources(tool_trace: List[Dict[str, Any]]) -> List[str]:
    sources = []

    for item in tool_trace:
        tool_name = item.get("tool", "")
        result = item.get("result", {})

        if tool_name == "lookup_term":
            source = result.get("source", "dictionary/fallback")
            if source and source != "none":
                sources.append(f"Dictionary source: {source}")
            else:
                sources.append("General explanation used because no dictionary entry was found.")

        elif tool_name == "search_course_notes":
            matches = result.get("matches", [])
            if matches:
                topics = [note.get("topic", "Course note") for note in matches]
                sources.append("Course notes: " + ", ".join(topics))
            else:
                sources.append("Course notes searched, but no direct match was found.")

        elif tool_name == "build_study_plan":
            topics = result.get("topics", [])
            if topics:
                sources.append("Study plan generated for: " + ", ".join(topics))
            else:
                sources.append("Study plan builder used.")

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
        st.info("No tools were needed for this response.")
        return

    st.markdown("### Sources Used")

    sources = extract_sources(tool_trace)
    for source in sources:
        st.success(source)

    st.markdown("### Tool Decisions")
    for index, item in enumerate(tool_trace, start=1):
        tool_name = item.get("tool", "")
        st.markdown(f"**{index}. {tool_display_name(tool_name)}**")
        st.caption(tool_purpose(tool_name))


def render_debug_trace(tool_trace: List[Dict[str, Any]]):
    if not tool_trace:
        return

    with st.expander("Developer view: raw tool trace"):
        st.json(tool_trace)


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
                A grounded AI study companion for explanations, course-note support, quizzes, and exam planning.
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
            "MentorMate is designed for students who want study support that is more grounded and actionable than a basic chatbot."
        )

        st.markdown("**It can:**")
        st.markdown(
            """
            - Explain technical concepts
            - Search course notes
            - Build study plans
            - Generate practice quizzes
            - Show which tools supported the answer
            """
        )

        st.markdown("---")
        st.markdown("**Best for:**")
        st.caption("Generative AI concepts, assignment review, exam preparation, practice questions, and study planning.")

    st.markdown("### What do you need help with?")

    col1, col2, col3, col4, col5 = st.columns(5)

    if "selected_prompt" not in st.session_state:
        st.session_state.selected_prompt = ""

    with col1:
        if st.button("Explain", use_container_width=True):
            st.session_state.selected_prompt = SAMPLE_PROMPTS["Explain Concept"]

    with col2:
        if st.button("Summarize", use_container_width=True):
            st.session_state.selected_prompt = SAMPLE_PROMPTS["Summarize Notes"]

    with col3:
        if st.button("Study Plan", use_container_width=True):
            st.session_state.selected_prompt = SAMPLE_PROMPTS["Make Study Plan"]

    with col4:
        if st.button("Quiz Me", use_container_width=True):
            st.session_state.selected_prompt = SAMPLE_PROMPTS["Practice Quiz"]

    with col5:
        if st.button("Compare", use_container_width=True):
            st.session_state.selected_prompt = SAMPLE_PROMPTS["Compare Concepts"]

    user_input = st.text_area(
        "Enter your study question, topic, or deadline",
        value=st.session_state.selected_prompt,
        height=150,
        placeholder=(
            "Example: Generate a practice quiz on grounding in generative AI."
        ),
    )

    ask_button = st.button("Get Study Support", type="primary", use_container_width=True)

    if ask_button:
        if not user_input.strip():
            st.warning("Please enter a study question or choose one of the quick actions.")
            return

        run_prompt(user_input.strip())

    st.markdown("---")

    with st.expander("Example requests you can try"):
        for label, prompt in SAMPLE_PROMPTS.items():
            st.markdown(f"**{label}:** {prompt}")

    with st.expander("What makes this different from a regular chatbot?"):
        st.markdown(
            """
            MentorMate uses an agentic workflow. The model decides whether it needs a tool,
            chooses the best tool, reads the result, and then creates a response.

            Instead of only relying on model memory, it can use dictionary lookup,
            course-note grounding, study-plan generation, and practice quiz generation.
            """
        )


if __name__ == "__main__":
    main()