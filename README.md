# StudySense — Project 3 AI Study Companion

StudySense is a capstone draft app for the Generative AI course. It combines a custom MCP tool, agentic decision making, prompt engineering, grounding, and a deployed-ready web interface.

## Problem statement

Students often need quick, reliable concept explanations and examples while studying generative AI and related technical topics. StudySense solves this by letting a learner ask questions directly and triggering a live dictionary lookup tool when the model decides it needs grounded definitions.

## Target user

- Undergraduate or graduate students studying generative AI.
- Learners who need a simple deployed assistant to explain technical terms, show examples, and guide study decisions.
- Instructors or graders who want to evaluate an agentic system with visible tool usage.

## System architecture

- `app.py`: FastAPI backend that serves the UI and handles the chat API.
- `templates/index.html`: Simple frontend allowing users to ask questions.
- `static/style.css`: UI styling.
- `data/fallback_dictionary.json`: Local fallback data used when the live dictionary API is unavailable.
- `data/course_notes.json`: Local course notes used by the `search_course_notes` tool for domain grounding.
- `scripts/run_evaluation.py`: A test harness script that executes sample prompts against the LLM and saves results to `evaluation.md`.
- `app.py` contains MCP tool definitions for `lookup_dictionary_entry` and `search_course_notes`, plus an agent loop that:
  1. sends the user request to the LLM,
  2. detects whether the model wants to call a tool,
  3. executes that tool if requested,
  4. returns the result to the model,
  5. continues until the model produces a final answer.

## Agentic behavior

StudySense is agentic because the model decides whether to call the `lookup_dictionary_entry` tool. The Python backend does not hardcode the decision path. Instead, it exposes the tool and executes it only when the model returns a tool call.

## MCP tool

Tool name: `lookup_dictionary_entry`

- Description: Fetches a definition, example usage, and explanation for a study term or concept.
- Input schema: `word` (string, required), `language` (string, default: English).
- Execution: either live dictionary data from `dictionaryapi.dev` or fallback local data.

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

5. Run the app:

```bash
uvicorn app:app --reload
```

6. Open `http://127.0.0.1:8000` in your browser.

## Deployment

This app is ready for deployment to platforms like Railway, Render, or Heroku using `uvicorn app:app --host=0.0.0.0 --port=${PORT:-8000}`. A `procfile` is included for easy deployment.

## Example interaction

- User: `What does agentic behavior mean in an AI system?`
- Model may choose to call the tool with `word=agentic`
- Tool returns the definition and examples
- Model returns a grounded answer referencing the live lookup result

## Evaluation plan

- Use test prompts that ask for definitions, course grounding, or study guidance.
- Confirm that the model selects a tool and that the tool call is visible in the tool trace.
- Verify that the final answer is coherent and grounded in the returned data.
- Run `python3 scripts/run_evaluation.py` to generate `evaluation.md` with live model outputs.
- Document failures and iterate on prompt wording.

## What changed from draft to this version

- Added a public-facing web UI with a chat-style experience.
- Implemented two MCP tools and an agent loop in `app.py`.
- Added `search_course_notes` for course-specific grounding and `lookup_dictionary_entry` for definitions.
- Included prompt engineering rationale, grounded tool execution, and a build log.
- Added fallback data for more reliable dictionary responses.
- Added a test harness script for evaluation and a dedicated `evaluation.md` output.

## Known limitations

- Requires an OpenAI API key.
- The tool currently supports English dictionary lookups only.
- The frontend is intentionally minimal for rapid iteration.

## Next steps for final submission

- Add a second tool for concept search or study-plan generation.
- Expand grounding with course-specific notes or rubric-aware examples.
- Include structured evaluation metrics and test cases in the final write-up.
