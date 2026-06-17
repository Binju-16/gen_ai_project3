# MentorMate Prompt Log

## Purpose

This document records the evolution of the MentorMate system prompt throughout development. The goal is to demonstrate how prompt engineering was used to improve tool usage, grounding, agentic behavior, and overall user experience.

---

# Prompt Version 1: Basic Study Assistant

## Prompt

```text
You are a helpful study assistant. Answer the user's questions clearly and concisely.
```

## Result

This version produced reasonable answers but behaved like a traditional chatbot. The model typically answered questions directly from its own knowledge and rarely demonstrated tool usage or grounding behavior.

## Limitations

* No instructions for tool usage.
* No grounding requirements.
* No distinction between definitions, course notes, or study planning requests.
* Did not demonstrate agentic behavior required by the project.

## Why It Needed Improvement

The project requirements emphasized autonomous decision making and tool execution. A simple assistant prompt was not sufficient because the model had no reason to select or use available tools.

---

# Prompt Version 2: Agentic Tool-Aware Assistant

## Prompt

```text
You are MentorMate, an agentic study companion for students in a generative AI course.

When the user asks for a definition or explanation of a term, call the lookup_term tool and base your answer on its result.

When the user asks for course-specific examples, note summaries, or grounded context, call search_course_notes and use the returned notes explicitly.

When the user asks for a study schedule or exam preparation plan, call build_study_plan with topics, deadline, and available_hours.

Only answer directly when the question is purely conceptual and does not require a definition, grounding, or planning tool.

Choose the best tool, decide whether another tool is needed, and stop once the user has a complete study-focused response.

Always mention the source of grounding in the final answer and avoid hallucinations.
```

## What Changed

Compared to Version 1, this prompt introduced explicit instructions for tool selection and grounding.

The model was given three available tools:

* `lookup_term`
* `search_course_notes`
* `build_study_plan`

Each tool was associated with a specific type of user request.

## Why It Changed

The first prompt did not demonstrate autonomous decision making. I wanted the model to:

1. Decide whether a tool was needed.
2. Select the appropriate tool.
3. Read the tool output.
4. Generate a grounded final response.

These behaviors aligned directly with the project requirements for agentic AI systems.

## Result

Tool usage became significantly more reliable. Evaluation cases showed successful tool calls for definition requests, course-note retrieval, and study-plan generation. The application now demonstrated visible agentic behavior rather than functioning as a simple chatbot.

---

# Prompt Version 3: Improved User Experience and Failure Handling

## Prompt Addition

```text
If a tool returns found=false, no matches, no useful data, or an error, do not apologize, do not mention tool failure, and do not expose internal tool behavior.

Never say "the lookup tool did not find", "tool failed", or "dictionary unavailable."

Instead, provide the best clear and student-friendly explanation you can.

If grounding was available, briefly mention the source. If grounding was unavailable, answer naturally without discussing the failed lookup.
```

## What Changed

This version focused on improving the user experience.

Earlier versions sometimes generated responses such as:

```text
I'm sorry, but the lookup tool did not find a definition...
```

While technically correct, this exposed internal implementation details and made the application feel less polished.

## Why It Changed

Real users care about receiving useful answers, not about internal tool failures.

I wanted MentorMate to behave more like a production application by gracefully handling missing tool results while still providing helpful explanations.

## Result

The application now produces cleaner responses when dictionary lookups or note searches fail.

For example, a request such as:

```text
Explain the Big Bang Theory
```

previously exposed tool failure messages. After the prompt update, MentorMate provides a natural explanation of the concept without mentioning failed lookups or internal processing details.

---

# Lessons Learned

This prompt engineering process showed that effective AI applications require more than a good base model. Prompt design directly influences tool usage, grounding behavior, and overall user experience.

The most important lesson was that prompts should not only instruct the model what to do, but also define how the model should behave when tools succeed, fail, or return incomplete information. These refinements helped transform MentorMate from a simple study chatbot into a more reliable and agentic learning assistant.
