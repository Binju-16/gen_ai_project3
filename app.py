import json
import os
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv
import httpx
import openai
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
FALLBACK_DICTIONARY = DATA_DIR / "fallback_dictionary.json"
COURSE_NOTES_FILE = DATA_DIR / "course_notes.json"

openai.api_key = os.getenv("OPENAI_API_KEY", "")
if not openai.api_key:
    print("WARNING: OPENAI_API_KEY is not set.")

app = FastAPI(title="MentorMate AI Companion")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are MentorMate, an agentic study companion for students. "
        "Use tools when they help the user: lookup_term for definitions, "
        "search_course_notes for course-specific context, and build_study_plan for study schedules. "
        "The model decides whether a tool is needed and which tool to use. "
        "When a tool returns useful information, use it to ground your answer. "
        "If a tool returns found=false, no matches, no useful data, or an error, do not apologize, "
        "do not mention tool failure, and do not expose internal tool behavior. "
        "Never say 'the lookup tool did not find', 'tool failed', or 'dictionary unavailable'. "
        "Instead, give the best clear, student-friendly explanation you can. "
        "If grounding was used, briefly mention the source. If grounding was not available, answer naturally without discussing the failed lookup. "
        "Keep answers concise, helpful, and study-focused."
    ),
}

TOOL_DEFINITIONS = [
    {
        "name": "lookup_term",
        "description": "Look up a term in a dictionary or fallback glossary when the user asks for a precise definition.",
        "parameters": {
            "type": "object",
            "properties": {
                "term": {
                    "type": "string",
                    "description": "The study term or concept to define.",
                },
                "language": {
                    "type": "string",
                    "description": "The language for the definition lookup. Use English.",
                    "default": "English",
                },
            },
            "required": ["term"],
        },
    },
    {
        "name": "search_course_notes",
        "description": "Search local course notes for class topics, examples, and grounded course context.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The course topic or concept to search for.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of matching notes to return.",
                    "default": 3,
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "build_study_plan",
        "description": "Create a structured study plan based on topics, deadlines, and available study hours.",
        "parameters": {
            "type": "object",
            "properties": {
                "topics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Topics the student needs to study.",
                },
                "deadline": {
                    "type": "string",
                    "description": "Deadline or exam date.",
                },
                "available_hours": {
                    "type": "integer",
                    "description": "Estimated study hours available per day.",
                    "default": 2,
                },
            },
            "required": ["topics", "deadline"],
        },
    },
]


def load_fallback_dictionary() -> Dict[str, Any]:
    if not FALLBACK_DICTIONARY.exists():
        return {}
    with open(FALLBACK_DICTIONARY, "r", encoding="utf-8") as handle:
        return json.load(handle)


def format_api_dictionary_result(raw_data: Any) -> Dict[str, Any]:
    entries = []

    for item in raw_data:
        word = item.get("word")
        phonetics = ", ".join(
            [p.get("text", "") for p in item.get("phonetics", []) if p.get("text")]
        )

        meanings = []
        for meaning in item.get("meanings", []):
            definitions = []
            for definition in meaning.get("definitions", []):
                definitions.append(
                    {
                        "definition": definition.get("definition"),
                        "example": definition.get("example"),
                        "synonyms": definition.get("synonyms", []),
                    }
                )

            meanings.append(
                {
                    "part_of_speech": meaning.get("partOfSpeech"),
                    "definitions": definitions,
                }
            )

        entries.append(
            {
                "word": word,
                "phonetics": phonetics,
                "meanings": meanings,
            }
        )

    return {
        "found": True,
        "source": "dictionaryapi.dev",
        "entries": entries,
    }


async def lookup_term(term: str, language: str = "English") -> Dict[str, Any]:
    language = language.strip().lower()
    cleaned_term = term.strip()

    if language != "english":
        return {
            "term": cleaned_term,
            "source": "none",
            "found": False,
            "message": "Only English lookup is supported.",
        }

    api_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{cleaned_term}"

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(api_url)
            response.raise_for_status()
            raw_data = response.json()
            return format_api_dictionary_result(raw_data)
        except Exception:
            fallback = load_fallback_dictionary()
            entry = fallback.get(cleaned_term.lower())

            if entry:
                return {
                    "found": True,
                    "source": "fallback",
                    "entries": [entry],
                }

            return {
                "term": cleaned_term,
                "source": "none",
                "found": False,
                "message": "No dictionary definition was found.",
            }


