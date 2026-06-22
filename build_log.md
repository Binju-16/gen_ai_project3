# MentorMate Build Log

## Initial Idea

- Build an AI study assistant that can explain technical terms and concepts.
- The core requirement was to build custom tools for grounded study support and demonstrate autonomous tool usage.
- The original version focused mainly on Generative AI course concepts, but later evolved into a broader AI study companion for multiple academic subjects.

---

## Prompt Engineering Experiments

### Version 1

- System prompt was generic: "You are an assistant. Answer the user."
- Result: model rarely used the tool and often answered from memory.

### Version 2

- Added explicit instructions to use tools for definitions and concept lookups.
- Included an agent role and constraints about not calling tools unnecessarily.
- Result: model began returning tool calls more reliably for definition requests.

### Version 3

- Added an explicit grounding sentence: "Use the tool whenever the user asks for a definition, example usage, or explanation."
- Result: stronger tool usage and more grounded responses.

### Version 4

- Added `search_course_notes` for course-specific grounding and study advice.
- Changed the system prompt to let the model choose between definition lookup and course-note search.
- This improved agentic behavior by giving the model two decisions:
  1. whether to use a tool
  2. which tool to use

### Version 5

- Updated the prompt to improve user experience when tools returned no useful result.
- The model was instructed not to expose internal tool failures to users.
- Result: responses became more natural and production-ready.

### Version 6

- Expanded the system prompt from a Generative AI course tutor into a broader academic study companion.
- The model can now support explanations, quizzes, study guides, comparisons, summaries, and study plans across different academic subjects.
- Result: the app became more useful for real students instead of feeling like a rubric demonstration.

---

## Tool Design

- Created `lookup_term` as the first custom tool used for grounded term definitions.
- Defined the tool with a clear JSON schema for `term` and `language`.
- Implemented execution with a live dictionary API and a fallback local dictionary.
- Added `search_course_notes` to retrieve local grounded study material.
- Added `build_study_plan` for structured review schedules and practical student support.
- Added `generate_practice_quiz` to create topic-specific practice questions and answers.

---

## Agent Loop

- The backend sends the user request to OpenAI with tool definitions.
- The model decides whether a tool is needed and which tool to call.
- If the model returns a tool call, the backend executes the selected tool and returns results.
- The model then receives the tool output and produces a final answer.
- This loop ensures the decision to call tools is controlled by the LLM rather than hardcoded Python routing.

---

## Evaluation Notes

- Tested concept explanations such as:
  - "Explain the anatomy of a frog."
  - "Compare mitosis and meiosis."
  - "Explain photosynthesis."

- Tested study-support workflows:
  - "Generate a practice quiz on frog anatomy."
  - "Create a study guide on photosynthesis."
  - "I have a biology exam in three days. Build a study plan."

- Verified tool traces in the UI to confirm autonomous tool selection and execution.

---

## Major Design Decisions

### Why I Chose a Study Assistant

As a graduate student, I regularly use AI tools to learn new concepts, review coursework, and prepare for exams. While many AI tools can answer questions, they often provide generic explanations and do not always help structure learning. I wanted to build a study assistant that could combine explanations, grounded information, quizzes, study planning, and autonomous tool usage in a single application.

### Why Grounding Was Important

One of the main goals of MentorMate was to reduce reliance on model memory alone. By grounding answers in local notes, external definitions, and tool outputs, the assistant can provide responses that are more accurate, transparent, and useful for learning.

### Why Multiple Tools Were Added

The first version only supported term lookup. During development, I realized that definitions alone were not enough for real student use cases. Students also need explanations, quizzes, study plans, summaries, and support for organizing study time. This led to the addition of `search_course_notes`, `build_study_plan`, and `generate_practice_quiz`.

### Why the UI Was Redesigned

The early interface was functional but too minimal and technical. It showed raw tool information and felt closer to a class demonstration than a real application. I redesigned the interface around student workflows: Explain, Summarize, Study Plan, Quiz Me, Study Mode, and Compare. This made the app easier for an average student to understand and use.

---

## Engineering Challenges and Fixes

### OpenAI SDK Serialization Issue

**Problem:**  
The evaluation script failed because OpenAI response objects could not be written directly to JSON.

**Investigation:**  
The newer OpenAI SDK returns structured response objects instead of plain dictionaries.

