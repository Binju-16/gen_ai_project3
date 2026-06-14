# MentorMate Build Log

## Initial idea

- Build an AI study assistant that can explain technical terms and concepts.
- The core requirement would be a custom MCP tool for grounded lookup.

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

- Created `lookup_term` as the first MCP tool.
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

## What to improve next

- Add more grounding data for course-specific terms.
- Expand the UI with better state tracking and session history.
- Add evaluation metrics for accuracy and tool call reliability.

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