def load_course_notes() -> Dict[str, Any]:
    if not COURSE_NOTES_FILE.exists():
        return {}
    with open(COURSE_NOTES_FILE, "r", encoding="utf-8") as handle:
        return json.load(handle)


async def search_course_notes(query: str, max_results: int = 3) -> Dict[str, Any]:
    query = query.strip().lower()
    notes = load_course_notes().get("notes", [])
    matches = []

    for note in notes:
        title = note.get("topic", "").lower()
        content = note.get("content", "").lower()

        if query in title or query in content:
            matches.append(note)

    return {
        "query": query,
        "source": "course_notes",
        "found": len(matches) > 0,
        "matches": matches[:max_results],
    }


async def build_study_plan(
    topics: list[str], deadline: str, available_hours: int = 2
) -> Dict[str, Any]:
    if not topics:
        return {
            "found": False,
            "message": "No study topics were provided.",
        }

    plan = []
    for index, topic in enumerate(topics, start=1):
        plan.append(
            {
                "session": index,
                "topic": topic,
                "recommendation": (
                    f"Review {topic} with focused notes and examples, "
                    "then test your recall with a short summary."
                ),
                "estimated_hours": min(available_hours, 2),
            }
        )

    return {
        "found": True,
        "source": "study_plan_builder",
        "deadline": deadline,
        "available_hours": available_hours,
        "topics": topics,
        "plan": plan,
        "summary": (
            f"Build a study plan for {len(topics)} topic(s) before {deadline} "
            f"with about {available_hours} hours per day."
        ),
    }


TOOL_HANDLERS = {
    "lookup_term": lookup_term,
    "search_course_notes": search_course_notes,
    "build_study_plan": build_study_plan,
}


async def call_openai_chat(messages: list[dict]) -> Any:
    if not openai.api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    response = openai.chat.completions.create(
        model="gpt-4-0613",
        messages=messages,
        functions=TOOL_DEFINITIONS,
        function_call="auto",
        temperature=0.2,
    )

    return response


async def process_user_message(user_message: str) -> Dict[str, Any]:
    messages = [SYSTEM_PROMPT, {"role": "user", "content": user_message}]
    tool_trace = []

    for _ in range(5):
        response = await call_openai_chat(messages)
        choice = response.choices[0]
        message = choice.message

        function_call = message.function_call

        if function_call:
            tool_name = function_call.name
            raw_args = function_call.arguments or "{}"

            try:
                args = json.loads(raw_args)
            except json.JSONDecodeError:
                args = {}

            tool_func = TOOL_HANDLERS.get(tool_name)

            if tool_func:
                try:
                    tool_result = await tool_func(**args)
                except Exception as exc:
                    tool_result = {
                        "found": False,
                        "source": "none",
                        "message": "The tool could not return usable data.",
                        "debug_error": str(exc),
                    }
            else:
                tool_result = {
                    "found": False,
                    "source": "none",
                    "message": f"Unknown tool: {tool_name}",
                }

            tool_trace.append(
                {
                    "tool": tool_name,
                    "args": args,
                    "result": tool_result,
                }
            )

            messages.append(
                {
                    "role": "assistant",
                    "content": None,
                    "function_call": {
                        "name": tool_name,
                        "arguments": json.dumps(args),
                    },
                }
            )

            messages.append(
                {
                    "role": "function",
                    "name": tool_name,
                    "content": json.dumps(tool_result),
                }
            )

            continue

        assistant_content = message.content or ""
        return {
            "answer": assistant_content,
            "tool_trace": tool_trace,
        }

    return {
        "answer": (
            "I could not complete the full tool workflow, but I can still help. "
            "Please try rephrasing your question."
        ),
        "tool_trace": tool_trace,
    }


@app.get("/", response_class=HTMLResponse)
async def root(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/chat")
async def chat_api(request: Request) -> JSONResponse:
    payload = await request.json()
    user_message = payload.get("message", "").strip()

    if not user_message:
        raise HTTPException(status_code=400, detail="Message text is required.")

    result = await process_user_message(user_message)
    return JSONResponse(result)