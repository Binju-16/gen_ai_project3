# Project 3 Roadmap

## 1. Project context

This Project 3 draft is the capstone for the Generative AI course. It should combine prompt engineering, grounding, evaluation, and agentic architecture from earlier projects while shifting focus to production-quality delivery and real-world impact.

## 2. Problem statement

Build an AI application that solves a concrete real-world problem by using an LLM-driven agent with at least one custom MCP tool. The draft should demonstrate a working deployed mini-app, not just a local proof-of-concept.

## 3. Target user

- A non-technical user who wants a practical AI assistant for the chosen problem domain.
- Someone who needs an easy-to-use deployed application, not a code demo.
- The instructor or grader evaluating the project.

## 4. MVP scope for this week

- Deploy a public URL that loads and accepts real user input.
- Implement one custom MCP tool definition with name, description, and input schema.
- Show the LLM calling that tool autonomously during a real interaction.
- Include at least one agent loop where the model reads tool output and decides what to do next.
- Create a project repository with a README and build log notes.

## 5. Out-of-scope items for the draft

- A fully polished final product with every feature.
- Complete edge-case coverage, but basic error handling is required.
- Multi-user authentication or large-scale production infrastructure.
- Supporting many different domains; focus on one useful, coherent use case.

## 6. Recommended tech stack

- Python backend using FastAPI, Flask, or Streamlit depending on deployment needs.
- If using MCP tooling, FastAPI gives clearer API / tool server structure.
- Frontend can be minimal HTML or Streamlit/Gradio UI for faster deployment.
- Deploy on a free public hosting service (e.g. Railway, Render, Vercel, or Hugging Face if using Gradio).
- Use OpenAI-compatible model access via environment variables for API keys.

## 7. Hosting/deployment plan

- Choose a platform that supports Python web apps and public URLs.
- Railway or Render are good for FastAPI/Flask apps with a free tier.
- Streamlit Community Cloud or Hugging Face Spaces are easiest for Streamlit/Gradio.
- Ensure the URL is not localhost and stays accessible for the instructor.

## 8. System prompt design

- Create a system prompt that defines the model’s role clearly.
- Example: “You are an autonomous AI assistant for [problem]. Use available tools when needed, ask clarifying questions, and return actionable results.”
- If using multiple agents, give each a tailored system prompt reflecting its purpose.
- Include behavior constraints, output format expectations, and the tool policy.

## 9. Prompt engineering techniques to use

- Use few-shot examples for the tool-call format and expected responses.
- Add explicit instructions for when to call tools versus when to answer directly.
- Provide a clear output template for agent responses and summaries.
- Document at least two prompt versions and the changes made between them.

## 10. Grounding strategy

- Ground the model with real context it cannot infer from pretraining.
- Use live data from the custom tool (API results, database, or files) rather than only static prompts.
- Optionally include curated domain knowledge or example cases in the prompt.
- Ensure the model receives structured facts before making decisions.

## 11. Coding plan

- Step 1: choose the problem domain and define the target user.
- Step 2: scaffold the app and deploy a basic public UI.
- Step 3: implement the MCP tool definition and tool execution loop.
- Step 4: add the LLM orchestration layer so the model decides whether to call the tool.
- Step 5: implement grounding and system prompt logic.
- Step 6: test the live app, capture tool-call traces, and document outputs.

## 12. Test harness / evaluation plan

- Create a set of example inputs to exercise the app’s core behavior.
- Record test cases that show the model calling the tool and using results.
- Evaluate success based on correct agent decisions and useful final responses.
- Log failures and iterate on prompt/tool definitions.

## 13. Success metrics

- Public app URL is reachable and interactive.
- Custom MCP tool is defined, exposed, and executed in a real session.
- The LLM makes at least one autonomous decision via tool use.
- The draft includes a GitHub repo with README and build notes.
- The system can handle sample inputs and returns coherent, grounded outputs.

## 14. Risks and limitations

- Deployment may sleep or time out on free hosting.
- API keys must be handled securely; misconfiguration can break the app.
- The model may choose not to call the tool unless prompts and tool descriptions are precise.
- Real-world data sources may be unavailable if service limits or network issues occur.

## 15. GitHub commit plan

- Commit 1: initial scaffold and project README.
- Commit 2: MVP app with public deployment and basic UI.
- Commit 3: custom MCP tool definition and execution logic.
- Commit 4: agentic orchestration and system prompt improvements.
- Commit 5: test cases, evaluation notes, and build log documentation.

## 16. README/build log plan

- Document the problem, architecture, and deployment URL.
- Explain the MCP tool, its schema, and how the model uses it.
- Include a sample interaction with tool call trace.
- Add a build log section listing prompt versions, experiments, and what changed.
- Describe known limitations and next steps.

## 17. Questions I need to answer before coding

- What exact problem should the app solve, and who is the target user?
- Should I build this with Python Streamlit/Gradio or use FastAPI/Flask?
- Which hosting option is easiest and reliable for the deadline?
- How will I store API keys safely in deployment?
- Can I implement a draft that works without paid API keys, or is paid access required?
- What sample inputs demonstrate the app’s value clearly?
- What does a successful output look like for this application?

## 18. Step-by-step task list for building the MVP

1. Define the concrete use case and target user.
2. Choose the framework and hosting platform.
3. Create the project repository and initial README.
4. Build the public UI and deploy a first working version.
5. Define the custom MCP tool with name, description, and schema.
6. Implement the tool executor and response loop.
7. Write a system prompt and agent behavior prompt.
8. Add grounding context and example tool-call prompts.
9. Test with sample inputs and record whether the tool is called.
10. Capture evaluation notes and document roadmap progress.
11. Save the deployment URL, GitHub repo link, and write-up outline.
12. Iterate on prompt design and fix tool-call failures.
