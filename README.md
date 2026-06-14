# MentorMate — AI Study Companion

MentorMate is an AI study companion for students who need fast, grounded answers to course questions. It helps learners understand technical concepts, find relevant course material, and prepare more effectively for assignments and exams.

## Problem statement

Students often struggle to understand complex course concepts quickly because answers from generic AI systems are vague or ungrounded. MentorMate solves this by combining course notes and reliable definitions with an AI model that decides when to use supporting tools behind the scenes.

## Target user

- University students studying generative AI or related coursework.
- Learners who want explanations grounded in lecture notes and accurate terminology.
- Students preparing for exams, assignments, or concept reviews who need a quick study assistant.

## System architecture

- `app.py`: FastAPI backend that handles the chat API.
- `streamlit_app.py`: Streamlit front-end for interactive study sessions and tool tracing.
- `templates/index.html`: Simple fallback web frontend allowing users to ask questions.
- `static/style.css`: UI styling.
- `data/fallback_dictionary.json`: Local fallback data used when a live dictionary API lookup is unavailable.
- `data/course_notes.json`: Local course notes used by the `search_course_notes` tool to find relevant study material.
- `scripts/run_evaluation.py`: A test harness script that evaluates the app using real study-style questions and saves results to `evaluation.md`.
- `app.py` contains the AI orchestration logic and tool definitions for `lookup_term`, `search_course_notes`, and `build_study_plan`, allowing the model to request supporting data when needed.

## How it works

MentorMate uses a small set of tools to provide more accurate answers. When a user asks a question, the AI decides if it needs a definition or a note lookup, then requests the appropriate tool. This keeps the response grounded and study-ready.

## Tools available

Tool name: `lookup_term`

- Description: Fetches a precise definition, example usage, and explanation for a technical term.
- Input schema: `term` (string, required), `language` (string, default: English).
- Execution: first attempts a live dictionary lookup, then falls back to local definitions if needed.

Tool name: `search_course_notes`

- Description: Searches local course notes for explanations, examples, or context related to the question.
- Input schema: `query` (string, required), `max_results` (integer, default: 3).

Tool name: `build_study_plan`

- Description: Creates a structured study plan based on topics, deadlines, and available study hours.
- Input schema: `topics` (array of strings, required), `deadline` (string, required), `available_hours` (integer, default: 2).

## Setup

1. Clone this repository.
2. Create a Python environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set `OPENAI_API_KEY` in your environment.

```bash
export OPENAI_API_KEY="your_api_key_here"
```

5. Run the app locally using Streamlit:

```bash
streamlit run streamlit_app.py
```

6. Alternatively, run the FastAPI backend:

```bash
uvicorn app:app --reload
```

## Recommended commit messages
Use the following commit messages as a guide when saving your work:

- `feat: add Streamlit front-end and interactive study UI`
- `feat: implement MCP tools and tool dispatch`
- `docs: update README with Streamlit setup and project architecture`
- `test: add evaluation harness and sample model cases`
- `chore: add commit guidance and GitHub description`

7. Open the Streamlit app in your browser at the URL shown by Streamlit.

## Deployment

This app can be deployed either as the original FastAPI backend or as the Streamlit frontend. Example deployment options:

- FastAPI (existing):

  ```bash
  uvicorn app:app --host=0.0.0.0 --port=${PORT:-8000}
  ```

- Streamlit (recommended for interactive study UI):

  Example `Procfile` entry for platforms like Heroku:

  ```text
  web: sh -c 'streamlit run streamlit_app.py --server.port=${PORT:-8501} --server.address=0.0.0.0'
  ```

  Or run locally:

  ```bash
  streamlit run streamlit_app.py
  ```

## Example interaction

- User: `What is the difference between prompt engineering and fine-tuning?`
- The model may decide to search course notes or look up a precise definition.
- The tool returns supporting information.
- The final answer combines the model's explanation with grounded data.

## Evaluation plan

- Use real study questions to test whether MentorMate answers correctly.
- Measure usefulness by checking whether responses include supporting data and relevant course context.
- Track tool usage only when it improves the answer.
- Run `python3 scripts/run_full_evaluation.py` to generate `evaluation.md` from the latest app logic.

## What changed from draft to this version

- Added a public-facing web UI with a chat-style experience.
- Implemented three MCP tools and an agent loop in `app.py`.
- Added `search_course_notes` for course-specific grounding, `lookup_term` for definitions, and `build_study_plan` for scheduling.
- Included prompt engineering rationale, grounded tool execution, and a build log.
- Added fallback data for more reliable dictionary responses.
- Added a test harness script for evaluation and a dedicated `evaluation.md` output.

## Known limitations

- Requires an OpenAI API key.
- The tool currently supports English dictionary lookups only.
- The frontend is intentionally minimal for rapid iteration.

## Next steps for final submission

- Add a second tool for concept search or study-plan generation.
- Expand grounding with course-specific notes or focused study examples.
- Include structured evaluation metrics and test cases in the final write-up.
