# Evaluation Results

## Overview

This evaluation documents how StudySense behaves on representative prompts and whether it uses the MCP tools correctly.

## Evaluation process

- Run the sample prompts from `scripts/run_evaluation.py`.
- Confirm the model returns a tool call when appropriate.
- Confirm the final answer is grounded in the returned tool data.

## Sample prompts

1. Definition request: `Explain agentic behavior in AI and when I should use a tool.`
2. Course grounding request: `What is grounding and why does it matter for this project?`
3. Combined study question: `Define mocking in testing and find course guidance on evaluation.`

## Success criteria

- The model makes at least one tool call in a real session.
- The tool result is included in the final answer.
- The model decides whether to use `lookup_dictionary_entry` or `search_course_notes` based on the prompt.
- The final answer is accurate, useful, and grounded.

## Results

> Run `python3 scripts/run_evaluation.py` once `OPENAI_API_KEY` is configured. The generated response content and tool trace will be written to this file.