**Solution:**  
Updated `run_full_evaluation.py` to safely convert response objects using `raw_message.to_dict()` before writing evaluation output.

**Result:**  
The evaluation script regenerated `evaluation.md` successfully without serialization errors.

### Environment Variable Setup

**Problem:**  
The app could not call OpenAI because `OPENAI_API_KEY` was missing.

**Investigation:**  
The project expected the key from the environment, but no `.env` file existed locally.

**Solution:**  
Added `python-dotenv`, created `.env`, and loaded environment variables with `load_dotenv()`.

**Result:**  
The app can now load the API key locally while keeping secrets out of GitHub.

### Tool Failure Messages

**Problem:**  
Earlier versions exposed internal messages such as "the lookup tool did not find a definition."

**Investigation:**  
This made the app feel less polished and revealed implementation details that were not useful to students.

**Solution:**  
Updated the system prompt and fallback handling so the assistant gives a helpful answer without exposing tool failures.

**Result:**  
Responses became cleaner and more user-friendly.

### Quiz Quality

**Problem:**  
The first quiz tool generated generic template questions that were not specific enough for academic topics.

**Investigation:**  
Questions like "What is one important idea related to frog anatomy?" were not useful for real studying.

**Solution:**  
Updated the quiz-generation workflow so quizzes became more topic-specific and useful for exam preparation.

**Result:**  
The app now provides better practice questions for user-selected topics.

---

## Project Evolution

### Stage 1: Basic Study Assistant

The project began as a simple study assistant that answered questions about course concepts. At this stage, the system behaved similarly to a standard chatbot and relied primarily on model knowledge.

### Stage 2: Introducing Tool Usage

After reviewing the project requirements, I realized the application needed to demonstrate autonomous tool use. I created the `lookup_term` tool and modified the prompt so the model could decide when a definition lookup was needed.

### Stage 3: Improving Grounding

While testing the application, I noticed that many course-related questions required information beyond standard dictionary definitions. To improve grounding, I added the `search_course_notes` tool and connected the application to local course notes. This allowed the model to provide answers that were more relevant to coursework and exam preparation.

### Stage 4: Expanding Student Support

Definitions and note retrieval alone were not sufficient for practical study scenarios. To support students preparing for assignments and exams, I implemented the `build_study_plan` tool, allowing the model to generate structured study schedules based on topics and deadlines.

### Stage 5: Evaluation and User Experience

Once the core functionality was working, I focused on evaluation and usability. I created evaluation scripts to test tool selection and grounding behavior, fixed serialization issues in evaluation outputs, and improved fallback handling so users would receive helpful answers even when a tool could not find relevant information.

### Stage 6: Transition to a General Study Companion

After receiving draft feedback, I realized the application still felt too much like a demonstration of Generative AI course concepts. The interface, example prompts, and evaluations were heavily focused on the course itself.

To make the application more useful for real students, I redesigned MentorMate into a broader academic study companion. New study modes such as Explain, Summarize, Study Plan, Quiz Me, Study Mode, and Compare were added. The interface was redesigned to focus on learning workflows rather than AI terminology.

This change significantly improved the practical usefulness of the application while preserving the underlying agentic architecture, grounding strategy, and MCP tool execution.

### Final Version

The final MentorMate system combines prompt engineering, grounding, tool orchestration, evaluation, and a deployed Streamlit interface. The application can autonomously select tools, retrieve supporting information, generate study plans, create practice quizzes, compare concepts, and provide grounded academic support across a variety of subjects.

---

## Future Improvements

- Expand course-note coverage across multiple academic subjects.
- Add PDF and lecture-note uploads.
- Improve retrieval quality for uploaded study materials.
- Add conversation history and session memory.
- Support downloadable study guides and quizzes.
- Add optional web-search grounding.

---

## Reflection

This project changed my understanding of generative AI systems. Initially I viewed AI assistants primarily as prompt-and-response applications. Through this project I learned that effective AI products require much more than prompting. They require system design, tool orchestration, grounding, evaluation, deployment, and user experience considerations.

The final MentorMate system demonstrates how an LLM can autonomously choose tools, retrieve supporting information, generate quizzes and study plans, and produce student-focused responses. The project also reinforced the importance of iteration because a system that appears to work can still reveal weaknesses when tested against realistic scenarios and instructor feedback.