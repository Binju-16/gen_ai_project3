# MentorMate — AI Study Companion

MentorMate is an AI-powered study companion designed to help students learn more effectively. Instead of functioning as a generic chatbot, MentorMate provides structured learning support through concept explanations, study guides, practice quizzes, study plans, summaries, and concept comparisons.

The application combines prompt engineering, grounding, MCP tool use, and agentic decision-making to create a learning-focused experience that helps students prepare for exams, assignments, and concept reviews.

---

## Problem Statement

Students often spend significant time searching for explanations, creating study guides, generating practice questions, and organizing exam preparation. While general AI chatbots can answer questions, they rarely provide structured learning support tailored to studying.

MentorMate solves this problem by combining explanations, study guides, practice quizzes, concept comparison, and study planning into a single AI-powered study assistant.

---

## Why I Built This

As a graduate student in Data Science and Analytics, I regularly use AI tools to learn new concepts, review coursework, and prepare for exams. While AI assistants are useful, I often found that they provided isolated answers rather than helping me learn systematically.

I built MentorMate to explore how an AI system could become a more effective study companion by combining grounded information, structured study workflows, and autonomous tool usage. The goal was not simply to answer questions, but to help students learn more efficiently and prepare more effectively.

---

## What Makes MentorMate Different?

Many AI chatbots provide explanations but stop there.

MentorMate is designed around student workflows. Depending on the user's request, it can:

* Explain academic concepts
* Generate complete study guides
* Create practice quizzes
* Build study plans
* Summarize learning material
* Compare concepts
* Use supporting tools when helpful

The model decides whether a tool is needed and which tool to use. This allows MentorMate to provide more structured learning support than a standard chatbot response.

---

## Target Users

* University students preparing for exams, assignments, and concept reviews.
* Learners who need explanations, study guides, quizzes, and study plans.
* Students who want a study-focused AI assistant rather than a general-purpose chatbot.
* Self-directed learners looking for structured academic support.

---

## System Architecture

### Components

* `app.py` – Agent orchestration layer, system prompt, MCP tool definitions, and tool execution loop.
* `streamlit_app.py` – User-facing Streamlit application.
* `templates/index.html` – Lightweight web interface.
* `static/style.css` – Application styling.
* `data/course_notes.json` – Local grounded knowledge source.
* `data/fallback_dictionary.json` – Backup glossary data.
* `scripts/run_full_evaluation.py` – Evaluation harness.
* `evaluation.md` – Recorded evaluation results.

### Architecture Overview

```text
User
  ↓
Streamlit Interface
  ↓
OpenAI Agent
  ↓
Tool Decision
 ┌────────────────────┬──────────────────────┬────────────────────┬────────────────────────┐
 │ lookup_term        │ search_course_notes  │ build_study_plan   │ generate_practice_quiz │
 └────────────────────┴──────────────────────┴────────────────────┴────────────────────────┘
  ↓
Tool Output
  ↓
Grounded Response
  ↓
Student
```

The model determines whether a tool is required, chooses the appropriate tool, reads the returned result, and then generates the final response.

---

## Agentic Behavior

MentorMate satisfies the agentic requirement because the model, not the application code, decides:

* Whether a tool should be called.
* Which tool should be called.
* Whether additional information is needed.
* When enough information has been gathered to answer the user.

The Python application provides tools and an execution loop, but the model remains responsible for decision-making throughout the interaction.

Example:

1. User asks for a definition.
2. The model chooses `lookup_term`.
3. The application executes the tool.
4. The result is returned to the model.
5. The model uses the result to generate the final answer.

---

## Grounding Strategy

MentorMate uses grounding to improve reliability and usefulness.

Grounding sources include:

* Local course notes (`course_notes.json`)
* Dictionary API lookups
* Local fallback glossary entries
* Tool-generated outputs such as study plans and quizzes

When relevant grounded information exists, the model can use it before generating a response. When no grounded information is available, the model can still provide a general explanation.

---

## MCP Tools

### Tool: `lookup_term`

**Purpose**

Provides definitions and explanations for concepts.

**Inputs**

* `term` (string, required)
* `language` (string, optional)

**Execution**

* Attempts live dictionary lookup.
* Falls back to local glossary data when needed.

---

### Tool: `search_course_notes`

**Purpose**

Searches local study notes and returns relevant content.

**Inputs**

* `query` (string, required)
* `max_results` (integer, optional)

**Execution**

* Searches local grounded note content.
* Returns matching notes to the model.

---

### Tool: `build_study_plan`

**Purpose**

Creates structured study schedules.

**Inputs**

* `topics` (array, required)
* `deadline` (string, required)
* `available_hours` (integer, optional)

**Execution**

* Generates a structured review plan.
* Returns schedule information to the model.

---

### Tool: `generate_practice_quiz`

**Purpose**

Creates topic-specific practice quizzes.

**Inputs**

* `topic` (string, required)
* `num_questions` (integer, optional)

**Execution**

* Generates topic-specific study questions.
* Returns quiz content to the model.

---

## Setup Instructions

### 1. Clone Repository

```bash
git clone <repository-url>
cd MentorMate
```

### 2. Create Environment

```bash
python -m venv .venv
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Key

```bash
export OPENAI_API_KEY="your_api_key_here"
```

### 5. Run Streamlit Application

```bash
streamlit run streamlit_app.py
```

### Optional: Run FastAPI Backend

```bash
uvicorn app:app --reload
```

---

## Deployment

### Live Application

https://binjugenaiproject3.streamlit.app/

The deployed Streamlit application is publicly accessible and allows users to interact with MentorMate without local setup.

---

## Example Interaction

**User**

```text
Generate a practice quiz on anatomy of frog.
```

**Agent Decision**

* Chooses `generate_practice_quiz`.

**Tool Execution**

* Creates topic-specific practice questions.

**Final Response**

* Returns a quiz designed to help the student prepare for assessment on frog anatomy.

---

## Evaluation

MentorMate was evaluated using structured test cases covering:

* Tool selection
* Tool execution
* Grounding behavior
* Study plan generation
* Quiz generation
* Response quality

Results are documented in `evaluation.md`.

Evaluation confirmed:

* Successful tool execution.
* Correct tool selection behavior.
* Grounded responses when supporting data exists.
* Reliable study-support workflows.

---

## What Changed After Draft Feedback

The draft review identified two primary weaknesses:

### 1. Limited Grounding

Improvements:

* Expanded grounded note content.
* Improved retrieval behavior.
* Improved tool usage visibility.

### 2. Minimal User Interface

Improvements:

* Added study modes.
* Improved answer presentation.
* Added structured quiz display.
* Added cleaner tool summaries.
* Reduced exposure of raw JSON outputs.

These changes transformed MentorMate from a proof-of-concept study assistant into a more practical learning application.

---

## Known Limitations

* Requires an OpenAI API key.
* Grounding is strongest for topics represented in local notes.
* The application does not currently support PDF or document uploads.
* Real-time web search grounding is not implemented.
* Long-term memory across sessions is not available.

---

## Future Improvements

Potential future enhancements include:

* PDF upload and note extraction.
* Flashcard generation.
* Downloadable study guides.
* Session history.
* Web search grounding.
* Multi-course support.
* Personalized study recommendations.

---

## Repository Contents

* `README.md`
* `PROMPT_LOG.md`
* `BUILD_LOG.md`
* `EVALUATION.md`
* `app.py`
* `streamlit_app.py`
* `data/`
* `scripts/`

These documents provide sufficient information for another developer or evaluator to understand, deploy, test, and extend the system.
