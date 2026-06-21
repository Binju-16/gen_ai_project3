# MentorMate Roadmap

## Current Implementation

MentorMate is a deployed AI study companion built with Streamlit and a FastAPI-style agent backend in `app.py`. The application helps students explain academic concepts, generate practice quizzes, create study guides, compare concepts, summarize material, and build study plans.

The system supports four custom tools:

- `lookup_term`
- `search_course_notes`
- `build_study_plan`
- `generate_practice_quiz`

The model decides when to call these tools through OpenAI function calling, and the app displays tool-supported outputs in a student-friendly interface.

## Project Goal

The goal of MentorMate is to help students turn academic questions into usable study support. Instead of functioning only as a general chatbot, MentorMate provides structured study workflows such as explanation, quiz generation, study planning, comparison, and study-guide creation.

## Target Users

- Students preparing for exams or assignments.
- Students who need quick explanations of academic topics.
- Learners who want practice questions, summaries, and study plans.
- Users who want a simple study tool without needing to understand AI architecture.

## Architecture

- `streamlit_app.py`: User-facing Streamlit interface.
- `app.py`: Agent loop, system prompt, tool definitions, and tool execution.
- `data/course_notes.json`: Local grounding source for study-related course concepts.
- `data/fallback_dictionary.json`: Backup glossary for dictionary lookup.
- `scripts/run_full_evaluation.py`: Evaluation runner.
- `evaluation.md`: Recorded test cases and results.

## Agentic Workflow

1. User selects a study mode or types a request.
2. The prompt is sent to the LLM with tool definitions.
3. The LLM decides whether a tool is needed.
4. If needed, the backend executes the selected tool.
5. The tool result is returned to the model.
6. The model generates a final student-facing answer.

This satisfies the agentic requirement because the model, not hardcoded routing logic, decides whether to call tools and which tool to call.

## Grounding Strategy

MentorMate uses grounding through:

- Local course notes in `course_notes.json`
- Dictionary API lookups
- Fallback dictionary entries
- Tool outputs returned to the model

The system can answer general academic questions directly, while using grounded sources when available.

## Evaluation Strategy

MentorMate is evaluated using structured test cases that check:

- Whether the model selects the correct tool.
- Whether tool calls execute successfully.
- Whether final answers use tool outputs.
- Whether outputs are useful for student learning.
- Whether the UI presents results clearly.

Evaluation results are recorded in `evaluation.md`.

## Completed Improvements

- Deployed the app publicly on Streamlit Cloud.
- Added multiple custom tools.
- Implemented an LLM-driven tool loop.
- Added prompt version documentation in `PROMPT_LOG.md`.
- Expanded the build log to show project evolution.
- Improved UI/UX with study modes and quiz cards.
- Hid raw JSON traces behind an optional developer view.
- Expanded grounding data.
- Improved quiz generation to support user-selected academic topics.

## Remaining Future Improvements

- Add file upload so students can generate quizzes and study guides from their own notes.
- Add PDF parsing for lecture slides or readings.
- Add downloadable study guides and quizzes.
- Add session history.
- Add optional web search grounding for current information.