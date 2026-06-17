# MentorMate Build Log

## Initial idea

- Build an AI study assistant that can explain technical terms and concepts.
- The core requirement was to build a custom tool for grounded term lookup and demonstrate autonomous tool usage.

## Prompt engineering experiments

### Version 1

- System prompt was generic: "You are an assistant. Answer the user."
- Result: model rarely used the tool and often answered from memory.

### Version 2

- Added explicit instructions to use the tool for definitions and concept lookups.
- Included an agent role and constraints about not calling the tool unnecessarily.
- Result: model began returning `function_call` more reliably for definition requests.

### Version 3

- Added an explicit grounding sentence: "Use the tool whenever the user asks for a definition, example usage, or explanation."
- Result: stronger tool usage and more grounded responses.

### Version 4

- Added a second tool, `search_course_notes`, for course-specific grounding and study advice.
- Changed the system prompt to let the model choose between definition lookups and course note searches.
- This improves agentic behavior by giving the model two decisions:
  1) whether to use a tool, and 2) which tool to use.

## Tool design

- Created `lookup_term` as the first custom tool used for grounded term definitions.
- Defined the tool with a clear JSON schema for `term` and `language`.
- Implemented execution with a live dictionary API and a fallback local dictionary.
- Added `build_study_plan` for structured review schedules and more practical student support.

## Agent loop

- The backend sends the user request to OpenAI with tool definitions.
- If the model returns a tool call, the backend executes the tool and returns results.
- The model then receives the tool output and produces a final answer.
- This loop ensures the decision to call the tool is controlled by the LLM.

## Evaluation notes

- Tested with prompts like:
  - "What is grounding in an AI system?"
  - "Define agentic behavior and give an example."
  - "Explain the term prompt engineering."
- Verified the tool trace in the UI to confirm actual tool invocation.

## Major Design Decisions

### Why I Chose a Study Assistant

As a graduate student, I regularly use AI tools to learn new concepts, review coursework, and prepare for exams. While many AI tools can answer questions, they often provide generic explanations that are not connected to course material. I wanted to build a study assistant that could combine grounded information, structured study planning, and autonomous tool usage in a single application.

### Why Grounding Was Important

One of the main goals of MentorMate was to reduce reliance on model memory alone. By grounding answers in course notes and external definitions, the assistant can provide responses that are more accurate, transparent, and useful for learning.

### Why Multiple Tools Were Added

The first version only supported term lookup. During development I realized that definitions alone were not enough for real student use cases. Students also need explanations connected to course content and help organizing study time. This led to the addition of the `search_course_notes` and `build_study_plan` tools.


## Future Improvements

- Expand course-note coverage for additional AI concepts.
- Improve retrieval quality for domain-specific terminology.
- Add conversation history and session memory.
- Support multiple courses and subject areas.

## Engineering challenges and fixes

### OpenAI SDK serialization issue

**Problem:**  
The evaluation script failed because OpenAI response objects could not be written directly to JSON.

**Investigation:**  
The newer OpenAI SDK returns structured response objects instead of plain dictionaries.

**Solution:**  
Updated `run_full_evaluation.py` to safely convert response objects using `raw_message.to_dict()` before writing evaluation output.

**Result:**  
The evaluation script regenerated `evaluation.md` successfully without serialization errors.

### Environment variable setup

**Problem:**  
The app could not call OpenAI because `OPENAI_API_KEY` was missing.

**Investigation:**  
The project expected the key from the environment, but no `.env` file existed locally.

**Solution:**  
Added `python-dotenv`, created `.env`, and loaded environment variables with `load_dotenv()`.

**Result:**  
The app can now load the API key locally while keeping secrets out of GitHub.

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

### Final Version

The final MentorMate system combines prompt engineering, grounding, tool orchestration, evaluation, and a deployed Streamlit interface. The application can autonomously select tools, retrieve supporting information, generate study plans, and provide grounded responses for students.


## Reflection

This project changed my understanding of generative AI systems. Initially I viewed AI assistants primarily as prompt-and-response applications. Through this project I learned that effective AI products require much more than prompting. They require system design, tool orchestration, grounding, evaluation, and user experience considerations.

The final MentorMate system demonstrates how an LLM can autonomously choose tools, retrieve supporting information, and generate grounded responses. The project also reinforced the importance of evaluation because a system that appears to work can still reveal weaknesses when tested against realistic scenarios.
