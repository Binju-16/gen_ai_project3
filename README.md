# MentorMate — AI Study Companion

MentorMate is an AI study companion for students who need fast, grounded answers to course questions. It helps learners understand technical concepts, find relevant course material, and prepare more effectively for assignments and exams.

## Problem statement

Students often struggle to understand complex course concepts quickly because answers from generic AI systems are vague or ungrounded. MentorMate solves this by combining course notes and reliable definitions with an AI model that decides when to use supporting tools behind the scenes.

## Why I Built This

As a graduate student in Data Science, I frequently use AI tools to learn new concepts, review coursework, and prepare for exams. While many AI assistants can answer questions, they often provide generic explanations that are not connected to course material or study goals.

I built MentorMate to explore how an AI system could become a more effective learning companion by combining grounded course notes, reliable concept definitions, and structured study planning. The goal was not simply to answer questions, but to help students learn more effectively through transparent and grounded responses.


## Why MentorMate is different

MentorMate is not just a general chatbot. It uses an agentic workflow where the model decides whether it needs a definition, course-note context, or a study plan before answering. This makes the response more useful for students because answers are grounded in either course notes, dictionary data, or structured planning logic instead of only relying on model memory.

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

## Agentic Workflow

```text
User Question
      ↓
Streamlit Interface
      ↓
OpenAI Agent
      ↓
Tool Decision
 ┌───────────────┬───────────────────┬─────────────────┐
 │ lookup_term   │ search_course_notes │ build_study_plan │
 └───────────────┴───────────────────┴─────────────────┘
      ↓
Tool Output
      ↓
Grounded Response
      ↓
Student
```

The model decides whether a tool is needed, selects the appropriate tool, reads the returned information, and then generates a grounded final response.


## How it works

MentorMate uses a small set of tools to provide more accurate answers. When a user asks a question, the AI decides if it needs a definition or a note lookup, then requests the appropriate tool. This keeps the response grounded and study-ready.

## Key Design Decisions

### Why Multiple Tools?

A single definition tool was not sufficient for realistic student workflows. Students often need both conceptual explanations and practical study guidance. This led to the addition of course-note retrieval and study-plan generation.

### Why Grounding?

Grounding improves reliability by providing information that the model cannot infer from pretraining alone. Course notes and tool outputs help reduce generic responses and improve educational usefulness.

### Why Streamlit?

Streamlit provided a simple way to build and deploy an interactive interface while allowing users to inspect tool traces and understand how answers were generated.


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

## Evaluation Results

- Evaluated using 8 study-oriented test cases.
- Verified autonomous tool selection across definition lookup, note retrieval, and study planning scenarios.
- Achieved 100% tool execution success across evaluation cases.
- Tool traces and grounded outputs are documented in `evaluation.md`.

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
- The application currently focuses on generative AI coursework and is not optimized for other academic domains.
- Dictionary-based lookups may not always contain specialized AI terminology.
- The system does not currently maintain long-term conversation memory across sessions.


## Live Application

Deployment URL:

https://binjugenaiproject3.streamlit.app/

The deployed application allows users to interact with MentorMate through the Streamlit interface and observe tool traces generated during agent execution.